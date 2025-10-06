"""User Pydantic schemas."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.core.constants import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating user."""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """Schema for updating user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)


class UserInDB(UserBase):
    """User schema in database."""
    id: int
    role: UserRole
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class UserResponse(UserInDB):
    """User response schema."""
    pass


class UserProfile(UserBase):
    """User profile schema (without sensitive data)."""
    id: int
    role: UserRole
    created_at: datetime
    
    model_config = {"from_attributes": True}
