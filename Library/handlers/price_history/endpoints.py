from db.base import AsyncSession, get_db
from fastapi import APIRouter
from cruds.price_history_crud import PriceHistoryCrud
from fastapi import Depends
from handlers.price_history.schemas import PriceHistoryShow
from typing import List

price_history_router = APIRouter()


async def _show_history_book(db: AsyncSession, book_id: int, lim: int, offset: int) -> List[PriceHistoryShow]:
    async with db as session:
        async with session.begin():
            crud = PriceHistoryCrud(session)
            return await crud.get_history_book(book_id=book_id, lim=lim, offset=offset)


@price_history_router.get('/{book_id}', tags=['price_history'])
async def show_history(book_id: int, lim: int = 10, offset: int = 0,
                       db: AsyncSession = Depends(get_db)):
    return await _show_history_book(db=db, book_id=book_id, lim=lim, offset=offset)
