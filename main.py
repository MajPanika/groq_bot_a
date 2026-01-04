import asyncio
from telegram_bot import bot, dp


async def main():
    print("Бот запускается... 🤍")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
