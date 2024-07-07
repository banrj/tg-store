from aiogram import Bot, Dispatcher
from contextlib import asynccontextmanager
from asyncio import create_task, CancelledError

from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.tg.fsm.storage import DynamoDBStorage
from app.db import connection as app_dynamo
from app.tg.routers.start import router as start_rout
from app.core.log_config import logger
from app.config import settings


@asynccontextmanager
async def create_tg(bot: Bot, storage: DynamoDBStorage, use_webhook: bool):
    logger.info("Crate TG in Lifespan")
    dp = Dispatcher(storage=storage)

    dp.include_router(start_rout)
    if use_webhook:
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


async def initialize_components(fastapi):
    logger.info("Initializing components")
    bot = Bot(token=settings.TG_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    async with app_dynamo.dynamodb_connection() as (resource_conn, client_conn):
        conn = app_dynamo.DynamoConnection(client_conn, resource_conn)
        async with conn.table() as table:
            dynamo_storage = DynamoDBStorage(table=table)
            dp = Dispatcher(storage=dynamo_storage)
            dp.include_router(start_rout)

            logger.info(f'Webhook use: {settings.WEBHOOK}')

            fastapi.state.dynamo_table = table
            fastapi.state.dynamo_client = client_conn
            fastapi.state.storage = dynamo_storage
            fastapi.state.bot = bot
            fastapi.state.dispatcher_tg = dp


async def shutdown(fastapi):
    await fastapi.app.state.bot.close()
    logger.info('BOT SHUTDOWN')
