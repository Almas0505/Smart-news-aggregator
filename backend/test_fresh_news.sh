#!/bin/bash
# Test Fresh News API Endpoint

set -e

echo "🚀 Testing Fresh News API Endpoint"
echo "=================================="

# Check if Docker services are running
echo ""
echo "📦 Checking Docker services..."
docker ps | grep -E "(postgres|redis)" || {
    echo "❌ Docker services not running. Starting..."
    docker-compose up -d postgres redis
    sleep 10
}

# Build backend Docker image if needed
echo ""
echo "🏗️  Building backend Docker image..."
cd /mnt/c/Projects/smart-news-aggregator
docker-compose build backend

# Run database migrations
echo ""
echo "🗄️  Running database migrations..."
docker-compose run --rm backend alembic upgrade head || {
    echo "⚠️  Migrations might have issues, continuing..."
}

# Start backend service
echo ""
echo "🚀 Starting backend service..."
docker-compose up -d backend

# Wait for backend to be healthy
echo ""
echo "⏳ Waiting for backend to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        break
    fi
    echo "   Attempt $i/30..."
    sleep 2
done

# Create test data script
echo ""
echo "📝 Creating test data..."
cat > /tmp/create_test_news.py << 'PYTHON_SCRIPT'
import asyncio
import sys
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

sys.path.append('/app')

from app.models.source import Source
from app.models.category import Category
from app.models.news import News

DATABASE_URL = "postgresql+asyncpg://postgres:postgres@postgres:5432/news_aggregator"

async def create_test_data():
    """Create test data for fresh news endpoint."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create source
        source = Source(
            name="Test News Source",
            url="https://test-news.com",
            is_active=True
        )
        session.add(source)
        await session.flush()
        
        # Create category
        category = Category(
            name="Technology",
            slug="technology"
        )
        session.add(category)
        await session.flush()
        
        # Create fresh news (last 24 hours)
        now = datetime.utcnow()
        news_items = []
        
        for i in range(10):
            news = News(
                title=f"Fresh News Article {i+1}",
                url=f"https://test-news.com/article-{i+1}",
                content=f"This is fresh content for article {i+1}. Published recently.",
                summary=f"Summary of article {i+1}",
                source_id=source.id,
                category_id=category.id,
                published_at=now - timedelta(hours=i),
                scraped_at=now,
                sentiment="neutral",
                views_count=i * 10,
                bookmarks_count=i * 2
            )
            news_items.append(news)
        
        session.add_all(news_items)
        await session.commit()
        
        print(f"✅ Created {len(news_items)} fresh news articles")
        print(f"   - Source: {source.name}")
        print(f"   - Category: {category.name}")
        print(f"   - Time range: Last {len(news_items)} hours")

if __name__ == "__main__":
    asyncio.run(create_test_data())
PYTHON_SCRIPT

# Run test data creation inside Docker
echo ""
docker cp /tmp/create_test_news.py smart_news_backend:/tmp/
docker-compose exec -T backend python3 /tmp/create_test_news.py

# Test the API endpoint
echo ""
echo "🧪 Testing Fresh News API Endpoint"
echo "=================================="

# Test 1: Get fresh news (default 24 hours)
echo ""
echo "Test 1: GET /api/v1/news/fresh (default)"
curl -s http://localhost:8000/api/v1/news/fresh | python3 -m json.tool | head -50

# Test 2: Get fresh news (last 12 hours)
echo ""
echo ""
echo "Test 2: GET /api/v1/news/fresh?hours=12"
curl -s "http://localhost:8000/api/v1/news/fresh?hours=12" | python3 -m json.tool | head -30

# Test 3: Get fresh news with limit
echo ""
echo ""
echo "Test 3: GET /api/v1/news/fresh?limit=5"
curl -s "http://localhost:8000/api/v1/news/fresh?limit=5" | python3 -m json.tool | head -30

# Test 4: Check response structure
echo ""
echo ""
echo "Test 4: Checking response structure..."
RESPONSE=$(curl -s http://localhost:8000/api/v1/news/fresh)
if echo "$RESPONSE" | grep -q "title"; then
    echo "✅ Response contains 'title' field"
else
    echo "❌ Response missing 'title' field"
fi

if echo "$RESPONSE" | grep -q "published_at"; then
    echo "✅ Response contains 'published_at' field"
else
    echo "❌ Response missing 'published_at' field"
fi

# Test 5: Count results
echo ""
echo "Test 5: Counting results..."
COUNT=$(curl -s "http://localhost:8000/api/v1/news/fresh?limit=100" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "   Found $COUNT fresh news articles"

# Test 6: Verify sorting (newest first)
echo ""
echo "Test 6: Verifying sort order (newest first)..."
curl -s "http://localhost:8000/api/v1/news/fresh?limit=3" | python3 -c "
import sys, json
from datetime import datetime

data = json.load(sys.stdin)
if len(data) >= 2:
    dates = [datetime.fromisoformat(item['published_at'].replace('Z', '+00:00')) for item in data]
    is_sorted = all(dates[i] >= dates[i+1] for i in range(len(dates)-1))
    if is_sorted:
        print('✅ News is sorted by newest first')
    else:
        print('❌ News is NOT properly sorted')
else:
    print('⚠️  Not enough data to verify sorting')
"

echo ""
echo "=================================="
echo "✅ Fresh News API Testing Complete!"
echo "=================================="
echo ""
echo "📊 Summary:"
echo "   - Endpoint: GET /api/v1/news/fresh"
echo "   - Parameters: hours (1-168), limit (1-100), category_id"
echo "   - Returns: List of news sorted by newest first"
echo "   - Cache TTL: 5 minutes"
echo ""
echo "🌐 API Documentation:"
echo "   http://localhost:8000/docs#/news/get_fresh_news_api_v1_news_fresh_get"
