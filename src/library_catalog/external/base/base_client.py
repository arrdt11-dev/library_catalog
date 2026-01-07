"""
Базовый HTTP клиент для внешних API.
"""

from abc import ABC, abstractmethod
import asyncio
import httpx
import logging
import time
from typing import Any, Dict, Optional


class BaseApiClient(ABC):
    """
    Базовый класс для HTTP клиентов внешних API.

    Включает:
    - Retry логику
    - Обработку ошибок
    - Логирование
    - Timeout management
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 10.0,
        retries: int = 3,
        backoff: float = 0.5,
    ):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff
        self._client: Optional[httpx.AsyncClient] = None
        self.logger = logging.getLogger(self.client_name())

    @abstractmethod
    def client_name(self) -> str:
        """Имя клиента для логирования."""
        pass

    @property
    def client(self) -> httpx.AsyncClient:
        """Ленивая инициализация клиента."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    def _build_url(self, path: str) -> str:
        """Построить полный URL."""
        if not path.startswith("/"):
            path = "/" + path
        return self.base_url + path

    async def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict] = None,
        json: Optional[Dict] = None,
        headers: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """
        Выполнить HTTP запрос с retry логикой.

        Returns:
            dict: JSON ответ

        Raises:
            httpx.TimeoutException: При таймауте
            httpx.HTTPError: При HTTP ошибке
        """
        url = self._build_url(path)

        for attempt in range(self.retries):
            try:
                self.logger.debug(f"{method} {url} params={params}")

                response = await self.client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    headers=headers,
                )

                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                if attempt == self.retries - 1:
                    self.logger.error(f"Timeout after {self.retries} attempts")
                    raise

                wait_time = self.backoff * (2**attempt)
                self.logger.warning(f"Timeout, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as e:
                # 5xx ошибки - retry
                if e.response.status_code >= 500 and attempt < self.retries - 1:
                    wait_time = self.backoff * (2**attempt)
                    self.logger.warning(
                        f"Server error {e.response.status_code}, retrying in {wait_time}s..."
                    )
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"HTTP error {e.response.status_code}: {e}")
                    raise

            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                raise

    async def _get(self, path: str, **kwargs) -> Dict[str, Any]:
        """GET запрос."""
        return await self._request("GET", path, **kwargs)

    async def close(self) -> None:
        """Закрыть HTTP клиент."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Поддержка async context manager."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Закрыть клиент при выходе из контекста."""
        await self.close()
