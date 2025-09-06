import asyncio
import logging
from aiogram import Bot, Dispatcher
from core.config import settings
from handlers import start, subscribe, test
from middlewares import RetryMiddleware


logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

async def main():
    dp.include_router(start.router)
    dp.include_router(subscribe.router)
    dp.include_router(test.router)

    dp.update.middleware(RetryMiddleware(retry_count=3, retry_delay=2.0))

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())