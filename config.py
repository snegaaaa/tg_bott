import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # Bot configuration
    BOT_TOKEN = os.getenv("BOT_TOKEN")

    # Database configuration
    DB_URL = os.getenv("DB_URL", "sqlite+aiosqlite:///math_tutor.db")

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Other settings
    ADMIN_IDS = [123456789]  # Ваш Telegram ID