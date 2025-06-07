from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

def levels_keyboard():
    """Клавиатура для выбора уровня ученика"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(text="ОГЭ", callback_data="level_oge"),
        InlineKeyboardButton(text="ЕГЭ база", callback_data="level_ege_base"),
        InlineKeyboardButton(text="ЕГЭ профиль", callback_data="level_ege_profile")
    )
    builder.adjust(2)
    return builder.as_markup()