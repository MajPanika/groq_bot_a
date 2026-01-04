from config import STYLES

class GenerationService:
    def __init__(self, memory_store, groq_client, max_history_messages=20):
        self.memory_store = memory_store
        self.groq_client = groq_client
        self.max_history_messages = max_history_messages

    def generate(self, chat_id, thread_id, user_text: str) -> str:
        self.memory_store.add_user_message(chat_id, thread_id, user_text)

        dialog = self.memory_store._get_dialog(chat_id, thread_id)
        messages = []

        # system prompt
        style = dialog["style"]
        system_prompt = STYLES.get(style, STYLES["default"])
        messages.append({"role": "system", "content": system_prompt})

        # история
        if dialog["memory_mode"]:
            history = dialog["messages"][-self.max_history_messages:]
            messages.extend(history)

        # последнее сообщение пользователя
        messages.append({"role": "user", "content": user_text})

        # запрос к Groq
        reply = self.groq_client.chat(messages)

        self.memory_store.add_assistant_message(chat_id, thread_id, reply)

        return reply
