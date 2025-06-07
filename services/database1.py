from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from config import Config

# Для SQLite используем упрощенные настройки
if "sqlite" in Config.DB_URL:
    engine = create_async_engine(
        Config.DB_URL,
        echo=True,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_async_engine(
        Config.DB_URL,
        echo=True,
        pool_size=20,
        max_overflow=10
    )

Base = declarative_base()

# Create session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db_session():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()