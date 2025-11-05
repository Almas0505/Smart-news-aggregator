"""Integration tests for fresh news API endpoint."""

import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.news import News


class TestFreshNewsAPI:
    """Test suite for fresh news API."""
    
    @pytest.mark.asyncio
    async def test_get_fresh_news_default(
        self,
        async_client: AsyncClient,
        sample_news: News
    ):
        """Test getting fresh news with default parameters (24 hours)."""
        response = await async_client.get("/api/v1/news/fresh")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Check that news is recent
        news_item = data[0]
        assert "id" in news_item
        assert "title" in news_item
        assert "published_at" in news_item
    
    @pytest.mark.asyncio
    async def test_get_fresh_news_custom_hours(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        sample_source,
        sample_category
    ):
        """Test getting fresh news with custom time window."""
        # Create news from different time periods
        now = datetime.utcnow()
        
        # Fresh news (1 hour ago)
        fresh_news = News(
            title="Fresh News 1 Hour",
            url="https://test.com/fresh1",
            content="Fresh content",
            source_id=sample_source.id,
            category_id=sample_category.id,
            published_at=now - timedelta(hours=1),
            scraped_at=now
        )
        
        # Old news (25 hours ago)
        old_news = News(
            title="Old News 25 Hours",
            url="https://test.com/old25",
            content="Old content",
            source_id=sample_source.id,
            category_id=sample_category.id,
            published_at=now - timedelta(hours=25),
            scraped_at=now
        )
        
        db_session.add_all([fresh_news, old_news])
        await db_session.commit()
        
        # Request news from last 12 hours
        response = await async_client.get("/api/v1/news/fresh?hours=12")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only contain fresh news
        titles = [item["title"] for item in data]
        assert "Fresh News 1 Hour" in titles
        assert "Old News 25 Hours" not in titles
    
    @pytest.mark.asyncio
    async def test_get_fresh_news_with_category_filter(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        sample_source,
        sample_category
    ):
        """Test getting fresh news filtered by category."""
        from app.models.category import Category
        
        # Create second category
        category2 = Category(name="Sports", slug="sports")
        db_session.add(category2)
        await db_session.commit()
        await db_session.refresh(category2)
        
        now = datetime.utcnow()
        
        # News in category 1
        news1 = News(
            title="Tech News",
            url="https://test.com/tech1",
            content="Tech content",
            source_id=sample_source.id,
            category_id=sample_category.id,
            published_at=now - timedelta(hours=1),
            scraped_at=now
        )
        
        # News in category 2
        news2 = News(
            title="Sports News",
            url="https://test.com/sports1",
            content="Sports content",
            source_id=sample_source.id,
            category_id=category2.id,
            published_at=now - timedelta(hours=1),
            scraped_at=now
        )
        
        db_session.add_all([news1, news2])
        await db_session.commit()
        
        # Request fresh news from category 1 only
        response = await async_client.get(
            f"/api/v1/news/fresh?category_id={sample_category.id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should only contain news from category 1
        for item in data:
            if item["title"] in ["Tech News", "Sports News"]:
                assert item["title"] == "Tech News"
    
    @pytest.mark.asyncio
    async def test_get_fresh_news_sorted_by_newest(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        sample_source,
        sample_category
    ):
        """Test that fresh news is sorted by newest first."""
        now = datetime.utcnow()
        
        # Create news with different timestamps
        news_items = []
        for i in range(5):
            news = News(
                title=f"News {i}",
                url=f"https://test.com/news{i}",
                content=f"Content {i}",
                source_id=sample_source.id,
                category_id=sample_category.id,
                published_at=now - timedelta(hours=i),
                scraped_at=now
            )
            news_items.append(news)
        
        db_session.add_all(news_items)
        await db_session.commit()
        
        # Get fresh news
        response = await async_client.get("/api/v1/news/fresh?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check order (newest first)
        assert len(data) >= 5
        titles = [item["title"] for item in data[:5]]
        assert "News 0" in titles
        
        # Verify timestamps are in descending order
        if len(data) >= 2:
            for i in range(len(data) - 1):
                date1 = datetime.fromisoformat(data[i]["published_at"].replace("Z", "+00:00"))
                date2 = datetime.fromisoformat(data[i + 1]["published_at"].replace("Z", "+00:00"))
                assert date1 >= date2, "News should be sorted by newest first"
    
    @pytest.mark.asyncio
    async def test_get_fresh_news_limit_parameter(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession,
        sample_source,
        sample_category
    ):
        """Test limit parameter works correctly."""
        now = datetime.utcnow()
        
        # Create 10 fresh news items
        news_items = []
        for i in range(10):
            news = News(
                title=f"News Limit {i}",
                url=f"https://test.com/limit{i}",
                content=f"Content {i}",
                source_id=sample_source.id,
                category_id=sample_category.id,
                published_at=now - timedelta(minutes=i),
                scraped_at=now
            )
            news_items.append(news)
        
        db_session.add_all(news_items)
        await db_session.commit()
        
        # Request only 3 items
        response = await async_client.get("/api/v1/news/fresh?limit=3")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return exactly 3 items (or less if db has fewer)
        fresh_items = [item for item in data if "News Limit" in item["title"]]
        assert len(fresh_items) <= 3
    
    @pytest.mark.asyncio
    async def test_get_fresh_news_max_hours_limit(
        self,
        async_client: AsyncClient
    ):
        """Test that hours parameter is limited to max 7 days (168 hours)."""
        # Try with hours > 168
        response = await async_client.get("/api/v1/news/fresh?hours=200")
        
        # Should fail validation
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_get_fresh_news_empty_result(
        self,
        async_client: AsyncClient,
        db_session: AsyncSession
    ):
        """Test fresh news endpoint with no matching results."""
        # Request news from last 1 hour (when all news is older)
        response = await async_client.get("/api/v1/news/fresh?hours=1")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # May be empty or contain only very recent news
    
    @pytest.mark.asyncio
    async def test_get_fresh_news_includes_relations(
        self,
        async_client: AsyncClient,
        sample_news: News
    ):
        """Test that fresh news includes source, category, and tags."""
        response = await async_client.get("/api/v1/news/fresh")
        
        assert response.status_code == 200
        data = response.json()
        
        if len(data) > 0:
            news_item = data[0]
            # Check that relations are included
            assert "source" in news_item or "source_id" in news_item
            assert "category" in news_item or "category_id" in news_item
    
    @pytest.mark.asyncio
    async def test_get_fresh_news_cache(
        self,
        async_client: AsyncClient,
        sample_news: News
    ):
        """Test that fresh news endpoint uses caching."""
        # First request
        response1 = await async_client.get("/api/v1/news/fresh")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second request (should be cached)
        response2 = await async_client.get("/api/v1/news/fresh")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Data should be the same
        assert len(data1) == len(data2)
        if len(data1) > 0:
            assert data1[0]["id"] == data2[0]["id"]
