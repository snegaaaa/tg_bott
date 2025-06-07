from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import get_tutor, get_submitted_homeworks, get_homework, update_homework_check, get_user
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class CheckHomeworkStates(StatesGroup):
    checking = State()

async def check_homework_callback(callback: types.CallbackQuery):
    tutor = get_tutor()
    if tutor and callback.from_user.id == tutor[0]:
        submissions = get_submitted_homeworks()
        if not submissions:
            await callback.message.answer("Нет отправленных ДЗ для проверки.")
            return
        keyboard = InlineKeyboardMarkup()
        for sub in submissions:
            keyboard.add(InlineKeyboardButton(f"Проверить ДЗ ID: {sub[0]}", callback_data=f'check_{sub[0]}'))
        await callback.message.answer("Выберите ДЗ для проверки:", reply_markup=keyboard)
    else:
        await callback.message.answer("Только репетитор может проверять ДЗ.")
    await callback.answer()

async def select_homework_to_check(callback: types.CallbackQuery, state: FSMContext):
    tutor = get_tutor()
    if tutor and callback.from_user.id == tutor[0]:
        try:
            homework_id = int(callback.data.split('_')[1])
            homework = get_homework(homework_id)
            if homework and homework[7] == 'submitted':
                await state.set_state("CheckHomeworkStates:checking")
                await state.update_data(homework_id=homework_id)
                await callback.message.answer("Введите результаты проверки:")
            else:
                await callback.message.answer("ДЗ не найдено или уже проверено.")
        except ValueError:
            await callback.message.answer("Неверный ID ДЗ.")
    else:
        await callback.message.answer("Только репетитор может проверять ДЗ.")
    await callback.answer()

async def check_homework_details(message: types.Message, state: FSMContext):
    data = await state.get_data()
    homework_id = data['homework_id']
    check_results = message.text
    update_homework_check(homework_id, check_results)
    homework = get_homework(homework_id)
    student_id = homework[1]
    student = get_user(student_id)
    await state.finish()
    await message.bot.send_message(student_id, f"ДЗ ID: {homework_id} проверено: {check_results}")
    await message.reply("Результаты отправлены ученику.")

async def view_submissions_callback(callback: types.CallbackQuery):
    tutor = get_tutor()
    if tutor and callback.from_user.id == tutor[0]:
        submissions = get_submitted_homeworks()
        if submissions:
            response = "Список отправленных заданий:\n"
            for submission in submissions:
                student = get_user(submission[1])
                response += f"ID задания: {submission[0]}, Ученик: {student[2]} {student[3]} (ID: {student[0]})\n"
            await callback.message.answer(response)
        else:
            await callback.message.answer("Нет отправленных заданий для проверки.")
    else:
        await callback.message.answer("Только репетитор может использовать эту команду.")
    await callback.answer()