import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramNetworkError


async def send_discount_reminder(bot: Bot, chat_id: int, delay: int, text: str):
    await asyncio.sleep(delay)
    try:
        await bot.send_message(chat_id, text)
        logging.info(f"Жеңілдік туралы хабарлама чатқа жіберілді {chat_id}")
    except TelegramNetworkError as e:
        logging.error(f"Жеңілдік туралы хабарламаны жіберуде ақау: {e}")
    except Exception as e:
        logging.error(f"Жеңілдік туралы хабарламаны жіберуде ақау: {e}")

async def schedule_discount_reminders(bot: Bot, chat_id: int):
    asyncio.create_task(send_discount_reminder(bot, chat_id, 30 * 60, "Курсқа жеңілдікпен жазылуға 30 минут қалды! Курска жазылып үлгер, деңгейіңді көтер! 😊"))
    asyncio.create_task(send_discount_reminder(bot, chat_id, 45 * 60, "Досым жеңілдіктің бітуіне 15 минут қалды! Жеңілдікпен курсқа жазылып қал! 🚀"))
    asyncio.create_task(send_discount_reminder(bot, chat_id, 55 * 60, "Туысқан жеңілдіктің бітуіне 5 минут қалды! Жеңілдікпен курсқа жазыл 😘"))
    asyncio.create_task(send_discount_reminder(bot, chat_id, 60 * 60, "Уақыт аяқталды! Бірақ курсқа жеңілдікпен әліде жазылуға болады, сәттілік 🤪"))