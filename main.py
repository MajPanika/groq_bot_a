import asyncio
from telegram_bot import dp, bot  # dp с хэндлерами уже подключен

# =====================
# Точка входа
# =====================
if __name__ == "__main__":
    print("Бот запускается... 🤍")
    try:
        # В aiogram 3.x используем метод start_polling у dispatcher
        asyncio.run(dp.start_polling(bot, skip_updates=True))
    except KeyboardInterrupt:
        print("Бот остановлен вручную")
    finally:
        # Закрываем сессию бота корректно
        asyncio.run(bot.session.close())
