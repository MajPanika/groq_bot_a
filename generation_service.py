import logging
from groq_client import GroqClient
from memory_store import chat_store

logger = logging.getLogger("generation")

DEFAULT_MODEL = "llama-3.1-8b-instant"


class GenerationService:

    @staticmethod
    def generate(text: str, chat_id: int) -> str:
        """
        Генерация ответа через Groq с in-memory историей
        """
        # Получаем историю чата
        history = chat_store.get_messages(chat_id)

        # Формируем сообщения для Groq
        messages = history + [{"role": "user", "content": text}]

        # Генерация через Groq
        response = GroqClient.generate(model=DEFAULT_MODEL, messages=messages)

        # Сохраняем в память
        chat_store.add_message(chat_id, "user", text)
        chat_store.add_message(
            chat_id, "assistant", response.choices[0].message.content
        )

        # Логируем токены
        usage = response.usage
        logger.info(
            f"Tokens used: in={usage.prompt_tokens}, "
            f"out={usage.completion_tokens}, "
            f"total={usage.total_tokens}"
        )

        return response.choices[0].message.content
