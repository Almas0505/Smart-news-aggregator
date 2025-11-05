"""API v1 router."""

from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, news, categories, sources, search, health


api_router = APIRouter()

# Include routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(news.router, prefix="/news", tags=["news"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(sources.router, prefix="/sources", tags=["sources"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
