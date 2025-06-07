from aiogram import types
from aiogram.dispatcher import FSMContext
from database import get_user, get_homework, update_homework_submission, get_tutor

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def submit_homework_details(message: types.Message, state: FSMContext):
    data = await state.get_data()
    homework_id = data['homework_id']
    submission_details = message.text if message.text else ""
    submission_type = 'text'
    if message.photo:
        file_id = message.photo[-1].file_id
        submission_details = file_id
        submission_type = 'photo'
    elif message.document:
        file_id = message.document.file_id
        submission_details = file_id
        submission_type = 'document'
    update_homework_submission(homework_id, submission_details, submission_type)
    await state.finish()
    tutor = get_tutor()
    student = get_user(message.from_user.id)
    notification = f"Ученик {student[2]} {student[3]} отправил ДЗ №{homework_id}"
    if submission_type == 'photo':
        await message.bot.send_photo(tutor[0], submission_details, caption=notification)
    elif submission_type == 'document':
        await message.bot.send_document(tutor[0], submission_details, caption=notification)
    else:
        await message.bot.send_message(tutor[0], f"{notification}\nРешение: {submission_details}")
    await message.reply("Решение отправлено.")