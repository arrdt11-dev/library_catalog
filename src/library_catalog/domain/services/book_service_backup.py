"""
Сервисный слой для работы с книгами (бизнес-логика).
"""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from ...api.v1.schemas.book import (
    BookCreate,
    BookUpdate,
    BookResponse,
    BookListResponse,
)
from ...data.repositories.book_repository import BookRepository
from ..exceptions import (
    BookNotFoundException,
    BookAlreadyExistsException,
    BookNotAvailableException,
    ServiceException,
)
from ..mappers.book_mapper import BookMapper


class BookService:
    """Сервис для работы с книгами."""

    def __init__(self, session: AsyncSession):
        """
        Инициализация сервиса.

        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        self.session = session
        self.book_repository = BookRepository(session)

    async def create_book(self, book_create: BookCreate) -> BookResponse:
        """
        Создать новую книгу.

        Args:
            book_create: Данные для создания книги

        Returns:
            Созданная книга

        Raises:
            BookAlreadyExistsException: Если книга с таким названием, автором и годом уже существует
            ServiceException: При других ошибках
        """
        try:
            # 1. Проверяем бизнес-правила
            await self._validate_book_creation(book_create)

            # 2. Преобразуем DTO в модель
            book_model = BookMapper.create_to_model(book_create)

            # 3. Сохраняем в БД
            created_book = await self.book_repository.create(
                title=book_model.title,
                author=book_model.author,
                year=book_model.year,
                genre=book_model.genre,
                pages=book_model.pages,
                isbn=book_model.isbn,
                description=book_model.description,
                available=book_model.available,
            )

            # 4. Преобразуем модель в ответ
            return BookMapper.model_to_response(created_book)

        except BookAlreadyExistsException:
            raise  # Пробрасываем дальше
        except Exception as e:
            raise ServiceException(
                f"Failed to create book: {str(e)}",
                details={"book_create": book_create.dict()},
            )

    async def get_book(self, book_id: UUID) -> BookResponse:
        """
        Получить книгу по ID.

        Args:
            book_id: UUID книги

        Returns:
            Книга

        Raises:
            BookNotFoundException: Если книга не найдена
            ServiceException: При других ошибках
        """
        try:
            book = await self.book_repository.get_by_id(book_id)

            if not book:
                raise BookNotFoundException(book_id)

            return BookMapper.model_to_response(book)

        except BookNotFoundException:
            raise
        except Exception as e:
            raise ServiceException(
                f"Failed to get book: {str(e)}", details={"book_id": str(book_id)}
            )

    async def update_book(
        self,
        book_id: UUID,
        book_update: BookUpdate,
    ) -> BookResponse:
        """
        Обновить книгу.

        Args:
            book_id: UUID книги
            book_update: Данные для обновления

        Returns:
            Обновленная книга

        Raises:
            BookNotFoundException: Если книга не найдена
            ServiceException: При других ошибках
        """
        try:
            # 1. Находим книгу
            book = await self.book_repository.get_by_id(book_id)
            if not book:
                raise BookNotFoundException(book_id)

            # 2. Проверяем бизнес-правила для обновления
            await self._validate_book_update(book_update, book)

            # 3. Обновляем данные
            updated_book = await self.book_repository.update(
                book_id, **book_update.dict(exclude_unset=True)
            )

            if not updated_book:
                raise BookNotFoundException(book_id)

            # 4. Преобразуем в ответ
            return BookMapper.model_to_response(updated_book)

        except (BookNotFoundException, InvalidBookDataException):
            raise
        except Exception as e:
            raise ServiceException(
                f"Failed to update book: {str(e)}",
                details={
                    "book_id": str(book_id),
                    "book_update": book_update.dict(exclude_unset=True),
                },
            )

    async def delete_book(self, book_id: UUID) -> bool:
        """
        Удалить книгу.

        Args:
            book_id: UUID книги

        Returns:
            True если удалено

        Raises:
            BookNotFoundException: Если книга не найдена
            ServiceException: При других ошибках
        """
        try:
            # Проверяем что книга существует
            book = await self.book_repository.get_by_id(book_id)
            if not book:
                raise BookNotFoundException(book_id)

            # Удаляем книгу
            deleted = await self.book_repository.delete(book_id)

            if not deleted:
                raise BookNotFoundException(book_id)

            return True

        except BookNotFoundException:
            raise
        except Exception as e:
            raise ServiceException(
                f"Failed to delete book: {str(e)}", details={"book_id": str(book_id)}
            )

    async def get_books(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        genre: Optional[str] = None,
        year: Optional[int] = None,
        available: Optional[bool] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> BookListResponse:
        """
        Получить список книг с фильтрацией.

        Args:
            title: Фильтр по названию
            author: Фильтр по автору
            genre: Фильтр по жанру
            year: Фильтр по году
            available: Фильтр по доступности
            limit: Максимальное количество
            offset: Смещение

        Returns:
            Список книг с пагинацией
        """
        try:
            # Получаем книги с фильтрами
            books = await self.book_repository.find_by_filters(
                title=title,
                author=author,
                genre=genre,
                year=year,
                available=available,
                limit=limit,
                offset=offset,
            )

            # Получаем общее количество для пагинации
            total = await self.book_repository.count_by_filters(
                title=title,
                author=author,
                genre=genre,
                year=year,
                available=available,
            )

            # Преобразуем модели в ответы
            book_responses = BookMapper.models_to_responses(books)

            return BookListResponse(
                items=book_responses,
                total=total,
                limit=limit,
                offset=offset,
            )

        except Exception as e:
            raise ServiceException(
                f"Failed to get books: {str(e)}",
                details={
                    "filters": {
                        "title": title,
                        "author": author,
                        "genre": genre,
                        "year": year,
                        "available": available,
                    },
                    "pagination": {"limit": limit, "offset": offset},
                },
            )

    async def mark_book_as_unavailable(self, book_id: UUID) -> BookResponse:
        """
        Пометить книгу как недоступную (выдана).

        Args:
            book_id: UUID книги

        Returns:
            Обновленная книга

        Raises:
            BookNotFoundException: Если книга не найдена
            BookNotAvailableException: Если книга уже недоступна
            ServiceException: При других ошибках
        """
        try:
            # Находим книгу
            book = await self.book_repository.get_by_id(book_id)
            if not book:
                raise BookNotFoundException(book_id)

            # Проверяем что книга доступна
            if not book.available:
                raise BookNotAvailableException(book_id)

            # Обновляем статус
            updated_book = await self.book_repository.update(book_id, available=False)

            return BookMapper.model_to_response(updated_book)

        except (BookNotFoundException, BookNotAvailableException):
            raise
        except Exception as e:
            raise ServiceException(
                f"Failed to mark book as unavailable: {str(e)}",
                details={"book_id": str(book_id)},
            )

    async def mark_book_as_available(self, book_id: UUID) -> BookResponse:
        """
        Пометить книгу как доступную (возвращена).

        Args:
            book_id: UUID книги

        Returns:
            Обновленная книга

        Raises:
            BookNotFoundException: Если книга не найдена
            ServiceException: При других ошибках
        """
        try:
            # Находим книгу
            book = await self.book_repository.get_by_id(book_id)
            if not book:
                raise BookNotFoundException(book_id)

            # Обновляем статус
            updated_book = await self.book_repository.update(book_id, available=True)

            return BookMapper.model_to_response(updated_book)

        except BookNotFoundException:
            raise
        except Exception as e:
            raise ServiceException(
                f"Failed to mark book as available: {str(e)}",
                details={"book_id": str(book_id)},
            )

    # ========== ПРИВАТНЫЕ МЕТОДЫ ДЛЯ ВАЛИДАЦИИ ==========

    async def _validate_book_creation(self, book_create: BookCreate) -> None:
        """
        Проверить бизнес-правила при создании книги.

        Args:
            book_create: Данные для создания

        Raises:
            BookAlreadyExistsException: Если книга уже существует
        """
        # Проверяем нет ли уже книги с таким названием, автором и годом
        existing_books = await self.book_repository.find_by_filters(
            title=book_create.title,
            author=book_create.author,
            year=book_create.year,
            limit=1,
        )

        if existing_books:
            raise BookAlreadyExistsException(
                title=book_create.title,
                author=book_create.author,
                year=book_create.year,
            )

    async def _validate_book_update(
        self,
        book_update: BookUpdate,
        existing_book,
    ) -> None:
        """
        Проверить бизнес-правила при обновлении книги.

        Args:
            book_update: Данные для обновления
            existing_book: Существующая книга

        Raises:
            InvalidBookDataException: Если данные невалидны
        """
        # Если меняется ISBN, проверяем что он уникальный
        if book_update.isbn is not None and book_update.isbn != existing_book.isbn:
            book_with_isbn = await self.book_repository.find_by_isbn(book_update.isbn)
            if book_with_isbn and book_with_isbn.book_id != existing_book.book_id:
                from ..exceptions import InvalidBookDataException

                raise InvalidBookDataException(
                    field="isbn", value=book_update.isbn, reason="ISBN must be unique"
                )

        # Если меняется год, проверяем валидность
        if book_update.year is not None:
            BookMapper.validate_book_year(book_update.year)
