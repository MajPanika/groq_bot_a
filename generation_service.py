from typing import Optional, List, Dict

from memory_store import MemoryStore
from groq_client import GroqClient
from config import STYLES


class GenerationService:
    def __init__(
        self,
        memory_store: MemoryStore,
        groq_client: GroqClient,
        max_history_messages: int = 20,
    ):
        self.memory_store = memory_store
        self.groq = groq_client
        self.max_history_messages = max_history_messages

    def generate(
        self,
        chat_id: int,
        thread_id: Optional[int],
        user_text: str,
    ) -> str:
        # 1️⃣ сохранить сообщение пользователя
        self.memory_store.add_user_message(chat_id, thread_id, user_text)

        # 2️⃣ собрать контекст
        messages = self._build_context(chat_id, thread_id, user_text)

        # 3️⃣ запрос к модели
        reply = self.groq.chat(messages)

        # 4️⃣ сохранить ответ ассистента
        self.memory_store.add_assistant_message(chat_id, thread_id, reply)

        return reply

    # ---------- internals ----------

    def _build_context(
        self,
        chat_id: int,
        thread_id: Optional[int],
        last_user_text: str,
    ) -> List[Dict[str, str]]:
        dialog = self.memory_store.get_dialog(chat_id, thread_id)

        style_name = dialog["style"]
        memory_mode = dialog["memory_mode"]

        system_prompt = self._get_system_prompt(style_name)

        context: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]

        if memory_mode:
            history = dialog["messages"][:-1]  # всё кроме последнего user
            if history:
                # жёсткий лимит по количеству сообщений
                history = history[-self.max_history_messages:]
                context.extend(
                    {"role": m["role"], "content": m["content"]}
                    for m in history
                )

        # последнее сообщение пользователя — ВСЕГДА
        context.append(
            {"role": "user", "content": last_user_text}
        )

        return context

    def _get_system_prompt(self, style_name: str) -> str:
        if style_name not in STYLES:
            return STYLES["default"]
        return STYLES[style_name]
