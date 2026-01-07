"""
Обновленный BookService с интеграцией Open Library API.
"""

from typing import Optional
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from ...api.v1.schemas.book import BookCreate, BookUpdate, BookResponse, BookListResponse
from ...data.repositories.book_repository import BookRepository
from ...external.openlibrary.client import OpenLibraryClient
from ..exceptions import (
    BookNotFoundException,
    BookAlreadyExistsException,
    BookNotAvailableException,
    InvalidYearException,
    InvalidPagesException,
    ServiceException,
)
from ..mappers.book_mapper import BookMapper


class BookService:
    """Сервис для работы с книгами с обогащением данных."""
    
    def __init__(self, session: AsyncSession):
        """
        Инициализация сервиса.
        
        Args:
            session: Асинхронная сессия SQLAlchemy
        """
        self.session = session
        self.book_repository = BookRepository(session)
        self.openlibrary_client = OpenLibraryClient()
    
    async def create_book(self, book_create: BookCreate) -> BookResponse:
        """
        Создать новую книгу с обогащением из Open Library.
        
        Args:
            book_create: Данные для создания книги
        
        Returns:
            Созданная книга
        
        Raises:
            BookAlreadyExistsException: Если книга с таким названием, автором и годом уже существует
            InvalidYearException: Если год невалиден
            InvalidPagesException: Если количество страниц невалидно
            ServiceException: При других ошибках
        """
        try:
            # 1. Валидация бизнес-правил
            self._validate_book_data(book_create)
            
            # 2. Проверка уникальности
            await self._validate_book_creation(book_create)
            
            # 3. Обогащение данных из Open Library
            extra_data = await self._enrich_book_data(book_create)
            
            # 4. Создание модели с обогащенными данными
            book_model = BookMapper.create_to_model(book_create)
            if extra_data:
                book_model.extra = extra_data
            
            # 5. Сохраняем в БД
            created_book = await self.book_repository.create(
                title=book_model.title,
                author=book_model.author,
                year=book_model.year,
                genre=book_model.genre,
                pages=book_model.pages,
                isbn=book_model.isbn,
                description=book_model.description,
                available=book_model.available,
                extra=book_model.extra,
            )
            
            # 6. Преобразуем модель в ответ
            return BookMapper.model_to_response(created_book)
            
        except (BookAlreadyExistsException, InvalidYearException, InvalidPagesException):
            raise
        except Exception as e:
            raise ServiceException(
                f"Failed to create book: {str(e)}",
                details={"book_create": book_create.dict()}
            )
        finally:
            # Закрываем клиент Open Library
            await self.openlibrary_client.close()
    
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
                f"Failed to get book: {str(e)}",
                details={"book_id": str(book_id)}
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
            InvalidYearException: Если год невалиден
            InvalidPagesException: Если количество страниц невалидно
            ServiceException: При других ошибках
        """
        try:
            # 1. Находим книгу
            book = await self.book_repository.get_by_id(book_id)
            if not book:
                raise BookNotFoundException(book_id)
            
            # 2. Валидация обновляемых данных
            if book_update.year is not None:
                self._validate_year(book_update.year)
            if book_update.pages is not None:
                self._validate_pages(book_update.pages)
            
            # 3. Обновляем данные
            updated_book = await self.book_repository.update(
                book_id,
                **book_update.dict(exclude_unset=True)
            )
            
            if not updated_book:
                raise BookNotFoundException(book_id)
            
            # 4. Преобразуем в ответ
            return BookMapper.model_to_response(updated_book)
            
        except (BookNotFoundException, InvalidYearException, InvalidPagesException):
            raise
        except Exception as e:
            raise ServiceException(
                f"Failed to update book: {str(e)}",
                details={
                    "book_id": str(book_id),
                    "book_update": book_update.dict(exclude_unset=True)
                }
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
                f"Failed to delete book: {str(e)}",
                details={"book_id": str(book_id)}
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
                    "pagination": {"limit": limit, "offset": offset}
                }
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
            updated_book = await self.book_repository.update(
                book_id,
                available=False
            )
            
            return BookMapper.model_to_response(updated_book)
            
        except (BookNotFoundException, BookNotAvailableException):
            raise
        except Exception as e:
            raise ServiceException(
                f"Failed to mark book as unavailable: {str(e)}",
                details={"book_id": str(book_id)}
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
            updated_book = await self.book_repository.update(
                book_id,
                available=True
            )
            
            return BookMapper.model_to_response(updated_book)
            
        except BookNotFoundException:
            raise
        except Exception as e:
            raise ServiceException(
                f"Failed to mark book as available: {str(e)}",
                details={"book_id": str(book_id)}
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
    
    def _validate_book_data(self, book_data: BookCreate) -> None:
        """Валидация бизнес-правил для новой книги."""
        self._validate_year(book_data.year)
        self._validate_pages(book_data.pages)
    
    def _validate_year(self, year: int) -> None:
        """Проверить что год валиден."""
        current_year = datetime.now().year
        if year < 1000 or year > current_year:
            raise InvalidYearException(year)
    
    def _validate_pages(self, pages: int) -> None:
        """Проверить что количество страниц валидно."""
        if pages <= 0:
            raise InvalidPagesException(pages)
    
    async def _enrich_book_data(self, book_data: BookCreate) -> Optional[dict]:
        """
        Обогатить данные книги из Open Library.
        
        Args:
            book_data: Данные книги
        
        Returns:
            Обогащенные данные или None
        
        Note:
            Не выбрасывает исключение если API недоступен.
        """
        try:
            enriched_data = await self.openlibrary_client.enrich(
                title=book_data.title,
                author=book_data.author,
                isbn=book_data.isbn,
            )
            return enriched_data if enriched_data else None
        except Exception as e:
            # Логируем но не прерываем создание книги
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                "Failed to enrich book data from Open Library",
                extra={
                    "title": book_data.title,
                    "author": book_data.author,
                    "isbn": book_data.isbn,
                    "error": str(e)
                }
            )
            return None
