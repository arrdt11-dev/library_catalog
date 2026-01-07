"""
Pydantic схемы для Open Library API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class OpenLibrarySearchDoc(BaseModel):
    """Документ из поиска Open Library."""

    title: str
    author_name: Optional[List[str]] = Field(None, alias="author_name")
    cover_i: Optional[int] = Field(None, alias="cover_i")
    subject: Optional[List[str]] = None
    publisher: Optional[List[str]] = None
    language: Optional[List[str]] = None
    ratings_average: Optional[float] = Field(None, alias="ratings_average")
    description: Optional[str] = None
    first_publish_year: Optional[int] = Field(None, alias="first_publish_year")

    class Config:
        populate_by_name = True  # Позволяет использовать alias и обычные имена


class OpenLibrarySearchResponse(BaseModel):
    """Ответ от /search.json"""

    numFound: int
    docs: List[OpenLibrarySearchDoc]
