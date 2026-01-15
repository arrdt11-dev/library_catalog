"""
Мапперы для преобразования данных между слоями.
"""

from typing import List

from ...data.models.book import Book
from ..schemas.book import BookResponse


class BookMapper:
    """Маппер для преобразования Book entity в DTO."""

    @staticmethod
    def to_response(book: Book) -> BookResponse:
        """
        Преобразовать Book ORM модель в BookResponse DTO.

        Args:
            book: ORM модель из БД

        Returns:
            BookResponse: Pydantic модель для API
        """
        return BookResponse(
            book_id=book.book_id,
            title=book.title,
            author=book.author,
            year=book.year,
            genre=book.genre,
            pages=book.pages,
            isbn=book.isbn,
            description=book.description,
            available=book.available,
            extra=book.extra,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )

    @staticmethod
    def to_responses(books: List[Book]) -> List[BookResponse]:
        """Преобразовать список книг."""
        return [BookMapper.to_response(book) for book in books]
