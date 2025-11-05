"""Recommendation service for personalized news."""

from typing import List
from datetime import datetime, timedelta
from sqlalchemy import select, desc, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.news import News
from app.models.reading_history import ReadingHistory
from app.models.bookmark import Bookmark
from app.models.user_preference import UserPreference


class RecommendationService:
    """Service for generating personalized recommendations."""
    
    @staticmethod
    async def get_recommendations(
        db: AsyncSession,
        user_id: int,
        limit: int = 20
    ) -> List[News]:
        """Get personalized news recommendations.
        
        Args:
            db: Database session
            user_id: User ID
            limit: Number of recommendations
            
        Returns:
            List of recommended news
        """
        # Get user's reading history (last 30 days)
        since = datetime.utcnow() - timedelta(days=30)
        
        history_result = await db.execute(
            select(ReadingHistory.news_id)
            .where(
                and_(
                    ReadingHistory.user_id == user_id,
                    ReadingHistory.read_at >= since
                )
            )
        )
        read_news_ids = [row[0] for row in history_result.all()]
        
        # Get user's bookmarked news
        bookmark_result = await db.execute(
            select(Bookmark.news_id)
            .where(Bookmark.user_id == user_id)
        )
        bookmarked_ids = [row[0] for row in bookmark_result.all()]
        
        # Combine all read/bookmarked news IDs
        excluded_ids = list(set(read_news_ids + bookmarked_ids))
        
        # Get user's preferred categories (if any)
        pref_result = await db.execute(
            select(UserPreference.category_id, UserPreference.weight)
            .where(UserPreference.user_id == user_id)
            .order_by(desc(UserPreference.weight))
        )
        preferences = pref_result.all()
        
        if preferences:
            # Recommend from preferred categories
            preferred_categories = [pref[0] for pref in preferences[:3]]
            
            query = select(News).options(
                selectinload(News.source),
                selectinload(News.category),
                selectinload(News.tags)
            ).where(
                and_(
                    News.category_id.in_(preferred_categories),
                    ~News.id.in_(excluded_ids) if excluded_ids else True
                )
            ).order_by(
                desc(News.published_at)
            ).limit(limit)
        else:
            # Fallback: recommend trending news
            query = select(News).options(
                selectinload(News.source),
                selectinload(News.category),
                selectinload(News.tags)
            ).where(
                ~News.id.in_(excluded_ids) if excluded_ids else True
            ).order_by(
                desc(News.views_count),
                desc(News.bookmarks_count),
                desc(News.published_at)
            ).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def update_user_preferences(
        db: AsyncSession,
        user_id: int
    ) -> None:
        """Update user preferences based on reading history.
        
        Args:
            db: Database session
            user_id: User ID
        """
        # Get reading history (last 30 days)
        since = datetime.utcnow() - timedelta(days=30)
        
        # Count reads per category
        result = await db.execute(
            select(
                News.category_id,
                func.count(ReadingHistory.id).label('read_count')
            )
            .join(News, News.id == ReadingHistory.news_id)
            .where(
                and_(
                    ReadingHistory.user_id == user_id,
                    ReadingHistory.read_at >= since,
                    News.category_id.isnot(None)
                )
            )
            .group_by(News.category_id)
        )
        
        category_counts = result.all()
        
        if not category_counts:
            return
        
        # Calculate total reads
        total_reads = sum(count for _, count in category_counts)
        
        # Update or create preferences
        for category_id, read_count in category_counts:
            # Calculate weight (0.0 to 1.0)
            weight = min(read_count / total_reads, 1.0)
            
            # Check if preference exists
            pref_result = await db.execute(
                select(UserPreference).where(
                    and_(
                        UserPreference.user_id == user_id,
                        UserPreference.category_id == category_id
                    )
                )
            )
            preference = pref_result.scalar_one_or_none()
            
            if preference:
                # Update existing
                preference.weight = weight
            else:
                # Create new
                preference = UserPreference(
                    user_id=user_id,
                    category_id=category_id,
                    weight=weight
                )
                db.add(preference)
        
        await db.commit()
    
    @staticmethod
    async def get_similar_news(
        db: AsyncSession,
        news_id: int,
        limit: int = 5
    ) -> List[News]:
        """Get similar news articles.
        
        Args:
            db: Database session
            news_id: News ID
            limit: Number of similar articles
            
        Returns:
            List of similar news
        """
        # Get the original news
        original = await db.get(News, news_id)
        
        if not original:
            return []
        
        # Find news with same category or tags
        query = select(News).options(
            selectinload(News.source),
            selectinload(News.category),
            selectinload(News.tags)
        ).where(
            and_(
                News.id != news_id,
                News.category_id == original.category_id
            )
        ).order_by(
            desc(News.published_at)
        ).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
