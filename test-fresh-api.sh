#!/bin/bash

# Simplified Quick Test for Smart News Aggregator
# Tests the /fresh API endpoint with minimal setup

set -e

echo "🚀 Testing Smart News Fresh API"
echo "================================"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Ensure postgres and redis are running
echo -e "\n${YELLOW}🔍 Checking Docker services...${NC}"
docker-compose ps | grep -q smart_news_postgres || {
    echo "Starting postgres and redis..."
    docker-compose up -d postgres redis
    sleep 10
}

echo -e "${GREEN}✅ Docker services running${NC}"

# Go to backend directory
cd backend

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi

# Install deps if needed
echo -e "\n${YELLOW}📦 Checking dependencies...${NC}"
python3 -m pip install --user -q fastapi uvicorn sqlalchemy asyncpg pydantic-settings alembic redis || true

# Export environment variables
export POSTGRES_SERVER=localhost
export POSTGRES_PORT=5432
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=news_aggregator
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/news_aggregator"
export REDIS_HOST=localhost
export REDIS_PORT=6379
export REDIS_URL="redis://localhost:6379/0"
export SECRET_KEY="dev-secret-key"
export ENVIRONMENT=development
export DEBUG=True

# Run migrations
echo -e "\n${YELLOW}🗄️  Setting up database...${NC}"
python3 -m alembic upgrade head 2>/dev/null || echo "Database may already be set up"

# Initialize DB
echo -e "\n${YELLOW}👤 Creating admin user...${NC}"
python3 << 'PYTHON'
import asyncio
import sys
sys.path.insert(0, '.')

async def init():
    try:
        from app.db.session import SessionLocal
        from app.db.init_db import init_db
        async for db in SessionLocal():
            await init_db(db)
            break
        print("✅ Database initialized")
    except Exception as e:
        print(f"Note: {e}")

asyncio.run(init())
PYTHON

# Start server
echo -e "\n${YELLOW}🚀 Starting backend server on port 8000...${NC}"
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Stopping server...${NC}"
    kill $SERVER_PID 2>/dev/null || true
}
trap cleanup EXIT

# Wait for server
echo -e "${YELLOW}⏳ Waiting for server to start...${NC}"
sleep 8

# Check health
if curl -sf http://localhost:8000/api/v1/health > /dev/null; then
    echo -e "${GREEN}✅ Server is running!${NC}"
else
    echo -e "${RED}❌ Server failed to start${NC}"
    exit 1
fi

# Login
echo -e "\n${YELLOW}🔑 Logging in...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@smartnews.com","password":"changethis"}')

TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}Note: Login failed, trying to create test data anyway${NC}"
    TOKEN="dummy"
fi

# Create a test source
echo -e "\n${YELLOW}📰 Creating test source...${NC}"
curl -s -X POST "http://localhost:8000/api/v1/sources" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test News Source",
    "url": "https://test.com",
    "description": "Test source",
    "is_active": true,
    "reliability_score": 0.9
  }' | python3 -m json.tool || echo "Source may already exist"

# Create a test category
echo -e "\n${YELLOW}📁 Creating test category...${NC}"
curl -s -X POST "http://localhost:8000/api/v1/categories" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Technology",
    "slug": "tech",
    "description": "Tech news"
  }' | python3 -m json.tool || echo "Category may already exist"

# Create fresh news
echo -e "\n${YELLOW}📝 Creating fresh news articles...${NC}"
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

for i in 1 2 3; do
    echo "Creating article $i..."
    curl -s -X POST "http://localhost:8000/api/v1/news" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"title\": \"Breaking: Fresh News Article #$i\",
        \"content\": \"This is fresh news content for article $i, published just now.\",
        \"summary\": \"Fresh news summary $i\",
        \"url\": \"https://example.com/news-$RANDOM\",
        \"source_id\": 1,
        \"category_id\": 1,
        \"published_at\": \"$NOW\",
        \"sentiment\": \"positive\",
        \"language\": \"en\"
      }" > /dev/null && echo "  ✓ Article $i created" || echo "  ✗ Failed"
done

# Test Fresh News API
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Testing Fresh News API${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}1️⃣  GET /api/v1/news/fresh (last 24 hours):${NC}\n"
curl -s "http://localhost:8000/api/v1/news/fresh" | python3 -m json.tool | head -50

echo -e "\n\n${YELLOW}2️⃣  GET /api/v1/news/fresh?hours=1 (last hour):${NC}\n"
curl -s "http://localhost:8000/api/v1/news/fresh?hours=1" | python3 -m json.tool | head -50

echo -e "\n\n${YELLOW}3️⃣  GET /api/v1/news/fresh?limit=2 (limit 2):${NC}\n"
curl -s "http://localhost:8000/api/v1/news/fresh?limit=2" | python3 -m json.tool

echo -e "\n\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Test Complete!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}📋 Available Endpoints:${NC}"
echo "Fresh news (24h):     http://localhost:8000/api/v1/news/fresh"
echo "Fresh news (custom):  http://localhost:8000/api/v1/news/fresh?hours=6&limit=10"
echo "All news:             http://localhost:8000/api/v1/news"
echo "Trending news:        http://localhost:8000/api/v1/news/trending"
echo "API Documentation:    http://localhost:8000/docs"
echo "Health Check:         http://localhost:8000/api/v1/health"

echo -e "\n${YELLOW}Press Ctrl+C to stop the server${NC}\n"

# Wait for user interrupt
wait $SERVER_PID
