import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

DEFAULT_MODEL = "llama-3.1-8b-instant"

STYLES = {
    "default": "You are a helpful assistant.",
    "translator": "You are a professional translator. Translate accurately.",
    "coder": "You are an experienced software developer.",
    "concise": "Answer briefly and clearly.",
}

