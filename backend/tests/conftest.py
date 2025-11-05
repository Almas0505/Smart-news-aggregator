"""Test configuration and fixtures."""

import pytest
import asyncio
from typing import AsyncGenerator, Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from datetime import datetime

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.models.user import User
from app.models.source import Source
from app.models.category import Category
from app.models.news import News
from app.core.security import get_password_hash, create_access_token
from app.core.constants import UserRole


# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Create async engine for tests
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    # Create tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # Create session
    async with TestSessionLocal() as session:
        yield session
    
    # Drop tables after test
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test client."""
    
    # Override get_db dependency
    async def override_get_db():
        yield db
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
async def sample_user(db: AsyncSession) -> User:
    """Create sample user."""
    user = User(
        email="user@test.com",
        hashed_password=get_password_hash("TestPassword123!"),
        full_name="Test User",
        role=UserRole.USER,
        is_active=True,
        is_superuser=False
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def sample_admin(db: AsyncSession) -> User:
    """Create sample admin user."""
    admin = User(
        email="admin@test.com",
        hashed_password=get_password_hash("AdminPassword123!"),
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True,
        is_superuser=True
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)
    return admin


@pytest.fixture
def user_token(sample_user: User) -> str:
    """Create user access token."""
    return create_access_token(subject=str(sample_user.id))


@pytest.fixture
def admin_token(sample_admin: User) -> str:
    """Create admin access token."""
    return create_access_token(subject=str(sample_admin.id))


@pytest.fixture
async def sample_source(db: AsyncSession) -> Source:
    """Create sample news source."""
    source = Source(
        name="Test News Source",
        url="https://testnews.com",
        type="rss",
        language="en",
        country="US",
        is_active=True
    )
    db.add(source)
    await db.commit()
    await db.refresh(source)
    return source


@pytest.fixture
async def sample_category(db: AsyncSession) -> Category:
    """Create sample category."""
    category = Category(
        name="Technology",
        slug="technology",
        description="Tech news"
    )
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@pytest.fixture
async def sample_news(
    db: AsyncSession,
    sample_source: Source,
    sample_category: Category
) -> News:
    """Create sample news article."""
    news = News(
        title="Test News Article",
        content="This is test content",
        url="https://testnews.com/article-1",
        source_id=sample_source.id,
        category_id=sample_category.id,
        published_at=datetime.utcnow(),
        scraped_at=datetime.utcnow(),
        views_count=0,
        bookmarks_count=0
    )
    db.add(news)
    await db.commit()
    await db.refresh(news)
    return news
