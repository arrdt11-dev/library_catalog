"""
Кастомные исключения для приложения.
"""

from typing import Any, Optional
from uuid import UUID


class DomainException(Exception):
    """Базовое исключение доменного слоя."""
    
    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class BookNotFoundException(DomainException):
    """Книга не найдена."""
    
    def __init__(self, book_id: Optional[UUID] = None, details: Optional[dict] = None):
        message = f"Book not found"
        if book_id:
            message = f"Book with id {book_id} not found"
        super().__init__(message, details)
        self.book_id = book_id


class BookAlreadyExistsException(DomainException):
    """Книга уже существует."""
    
    def __init__(self, title: str, author: str, year: int, details: Optional[dict] = None):
        message = f"Book '{title}' by {author} ({year}) already exists"
        super().__init__(message, details)
        self.title = title
        self.author = author
        self.year = year


class InvalidBookDataException(DomainException):
    """Некорректные данные книги."""
    
    def __init__(self, field: str, value: Any, reason: str, details: Optional[dict] = None):
        message = f"Invalid book data: {field} = {value} - {reason}"
        super().__init__(message, details)
        self.field = field
        self.value = value
        self.reason = reason


class BookNotAvailableException(DomainException):
    """Книга недоступна для выдачи."""
    
    def __init__(self, book_id: UUID, details: Optional[dict] = None):
        message = f"Book with id {book_id} is not available"
        super().__init__(message, details)
        self.book_id = book_id


class RepositoryException(DomainException):
    """Ошибка в репозитории."""
    pass


class ServiceException(DomainException):
    """Ошибка в сервисе."""
    pass
