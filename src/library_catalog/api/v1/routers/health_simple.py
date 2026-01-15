"""
Простой health check без БД.
"""

from fastapi import APIRouter

router = APIRouter(tags=["Health"])


@router.get("/health")
async def health_check():
    """
    Простой health check.
    """
    return {
        "status": "healthy",
        "service": "library_catalog",
        "version": "1.0.0",
        "database": "unknown"
    }


@router.get("/health/db")
async def health_check_with_db():
    """
    Health check с проверкой БД (старый вариант).
    """
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import AsyncSession
    from ....core.database import get_db
    
    try:
        db = get_db()
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "service": "library_catalog",
        "version": "1.0.0",
        "database": db_status,
    }
