"""News endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.models.user import User
from app.schemas.news import (
    NewsCreate,
    NewsUpdate,
    NewsResponse,
    NewsBrief,
    NewsFilter,
    NewsSearchRequest
)
from app.schemas.common import PaginatedResponse, PaginationParams, Message
from app.services.news_service import NewsService
from app.services.cache_service import get_cache_service
from app.core.constants import CACHE_TTL_MEDIUM
from app.api.v1.endpoints.recommendations import router as recommendations_router


router = APIRouter()

# Include recommendations router
router.include_router(recommendations_router, tags=["recommendations"])


@router.get("", response_model=PaginatedResponse[NewsBrief])
async def get_news_list(
    category_id: Optional[int] = Query(None, description="Filter by category"),
    source_id: Optional[int] = Query(None, description="Filter by source"),
    sentiment: Optional[str] = Query(None, description="Filter by sentiment"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    cache_service = Depends(get_cache_service)
):
    """Get list of news with filters.
    
    Args:
        category_id: Filter by category
        source_id: Filter by source
        sentiment: Filter by sentiment
        skip: Number of items to skip
        limit: Number of items to return
        db: Database session
        cache_service: Cache service
        
    Returns:
        Paginated news list
    """
    # Create cache key
    cache_key = f"news:list:{category_id}:{source_id}:{sentiment}:{skip}:{limit}"
    
    # Try to get from cache
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        return cached_data
    
    # Create filters
    filters = NewsFilter(
        category_id=category_id,
        source_id=source_id,
        sentiment=sentiment
    )
    
    # Get from database
    news_list, total = await NewsService.get_list(db, skip, limit, filters)
    
    # Create response
    response = PaginatedResponse.create(
        items=news_list,
        total=total,
        skip=skip,
        limit=limit
    )
    
    # Cache response
    await cache_service.set(cache_key, response.model_dump(), ttl=CACHE_TTL_MEDIUM)
    
    return response


@router.get("/trending", response_model=list[NewsBrief])
async def get_trending_news(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    cache_service = Depends(get_cache_service)
):
    """Get trending news.
    
    Args:
        limit: Number of news to return
        db: Database session
        cache_service: Cache service
        
    Returns:
        List of trending news
    """
    cache_key = f"news:trending:{limit}"
    
    # Try cache
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        return cached_data
    
    # Get trending
    news_list = await NewsService.get_trending(db, limit)
    
    # Cache
    await cache_service.set(cache_key, [n.__dict__ for n in news_list], ttl=CACHE_TTL_MEDIUM)
    
    return news_list


@router.get("/fresh", response_model=list[NewsBrief])
async def get_fresh_news(
    hours: int = Query(24, ge=1, le=168, description="Time window in hours (max 7 days)"),
    limit: int = Query(20, ge=1, le=100, description="Number of news to return"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    db: AsyncSession = Depends(get_db),
    cache_service = Depends(get_cache_service)
):
    """Get fresh news published within specified time window.
    
    Args:
        hours: Time window in hours (default 24, max 168 = 7 days)
        limit: Number of news to return
        category_id: Optional category filter
        db: Database session
        cache_service: Cache service
        
    Returns:
        List of fresh news sorted by published date (newest first)
    """
    cache_key = f"news:fresh:{hours}:{limit}:{category_id}"
    
    # Try cache
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        return cached_data
    
    # Get fresh news
    news_list = await NewsService.get_fresh(
        db, 
        hours=hours, 
        limit=limit,
        category_id=category_id
    )
    
    # Cache for 5 minutes (fresh news should update frequently)
    await cache_service.set(cache_key, [n.__dict__ for n in news_list], ttl=300)
    
    return news_list


@router.get("/{news_id}", response_model=NewsResponse)
async def get_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    cache_service = Depends(get_cache_service)
):
    """Get single news article.
    
    Args:
        news_id: News ID
        db: Database session
        cache_service: Cache service
        
    Returns:
        News article
        
    Raises:
        HTTPException: If news not found
    """
    cache_key = f"news:{news_id}"
    
    # Try cache
    cached_data = await cache_service.get(cache_key)
    if cached_data:
        # Increment views in background
        await NewsService.increment_views(db, news_id)
        return cached_data
    
    # Get from database
    news = await NewsService.get_by_id(db, news_id)
    
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )
    
    # Increment views
    await NewsService.increment_views(db, news_id)
    
    # Cache
    await cache_service.set(cache_key, news.__dict__, ttl=CACHE_TTL_MEDIUM)
    
    return news


@router.post("", response_model=NewsResponse, status_code=status.HTTP_201_CREATED)
async def create_news(
    news_in: NewsCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    cache_service = Depends(get_cache_service)
):
    """Create new news article (admin only).
    
    Args:
        news_in: News creation data
        db: Database session
        current_user: Current user (must be admin)
        cache_service: Cache service
        
    Returns:
        Created news
    """
    # Check for duplicate URL
    existing = await NewsService.get_by_url(db, news_in.url)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="News with this URL already exists"
        )
    
    news = await NewsService.create(db, news_in)
    
    # Invalidate cache
    await cache_service.delete_pattern("news:list:*")
    await cache_service.delete_pattern("news:trending:*")
    
    return news


@router.put("/{news_id}", response_model=NewsResponse)
async def update_news(
    news_id: int,
    news_in: NewsUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    cache_service = Depends(get_cache_service)
):
    """Update news article (admin only).
    
    Args:
        news_id: News ID
        news_in: Update data
        db: Database session
        current_user: Current user (must be admin)
        cache_service: Cache service
        
    Returns:
        Updated news
        
    Raises:
        HTTPException: If news not found
    """
    news = await NewsService.get_by_id(db, news_id, load_relations=False)
    
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )
    
    news = await NewsService.update(db, news, news_in)
    
    # Invalidate cache
    await cache_service.delete(f"news:{news_id}")
    await cache_service.delete_pattern("news:list:*")
    
    return news


@router.delete("/{news_id}", response_model=Message)
async def delete_news(
    news_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser),
    cache_service = Depends(get_cache_service)
):
    """Delete news article (admin only).
    
    Args:
        news_id: News ID
        db: Database session
        current_user: Current user (must be admin)
        cache_service: Cache service
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If news not found
    """
    deleted = await NewsService.delete(db, news_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )
    
    # Invalidate cache
    await cache_service.delete(f"news:{news_id}")
    await cache_service.delete_pattern("news:list:*")
    await cache_service.delete_pattern("news:trending:*")
    
    return Message(message="News deleted successfully")
