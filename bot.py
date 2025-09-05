import asyncio
import logging
from aiogram import Bot, Dispatcher
from core.config import settings
from handlers import start


logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(start.router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())