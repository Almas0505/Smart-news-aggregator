"""User Pydantic schemas."""

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.core.constants import UserRole


class UserBase(BaseModel):
    """Base user schema."""
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Schema for creating user."""
    password: str = Field(..., min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password strength.
        
        Password must contain:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        # Check for common passwords
        common_passwords = ['password', '12345678', 'qwerty', 'admin', 'letmein']
        if v.lower() in common_passwords:
            raise ValueError('Password is too common. Please choose a stronger password')
        
        return v


class UserUpdate(BaseModel):
    """Schema for updating user."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    
    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if provided."""
        if v is None:
            return v
        
        # Reuse validation from UserCreate
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        
        return v


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
