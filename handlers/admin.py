import logging
from aiogram import Router, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command("admin"))
async def admin_panel(message: types.Message):
    await message.answer("Панель администратора")