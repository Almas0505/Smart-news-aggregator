"""Category service for business logic."""

from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.news import News
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service for category operations."""
    
    @staticmethod
    async def get_by_id(db: AsyncSession, category_id: int) -> Optional[Category]:
        """Get category by ID.
        
        Args:
            db: Database session
            category_id: Category ID
            
        Returns:
            Category if found, None otherwise
        """
        result = await db.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_slug(db: AsyncSession, slug: str) -> Optional[Category]:
        """Get category by slug.
        
        Args:
            db: Database session
            slug: Category slug
            
        Returns:
            Category if found, None otherwise
        """
        result = await db.execute(
            select(Category).where(Category.slug == slug)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_list(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> tuple[List[Category], int]:
        """Get list of categories.
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            Tuple of (category list, total count)
        """
        # Count total
        count_result = await db.execute(
            select(func.count(Category.id))
        )
        total = count_result.scalar()
        
        # Get categories
        query = select(Category).offset(skip).limit(limit)
        result = await db.execute(query)
        categories = list(result.scalars().all())
        
        return categories, total
    
    @staticmethod
    async def create(db: AsyncSession, category_in: CategoryCreate) -> Category:
        """Create new category.
        
        Args:
            db: Database session
            category_in: Category creation data
            
        Returns:
            Created category
        """
        category = Category(**category_in.model_dump())
        
        db.add(category)
        await db.commit()
        await db.refresh(category)
        
        return category
    
    @staticmethod
    async def update(
        db: AsyncSession,
        category: Category,
        category_in: CategoryUpdate
    ) -> Category:
        """Update category.
        
        Args:
            db: Database session
            category: Category to update
            category_in: Update data
            
        Returns:
            Updated category
        """
        update_data = category_in.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(category, field, value)
        
        await db.commit()
        await db.refresh(category)
        
        return category
    
    @staticmethod
    async def delete(db: AsyncSession, category_id: int) -> bool:
        """Delete category.
        
        Args:
            db: Database session
            category_id: Category ID
            
        Returns:
            True if deleted, False otherwise
        """
        category = await CategoryService.get_by_id(db, category_id)
        
        if not category:
            return False
        
        await db.delete(category)
        await db.commit()
        
        return True
    
    @staticmethod
    async def get_news_count(db: AsyncSession, category_id: int) -> int:
        """Get news count for category.
        
        Args:
            db: Database session
            category_id: Category ID
            
        Returns:
            News count
        """
        result = await db.execute(
            select(func.count(News.id)).where(News.category_id == category_id)
        )
        return result.scalar() or 0
