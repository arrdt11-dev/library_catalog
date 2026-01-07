"""
Настройка базы данных.
"""

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text

from .config import settings


class Base(DeclarativeBase):
    """Базовый класс для всех моделей SQLAlchemy."""

    pass


# Создать async engine
engine = create_async_engine(
    str(settings.database_url),
    echo=settings.debug,
    pool_size=settings.database_pool_size,
)

# Создать session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """Dependency для получения сессии БД."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Инициализировать базу данных."""
    # Создать все таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def check_db_connection() -> bool:
    """
    Проверить подключение к базе данных.

    Returns:
        bool: True если подключение работает
    """
    try:
        async with engine.begin() as conn:
            # Простой запрос для проверки подключения
            await conn.execute(text("SELECT 1"))
            return True
    except Exception:
        return False


async def dispose_engine() -> None:
    """Закрыть все соединения с БД."""
    await engine.dispose()
