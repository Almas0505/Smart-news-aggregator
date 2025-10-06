"""News service for business logic."""

from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, desc, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models.news import News
from app.models.tag import Tag, news_tags
from app.models.entity import Entity
from app.schemas.news import NewsCreate, NewsUpdate, NewsFilter
from app.core.constants import HTTP_404_NOT_FOUND


class NewsService:
    """Service for news operations."""
    
    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        news_id: int,
        load_relations: bool = True
    ) -> Optional[News]:
        """Get news by ID.
        
        Args:
            db: Database session
            news_id: News ID
            load_relations: Load related data (source, category, tags)
            
        Returns:
            News if found, None otherwise
        """
        query = select(News).where(News.id == news_id)
        
        if load_relations:
            query = query.options(
                selectinload(News.source),
                selectinload(News.category),
                selectinload(News.tags),
                selectinload(News.entities)
            )
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        filters: Optional[NewsFilter] = None
    ) -> tuple[List[News], int]:
        """Get list of news with filters.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Number of records to return
            filters: Filter parameters
            
        Returns:
            Tuple of (news list, total count)
        """
        query = select(News).options(
            selectinload(News.source),
            selectinload(News.category),
            selectinload(News.tags)
        )
        
        # Apply filters
        if filters:
            if filters.category_id:
                query = query.where(News.category_id == filters.category_id)
            
            if filters.source_id:
                query = query.where(News.source_id == filters.source_id)
            
            if filters.sentiment:
                query = query.where(News.sentiment == filters.sentiment)
            
            if filters.date_from:
                query = query.where(News.published_at >= filters.date_from)
            
            if filters.date_to:
                query = query.where(News.published_at <= filters.date_to)
            
            if filters.search_query:
                search_pattern = f"%{filters.search_query}%"
                query = query.where(
                    or_(
                        News.title.ilike(search_pattern),
                        News.content.ilike(search_pattern)
                    )
                )
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Get paginated results
        query = query.order_by(desc(News.published_at))
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        news_list = result.scalars().all()
        
        return list(news_list), total
    
    @staticmethod
    async def create(
        db: AsyncSession,
        news_in: NewsCreate,
        tags: Optional[List[str]] = None
    ) -> News:
        """Create new news article.
        
        Args:
            db: Database session
            news_in: News creation data
            tags: List of tag names
            
        Returns:
            Created news
        """
        # Create news
        news_data = news_in.model_dump(exclude={'tags'})
        news = News(
            **news_data,
            scraped_at=datetime.utcnow()
        )
        
        # Add tags
        if tags:
            for tag_name in tags:
                # Get or create tag
                result = await db.execute(
                    select(Tag).where(Tag.name == tag_name)
                )
                tag = result.scalar_one_or_none()
                
                if not tag:
                    tag = Tag(name=tag_name)
                    db.add(tag)
                
                news.tags.append(tag)
        
        db.add(news)
        await db.commit()
        await db.refresh(news)
        
        # Load relations
        await db.refresh(news, ['source', 'category', 'tags'])
        
        return news
    
    @staticmethod
    async def update(
        db: AsyncSession,
        news: News,
        news_in: NewsUpdate
    ) -> News:
        """Update news article.
        
        Args:
            db: Database session
            news: News to update
            news_in: Update data
            
        Returns:
            Updated news
        """
        update_data = news_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(news, field, value)
        
        await db.commit()
        await db.refresh(news)
        
        return news
    
    @staticmethod
    async def delete(db: AsyncSession, news_id: int) -> bool:
        """Delete news article.
        
        Args:
            db: Database session
            news_id: News ID
            
        Returns:
            True if deleted, False otherwise
        """
        news = await NewsService.get_by_id(db, news_id, load_relations=False)
        
        if not news:
            return False
        
        await db.delete(news)
        await db.commit()
        
        return True
    
    @staticmethod
    async def increment_views(db: AsyncSession, news_id: int) -> None:
        """Increment news views count.
        
        Args:
            db: Database session
            news_id: News ID
        """
        news = await NewsService.get_by_id(db, news_id, load_relations=False)
        
        if news:
            news.views_count += 1
            await db.commit()
    
    @staticmethod
    async def get_trending(
        db: AsyncSession,
        limit: int = 10,
        hours: int = 24
    ) -> List[News]:
        """Get trending news.
        
        Args:
            db: Database session
            limit: Number of news to return
            hours: Time window in hours
            
        Returns:
            List of trending news
        """
        since = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        query = select(News).options(
            selectinload(News.source),
            selectinload(News.category),
            selectinload(News.tags)
        ).where(
            News.published_at >= since
        ).order_by(
            desc(News.views_count),
            desc(News.bookmarks_count)
        ).limit(limit)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def add_entities(
        db: AsyncSession,
        news_id: int,
        entities_data: List[dict]
    ) -> None:
        """Add entities to news article.
        
        Args:
            db: Database session
            news_id: News ID
            entities_data: List of entity data dicts
        """
        for entity_data in entities_data:
            entity = Entity(
                news_id=news_id,
                **entity_data
            )
            db.add(entity)
        
        await db.commit()
    
    @staticmethod
    async def get_by_url(db: AsyncSession, url: str) -> Optional[News]:
        """Get news by URL (for deduplication).
        
        Args:
            db: Database session
            url: News URL
            
        Returns:
            News if found, None otherwise
        """
        result = await db.execute(
            select(News).where(News.url == url)
        )
        return result.scalar_one_or_none()
