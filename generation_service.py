from config import DEFAULT_MODEL
from groq_client import GroqClient
import logging
logger = logging.getLogger("generation")


class GenerationService:

    @staticmethod
    def generate(text: str) -> str:
        logger.info("Generating response")

        messages = [{"role": "user", "content": text}]
        response = GroqClient.generate(DEFAULT_MODEL, messages)

        usage = response.usage
        logger.info(
            f"Tokens used: "
            f"in={usage.prompt_tokens}, "
            f"out={usage.completion_tokens}, "
            f"total={usage.total_tokens}"
        )

        return response.choices[0].message.content

