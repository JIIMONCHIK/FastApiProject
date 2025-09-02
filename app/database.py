import os
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy import text

# URL подключения к PostgreSQL
DATABASE_URL = os.getenv(
    "POSTGRES_URL", 
    f"postgresql+asyncpg://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@postgres:5432/{os.getenv('POSTGRES_DB')}"
)

# Создаем асинхронный движок
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_size=20,
    max_overflow=10,
)

# Создаем фабрику сессий
AsyncSessionLocal = sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

# Базовый класс для моделей
Base = declarative_base()

# Функция для проверки подключения к БД
async def check_database_connection():
    max_retries = int(os.getenv("DATABASE_RETRY_ATTEMPTS", 10))
    retry_interval = int(os.getenv("DATABASE_RETRY_INTERVAL", 5))
    
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                await conn.execute(text("SELECT 1"))
            print("Database connection successful!")
            return True
        except OperationalError as e:
            print(f"Attempt {attempt + 1}/{max_retries}: Database not ready yet - {e}")
            if attempt == max_retries - 1:
                raise e
            await asyncio.sleep(retry_interval)
    
    return False

# Зависимость для получения сессии БД
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()