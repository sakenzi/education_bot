from aiogram import Router, types, F
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart
from states.register import RegisterForm
from keyboards.register import directions_kb, phone_kb
from crud.student_crud import create_student
from aiogram.fsm.context import FSMContext


router = Router()

@router.message(CommandStart())
async def start_handler(message: Message, state: FSMContext):
    await message.answer("Сәлем түлек, біздің ботқа қош келдің, сені көргенімізге қуаныштымыз!")
    welcome_video = FSInputFile("media/IMG_4331.MP4")
    await message.answer_video(
        video=welcome_video
    )
    await message.answer("Танысып алайық! Аты-жөніңді жаз 👇")
    await state.set_state(RegisterForm.name)


@router.message(RegisterForm.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(full_name=message.text)
    await message.answer("Телефон номеріңді жібер 👇:", reply_markup=phone_kb)
    await state.set_state(RegisterForm.phone)


@router.message(RegisterForm.phone, F.contact)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    kb = await directions_kb()
    await message.answer("Өз пәндік бағытыңды таңда 👇", reply_markup=kb)
    await state.set_state(RegisterForm.direction)


@router.message(RegisterForm.direction)
async def get_direction(message: types.Message, state: FSMContext):
    data = await state.get_data()
    student = await create_student(
        telegram_id=str(message.from_user.id),
        username=message.from_user.username,
        full_name=data["full_name"],
        phone=data["phone"],
        direction_name=message.text
    )

    if not student:
        await message.answer("Бұндай бағыт жоқ, берілгендерден таңда")
        return
    
    await message.answer(
        f"Жарайсың {data['full_name']}! 🎉 Сен {message.text} бағытына тіркелдің!",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.clear()