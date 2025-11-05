"""Category endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_superuser
from app.models.user import User
from app.schemas.category import (
    CategoryCreate,
    CategoryUpdate,
    CategoryResponse,
    CategoryWithCount
)
from app.schemas.news import NewsBrief
from app.schemas.common import PaginatedResponse, Message
from app.services.category_service import CategoryService
from app.services.news_service import NewsService
from app.schemas.news import NewsFilter


router = APIRouter()


@router.get("", response_model=PaginatedResponse[CategoryResponse])
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get list of categories.
    
    Args:
        skip: Number of items to skip
        limit: Number of items to return
        db: Database session
        
    Returns:
        Paginated category list
    """
    categories, total = await CategoryService.get_list(db, skip, limit)
    
    return PaginatedResponse.create(
        items=categories,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get single category.
    
    Args:
        category_id: Category ID
        db: Database session
        
    Returns:
        Category
        
    Raises:
        HTTPException: If category not found
    """
    category = await CategoryService.get_by_id(db, category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.get("/{category_id}/news", response_model=PaginatedResponse[NewsBrief])
async def get_category_news(
    category_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get news for category.
    
    Args:
        category_id: Category ID
        skip: Number of items to skip
        limit: Number of items to return
        db: Database session
        
    Returns:
        Paginated news list
        
    Raises:
        HTTPException: If category not found
    """
    # Check if category exists
    category = await CategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Get news
    filters = NewsFilter(category_id=category_id)
    news_list, total = await NewsService.get_list(db, skip, limit, filters)
    
    return PaginatedResponse.create(
        items=news_list,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_in: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Create new category (admin only).
    
    Args:
        category_in: Category creation data
        db: Database session
        current_user: Current user (must be admin)
        
    Returns:
        Created category
        
    Raises:
        HTTPException: If category with slug already exists
    """
    # Check if slug exists
    existing = await CategoryService.get_by_slug(db, category_in.slug)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Category with this slug already exists"
        )
    
    category = await CategoryService.create(db, category_in)
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_in: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Update category (admin only).
    
    Args:
        category_id: Category ID
        category_in: Update data
        db: Database session
        current_user: Current user (must be admin)
        
    Returns:
        Updated category
        
    Raises:
        HTTPException: If category not found
    """
    category = await CategoryService.get_by_id(db, category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category = await CategoryService.update(db, category, category_in)
    return category


@router.delete("/{category_id}", response_model=Message)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Delete category (admin only).
    
    Args:
        category_id: Category ID
        db: Database session
        current_user: Current user (must be admin)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If category not found
    """
    deleted = await CategoryService.delete(db, category_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return Message(message="Category deleted successfully")
