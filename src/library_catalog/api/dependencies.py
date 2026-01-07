"""
Dependency Injection контейнер.
"""

from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.config import settings
from ..external.openlibrary.client import OpenLibraryClient


# ========== EXTERNAL CLIENTS (Singletons) ==========


@lru_cache
def get_openlibrary_client() -> OpenLibraryClient:
    """
    Получить singleton OpenLibraryClient.

    lru_cache создает клиент один раз и переиспользует.
    """
    return OpenLibraryClient(
        base_url=settings.openlibrary_base_url,
        timeout=settings.openlibrary_timeout,
    )


# ========== TYPE ALIASES ДЛЯ УДОБСТВА ==========

OpenLibraryClientDep = Annotated[OpenLibraryClient, Depends(get_openlibrary_client)]
DbSessionDep = Annotated[AsyncSession, Depends(get_db)]
