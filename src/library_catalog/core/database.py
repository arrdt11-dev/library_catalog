"""
Настройка базы данных.
"""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from .config import settings


class Base(DeclarativeBase):
    """Базовый класс для всех моделей."""
    pass


# Создаем асинхронный engine
engine = create_async_engine(
    str(settings.database_url),  # Преобразуем PostgresDsn в строку
    pool_size=settings.database_pool_size,
    echo=settings.debug,
    future=True,
)

# Создаем фабрику сессий
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency для получения сессии БД.
    
    Использование в FastAPI:
    @router.get("/")
    async def get_items(db: AsyncSession = Depends(get_db)):
        ...
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """
    Инициализация базы данных (создание таблиц).
    Вызывается при старте приложения.
    """
    async with engine.begin() as conn:
        # Создаем все таблицы, если их нет
        await conn.run_sync(Base.metadata.create_all)


async def check_db_connection() -> bool:
    """
    Проверка подключения к базе данных.
    Возвращает True если подключение успешно.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
        return True
    except Exception:
        return False


async def dispose_engine() -> None:
    """
    Корректное закрытие соединений с БД.
    Вызывается при остановке приложения.
    """
    await engine.dispose()
