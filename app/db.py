"""Подключение к базе данных.

Шаг 5: асинхронный движок, фабрика сессий и зависимость get_session,
которая отдаёт сессию через yield.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

# Асинхронный движок. Драйвер asyncpg указан в самой строке подключения:
# postgresql+asyncpg://...
async_engine = create_async_engine(get_settings().DATABASE_URL)

# Фабрика асинхронных сессий, привязанная к движку.
session_factory = async_sessionmaker(bind=async_engine, class_=AsyncSession)


# Базовый класс для ORM-моделей. Его metadata использует Alembic (шаг 9).
class Base(DeclarativeBase):
    pass


# Зависимость FastAPI: на каждый запрос создаётся новая сессия,
# отдаётся обработчику через yield и закрывается после ответа в блоке finally.
async def get_session():
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()
