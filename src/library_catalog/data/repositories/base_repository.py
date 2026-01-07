"""
Базовый репозиторий для CRUD операций.
"""

from typing import Generic, TypeVar, Type, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T", bound="Base")


class BaseRepository(Generic[T]):
    """Generic репозиторий для работы с моделями."""

    def __init__(self, session: AsyncSession, model: Type[T]) -> None:
        """
        Инициализация репозитория.

        Args:
            session: Асинхронная сессия SQLAlchemy
            model: Класс модели
        """
        self.session = session
        self.model = model

    async def create(self, **kwargs) -> T:
        """
        Создать запись.

        Args:
            **kwargs: Атрибуты для создания

        Returns:
            Созданный объект
        """
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get_by_id(self, id: UUID) -> Optional[T]:
        """
        Получить запись по ID.

        Args:
            id: UUID записи

        Returns:
            Найденный объект или None
        """
        return await self.session.get(self.model, id)

    async def update(self, id: UUID, **kwargs) -> Optional[T]:
        """
        Обновить запись.

        Args:
            id: UUID записи
            **kwargs: Атрибуты для обновления

        Returns:
            Обновленный объект или None если не найден
        """
        instance = await self.get_by_id(id)
        if not instance:
            return None

        for key, value in kwargs.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: UUID) -> bool:
        """
        Удалить запись.

        Args:
            id: UUID записи

        Returns:
            True если удалено, False если не найдено
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False

        await self.session.delete(instance)
        await self.session.commit()
        return True

    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[T]:
        """
        Получить все записи с пагинацией.

        Args:
            limit: Максимальное количество записей
            offset: Смещение

        Returns:
            Список объектов
        """
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
