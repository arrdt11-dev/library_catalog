"""
Менеджер для управления внешними клиентами.
"""

import logging
from typing import Optional

from ..external.openlibrary.client import OpenLibraryClient
from .config import settings

logger = logging.getLogger(__name__)


class ClientsManager:
    """
    Менеджер для управления внешними клиентами.
    
    Управляет созданием и закрытием клиентов.
    """
    
    def __init__(self):
        """Инициализация менеджера."""
        self._openlibrary: Optional[OpenLibraryClient] = None
    
    def get_openlibrary(self) -> OpenLibraryClient:
        """
        Получить OpenLibrary клиент.
        
        Returns:
            OpenLibraryClient: Клиент Open Library
        """
        if self._openlibrary is None:
            logger.info("Создание OpenLibrary клиента")
            self._openlibrary = OpenLibraryClient(
                base_url=settings.openlibrary_base_url,
                timeout=settings.openlibrary_timeout,
            )
        return self._openlibrary
    
    async def close_all(self):
        """Закрыть все клиенты."""
        if self._openlibrary:
            logger.info("Закрытие OpenLibrary клиента")
            await self._openlibrary.close()
            self._openlibrary = None


# Глобальный экземпляр менеджера
clients_manager = ClientsManager()
