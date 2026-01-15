"""
Точка входа FastAPI приложения Library Catalog.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.errors import setup_exception_handlers
from .api.v1.routers.books import router as books_router
from .core.config import settings
from .core.clients import clients_manager
from .core.database import (
    init_db,
    check_db_connection,
    dispose_engine,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Lifespan контекст для управления жизненным циклом приложения.

    - При запуске: инициализация БД
    - При остановке: закрытие соединений
    """
    # Startup
    print("Starting Library Catalog API...")

    # Инициализация БД
    try:
        await init_db()
        db_status = await check_db_connection()
        if db_status:
            print("Database connection established")
        else:
            print("Database connection failed")
    except Exception as e:
        print(f"Database initialization failed: {e}")

    yield

    # Shutdown
    print("Shutting down Library Catalog API...")
    
    # Закрыть все внешние клиенты
    await clients_manager.close_all()
    
    # Закрыть соединения с БД
    await dispose_engine()
    
    print("Clean shutdown completed")


# Создать приложение с lifespan
app = FastAPI(
    title=settings.app_name,
    description="REST API для управления библиотечным каталогом",
    version="1.0.0",
    docs_url=settings.docs_url if not settings.is_production else None,
    redoc_url=settings.redoc_url if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
    lifespan=lifespan,
)

# Настроить CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настроить обработчики ошибок
setup_exception_handlers(app)

# Включить роутеры
app.include_router(
    books_router,
    prefix=settings.api_v1_prefix,
)


# Базовые эндпоинты
@app.get("/")
async def root():
    """Корневой эндпоинт."""
    return {
        "message": "Welcome to Library Catalog API",
        "version": "1.0.0",
        "docs": f"{settings.docs_url}" if settings.docs_url else None,
        "health": "/health",
    }


@app.get("/health")
async def health_check():
    """Health check эндпоинт."""
    db_healthy = await check_db_connection()

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "library_catalog",
        "version": "1.0.0",
        "database": "connected" if db_healthy else "disconnected",
    }


@app.get("/info")
async def info():
    """Информация о приложении."""
    return {
        "app": settings.app_name,
        "environment": settings.environment,
        "debug": settings.debug,
        "database_url": str(settings.database_url).split("@")[0] + "@***",
        "api_prefix": settings.api_v1_prefix,
    }


# Для запуска через python -m
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
