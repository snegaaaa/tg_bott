import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from models.homework import Homework
from keyboards import reply

router = Router()
logger = logging.getLogger(__name__)


@router.message(Command("assign_homework"))
async def assign_homework_start(
        message: types.Message,
        state: FSMContext
):
    await state.set_state("waiting_student_id")
    await message.answer(
        "👤 Введите ID ученика:",
        reply_markup=reply.cancel_keyboard()
    )


@router.message(F.text.regexp(r'^\d+$'), state="waiting_student_id")
async def get_student_id(
        message: types.Message,
        state: FSMContext
):
    student_id = int(message.text)
    await state.update_data(student_id=student_id)
    await state.set_state("waiting_homework_text")
    await message.answer("📝 Введите задание:")


@router.message(state="waiting_homework_text")
async def get_homework_text(
        message: types.Message,
        state: FSMContext,
        db_session: AsyncSession
):
    data = await state.get_data()
    student_id = data["student_id"]

    # Save homework to database
    new_homework = Homework(
        student_id=student_id,
        assignment=message.text
    )

    db_session.add(new_homework)
    await db_session.commit()

    await message.answer("✅ Домашнее задание успешно назначено!")
    await state.clear()