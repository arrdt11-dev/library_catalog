"""
Репозиторий для работы с книгами.
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.book import Book
from .base_repository import BaseRepository


class BookRepository(BaseRepository[Book]):
    """Репозиторий для работы с книгами."""

    def __init__(self, session: AsyncSession) -> None:
        """
        Инициализация репозитория книг.

        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        super().__init__(session, Book)

    async def find_by_filters(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        available: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[Book]:
        """
        Поиск книг с фильтрацией.

        Args:
            title: Фильтр по названию (частичное совпадение)
            author: Фильтр по автору (частичное совпадение)
            genre: Фильтр по жанру (точное совпадение)
            year: Фильтр по году
            available: Фильтр по доступности
            limit: Максимальное количество записей
            offset: Смещение

        Returns:
            Список книг
        """
        stmt = select(Book)

        # Применяем фильтры если они указаны
        if title:
            stmt = stmt.where(Book.title.ilike(f"%{title}%"))

        if author:
            stmt = stmt.where(Book.author.ilike(f"%{author}%"))

        if genre:
            stmt = stmt.where(Book.genre == genre)

        if year:
            stmt = stmt.where(Book.year == year)

        if available is not None:
            stmt = stmt.where(Book.available == available)

        # Применяем пагинацию и сортировку
        stmt = stmt.order_by(Book.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_isbn(self, isbn: str) -> Optional[Book]:
        """
        Найти книгу по ISBN.

        Args:
            isbn: ISBN книги

        Returns:
            Книга или None если не найдена
        """
        stmt = select(Book).where(Book.isbn == isbn)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_by_filters(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        available: Optional[bool] = None,
    ) -> int:
        """
        Подсчитать количество книг по фильтрам.

        Args:
            title: Фильтр по названию
            author: Фильтр по автору
            genre: Фильтр по жанру
            year: Фильтр по году
            available: Фильтр по доступности

        Returns:
            Количество книг
        """
        stmt = select(func.count()).select_from(Book)

        if title:
            stmt = stmt.where(Book.title.ilike(f"%{title}%"))

        if author:
            stmt = stmt.where(Book.author.ilike(f"%{author}%"))

        if genre:
            stmt = stmt.where(Book.genre == genre)

        if year:
            stmt = stmt.where(Book.year == year)

        if available is not None:
            stmt = stmt.where(Book.available == available)

        result = await self.session.execute(stmt)
        return result.scalar()

    async def find_by_title_or_author(
        self,
        search_query: str,
        limit: int = 20,
    ) -> list[Book]:
        """
        Поиск книг по названию или автору.

        Args:
            search_query: Строка для поиска
            limit: Максимальное количество записей

        Returns:
            Список книг
        """
        stmt = select(Book).where(
            or_(
                Book.title.ilike(f"%{search_query}%"),
                Book.author.ilike(f"%{search_query}%"),
            )
        )
        stmt = stmt.order_by(Book.created_at.desc()).limit(limit)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())
