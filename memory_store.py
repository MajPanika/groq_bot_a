import time
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


DialogKey = Tuple[int, Optional[int]]


class MemoryStore:
    def __init__(self):
        self._dialogs: Dict[DialogKey, dict] = {}

    # ---------- core ----------

    def get_dialog(self, chat_id: int, thread_id: Optional[int]) -> dict:
        key = (chat_id, thread_id)
        if key not in self._dialogs:
            self._dialogs[key] = self._new_dialog()
        self._dialogs[key]["stats"]["last_used"] = time.time()
        return self._dialogs[key]

    def clear_dialog(self, chat_id: int, thread_id: Optional[int]) -> None:
        dialog = self.get_dialog(chat_id, thread_id)
        dialog["messages"].clear()

    # ---------- messages ----------

    def add_user_message(self, chat_id: int, thread_id: Optional[int], text: str) -> None:
        dialog = self.get_dialog(chat_id, thread_id)
        dialog["messages"].append({
            "role": "user",
            "content": text,
            "ts": time.time(),
        })
        dialog["stats"]["user_messages"] += 1
        dialog["stats"]["total_messages"] += 1

    def add_assistant_message(self, chat_id: int, thread_id: Optional[int], text: str) -> None:
        dialog = self.get_dialog(chat_id, thread_id)
        dialog["messages"].append({
            "role": "assistant",
            "content": text,
            "ts": time.time(),
        })
        dialog["stats"]["assistant_messages"] += 1
        dialog["stats"]["total_messages"] += 1

    # ---------- style ----------

    def get_style(self, chat_id: int, thread_id: Optional[int]) -> str:
        return self.get_dialog(chat_id, thread_id)["style"]

    def set_style(self, chat_id: int, thread_id: Optional[int], style: str) -> None:
        self.get_dialog(chat_id, thread_id)["style"] = style

    # ---------- memory mode ----------

    def get_memory_mode(self, chat_id: int, thread_id: Optional[int]) -> bool:
        return self.get_dialog(chat_id, thread_id)["memory_mode"]

    def toggle_memory_mode(self, chat_id: int, thread_id: Optional[int]) -> bool:
        dialog = self.get_dialog(chat_id, thread_id)
        dialog["memory_mode"] = not dialog["memory_mode"]
        return dialog["memory_mode"]

    # ---------- admin ----------

    def list_dialogs(self) -> List[dict]:
        result = []
        for (chat_id, thread_id), dialog in self._dialogs.items():
            result.append({
                "chat_id": chat_id,
                "thread_id": thread_id,
                "style": dialog["style"],
                "memory_mode": dialog["memory_mode"],
                "last_used": dialog["stats"]["last_used"],
                "messages": len(dialog["messages"]),
            })
        return result

    def get_stats(self) -> dict:
        dialogs = len(self._dialogs)
        total_messages = sum(d["stats"]["total_messages"] for d in self._dialogs.values())
        memory_on = sum(1 for d in self._dialogs.values() if d["memory_mode"])
        memory_off = dialogs - memory_on

        return {
            "dialogs": dialogs,
            "total_messages": total_messages,
            "memory_on": memory_on,
            "memory_off": memory_off,
        }

    def gc(self, ttl_seconds: int = 3600) -> int:
        now = time.time()
        to_delete = [
            key for key, dialog in self._dialogs.items()
            if now - dialog["stats"]["last_used"] > ttl_seconds
        ]
        for key in to_delete:
            del self._dialogs[key]
        return len(to_delete)

    # ---------- internals ----------

    def _new_dialog(self) -> dict:
        return {
            "messages": [],
            "style": "default",
            "memory_mode": True,
            "stats": {
                "created": time.time(),
                "last_used": time.time(),
                "user_messages": 0,
                "assistant_messages": 0,
                "total_messages": 0,
            },
        }
