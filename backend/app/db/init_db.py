"""Initialize database with initial data."""

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import get_password_hash
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.models.category import Category
from app.core.constants import UserRole, NewsCategory
from app.core.logging import get_logger
from slugify import slugify


logger = get_logger(__name__)


async def init_categories(db: AsyncSession) -> None:
    """Initialize default categories.
    
    Args:
        db: Database session
    """
    categories_data = [
        ("Technology", "Latest technology news and innovations"),
        ("Business", "Business news, markets, and economy"),
        ("Politics", "Political news and government updates"),
        ("Sports", "Sports news, scores, and highlights"),
        ("Entertainment", "Entertainment news, movies, and music"),
        ("Science", "Scientific discoveries and research"),
        ("Health", "Health news and medical updates"),
        ("World", "International news from around the globe"),
        ("Local", "Local news and community updates"),
    ]
    
    for name, description in categories_data:
        result = await db.execute(
            select(Category).where(Category.name == name)
        )
        category = result.scalar_one_or_none()
        
        if not category:
            category = Category(
                name=name,
                slug=slugify(name),
                description=description
            )
            db.add(category)
            logger.info(f"Created category: {name}")
    
    await db.commit()


async def init_superuser(db: AsyncSession) -> None:
    """Initialize superuser.
    
    Args:
        db: Database session
    """
    result = await db.execute(
        select(User).where(User.email == settings.FIRST_SUPERUSER_EMAIL)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            hashed_password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name="Admin User",
            is_superuser=True,
            is_active=True,
            role=UserRole.ADMIN,
        )
        db.add(user)
        await db.commit()
        logger.info(f"Created superuser: {settings.FIRST_SUPERUSER_EMAIL}")
    else:
        logger.info(f"Superuser already exists: {settings.FIRST_SUPERUSER_EMAIL}")


async def init_db() -> None:
    """Initialize database with initial data."""
    logger.info("Initializing database...")
    
    async with AsyncSessionLocal() as db:
        try:
            await init_categories(db)
            await init_superuser(db)
            logger.info("Database initialization completed successfully")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(init_db())
