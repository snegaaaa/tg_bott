import asyncio
from services.database import engine, Base
from models.student import Student
from models.homework import Homework, HomeworkSubmission
from models.lesson import Lesson

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы успешно созданы!")

if __name__ == "__main__":
    asyncio.run(init_models())