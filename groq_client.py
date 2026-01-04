import requests

class GroqClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.groq.com/v1/chat"  # актуальный endpoint Groq
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def chat(self, messages: list[dict]) -> str:
        payload = {"messages": messages}
        response = requests.post(self.base_url, json=payload, headers=self.headers)
        response.raise_for_status()
        data = response.json()
        return data.get("content", "")
