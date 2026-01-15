"""
Pydantic схемы для работы с книгами.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, validator
from uuid import UUID


class BookBase(BaseModel):
    """Базовая схема для книги."""

    title: str = Field(..., min_length=1, max_length=500, description="Название книги")
    author: str = Field(..., min_length=1, max_length=200, description="Автор книги")
    year: int = Field(..., ge=1000, le=2100, description="Год публикации")
    genre: str = Field(..., max_length=100, description="Жанр книги")
    pages: int = Field(..., ge=1, description="Количество страниц")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN книги")
    description: Optional[str] = Field(None, description="Описание книги")

    @validator("year")
    def validate_year_not_in_future(cls, value: int) -> int:
        """Проверяем что год не в будущем."""
        from datetime import datetime
        current_year = datetime.now().year
        if value > current_year:
            raise ValueError(f"Year cannot be in the future: {value}")
        return value

    model_config = ConfigDict(from_attributes=True)


class BookCreate(BookBase):
    """Схема для создания книги."""
    pass


class BookUpdate(BaseModel):
    """Схема для обновления книги."""

    title: Optional[str] = Field(
        None, min_length=1, max_length=500, description="Название книги"
    )
    author: Optional[str] = Field(
        None, min_length=1, max_length=200, description="Автор книги"
    )
    year: Optional[int] = Field(None, ge=1000, le=2100, description="Год публикации")
    genre: Optional[str] = Field(None, max_length=100, description="Жанр книги")
    pages: Optional[int] = Field(None, ge=1, description="Количество страниц")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN книги")
    description: Optional[str] = Field(None, description="Описание книги")

    model_config = ConfigDict(from_attributes=True)


class BookResponse(BookBase):
    """Схема для ответа с книгой."""

    book_id: UUID
    available: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    extra: Optional[dict] = None

    model_config = ConfigDict(from_attributes=True)
