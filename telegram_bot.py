import asyncio
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from generation_service import GenerationService

BOT_TOKEN = "YOUR_TELEGRAM_TOKEN"

logging.basicConfig(level=logging.INFO)

router = Router()

# ─────────────────────────────
# Настройки
# ─────────────────────────────

MAX_MESSAGES_PER_DIALOG = 20

STYLE_PROMPTS = {
    "chat": "Ты дружелюбный, умный собеседник.",
    "translator": "Ты профессиональный переводчик. Переводи только последний текст.",
    "coder": "Ты опытный программист. Отвечай кратко и по делу.",
}

# ─────────────────────────────
# In-memory хранилище диалогов
# key = (chat_id, thread_id)
# ─────────────────────────────

dialogs: dict[tuple[int, int | None], dict] = {}


def dialog_key(message: Message) -> tuple[int, int | None]:
    return message.chat.id, message.message_thread_id


def get_dialog(message: Message) -> dict:
    key = dialog_key(message)
    now = datetime.utcnow()

    if key not in dialogs:
        dialogs[key] = {
            "messages": [],
            "style": "chat",
            "mmode": "history",  # history | stateless
            "created_at": now,
            "updated_at": now,
        }

    return dialogs[key]


# ─────────────────────────────
# Utils
# ─────────────────────────────

def build_messages(dialog: dict, user_text: str) -> list[dict]:
    system_msg = {
        "role": "system",
        "content": STYLE_PROMPTS.get(dialog["style"], STYLE_PROMPTS["chat"]),
    }

    if dialog["mmode"] == "stateless":
        return [
            system_msg,
            {"role": "user", "content": user_text},
        ]

    history = dialog["messages"][-MAX_MESSAGES_PER_DIALOG * 2 :]

    return [
        system_msg,
        *history,
        {"role": "user", "content": user_text},
    ]


# ─────────────────────────────
# Commands
# ─────────────────────────────

@router.message(Command("start"))
async def start_cmd(message: Message):
    await message.answer(
        "Привет 🤍\n\n"
        "Команды:\n"
        "/style — текущий стиль\n"
        "/style <name> — сменить стиль\n"
        "/mmode — режим памяти\n"
        "/reset — очистить диалог\n"
        "/stats — статистика"
    )


@router.message(Command("style"))
async def style_cmd(message: Message):
    dialog = get_dialog(message)
    parts = message.text.split(maxsplit=1)

    if len(parts) == 1:
        await message.answer(
            f"🎨 Текущий стиль: <b>{dialog['style']}</b>\n\n"
            "Доступные стили:\n"
            + "\n".join(f"• {k}" for k in STYLE_PROMPTS)
        )
        return

    style_name = parts[1].strip()
    if style_name not in STYLE_PROMPTS:
        await message.answer("❌ Неизвестный стиль")
        return

    dialog["style"] = style_name
    dialog["updated_at"] = datetime.utcnow()

    await message.answer(f"🎨 Стиль изменён на <b>{style_name}</b>")


@router.message(Command("mmode"))
async def mmode_cmd(message: Message):
    dialog = get_dialog(message)

    dialog["mmode"] = (
        "stateless"
        if dialog["mmode"] == "history"
        else "history"
    )
    dialog["updated_at"] = datetime.utcnow()

    await message.answer(
        "🧠 Режим памяти изменён\n"
        f"Теперь: <b>{dialog['mmode']}</b>"
    )


@router.message(Command("reset"))
async def reset_cmd(message: Message):
    dialog = get_dialog(message)

    dialog["messages"].clear()
    dialog["updated_at"] = datetime.utcnow()

    await message.answer("♻️ Диалог очищен")


@router.message(Command("stats"))
async def stats_cmd(message: Message):
    dialog = get_dialog(message)

    await message.answer(
        "📊 Статистика диалога:\n"
        f"Сообщений: {len(dialog['messages'])}\n"
        f"Стиль: {dialog['style']}\n"
        f"Режим памяти: {dialog['mmode']}"
    )


# ─────────────────────────────
# Main handler
# ─────────────────────────────

@router.message()
async def message_handler(message: Message):
    dialog = get_dialog(message)
    user_text = message.text

    messages = build_messages(dialog, user_text)

    try:
        response = GenerationService.generate(
            messages=messages
        )
    except Exception as e:
        logging.exception("Generation error")
        await message.answer("⚠️ Ошибка генерации")
        return

    answer = response["content"]

    await message.answer(answer)

    if dialog["mmode"] == "history":
        dialog["messages"].extend([
            {"role": "user", "content": user_text},
            {"role": "assistant", "content": answer},
        ])
        dialog["updated_at"] = datetime.utcnow()


# ─────────────────────────────
# Entrypoint
# ─────────────────────────────

async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    logging.info("Бот запускается… 🤍")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
