import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode

from config import TELEGRAM_TOKEN
from generation_service import GenerationService
from memory_store import chat_store

logger = logging.getLogger("telegram")

# --- настройки ---
MAX_TOPICS_PER_CHAT = 20
DEFAULT_STYLE = "default"

BUILTIN_STYLES = {
    "default": {
        "title": "Обычный",
        "system": "Ты полезный и дружелюбный ассистент."
    },
    "creative": {
        "title": "Креативный",
        "system": "Ты креативный, образный и смелый в ответах."
    },
    "coder": {
        "title": "Программист",
        "system": "Ты опытный разработчик, отвечаешь чётко и по делу."
    }
}

bot = Bot(
    token=TELEGRAM_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)
dp = Dispatcher()


# --- utils ---
def get_dialog_key(message: types.Message) -> tuple:
    return (
        message.chat.id,
        message.message_thread_id  # None для обычных чатов
    )


def ensure_dialog_exists(key: tuple):
    if not chat_store.exists(key):
        chat_store.create(
            key=key,
            meta={
                "style": DEFAULT_STYLE,
                "created_at": datetime.utcnow(),
                "last_used": datetime.utcnow(),
            }
        )


def cleanup_old_topics(chat_id: int):
    dialogs = chat_store.list_by_chat(chat_id)

    if len(dialogs) <= MAX_TOPICS_PER_CHAT:
        return

    dialogs.sort(key=lambda d: d["meta"].get("last_used"))
    to_delete = dialogs[:-MAX_TOPICS_PER_CHAT]

    for d in to_delete:
        chat_store.delete(d["key"])
        logger.info(f"Old dialog removed: {d['key']}")


# --- handlers ---
@dp.message(CommandStart())
async def start(message: types.Message):
    await message.answer(
        "Я жив 🤍\n"
        "Каждая тема — отдельный диалог.\n"
        "Команды: /style, /reset, /stats"
    )


@dp.message(Command("reset"))
async def reset_chat(message: types.Message):
    key = get_dialog_key(message)
    chat_store.clear(key)
    await message.answer("Контекст этой темы сброшен ✨")


@dp.message(Command("style"))
async def choose_style(message: types.Message):
    text = "Доступные стили:\n\n"
    for k, v in BUILTIN_STYLES.items():
        text += f"• `{k}` — {v['title']}\n"

    text += "\nПример:\n`/style creative`"
    await message.answer(text)


@dp.message(Command("stats"))
async def stats(message: types.Message):
    dialogs = chat_store.list_by_chat(message.chat.id)
    await message.answer(
        f"📊 Статистика:\n"
        f"Тем: {len(dialogs)} / {MAX_TOPICS_PER_CHAT}"
    )


@dp.message(Command("style"))
async def set_style(message: types.Message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        return

    style_id = parts[1].strip()
    if style_id not in BUILTIN_STYLES:
        await message.answer("Такого стиля нет 😌")
        return

    key = get_dialog_key(message)
    ensure_dialog_exists(key)

    chat_store.update_meta(key, style=style_id)
    await message.answer(f"Стиль установлен: *{BUILTIN_STYLES[style_id]['title']}*")


@dp.message()
async def handle_message(message: types.Message):
    key = get_dialog_key(message)
    ensure_dialog_exists(key)

    meta = chat_store.get_meta(key)
    meta["last_used"] = datetime.utcnow()

    cleanup_old_topics(message.chat.id)

    style_id = meta.get("style", DEFAULT_STYLE)
    style = BUILTIN_STYLES.get(style_id, BUILTIN_STYLES["default"])

    logger.debug(
        f"chat_id={message.chat.id} "
        f"thread_id={message.message_thread_id} "
        f"style={style_id}"
    )

    response = GenerationService.generate(
        text=message.text,
        chat_id=key,
        system_prompt=style["system"]
    )

    await message.answer(response)
