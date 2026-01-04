import logging
from typing import Optional
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from memory_store import MemoryStore
from generation_service import GenerationService

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token: str, memory_store: MemoryStore, generation_service: GenerationService):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()
        self.memory_store = memory_store
        self.generation_service = generation_service

        self.dp.message.register(self.cmd_reset, Command("reset"))
        self.dp.message.register(self.cmd_mmode, Command("mmode"))
        self.dp.message.register(self.cmd_style, Command("style"))
        self.dp.message.register(self.on_message)

    @staticmethod
    def _get_ids(message: Message) -> tuple[int, Optional[int]]:
        chat_id = message.chat.id
        thread_id = message.message_thread_id
        return chat_id, thread_id

    async def cmd_reset(self, message: Message):
        chat_id, thread_id = self._get_ids(message)
        self.memory_store.clear_dialog(chat_id, thread_id)
        await message.answer("🧹 История диалога очищена.")

    async def cmd_mmode(self, message: Message):
        chat_id, thread_id = self._get_ids(message)
        new_mode = self.memory_store.toggle_memory_mode(chat_id, thread_id)
        status = "ON 🧠" if new_mode else "OFF 🚫"
        await message.answer(f"Memory mode: {status}")

    async def cmd_style(self, message: Message):
        chat_id, thread_id = self._get_ids(message)
        parts = message.text.split(maxsplit=1)
        if len(parts) == 1:
            current = self.memory_store.get_style(chat_id, thread_id)
            await message.answer(f"🎨 Текущий стиль: `{current}`", parse_mode="Markdown")
            return
        new_style = parts[1].strip()
        self.memory_store.set_style(chat_id, thread_id, new_style)
        await message.answer(f"🎨 Стиль установлен: `{new_style}`", parse_mode="Markdown")

    async def on_message(self, message: Message):
        if not message.text:
            return
        chat_id, thread_id = self._get_ids(message)
        user_text = message.text
        try:
            reply = self.generation_service.generate(chat_id, thread_id, user_text)
        except Exception as e:
            logger.exception("Generation failed")
            await message.answer("⚠️ Ошибка генерации ответа.")
            return
        await message.answer(reply)

    def run(self):
        logging.basicConfig(level=logging.INFO)
        self.dp.run_polling(self.bot)
