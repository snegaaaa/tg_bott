import logging
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from models.student import Student

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("register"))
async def register_student(
        message: types.Message,
        db_session: AsyncSession
):
    # Check if student already registered
    existing = await db_session.execute(
        select(Student).where(Student.telegram_id == str(message.from_user.id))
    if existing.scalar():
        await message.answer("Вы уже зарегистрированы!")
    return

    # Create new student
    new_student = Student(
        telegram_id=str(message.from_user.id),
        full_name=f"{message.from_user.first_name} {message.from_user.last_name or ''}"
    )

    db_session.add(new_student)
    await db_session.commit()

    await message.answer("✅ Регистрация успешно завершена!")