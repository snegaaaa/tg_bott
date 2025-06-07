import logging
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from models.homework import HomeworkSubmission

router = Router()
logger = logging.getLogger(__name__)


class SubmissionStates(StatesGroup):
    waiting_homework_id = State()
    waiting_solution = State()


@router.message(Command("submit_homework"))
async def submit_homework_start(
        message: types.Message,
        state: FSMContext
):
    await state.set_state(SubmissionStates.waiting_homework_id)
    await message.answer("Введите ID домашнего задания:")


@router.message(F.text.regexp(r'^\d+$'), SubmissionStates.waiting_homework_id)
async def get_homework_id(
        message: types.Message,
        state: FSMContext
):
    homework_id = int(message.text)
    await state.update_data(homework_id=homework_id)
    await state.set_state(SubmissionStates.waiting_solution)
    await message.answer("📝 Отправьте решение:")


@router.message(SubmissionStates.waiting_solution)
async def save_solution(
        message: types.Message,
        state: FSMContext,
        db_session: AsyncSession
):
    data = await state.get_data()
    homework_id = data["homework_id"]

    # Save submission
    submission = HomeworkSubmission(
        homework_id=homework_id,
        submission_text=message.text,
        submitted_by=message.from_user.id
    )

    db_session.add(submission)
    await db_session.commit()

    await message.answer("✅ Решение успешно отправлено!")
    await state.clear()