from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Book, PriceHistory
from sqlalchemy import delete, select
from typing import List, Text, Dict
from fastapi.responses import JSONResponse
from handlers.book.schemas import UpdateBook, InvalidBook
from sqlalchemy.exc import IntegrityError, DataError, DBAPIError


class BookCrud:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_book(
            self,
            title: str,
            publication_year: int,
            genre: List[str],
            price: int | None = 0,
            author: str | None = None,
            description: Text | None = None,
            cover_image: str | None = None
                          ) -> Book | JSONResponse:
        """
        func for create new book
        """
        try:

            new_book = Book(title=title,
                            publication_year=publication_year,
                            genre=genre,
                            author=author,
                            price=price,
                            description=description,
                            cover_image=cover_image)
            self.db_session.add(new_book)
            await self.db_session.flush()
            return new_book
        except (IntegrityError, DataError, TypeError, DBAPIError) as ex:
            await self.db_session.rollback()
            invalid_book = InvalidBook(title=title, publication_year=publication_year,
                                       genre=genre, author=author, price=price,
                                       description=description, cover_image=cover_image,
                                       error=f'{str(ex)}').json()
            return JSONResponse(content={'message': f'{str(ex)}',
                                         'invalid_book': invalid_book},
                                status_code=400)

        except Exception as ex:
            await self.db_session.rollback()
            return JSONResponse(content={'message': f'Произошла ошибка!: {str(ex)}'},
                                status_code=500)

    async def delete_book(self, book_id: int) -> JSONResponse:
        try:
            stmt0 = (delete(PriceHistory).where(PriceHistory.book_id == book_id))
            await self.db_session.execute(stmt0)
            stmt = (delete(Book).where(Book.id == book_id).returning(Book.id))
            deleted_id = await self.db_session.scalar(stmt)

            if deleted_id:
                await self.db_session.commit()
                return JSONResponse(content={
                    'message': f'Книга под №{deleted_id} удалена!\nИ вся связанная с ней история тоже'},
                                    status_code=200)

            await self.db_session.rollback()
            return JSONResponse(content={
                                'message': f'Книги с id {book_id} не существует'},
                                status_code=404)

        except Exception as ex:
            await self.db_session.rollback()
            return JSONResponse(content={'message': f'Произошла ошибка!: {str(ex)}'},
                                status_code=500)

    async def get_book(self, book_id: int) -> Book | JSONResponse:
        try:
            query = select(Book).where(Book.id == book_id)
            row = await self.db_session.execute(query)
            book_row = row.fetchone()
            if book_row:
                return book_row[0]
            return JSONResponse(content={
                'message': f'Книги с id {book_id} не существует'},
                                status_code=404)
        except Exception as ex:
            return JSONResponse(content={'message': f'Произошла ошибка!: {str(ex)}'},
                                status_code=500)

    async def update_book(self, book_id: int, update_book: UpdateBook) -> Dict | JSONResponse:

        try:
            query = select(Book).where(Book.id == book_id)
            row = await self.db_session.execute(query)
            book_row = row.fetchone()
            if book_row:
                cur_book = book_row[0]
                price_flag = ((update_book.price is not None) and update_book.price != cur_book.price)
                book_data = update_book.model_dump(exclude_none=True, exclude_unset=True)
                for key, value in book_data.items():
                    setattr(cur_book, key, value)
                # await self.db_session.commit()
                return {'book': cur_book, 'flag': price_flag}
            return JSONResponse(content={
                'message': f'Книги с id {book_id} не существует'},
                status_code=404)
        except Exception as ex:
            await self.db_session.rollback()
            return JSONResponse(content={'message': f'Произошла ошибка!: {str(ex)}'},
                                status_code=500)

    async def get_books(self, lim: int, offset: int, title: str = None,
                        author: str = None, genres: str = None, price: int = None,
                        description: str = None, genres_neq: str = None
                        ) -> JSONResponse:
        try:
            stmt = select(Book.id, Book.title, Book.publication_year,
                          Book.author, Book.genre, Book.description,
                          Book.cover_image, Book.price
                          ).order_by(Book.id).limit(lim).offset(offset)
            if title:
                stmt = stmt.filter(Book.title == title)
            if price:
                stmt = stmt.filter(Book.price == price)
            if author:
                stmt = stmt.filter(Book.author == author)
            if genres:
                stmt = stmt.filter(Book.genre.contains(genres.split(',')))
            if genres_neq:
                stmt = stmt.filter(~(Book.genre.contains(genres_neq.split(','))))
            if description:
                stmt = stmt.filter(Book.description.ilike(f'%{description}%'))

            res = await self.db_session.execute(stmt)
            book_row = [r._asdict() for r in res.fetchall()]

            if not book_row:
                return JSONResponse(content={'message': f'Нет книги с такими параметрами'},
                                    status_code=404)
            return JSONResponse(content={'response: ': book_row}, status_code=200)

        except Exception as ex:
            await self.db_session.rollback()
            return JSONResponse(content={'message': f'Произошла ошибка!: {str(ex)}'},
                                status_code=500)

    async def load_data(self, load_data):
        duplicates = []
        original = []
        try:
            stmt = select(Book.title)
            res = await self.db_session.execute(stmt)
            book_row = [r[0] for r in res.fetchall()]
            for data in load_data:
                if data['title'] not in book_row:
                    book = Book(**data)
                    original.append(book)
                    book_row.append(data['title'])
                else:
                    duplicates.append(data)

            self.db_session.add_all(original)
            await self.db_session.commit()

        except Exception as ex:
            await self.db_session.rollback()
            return JSONResponse(content={'message': f'Произошла ошибка!: {str(ex)}'},
                                status_code=500)
        finally:
            await self.db_session.close()

        return {'message': 'Data processed', 'valid_books': original, 'duplicate_books': duplicates}
