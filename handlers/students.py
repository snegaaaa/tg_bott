import logging
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.student import Student
from keyboards import reply, inline

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("students"))
async def list_students(
        message: types.Message,
        db_session: AsyncSession
):
    try:
        # Get list of students
        result = await db_session.execute(select(Student))
        students = result.scalars().all()

        if not students:
            await message.answer("🔄 Список учеников пуст")
            return

        # Format response
        response = "📚 Список ваших учеников:\n\n"
        for student in students:
            response += f"• {student.full_name}\n"
            response += f"  👤 ID: {student.id}\n"
            if student.contact_info:
                response += f"  📞 Контакт: {student.contact_info}\n"
            response += "\n"

        await message.answer(response)

    except Exception as e:
        logger.error(f"Ошибка при получении списка учеников: {e}")
        await message.answer("⚠️ Произошла ошибка. Попробуйте позже")


@router.message(Command("add_student"))
async def add_student_start(
        message: types.Message,
        state: FSMContext
):
    await state.set_state("waiting_student_name")
    await message.answer(
        "👤 Введите полное имя ученика:",
        reply_markup=reply.cancel_keyboard()
    )


@router.message(F.text, state="waiting_student_name")
async def add_student_name(
        message: types.Message,
        state: FSMContext
):
    await state.update_data(full_name=message.text)
    await state.set_state("waiting_student_level")
    await message.answer(
        "📊 Выберите уровень ученика:",
        reply_markup=inline.levels_keyboard()
    )