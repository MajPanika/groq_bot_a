import time
from typing import Optional, Dict, List


class MemoryStore:
    def __init__(self):
        # структура: {(chat_id, thread_id): dialog_data}
        self.dialogs: Dict[tuple[int, Optional[int]], dict] = {}

    # ---------- utils ----------

    def _get_dialog(self, chat_id: int, thread_id: Optional[int]) -> dict:
        key = (chat_id, thread_id)
        if key not in self.dialogs:
            self.dialogs[key] = {
                "messages": [],         # {"role": "user/assistant", "content": str, "timestamp": float}
                "style": "default",
                "memory_mode": True,
                "stats": {"last_used": time.time(), "count": 0},
            }
        return self.dialogs[key]

    # ---------- dialog management ----------

    def add_user_message(self, chat_id: int, thread_id: Optional[int], text: str):
        dialog = self._get_dialog(chat_id, thread_id)
        dialog["messages"].append({"role": "user", "content": text, "timestamp": time.time()})
        dialog["stats"]["last_used"] = time.time()
        dialog["stats"]["count"] += 1

    def add_assistant_message(self, chat_id: int, thread_id: Optional[int], text: str):
        dialog = self._get_dialog(chat_id, thread_id)
        dialog["messages"].append({"role": "assistant", "content": text, "timestamp": time.time()})
        dialog["stats"]["last_used"] = time.time()
        dialog["stats"]["count"] += 1

    def clear_dialog(self, chat_id: int, thread_id: Optional[int]):
        dialog = self._get_dialog(chat_id, thread_id)
        dialog["messages"] = []

    # ---------- style ----------

    def get_style(self, chat_id: int, thread_id: Optional[int]) -> str:
        dialog = self._get_dialog(chat_id, thread_id)
        return dialog["style"]

    def set_style(self, chat_id: int, thread_id: Optional[int], style: str):
        dialog = self._get_dialog(chat_id, thread_id)
        dialog["style"] = style

    # ---------- memory mode ----------

    def get_memory_mode(self, chat_id: int, thread_id: Optional[int]) -> bool:
        dialog = self._get_dialog(chat_id, thread_id)
        return dialog["memory_mode"]

    def toggle_memory_mode(self, chat_id: int, thread_id: Optional[int]) -> bool:
        dialog = self._get_dialog(chat_id, thread_id)
        dialog["memory_mode"] = not dialog["memory_mode"]
        return dialog["memory_mode"]

    # ---------- stats ----------

    def get_stats(self) -> dict:
        return {
            "total_dialogs": len(self.dialogs),
            "dialogs": {k: v["stats"] for k, v in self.dialogs.items()}
        }

    def list_dialogs(self) -> List[tuple[int, Optional[int]]]:
        return list(self.dialogs.keys())

    # ---------- garbage collection ----------

    def gc(self, ttl_seconds: float = 3600):
        now = time.time()
        to_delete = [k for k, v in self.dialogs.items() if now - v["stats"]["last_used"] > ttl_seconds]
        for k in to_delete:
            del self.dialogs[k]
