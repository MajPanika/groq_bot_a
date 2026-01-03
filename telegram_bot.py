import logging

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart

from config import TELEGRAM_TOKEN
from generation_service import GenerationService
from memory_store import chat_store

logger = logging.getLogger("telegram")

# --- init bot & dispatcher ---

bot = Bot(
    token=TELEGRAM_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)

dp = Dispatcher()


# --- helpers ---

def get_context_key(message: types.Message) -> str:
    """
    Уникальный ключ контекста:
    один чат + одна тема (thread)
    """
    thread_id = message.message_thread_id or "main"
    return f"{message.chat.id}:{thread_id}"


# --- commands ---

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Я живой 🤍\n"
        "Каждая тема — отдельный диалог.\n"
        "Команда /reset сбрасывает текущую тему."
    )


@dp.message(Command("reset"))
async def reset_chat(message: types.Message):
    context_key = get_context_key(message)
    chat_store.clear(context_key)

    await message.answer("Контекст этой темы сброшен ✨")


# --- main handler ---

@dp.message()
async def handle_message(message: types.Message):
    context_key = get_context_key(message)

    logger.debug(
        f"Message from user={message.from_user.id} "
        f"chat_id={message.chat.id} "
        f"thread_id={message.message_thread_id} "
        f"context_key={context_key}"
    )

    response = GenerationService.generate(
        text=message.text,
        chat_id=context_key
    )

    await message.answer(response)
