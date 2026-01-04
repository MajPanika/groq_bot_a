from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

DialogKey = Tuple[int, Optional[int]]  # (chat_id, thread_id)


@dataclass
class Dialog:
    style: str = "default"
    memory_enabled: bool = True
    messages: List[dict] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_used: float = field(default_factory=time.time)


class InMemoryChatStore:
    def __init__(self, max_messages: int = 20):
        self.dialogs: Dict[DialogKey, Dialog] = {}
        self.max_messages = max_messages

    # ---------- helpers ----------

    def _key(self, chat_id: int, thread_id: Optional[int]) -> DialogKey:
        return chat_id, thread_id

    def _get_or_create(self, chat_id: int, thread_id: Optional[int]) -> Dialog:
        key = self._key(chat_id, thread_id)
        if key not in self.dialogs:
            self.dialogs[key] = Dialog()
        dialog = self.dialogs[key]
        dialog.last_used = time.time()
        return dialog

    def _trim(self, dialog: Dialog):
        if len(dialog.messages) > self.max_messages:
            dialog.messages = dialog.messages[-self.max_messages :]

    # ---------- style ----------

    def set_style(self, chat_id: int, thread_id: Optional[int], style: str):
        dialog = self._get_or_create(chat_id, thread_id)
        dialog.style = style

    def get_style(self, chat_id: int, thread_id: Optional[int]) -> str:
        return self._get_or_create(chat_id, thread_id).style

    # ---------- memory mode ----------

    def toggle_memory_mode(self, chat_id: int, thread_id: Optional[int]) -> bool:
        dialog = self._get_or_create(chat_id, thread_id)
        dialog.memory_enabled = not dialog.memory_enabled
        return dialog.memory_enabled

    def is_memory_enabled(self, chat_id: int, thread_id: Optional[int]) -> bool:
        return self._get_or_create(chat_id, thread_id).memory_enabled

    # ---------- messages (ВАЖНО: контракт сохранён) ----------

    def add_user_message(self, chat_id: int, thread_id: Optional[int], text: str):
        dialog = self._get_or_create(chat_id, thread_id)
        if not dialog.memory_enabled:
            return

        dialog.messages.append({
            "role": "user",
            "content": text
        })
        self._trim(dialog)

    def add_bot_message(self, chat_id: int, thread_id: Optional[int], text: str):
        dialog = self._get_or_create(chat_id, thread_id)
        if not dialog.memory_enabled:
            return

        dialog.messages.append({
            "role": "assistant",
            "content": text
        })
        self._trim(dialog)

    def get_dialog(self, chat_id: int, thread_id: Optional[int]) -> List[dict]:
        dialog = self._get_or_create(chat_id, thread_id)
        if not dialog.memory_enabled:
            return []
        return list(dialog.messages)

    # ---------- reset ----------

    def clear_dialog(self, chat_id: int, thread_id: Optional[int]):
        key = self._key(chat_id, thread_id)
        if key in self.dialogs:
            del self.dialogs[key]

    # ---------- stats ----------

    def stats(self, chat_id: Optional[int] = None, thread_id: Optional[int] = None) -> str:
        if chat_id is not None:
            key = self._key(chat_id, thread_id)
            dialog = self.dialogs.get(key)
            if not dialog:
                return "Диалог не найден."

            return (
                f"🧠 Диалог\n"
                f"Стиль: {dialog.style}\n"
                f"Память: {'включена' if dialog.memory_enabled else 'выключена'}\n"
                f"Сообщений: {len(dialog.messages)}"
            )

        return f"📊 Всего диалогов: {len(self.dialogs)}"

    # ---------- cleanup ----------

    def cleanup_old(self, max_age_seconds: int) -> int:
        now = time.time()
        to_delete = [
            key for key, dialog in self.dialogs.items()
            if now - dialog.last_used > max_age_seconds
        ]
        for key in to_delete:
            del self.dialogs[key]
        return len(to_delete)


# 🔥 ВАЖНО: публичный singleton (его ждут импорты)
chat_store = InMemoryChatStore()
