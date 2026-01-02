from groq import Groq
from config import GROQ_API_KEY
import logging
logger = logging.getLogger("groq")


client = Groq(api_key=GROQ_API_KEY)


class GroqClient:

    @staticmethod
    def generate(model: str, messages: list):
        logger.info(f"Calling Groq model={model}")
        return client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.7,
        )

