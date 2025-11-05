"""Test authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test root endpoint."""
    response = await client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    """Test health check endpoint."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    """Test user registration."""
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "full_name": "Test User"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    """Test user login."""
    # First register user
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "full_name": "Test User"
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    # Then login
    login_data = {
        "email": user_data["email"],
        "password": user_data["password"]
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    login_data = {
        "email": "nonexistent@example.com",
        "password": "WrongPassword123"
    }
    
    response = await client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_current_user(client: AsyncClient):
    """Test getting current user info."""
    # Register and login
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "full_name": "Test User"
    }
    await client.post("/api/v1/auth/register", json=user_data)
    
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"email": user_data["email"], "password": user_data["password"]}
    )
    token = login_response.json()["access_token"]
    
    # Get current user
    response = await client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
