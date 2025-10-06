# 📚 API Documentation

## Smart News Aggregator API Reference

Base URL: `http://localhost:8000/api/v1`

---

## 🔐 Authentication

### Register User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "created_at": "2025-10-05T12:00:00Z"
}
```

### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 📰 News Endpoints

### Get News List
```http
GET /api/v1/news?page=1&limit=20&category_id=uuid&sort=latest
Authorization: Bearer {token}
```

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)
- `category_id` (uuid): Filter by category
- `source_id` (uuid): Filter by source
- `sentiment` (string): Filter by sentiment (positive/negative/neutral)
- `sort` (string): Sort order (latest, trending, relevant)

**Response (200):**
```json
{
  "items": [
    {
      "id": "uuid",
      "title": "Breaking News Title",
      "summary": "Brief summary of the article...",
      "content": "Full article content...",
      "url": "https://source.com/article",
      "image_url": "https://cdn.com/image.jpg",
      "category": {
        "id": "uuid",
        "name": "Technology",
        "slug": "technology"
      },
      "source": {
        "id": "uuid",
        "name": "TechCrunch"
      },
      "sentiment": "positive",
      "published_at": "2025-10-05T10:00:00Z",
      "tags": ["AI", "Machine Learning"]
    }
  ],
  "total": 1000,
  "page": 1,
  "limit": 20,
  "pages": 50
}
```

### Get Single News
```http
GET /api/v1/news/{news_id}
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "id": "uuid",
  "title": "Article Title",
  "summary": "Summary...",
  "content": "Full content...",
  "url": "https://source.com/article",
  "image_url": "https://cdn.com/image.jpg",
  "category": {...},
  "source": {...},
  "sentiment": "positive",
  "entities": [
    {
      "text": "Elon Musk",
      "type": "PERSON",
      "confidence": 0.95
    }
  ],
  "tags": ["AI", "Tech"],
  "published_at": "2025-10-05T10:00:00Z",
  "views": 1234
}
```

### Get Trending News
```http
GET /api/v1/news/trending?limit=10
Authorization: Bearer {token}
```

### Get Recommended News
```http
GET /api/v1/news/recommended?limit=20
Authorization: Bearer {token}
```

---

## 🔍 Search

### Search News
```http
POST /api/v1/search
Authorization: Bearer {token}
Content-Type: application/json

{
  "query": "artificial intelligence",
  "filters": {
    "category_id": "uuid",
    "sentiment": "positive",
    "date_from": "2025-10-01",
    "date_to": "2025-10-05"
  },
  "sort": "relevance",
  "page": 1,
  "limit": 20
}
```

**Response (200):**
```json
{
  "results": [
    {
      "id": "uuid",
      "title": "AI Breakthrough",
      "summary": "...",
      "relevance_score": 0.95,
      "highlight": "...artificial intelligence..."
    }
  ],
  "total": 50,
  "took_ms": 42
}
```

---

## 📂 Categories

### Get Categories
```http
GET /api/v1/categories
```

**Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "Technology",
    "slug": "technology",
    "description": "Latest tech news",
    "news_count": 1234
  }
]
```

### Get Category News
```http
GET /api/v1/categories/{category_id}/news?page=1&limit=20
Authorization: Bearer {token}
```

---

## 🌐 Sources

### Get Sources
```http
GET /api/v1/sources
Authorization: Bearer {token}
```

**Response (200):**
```json
[
  {
    "id": "uuid",
    "name": "TechCrunch",
    "url": "https://techcrunch.com",
    "type": "rss",
    "is_active": true,
    "news_count": 5678
  }
]
```

---

## 👤 User Endpoints

### Get Current User
```http
GET /api/v1/users/me
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "full_name": "John Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2025-01-01T00:00:00Z"
}
```

### Update Profile
```http
PUT /api/v1/users/me
Authorization: Bearer {token}
Content-Type: application/json

{
  "full_name": "John Smith",
  "preferences": {
    "categories": ["technology", "business"],
    "email_notifications": true
  }
}
```

### Get User Bookmarks
```http
GET /api/v1/users/me/bookmarks?page=1&limit=20
Authorization: Bearer {token}
```

### Add Bookmark
```http
POST /api/v1/users/me/bookmarks
Authorization: Bearer {token}
Content-Type: application/json

{
  "news_id": "uuid"
}
```

### Remove Bookmark
```http
DELETE /api/v1/users/me/bookmarks/{news_id}
Authorization: Bearer {token}
```

### Get Reading History
```http
GET /api/v1/users/me/history?page=1&limit=20
Authorization: Bearer {token}
```

---

## 🛠️ Admin Endpoints

**Note:** Requires admin privileges

### Get All Sources
```http
GET /api/v1/admin/sources
Authorization: Bearer {admin_token}
```

### Add Source
```http
POST /api/v1/admin/sources
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "name": "BBC News",
  "url": "https://feeds.bbci.co.uk/news/rss.xml",
  "type": "rss",
  "is_active": true,
  "scrape_interval": 1800
}
```

### Update Source
```http
PUT /api/v1/admin/sources/{source_id}
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "is_active": false
}
```

### Trigger Manual Scraping
```http
POST /api/v1/admin/scrape/trigger
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "source_ids": ["uuid1", "uuid2"]
}
```

---

## 📊 Analytics

### Get Statistics
```http
GET /api/v1/analytics/stats
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "total_news": 50000,
  "total_sources": 15,
  "total_categories": 8,
  "today_scraped": 1234,
  "trending_topics": ["AI", "Climate", "Economy"]
}
```

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Not authenticated"
}
```

### 403 Forbidden
```json
{
  "detail": "Not enough permissions"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 429 Too Many Requests
```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

## 🔄 Rate Limiting

- **General endpoints:** 100 requests/minute
- **Auth endpoints:** 5 requests/minute
- **Search endpoints:** 20 requests/minute

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1696512000
```

---

## 📝 Response Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

---

## 🔗 Interactive Documentation

Visit the interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📦 SDKs & Libraries

### Python
```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/v1/auth/login",
    json={
        "email": "user@example.com",
        "password": "password"
    }
)
token = response.json()["access_token"]

# Get news
headers = {"Authorization": f"Bearer {token}"}
news = requests.get(
    "http://localhost:8000/api/v1/news",
    headers=headers
).json()
```

### JavaScript/TypeScript
```javascript
// Login
const response = await fetch('http://localhost:8000/api/v1/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    email: 'user@example.com',
    password: 'password'
  })
});
const { access_token } = await response.json();

// Get news
const news = await fetch('http://localhost:8000/api/v1/news', {
  headers: { 'Authorization': `Bearer ${access_token}` }
}).then(r => r.json());
```

---

## 🛡️ Security

- All endpoints use HTTPS in production
- JWT tokens expire after 30 minutes
- Refresh tokens expire after 7 days
- Passwords are hashed with bcrypt
- Rate limiting on all endpoints
- CORS configured for allowed origins

---

## 📞 Support

For API support:
- Documentation: http://localhost:8000/docs
- Issues: GitHub Issues
- Email: api@smartnews.com

---

**Last Updated:** October 2025  
**API Version:** v1.0.0
