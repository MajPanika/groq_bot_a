import logging
from typing import Optional

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message

from memory_store import MemoryStore
from generation_service import GenerationService

logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(
        self,
        token: str,
        memory_store: MemoryStore,
        generation_service: GenerationService,
    ):
        self.bot = Bot(token=token)
        self.dp = Dispatcher()

        self.memory_store = memory_store
        self.generation_service = generation_service

        # commands
        self.dp.message.register(self.cmd_reset, Command("reset"))
        self.dp.message.register(self.cmd_mmode, Command("mmode"))
        self.dp.message.register(self.cmd_style, Command("style"))

        # messages
        self.dp.message.register(self.on_message)

    # ---------- utils ----------

    @staticmethod
    def _get_ids(message: Message) -> tuple[int, Optional[int]]:
        chat_id = message.chat.id
        thread_id = message.message_thread_id
        return chat_id, thread_id

    # ---------- handlers ----------

    async def cmd_reset(self, message: Message):
        chat_id, thread_id = self._get_ids(message)
        self.memory_store.clear_dial
