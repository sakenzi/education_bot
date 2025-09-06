from sqlalchemy import select
from db.database import async_session_factory
from db.models import Student, Test, TestAnswer, StudentResult, Video, Rating


async def get_student_by_telegram_id(telegram_id: str):
    async with async_session_factory() as session:
        return (await session.execute(
            select(Student).where(Student.telegram_id == telegram_id)
        )).scalars().first()
    

async def get_tests_by_direction(direction_id: int):
    async with async_session_factory() as session:
        return (await session.execute(
            select(Test).where(Test.direction_id == direction_id)
        )).scalars().all()
    

async def get_test_by_id(test_id: int):
    async with async_session_factory() as session:
        return (await session.execute(
            select(Test).where(Test.id == test_id)
        )).scalars().first()
    

async def get_answers_by_test(test_id: int):
    async with async_session_factory() as session:
        return (await session.execute(
            select(TestAnswer).where(TestAnswer.test_id == test_id)
        )).scalars().all()
    

async def save_student_result(student_id: int, rating_id: int):
    async with async_session_factory() as session:
        result = StudentResult(student_id=student_id, rating_id=rating_id)
        session.add(result)
        await session.commit()


async def get_video_by_rating_and_direction(rating_id: int, direction_id: int):
    async with async_session_factory() as session:
        return (await session.execute(
            select(Video)
            .where(Video.rating_id == rating_id, Video.direction_id == direction_id)
            .limit(1)  
        )).scalars().first()
    

async def get_rating(rating_name: str):
    async with async_session_factory() as session:
        return (await session.execute(
            select(Rating).where(Rating.rating == rating_name)
        )).scalars().first()