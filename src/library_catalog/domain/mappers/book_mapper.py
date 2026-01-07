"""
Маппер для преобразования между сущностями книги.
"""

from typing import Optional
from uuid import UUID

from ...api.v1.schemas.book import BookCreate, BookUpdate, BookResponse
from ...data.models.book import Book
from ..exceptions import InvalidBookDataException


class BookMapper:
    """Маппер для книг."""
    
    @staticmethod
    def create_to_model(book_create: BookCreate, book_id: Optional[UUID] = None) -> Book:
        """
        Преобразовать BookCreate в модель Book.
        
        Args:
            book_create: Данные для создания книги
            book_id: Опциональный UUID (если не указан, сгенерируется автоматически)
        
        Returns:
            Модель Book
        """
        try:
            return Book(
                book_id=book_id,
                title=book_create.title,
                author=book_create.author,
                year=book_create.year,
                genre=book_create.genre,
                pages=book_create.pages,
                isbn=book_create.isbn,
                description=book_create.description,
                available=book_create.available,
                # created_at и updated_at установятся автоматически
            )
        except Exception as e:
            raise InvalidBookDataException(
                field="general",
                value=str(book_create.dict()),
                reason=str(e),
                details={"book_create": book_create.dict()}
            )
    
    @staticmethod
    def update_to_model(book_update: BookUpdate, book_model: Book) -> Book:
        """
        Обновить модель Book данными из BookUpdate.
        
        Args:
            book_update: Данные для обновления
            book_model: Существующая модель книги
        
        Returns:
            Обновленная модель Book
        """
        try:
            update_data = book_update.dict(exclude_unset=True)
            
            for field, value in update_data.items():
                if value is not None and hasattr(book_model, field):
                    setattr(book_model, field, value)
            
            return book_model
        except Exception as e:
            raise InvalidBookDataException(
                field="general",
                value=str(book_update.dict(exclude_unset=True)),
                reason=str(e),
                details={
                    "book_update": book_update.dict(exclude_unset=True),
                    "book_model_id": str(book_model.book_id)
                }
            )
    
    @staticmethod
    def model_to_response(book_model: Book) -> BookResponse:
        """
        Преобразовать модель Book в BookResponse.
        
        Args:
            book_model: Модель книги из БД
        
        Returns:
            BookResponse для API
        """
        try:
            return BookResponse(
                book_id=book_model.book_id,
                title=book_model.title,
                author=book_model.author,
                year=book_model.year,
                genre=book_model.genre,
                pages=book_model.pages,
                isbn=book_model.isbn,
                description=book_model.description,
                available=book_model.available,
                created_at=book_model.created_at,
                updated_at=book_model.updated_at,
            )
        except Exception as e:
            raise InvalidBookDataException(
                field="model_conversion",
                value=str(book_model),
                reason=f"Failed to convert model to response: {str(e)}",
                details={"book_model": str(book_model)}
            )
    
    @staticmethod
    def models_to_responses(book_models: list[Book]) -> list[BookResponse]:
        """
        Преобразовать список моделей Book в список BookResponse.
        
        Args:
            book_models: Список моделей книг
        
        Returns:
            Список BookResponse
        """
        return [BookMapper.model_to_response(book) for book in book_models]
    
    @staticmethod
    def validate_book_year(year: int) -> bool:
        """
        Проверить валидность года книги.
        
        Args:
            year: Год книги
        
        Returns:
            True если год валиден
        
        Raises:
            InvalidBookDataException: Если год невалиден
        """
        from datetime import datetime
        current_year = datetime.now().year
        
        if year < 1000:
            raise InvalidBookDataException(
                field="year",
                value=year,
                reason="Year cannot be before 1000 (first printed book)"
            )
        
        if year > current_year:
            raise InvalidBookDataException(
                field="year",
                value=year,
                reason=f"Year cannot be in the future. Current year is {current_year}"
            )
        
        return True
