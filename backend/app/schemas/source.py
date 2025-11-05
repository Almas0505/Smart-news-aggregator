"""Source Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, HttpUrl

from app.core.constants import SourceType


class SourceBase(BaseModel):
    """Base source schema."""
    name: str = Field(..., min_length=1, max_length=255)
    url: str = Field(..., max_length=500)
    type: SourceType
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: bool = True
    scrape_interval: int = Field(3600, ge=60, description="Scrape interval in seconds")


class SourceCreate(SourceBase):
    """Schema for creating source."""
    pass


class SourceUpdate(BaseModel):
    """Schema for updating source."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    url: Optional[str] = Field(None, max_length=500)
    type: Optional[SourceType] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None
    scrape_interval: Optional[int] = Field(None, ge=60)


class SourceInDB(SourceBase):
    """Source schema in database."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class SourceResponse(SourceInDB):
    """Source response schema."""
    pass


class SourceWithCount(SourceResponse):
    """Source with news count."""
    news_count: int = 0
