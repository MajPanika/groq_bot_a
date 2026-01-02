import asyncio
from telegram_bot import dp  # Dispatcher с хэндлерами уже подключен

# =====================
# Точка входа
# =====================
if __name__ == "__main__":
    # asyncio.run нужен для асинхронного запуска aiogram
    from aiogram import executor
    from telegram_bot import bot

    print("Бот запускается... 🤍")
    try:
        from aiogram import executor
        executor.start_polling(dp, skip_updates=True)
    except KeyboardInterrupt:
        print("Бот остановлен вручную")
    finally:
        # Закрываем соединение бота корректно
        asyncio.run(bot.session.close())
