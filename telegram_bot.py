from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode

from config import TELEGRAM_TOKEN
from generation_service import GenerationService

import logging
logger = logging.getLogger("telegram")


bot = Bot(
    token=TELEGRAM_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)
dp = Dispatcher()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Я живой 🤍\nНапиши что-нибудь."
    )


@dp.message()
async def handle_message(message: Message):
    logger.info(
        f"Message from {message.from_user.id}: {message.text[:50]}"
    )
    response = GenerationService.generate(
    text=message.text,
    chat_id=message.chat.id
    )

    await message.answer(response)
