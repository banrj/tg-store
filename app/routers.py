from fastapi import Response, Request, APIRouter
from aiogram import Bot
from aiogram.types import Update

from app.common import TelegramApp
from app.config import settings
from app.core.log_config import logger

main_router = APIRouter()

bot = Bot(settings.TG_KEY)


@main_router.post('/tgwebhook', tags=['telegram'], response_model=None)
async def telegram_webhook(request: Request, tg_app: TelegramApp) -> Response:
    """Handle incoming Telegram updates by putting them into the `update_queue`"""
    try:
        json_data = await request.json()
        logger.info(f"Дернули rout: {json_data}")

        update = Update.model_validate(await request.json(), context={"bot": bot})
        await tg_app.feed_webhook_update(update=update)

        logger.info("Update processed successfully")
        return Response(status_code=200, content='Update передан боту')
    except Exception as e:
        logger.error(f"Что-то в роуте: {e}")
        return Response(status_code=500, content=str(e))


@main_router.get('/checkstate', tags=['service'])
async def check_state(request: Request):
    state = request.app.state
    return Response(status_code=200, content=str(state))
