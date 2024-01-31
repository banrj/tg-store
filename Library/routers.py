from fastapi import APIRouter
from handlers.book.endpoints import book_router
from handlers.price_history.endpoints import price_history_router

main_api_router = APIRouter(prefix='/api/v1')

main_api_router.include_router(book_router, prefix='/books', tags=['books'])
main_api_router.include_router(price_history_router, prefix='/price-history', tags=['price_history'])
