"""Bookmark endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.news import NewsBrief
from app.schemas.common import PaginatedResponse, Message
from app.services.bookmark_service import BookmarkService
from app.services.news_service import NewsService


router = APIRouter()


@router.get("/bookmarks", response_model=PaginatedResponse[NewsBrief])
async def get_my_bookmarks(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's bookmarks.
    
    Args:
        skip: Number of items to skip
        limit: Number of items to return
        current_user: Current user
        db: Database session
        
    Returns:
        Paginated bookmarks
    """
    news_list, total = await BookmarkService.get_user_bookmarks(
        db,
        current_user.id,
        skip,
        limit
    )
    
    return PaginatedResponse.create(
        items=news_list,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("/bookmarks/{news_id}", response_model=Message)
async def add_bookmark(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add news to bookmarks.
    
    Args:
        news_id: News ID
        current_user: Current user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If news not found or already bookmarked
    """
    # Check if news exists
    news = await NewsService.get_by_id(db, news_id, load_relations=False)
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="News not found"
        )
    
    # Add bookmark
    bookmark = await BookmarkService.add_bookmark(db, current_user.id, news_id)
    
    if not bookmark:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="News already bookmarked"
        )
    
    return Message(message="Bookmark added successfully")


@router.delete("/bookmarks/{news_id}", response_model=Message)
async def remove_bookmark(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove news from bookmarks.
    
    Args:
        news_id: News ID
        current_user: Current user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If bookmark not found
    """
    removed = await BookmarkService.remove_bookmark(db, current_user.id, news_id)
    
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bookmark not found"
        )
    
    return Message(message="Bookmark removed successfully")


@router.get("/bookmarks/{news_id}/check")
async def check_bookmark(
    news_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if news is bookmarked.
    
    Args:
        news_id: News ID
        current_user: Current user
        db: Database session
        
    Returns:
        Bookmark status
    """
    is_bookmarked = await BookmarkService.is_bookmarked(
        db,
        current_user.id,
        news_id
    )
    
    return {"is_bookmarked": is_bookmarked}
