from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from crud import test_crud
from handlers.subscribe import CHANNELS
from keyboards.subscribe import subscribe_kb
from keyboards.subscribe import test_start_kb
from keyboards.video import video_kb


router = Router()

@router.callback_query(F.data == "real_start_test")
async def start_test(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    user_id = callback.from_user.id
    not_subscribed = []

    for channel in CHANNELS:
        try:
            chat_member = await bot.get_chat_member(channel, user_id)
            if chat_member.status in ["left", "kicked"]:
                not_subscribed.append(channel)
        except Exception as e:
            not_subscribed.append(channel)

    if not_subscribed:
        await callback.message.answer(
            "❌ Сен келесі каналдарға әлі жазылмадың:\n" + "\n".join(not_subscribed),
            reply_markup=subscribe_kb()
        )
        return

    user_id_str = str(user_id)
    student = await test_crud.get_student_by_telegram_id(user_id_str)
    if not student:
        await callback.message.answer("❌ Сен тіркелмегенсің!")
        return

    tests = await test_crud.get_tests_by_direction(student.direction_id)
    if not tests:
        await callback.message.answer("❌ Бұл бағытта тест жоқ")
        return

    await state.update_data(
        tests=[t.id for t in tests],
        current=0,
        correct=0
    )

    await send_question(callback.message, state)


async def send_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    test_ids = data["tests"]
    current = data["current"]

    if current >= len(test_ids):
        await finish_test(message, state)
        return

    test = await test_crud.get_test_by_id(test_ids[current])
    answers = await test_crud.get_answers_by_test(test.id)

    options = [a.text for a in answers]
    correct_option_id = next(
        (i for i, a in enumerate(answers) if a.is_correct), None
    )

    await message.answer_poll(
        question=test.question,
        options=options,
        type="quiz",
        correct_option_id=correct_option_id,
        is_anonymous=False
    )


@router.poll_answer()
async def handle_poll_answer(poll: types.PollAnswer, state: FSMContext):
    data = await state.get_data()
    current = data["current"]
    test_ids = data["tests"]

    test = await test_crud.get_test_by_id(test_ids[current])
    answers = await test_crud.get_answers_by_test(test.id)

    correct_option_id = next(
        (i for i, a in enumerate(answers) if a.is_correct), None
    )
    chosen = poll.option_ids[0] if poll.option_ids else None

    correct = data["correct"]
    if chosen == correct_option_id:
        correct += 1

    await state.update_data(
        current=current + 1,
        correct=correct
    )

    bot: Bot = poll.bot
    chat_id = poll.user.id
    await send_question(await bot.send_message(chat_id, "Келесі сұрақ 👇"), state)


async def finish_test(message: types.Message, state: FSMContext):
    data = await state.get_data()
    correct = data["correct"]
    total = len(data["tests"])

    if total != 10:
        await message.answer("Тест дайындалуда, кішкене күте тұр 😉")
        await state.clear()
        return

    if correct <= 3:
        rating_name = "A"
    elif 4 <= correct <= 6:
        rating_name = "B"
    else:
        rating_name = "C"

    student = await test_crud.get_student_by_telegram_id(str(message.chat.id))
    if not student:
        await message.answer("❌ Техникалық ақау, абитуриент табылмады")
        await state.clear()
        return

    rating = await test_crud.get_rating(rating_name)
    if not rating:
        await message.answer(f"Т❌ Техникалық ақау: Деңгей {rating_name} табылмады!")
        await state.clear()
        return

    await test_crud.save_student_result(student.id, rating.id)

    video = await test_crud.get_video_by_rating_and_direction(rating.id, student.direction_id)
    video_message = (
        f"🎥 Сенің  деңгейіңе арналған сынақ сабағы ({rating_name}): {video.title}\n"
        f"Сілтеме: {video.url}" if video else "❌ Сенің деңгейіңе арналған бейнежазба табылмады."
    )

    await message.answer(
        f"✅ Тест аяқталды! Сен {correct}/{total} дұрыс жауап бердің 🎉\n"
        f"Сенің деңгейің: {rating_name}\n"
        f"{video_message}",
        reply_markup=video_kb(video.url) if video else test_start_kb() 
    )
    await state.clear()