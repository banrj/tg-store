from aiogram import Bot, Dispatcher
from aiogram.types import Update


import asyncio
import json
import logging
import os

from aiogram import Bot, Dispatcher
from app.tg.routers.start import router
from app.config import settings

# Logger initialization and logging level setting
log = logging.getLogger(__name__)
log.setLevel(os.environ.get('LOGGING_LEVEL', 'INFO').upper())


# Functions for Yandex.Cloud
async def register_handlers(dp: Dispatcher):
    """Registration all handlers before processing update."""

    dp.include_router(router)
    log.debug('Handlers are registered.')


async def process_event(event, dp: Dispatcher, bot: Bot):
    """
    Converting an Yandex.Cloud functions event to an update and
    handling tha update.
    """

    update = json.loads(event['body'])
    log.debug('Update: ' + str(update))

    update = Update.model_validate(update, context={"bot": bot})
    await dp.feed_update(update=update, bot=bot)


async def handler(event, context):
    """Yandex.Cloud functions handler."""

    if event['httpMethod'] == 'POST':
        # Bot and dispatcher initialization
        bot = Bot(settings.TG_KEY)
        dp = Dispatcher()

        await register_handlers(dp)
        await process_event(event, dp, bot)

        return {'statusCode': 200, 'body': 'ok'}
    return {'statusCode': 405}
