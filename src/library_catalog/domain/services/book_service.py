"""
Сервис для работы с книгами.
Содержит всю бизнес-логику приложения.
"""

from uuid import UUID
from typing import Optional, List, Tuple

from ...data.repositories.book_repository import BookRepository
from ...external.openlibrary.client import OpenLibraryClient
from ..exceptions import (
    BookNotFoundException,
    BookAlreadyExistsException,
    InvalidYearException,
    InvalidPagesException,
    OpenLibraryException,
    OpenLibraryTimeoutException,
)
from ..schemas.book import BookCreate, BookUpdate, BookResponse
from ..mappers.book_mapper import BookMapper


class BookService:
    """
    Сервис для работы с книгами.

    Содержит всю бизнес-логику приложения.
    """

    def __init__(
        self,
        book_repository: BookRepository,
        openlibrary_client: OpenLibraryClient,
    ):
        self.book_repo = book_repository
        self.ol_client = openlibrary_client

    async def create_book(self, book_data: BookCreate) -> BookResponse:
        """
        Создать новую книгу с обогащением из Open Library.

        Бизнес-правила:
        - Год не в будущем
        - Страницы > 0
        - ISBN уникален (если указан)

        Args:
            book_data: Данные для создания

        Returns:
            BookResponse: Созданная книга

        Raises:
            InvalidYearException: Если год невалиден
            InvalidPagesException: Если страницы <= 0
            BookAlreadyExistsException: Если ISBN уже существует
        """
        # 1. Валидация бизнес-правил
        self._validate_book_data(book_data)

        # 2. Проверка уникальности ISBN
        if book_data.isbn:
            existing = await self.book_repo.find_by_isbn(book_data.isbn)
            if existing:
                raise BookAlreadyExistsException(book_data.isbn)

        # 3. Обогащение данных из Open Library
        extra = await self._enrich_book_data(book_data)

        # 4. Создание в БД
        book = await self.book_repo.create(
            title=book_data.title,
            author=book_data.author,
            year=book_data.year,
            genre=book_data.genre,
            pages=book_data.pages,
            isbn=book_data.isbn,
            description=book_data.description,
            extra=extra,
        )

        # 5. Делаем commit (теперь сервис управляет транзакциями)
        await self.book_repo.session.commit()

        # 6. Маппинг в DTO
        return BookMapper.to_response(book)

    async def get_book_by_id(self, book_id: UUID) -> BookResponse:
        """
        Получить книгу по ID.

        Raises:
            BookNotFoundException: Если книга не найдена
        """
        book = await self.book_repo.get_by_id(book_id)
        if book is None:
            raise BookNotFoundException(book_id)

        return BookMapper.to_response(book)

    async def update_book(
        self,
        book_id: UUID,
        book_data: BookUpdate,
    ) -> BookResponse:
        """
        Обновить книгу.

        Обновляются только переданные поля.
        """
        # Проверить существование
        existing = await self.book_repo.get_by_id(book_id)
        if existing is None:
            raise BookNotFoundException(book_id)

        # Валидация если обновляется год
        if book_data.year is not None:
            self._validate_year(book_data.year)

        # Обновить
        updated = await self.book_repo.update(
            book_id, **book_data.dict(exclude_unset=True)
        )

        if updated:
            # Делаем commit (теперь сервис управляет транзакциями)
            await self.book_repo.session.commit()

        return BookMapper.to_response(updated)

    async def delete_book(self, book_id: UUID) -> bool:
        """
        Удалить книгу.

        Returns:
            bool: True если книга удалена

        Raises:
            BookNotFoundException: Если книга не найдена
        """
        deleted = await self.book_repo.delete(book_id)
        if not deleted:
            raise BookNotFoundException(book_id)
        
        # Делаем commit (теперь сервис управляет транзакциями)
        await self.book_repo.session.commit()
        
        return True

    async def get_books(
        self,
        skip: int = 0,
        limit: int = 100,
    ) -> List[BookResponse]:
        """
        Получить список книг с пагинацией.
        """
        books = await self.book_repo.get_all(skip=skip, limit=limit)
        return BookMapper.to_responses(books)

    async def search_books(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Tuple[List[BookResponse], int]:
        """
        Поиск книг с фильтрами и пагинацией.

        Returns:
            tuple: (список книг, общее количество)
        """
        books = await self.book_repo.find_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
            limit=limit,
            offset=offset,
        )

        total = await self.book_repo.count_by_filters(
            title=title,
            author=author,
            genre=genre,
            year=year,
        )

        return BookMapper.to_responses(books), total

    # ========== ПРИВАТНЫЕ МЕТОДЫ ==========

    def _validate_book_data(self, data: BookCreate) -> None:
        """Валидация бизнес-правил для новой книги."""
        self._validate_year(data.year)

    def _validate_year(self, year: int) -> None:
        """Проверить что год валиден."""
        from datetime import datetime

        current_year = datetime.now().year
        if year < 1000 or year > current_year:
            raise InvalidYearException(year)

    async def _enrich_book_data(self, book_data: BookCreate) -> Optional[dict]:
        """
        Обогатить данные книги из Open Library.

        Не выбрасывает исключение если API недоступен.
        """
        try:
            extra = await self.ol_client.enrich(
                title=book_data.title,
                author=book_data.author,
                isbn=book_data.isbn,
            )
            return extra if extra else None
        except (OpenLibraryException, OpenLibraryTimeoutException) as e:
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                "Не удалось обогатить данные книги из Open Library",
                extra={
                    "title": book_data.title,
                    "author": book_data.author,
                    "error": str(e),
                },
            )
            return None
