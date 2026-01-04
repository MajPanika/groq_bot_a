from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import time


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
        self._dialogs: Dict[DialogKey, Dialog] = {}
        self.max_messages = max_messages

    # ---------- core ----------

    def _get_or_create(self, key: DialogKey) -> Dialog:
        if key not in self._dialogs:
            self._dialogs[key] = Dialog()
        dialog = self._dialogs[key]
        dialog.last_used = time.time()
        return dialog

    def clear(self, key: DialogKey) -> None:
        if key in self._dialogs:
            del self._dialogs[key]

    # ---------- style ----------

    def set_style(self, key: DialogKey, style: str) -> None:
        dialog = self._get_or_create(key)
        dialog.style = style

    def get_style(self, key: DialogKey) -> str:
        dialog = self._get_or_create(key)
        return dialog.style

    # ---------- memory mode ----------

    def toggle_memory_mode(self, key: DialogKey) -> bool:
        dialog = self._get_or_create(key)
        dialog.memory_enabled = not dialog.memory_enabled
        return dialog.memory_enabled

    def memory_enabled(self, key: DialogKey) -> bool:
        dialog = self._get_or_create(key)
        return dialog.memory_enabled

    # ---------- dialog ----------

    def add_user_message(self, key: DialogKey, text: str) -> None:
        dialog = self._get_or_create(key)
        if not dialog.memory_enabled:
            return

        dialog.messages.append({
            "role": "user",
            "content": text
        })
        self._trim(dialog)

    def add_bot_message(self, key: DialogKey, text: str) -> None:
        dialog = self._get_or_create(key)
        if not dialog.memory_enabled:
            return

        dialog.messages.append({
            "role": "assistant",
            "content": text
        })
        self._trim(dialog)

    def get_dialog(self, key: DialogKey) -> List[dict]:
        dialog = self._get_or_create(key)
        if not dialog.memory_enabled:
            return []
        return list(dialog.messages)

    def _trim(self, dialog: Dialog) -> None:
        if len(dialog.messages) > self.max_messages:
            dialog.messages = dialog.messages[-self.max_messages :]

    # ---------- stats ----------

    def stats(self, key: Optional[DialogKey] = None) -> str:
        if key:
            dialog = self._dialogs.get(key)
            if not dialog:
                return "Диалог не найден."

            return (
                f"🧠 Диалог\n"
                f"Стиль: {dialog.style}\n"
                f"Память: {'включена' if dialog.memory_enabled else 'выключена'}\n"
                f"Сообщений в памяти: {len(dialog.messages)}"
            )

        return (
            f"📊 Общая статистика\n"
            f"Диалогов: {len(self._dialogs)}"
        )

    # ---------- maintenance ----------

    def cleanup_old(self, max_age_seconds: int) -> int:
        now = time.time()
        to_delete = [
            key for key, dialog in self._dialogs.items()
            if now - dialog.last_used > max_age_seconds
        ]

        for key in to_delete:
            del self._dialogs[key]

        return len(to_delete)
