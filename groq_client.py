import requests
import logging

logger = logging.getLogger(__name__)

class GroqClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        # ⚡ замените на актуальный endpoint из вашего аккаунта Groq
        self.base_url = "https://api.groq.ai/v1/chat"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(self, messages: list[dict]) -> str:
        """
        messages: [{"role": "user"/"assistant"/"system", "content": str}]
        Возвращает текст ответа от Groq.
        """
        payload = {"messages": messages}
        try:
            response = requests.post(self.base_url, json=payload, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # ⚡ подстрой под актуальную структуру ответа Groq
            return data.get("content", "") or "⚠️ Пустой ответ от Groq"
        except requests.exceptions.RequestException as e:
            logger.error(f"Groq API request failed: {e}")
            return "⚠️ Ошибка API"
