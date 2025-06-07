from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from database import get_tutor, get_all_students, delete_student, get_unanswered_questions, answer_question, get_user, get_homework, get_connection
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class AnswerQuestionStates(StatesGroup):
    answering = State()

async def assign_homework_callback(callback: types.CallbackQuery):
    tutor = get_tutor()
    if tutor and callback.from_user.id == tutor[0]:
        students = get_all_students()
        if students:
            keyboard = InlineKeyboardMarkup()
            for student in students:
                keyboard.add(InlineKeyboardButton(f"{student[1]} {student[2]}", callback_data=f'assign_to_{student[0]}'))
            await callback.message.answer("Выберите ученика для назначения ДЗ:", reply_markup=keyboard)
        else:
            await callback.message.answer("Нет зарегистрированных учеников.")
    else:
        await callback.message.answer("Только репетитор может назначать ДЗ.")
    await callback.answer()

async def select_student_for_assignment(callback: types.CallbackQuery, state: FSMContext):
    tutor = get_tutor()
    if tutor and callback.from_user.id == tutor[0]:
        try:
            student_id = int(callback.data.split('_')[2])
            await state.set_state("HomeworkStates:assigning_details")
            await state.update_data(student_id=student_id)
            await callback.message.answer("Введите детали задания (текст или прикрепите файл):")
        except ValueError:
            await callback.message.answer("Неверный ID ученика.")
    else:
        await callback.message.answer("Только репетитор может назначать ДЗ.")
    await callback.answer()

async def view_students_callback(callback: types.CallbackQuery):
    tutor = get_tutor()
    if tutor and callback.from_user.id == tutor[0]:
        students = get_all_students()
        if students:
            response = "Список учеников:\n"
            for student in students:
                response += f"ID: {student[0]}, Имя: {student[1]} {student[2]}, Класс: {student[3]}\n"
            await callback.message.answer(response)
        else:
            await callback.message.answer("Нет зарегистрированных учеников.")
    else:
        await callback.message.answer("Только репетитор может использовать эту команду.")
    await callback.answer()

async def view_questions_callback(callback: types.CallbackQuery):
    tutor = get_tutor()
    if tutor and callback.from_user.id == tutor[0]:
        questions = get_unanswered_questions()
        if questions:
            keyboard = InlineKeyboardMarkup()
            for idx, q in enumerate(questions, start=1):
                student = get_user(q[2])
                homework = get_homework(q[1])
                keyboard.add(InlineKeyboardButton(f"Вопрос №{idx} от {student[2]} {student[3]} по ДЗ №{homework[0]}", callback_data=f'answer_{q[0]}_{idx}'))
            await callback.message.answer("Выберите вопрос для ответа:", reply_markup=keyboard)
        else:
            await callback.message.answer("Нет непрочитанных вопросов.")
    else:
        await callback.message.answer("Только репетитор может использовать эту команду.")
    await callback.answer()

async def select_question_to_answer(callback: types.CallbackQuery, state: FSMContext):
    tutor = get_tutor()
    if tutor and callback.from_user.id == tutor[0]:
        try:
            parts = callback.data.split('_')
            question_id = int(parts[1])
            question_number = parts[2]
            await state.set_state("AnswerQuestionStates:answering")
            await state.update_data(question_id=question_id, question_number=question_number)
            await callback.message.answer("Введите ваш ответ на вопрос:")
        except (ValueError, IndexError):
            await callback.message.answer("Неверный ID вопроса.")
    else:
        await callback.message.answer("Только репетитор может отвечать на вопросы.")
    await callback.answer()

async def answer_question_details(message: types.Message, state: FSMContext):
    data = await state.get_data()
    question_id = data['question_id']
    question_number = data['question_number']
    answer_text = message.text
    answer_question(question_id, answer_text)
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT student_id FROM questions WHERE question_id=?", (question_id,))
    student_id = c.fetchone()[0]
    conn.close()
    student = get_user(student_id)
    await state.finish()
    await message.bot.send_message(student_id, f"Ответ на ваш вопрос №{question_number}: {answer_text}")
    await message.reply("Ответ отправлен.")

async def delete_student_callback(callback: types.CallbackQuery):
    tutor = get_tutor()
    if tutor and callback.from_user.id == tutor[0]:
        students = get_all_students()
        if students:
            keyboard = InlineKeyboardMarkup()
            for student in students:
                keyboard.add(InlineKeyboardButton(f"Удалить {student[1]} {student[2]}", callback_data=f'delete_student_{student[0]}'))
            await callback.message.answer("Выберите ученика для удаления:", reply_markup=keyboard)
        else:
            await callback.message.answer("Нет учеников для удаления.")
    else:
        await callback.message.answer("Только репетитор может удалять учеников.")
    await callback.answer()

async def select_student_to_delete(callback: types.CallbackQuery):
    tutor = get_tutor()
    if tutor and callback.from_user.id == tutor[0]:
        try:
            student_id = int(callback.data.split('_')[2])
            delete_student(student_id)
            await callback.message.answer(f"Ученик с ID {student_id} удален.")
        except ValueError:
            await callback.message.answer("Неверный ID ученика.")
    else:
        await callback.message.answer("Только репетитор может удалять учеников.")
    await callback.answer()