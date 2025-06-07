from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import TUTOR_LOGIN, TUTOR_PASSWORD
from database import get_user, set_user, is_tutor_set


class RegisterStudent(StatesGroup):
    waiting_for_first_name = State()
    waiting_for_last_name = State()
    waiting_for_grade = State()

class TutorAuth(StatesGroup):
    waiting_for_login = State()
    waiting_for_password = State()

async def start(message: types.Message):
    user = get_user(message.from_user.id)
    if user:
        if user[1] == 'tutor':
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Назначить ДЗ", callback_data='assign_homework'))
            keyboard.add(InlineKeyboardButton("Проверить ДЗ", callback_data='check_homework'))
            keyboard.add(InlineKeyboardButton("Просмотреть учеников", callback_data='view_students'))
            keyboard.add(InlineKeyboardButton("Просмотреть отправленные ДЗ", callback_data='view_submissions'))
            keyboard.add(InlineKeyboardButton("Просмотреть вопросы", callback_data='view_questions'))
            keyboard.add(InlineKeyboardButton("Удалить ученика", callback_data='delete_student'))
            await message.reply("Добро пожаловать, репетитор! Выберите действие:", reply_markup=keyboard)
        else:
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Мои ДЗ", callback_data='my_homework'))
            keyboard.add(InlineKeyboardButton("Отправить ДЗ", callback_data='submit_homework'))
            keyboard.add(InlineKeyboardButton("Просмотреть результаты", callback_data='view_results'))
            keyboard.add(InlineKeyboardButton("Ресурсы", callback_data='resources'))
            keyboard.add(InlineKeyboardButton("Задать вопрос", callback_data='ask_question'))
            await message.reply("Добро пожаловать, ученик! Выберите действие:", reply_markup=keyboard)
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Зарегистрироваться как ученик", callback_data='register_student'))
        keyboard.add(InlineKeyboardButton("Войти как репетитор", callback_data='login_tutor'))
        await message.reply("Выберите действие:", reply_markup=keyboard)

async def register_student_callback(callback: types.CallbackQuery):
    if get_user(callback.from_user.id):
        await callback.message.answer("Вы уже зарегистрированы.")
    else:
        await RegisterStudent.waiting_for_first_name.set()
        await callback.message.answer("Пожалуйста, введите ваше имя:")
    await callback.answer()

async def process_first_name(message: types.Message, state: FSMContext):
    first_name = message.text.strip()
    if not first_name:
        await message.reply("Имя не может быть пустым. Введите снова:")
        return
    await state.update_data(first_name=first_name)
    await RegisterStudent.waiting_for_last_name.set()
    await message.reply("Теперь введите вашу фамилию:")

async def process_last_name(message: types.Message, state: FSMContext):
    last_name = message.text.strip()
    if not last_name:
        await message.reply("Фамилия не может быть пустой. Введите снова:")
        return
    await state.update_data(last_name=last_name)
    await RegisterStudent.waiting_for_grade.set()
    await message.reply("Введите ваш класс (от 1 до 11):")

async def process_grade(message: types.Message, state: FSMContext):
    try:
        grade = int(message.text)
        if 1 <= grade <= 11:
            data = await state.get_data()
            first_name = data['first_name']
            last_name = data['last_name']
            user_id = message.from_user.id
            set_user(user_id, 'student', first_name, last_name, grade)
            await message.reply("Вы успешно зарегистрированы как ученик!")
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton("Мои ДЗ", callback_data='my_homework'))
            keyboard.add(InlineKeyboardButton("Отправить ДЗ", callback_data='submit_homework'))
            keyboard.add(InlineKeyboardButton("Просмотреть результаты", callback_data='view_results'))
            keyboard.add(InlineKeyboardButton("Ресурсы", callback_data='resources'))
            keyboard.add(InlineKeyboardButton("Задать вопрос", callback_data='ask_question'))
            await message.answer("Выберите действие:", reply_markup=keyboard)
            await state.finish()
        else:
            await message.reply("Класс должен быть от 1 до 11. Пожалуйста, введите снова:")
    except ValueError:
        await message.reply("Пожалуйста, введите число для класса.")

async def login_tutor_callback(callback: types.CallbackQuery):
    await TutorAuth.waiting_for_login.set()
    await callback.message.answer("Введите логин репетитора:")
    await callback.answer()

async def process_tutor_login(message: types.Message, state: FSMContext):
    login = message.text.strip()
    if login == TUTOR_LOGIN:
        await state.update_data(login=login)
        await TutorAuth.waiting_for_password.set()
        await message.reply("Введите пароль репетитора:")
    else:
        await message.reply("Неверный логин.")
        await state.finish()

async def process_tutor_password(message: types.Message, state: FSMContext):
    password = message.text.strip()
    if password == TUTOR_PASSWORD:
        user_id = message.from_user.id
        set_user(user_id, 'tutor', "Репетитор", "", None)
        await message.reply("Вы успешно вошли как репетитор!")
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("Назначить ДЗ", callback_data='assign_homework'))
        keyboard.add(InlineKeyboardButton("Проверить ДЗ", callback_data='check_homework'))
        keyboard.add(InlineKeyboardButton("Просмотреть учеников", callback_data='view_students'))
        keyboard.add(InlineKeyboardButton("Просмотреть отправленные ДЗ", callback_data='view_submissions'))
        keyboard.add(InlineKeyboardButton("Просмотреть вопросы", callback_data='view_questions'))
        keyboard.add(InlineKeyboardButton("Удалить ученика", callback_data='delete_student'))
        await message.answer("Выберите действие:", reply_markup=keyboard)
    else:
        await message.reply("Неверный пароль.")
    await state.finish()