from __future__ import annotations

import time
from typing import Dict, List, Optional, Tuple, Union

DialogKey = Tuple[int, Optional[int]]


class InMemoryChatStore:
    def __init__(self, max_messages: int = 20):
        self.dialogs: Dict[DialogKey, dict] = {}
        self.max_messages = max_messages

    # ---------- helpers ----------

    def _normalize_key(
        self,
        chat_id: Union[int, DialogKey],
        thread_id: Optional[int] = None,
    ) -> DialogKey:
        if isinstance(chat_id, tuple):
            return chat_id
        return chat_id, thread_id

    def _get(self, key: DialogKey) -> dict:
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

    def set_style(self, chat_id, thread_id=None, style: str = "default"):
        key = self._normalize_key(chat_id, thread_id)
        self._get(key)["style"] = style

    def get_style(self, chat_id, thread_id=None) -> str:
        key = self._normalize_key(chat_id, thread_id)
        return self._get(key)["style"]

    # ---------- memory mode ----------

    def toggle_memory_mode(self, chat_id, thread_id=None) -> bool:
        key = self._normalize_key(chat_id, thread_id)
        dialog = self._get(key)
        dialog["memory"] = not dialog["memory"]
        return dialog["memory"]

    def is_memory_enabled(self, chat_id, thread_id=None) -> bool:
        key = self._normalize_key(chat_id, thread_id)
        return self._get(key)["memory"]

    # ---------- messages (backward compatible) ----------

    def add_user_message(self, chat_id, thread_id=None, text: Optional[str] = None):
        if not text:
            return
        key = self._normalize_key(chat_id, thread_id)
        dialog = self._get(key)
        if not dialog["memory"]:
            return
        dialog["messages"].append({"role": "user", "content": text})
        self._trim(dialog)

    def add_bot_message(self, chat_id, thread_id=None, text: Optional[str] = None):
        if not text:
            return
        key = self._normalize_key(chat_id, thread_id)
        dialog = self._get(key)
        if not dialog["memory"]:
            return
        dialog["messages"].append({"role": "assistant", "content": text})
        self._trim(dialog)

    # ---------- dialog access ----------

    def get_dialog(self, chat_id, thread_id=None) -> List[dict]:
        key = self._normalize_key(chat_id, thread_id)
        dialog = self._get(key)
        if not dialog["memory"]:
            return []
        return list(dialog["messages"])

    # ---------- reset (ALL ALIASES) ----------

    def clear(self, chat_id, thread_id=None):
        key = self._normalize_key(chat_id, thread_id)
        self.dialogs.pop(key, None)

    def clear_dialog(self, chat_id, thread_id=None):
        self.clear(chat_id, thread_id)

    # ---------- stats ----------

    def stats(self, chat_id, thread_id=None) -> str:
        key = self._normalize_key(chat_id, thread_id)
        dialog = self._get(key)
        return (
            f"🧠 Диалог\n"
            f"Стиль: {dialog['style']}\n"
            f"Память: {'on' if dialog['memory'] else 'off'}\n"
            f"Сообщений: {len(dialog['messages'])}"
        )


# ❗ ОБЯЗАТЕЛЬНО
chat_store = InMemoryChatStore()
