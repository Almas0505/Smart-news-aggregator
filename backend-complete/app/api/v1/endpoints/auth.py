"""Authentication endpoints."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import (
    Token,
    LoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
)
from app.schemas.user import UserResponse
from app.services.user_service import UserService
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.core.config import settings
from app.core.constants import INVALID_CREDENTIALS, INACTIVE_USER
from app.schemas.user import UserCreate


router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register new user.
    
    Args:
        user_data: Registration data
        db: Database session
        
    Returns:
        Created user
    """
    user_create = UserCreate(
        email=user_data.email,
        password=user_data.password,
        full_name=user_data.full_name,
    )
    
    user = await UserService.create(db, user_create)
    return user


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user.
    
    Args:
        login_data: Login credentials
        db: Database session
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If credentials invalid or user inactive
    """
    user = await UserService.authenticate(
        db,
        login_data.email,
        login_data.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=INVALID_CREDENTIALS,
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=INACTIVE_USER,
        )
    
    # Create tokens
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token.
    
    Args:
        refresh_data: Refresh token data
        db: Database session
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException: If refresh token invalid or user not found
    """
    user_id = verify_token(refresh_data.refresh_token, token_type="refresh")
    
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    
    user = await UserService.get_by_id(db, int(user_id))
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive",
        )
    
    # Create new tokens
    access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))
    
    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer"
    )
