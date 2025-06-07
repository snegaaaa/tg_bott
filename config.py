import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env
load_dotenv()

# Токен бота
API_TOKEN = os.getenv("API_TOKEN")

# Путь к базе данных
DB_PATH = "math_tutor.db"

# Логин и пароль репетитора
TUTOR_LOGIN = "tutor"
TUTOR_PASSWORD = "math2023"