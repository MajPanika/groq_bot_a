import time
from collections import OrderedDict
from typing import Dict, List, Optional


class InMemoryChatStore:
    def __init__(
        self,
        max_dialogs_per_user: int = 10,
        max_messages_per_dialog: int = 50
    ):
        self.dialogs: Dict[str, dict] = {}
        self.user_dialogs: Dict[int, OrderedDict] = {}

        self.max_dialogs_per_user = max_dialogs_per_user
        self.max_messages_per_dialog = max_messages_per_dialog

    # -------------------------
    # dialogs
    # -------------------------
    def exists(self, key: str) -> bool:
        return key in self.dialogs

    def create_dialog(self, key: str, user_id: int):
        now = time.time()

        self.dialogs[key] = {
            "messages": [],
            "meta": {
                "style": None,
                "created_at": now,
                "last_used": now,
            }
        }

        dialogs = self.user_dialogs.setdefault(user_id, OrderedDict())
        dialogs[key] = now

        self._enforce_dialog_limit(user_id)

    def _enforce_dialog_limit(self, user_id: int):
        dialogs = self.user_dialogs[user_id]

        while len(dialogs) > self.max_dialogs_per_user:
            oldest_key, _ = dialogs.popitem(last=False)
            self.dialogs.pop(oldest_key, None)

    # -------------------------
    # messages
    # -------------------------
    def add_message(self, key: str, role: str, content: str):
        dialog = self.dialogs[key]
        dialog["messages"].append(
            {"role": role, "content": content}
        )

        dialog["meta"]["last_used"] = time.time()

        if len(dialog["messages"]) > self.max_messages_per_dialog:
            dialog["messages"] = dialog["messages"][-self.max_messages_per_dialog :]

    def get_messages(self, key: str) -> List[dict]:
        return self.dialogs[key]["messages"]

    def clear(self, key: str):
        if key in self.dialogs:
            self.dialogs[key]["messages"] = []

    # -------------------------
    # meta
    # -------------------------
    def get_meta(self, key: str) -> dict:
        return self.dialogs.get(key, {}).get("meta", {})

    def update_meta(self, key: str, **kwargs):
        if key not in self.dialogs:
            return
        self.dialogs[key]["meta"].update(kwargs)

    # -------------------------
    # styles
    # -------------------------
    def get_user_styles(self, user_id: int) -> Dict[str, str]:
        # задел под будущее
        return {}

    # -------------------------
    # stats
    # -------------------------
    def get_stats(self) -> dict:
        return {
            "dialogs": len(self.dialogs),
            "users": len(self.user_dialogs),
            "messages": sum(
                len(d["messages"]) for d in self.dialogs.values()
            ),
        }


# singleton
chat_store = InMemoryChatStore()
