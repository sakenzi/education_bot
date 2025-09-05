from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db.models import Direction
from db.database import async_session_factory


# Кнопка отправки номера
phone_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Телефон номермен бөлісу", request_contact=True)]],
    resize_keyboard=True
)

# Динамическая клавиатура направлений
async def directions_kb():
    async with async_session_factory() as session:
        result = await session.execute(Direction.__table__.select())
        directions = result.fetchall()

        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=row.name)] for row in directions],
            resize_keyboard=True
        )