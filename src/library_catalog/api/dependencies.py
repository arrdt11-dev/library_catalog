"""
Dependency Injection контейнер.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.clients import clients_manager
from ..core.database import get_db
from ..data.repositories.book_repository import BookRepository
from ..domain.services.book_service import BookService
from ..external.openlibrary.client import OpenLibraryClient


# ========== EXTERNAL CLIENTS ==========

def get_openlibrary_client() -> OpenLibraryClient:
    """
    Получить OpenLibrary клиент из менеджера.
    """
    return clients_manager.get_openlibrary()


# ========== REPOSITORIES ==========

async def get_book_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> BookRepository:
    """
    Создать BookRepository для текущей сессии.
    """
    return BookRepository(db)


# ========== SERVICES ==========

async def get_book_service(
    book_repo: Annotated[BookRepository, Depends(get_book_repository)],
    ol_client: Annotated[OpenLibraryClient, Depends(get_openlibrary_client)],
) -> BookService:
    """
    Создать BookService с внедренными зависимостями.
    """
    return BookService(
        book_repository=book_repo,
        openlibrary_client=ol_client,
    )


# ========== TYPE ALIASES ==========

OpenLibraryClientDep = Annotated[OpenLibraryClient, Depends(get_openlibrary_client)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
BookRepositoryDep = Annotated[BookRepository, Depends(get_book_repository)]
BookServiceDep = Annotated[BookService, Depends(get_book_service)]
