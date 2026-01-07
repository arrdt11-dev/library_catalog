import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Импортировать config и Base
from src.library_catalog.core.config import settings
from src.library_catalog.core.database import Base

# Импортировать все модели (ОБЯЗАТЕЛЬНО!)
from src.library_catalog.data.models import book  # noqa

# this is the Alembic Config object
config = context.config

# Установить database_url из settings
# ⚠️ ВАЖНО: Используем sync версию URL для alembic
sync_url = str(settings.database_url).replace("+asyncpg", "")
config.set_main_option("sqlalchemy.url", sync_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Установить target_metadata из Base
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' mode with async engine."""
    # Временно используем sync engine для миграций
    from sqlalchemy import engine_from_config

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        do_run_migrations(connection)

    connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Запускаем в отдельном event loop
    loop = asyncio.get_event_loop()
    if loop.is_running():
        # Если loop уже запущен (в async приложении)
        import nest_asyncio

        nest_asyncio.apply()
        loop.run_until_complete(run_async_migrations())
    else:
        # Обычный запуск
        asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
