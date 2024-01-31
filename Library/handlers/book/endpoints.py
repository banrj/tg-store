import asyncio
import pandas as pd

from httpx import AsyncClient, HTTPError
from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from handlers.book.schemas import (CreateBook, ShowBook, DeleteBook,
                                   SearchBook, UpdateBook, InvalidBook)
from db.base import AsyncSession, get_db
from cruds.book_crud import BookCrud
from cruds.price_history_crud import PriceHistoryCrud
from config import LOAD_BOOKS_URL, COLUMNS

book_router = APIRouter()


async def _create_new_book(db: AsyncSession, body: CreateBook):
    async with db as session:
        async with session.begin():
            crud = BookCrud(session)
            history_crud = PriceHistoryCrud(session)
            new_book = await crud.create_book(
                title=body.title, author=body.author, genre=body.genre,
                description=body.description, cover_image=body.cover_image,
                publication_year=body.publication_year, price=body.price
            )
            if isinstance(new_book, JSONResponse):
                return new_book
            await history_crud.create_history(book_id=new_book.id, price=new_book.price)
            return ShowBook(
                id=new_book.id, title=new_book.title, genre=new_book.genre,
                author=new_book.author, description=new_book.description,
                publication_year=new_book.publication_year, price=new_book.price,
                cover_image=new_book.cover_image
            )


@book_router.post('/create', tags=['books'], response_model=ShowBook)
async def create_book(db: AsyncSession = Depends(get_db),
                      body: CreateBook = Depends()) -> ShowBook:

    return await _create_new_book(body=body, db=db)


async def _delete_book(db: AsyncSession, body: DeleteBook):
    async with db as session:
        async with session.begin():
            crud = BookCrud(session)
            return await crud.delete_book(book_id=body.id)


@book_router.delete('/delete/{book_id}', tags=['books'])
async def delete_book(db: AsyncSession = Depends(get_db),
                      body: DeleteBook = Depends()):

    return await _delete_book(body=body, db=db)


async def _get_current_book(db: AsyncSession, body: SearchBook):
    async with db as session:
        async with session.begin():
            crud = BookCrud(session)
            return await crud.get_book(book_id=body.id)


@book_router.get('/{book_id}', tags=['books'])
async def get_book(db: AsyncSession = Depends(get_db),
                   body: SearchBook = Depends()):

    return await _get_current_book(body=body, db=db)


async def _update_current_book(db: AsyncSession, book_id: int, body: UpdateBook) -> ShowBook:
    async with db as session:
        async with session.begin():
            crud = BookCrud(session)
            if body.genre == ['string']:
                body.genre = None
            data = await crud.update_book(book_id=book_id, update_book=body)

            if data['flag']:
                history_crud = PriceHistoryCrud(session)
                await history_crud.create_history(book_id=book_id, price=body.price)
            return data['book']


@book_router.patch('/update/{book_id}', tags=['books'])
async def update_book(book_id: int,
                      db: AsyncSession = Depends(get_db),
                      body: UpdateBook = Depends()):

    return await _update_current_book(body=body, db=db, book_id=book_id)


async def _get_list_books(db: AsyncSession, lim: int, offset: int, title: str = None,
                          author: str = None, genres: str = None, price: int = None,
                          description: str = None, genres_neq: str = None
                          ):
    async with db as session:
        async with session.begin():
            crud = BookCrud(session)
            return await crud.get_books(lim=lim, offset=offset, title=title,
                                        author=author, genres=genres, genres_neq=genres_neq,
                                        description=description, price=price
            )


@book_router.get('/', tags=['books'])
async def get_books(offset: int = 0, lim: int = 10, title: str = None,
                    author: str = None, genres: str = None, price: int = None,
                    description: str = None, genres_neq: str = None,
                    db: AsyncSession = Depends(get_db)):
    return await _get_list_books(db=db, lim=lim, offset=offset, title=title,
                                 author=author, genres=genres, genres_neq=genres_neq,
                                 description=description, price=price
                                 )


async def _make_api_request():
    async with AsyncClient() as client:
        try:
            response = await client.get(LOAD_BOOKS_URL)
            response.raise_for_status()
            data = response.json()
            return data
        except HTTPError as ex:
            return JSONResponse({'message': f'Возникла ошибка во время стороннего запроса!: {ex}'}, status_code=500)


async def _filter_books(db: AsyncSession):
    async with db as session:
        crud = BookCrud(session)
        books_data = await _make_api_request()
        if isinstance(books_data, JSONResponse):
            return books_data
        loaded_book = []
        unloaded_book = []
        for book in books_data:
            try:
                new = CreateBook(**book)
                loaded_book.append(new.json())
            except ValidationError:
                unloaded_book.append(book)
        information = await crud.load_data(loaded_book)
        if isinstance(information, JSONResponse):
            return information

        return {'loaded_books': information['valid_books'],
                'invalid_books': unloaded_book, 'duplicates': information['duplicate_books']}


async def _last_stage(db: AsyncSession, func, *args, **kwargs):
    async with db as session:
        crud = PriceHistoryCrud(session)
        books_data = await func(db, *args, **kwargs)
        if isinstance(books_data, JSONResponse):
            return books_data
        price_data = [(book.id, book.price) for book in books_data['loaded_books']]
        await crud.create_many_history(price_data)
        return books_data


@book_router.get('/loading/', tags=['books'])
async def load_books(db: AsyncSession = Depends(get_db)):
    return await _last_stage(db=db, func=_filter_books)


async def run_in_threadpool(func, *args, **kwargs):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args, **kwargs)


async def _validate_columns(actual_columns):
    if set(COLUMNS.keys()) != set(actual_columns):
        return JSONResponse(
            content={'Ваши поля не соответсвуют стандартной форме.\n'
                     'title|publication_year|genre|price|author|description|cover_image\n'
                     'Внимательно следите чтобы в названиях не было дополнительно символов и пробелов'},
            status_code=400)


async def _check_file(db: AsyncSession, file: UploadFile):

    if file.filename[-5:] != '.xlsx':
        return JSONResponse(content={'message': 'File must be .xlsx'}, status_code=400)
    file = file.file
    valid = []
    invalid = []
    try:
        df = await run_in_threadpool(pd.read_excel, file)

        check_response = await _validate_columns(df.columns)
        if isinstance(check_response, JSONResponse):
            return check_response
        for number in range(df.index.start, df.index.stop, df.index.step):
            book = [df['title'][number], df['publication_year'][number], df['genre'][number],
                    df['price'][number], df['author'][number], df['description'][number],
                    df['cover_image'][number]]
            if isinstance(book[2], str):
                book[2] = book[2].split(',')
            book = [data if data == data else None for data in book]
            try:
                new = CreateBook(title=book[0], publication_year=book[1], genre=book[2],
                                 price=book[3], author=book[4],
                                 description=book[5], cover_image=book[6])
                valid.append(new.json())
            except ValidationError as ex:
                invalid_book = InvalidBook(title=book[0], publication_year=book[1], genre=book[2],
                                           price=book[3], author=book[4], error=str(ex),
                                           description=book[5], cover_image=book[6])
                invalid.append(invalid_book)

        async with db as session:
            crud = BookCrud(session)
            information = await crud.load_data(valid)

            if isinstance(information, JSONResponse):
                return information

            return {'loaded_books': information['valid_books'],
                    'invalid_books': invalid, 'duplicates': information['duplicate_books']}

    except Exception as ex:
        return JSONResponse(content={'message': f'{str(ex)}'}, status_code=500)


@book_router.post("/file/upload-file")
async def upload_file(file: UploadFile, db: AsyncSession = Depends(get_db)):
    return await _last_stage(file=file, func=_check_file, db=db)
