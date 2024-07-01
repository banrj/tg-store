from fastapi import Response, Request, APIRouter
from aiogram import Dispatcher, Bot
from aiogram.types import Update

from app.common import TelegramApp
from app.config import settings

main_router = APIRouter()

bot = Bot(settings.TG_KEY)


@main_router.post('/tg-webhook', tags=['telegram'], response_model=None)
async def telegram_webhook(request: Request, tg_app: TelegramApp) -> Response:
    """Handle incoming Telegram updates by putting them into the `update_queue`"""
    json_data = await request.json()
    update = Update.de_json(data=json_data)
    await tg_app.feed_update(update=update, bot=bot)
    return Response()
