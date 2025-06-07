import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import Config
from handlers import (
    admin,
    homework,
    registration,
    students,
    submission,
    tutor
)

# Configure logging
logging.basicConfig(
    level=Config.LOG_LEVEL,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    filename="bot.log"
)
logger = logging.getLogger(__name__)


async def main():
    # Initialize bot and dispatcher
    bot = Bot(token=Config.BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Include routers
    dp.include_router(registration.router)
    dp.include_router(students.router)
    dp.include_router(homework.router)
    dp.include_router(submission.router)
    dp.include_router(tutor.router)
    dp.include_router(admin.router)

    # Start polling
    try:
        logger.info("Starting bot...")
        await dp.start_polling(bot)
    except Exception as e:
        logger.exception(f"Bot stopped with error: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())