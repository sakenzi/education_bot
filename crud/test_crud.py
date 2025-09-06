from sqlalchemy import select
from db.database import async_session_factory
from db.models import Student, Direction, Test, TestAnswer, StudentResult


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
    

async def save_student_result(student_id: int, rating_id: int = None):
    async with async_session_factory() as session:
        result = StudentResult(student_id=student_id, rating_id=rating_id)
        session.add(result)
        await session.commit()