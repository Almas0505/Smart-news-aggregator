"""Recommendations endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.news import NewsBrief
from app.services.recommendation_service import RecommendationService
from app.services.cache_service import get_cache_service
from app.core.constants import CACHE_TTL_LONG


router = APIRouter()


@router.get("/recommended", response_model=list[NewsBrief])
async def get_recommended_news(
    limit: int = Query(20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    cache_service = Depends(get_cache_service)
):
    """Get personalized news recommendations.
    
    Args:
        limit: Number of recommendations
        current_user: Current user
        db: Database session
        cache_service: Cache service
        
    Returns:
        List of recommended news
    """
    cache_key = f"recommendations:{current_user.id}:{limit}"
    
    # Try cache
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        return cached_data
    
    # Get recommendations
    news_list = await RecommendationService.get_recommendations(
        db,
        current_user.id,
        limit
    )
    
    # Cache
    await cache_service.set(
        cache_key,
        [n.__dict__ for n in news_list],
        ttl=CACHE_TTL_LONG
    )
    
    return news_list


@router.get("/{news_id}/similar", response_model=list[NewsBrief])
async def get_similar_news(
    news_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
    cache_service = Depends(get_cache_service)
):
    """Get similar news articles.
    
    Args:
        news_id: News ID
        limit: Number of similar articles
        db: Database session
        cache_service: Cache service
        
    Returns:
        List of similar news
    """
    cache_key = f"similar:{news_id}:{limit}"
    
    # Try cache
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        return cached_data
    
    # Get similar news
    news_list = await RecommendationService.get_similar_news(
        db,
        news_id,
        limit
    )
    
    # Cache
    await cache_service.set(
        cache_key,
        [n.__dict__ for n in news_list],
        ttl=CACHE_TTL_LONG
    )
    
    return news_list
