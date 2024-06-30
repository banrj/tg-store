import asyncio
from aiogram import Bot
from config import settings
from app.core.log_config import logger
from app.db import connection as app_dynamo
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.fsm.storage import DynamoDBStorage
from fastapi import FastAPI
from contextlib import asynccontextmanager
from routers import main_router
from app.tg.create_app import create_tg


@asynccontextmanager
async def lifespan():
    logger.info("APPLICATION STARTUP")
    bot = Bot(token=settings.TG_KEY, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    logger.info("BOT CREATED")

    logger.info("DATABASE INITIALIZATION...")
    async with app_dynamo.dynamodb_connection() as (resource_conn, client_conn):
        logger.info("DATABASE INITIALIZATION \t\tSUCCESS")

        conn = app_dynamo.DynamoConnection(client_conn, resource_conn)
        logger.debug(f'starting... after conn created')
        async with conn.table() as table:
            logger.debug(f'starting... before yield, {table=}, {client_conn=}')
            logger.info("APPLICATION STARTUP \t\tCOMPLETE")
            logger.info("DYNAMO STORAGE INITIALIZATION")
            dynamo_storage = DynamoDBStorage(table=table)
            logger.info("DYNAMO STORAGE INITIALIZATION \t\tSUCCESS")
            await create_tg(bot=bot, storage=dynamo_storage)
            yield {"dynamo_table": table, "dynamo_client": client_conn, "storage": dynamo_storage,
                   "bot": bot}
            logger.info("TG BOT`s SHUTDOWN")

    logger.info("APPLICATION SHUTDOWN")


def create_app() -> FastAPI:
    fastapi_dev = FastAPI(
        lifespan=lifespan,
        root_path=f"/{settings.VERSION}",
        title="TG STORE DEV"
    )
    fastapi_dev.include_router(main_router)

    return fastapi_dev


if __name__ == "__main__":
    asyncio.run(create_app())
