import logging
import asyncio
from aiogram import Router, F, types, Bot
from aiogram.types import FSInputFile
from keyboards.course import course_button
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramNetworkError
from crud import test_crud
from handlers.subscribe import CHANNELS
from keyboards.subscribe import subscribe_kb, test_start_kb
from keyboards.video import video_kb
from handlers.discount_reminder import schedule_discount_reminders
from datetime import datetime, timedelta

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
        correct=0,
        first_half_correct=0,
        second_half_correct=0
    )
    await send_question(callback.message, state, bot)

async def send_question(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    test_ids = data.get("tests", [])
    current = data.get("current", 0)

    if current >= len(test_ids):
        await finish_test(message, state, bot)
        return

    test = await test_crud.get_test_by_id(test_ids[current])
    if not test:
        await state.update_data(current=current + 1)
        await send_question(message, state, bot)
        return

    answers = await test_crud.get_answers_by_test(test.id)
    if len(answers) < 2:
        await state.update_data(current=current + 1)
        await send_question(message, state, bot)
        return

    options = [a.text for a in answers]
    correct_option_id = next((i for i, a in enumerate(answers) if a.is_correct), None)
    if correct_option_id is None:
        await state.update_data(current=current + 1)
        await send_question(message, state, bot)
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
        await send_question(message, state, bot)

@router.poll_answer()
async def handle_poll_answer(poll: types.PollAnswer, state: FSMContext, bot: Bot):
    data = await state.get_data()
    current = data.get("current", 0)
    test_ids = data.get("tests", [])
    first_half_correct = data.get("first_half_correct", 0)
    second_half_correct = data.get("second_half_correct", 0)

    test = await test_crud.get_test_by_id(test_ids[current])
    answers = await test_crud.get_answers_by_test(test.id)

    correct_option_id = next((i for i, a in enumerate(answers) if a.is_correct), None)
    chosen = poll.option_ids[0] if poll.option_ids else None

    is_correct = chosen == correct_option_id

    if current < 5:
        first_half_correct += 1 if is_correct else 0
    else:
        second_half_correct += 1 if is_correct else 0

    total_correct = data.get("correct", 0) + (1 if is_correct else 0)

    await state.update_data(
        current=current + 1,
        correct=total_correct,
        first_half_correct=first_half_correct,
        second_half_correct=second_half_correct
    )

    chat_id = poll.user.id
    try:
        await send_question(await bot.send_message(chat_id, "Келесі сұрақ 👇"), state, bot)
    except TelegramNetworkError as e:
        await bot.send_message(chat_id, "❌ Хабарды жіберу мүмкін болмады. Қайтадан байқап көр")

async def finish_test(message: types.Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    correct = data.get("correct", 0)
    total = len(data.get("tests", []))
    first_half_correct = data.get("first_half_correct", 0)
    second_half_correct = data.get("second_half_correct", 0)

    if total != 10:
        try:
            await message.answer("❌ Тесттер әлі дайын емес, кейінірек қайталап көр! 😉")
        except TelegramNetworkError as e:
            logging.error(f"Хабарды жіберу кезіндегі желілік ақау: {e} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await state.clear()
        return

    if first_half_correct <= 2:
        first_rating_name = "A"
    elif first_half_correct == 3:
        first_rating_name = "B"
    else:
        first_rating_name = "C"

    if second_half_correct <= 2:
        second_rating_name = "A"
    elif second_half_correct == 3:
        second_rating_name = "B"
    else:
        second_rating_name = "C"

    student = await test_crud.get_student_by_telegram_id(str(message.chat.id))
    if not student:
        try:
            await message.answer("❌ Техникалық ақау, абитуриент табылмады")
        except TelegramNetworkError as e:
            logging.error(f"Хабарды жіберу кезіндегі желілік ақау: {e} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await state.clear()
        return

    first_rating = await test_crud.get_rating(first_rating_name)
    second_rating = await test_crud.get_rating(second_rating_name)

    if first_rating and second_rating:
        first_videos = await test_crud.get_videos_by_rating_and_direction(first_rating.id, student.direction_id)
        second_videos = await test_crud.get_videos_by_rating_and_direction(second_rating.id, student.direction_id)

        first_video = first_videos[0] if first_videos else None
        second_video = first_videos[1] if len(first_videos) > 1 else second_videos[0] if second_videos else None
    else:
        first_video = None
        second_video = None

    if first_rating:
        await test_crud.save_student_result(student.id, first_rating.id)

    try:
        await message.answer(
            f"✅ Тест аяқталды! Сен {correct}/{total} дұрыс жауап бердің 🎉\n\n"
            f"Бірінші таңдау пән бойынша: {first_half_correct}/5 ({first_rating_name} деңгей)\n"
            f"Екінші таңдау пән бойынша: {second_half_correct}/5 ({second_rating_name} деңгей)",
        )
    except TelegramNetworkError as e:
        await message.answer(
            "❌ Желі қатесіне байланысты нәтиже жіберу мүмкін болмады. Әрекетті кейінірек қайтала",
            reply_markup=test_start_kb()
        )
    except Exception as e:
        logging.error(f"Нәтиже жіберу кезіндегі ақау: {e} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await message.answer(
            "❌ Техникалық ақау туындады. Әрекетті кейінірек қайтала",
            reply_markup=test_start_kb()
        )

    if first_video:
        try:
            await message.answer(
                f"🎥 Бірінші таңдау пәнге арналған сабақ: {first_video.title}\nСілтеме: {first_video.url}"
            )
        except TelegramNetworkError as e:
            logging.error(f"Бірінші видео жіберу кезіндегі желілік ақау: {e} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await message.answer("❌ Бірінші видео жіберу мүмкін болмады. Кейінірек қайталаңыз")
        except Exception as e:
            logging.error(f"Бірінші видео жіберу кезіндегі ақау: {e} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await message.answer("❌ Бірінші видео жіберу кезінде техникалық ақау туындады")

    if second_video:
        try:
            await message.answer(
                f"🎥 Екінші таңдау пәнге арналған сабақ: {second_video.title}\nСілтеме: {second_video.url}"
            )
        except TelegramNetworkError as e:
            logging.error(f"Екінші видео жіберу кезіндегі желілік ақау: {e} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await message.answer("❌ Екінші видео жіберу мүмкін болмады. Кейінірек қайталаңыз")
        except Exception as e:
            logging.error(f"Екінші видео жіберу кезіндегі ақау: {e} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            await message.answer("❌ Екінші видео жіберу кезінде техникалық ақау туындады")

    try:
        photo = FSInputFile("media/hqdefault.jpg")  
        await message.answer_photo(photo, caption="📸 Арнайы курс туралы ақпарат!")
    except TelegramNetworkError as e:
        logging.error(f"Суретті жіберу ақауы: {e} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logging.error(f"Суретті жіберу ақауы: {e} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    discount_end_time = datetime.now() + timedelta(hours=1)
    discount_end_message = discount_end_time.strftime("%H:%M")
    course_text = f"📚 Деңгейіңді көтеру үшін арнайы курс бар! 1 сағат ішінде жазылып үлгеріңіз, жеңілдікпен! Жеңілдіктің аяқталу уақыты {discount_end_message}."

    try:
        await message.answer(course_text)
        await asyncio.sleep(0.5)
        await message.answer("Курсқа тіркелу 👇", reply_markup=course_button)
    except TelegramNetworkError as e:
        logging.error(f"Курс хабарламасын жіберу кезіндегі желілік ақау: {e} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await message.answer("❌ Желі қатесіне байланысты курс хабарламасын жіберу мүмкін болмады. Кейінірек қайталаңыз")
    except Exception as e:
        logging.error(f"Курс хабарламасын жіберу кезіндегі ақау: {e} в {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        await message.answer("❌ Техникалық ақау туындады. Кейінірек қайталаңыз")

    await schedule_discount_reminders(bot, message.chat.id)
    await state.clear()