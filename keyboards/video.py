from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def video_kb(video_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Бейнежазбаны қарау", url=video_url)],
        [InlineKeyboardButton(text="📘 Тестты қайтадан өту", callback_data="real_start_test")]
    ])