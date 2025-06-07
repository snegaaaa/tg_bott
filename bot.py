import os
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from handlers import registration, homework, submission, check, tutor, student
from config import API_TOKEN
from database import init_db

# Инициализация базы данных
init_db()

# Инициализация бота
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Регистрация обработчиков сообщений
dp.register_message_handler(registration.start, commands=['start'])
dp.register_message_handler(registration.process_first_name, state=registration.RegisterStudent.waiting_for_first_name)
dp.register_message_handler(registration.process_last_name, state=registration.RegisterStudent.waiting_for_last_name)
dp.register_message_handler(registration.process_grade, state=registration.RegisterStudent.waiting_for_grade)
dp.register_message_handler(registration.process_tutor_login, state=registration.TutorAuth.waiting_for_login)
dp.register_message_handler(registration.process_tutor_password, state=registration.TutorAuth.waiting_for_password)
dp.register_message_handler(homework.assign_homework_details, state=homework.HomeworkStates.assigning_details)
dp.register_message_handler(homework.assign_homework_due_date, state=homework.HomeworkStates.assigning_due_date)
dp.register_message_handler(submission.submit_homework_details, state=homework.HomeworkStates.submitting, content_types=['text', 'document', 'photo'])
dp.register_message_handler(check.check_homework_details, state=check.CheckHomeworkStates.checking)
dp.register_message_handler(tutor.answer_question_details, state=tutor.AnswerQuestionStates.answering)
dp.register_message_handler(student.enter_question, state=student.AskQuestionStates.entering_question)

# Регистрация обработчиков callback-запросов
dp.register_callback_query_handler(registration.register_student_callback, lambda c: c.data == 'register_student')
dp.register_callback_query_handler(registration.login_tutor_callback, lambda c: c.data == 'login_tutor')
dp.register_callback_query_handler(tutor.view_students_callback, lambda c: c.data == 'view_students')
dp.register_callback_query_handler(tutor.assign_homework_callback, lambda c: c.data == 'assign_homework')
dp.register_callback_query_handler(tutor.select_student_for_assignment, lambda c: c.data.startswith('assign_to_'))
dp.register_callback_query_handler(check.check_homework_callback, lambda c: c.data == 'check_homework')
dp.register_callback_query_handler(check.select_homework_to_check, lambda c: c.data.startswith('check_'))
dp.register_callback_query_handler(check.view_submissions_callback, lambda c: c.data == 'view_submissions')
dp.register_callback_query_handler(tutor.view_questions_callback, lambda c: c.data == 'view_questions')
dp.register_callback_query_handler(tutor.select_question_to_answer, lambda c: c.data.startswith('answer_'))
dp.register_callback_query_handler(tutor.delete_student_callback, lambda c: c.data == 'delete_student')
dp.register_callback_query_handler(tutor.select_student_to_delete, lambda c: c.data.startswith('delete_student_'))
dp.register_callback_query_handler(student.my_homework_callback, lambda c: c.data == 'my_homework')
dp.register_callback_query_handler(student.submit_homework_callback, lambda c: c.data == 'submit_homework')
dp.register_callback_query_handler(student.select_homework_for_submission, lambda c: c.data.startswith('submit_'))
dp.register_callback_query_handler(student.view_results_callback, lambda c: c.data == 'view_results')
dp.register_callback_query_handler(student.resources_callback, lambda c: c.data == 'resources')
dp.register_callback_query_handler(student.ask_question_callback, lambda c: c.data == 'ask_question')
dp.register_callback_query_handler(student.select_homework_for_question, lambda c: c.data.startswith('ask_about_'))

# Запуск бота
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)