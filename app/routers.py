from fastapi import Response, Request, APIRouter
from aiogram import Dispatcher, Bot
from aiogram.types import Update

from app.common import TelegramApp
from app.config import settings
from app.core.log_config import logger

main_router = APIRouter()

bot = Bot(settings.TG_KEY)


@main_router.post('/tg-webhook', tags=['telegram'], response_model=None)
async def telegram_webhook(request: Request, tg_app: TelegramApp) -> Response:
    """Handle incoming Telegram updates by putting them into the `update_queue`"""
    try:
        json_data = await request.json()
        logger.info(f"Received update: {json_data}")

        update = Update.de_json(data=json_data)
        await tg_app.feed_update(update=update, bot=bot)

        logger.info("Update processed successfully")
        return Response(status_code=200)
    except Exception as e:
        logger.error(f"Error handling update: {e}")
        return Response(status_code=500, content=str(e))
