from db.models import Student, Direction
from db.database import async_session_factory
from sqlalchemy import select


async def create_student(telegram_id: str, username: str, full_name: str, phone: str, direction_name: str):
    async with async_session_factory() as session:
        direction = (await session.execute(
            select(Direction).where(Direction.name == direction_name)
        )).scalar_one_or_none()

        if not direction:
            return None

        existing_student = (await session.execute(
            select(Student).where(Student.telegram_id == telegram_id)
        )).scalar_one_or_none()

        if existing_student:
            existing_student.username = username or existing_student.username
            existing_student.full_name = full_name or existing_student.full_name
            existing_student.phone_number = phone or existing_student.phone_number
            existing_student.direction_id = direction.id

            await session.commit()
            await session.refresh(existing_student)
            return existing_student

        student = Student(
            telegram_id=telegram_id,
            username=username or "",
            full_name=full_name,
            phone_number=phone,
            direction_id=direction.id
        )
        session.add(student)
        await session.commit()
        await session.refresh(student)
        return student
