from config import DEFAULT_MODEL
from groq_client import GroqClient


class GenerationService:

    @staticmethod
    def generate(text: str) -> str:
        messages = [
            {"role": "user", "content": text}
        ]

        response = GroqClient.generate(
            model=DEFAULT_MODEL,
            messages=messages
        )

        # логируем токены
        usage = response.usage
        print(
            f"[TOKENS] input={usage.prompt_tokens} "
            f"output={usage.completion_tokens} "
            f"total={usage.total_tokens}"
        )

        return response.choices[0].message.content
