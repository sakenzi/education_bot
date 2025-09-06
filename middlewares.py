import asyncio
import logging
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.exceptions import TelegramNetworkError


class RetryMiddleware(BaseMiddleware):
    def __init__(self, retry_count: int = 3, retry_delay: float = 2.0):
        self.retry_count = retry_count
        self.retry_delay = retry_delay

    async def __call__(self, handler, event: TelegramObject, data: dict):
        for attempt in range(self.retry_count):
            try:
                return await handler(event, data)
            except TelegramNetworkError as e:
                logging.error(f"Сетевая ошибка: {e}, попытка {attempt + 1}/{self.retry_count}")
                if attempt + 1 == self.retry_count:
                    raise  
                await asyncio.sleep(self.retry_delay)
        return None