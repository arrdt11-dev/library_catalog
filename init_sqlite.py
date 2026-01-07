"""
Скрипт для инициализации базы данных SQLite.
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text


async def init_database():
    """Создать таблицы в SQLite."""
    # Используем SQLite
    DATABASE_URL = "sqlite+aiosqlite:///./library.db"

    engine = create_async_engine(DATABASE_URL, echo=True)

    async with engine.begin() as conn:
        # Создаем таблицу books
        await conn.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(500) NOT NULL,
                author VARCHAR(200) NOT NULL,
                isbn VARCHAR(20),
                publication_year INTEGER,
                genre VARCHAR(100),
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
            )
        )
        print("✅ SQLite database 'library.db' created successfully")
        print("✅ Table 'books' created successfully")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(init_database())
