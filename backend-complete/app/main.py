"""Main FastAPI application."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.api.v1 import api_router
from app.db.base import Base
from app.db.session import engine
from app.db.init_db import init_db


logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events.
    
    Args:
        app: FastAPI application
    """
    # Startup
    logger.info("Starting application...")
    
    # Setup logging
    setup_logging()
    
    # Initialize cache service
    from app.services.cache_service import cache_service
    await cache_service.connect()
    
    # Create database tables
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)  # Uncomment to drop all tables
        await conn.run_sync(Base.metadata.create_all)
    
    # Initialize database with initial data
    try:
        await init_db()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await cache_service.disconnect()
    await engine.dispose()
    logger.info("Application shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)


# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint.
    
    Returns:
        Welcome message
    """
    return {
        "message": "Welcome to Smart News Aggregator API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint.
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors.
    
    Args:
        request: Request object
        exc: Exception
        
    Returns:
        JSON response
    """
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle 500 errors.
    
    Args:
        request: Request object
        exc: Exception
        
    Returns:
        JSON response
    """
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
