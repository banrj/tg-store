from fastapi import Response, Request, APIRouter
from aiogram.types import Update

from app.common import TgBot, BotDispatcher
from app.core.log_config import logger

main_router = APIRouter()


@main_router.post('/tgwebhook', tags=['telegram'], response_model=None)
async def telegram_webhook(request: Request, dp: BotDispatcher, bot: TgBot) -> Response:
    """Handle incoming Telegram updates by putting them into the `update_queue`"""
    try:
        json_data = await request.json()
        logger.info(f"Дернули rout: {json_data}")

        update = Update.model_validate(json_data, context={"bot": bot})
        await dp.feed_update(update=update, bot=bot)

    except Exception as e:
        logger.error(f"Что-то в роуте: {e}")
        return Response(status_code=500, content=str(e))
    finally:
        logger.info("Update processed successfully")
        return Response(status_code=200, content='Update передан боту')


@main_router.get('/checkstate', tags=['service'])
async def check_state(request: Request):
    state = request.app.state
    return Response(status_code=200, content=str(state))
