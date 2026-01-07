"""
Клиент для Open Library API.
"""

import httpx
from typing import Dict, Optional

from ..base.base_client import BaseApiClient
from ...domain.exceptions import OpenLibraryException, OpenLibraryTimeoutException


class OpenLibraryClient(BaseApiClient):
    """Клиент для Open Library API."""

    def __init__(
        self,
        base_url: str = "https://openlibrary.org",
        timeout: float = 10.0,
    ):
        super().__init__(base_url, timeout=timeout, retries=2, backoff=0.5)

    def client_name(self) -> str:
        return "openlibrary"

    async def search_by_isbn(self, isbn: str) -> Dict:
        """
        Поиск книги по ISBN.

        Args:
            isbn: ISBN-10 или ISBN-13

        Returns:
            dict: Данные книги (cover_url, subjects, etc.)

        Raises:
            OpenLibraryException: При ошибке API
        """
        try:
            data = await self._get("/search.json", params={"isbn": isbn, "limit": 1})

            docs = data.get("docs", [])
            if not docs:
                return {}

            return self._extract_book_data(docs[0])

        except httpx.TimeoutException:
            raise OpenLibraryTimeoutException(self.timeout)
        except httpx.HTTPError as e:
            raise OpenLibraryException(str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error in search_by_isbn: {e}")
            return {}

    async def search_by_title_author(self, title: str, author: str) -> Dict:
        """Поиск по названию и автору."""
        try:
            data = await self._get(
                "/search.json", params={"title": title, "author": author, "limit": 1}
            )

            docs = data.get("docs", [])
            if not docs:
                return {}

            return self._extract_book_data(docs[0])

        except httpx.TimeoutException:
            raise OpenLibraryTimeoutException(self.timeout)
        except httpx.HTTPError as e:
            raise OpenLibraryException(str(e))
        except Exception as e:
            self.logger.error(f"Unexpected error in search_by_title_author: {e}")
            return {}

    async def enrich(
        self,
        title: str,
        author: str,
        isbn: Optional[str] = None,
    ) -> Dict:
        """
        Обогатить данные книги.

        Сначала пытается найти по ISBN, затем по title+author.

        Returns:
            dict: Обогащенные данные или пустой словарь
        """
        # Попытка 1: По ISBN
        if isbn:
            data = await self.search_by_isbn(isbn)
            if data:
                return data

        # Попытка 2: По title + author
        return await self.search_by_title_author(title, author)

    def _extract_book_data(self, doc: dict) -> dict:
        """
        Извлечь нужные поля из ответа Open Library.

        Args:
            doc: Документ из массива docs

        Returns:
            dict: Обработанные данные
        """
        result = {}

        # Cover URL
        if cover_id := doc.get("cover_i"):
            result["cover_url"] = (
                f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
            )

        # Subjects (темы)
        if subjects := doc.get("subject"):
            result["subjects"] = subjects[:10]  # Первые 10

        # Publisher
        if publisher := doc.get("publisher"):
            result["publisher"] = (
                publisher[0] if isinstance(publisher, list) and publisher else publisher
            )

        # Language
        if language := doc.get("language"):
            result["language"] = (
                language[0] if isinstance(language, list) and language else language
            )

        # Description (из description или first_sentence)
        if description := doc.get("description"):
            if isinstance(description, str):
                result["description"] = description
            elif isinstance(description, dict) and "value" in description:
                result["description"] = description["value"]

        # Author (полное имя)
        if author_name := doc.get("author_name"):
            result["author_full"] = author_name[0] if author_name else None

        # Title (полное название)
        if title := doc.get("title"):
            result["title_full"] = title

        # First publish year
        if first_publish_year := doc.get("first_publish_year"):
            result["first_publish_year"] = first_publish_year

        return result
