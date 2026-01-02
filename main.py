# main.py

import asyncio
from logger import setup_logger
from telegram_bot import bot, dp


async def main():
    setup_logger()
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
