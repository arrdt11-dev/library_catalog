import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd()))

async def check_tables():
    try:
        from sqlalchemy import text
        from src.library_catalog.core.database import engine
        
        print("Проверяем таблицы в базе данных...")
        
        async with engine.connect() as conn:
            # Смотрим все таблицы
            result = await conn.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """))
            
            tables = result.fetchall()
            
            if tables:
                print("Найдены таблицы:")
                for table in tables:
                    print(f"  - {table[0]}")
            else:
                print("Таблиц пока нет. Это нормально для первого запуска.")
                
            # Проверяем, есть ли таблицы книг или авторов
            result = await conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('books', 'authors');
            """))
            
            book_tables_count = result.scalar()
            
            if book_tables_count == 0:
                print("Таблиц 'books' и 'authors' пока нет. Нужно будет создать.")
            else:
                print(f"Таблиц книг/авторов найдено: {book_tables_count}")
        
        return True
        
    except Exception as e:
        print(f"Ошибка при проверке таблиц: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(check_tables())
    sys.exit(0 if success else 1)
