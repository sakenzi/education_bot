from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


switch_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Бейне сабақты ауыстыру", callback_data="switch_video")]
])

def video_kb(video_url: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎥 Бейнежазбаны қарау", url=video_url)],
    ])