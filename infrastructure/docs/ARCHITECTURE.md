# 🏗️ Architecture Documentation

## System Overview

Smart News Aggregator is built on a **microservices architecture** with four main services:

1. **Backend API** (FastAPI) - Core business logic
2. **ML Service** (FastAPI) - Machine learning & NLP
3. **Scraper Service** (Celery) - News aggregation
4. **Frontend** (Next.js) - User interface

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     INTERNET                            │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────┐
│                  NGINX (Reverse Proxy)                  │
│  - Load Balancing                                       │
│  - SSL Termination                                      │
│  - Rate Limiting                                        │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌────────┐    ┌────────┐    ┌─────────┐
    │Frontend│    │Backend │    │   ML    │
    │Next.js │    │FastAPI │    │ Service │
    └────┬───┘    └───┬────┘    └────┬────┘
         │            │              │
         └────────────┼──────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
   ┌─────────┐  ┌─────────┐  ┌──────────┐
   │   DB    │  │  Cache  │  │  Queue   │
   │PostgreSQL│ │  Redis  │  │ RabbitMQ │
   └─────────┘  └─────────┘  └──────────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
                      ▼
               ┌────────────┐
               │  Scraper   │
               │   Celery   │
               └────────────┘
```

---

## Component Details

### 1. Backend API (FastAPI)

**Responsibilities:**
- REST API endpoints
- Business logic
- Authentication & authorization
- Data validation
- Caching
- WebSocket connections

**Technologies:**
- FastAPI (async Python)
- SQLAlchemy ORM
- Pydantic validation
- JWT authentication
- Redis caching

**Key Features:**
- Async/await for high performance
- Automatic API documentation
- Type hints throughout
- Dependency injection
- Middleware pipeline

**Endpoints:**
```
/api/v1/auth/*       - Authentication
/api/v1/news/*       - News operations
/api/v1/categories/* - Categories
/api/v1/users/*      - User management
/api/v1/search       - Search
/api/v1/admin/*      - Admin operations
```

---

### 2. ML Service

**Responsibilities:**
- News classification
- Sentiment analysis
- Named Entity Recognition (NER)
- Text summarization
- Clustering
- Embeddings generation
- Recommendations

**Technologies:**
- FastAPI
- scikit-learn
- spaCy (NLP)
- sentence-transformers
- NLTK
- TensorFlow (optional)

**Models:**
1. **Classifier** - 8 categories
2. **NER** - Entities extraction
3. **Sentiment** - Positive/Negative/Neutral
4. **Summarizer** - Text summarization
5. **Clustering** - Similar articles
6. **Embeddings** - Vector representations

**Processing Pipeline:**
```
Raw Text
   ↓
Preprocessing (cleaning, tokenization)
   ↓
Classification → Category
   ↓
NER → Entities
   ↓
Sentiment Analysis → Sentiment
   ↓
Summarization → Summary
   ↓
Embeddings → Vector
```

---

### 3. Scraper Service

**Responsibilities:**
- News scraping
- Data extraction
- Image downloading
- Deduplication
- ML processing integration
- Periodic scheduling

**Technologies:**
- Celery (task queue)
- RabbitMQ (broker)
- BeautifulSoup (parsing)
- Scrapy (framework)
- feedparser (RSS)

**Scrapers:**
1. **RSS Scraper** - RSS feeds (10+ sources)
2. **API Scraper** - News API (80,000+ sources)
3. **Web Scraper** - Direct web scraping

**Workflow:**
```
Celery Beat (scheduler)
   ↓
Scrape Task
   ↓
Extract Article Data
   ↓
Download Images
   ↓
Check Duplicates
   ↓
Send to ML Service
   ↓
Save to Database
   ↓
Index in Elasticsearch
```

---

### 4. Frontend

**Responsibilities:**
- User interface
- Client-side routing
- State management
- API communication
- Real-time updates

**Technologies:**
- Next.js 14 (React)
- TypeScript
- Tailwind CSS
- React Query
- Zustand

**Pages:**
- Home (`/`)
- Latest News (`/latest`)
- Categories (`/categories`)
- Article Detail (`/article/[id]`)
- Search (`/search`)
- Profile (`/profile`)

**Features:**
- Server-side rendering (SSR)
- Static generation (SSG)
- Client-side rendering (CSR)
- Incremental static regeneration
- Image optimization
- Code splitting

---

## Data Flow

### News Scraping Flow

```
1. Celery Beat triggers scheduled task
   ↓
2. Scraper fetches articles from sources
   ↓
3. Extract: title, content, URL, image, date
   ↓
4. Check for duplicates in database
   ↓
5. Download and process images
   ↓
6. Send to ML Service for processing
   ├── Classification
   ├── NER
   ├── Sentiment
   ├── Summarization
   └── Embeddings
   ↓
7. Save processed article to PostgreSQL
   ↓
8. Index in Elasticsearch
   ↓
9. Cache in Redis (if needed)
   ↓
10. Update user recommendations
```

### User Request Flow

```
1. User opens Frontend
   ↓
2. Frontend requests data from Backend
   ↓
3. Backend checks Redis cache
   ├── Hit → Return cached data
   └── Miss ↓
4. Query PostgreSQL
   ↓
5. Apply business logic
   ↓
6. Cache result in Redis
   ↓
7. Return to Frontend
   ↓
8. Frontend renders page
```

### Search Flow

```
1. User enters search query
   ↓
2. Frontend sends request to Backend
   ↓
3. Backend validates query
   ↓
4. Query Elasticsearch
   ├── Full-text search
   └── Filters (category, date, sentiment)
   ↓
5. Rank results by relevance
   ↓
6. Fetch additional data from PostgreSQL
   ↓
7. Return results to Frontend
```

---

## Database Design

### PostgreSQL Schema

```sql
-- Core tables
users
categories
sources
news

-- Relationships
news_tags (many-to-many)
bookmarks (user ↔ news)
user_preferences (user ↔ category)
reading_history (user ↔ news)

-- ML results
entities (news → entities)
```

### Redis Cache Strategy

**Cache Keys:**
- `news:latest:{page}` - Latest news
- `news:trending` - Trending articles
- `news:category:{id}:{page}` - Category news
- `user:{id}:feed` - User feed
- `search:{query}:{filters}` - Search results

**TTL:**
- Latest news: 5 minutes
- Trending: 15 minutes
- User feed: 10 minutes
- Search results: 30 minutes

### Elasticsearch Indices

**news index:**
```json
{
  "mappings": {
    "properties": {
      "title": {"type": "text"},
      "content": {"type": "text"},
      "summary": {"type": "text"},
      "category": {"type": "keyword"},
      "sentiment": {"type": "keyword"},
      "source": {"type": "keyword"},
      "published_at": {"type": "date"},
      "tags": {"type": "keyword"}
    }
  }
}
```

---

## Communication

### Inter-Service Communication

**Synchronous (HTTP):**
- Frontend ↔ Backend
- Backend ↔ ML Service

**Asynchronous (Queue):**
- Scraper → Backend (via RabbitMQ)
- Backend → ML Service (via RabbitMQ)

**Protocols:**
- REST API (HTTP/JSON)
- WebSocket (real-time)
- Message Queue (RabbitMQ/AMQP)

---

## Security

### Authentication Flow

```
1. User sends credentials
   ↓
2. Backend validates credentials
   ↓
3. Generate JWT tokens (access + refresh)
   ↓
4. Return tokens to user
   ↓
5. User includes token in requests
   ↓
6. Backend validates token
   ↓
7. Process request
```

**Token Structure:**
- **Access Token:** Short-lived (30 min)
- **Refresh Token:** Long-lived (7 days)

### Security Layers

1. **Transport:** HTTPS/TLS
2. **Authentication:** JWT tokens
3. **Authorization:** Role-based (RBAC)
4. **Input Validation:** Pydantic schemas
5. **Rate Limiting:** Redis-based
6. **CORS:** Configured origins only

---

## Scalability

### Horizontal Scaling

**Backend:**
- Multiple instances behind load balancer
- Stateless design
- Session storage in Redis

**ML Service:**
- Multiple workers
- Model caching
- Request queuing

**Scraper:**
- Multiple Celery workers
- Task distribution via RabbitMQ

**Database:**
- Read replicas for queries
- Write to master only
- Connection pooling

### Vertical Scaling

- Increase container resources
- Optimize queries
- Add database indexes
- Implement caching

---

## Monitoring & Observability

### Metrics (Prometheus)

**Backend:**
- Request rate
- Response time
- Error rate
- Cache hit ratio

**ML Service:**
- Model inference time
- Queue size
- Success/failure rate

**Scraper:**
- Articles scraped
- Processing time
- Failed tasks

**Infrastructure:**
- CPU usage
- Memory usage
- Disk I/O
- Network I/O

### Logging

**Levels:**
- DEBUG: Development
- INFO: Normal operations
- WARNING: Potential issues
- ERROR: Failures
- CRITICAL: System failures

**Structure:**
```json
{
  "timestamp": "2025-10-05T12:00:00Z",
  "level": "INFO",
  "service": "backend",
  "message": "Article created",
  "context": {
    "user_id": "123",
    "article_id": "456"
  }
}
```

---

## Deployment

### Development

```bash
docker-compose up -d
```

### Production

```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Using Kubernetes
kubectl apply -f infrastructure/kubernetes/
```

### CI/CD Pipeline

```
1. Code commit
   ↓
2. Run tests
   ↓
3. Run linters
   ↓
4. Build Docker images
   ↓
5. Push to registry
   ↓
6. Deploy to staging
   ↓
7. Run integration tests
   ↓
8. Deploy to production
```

---

## Performance

### Optimization Strategies

1. **Database:**
   - Indexes on frequently queried columns
   - Query optimization
   - Connection pooling
   - Read replicas

2. **Caching:**
   - Redis for frequent queries
   - CDN for static assets
   - Browser caching

3. **API:**
   - Async operations
   - Pagination
   - Field selection
   - Response compression

4. **Frontend:**
   - Code splitting
   - Lazy loading
   - Image optimization
   - SSR/SSG

### Expected Performance

- API Response: < 200ms (p95)
- Search: < 50ms
- ML Processing: < 500ms
- Throughput: 1000+ req/s
- Uptime: 99.9%

---

## Disaster Recovery

### Backup Strategy

**Database:**
- Daily full backups
- Hourly incremental
- Retention: 30 days

**Files:**
- Hourly backups to S3/MinIO
- Retention: 90 days

### Recovery

**RTO (Recovery Time Objective):** < 4 hours  
**RPO (Recovery Point Objective):** < 1 hour

**Procedure:**
1. Restore database from backup
2. Restore files from backup
3. Restart services
4. Verify data integrity
5. Resume operations

---

## Future Enhancements

1. **GraphQL API** - More flexible queries
2. **gRPC** - Faster inter-service communication
3. **Event Sourcing** - Complete audit trail
4. **Multi-tenancy** - Support multiple organizations
5. **Real-time Analytics** - Live dashboards
6. **Mobile Apps** - Native iOS/Android
7. **Offline Support** - PWA capabilities
8. **Multi-language** - Internationalization

---

## References

- [Backend README](../backend/README.md)
- [ML Service README](../ml_service/README.md)
- [Scraper README](../scraper_service/README.md)
- [Frontend README](../frontend/README.md)
- [API Documentation](API.md)
- [Deployment Guide](DEPLOYMENT.md)

---

**Last Updated:** October 2025  
**Version:** 1.0.0
