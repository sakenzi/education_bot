from db.models import Student, Direction
from db.database import async_sessionmaker


async def create_student(telegram_id: str, username: str, name: str, phone: str, direction_name: int):
    async with async_sessionmaker() as session:
        direction = (await session.execute(
            Direction.__table__.select().where(Direction.name == direction_name)
        )).first
        if not direction:
            return None
        
        student = Student(
            telegram_id=telegram_id,
            username=username or "",
            full_name=name,
            phone_number=phone,
            direction_id=direction.id
        )
        session.add(student)
        await session.commit()
        await session.refresh(student)
        return student
