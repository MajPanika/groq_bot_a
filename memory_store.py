# app/memory_store.py

from collections import defaultdict
from typing import List, Dict


class InMemoryChatStore:
    """
    Хранит историю сообщений по chat_id
    """
    def __init__(self):
        self._store: Dict[int, List[dict]] = defaultdict(list)

    def get_messages(self, chat_id: int) -> List[dict]:
        return self._store[chat_id]

    def add_message(self, chat_id: int, role: str, content: str):
        self._store[chat_id].append(
            {"role": role, "content": content}
        )

    def clear(self, chat_id: int):
        self._store[chat_id] = []


chat_store = InMemoryChatStore()
