"""
ORM модель книги.
"""

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Integer, JSON, String, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from ...core.database import Base


class Book(Base):
    """Модель книги."""

    __tablename__ = "books"

    # Primary Key
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
        nullable=False,
    )

    # Основные поля
    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True,
    )

    author: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
        index=True,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        index=True,
    )

    genre: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    pages: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    # Опциональные поля
    isbn: Mapped[Optional[str]] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    extra: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Строковое представление."""
        return f"<Book(id={self.book_id}, title='{self.title}')>"


# Дополнительный составной индекс для часто используемых запросов
__table_args__ = (
    Index("ix_books_author_title", "author", "title"),
    Index("ix_books_genre_year", "genre", "year"),
)
