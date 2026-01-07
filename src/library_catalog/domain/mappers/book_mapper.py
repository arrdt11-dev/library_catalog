"""
Мапперы для преобразования данных между слоями.
"""

from ...data.models.book import Book
from ...domain.schemas.book import BookResponse


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
            id=book.id,
            title=book.title,
            author=book.author,
            isbn=book.isbn,
            publication_year=book.publication_year,
            genre=book.genre,
            description=book.description,
            created_at=book.created_at,
            updated_at=book.updated_at,
        )

    @staticmethod
    def to_responses(books: list[Book]) -> list[BookResponse]:
        """Преобразовать список книг."""
        return [BookMapper.to_response(book) for book in books]
