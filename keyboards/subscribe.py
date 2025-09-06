from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def subscribe_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="📢 1", url="https://t.me/testqa_arnalgan")],
        [InlineKeyboardButton(text="📢 2", url="https://t.me/testqa_arnalgan_kanal")],
        [InlineKeyboardButton(text="✅ Тіркелдім", callback_data="check_subs")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


def test_start_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 Тест өту", callback_data="real_start_test")]
    ])
