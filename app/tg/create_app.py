from aiogram import Bot, Dispatcher
from contextlib import asynccontextmanager
import requests
from app.tg.fsm.storage import DynamoDBStorage
from app.tg.routers.start import router as start_rout
from app.core.log_config import logger
from app.config import settings

TG_TOKEN = settings.TG_KEY
WEBHOOK_URL = 'https://d5d6goq6did08enqmi0a.apigw.yandexcloud.net/tg-webhook'

url = 'https://api.telegram.org/bot{token}/getWebhookInfo'.format(token=TG_TOKEN)

data = {'url': WEBHOOK_URL}


def info_webhook():
    r = requests.post(url, data)
    logger.info(r.json())


@asynccontextmanager
async def create_tg(bot: Bot, storage: DynamoDBStorage, use_webhook: bool):
    dp = Dispatcher(storage=storage)

    dp.include_router(start_rout)
    if use_webhook:
        # webhook_url = settings.WEBHOOK
        # await bot.set_webhook(webhook_url)
        logger.info(f'Webhook use: {settings.WEBHOOK}')
        info_webhook()
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

