"""Category Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CategoryBase(BaseModel):
    """Base category schema."""
    name: str = Field(..., min_length=1, max_length=100)
    slug: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating category."""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating category."""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class CategoryInDB(CategoryBase):
    """Category schema in database."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class CategoryResponse(CategoryInDB):
    """Category response schema."""
    pass


class CategoryWithCount(CategoryResponse):
    """Category with news count."""
    news_count: int = 0
