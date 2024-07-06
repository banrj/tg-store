from fastapi import Response, Request, APIRouter
from aiogram import Bot
from aiogram.types import Update

from app.common import TelegramApp
from app.config import settings
from app.core.log_config import logger
from app.tg.create_app import shutdown

main_router = APIRouter()


@main_router.post('/tgwebhook', tags=['telegram'], response_model=None)
async def telegram_webhook(request: Request, tg_app: TelegramApp) -> Response:
    """Handle incoming Telegram updates by putting them into the `update_queue`"""
    try:
        json_data = await request.json()
        state_dict = {key: str(value) for key, value in request.app.state.__dict__.items()}
        logger.info(f"Дернули rout: {json_data}")
        logger.info(f"Check State: {state_dict}")

        update = Update.model_validate(await request.json(), context={"bot": state_dict['bot']})
        await tg_app.feed_webhook_update(update=update, bot=state_dict['bot'])

    except Exception as e:
        logger.error(f"Что-то в роуте: {e}")
        return Response(status_code=500, content=str(e))
    finally:
        logger.info("Update processed successfully")
        await shutdown(request.app)
        return Response(status_code=200, content='Update передан боту')


@main_router.get('/checkstate', tags=['service'])
async def check_state(request: Request):
    state = request.app.state
    return Response(status_code=200, content=str(state))
