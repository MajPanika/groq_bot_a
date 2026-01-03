import logging
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from config import TELEGRAM_TOKEN
from generation_service import GenerationService
from memory_store import chat_store


# -------------------------------------------------
# logging
# -------------------------------------------------
logger = logging.getLogger("telegram")


# -------------------------------------------------
# bot / dispatcher
# -------------------------------------------------
bot = Bot(
    token=TELEGRAM_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)
dp = Dispatcher()


# -------------------------------------------------
# styles
# -------------------------------------------------
SYSTEM_STYLES = {
    "default": {
        "title": "Обычный",
        "system": "Ты полезный, дружелюбный и вменяемый ассистент."
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


def get_dialog_key(message: Message) -> str:
    """
    Уникальный ключ диалога:
    chat_id + thread_id (если есть)
    """
    thread_id = message.message_thread_id or 0
    return f"{message.chat.id}:{thread_id}"


def resolve_style(style_meta: Optional[dict], user_id: int) -> str:
    """
    Возвращает system prompt по метаданным стиля
    """
    if not style_meta:
        return SYSTEM_STYLES["default"]["system"]

    if style_meta["type"] == "system":
        return SYSTEM_STYLES.get(
            style_meta["id"],
            SYSTEM_STYLES["default"]
        )["system"]

    if style_meta["type"] == "custom":
        user_styles = chat_store.get_user_styles(user_id)
        return user_styles.get(
            style_meta["id"],
            SYSTEM_STYLES["default"]["system"]
        )

    return SYSTEM_STYLES["default"]["system"]


# -------------------------------------------------
# commands
# -------------------------------------------------
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Я живой 🤍\n"
        "Каждая тема — отдельный диалог.\n"
        "Можно выбрать стиль через /style"
    )


@dp.message(Command("reset"))
async def reset_chat(message: Message):
    key = get_dialog_key(message)
    chat_store.clear(key)
    await message.answer("Контекст этого диалога сброшен ✨")


@dp.message(Command("style"))
async def style_command(message: Message):
    parts = message.text.split(maxsplit=1)

    # список
    if len(parts) == 1:
        text = "*Стили:*\n\n"
        for k, v in SYSTEM_STYLES.items():
            text += f"• `{k}` — {v['title']}\n"

        user_styles = chat_store.get_user_styles(message.from_user.id)
        if user_styles:
            text += "\n*Твои стили:*\n"
            for name in user_styles:
                text += f"• `{name}`\n"

        text += "\nПример:\n`/style creative`"
        await message.answer(text)
        return

    # установка
    name = parts[1].strip()
    key = get_dialog_key(message)

    if name in SYSTEM_STYLES:
        chat_store.update_meta(
            key,
            style={"type": "system", "id": name}
        )
        await message.answer(
            f"Стиль установлен: *{SYSTEM_STYLES[name]['title']}*"
        )
        return

    user_styles = chat_store.get_user_styles(message.from_user.id)
    if name in user_styles:
        chat_store.update_meta(
            key,
            style={"type": "custom", "id": name}
        )
        await message.answer(f"Применён твой стиль: *{name}*")
        return

    await message.answer("Такого стиля нет 😌")


@dp.message(Command("newstyle"))
async def new_style(message: Message):
    await message.answer(
        "Создание стиля:\n\n"
        "`Название | system prompt`\n\n"
        "Пример:\n"
        "`sarcastic | Ты язвительный, умный и сухо шутишь`"
    )


# -------------------------------------------------
# messages
# -------------------------------------------------
@dp.message()
async def handle_message(message: Message):
    key = get_dialog_key(message)

    logger.info(
        f"chat={message.chat.id} "
        f"thread={message.message_thread_id} "
        f"user={message.from_user.id}"
    )

    meta = chat_store.get_meta(key)
    system_prompt = resolve_style(
        meta.get("style"),
        message.from_user.id
    )

    response = GenerationService.generate(
        text=message.text,
        chat_id=key,
        system_prompt=system_prompt
    )

    await message.answer(response)
