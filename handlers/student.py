from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from database import get_user, get_homeworks_for_student, get_checked_homeworks_for_student, add_question, get_homework, get_tutor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

class AskQuestionStates(StatesGroup):
    entering_question = State()

async def my_homework_callback(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    if user and user[1] == 'student':
        homeworks = get_homeworks_for_student(user[0])
        if homeworks:
            response = ""
            for hw in homeworks:
                response += f"№ {hw[0]}\nСтатус: {hw[7]}\nЗадание: {hw[2]}\nСрок: {hw[3]}\n\n"
            await callback.message.answer(response.strip())
        else:
            await callback.message.answer("У вас нет ДЗ.")
    else:
        await callback.message.answer("Только ученики могут просматривать ДЗ.")
    await callback.answer()

async def submit_homework_callback(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    if user and user[1] == 'student':
        homeworks = get_homeworks_for_student(user[0])
        if not homeworks:
            await callback.message.answer("У вас нет невыполненных ДЗ.")
            return
        keyboard = InlineKeyboardMarkup()
        for hw in homeworks:
            if hw[7] == 'assigned':
                keyboard.add(InlineKeyboardButton(f"Отправить №{hw[0]}: {hw[2][:20]}...", callback_data=f'submit_{hw[0]}'))
        await callback.message.answer("Выберите ДЗ для отправки:", reply_markup=keyboard)
    else:
        await callback.message.answer("Только ученики могут отправлять ДЗ.")
    await callback.answer()

async def select_homework_for_submission(callback: types.CallbackQuery, state: FSMContext):
    user = get_user(callback.from_user.id)
    if user and user[1] == 'student':
        try:
            homework_id = int(callback.data.split('_')[1])
            homework = get_homework(homework_id)
            if homework and homework[1] == user[0] and homework[7] == 'assigned':
                await state.set_state("HomeworkStates:submitting")
                await state.update_data(homework_id=homework_id)
                await callback.message.answer("Отправьте ваше решение (текст или файл):")
            else:
                await callback.message.answer("Неверное ДЗ или оно не назначено вам.")
        except ValueError:
            await callback.message.answer("Неверный № ДЗ.")
    else:
        await callback.message.answer("Только ученики могут отправлять ДЗ.")
    await callback.answer()

async def view_results_callback(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    if user and user[1] == 'student':
        checked = get_checked_homeworks_for_student(user[0])
        if checked:
            response = "Результаты ваших проверенных заданий:\n"
            for hw in checked:
                response += f"№ задания: {hw[0]}, Результат: {hw[1]}\n"
            await callback.message.answer(response)
        else:
            await callback.message.answer("У вас нет проверенных заданий.")
    else:
        await callback.message.answer("Только ученики могут просматривать результаты.")
    await callback.answer()

async def resources_callback(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    if user and user[1] == 'student':
        resources = [
            "ФИПИ ([invalid url, do not cite])",
            "Решу ЕГЭ ([invalid url, do not cite])"
        ]
        response = "Полезные ресурсы для подготовки:\n"
        for res in resources:
            response += f"- {res}\n"
        await callback.message.answer(response)
    else:
        await callback.message.answer("Только ученики могут просматривать ресурсы.")
    await callback.answer()

async def ask_question_callback(callback: types.CallbackQuery):
    user = get_user(callback.from_user.id)
    if user and user[1] == 'student':
        homeworks = get_homeworks_for_student(user[0])
        if not homeworks:
            await callback.message.answer("У вас нет ДЗ для вопросов.")
            return
        keyboard = InlineKeyboardMarkup()
        for hw in homeworks:
            keyboard.add(InlineKeyboardButton(f"Задать вопрос по ДЗ №{hw[0]}", callback_data=f'ask_about_{hw[0]}'))
        await callback.message.answer("Выберите ДЗ, по которому хотите задать вопрос:", reply_markup=keyboard)
    else:
        await callback.message.answer("Только ученики могут задавать вопросы.")
    await callback.answer()

async def select_homework_for_question(callback: types.CallbackQuery, state: FSMContext):
    try:
        homework_id = int(callback.data.split('_')[2])
        await state.set_state("AskQuestionStates:entering_question")
        await state.update_data(homework_id=homework_id)
        await callback.message.answer("Введите ваш вопрос:")
    except ValueError:
        await callback.message.answer("Неверный № ДЗ.")
    await callback.answer()

async def enter_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    homework_id = data['homework_id']
    student_id = message.from_user.id
    question_text = message.text
    add_question(homework_id, student_id, question_text)
    await state.finish()
    await message.reply("Ваш вопрос отправлен репетитору.")
    tutor = get_tutor()
    if tutor:
        student = get_user(student_id)
        await message.bot.send_message(tutor[0], f"Новый вопрос от ученика {student[2]} {student[3]} по ДЗ №{homework_id}: {question_text}")