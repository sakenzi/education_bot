import logging
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramNetworkError
from crud import test_crud
from handlers.subscribe import CHANNELS
from keyboards.subscribe import subscribe_kb, test_start_kb
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
        try:
            await callback.message.answer(
                "Келесі каналдарға жазылып ал 👇:\n" + "\n".join(not_subscribed),
                reply_markup=subscribe_kb()
            )
        except TelegramNetworkError as e:
            await callback.message.answer("❌ Хабарды жіберу мүмкін болмады. Қайтадан байқап көр!")
        return

    user_id_str = str(user_id)
    student = await test_crud.get_student_by_telegram_id(user_id_str)
    if not student:
        try:
            await callback.message.answer("❌ Сен тіркелмегенсің!")
        except TelegramNetworkError as e:
            await callback.message.answer("❌ Хабарды жіберу мүмкін болмады. Қайтадан байқап көр")
        return

    tests = await test_crud.get_tests_by_direction(student.direction_id)
    if not tests or len(tests) < 10:
        try:
            await callback.message.answer("❌ Бұл бағытта тест жоқ или тесттер саны жеткіліксіз!")
        except TelegramNetworkError as e:
            await callback.message.answer("❌ Хабарды жіберу мүмкін болмады. Қайтадан байқап көр")
        return

    await state.update_data(
        tests=[t.id for t in tests],
        current=0,
        correct=0
    )

    await send_question(callback.message, state)

async def send_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    test_ids = data.get("tests", [])
    current = data.get("current", 0)

    if current >= len(test_ids):
        await finish_test(message, state)
        return

    test = await test_crud.get_test_by_id(test_ids[current])
    if not test:
        await state.update_data(current=current + 1)
        await send_question(message, state)
        return

    answers = await test_crud.get_answers_by_test(test.id)
    if len(answers) < 2:
        await state.update_data(current=current + 1)
        await send_question(message, state)
        return

    options = [a.text for a in answers]
    correct_option_id = next(
        (i for i, a in enumerate(answers) if a.is_correct), None
    )
    if correct_option_id is None:
        await state.update_data(current=current + 1)
        await send_question(message, state)
        return

    try:
        await message.answer_poll(
            question=test.question,
            options=options,
            type="quiz",
            correct_option_id=correct_option_id,
            is_anonymous=False,
            timeout=30
        )
    except TelegramNetworkError as e:
        await message.answer("❌ Хабарды жіберу мүмкін болмады. Қайтадан байқап көр")
        await state.update_data(current=current + 1)
        await send_question(message, state)

@router.poll_answer()
async def handle_poll_answer(poll: types.PollAnswer, state: FSMContext):
    data = await state.get_data()
    current = data.get("current", 0)
    test_ids = data.get("tests", [])

    test = await test_crud.get_test_by_id(test_ids[current])
    answers = await test_crud.get_answers_by_test(test.id)

    correct_option_id = next(
        (i for i, a in enumerate(answers) if a.is_correct), None
    )
    chosen = poll.option_ids[0] if poll.option_ids else None

    correct = data.get("correct", 0)
    if chosen == correct_option_id:
        correct += 1

    await state.update_data(
        current=current + 1,
        correct=correct
    )

    bot: Bot = poll.bot
    chat_id = poll.user.id
    try:
        await send_question(await bot.send_message(chat_id, "Келесі сұрақ 👇"), state)
    except TelegramNetworkError as e:
        await bot.send_message(chat_id, "❌ Хабарды жіберу мүмкін болмады. Қайтадан байқап көр")

async def finish_test(message: types.Message, state: FSMContext):
    data = await state.get_data()
    correct = data.get("correct", 0)
    total = len(data.get("tests", []))

    if total != 10:
        await message.answer("❌ Тесттер әлі дайын емес, кейінірек қайталап көр! 😉")
        await state.clear()
        return

    if correct <= 3:
        rating_name = "A"
        rating_text = "абитуриент деңгейің нашар, кем дегенде базаны үйреніп алшы 🙈"
    elif 4 <= correct <= 6:
        rating_name = "B"
        rating_text = "базаны жақсы білесің, бірақ баллыңды көбейту үшін мына бейнежазбаны қарап алшы 👌🏿"
    else:
        rating_name = "C"
        rating_text = "Жарайсың енді максимум балл алу үшін қиын бөлімдерді қарап шығу керек, мына бейнежазбаны қарап көрші ✌🏽"

    student = await test_crud.get_student_by_telegram_id(str(message.chat.id))
    if not student:
        await message.answer("❌ Техникалық ақау, абитуриент табылмады")
        await state.clear()
        return

    rating = await test_crud.get_rating(rating_name)
    if not rating:
        await message.answer(f"❌ Техникалық ақау: Деңгей {rating_name} табылмады!")
        await state.clear()
        return

    try:
        await test_crud.save_student_result(student.id, rating.id)
    except Exception as e:
        await message.answer("❌ Техникалық ақау при сохранении результата!")
        await state.clear()
        return

    video = await test_crud.get_video_by_rating_and_direction(rating.id, student.direction_id)
    video_message = (
        f"🎥 Сенің деңгейіңе арналған сынақ сабағы ({rating_name}): {video.title}\n"
        f"Сілтеме: {video.url}" if video else "❌ Сенің деңгейіңе арналған бейнежазба табылмады.\n"
        "Басқа сабақтарды көру үшін админмен байланыс!"
    )
    reply_markup = video_kb(video.url) if video else test_start_kb()

    try:
        await message.answer(
            f"✅ Тест аяқталды! Сен {correct}/{total} дұрыс жауап бердің 🎉\n"
            f"Сенің деңгейің: {rating_name} - {rating_text}\n"
            f"{video_message}",
            reply_markup=reply_markup
        )
        logging.info(f"Результат теста отправлен пользователю {message.from_user.id}")
    except TelegramNetworkError as e:
        logging.error(f"Сетевая ошибка при отправке результата: {e}")
        await message.answer(
            "❌ Желі қатесіне байланысты нәтиже жіберу мүмкін болмады. Әрекетті кейінірек қайтала",
            reply_markup=test_start_kb()
        )
    except Exception as e:
        await message.answer(
            "❌ Желі қатесіне байланысты нәтиже жіберу мүмкін болмады. Әрекетті кейінірек қайтала",
            reply_markup=test_start_kb()
        )

    await state.clear()