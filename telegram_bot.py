import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from config import TELEGRAM_TOKEN
from generation_service import GenerationService
from memory_store import chat_store

# =====================
# Логгер
# =====================
logger = logging.getLogger("telegram")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# =====================
# Инициализация бота
# =====================
bot = Bot(
    token=TELEGRAM_TOKEN,
    parse_mode=ParseMode.MARKDOWN
)
dp = Dispatcher(bot, storage=MemoryStorage())  # обязательно передаем bot в Dispatcher

# =====================
# Хэндлер /reset
# =====================
@dp.message_handler(commands=["reset"])
async def reset_chat(message: types.Message):
    """
    Очищает память текущего чата
    """
    chat_store.clear(message.chat.id)
    await message.reply("Контекст этого диалога сброшен ✨")

# =====================
# Хэндлер /start
# =====================
@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Я живой 🤍\nНапиши что-нибудь.")

# =====================
# Основной хэндлер сообщений
# =====================
@dp.message()
async def handle_message(message: Message):
    logger.info(f"Message from {message.from_user.id}: {message.text[:50]}")

    response = GenerationService.generate(
        text=message.text,
        chat_id=message.chat.id
    )

    await message.answer(response)
