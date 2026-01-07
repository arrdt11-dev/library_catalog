"""
Pydantic схемы для работы с книгами.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class BookBase(BaseModel):
    """Базовая схема для книги."""

    title: str = Field(..., min_length=1, max_length=500, description="Название книги")
    author: str = Field(..., min_length=1, max_length=200, description="Автор книги")
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN книги")
    publication_year: Optional[int] = Field(
        None, ge=0, le=2100, description="Год публикации"
    )
    genre: Optional[str] = Field(None, max_length=100, description="Жанр книги")
    description: Optional[str] = Field(None, description="Описание книги")

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
    isbn: Optional[str] = Field(None, max_length=20, description="ISBN книги")
    publication_year: Optional[int] = Field(
        None, ge=0, le=2100, description="Год публикации"
    )
    genre: Optional[str] = Field(None, max_length=100, description="Жанр книги")
    description: Optional[str] = Field(None, description="Описание книги")

    model_config = ConfigDict(from_attributes=True)


class BookResponse(BookBase):
    """Схема для ответа с книгой."""

    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
