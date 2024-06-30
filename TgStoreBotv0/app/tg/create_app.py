from aiogram import Bot, Dispatcher
from app.fsm.storage import DynamoDBStorage


async def create_tg(bot: Bot, storage: DynamoDBStorage):
    dp = Dispatcher(storage=storage)

    await dp.start_polling(bot)
