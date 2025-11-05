"""Authentication Pydantic schemas."""

from typing import Optional
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    """Access token response."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Token payload."""
    sub: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    """Login request."""
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    """Registration request."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request."""
    refresh_token: str


class PasswordChangeRequest(BaseModel):
    """Password change request."""
    old_password: str
    new_password: str
