"""
Базовый репозиторий для работы с моделями БЕЗ commit.
"""

import logging
from typing import Generic, TypeVar, Type, Optional, List
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.book import Book  # Исправленный импорт

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Book)


class BaseRepository(Generic[T]):
    """Generic репозиторий для работы с моделями БЕЗ commit."""

    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        """Инициализация репозитория.

        Args:
            session: Асинхронная сессия SQLAlchemy
            model: Модель SQLAlchemy
        """
        self.session = session
        self.model = model

    async def create(self, **kwargs) -> T:
        """Создать запись БЕЗ commit.

        Returns:
            Созданная запись
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()  # Только flush, не commit!
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Получить запись по ID.

        Args:
            id: UUID записи

        Returns:
            Найденная запись или None
        """
        stmt = select(self.model).where(self.model.book_id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, id: UUID, **kwargs) -> Optional[T]:
        """Обновить запись БЕЗ commit.

        Args:
            id: UUID записи
            **kwargs: Поля для обновления

        Returns:
            Обновленная запись или None, если запись не найдена
        """
        instance = await self.get_by_id(id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.flush()  # Только flush, не commit!
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """Удалить запись БЕЗ commit.

        Args:
            id: UUID записи

        Returns:
            True если запись удалена, False если запись не найдена
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False

        await self.session.delete(instance)
        await self.session.flush()  # Только flush, не commit!
        return True

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """Получить все записи с пагинацией.

        Args:
            limit: Максимальное количество записей
            offset: Смещение

        Returns:
            Список записей
        """
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self) -> int:
        """Получить общее количество записей.

        Returns:
            Количество записей
        """
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar() or 0
