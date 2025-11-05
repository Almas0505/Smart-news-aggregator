"""Bookmark service for business logic."""

from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.bookmark import Bookmark
from app.models.news import News


class BookmarkService:
    """Service for bookmark operations."""
    
    @staticmethod
    async def get_user_bookmarks(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> tuple[List[News], int]:
        """Get user bookmarks.
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            Tuple of (news list, total count)
        """
        # Get bookmarked news IDs
        bookmark_query = select(Bookmark.news_id).where(
            Bookmark.user_id == user_id
        )
        result = await db.execute(bookmark_query)
        news_ids = [row[0] for row in result.all()]
        
        if not news_ids:
            return [], 0
        
        # Get news
        query = select(News).where(News.id.in_(news_ids)).options(
            selectinload(News.source),
            selectinload(News.category),
            selectinload(News.tags)
        )
        
        # Count total
        from sqlalchemy import func
        count_result = await db.execute(
            select(func.count()).select_from(query.subquery())
        )
        total = count_result.scalar()
        
        # Get paginated
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        news_list = list(result.scalars().all())
        
        return news_list, total
    
    @staticmethod
    async def is_bookmarked(
        db: AsyncSession,
        user_id: int,
        news_id: int
    ) -> bool:
        """Check if news is bookmarked by user.
        
        Args:
            db: Database session
            user_id: User ID
            news_id: News ID
            
        Returns:
            True if bookmarked, False otherwise
        """
        result = await db.execute(
            select(Bookmark).where(
                and_(
                    Bookmark.user_id == user_id,
                    Bookmark.news_id == news_id
                )
            )
        )
        return result.scalar_one_or_none() is not None
    
    @staticmethod
    async def add_bookmark(
        db: AsyncSession,
        user_id: int,
        news_id: int
    ) -> Optional[Bookmark]:
        """Add bookmark.
        
        Args:
            db: Database session
            user_id: User ID
            news_id: News ID
            
        Returns:
            Created bookmark or None if already exists
        """
        # Check if already bookmarked
        existing = await BookmarkService.is_bookmarked(db, user_id, news_id)
        if existing:
            return None
        
        # Create bookmark
        bookmark = Bookmark(
            user_id=user_id,
            news_id=news_id
        )
        
        db.add(bookmark)
        
        # Update news bookmarks count
        news = await db.get(News, news_id)
        if news:
            news.bookmarks_count += 1
        
        await db.commit()
        await db.refresh(bookmark)
        
        return bookmark
    
    @staticmethod
    async def remove_bookmark(
        db: AsyncSession,
        user_id: int,
        news_id: int
    ) -> bool:
        """Remove bookmark.
        
        Args:
            db: Database session
            user_id: User ID
            news_id: News ID
            
        Returns:
            True if removed, False otherwise
        """
        result = await db.execute(
            select(Bookmark).where(
                and_(
                    Bookmark.user_id == user_id,
                    Bookmark.news_id == news_id
                )
            )
        )
        bookmark = result.scalar_one_or_none()
        
        if not bookmark:
            return False
        
        await db.delete(bookmark)
        
        # Update news bookmarks count
        news = await db.get(News, news_id)
        if news and news.bookmarks_count > 0:
            news.bookmarks_count -= 1
        
        await db.commit()
        
        return True
