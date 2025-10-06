"""User endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user, get_current_superuser
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdate
from app.schemas.common import Message
from app.services.user_service import UserService
from app.api.v1.endpoints.bookmarks import router as bookmarks_router


router = APIRouter()

# Include bookmarks router
router.include_router(bookmarks_router, prefix="/me", tags=["bookmarks"])


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Current user data
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user.
    
    Args:
        user_update: Update data
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Updated user data
    """
    user = await UserService.update(db, current_user, user_update)
    return user


@router.delete("/me", response_model=Message)
async def delete_current_user(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete current user account.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    await UserService.delete(db, current_user.id)
    return Message(message="Account deleted successfully")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _: User = Depends(get_current_superuser)
):
    """Get user by ID (admin only).
    
    Args:
        user_id: User ID
        db: Database session
        
    Returns:
        User data
        
    Raises:
        HTTPException: If user not found
    """
    user = await UserService.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user
