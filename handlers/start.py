from aiogram import Router
from aiogram.types import Message, FSInputFile
from aiogram.filters import CommandStart


router = Router()

@router.message(CommandStart())
async def start_handler(message: Message):
    await message.answer("Сәлем түлек, біздің ботқа қош келдің, сені көргенімізге қуаныштымыз!")
    welcome_video = FSInputFile("/Users/cenrsip/Desktop/edu_bot/education_bot/media/IMG_4331.MP4")
    await message.answer_video(
        video=welcome_video
    )