"""Search endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.news import NewsSearchRequest, NewsBrief
from app.schemas.common import PaginatedResponse
from app.services.search_service import get_search_service, SearchService
from app.services.news_service import NewsService


router = APIRouter()


@router.post("", response_model=PaginatedResponse[NewsBrief])
async def search_news(
    search_request: NewsSearchRequest,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    search_service: SearchService = Depends(get_search_service)
):
    """Search news articles.
    
    Args:
        search_request: Search parameters
        skip: Number of items to skip
        limit: Number of items to return
        db: Database session
        search_service: Search service
        
    Returns:
        Paginated search results
    """
    # Search in ElasticSearch
    results = await search_service.search(
        query=search_request.query,
        category_id=search_request.category_id,
        source_id=search_request.source_id,
        date_from=search_request.date_from,
        date_to=search_request.date_to,
        size=limit,
        from_=skip
    )
    
    # Extract news IDs
    hits = results.get("hits", {}).get("hits", [])
    news_ids = [int(hit["_id"]) for hit in hits]
    
    # Get full news data from database
    news_list = []
    for news_id in news_ids:
        news = await NewsService.get_by_id(db, news_id)
        if news:
            news_list.append(news)
    
    # Get total
    total = results.get("hits", {}).get("total", {}).get("value", 0)
    
    return PaginatedResponse.create(
        items=news_list,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/suggestions")
async def get_search_suggestions(
    q: str = Query(..., min_length=2, description="Search query prefix"),
    limit: int = Query(5, ge=1, le=10),
    search_service: SearchService = Depends(get_search_service)
):
    """Get search suggestions.
    
    Args:
        q: Search query prefix
        limit: Number of suggestions
        search_service: Search service
        
    Returns:
        List of suggestions
    """
    suggestions = await search_service.suggest(q, limit)
    return {"suggestions": suggestions}
