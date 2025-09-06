from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def subscribe_kb() -> InlineKeyboardMarkup:
    kb = [
        [InlineKeyboardButton(text="📢 ҰБТ мықтылар үшін", url="https://t.me/testqa_arnalgan")],
        [InlineKeyboardButton(text="📢 ҰБТ әлсіздерге арналмалмаған", url="https://t.me/testqa_arnalgan_kanal")],
        [InlineKeyboardButton(text="✅ Тіркелдім", callback_data="check_subs")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)

def test_start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📘 Тестті бастау", callback_data="real_start_test")]
    ])

def start_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Каналдарға жазылу", callback_data="start_test")]
    ])