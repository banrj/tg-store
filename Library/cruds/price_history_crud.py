from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models import PriceHistory
from fastapi.responses import JSONResponse


class PriceHistoryCrud:

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session

    async def create_history(self, book_id: int, price: int | None = 0):
        try:
            new_history = PriceHistory(book_id=book_id, price=price)
            self.db_session.add(new_history)
        except Exception as ex:
            await self.db_session.rollback()
            return JSONResponse(content={'message': f'Произошла ошибка!: {str(ex)}'},
                                status_code=500)

    async def delete_history_book(self, book_id: int):
        try:
            stmt = (delete(PriceHistory).where(PriceHistory.book_id == book_id).returning(PriceHistory.id))
            deleted_id = await self.db_session.scalar(stmt)

            if deleted_id:
                await self.db_session.commit()
                return JSONResponse(content={
                    'message': f'История цен книнги №{deleted_id} удалена!'},
                    status_code=200)

            await self.db_session.rollback()
            return JSONResponse(content={
                'message': f'История цен книги с id {book_id} не существует!'},
                status_code=404)
        except Exception as ex:
            await self.db_session.rollback()
            return JSONResponse(content={'message': f'Произошла ошибка!: {str(ex)}'},
                                status_code=500)

    async def get_history_book(self, book_id: int, lim: int, offset: int):
        try:
            stmt = select(PriceHistory.id, PriceHistory.book_id,
                          PriceHistory.price, PriceHistory.date
                          ).where(PriceHistory.book_id == book_id
                                  ).order_by(PriceHistory.date).limit(lim).offset(offset)
            res = await self.db_session.execute(stmt)
            history_row = [r._asdict() for r in res.fetchall()]
            if not history_row:
                return JSONResponse(content={
                    'message': f'История цен книги с id {book_id} не существует!'},
                    status_code=404)
            return history_row
        except Exception as ex:
            await self.db_session.rollback()
            return JSONResponse(content={'message': f'Произошла ошибка!: {str(ex)}'},
                                status_code=500)

    async def create_many_history(self, books_data):
        try:
            print(books_data)
            all_history = []
            for book in books_data:
                all_history.append(PriceHistory(book_id=book[0], price=book[1]))
            self.db_session.add_all(all_history)
            await self.db_session.commit()
        except Exception as ex:
            await self.db_session.rollback()
            return JSONResponse(content={'message': f'Произошла ошибка!: {str(ex)}'},
                                status_code=500)
