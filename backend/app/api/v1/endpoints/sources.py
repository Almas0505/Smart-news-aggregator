"""Source endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.deps import get_current_superuser
from app.models.user import User
from app.schemas.source import (
    SourceCreate,
    SourceUpdate,
    SourceResponse,
    SourceWithCount
)
from app.schemas.common import PaginatedResponse, Message
from app.services.source_service import SourceService
from app.services.news_service import NewsService
from app.schemas.news import NewsFilter, NewsBrief


router = APIRouter()


@router.get("", response_model=PaginatedResponse[SourceResponse])
async def get_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    active_only: bool = Query(False, description="Show only active sources"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of sources.
    
    Args:
        skip: Number of items to skip
        limit: Number of items to return
        active_only: Filter only active sources
        db: Database session
        
    Returns:
        Paginated source list
    """
    sources, total = await SourceService.get_list(db, skip, limit, active_only)
    
    return PaginatedResponse.create(
        items=sources,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get single source.
    
    Args:
        source_id: Source ID
        db: Database session
        
    Returns:
        Source
        
    Raises:
        HTTPException: If source not found
    """
    source = await SourceService.get_by_id(db, source_id)
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    return source


@router.get("/{source_id}/news", response_model=PaginatedResponse[NewsBrief])
async def get_source_news(
    source_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get news from source.
    
    Args:
        source_id: Source ID
        skip: Number of items to skip
        limit: Number of items to return
        db: Database session
        
    Returns:
        Paginated news list
        
    Raises:
        HTTPException: If source not found
    """
    # Check if source exists
    source = await SourceService.get_by_id(db, source_id)
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    # Get news
    filters = NewsFilter(source_id=source_id)
    news_list, total = await NewsService.get_list(db, skip, limit, filters)
    
    return PaginatedResponse.create(
        items=news_list,
        total=total,
        skip=skip,
        limit=limit
    )


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    source_in: SourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Create new source (admin only).
    
    Args:
        source_in: Source creation data
        db: Database session
        current_user: Current user (must be admin)
        
    Returns:
        Created source
        
    Raises:
        HTTPException: If source with name already exists
    """
    # Check if name exists
    existing = await SourceService.get_by_name(db, source_in.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Source with this name already exists"
        )
    
    source = await SourceService.create(db, source_in)
    return source


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    source_in: SourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Update source (admin only).
    
    Args:
        source_id: Source ID
        source_in: Update data
        db: Database session
        current_user: Current user (must be admin)
        
    Returns:
        Updated source
        
    Raises:
        HTTPException: If source not found
    """
    source = await SourceService.get_by_id(db, source_id)
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    source = await SourceService.update(db, source, source_in)
    return source


@router.delete("/{source_id}", response_model=Message)
async def delete_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Delete source (admin only).
    
    Args:
        source_id: Source ID
        db: Database session
        current_user: Current user (must be admin)
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If source not found
    """
    deleted = await SourceService.delete(db, source_id)
    
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    return Message(message="Source deleted successfully")


@router.post("/{source_id}/toggle", response_model=SourceResponse)
async def toggle_source_active(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_superuser)
):
    """Toggle source active status (admin only).
    
    Args:
        source_id: Source ID
        db: Database session
        current_user: Current user (must be admin)
        
    Returns:
        Updated source
        
    Raises:
        HTTPException: If source not found
    """
    source = await SourceService.toggle_active(db, source_id)
    
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source not found"
        )
    
    return source
