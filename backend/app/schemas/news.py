"""News Pydantic schemas."""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from app.core.constants import SentimentType
from app.schemas.category import CategoryResponse
from app.schemas.source import SourceResponse


class TagBase(BaseModel):
    """Base tag schema."""
    name: str


class TagResponse(TagBase):
    """Tag response schema."""
    id: int
    
    model_config = {"from_attributes": True}


class EntityBase(BaseModel):
    """Base entity schema."""
    entity_type: str
    entity_text: str
    confidence: Optional[float] = None


class EntityResponse(EntityBase):
    """Entity response schema."""
    id: int
    
    model_config = {"from_attributes": True}


class NewsBase(BaseModel):
    """Base news schema."""
    title: str = Field(..., min_length=1, max_length=500)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = None
    url: str = Field(..., max_length=1000)
    image_url: Optional[str] = Field(None, max_length=1000)
    published_at: datetime


class NewsCreate(NewsBase):
    """Schema for creating news."""
    source_id: int
    category_id: Optional[int] = None
    sentiment: Optional[SentimentType] = None
    sentiment_score: Optional[float] = None


class NewsUpdate(BaseModel):
    """Schema for updating news."""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = None
    image_url: Optional[str] = Field(None, max_length=1000)
    category_id: Optional[int] = None
    sentiment: Optional[SentimentType] = None
    sentiment_score: Optional[float] = None


class NewsInDB(NewsBase):
    """News schema in database."""
    id: int
    source_id: int
    category_id: Optional[int]
    sentiment: Optional[SentimentType]
    sentiment_score: Optional[float]
    views_count: int
    bookmarks_count: int
    scraped_at: datetime
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class NewsResponse(NewsInDB):
    """News response schema with relations."""
    source: SourceResponse
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    entities: List[EntityResponse] = []
    
    model_config = {"from_attributes": True}


class NewsBrief(BaseModel):
    """Brief news schema for list views."""
    id: int
    title: str
    summary: Optional[str]
    url: str
    image_url: Optional[str]
    published_at: datetime
    source: SourceResponse
    category: Optional[CategoryResponse]
    tags: List[TagResponse] = []
    views_count: int
    bookmarks_count: int
    
    model_config = {"from_attributes": True}


class NewsFilter(BaseModel):
    """News filter parameters."""
    category_id: Optional[int] = None
    source_id: Optional[int] = None
    sentiment: Optional[SentimentType] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    search_query: Optional[str] = None


class NewsSearchRequest(BaseModel):
    """News search request."""
    query: str = Field(..., min_length=1)
    category_id: Optional[int] = None
    source_id: Optional[int] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
