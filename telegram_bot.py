from typing import Optional

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    MessageHandler,
    CommandHandler,
    filters,
)

from memory_store import MemoryStore
from generation_service import GenerationService


class TelegramBot:
    def __init__(
        self,
        token: str,
        memory_store: MemoryStore,
        generation_service: GenerationService,
    ):
        self.memory_store = memory_store
        self.generation_service = generation_service

        self.app = ApplicationBuilder().token(token).build()

        # commands
        self.app.add_handler(CommandHandler("reset", self.reset))
        self.app.add_handler(CommandHandler("mmode", self.toggle_memory_mode))
        self.app.add_handler(CommandHandler("style", self.style))

        # messages
        self.app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.on_message)
        )

    # ---------- utils ----------

    def _get_ids(self, update: Update) -> tuple[int, Optional[int]]:
        chat_id = update.effective_chat.id
        thread_id = update.effective_message.message_thread_id
        return chat_id, thread_id

    # ---------- handlers ----------

    async def reset(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id, thread_id = self._get_ids(update)
        self.memory_store.clear_dialog(chat_id, thread_id)
        await update.message.reply_text("🧹 История диалога очищена.")

    async def toggle_memory_mode(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id, thread_id = self._get_ids(update)
        new_mode = self.memory_store.toggle_memory_mode(chat_id, thread_id)
        status = "ON 🧠" if new_mode else "OFF 🚫"
        await update.message.reply_text(f"Memory mode: {status}")

    async def style(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id, thread_id = self._get_ids(update)

        if not context.args:
            current = self.memory_store.get_style(chat_id, thread_id)
            await update.message.reply_text(
                f"Текущий стиль: `{current}`",
                parse_mode="Markdown",
            )
            return

        new_style = context.args[0]
        self.memory_store.set_style(chat_id, thread_id, new_style)
        await update.message.reply_text(f"🎨 Стиль установлен: `{new_style}`", parse_mode="Markdown")

    async def on_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        chat_id, thread_id = self._get_ids(update)
        text = update.message.text

        reply = self.generation_service.generate(
            chat_id=chat_id,
            thread_id=thread_id,
            user_text=text,
        )

        await update.message.reply_text(reply)

    # ---------- run ----------
