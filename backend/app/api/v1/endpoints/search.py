"""Search endpoints - Full-text and semantic search."""

from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db.session import get_db
from app.schemas.news import NewsBrief
from app.schemas.search import (
    SearchQuery,
    SearchResponse,
    SemanticSearchRequest,
    SemanticSearchResponse,
    SuggestRequest,
    SuggestResponse,
    IndexStatsResponse,
    SearchFilters
)
from app.services.elasticsearch_service import elasticsearch_service
from app.services.news_service import NewsService
from app.core.logging import get_logger


logger = get_logger(__name__)
router = APIRouter()



@router.post("/search", response_model=SearchResponse)
async def search_news(
    search_query: SearchQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    Full-text search with filters.
    
    Search across title, content, summary with support for:
    - Category filtering
    - Source filtering
    - Sentiment filtering
    - Date range filtering
    - Tag filtering
    - Aggregations/facets
    
    Args:
        search_query: Search parameters
        db: Database session
        
    Returns:
        Search results with aggregations
    """
    try:
        # Check if index exists
        if not await elasticsearch_service.index_exists():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Search index not available. Please contact administrator."
            )
        
        # Perform search
        results = await elasticsearch_service.search(
            query=search_query.query,
            filters=search_query.filters,
            page=search_query.page,
            size=search_query.size,
            sort_by=search_query.sort_by
        )
        
        return results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search failed"
        )


@router.post("/semantic-search", response_model=SemanticSearchResponse)
async def semantic_search(
    request: SemanticSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Semantic search using text embeddings.
    
    Finds articles similar in meaning to the query, even if different words are used.
    
    Args:
        request: Semantic search parameters
        db: Database session
        
    Returns:
        Similar articles ranked by semantic similarity
    """
    try:
        # Get embedding for query from ML service
        import httpx
        from app.core.config import settings
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/api/create-embedding",
                json={"text": request.query},
                timeout=30.0
            )
            response.raise_for_status()
            embedding_data = response.json()
            embedding = embedding_data["embedding"]
        
        # Perform semantic search
        results = await elasticsearch_service.semantic_search(
            embedding=embedding,
            filters=request.filters,
            size=request.size,
            min_score=request.min_score
        )
        
        return SemanticSearchResponse(
            results=results,
            total=len(results),
            query=request.query
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Semantic search failed"
        )


@router.get("/suggestions", response_model=SuggestResponse)
@router.get("/suggestions", response_model=SuggestResponse)
async def get_suggestions(
    text: str = Query(..., min_length=2, max_length=100),
    size: int = Query(5, ge=1, le=20)
):
    """
    Get search suggestions/autocomplete.
    
    Args:
        text: Partial search text
        size: Number of suggestions
        
    Returns:
        List of suggested queries
    """
    try:
        suggestions = await elasticsearch_service.suggest(text, size)
        return SuggestResponse(suggestions=suggestions, text=text)
    except Exception as e:
        logger.error(f"Suggestions error: {e}")
        return SuggestResponse(suggestions=[], text=text)


@router.get("/stats", response_model=IndexStatsResponse)
async def get_search_stats():
    """
    Get Elasticsearch index statistics.
    
    Returns:
        Index stats (document count, size)
    """
    try:
        stats = await elasticsearch_service.get_stats()
        return IndexStatsResponse(**stats)
    except Exception as e:
        logger.error(f"Stats error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get statistics"
        )


@router.post("/index/rebuild")
async def rebuild_index(
    delete_existing: bool = Query(False, description="Delete existing index"),
    db: AsyncSession = Depends(get_db)
):
    """
    Rebuild Elasticsearch index.
    
    **Admin only** - Recreates the index and reindexes all news.
    
    Args:
        delete_existing: Whether to delete existing index first
        db: Database session
        
    Returns:
        Status message
    """
    try:
        # Create/recreate index
        success = await elasticsearch_service.create_index(delete_if_exists=delete_existing)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create index"
            )
        
        # Get all news from database
        all_news = await NewsService.get_all(db, limit=10000)  # Adjust limit as needed
        
        # Bulk index
        success_count, error_count = await elasticsearch_service.bulk_index_news(all_news)
        
        return {
            "message": "Index rebuilt successfully",
            "indexed": success_count,
            "errors": error_count,
            "total_documents": success_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Index rebuild error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rebuild index"
        )


@router.get("/health")
async def search_health():
    """
    Check Elasticsearch health.
    
    Returns:
        Health status
    """
    try:
        health = await elasticsearch_service.health_check()
        return health
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {"status": "error", "message": str(e)}
