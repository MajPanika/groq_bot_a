import os

from dotenv import load_dotenv

from memory_store import MemoryStore
from groq_client import GroqClient
from generation_service import GenerationService
from telegram_bot import TelegramBot


def main():
    load_dotenv()

    telegram_token = os.getenv("TELEGRAM_TOKEN")
    groq_api_key = os.getenv("GROQ_API_KEY")

    if not telegram_token:
        raise RuntimeError("TELEGRAM_TOKEN is not set")

    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    # 1️⃣ core services (singletons)
    memory_store = MemoryStore()
    groq_client = GroqClient(api_key=groq_api_key)

    generation_service = GenerationService(
        memory_store=memory_store,
        groq_client=groq_client,
        max_history_messages=20,
    )

    # 2️⃣ telegram bot
    bot = TelegramBot(
        token=telegram_token,
        memory_store=memory_store,
        generation_service=generation_service,
    )

    # 3️⃣ run
    bot.run()


if __name__ == "__main__":
    main()
