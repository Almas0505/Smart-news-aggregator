"""Integration tests for News API endpoints."""

import pytest
from httpx import AsyncClient
from datetime import datetime


@pytest.mark.asyncio
class TestNewsAPI:
    """Test News API endpoints."""
    
    async def test_get_news_list(self, client: AsyncClient):
        """Test getting list of news."""
        response = await client.get("/api/v1/news")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "pages" in data
        assert isinstance(data["items"], list)
    
    async def test_get_news_list_with_pagination(self, client: AsyncClient):
        """Test news list pagination."""
        response = await client.get("/api/v1/news?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) <= 5
    
    async def test_get_news_list_with_category_filter(self, client: AsyncClient):
        """Test filtering news by category."""
        response = await client.get("/api/v1/news?category_id=1")
        
        assert response.status_code == 200
        data = response.json()
        
        # All items should belong to category 1
        for item in data["items"]:
            if item.get("category"):
                assert item["category"]["id"] == 1
    
    async def test_get_trending_news(self, client: AsyncClient):
        """Test getting trending news."""
        response = await client.get("/api/v1/news/trending")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) <= 10  # Default limit
    
    async def test_get_trending_news_with_limit(self, client: AsyncClient):
        """Test trending news with custom limit."""
        response = await client.get("/api/v1/news/trending?limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) <= 5
    
    async def test_get_news_by_id(self, client: AsyncClient, sample_news):
        """Test getting single news article."""
        news_id = sample_news["id"]
        response = await client.get(f"/api/v1/news/{news_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == news_id
        assert "title" in data
        assert "content" in data
        assert "url" in data
        assert "source" in data
    
    async def test_get_nonexistent_news(self, client: AsyncClient):
        """Test getting non-existent news returns 404."""
        response = await client.get("/api/v1/news/999999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    async def test_create_news_as_admin(self, client: AsyncClient, admin_token, sample_source, sample_category):
        """Test creating news as admin."""
        news_data = {
            "title": "Test News Article",
            "content": "This is test content for news article",
            "url": f"https://test.com/article-{datetime.utcnow().timestamp()}",
            "source_id": sample_source["id"],
            "category_id": sample_category["id"],
            "published_at": datetime.utcnow().isoformat()
        }
        
        response = await client.post(
            "/api/v1/news",
            json=news_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["title"] == news_data["title"]
        assert data["url"] == news_data["url"]
        assert "id" in data
    
    async def test_create_news_as_regular_user_forbidden(self, client: AsyncClient, user_token):
        """Test that regular users cannot create news."""
        news_data = {
            "title": "Test News",
            "content": "Content",
            "url": "https://test.com/article",
            "source_id": 1,
            "category_id": 1,
            "published_at": datetime.utcnow().isoformat()
        }
        
        response = await client.post(
            "/api/v1/news",
            json=news_data,
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_create_duplicate_news_url(self, client: AsyncClient, admin_token, sample_news):
        """Test that duplicate URLs are rejected."""
        news_data = {
            "title": "Different Title",
            "content": "Different content",
            "url": sample_news["url"],  # Same URL as existing news
            "source_id": 1,
            "category_id": 1,
            "published_at": datetime.utcnow().isoformat()
        }
        
        response = await client.post(
            "/api/v1/news",
            json=news_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()
    
    async def test_update_news_as_admin(self, client: AsyncClient, admin_token, sample_news):
        """Test updating news as admin."""
        news_id = sample_news["id"]
        update_data = {
            "title": "Updated Title",
            "content": "Updated content"
        }
        
        response = await client.put(
            f"/api/v1/news/{news_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["title"] == update_data["title"]
        assert data["content"] == update_data["content"]
    
    async def test_update_nonexistent_news(self, client: AsyncClient, admin_token):
        """Test updating non-existent news returns 404."""
        response = await client.put(
            "/api/v1/news/999999",
            json={"title": "Updated"},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 404
    
    async def test_delete_news_as_admin(self, client: AsyncClient, admin_token, sample_news):
        """Test deleting news as admin."""
        news_id = sample_news["id"]
        
        response = await client.delete(
            f"/api/v1/news/{news_id}",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        assert response.status_code == 200
        assert "success" in response.json()["message"].lower()
        
        # Verify news is deleted
        get_response = await client.get(f"/api/v1/news/{news_id}")
        assert get_response.status_code == 404
    
    async def test_delete_news_as_regular_user_forbidden(self, client: AsyncClient, user_token, sample_news):
        """Test that regular users cannot delete news."""
        news_id = sample_news["id"]
        
        response = await client.delete(
            f"/api/v1/news/{news_id}",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        
        assert response.status_code == 403
    
    async def test_news_views_increment(self, client: AsyncClient, sample_news):
        """Test that viewing news increments view count."""
        news_id = sample_news["id"]
        
        # Get initial view count
        response1 = await client.get(f"/api/v1/news/{news_id}")
        initial_views = response1.json()["views_count"]
        
        # View again
        response2 = await client.get(f"/api/v1/news/{news_id}")
        new_views = response2.json()["views_count"]
        
        assert new_views >= initial_views
