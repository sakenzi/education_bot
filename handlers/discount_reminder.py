import asyncio
import logging
from aiogram import Bot
from aiogram.exceptions import TelegramNetworkError


async def send_discount_reminder(bot: Bot, chat_id: int, delay: int, text: str):
    await asyncio.sleep(delay)
    try:
        await bot.send_message(chat_id, text)
        logging.info(f"Напоминание о скидке отправлено в чат {chat_id}")
    except TelegramNetworkError as e:
        logging.error(f"Сетевая ошибка при отправке напоминания о скидке: {e}")
    except Exception as e:
        logging.error(f"Ошибка при отправке напоминания о скидке: {e}")

async def schedule_discount_reminders(bot: Bot, chat_id: int):
    asyncio.create_task(send_discount_reminder(bot, chat_id, 15 * 60, "Курсқа жеңілдікпен жазылуға 15 минут қалды! Курска жазылып үлгер, деңгейіңді көтер! 😊"))
    asyncio.create_task(send_discount_reminder(bot, chat_id, 25 * 60, "Досым жеңілдіңтің бітуіне 5 минут қалды! Жеңілдікпен курсқа жазылып қал! 🚀"))
    asyncio.create_task(send_discount_reminder(bot, chat_id, 30 * 60, "Уақыт аяқталды! Бірақ курсқа жеңілдікпен әліде жазылуға болады, сәттілік 🤪"))