"""Health check endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.cache_service import cache_service

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    """Health check endpoint."""
    # Check database connection
    try:
        stmt = text("SELECT 1")
        result = await db.execute(stmt)
        # result.scalar_one_or_none() returns the scalar value or None
        value = result.scalar_one_or_none()
        if value is not None:
            db_status = "healthy"
        else:
            db_status = "unhealthy"
    except Exception as e:
        print(f"Database health check error: {e}")
        db_status = "unhealthy"

    # Check Redis connection
    try:
        await cache_service.redis_client.ping()
        redis_status = "healthy"
    except Exception:
        redis_status = "unhealthy"

    return {
        "status": "ok",
        "services": {
            "database": db_status,
            "redis": redis_status,
        }
    }