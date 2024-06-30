from fastapi import Response, Request, APIRouter
from aiogram import Dispatcher, Bot
from aiogram.types import Update
from config import settings

main_router = APIRouter()

bot = Bot(settings.TG_KEY)


@router.post('/telegram', tags=['telegram'])
async def telegram_webhook(request: Request, tg_app: Dispatcher) -> Response:
    """Handle incoming Telegram updates by putting them into the `update_queue`"""
    json_data = await request.json()
    update = Update.de_json(data=json_data)
    await tg_app.feed_update(update=update, bot=bot)
    return Response()
