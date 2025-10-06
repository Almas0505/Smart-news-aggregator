"""
Seed database with initial data for Smart News Aggregator
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.models.category import Category
from app.models.source import Source
from app.models.user import User
from app.core.security import get_password_hash
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_categories(db: Session) -> None:
    """Create initial news categories"""
    categories = [
        {
            "name": "Technology",
            "slug": "technology",
            "description": "Latest tech news, gadgets, and innovations",
        },
        {
            "name": "Business",
            "slug": "business",
            "description": "Financial markets, stocks, and economic news",
        },
        {
            "name": "Sports",
            "slug": "sports",
            "description": "Live scores, updates, and sports news",
        },
        {
            "name": "Entertainment",
            "slug": "entertainment",
            "description": "Movies, TV shows, music, and celebrity news",
        },
        {
            "name": "Health",
            "slug": "health",
            "description": "Medical news, wellness, and healthcare",
        },
        {
            "name": "Science",
            "slug": "science",
            "description": "Research, discoveries, and scientific breakthroughs",
        },
        {
            "name": "Politics",
            "slug": "politics",
            "description": "Government, policy, and political news",
        },
        {
            "name": "World",
            "slug": "world",
            "description": "International news and global events",
        },
    ]

    for cat_data in categories:
        # Check if category exists
        existing = db.query(Category).filter(Category.slug == cat_data["slug"]).first()
        if not existing:
            category = Category(**cat_data)
            db.add(category)
            logger.info(f"✓ Created category: {cat_data['name']}")
        else:
            logger.info(f"  Category already exists: {cat_data['name']}")

    db.commit()


def create_sources(db: Session) -> None:
    """Create initial news sources"""
    sources = [
        {
            "name": "BBC News",
            "url": "https://feeds.bbci.co.uk/news/rss.xml",
            "type": "rss",
            "is_active": True,
            "scrape_interval": 1800,  # 30 minutes
        },
        {
            "name": "CNN",
            "url": "http://rss.cnn.com/rss/cnn_topstories.rss",
            "type": "rss",
            "is_active": True,
            "scrape_interval": 1800,
        },
        {
            "name": "TechCrunch",
            "url": "https://techcrunch.com/feed/",
            "type": "rss",
            "is_active": True,
            "scrape_interval": 3600,
        },
        {
            "name": "Reuters",
            "url": "https://www.reutersagency.com/feed/",
            "type": "rss",
            "is_active": True,
            "scrape_interval": 1800,
        },
        {
            "name": "The Verge",
            "url": "https://www.theverge.com/rss/index.xml",
            "type": "rss",
            "is_active": True,
            "scrape_interval": 3600,
        },
        {
            "name": "Engadget",
            "url": "https://www.engadget.com/rss.xml",
            "type": "rss",
            "is_active": True,
            "scrape_interval": 3600,
        },
        {
            "name": "ESPN",
            "url": "https://www.espn.com/espn/rss/news",
            "type": "rss",
            "is_active": True,
            "scrape_interval": 1800,
        },
        {
            "name": "News API",
            "url": "https://newsapi.org/v2/top-headlines",
            "type": "api",
            "is_active": True,
            "scrape_interval": 3600,
        },
    ]

    for source_data in sources:
        # Check if source exists
        existing = db.query(Source).filter(Source.name == source_data["name"]).first()
        if not existing:
            source = Source(**source_data)
            db.add(source)
            logger.info(f"✓ Created source: {source_data['name']}")
        else:
            logger.info(f"  Source already exists: {source_data['name']}")

    db.commit()


def create_admin_user(db: Session) -> None:
    """Create admin user"""
    email = "admin@smartnews.com"
    existing = db.query(User).filter(User.email == email).first()

    if not existing:
        admin = User(
            email=email,
            hashed_password=get_password_hash("Admin123!"),
            full_name="Admin User",
            is_active=True,
            is_superuser=True,
        )
        db.add(admin)
        db.commit()
        logger.info(f"✓ Created admin user: {email}")
        logger.info(f"  Password: Admin123!")
    else:
        logger.info(f"  Admin user already exists: {email}")


def create_demo_user(db: Session) -> None:
    """Create demo user"""
    email = "demo@smartnews.com"
    existing = db.query(User).filter(User.email == email).first()

    if not existing:
        demo = User(
            email=email,
            hashed_password=get_password_hash("Demo123!"),
            full_name="Demo User",
            is_active=True,
            is_superuser=False,
        )
        db.add(demo)
        db.commit()
        logger.info(f"✓ Created demo user: {email}")
        logger.info(f"  Password: Demo123!")
    else:
        logger.info(f"  Demo user already exists: {email}")


def main():
    """Main seeding function"""
    logger.info("=" * 60)
    logger.info("Starting database seeding...")
    logger.info("=" * 60)

    db = SessionLocal()

    try:
        logger.info("\n1. Creating categories...")
        create_categories(db)

        logger.info("\n2. Creating news sources...")
        create_sources(db)

        logger.info("\n3. Creating admin user...")
        create_admin_user(db)

        logger.info("\n4. Creating demo user...")
        create_demo_user(db)

        logger.info("\n" + "=" * 60)
        logger.info("✓ Database seeding completed successfully!")
        logger.info("=" * 60)
        logger.info("\nDefault Users Created:")
        logger.info("  Admin: admin@smartnews.com / Admin123!")
        logger.info("  Demo:  demo@smartnews.com / Demo123!")
        logger.info("\n")

    except Exception as e:
        logger.error(f"Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
