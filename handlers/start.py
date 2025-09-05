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
    welcome_video = FSInputFile("/Users/cenrsip/Desktop/edu_bot/education_bot/media/IMG_4331.MP4")
    await message.answer_video(
        video=welcome_video
    )
    await message.answer("Танысып алайық! Аты-жөніңді жаз 👇")
    await state.set_state(RegisterForm.name)


@router.message(RegisterForm.name)
async def get_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Телефон номеріңді жібер 👇:", reply_markup=phone_kb)
    await state.set_state(RegisterForm.phone)


@router.message(RegisterForm.phone, F.contact)
async def get_phone(message: types.Message, state: FSMContext):
    await state.update_data(phone=message.contact.phone_number)
    kb = await directions_kb()
    await message.answer("Өз пәндік бағытыңды таңда 👇", reply_markup=kb)
    await state.set_data(RegisterForm.direction)