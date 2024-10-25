import uvicorn

from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routers import main_router
from app.tg.create_app import create_tg
from app.tg.fsm.storage import DynamoDBStorage
from app.db import connection as app_dynamo
from app.config import settings
from app.core.log_config import logger
from app.core.context import AppContext


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Lifespan STARTUP")
    bot = Bot(token=settings.TG_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    logger.info("BOT CREATED")

    logger.info("DATABASE INITIALIZATION...")
    resource_conn, client_conn = await app_dynamo.dynamodb_connection()

    logger.info("DATABASE INITIALIZATION \t\tSUCCESS")

    conn = app_dynamo.DynamoConnection(client_conn, resource_conn)
    logger.debug(f'starting... after conn created')
    table = await conn.table('dev')
    logger.debug(f'starting... before yield, {table=}, {client_conn=}')
    logger.info("APPLICATION STARTUP \t\tCOMPLETE")
    logger.info("DYNAMO STORAGE INITIALIZATION")
    dynamo_storage = DynamoDBStorage(table=table)
    logger.info("DYNAMO STORAGE INITIALIZATION \t\tSUCCESS")
    async with create_tg(bot=bot, storage=dynamo_storage, use_webhook=settings.USE_WEBHOOK) as tg_dp:
        logger.info("TG BOT - SUCCESS")
        AppContext().initialize(
            bot=bot,
            dynamo_table=table,
            dynamo_client=client_conn,
            dynamo_storage=dynamo_storage,
            dispatcher_tg=tg_dp)
        yield
        logger.info("TG BOT`s SHUTDOWN")

    logger.info("APPLICATION SHUTDOWN")


def create_app() -> FastAPI:
    fastapi_dev = FastAPI(
        lifespan=lifespan,
        root_path=f"/{settings.VERSION}",
        title="TG STORE DEV"
    )
    logger.info('INCLUDES ROUTERS')
    fastapi_dev.include_router(main_router)

    return fastapi_dev


if __name__ == '__main__':
    uvicorn.run('function_app:fastapi_application', host='0.0.0.0', port=settings.PORT, reload=True)
