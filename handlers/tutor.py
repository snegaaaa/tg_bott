import logging
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("schedule"))
async def show_schedule(
    message: types.Message,
    db_session: AsyncSession
):
    # Placeholder for schedule functionality
    await message.answer("Функционал расписания будет добавлен в ближайшее время")