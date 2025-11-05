"""Source service for business logic."""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.source import Source
from app.models.news import News
from app.schemas.source import SourceCreate, SourceUpdate


class SourceService:
    """Service for source operations."""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, source_id: int) -> Optional[Source]:
        """Get source by ID.
        
        Args:
            db: Database session
            source_id: Source ID
            
        Returns:
            Source if found, None otherwise
        """
        result = await db.execute(
            select(Source).where(Source.id == source_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_name(db: AsyncSession, name: str) -> Optional[Source]:
        """Get source by name.
        
        Args:
            db: Database session
            name: Source name
            
        Returns:
            Source if found, None otherwise
        """
        result = await db.execute(
            select(Source).where(Source.name == name)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        active_only: bool = False
    ) -> tuple[List[Source], int]:
        """Get list of sources.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Number of records to return
            active_only: Return only active sources
            
        Returns:
            Tuple of (source list, total count)
        """
        query = select(Source)
        
        if active_only:
            query = query.where(Source.is_active == True)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        count_result = await db.execute(count_query)
        total = count_result.scalar()
        
        # Get sources
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        sources = list(result.scalars().all())
        
        return sources, total
    
    @staticmethod
    async def create(db: AsyncSession, source_in: SourceCreate) -> Source:
        """Create new source.
        
        Args:
            db: Database session
            source_in: Source creation data
            
        Returns:
            Created source
        """
        source = Source(**source_in.model_dump())
        
        db.add(source)
        await db.commit()
        await db.refresh(source)
        
        return source
    
    @staticmethod
    async def update(
        db: AsyncSession,
        source: Source,
        source_in: SourceUpdate
    ) -> Source:
        """Update source.
        
        Args:
            db: Database session
            source: Source to update
            source_in: Update data
            
        Returns:
            Updated source
        """
        update_data = source_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(source, field, value)
        
        await db.commit()
        await db.refresh(source)
        
        return source
    
    @staticmethod
    async def delete(db: AsyncSession, source_id: int) -> bool:
        """Delete source.
        
        Args:
            db: Database session
            source_id: Source ID
            
        Returns:
            True if deleted, False otherwise
        """
        source = await SourceService.get_by_id(db, source_id)
        
        if not source:
            return False
        
        await db.delete(source)
        await db.commit()
        
        return True
    
    @staticmethod
    async def get_news_count(db: AsyncSession, source_id: int) -> int:
        """Get news count for source.
        
        Args:
            db: Database session
            source_id: Source ID
            
        Returns:
            News count
        """
        result = await db.execute(
            select(func.count(News.id)).where(News.source_id == source_id)
        )
        return result.scalar() or 0
    
    @staticmethod
    async def toggle_active(db: AsyncSession, source_id: int) -> Optional[Source]:
        """Toggle source active status.
        
        Args:
            db: Database session
            source_id: Source ID
            
        Returns:
            Updated source or None
        """
        source = await SourceService.get_by_id(db, source_id)
        
        if not source:
            return None
        
        source.is_active = not source.is_active
        await db.commit()
        await db.refresh(source)
        
        return source
