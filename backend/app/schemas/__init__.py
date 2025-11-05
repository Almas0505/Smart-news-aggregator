"""Pydantic schemas."""

from app.schemas.common import (
    PaginationParams,
    PaginatedResponse,
    Message,
    ErrorResponse,
)
from app.schemas.user import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserProfile,
)
from app.schemas.auth import (
    Token,
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    PasswordChangeRequest,
)
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithCount,
)
from app.schemas.source import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceWithCount,
)
from app.schemas.news import (
    NewsCreate,
    NewsUpdate,
    NewsResponse,
    NewsBrief,
    NewsFilter,
    NewsSearchRequest,
    TagResponse,
    EntityResponse,
)

__all__ = [
    "PaginationParams",
    "PaginatedResponse",
    "Message",
    "ErrorResponse",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserProfile",
    "Token",
    "LoginRequest",
    "RegisterRequest",
    "RefreshTokenRequest",
    "PasswordChangeRequest",
    "CategoryCreate",
    "CategoryUpdate",
    "CategoryResponse",
    "CategoryWithCount",
    "SourceCreate",
    "SourceUpdate",
    "SourceResponse",
    "SourceWithCount",
    "NewsCreate",
    "NewsUpdate",
    "NewsResponse",
    "NewsBrief",
    "NewsFilter",
    "NewsSearchRequest",
    "TagResponse",
    "EntityResponse",
]
