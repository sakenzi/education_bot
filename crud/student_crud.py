from db.models import Student, Direction
from db.database import async_session_factory
from sqlalchemy import select


async def create_student(telegram_id: str, username: str, full_name: str, phone: str, direction_name: str):
    async with async_session_factory() as session:
        result = await session.execute(
            select(Direction).where(Direction.name == direction_name)
        )
        direction = result.scalars().first()

        if not direction:
            return None
        
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
