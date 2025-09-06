from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.subscribe import subscribe_kb, test_start_kb


router = Router()

CHANNELS = ["@testqa_arnalgan", "@testqa_arnalgan_kanal"]


@router.callback_query(F.data == "start_test")
async def ask_subscribe(callback: CallbackQuery):
    await callback.message.answer(
        "Алдымен келесі каналдарға жазыл 👇",
        reply_markup=subscribe_kb()
    )


@router.callback_query(F.data == "check_subs")
async def check_subscriptions(callback: CallbackQuery, bot, state: FSMContext):
    user_id = callback.from_user.id
    not_subscribed = []

    for channel in CHANNELS:
        chat_member = await bot.get_chat_member(channel, user_id)
        if chat_member.status in ["left", "kicked"]:
            not_subscribed.append(channel)

    if not_subscribed:
        await callback.message.answer(
            "❌ Сен келесі каналдарға әлі жазылмадың:\n" + "\n".join(not_subscribed),
            reply_markup=subscribe_kb()
        )
    else:
        await callback.message.answer(
            "✅ Рахмет! Енді сен тестті өте аласың 🎉",
            reply_markup=test_start_kb()
        )
