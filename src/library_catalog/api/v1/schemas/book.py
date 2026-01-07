"""
Pydantic схемы для книг.
"""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, validator


# Базовые ограничения для повторного использования
class BookConstraints:
    """Ограничения для полей книги."""

    TITLE_MIN_LENGTH = 1
    TITLE_MAX_LENGTH = 500

    AUTHOR_MIN_LENGTH = 1
    AUTHOR_MAX_LENGTH = 300

    GENRE_MIN_LENGTH = 1
    GENRE_MAX_LENGTH = 100

    ISBN_MIN_LENGTH = 10
    ISBN_MAX_LENGTH = 20

    YEAR_MIN = 1000  # Первая печатная книга
    YEAR_MAX = 2100  # Будущее с запасом

    PAGES_MIN = 1
    PAGES_MAX = 10000


class BookBase(BaseModel):
    """Базовая схема книги."""

    title: str = Field(
        ...,
        min_length=BookConstraints.TITLE_MIN_LENGTH,
        max_length=BookConstraints.TITLE_MAX_LENGTH,
        example="Война и мир",
    )

    author: str = Field(
        ...,
        min_length=BookConstraints.AUTHOR_MIN_LENGTH,
        max_length=BookConstraints.AUTHOR_MAX_LENGTH,
        example="Лев Толстой",
    )

    year: int = Field(
        ...,
        ge=BookConstraints.YEAR_MIN,
        le=BookConstraints.YEAR_MAX,
        example=1869,
    )

    genre: str = Field(
        ...,
        min_length=BookConstraints.GENRE_MIN_LENGTH,
        max_length=BookConstraints.GENRE_MAX_LENGTH,
        example="Роман",
    )

    pages: int = Field(
        ...,
        ge=BookConstraints.PAGES_MIN,
        le=BookConstraints.PAGES_MAX,
        example=1225,
    )

    isbn: Optional[str] = Field(
        None,
        min_length=BookConstraints.ISBN_MIN_LENGTH,
        max_length=BookConstraints.ISBN_MAX_LENGTH,
        example="978-5-389-06256-0",
    )

    description: Optional[str] = Field(
        None,
        example="Роман-эпопея, описывающий русское общество в эпоху войн против Наполеона.",
    )

    available: bool = Field(
        True,
        example=True,
    )

    @validator("year")
    def validate_year_not_in_future(cls, value: int) -> int:
        """Проверяем что год не в будущем."""
        current_year = datetime.now().year
        if value > current_year:
            raise ValueError(
                f"Year cannot be in the future. Current year is {current_year}"
            )
        return value

    @validator("isbn")
    def validate_isbn_format(cls, value: Optional[str]) -> Optional[str]:
        """Проверяем формат ISBN (опционально)."""
        if value is None:
            return None

        # Убираем дефисы и пробелы
        clean_isbn = value.replace("-", "").replace(" ", "")

        # ISBN-10 или ISBN-13
        if len(clean_isbn) not in (10, 13):
            raise ValueError("ISBN must be 10 or 13 digits")

        # Проверяем что только цифры (последний символ может быть X для ISBN-10)
        if not clean_isbn[:-1].isdigit():
            raise ValueError("ISBN must contain only digits (except last character)")

        return value


class BookCreate(BookBase):
    """Схема для создания книги."""

    pass


class BookUpdate(BaseModel):
    """Схема для обновления книги (все поля опциональны)."""

    title: Optional[str] = Field(
        None,
        min_length=BookConstraints.TITLE_MIN_LENGTH,
        max_length=BookConstraints.TITLE_MAX_LENGTH,
    )

    author: Optional[str] = Field(
        None,
        min_length=BookConstraints.AUTHOR_MIN_LENGTH,
        max_length=BookConstraints.AUTHOR_MAX_LENGTH,
    )

    year: Optional[int] = Field(
        None,
        ge=BookConstraints.YEAR_MIN,
        le=BookConstraints.YEAR_MAX,
    )

    genre: Optional[str] = Field(
        None,
        min_length=BookConstraints.GENRE_MIN_LENGTH,
        max_length=BookConstraints.GENRE_MAX_LENGTH,
    )

    pages: Optional[int] = Field(
        None,
        ge=BookConstraints.PAGES_MIN,
        le=BookConstraints.PAGES_MAX,
    )

    isbn: Optional[str] = Field(
        None,
        min_length=BookConstraints.ISBN_MIN_LENGTH,
        max_length=BookConstraints.ISBN_MAX_LENGTH,
    )

    description: Optional[str] = None

    available: Optional[bool] = None

    @validator("year")
    def validate_year_not_in_future(cls, value: Optional[int]) -> Optional[int]:
        if value is None:
            return None

        current_year = datetime.now().year
        if value > current_year:
            raise ValueError(
                f"Year cannot be in the future. Current year is {current_year}"
            )
        return value


class BookInDB(BookBase):
    """Схема книги в БД (с ID и timestamp)."""

    book_id: UUID = Field(..., example="123e4567-e89b-12d3-a456-426614174000")
    created_at: datetime = Field(..., example="2024-01-07T10:30:00Z")
    updated_at: datetime = Field(..., example="2024-01-07T10:30:00Z")

    class Config:
        from_attributes = True  # Для совместимости с ORM


class BookResponse(BookInDB):
    """Схема для ответа API (может расширяться)."""

    pass


class BookListResponse(BaseModel):
    """Схема для списка книг с пагинацией."""

    items: list[BookResponse] = Field(..., example=[])
    total: int = Field(..., example=0, ge=0)
    limit: int = Field(..., example=20, ge=1)
    offset: int = Field(..., example=0, ge=0)
