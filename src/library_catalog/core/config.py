"""
Конфигурация приложения.
"""

from typing import Literal, Union
from functools import lru_cache

from pydantic import AnyUrl, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    app_name: str = "Library Catalog API"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # Изменяем с PostgresDsn на AnyUrl чтобы поддерживать SQLite
    database_url: Union[PostgresDsn, AnyUrl] = "sqlite+aiosqlite:///./library.db"
    database_pool_size: int = 20

    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    cors_origins: list[str] = ["*"]

    openlibrary_base_url: str = "https://openlibrary.org"
    openlibrary_timeout: float = 10.0

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )

    @property
    def is_production(self) -> bool:
        """Проверка, что окружение production."""
        return self.environment == "production"


@lru_cache
def get_settings() -> Settings:
    """Получение настроек с кэшированием."""
    return Settings()


settings = get_settings()
