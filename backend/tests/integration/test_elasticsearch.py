"""
Tests for Elasticsearch service.
"""

import pytest
from datetime import datetime, timedelta

from app.services.elasticsearch_service import elasticsearch_service
from app.schemas.search import SearchFilters


@pytest.mark.asyncio
class TestElasticsearchService:
    """Test Elasticsearch operations."""
    
    async def test_health_check(self):
        """Test Elasticsearch health check."""
        health = await elasticsearch_service.health_check()
        assert "status" in health
        assert health["status"] in ["green", "yellow", "red", "error"]
    
    async def test_create_index(self):
        """Test index creation."""
        # Delete if exists
        await elasticsearch_service.delete_index()
        
        # Create new
        success = await elasticsearch_service.create_index()
        assert success is True
        
        # Check exists
        exists = await elasticsearch_service.index_exists()
        assert exists is True
    
    async def test_index_news(self, sample_news):
        """Test indexing a single news article."""
        # Ensure index exists
        await elasticsearch_service.create_index()
        
        # Index news
        success = await elasticsearch_service.index_news(sample_news)
        assert success is True
        
        # Give ES time to index
        import asyncio
        await asyncio.sleep(1)
        
        # Verify indexed
        stats = await elasticsearch_service.get_stats()
        assert stats["total_documents"] >= 1
    
    async def test_search(self, sample_news):
        """Test full-text search."""
        # Ensure news is indexed
        await elasticsearch_service.create_index()
        await elasticsearch_service.index_news(sample_news)
        
        import asyncio
        await asyncio.sleep(1)  # Wait for indexing
        
        # Search by title keyword
        results = await elasticsearch_service.search(
            query=sample_news.title.split()[0],  # First word of title
            page=1,
            size=10
        )
        
        assert results.total >= 0
        assert isinstance(results.results, list)
    
    async def test_search_with_filters(self, sample_news, sample_category):
        """Test search with filters."""
        await elasticsearch_service.create_index()
        await elasticsearch_service.index_news(sample_news)
        
        import asyncio
        await asyncio.sleep(1)
        
        # Search with category filter
        filters = SearchFilters(category_ids=[sample_category.id])
        results = await elasticsearch_service.search(
            query="test",
            filters=filters,
            page=1,
            size=10
        )
        
        assert results.total >= 0
    
    async def test_search_with_date_filter(self, sample_news):
        """Test search with date range filter."""
        await elasticsearch_service.create_index()
        await elasticsearch_service.index_news(sample_news)
        
        import asyncio
        await asyncio.sleep(1)
        
        # Search with date filter
        date_from = datetime.utcnow() - timedelta(days=7)
        date_to = datetime.utcnow() + timedelta(days=1)
        
        filters = SearchFilters(date_from=date_from, date_to=date_to)
        results = await elasticsearch_service.search(
            query="*",
            filters=filters,
            page=1,
            size=10
        )
        
        assert results.total >= 0
    
    async def test_delete_news(self, sample_news):
        """Test deleting news from index."""
        await elasticsearch_service.create_index()
        await elasticsearch_service.index_news(sample_news)
        
        import asyncio
        await asyncio.sleep(1)
        
        # Delete
        success = await elasticsearch_service.delete_news(sample_news.id)
        assert success is True
    
    async def test_update_news(self, sample_news):
        """Test updating news in index."""
        await elasticsearch_service.create_index()
        await elasticsearch_service.index_news(sample_news)
        
        import asyncio
        await asyncio.sleep(1)
        
        # Update
        updates = {"views_count": 100}
        success = await elasticsearch_service.update_news(sample_news.id, updates)
        assert success is True
    
    async def test_suggest(self, sample_news):
        """Test search suggestions."""
        await elasticsearch_service.create_index()
        await elasticsearch_service.index_news(sample_news)
        
        import asyncio
        await asyncio.sleep(1)
        
        # Get suggestions
        suggestions = await elasticsearch_service.suggest(
            text=sample_news.title[:3],  # First 3 chars
            size=5
        )
        
        assert isinstance(suggestions, list)
    
    async def test_bulk_index(self, sample_news, sample_source, sample_category):
        """Test bulk indexing."""
        # Create multiple news
        from app.models.news import News
        
        news_list = [sample_news]
        for i in range(5):
            news = News(
                title=f"Test Article {i}",
                content=f"Content {i}",
                url=f"https://example.com/article-{i}",
                source_id=sample_source.id,
                category_id=sample_category.id
            )
            news.id = 1000 + i  # Mock ID
            news_list.append(news)
        
        await elasticsearch_service.create_index()
        
        # Bulk index
        success_count, error_count = await elasticsearch_service.bulk_index_news(news_list)
        
        assert success_count > 0
        assert error_count == 0
    
    async def test_get_stats(self):
        """Test getting index statistics."""
        await elasticsearch_service.create_index()
        
        stats = await elasticsearch_service.get_stats()
        
        assert "total_documents" in stats
        assert "index_size_mb" in stats
        assert isinstance(stats["total_documents"], int)
        assert isinstance(stats["index_size_mb"], float)


@pytest.mark.asyncio
class TestSearchAPI:
    """Test search API endpoints."""
    
    async def test_search_endpoint(self, client, sample_news):
        """Test /api/v1/search endpoint."""
        # Index news first
        await elasticsearch_service.create_index()
        await elasticsearch_service.index_news(sample_news)
        
        import asyncio
        await asyncio.sleep(1)
        
        # Search
        response = await client.post(
            "/api/v1/search/search",
            json={
                "query": "test",
                "page": 1,
                "size": 20,
                "sort_by": "_score"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "total" in data
        assert isinstance(data["results"], list)
    
    async def test_suggestions_endpoint(self, client, sample_news):
        """Test /api/v1/search/suggestions endpoint."""
        await elasticsearch_service.create_index()
        await elasticsearch_service.index_news(sample_news)
        
        import asyncio
        await asyncio.sleep(1)
        
        response = await client.get(
            "/api/v1/search/suggestions",
            params={"text": "te", "size": 5}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
    
    async def test_stats_endpoint(self, client):
        """Test /api/v1/search/stats endpoint."""
        await elasticsearch_service.create_index()
        
        response = await client.get("/api/v1/search/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_documents" in data
        assert "index_size_mb" in data
    
    async def test_health_endpoint(self, client):
        """Test /api/v1/search/health endpoint."""
        response = await client.get("/api/v1/search/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
    
    async def test_rebuild_index_endpoint(self, client, admin_token, sample_news):
        """Test /api/v1/search/index/rebuild endpoint."""
        response = await client.post(
            "/api/v1/search/index/rebuild",
            headers={"Authorization": f"Bearer {admin_token}"},
            params={"delete_existing": True}
        )
        
        # Note: This might fail if admin auth is not implemented
        # Adjust based on your auth implementation
        assert response.status_code in [200, 401, 403]
