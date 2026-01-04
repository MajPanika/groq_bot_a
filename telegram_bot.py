import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from aiogram.enums import ParseMode

from config import TELEGRAM_TOKEN
from generation_service import GenerationService
from memory_store import chat_store


# -------------------------------------------------------------------
# logging
# -------------------------------------------------------------------

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("telegram")


# -------------------------------------------------------------------
# bot / dispatcher / router
# -------------------------------------------------------------------

bot = Bot(
    token=TELEGRAM_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)

dp = Dispatcher()
router = Router()
dp.include_router(router)


# -------------------------------------------------------------------
# helpers
# -------------------------------------------------------------------

def dialog_key(message: types.Message) -> str:
    """
    Уникальный ключ диалога:
    chat_id + thread_id (темы Telegram)
    """
    return f"{message.chat.id}:{message.message_thread_id or 0}"


# -------------------------------------------------------------------
# commands
# -------------------------------------------------------------------

@router.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Я живой 🤍\n"
        "Напиши что-нибудь.\n\n"
        "/style — текущий стиль\n"
        "/mmode — режим памяти\n"
        "/reset — сброс диалога\n"
        "/stats — статистика"
    )


@router.message(Command("reset"))
async def reset_chat(message: types.Message):
    key = dialog_key(message)
    chat_store.clear(key)
    await message.answer("Контекст этого диалога сброшен ✨")


@router.message(Command("stats"))
async def stats(message: types.Message):
    key = dialog_key(message)
    stats = chat_store.stats(key)

    if not stats:
        await message.answer("Статистика пуста")
        return

    await message.answer(
        f"📊 *Статистика диалога*\n"
        f"Сообщений: {stats['messages']}\n"
        f"Символов: {stats['chars']}\n"
        f"Создан: {stats['created_at']}"
    )


@router.message(Command("mmode"))
async def memory_mode_toggle(message: types.Message):
    key = dialog_key(message)
    mode = chat_store.toggle_memory_mode(key)

    await message.answer(
        "🧠 Режим памяти: *ВКЛ*" if mode else "🧠 Режим памяти: *ВЫКЛ*"
    )


@router.message(Command("style"))
async def style_info(message: types.Message):
    key = dialog_key(message)
    style = chat_store.get_style(key)

    await message.answer(
        f"🎭 *Текущий стиль:*\n{style}\n\n"
        "Чтобы задать новый стиль:\n"
        "`/newstyle текст стиля`"
    )


@router.message(Command("newstyle"))
async def new_style(message: types.Message):
    key = dialog_key(message)
    text = message.text.replace("/newstyle", "").strip()

    if not text:
        await message.answer("Опиши стиль после команды.")
        return

    chat_store.set_style(key, text)
    await message.answer("✨ Новый стиль установлен")


# -------------------------------------------------------------------
# messages
# -------------------------------------------------------------------

@router.message()
async def handle_message(message: types.Message):
    key = dialog_key(message)

    logger.info(
        f"chat={message.chat.id} "
        f"thread={message.message_thread_id} "
        f"user={message.from_user.id}"
    )

    chat_store.add_user_message(key, message.text)

    try:
        response = GenerationService.generate(
            dialog=chat_store.get_dialog(key),
            system_prompt=chat_store.get_style(key),
            memory_enabled=chat_store.memory_enabled(key)
        )
    except Exception as e:
        logger.exception("Generation error")
        await message.answer("⚠️ Ошибка генерации, попробуй позже")
        return

    chat_store.add_bot_message(key, response)
    await message.answer(response)
