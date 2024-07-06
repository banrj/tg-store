from aiogram import Bot, Dispatcher
from contextlib import asynccontextmanager
from asyncio import create_task, CancelledError
from app.tg.fsm.storage import DynamoDBStorage
from app.tg.routers.start import router as start_rout
from app.core.log_config import logger
from app.config import settings


@asynccontextmanager
async def create_tg(bot: Bot, storage: DynamoDBStorage, use_webhook: bool):
    dp = Dispatcher(storage=storage)

    dp.include_router(start_rout)
    if use_webhook:
        # webhook_url = settings.WEBHOOK
        # await bot.set_webhook(webhook_url)
        logger.info(f'Webhook use: {settings.WEBHOOK}')
    else:
        logger.info('BOT USE LOCAL POLLING')
        polling_task = create_task(dp.start_polling(bot, polling_timeout=2))

    try:
        yield dp
    finally:
        if not use_webhook:
            logger.info('stop polling')
            polling_task.cancel()
            try:
                await polling_task
            except CancelledError:
                logger.info('Polling task cancelled.')

        await bot.close()
        logger.info('SHUTDOWN')