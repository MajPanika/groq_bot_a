from config import DEFAULT_MODEL
from groq_client import GroqClient
import logging
logger = logging.getLogger("generation")
from memory_store import chat_store


class GenerationService:

    @staticmethod
def generate(text: str, chat_id: int) -> str:
    history = chat_store.get_messages(chat_id)

    messages = history + [
        {"role": "user", "content": text}
    ]

    response = GroqClient.generate(
        model=DEFAULT_MODEL,
        messages=messages
    )

    chat_store.add_message(chat_id, "user", text)
    chat_store.add_message(
        chat_id,
        "assistant",
        response.choices[0].message.content
    )

    return response.choices[0].message.content

