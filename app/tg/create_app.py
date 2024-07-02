from aiogram import Bot, Dispatcher
from contextlib import asynccontextmanager

from app.tg.fsm.storage import DynamoDBStorage
from app.tg.routers.start import router as start_rout
from app.core.log_config import logger
from app.config import settings


@asynccontextmanager
async def create_tg(bot: Bot, storage: DynamoDBStorage, use_webhook: bool):
    dp = Dispatcher(storage=storage)

    dp.include_router(start_rout)
    if use_webhook:
        webhook_url = settings.WEBHOOK
        await bot.set_webhook(webhook_url)
        logger.info(f'Webhook use: {webhook_url}')
    else:
        logger.info('BOT USE LOCAL POLLING')
        await dp.start_polling(bot)

    try:
        yield dp
    finally:
        if not use_webhook:
            logger.info('stop polling')
            await dp.stop_polling()

        await bot.delete_webhook()
        await bot.close()
        logger.info('DELETE WEBHOOK')
        logger.info('SHUTDOWN')

