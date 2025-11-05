"""
Search Schemas - Request/Response models for search operations
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    """Search filters."""
    
    category_ids: Optional[List[int]] = Field(None, description="Filter by category IDs")
    source_ids: Optional[List[int]] = Field(None, description="Filter by source IDs")
    sentiment: Optional[str] = Field(None, description="Filter by sentiment (positive/negative/neutral)")
    date_from: Optional[datetime] = Field(None, description="Filter articles from this date")
    date_to: Optional[datetime] = Field(None, description="Filter articles until this date")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")


class SearchQuery(BaseModel):
    """Search query request."""
    
    query: str = Field(..., min_length=1, max_length=500, description="Search query text")
    filters: Optional[SearchFilters] = Field(None, description="Additional filters")
    page: int = Field(1, ge=1, description="Page number")
    size: int = Field(20, ge=1, le=100, description="Results per page")
    sort_by: str = Field("_score", description="Sort field: _score, published_at, views_count")
    
    class Config:
        json_schema_extra = {
            "example": {
                "query": "artificial intelligence",
                "filters": {
                    "category_ids": [1, 2],
                    "sentiment": "positive",
                    "date_from": "2025-01-01T00:00:00Z"
                },
                "page": 1,
                "size": 20,
                "sort_by": "_score"
            }
        }


class AggregationBucket(BaseModel):
    """Aggregation bucket."""
    
    key: str = Field(..., description="Bucket key")
    count: int = Field(..., description="Document count")


class SearchResult(BaseModel):
    """Single search result."""
    
    id: int
    title: str
    summary: Optional[str] = None
    url: str
    image_url: Optional[str] = None
    source_name: Optional[str] = None
    category_name: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_score: Optional[float] = None
    tags: List[str] = []
    published_at: Optional[datetime] = None
    views_count: int = 0
    score: Optional[float] = Field(None, alias="_score", description="Search relevance score")


class SearchResponse(BaseModel):
    """Search response with results and aggregations."""
    
    results: List[Dict[str, Any]] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
    page: int = Field(..., description="Current page")
    size: int = Field(..., description="Results per page")
    pages: int = Field(0, description="Total pages")
    query: str = Field(..., description="Original query")
    aggregations: Dict[str, List[Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Aggregations/facets"
    )
    took_ms: Optional[int] = Field(None, description="Query execution time in ms")
    
    def __init__(self, **data):
        """Calculate total pages."""
        super().__init__(**data)
        if self.total > 0 and self.size > 0:
            self.pages = (self.total + self.size - 1) // self.size
    
    class Config:
        json_schema_extra = {
            "example": {
                "results": [
                    {
                        "id": 1,
                        "title": "AI Breakthrough",
                        "summary": "New AI model achieves...",
                        "url": "https://example.com/article",
                        "category_name": "Technology",
                        "sentiment": "positive",
                        "_score": 12.5
                    }
                ],
                "total": 150,
                "page": 1,
                "size": 20,
                "pages": 8,
                "query": "artificial intelligence",
                "aggregations": {
                    "categories": [
                        {"key": "Technology", "count": 50},
                        {"key": "Science", "count": 30}
                    ],
                    "sentiments": [
                        {"key": "positive", "count": 80},
                        {"key": "neutral", "count": 50}
                    ]
                }
            }
        }


class SemanticSearchRequest(BaseModel):
    """Semantic search request."""
    
    query: str = Field(..., min_length=1, description="Query text for semantic search")
    filters: Optional[SearchFilters] = None
    size: int = Field(20, ge=1, le=100)
    min_score: float = Field(0.5, ge=0.0, le=1.0, description="Minimum similarity score")


class SemanticSearchResponse(BaseModel):
    """Semantic search response."""
    
    results: List[SearchResult]
    total: int
    query: str


class SuggestRequest(BaseModel):
    """Search suggestions request."""
    
    text: str = Field(..., min_length=1, max_length=100)
    size: int = Field(5, ge=1, le=20)


class SuggestResponse(BaseModel):
    """Search suggestions response."""
    
    suggestions: List[str]
    text: str


class IndexStatsResponse(BaseModel):
    """Elasticsearch index statistics."""
    
    total_documents: int
    index_size_bytes: int
    index_size_mb: float


class HealthCheckResponse(BaseModel):
    """Elasticsearch health check."""
    
    status: str
    cluster_name: Optional[str] = None
    number_of_nodes: Optional[int] = None
    message: Optional[str] = None
