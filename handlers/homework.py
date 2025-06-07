from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import create_homework, get_user

class HomeworkStates(StatesGroup):
    assigning_details = State()
    assigning_due_date = State()
    submitting = State()
    checking = State()

async def assign_homework_details(message: types.Message, state: FSMContext):
    details = message.text if message.text else ""
    files = []
    if message.photo:
        files.append(('photo', message.photo[-1].file_id))
    elif message.document:
        files.append(('document', message.document.file_id))
    await state.update_data(assignment_details=details, files=files)
    await HomeworkStates.assigning_due_date.set()
    await message.reply("Отправьте дату и время выполнения (в формате ГГГГ-ММ-ДД ЧЧ:ММ):")

async def assign_homework_due_date(message: types.Message, state: FSMContext):
    due_date = message.text
    data = await state.get_data()
    student_id = data['student_id']
    assignment_details = data['assignment_details']
    files = data.get('files', [])
    homework_id = create_homework(student_id, assignment_details, due_date)
    await state.finish()
    student = get_user(student_id)
    notification = f"Новое ДЗ №{homework_id}\nЗадание: {assignment_details}\nСрок сдачи: {due_date}"
    if files:
        for file_type, file_id in files:
            if file_type == 'photo':
                await message.bot.send_photo(student_id, file_id, caption=notification)
            elif file_type == 'document':
                await message.bot.send_document(student_id, file_id, caption=notification)
    else:
        await message.bot.send_message(student_id, notification)
    await message.reply(f"ДЗ назначено ученику {student[2]} {student[3]}, №{homework_id}")