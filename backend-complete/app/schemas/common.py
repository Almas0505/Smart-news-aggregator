"""Common Pydantic schemas."""

from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field


T = TypeVar("T")


class PaginationParams(BaseModel):
    """Pagination parameters."""
    skip: int = Field(0, ge=0, description="Number of items to skip")
    limit: int = Field(20, ge=1, le=100, description="Number of items to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper."""
    items: List[T]
    total: int
    skip: int
    limit: int
    has_more: bool
    
    @classmethod
    def create(
        cls,
        items: List[T],
        total: int,
        skip: int,
        limit: int
    ) -> "PaginatedResponse[T]":
        """Create paginated response."""
        return cls(
            items=items,
            total=total,
            skip=skip,
            limit=limit,
            has_more=skip + len(items) < total
        )


class Message(BaseModel):
    """Simple message response."""
    message: str


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
