import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

async def test_postgres():
    try:
        from sqlalchemy import text
        from src.library_catalog.core.config import settings
        from src.library_catalog.core.database import engine
        
        print(f"🔄 Проверяем подключение к PostgreSQL...")
        print(f"Database URL: {settings.database_url}")
        
        async with engine.connect() as conn:
            # Проверка версии PostgreSQL
            result = await conn.execute(text("SELECT version();"))
            version = result.scalar()
            print(f"✅ Подключено к PostgreSQL: {version.split(',')[0]}")
            
            # Проверка текущей базы данных
            result = await conn.execute(text("SELECT current_database();"))
            db_name = result.scalar()
            print(f"✅ База данных: {db_name}")
            
            # Проверка соединения
            result = await conn.execute(text("SELECT 1 as test_value"))
            test_value = result.scalar()
            print(f"✅ Тестовый запрос: {test_value}")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения к PostgreSQL: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_postgres())
    sys.exit(0 if success else 1)
