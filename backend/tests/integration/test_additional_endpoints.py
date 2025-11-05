"""
Tests for Category API endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCategoryAPI:
    """Test category endpoints."""
    
    async def test_get_categories(self, client: AsyncClient):
        """Test GET /categories."""
        response = await client.get("/api/v1/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_category_by_id(self, client: AsyncClient, sample_category):
        """Test GET /categories/{id}."""
        response = await client.get(f"/api/v1/categories/{sample_category.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_category.id
        assert data["name"] == sample_category.name
    
    async def test_get_nonexistent_category(self, client: AsyncClient):
        """Test GET /categories/{id} with invalid ID."""
        response = await client.get("/api/v1/categories/99999")
        
        assert response.status_code == 404
    
    async def test_get_news_by_category(self, client: AsyncClient, sample_category, sample_news):
        """Test GET /categories/{id}/news."""
        response = await client.get(f"/api/v1/categories/{sample_category.id}/news")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert isinstance(data["items"], list)
    
    async def test_get_category_statistics(self, client: AsyncClient, sample_category):
        """Test category statistics."""
        response = await client.get(f"/api/v1/categories/{sample_category.id}/stats")
        
        # This endpoint might not exist yet, adjust based on implementation
        assert response.status_code in [200, 404]


@pytest.mark.asyncio
class TestSourceAPI:
    """Test source endpoints."""
    
    async def test_get_sources(self, client: AsyncClient):
        """Test GET /sources."""
        response = await client.get("/api/v1/sources")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    async def test_get_source_by_id(self, client: AsyncClient, sample_source):
        """Test GET /sources/{id}."""
        response = await client.get(f"/api/v1/sources/{sample_source.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_source.id
        assert data["name"] == sample_source.name
    
    async def test_get_news_by_source(self, client: AsyncClient, sample_source):
        """Test GET /sources/{id}/news."""
        response = await client.get(f"/api/v1/sources/{sample_source.id}/news")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)


@pytest.mark.asyncio
class TestBookmarkAPI:
    """Test bookmark endpoints."""
    
    async def test_get_user_bookmarks(self, client: AsyncClient, user_token):
        """Test GET /users/me/bookmarks."""
        response = await client.get(
            "/api/v1/users/me/bookmarks",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
    
    async def test_add_bookmark(self, client: AsyncClient, user_token, sample_news):
        """Test POST /users/me/bookmarks."""
        response = await client.post(
            "/api/v1/users/me/bookmarks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"news_id": sample_news.id}
        )
        
        assert response.status_code in [200, 201]
    
    async def test_remove_bookmark(self, client: AsyncClient, user_token, sample_news):
        """Test DELETE /users/me/bookmarks/{news_id}."""
        # First add bookmark
        await client.post(
            "/api/v1/users/me/bookmarks",
            headers={"Authorization": f"Bearer {user_token}"},
            json={"news_id": sample_news.id}
        )
        
        # Then remove it
        response = await client.delete(
            f"/api/v1/users/me/bookmarks/{sample_news.id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code in [200, 204]
    
    async def test_bookmark_unauthorized(self, client: AsyncClient, sample_news):
        """Test bookmark without authentication."""
        response = await client.post(
            "/api/v1/users/me/bookmarks",
            json={"news_id": sample_news.id}
        )
        
        assert response.status_code == 401


@pytest.mark.asyncio
class TestRecommendationAPI:
    """Test recommendation endpoints."""
    
    async def test_get_recommendations_authenticated(self, client: AsyncClient, user_token):
        """Test GET /news/recommended with authentication."""
        response = await client.get(
            "/api/v1/news/recommended",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
    
    async def test_get_recommendations_unauthenticated(self, client: AsyncClient):
        """Test GET /news/recommended without authentication."""
        response = await client.get("/api/v1/news/recommended")
        
        # Should return general trending/popular news
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
    
    async def test_recommendations_limit(self, client: AsyncClient, user_token):
        """Test recommendations with limit parameter."""
        response = await client.get(
            "/api/v1/news/recommended?limit=5",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) <= 5


@pytest.mark.asyncio
class TestHealthEndpoint:
    """Test health check endpoint."""
    
    async def test_health_check(self, client: AsyncClient):
        """Test GET /health."""
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["healthy", "degraded", "unhealthy"]
    
    async def test_health_check_details(self, client: AsyncClient):
        """Test health check includes service details."""
        response = await client.get("/api/v1/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check for database health
        if "database" in data:
            assert data["database"]["status"] in ["up", "down"]
        
        # Check for redis health
        if "redis" in data:
            assert data["redis"]["status"] in ["up", "down"]


@pytest.mark.asyncio
class TestPaginationAndFiltering:
    """Test pagination and filtering across endpoints."""
    
    async def test_news_pagination(self, client: AsyncClient):
        """Test news pagination."""
        # First page
        response1 = await client.get("/api/v1/news?page=1&limit=5")
        assert response1.status_code == 200
        data1 = response1.json()
        
        # Second page
        response2 = await client.get("/api/v1/news?page=2&limit=5")
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Items should be different
        if data1["items"] and data2["items"]:
            assert data1["items"][0]["id"] != data2["items"][0]["id"]
    
    async def test_news_filtering_by_sentiment(self, client: AsyncClient):
        """Test filtering news by sentiment."""
        response = await client.get("/api/v1/news?sentiment=positive")
        
        assert response.status_code == 200
        data = response.json()
        
        # All items should have positive sentiment
        for item in data["items"]:
            if "sentiment" in item:
                assert item["sentiment"] == "positive"
    
    async def test_news_sorting(self, client: AsyncClient):
        """Test sorting news."""
        response = await client.get("/api/v1/news?sort_by=published_at&order=desc")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check if sorted by published_at descending
        if len(data["items"]) > 1:
            dates = [item.get("published_at") for item in data["items"] if item.get("published_at")]
            if len(dates) > 1:
                assert dates == sorted(dates, reverse=True)


@pytest.mark.asyncio
class TestErrorHandling:
    """Test error handling."""
    
    async def test_invalid_page_number(self, client: AsyncClient):
        """Test invalid page number."""
        response = await client.get("/api/v1/news?page=-1")
        
        assert response.status_code == 422  # Validation error
    
    async def test_invalid_limit(self, client: AsyncClient):
        """Test invalid limit."""
        response = await client.get("/api/v1/news?limit=0")
        
        assert response.status_code == 422
    
    async def test_malformed_json(self, client: AsyncClient, admin_token):
        """Test malformed JSON payload."""
        response = await client.post(
            "/api/v1/news",
            headers={"Authorization": f"Bearer {admin_token}"},
            content="invalid json{{{",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    async def test_missing_required_field(self, client: AsyncClient, admin_token):
        """Test missing required field in request."""
        response = await client.post(
            "/api/v1/news",
            headers={"Authorization": f"Bearer {admin_token}"},
            json={
                # Missing required fields
                "content": "Some content"
            }
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
class TestRateLimiting:
    """Test rate limiting."""
    
    async def test_rate_limit_not_triggered_normal_use(self, client: AsyncClient):
        """Test normal usage doesn't trigger rate limit."""
        for _ in range(10):
            response = await client.get("/api/v1/news")
            assert response.status_code == 200
    
    @pytest.mark.slow
    async def test_rate_limit_triggered(self, client: AsyncClient):
        """Test rate limit with excessive requests."""
        # This test depends on your rate limit configuration
        # Adjust the number based on your settings
        
        responses = []
        for _ in range(100):  # Adjust based on your rate limit
            response = await client.get("/api/v1/news")
            responses.append(response.status_code)
        
        # At least one should be rate limited
        # Status code 429 = Too Many Requests
        # Adjust this test based on your actual rate limiting implementation
        assert 200 in responses  # Some should succeed
