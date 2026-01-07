"""
Зависимости (dependencies) для FastAPI.
"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..data.repositories.book_repository import BookRepository
from ..domain.services.book_service import BookService
from ..external.openlibrary.client import OpenLibraryClient
from ..core.config import settings


# Функция для получения BookRepository
async def get_book_repository(
    db: AsyncSession = Depends(get_db),
) -> BookRepository:
    """Получить BookRepository."""
    return BookRepository(db)


# Функция для получения OpenLibraryClient
def get_openlibrary_client() -> OpenLibraryClient:
    """Получить OpenLibraryClient (singleton)."""
    return OpenLibraryClient(
        base_url=settings.openlibrary_base_url,
        timeout=settings.openlibrary_timeout,
    )


# Функция для получения BookService
async def get_book_service(
    db: AsyncSession = Depends(get_db),
) -> AsyncGenerator[BookService, None]:
    """
    Dependency для получения BookService.

    Использование в роутерах:
    @router.post("/books")
    async def create_book(
        book_create: BookCreate,
        book_service: BookService = Depends(get_book_service),
    ):
        ...
    """
    # Создаем зависимости
    book_repo = BookRepository(db)
    ol_client = OpenLibraryClient(
        base_url=settings.openlibrary_base_url,
        timeout=settings.openlibrary_timeout,
    )

    # Создаем сервис
    yield BookService(
        book_repository=book_repo,
        openlibrary_client=ol_client,
    )
