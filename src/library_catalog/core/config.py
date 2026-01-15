"""
Конфигурация приложения.
"""

from typing import Literal, Union, Optional
from functools import lru_cache

from pydantic import AnyUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    app_name: str = "Library Catalog API"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # Настройки PostgreSQL
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_db: str = "library_catalog"
    
    database_url: Optional[Union[PostgresDsn, AnyUrl]] = None
    
    @field_validator("database_url", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info):
        """Собираем DSN для подключения к БД."""
        if v:
            return v
            
        # Если URL не указан, собираем из настроек PostgreSQL
        values = info.data
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=values.get("postgres_user"),
            password=values.get("postgres_password"),
            host=values.get("postgres_host"),
            port=values.get("postgres_port"),
            path=values.get("postgres_db") or "",
        )

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
