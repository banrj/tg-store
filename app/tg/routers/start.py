from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

router = Router()


@router.message(CommandStart)
async def start_answer(message: Message):
    await message.answer('Привет это старт команда')
