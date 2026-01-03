import logging
import time

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart

from config import TELEGRAM_TOKEN
from generation_service import GenerationService
from memory_store import chat_store

logger = logging.getLogger("telegram")

# -------- settings --------

MAX_TOPICS_PER_CHAT = 10
TOPIC_TTL_SECONDS = 60 * 60 * 24 * 14  # 14 days

# -------- bot init --------

bot = Bot(
    token=TELEGRAM_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)

dp = Dispatcher()


# -------- helpers --------

def get_thread_id(message: types.Message) -> str:
    return str(message.message_thread_id or "main")


def get_context_key(chat_id: int, thread_id: str) -> str:
    return f"{chat_id}:{thread_id}"


def cleanup_old_topics(chat_id: int):
    """Удаляем старые темы по TTL"""
    now = time.time()

    for key, meta in list(chat_store.meta.items()):
        if not key.startswith(f"{chat_id}:"):
            continue

        if now - meta["last_used"] > TOPIC_TTL_SECONDS:
            chat_store.clear(key)
            logger.debug(f"Auto-cleaned old topic {key}")


def enforce_topic_limit(chat_id: int):
    """Ограничиваем количество активных тем"""
    topics = [
        (key, meta["last_used"])
        for key, meta in chat_store.meta.items()
        if key.startswith(f"{chat_id}:")
    ]

    if len(topics) <= MAX_TOPICS_PER_CHAT:
        return

    topics.sort(key=lambda x: x[1])  # старые первые

    for key, _ in topics[:-MAX_TOPICS_PER_CHAT]:
        chat_store.clear(key)
        logger.debug(f"Removed topic by limit: {key}")


# -------- commands --------

@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Я живой 🤍\n"
        "Каждая тема — отдельный диалог.\n\n"
        "/reset — сброс текущей темы\n"
        "/stats — статистика тем"
    )


@dp.message(Command("reset"))
async def reset_chat(message: types.Message):
    thread_id = get_thread_id(message)
    context_key = get_context_key(message.chat.id, thread_id)

    chat_store.clear(context_key)

    await message.answer("Контекст этой темы сброшен ✨")


@dp.message(Command("stats"))
async def stats(message: types.Message):
    chat_id = message.chat.id

    topics = [
        key for key in chat_store.meta.keys()
        if key.startswith(f"{chat_id}:")
    ]

    await message.answer(
        f"📊 *Статистика*\n\n"
        f"Активных тем: {len(topics)} / {MAX_TOPICS_PER_CHAT}\n"
        f"TTL темы: {TOPIC_TTL_SECONDS // 86400} дней"
    )


# -------- main handler --------

@dp.message()
async def handle_message(message: types.Message):
    chat_id = message.chat.id
    thread_id = get_thread_id(message)
    context_key = get_context_key(chat_id, thread_id)

    cleanup_old_topics(chat_id)
    enforce_topic_limit(chat_id)

    logger.debug(
        f"chat_id={chat_id} "
        f"thread_id={thread_id} "
        f"context_key={context_key}"
    )

    response = GenerationService.generate(
        text=message.text,
        chat_id=context_key
    )

    await message.answer(response)
