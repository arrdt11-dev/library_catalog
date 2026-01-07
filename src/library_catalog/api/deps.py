"""
Зависимости (dependencies) для FastAPI.
"""

from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..domain.services.book_service import BookService


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
    yield BookService(db)
