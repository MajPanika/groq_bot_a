from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple

DialogKey = Tuple[int, Optional[int]]  # (chat_id, thread_id)


class InMemoryChatStore:
    def __init__(self, max_messages: int = 20):
        self.dialogs: Dict[DialogKey, dict] = {}
        self.max_messages = max_messages

    # ---------- helpers ----------

    def _key(self, chat_id: int, thread_id: Optional[int]) -> DialogKey:
        return chat_id, thread_id

    def _get(self, chat_id: int, thread_id: Optional[int]) -> dict:
        key = self._key(chat_id, thread_id)
        if key not in self.dialogs:
            self.dialogs[key] = {
                "style": "default",
                "memory": True,
                "messages": [],
                "created": time.time(),
                "last_used": time.time(),
            }
        self.dialogs[key]["last_used"] = time.time()
        return self.dialogs[key]

    def _trim(self, dialog: dict):
        if len(dialog["messages"]) > self.max_messages:
            dialog["messages"] = dialog["messages"][-self.max_messages :]

    # ---------- style ----------

    def set_style(self, chat_id: int, thread_id: Optional[int], style: str):
        self._get(chat_id, thread_id)["style"] = style

    def get_style(self, chat_id: int, thread_id: Optional[int]) -> str:
        return self._get(chat_id, thread_id)["style"]

    # ---------- memory mode ----------

    def toggle_memory_mode(self, chat_id: int, thread_id: Optional[int]) -> bool:
        dialog = self._get(chat_id, thread_id)
        dialog["memory"] = not dialog["memory"]
        return dialog["memory"]

    def is_memory_enabled(self, chat_id: int, thread_id: Optional[int]) -> bool:
        return self._get(chat_id, thread_id)["memory"]

    # ---------- messages (ОБРАТНАЯ СОВМЕСТИМОСТЬ) ----------

    def add_user_message(
        self,
        chat_id: int,
        thread_id: Optional[int],
        text: Optional[str] = None,
    ):
        if not text:
            return
        dialog = self._get(chat_id, thread_id)
        if not dialog["memory"]:
            return
        dialog["messages"].append({"role": "user", "content": text})
        self._trim(dialog)

    def add_bot_message(
        self,
        chat_id: int,
        thread_id: Optional[int],
        text: Optional[str] = None,
    ):
        if not text:
            return
        dialog = self._get(chat_id, thread_id)
        if not dialog["memory"]:
            return
        dialog["messages"].append({"role": "assistant", "content": text})
        self._trim(dialog)

    def get_dialog(self, chat_id: int, thread_id: Optional[int]) -> List[dict]:
        dialog = self._get(chat_id, thread_id)
        if not dialog["memory"]:
            return []
        return list(dialog["messages"])

    # ---------- reset ----------

    def clear_dialog(self, chat_id: int, thread_id: Optional[int]):
        self.dialogs.pop(self._key(chat_id, thread_id), None)

    # ---------- stats ----------

    def stats(self, chat_id: int, thread_id: Optional[int]) -> str:
        dialog = self._get(chat_id, thread_id)
        return (
            f"🧠 Диалог\n"
            f"Стиль: {dialog['style']}\n"
            f"Память: {'on' if dialog['memory'] else 'off'}\n"
            f"Сообщений: {len(dialog['messages'])}"
        )


# ❗️КРИТИЧЕСКИ ВАЖНО
chat_store = InMemoryChatStore()
