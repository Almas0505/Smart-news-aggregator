#!/bin/bash

# Quick test script for Smart News Aggregator API
# Запускает backend локально и тестирует /fresh endpoint

set -e

echo "🚀 Quick Start - Smart News Aggregator"
echo "======================================="

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check if postgres and redis are running
echo -e "\n${YELLOW}🔍 Checking Docker services...${NC}"
if ! docker ps | grep -q smart_news_postgres; then
    echo -e "${RED}❌ Postgres is not running. Starting...${NC}"
    docker-compose up -d postgres redis
    sleep 10
fi

echo -e "${GREEN}✅ Docker services are running${NC}"

# Update .env for local development
echo -e "\n${YELLOW}🔧 Updating .env for local development...${NC}"
cd backend

# Create temporary .env for local run
cat > .env.local << EOF
# Local Development Environment
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=news_aggregator
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/news_aggregator

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://localhost:6379/0

ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_URL=http://localhost:9200

ML_SERVICE_URL=http://localhost:8001

SECRET_KEY=dev-secret-key-for-local-testing
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

ENVIRONMENT=development
DEBUG=True
API_V1_PREFIX=/api/v1

BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:3001"]
RATE_LIMIT_PER_MINUTE=60
LOG_LEVEL=INFO
EOF

# Use the local env file
export $(grep -v '^#' .env.local | xargs)

echo -e "${GREEN}✅ Environment configured${NC}"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}📦 Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "\n${YELLOW}📦 Installing dependencies...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Run migrations
echo -e "\n${YELLOW}🗄️  Running database migrations...${NC}"
alembic upgrade head || echo "Migrations may already be applied"

# Initialize database with superuser
echo -e "\n${YELLOW}👤 Initializing database...${NC}"
python -c "
import asyncio
from app.db.session import SessionLocal
from app.db.init_db import init_db

async def main():
    async for db in SessionLocal():
        await init_db(db)
        break

asyncio.run(main())
" || echo "Database may already be initialized"

echo -e "${GREEN}✅ Database ready${NC}"

# Start backend server in background
echo -e "\n${YELLOW}🚀 Starting backend server...${NC}"
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait for backend to start
echo -e "\n${YELLOW}⏳ Waiting for backend to start...${NC}"
sleep 5

# Health check
for i in {1..10}; do
    if curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is running!${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Create test data
echo -e "\n${YELLOW}📝 Creating test data...${NC}"

# Login and get token
echo "Logging in..."
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@smartnews.com",
    "password": "changethis"
  }' | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to login${NC}"
    kill $BACKEND_PID
    exit 1
fi

echo -e "${GREEN}✅ Logged in${NC}"

# Create sources
echo "Creating sources..."
curl -s -X POST "http://localhost:8000/api/v1/sources" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BBC News",
    "url": "https://www.bbc.com/news",
    "description": "British Broadcasting Corporation",
    "is_active": true,
    "reliability_score": 0.95
  }' > /dev/null

# Create categories
echo "Creating categories..."
curl -s -X POST "http://localhost:8000/api/v1/categories" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Technology",
    "slug": "tech",
    "description": "Tech news"
  }' > /dev/null

# Create fresh news
echo "Creating fresh news..."
CURRENT_TIME=$(date -u +"%Y-%m-%dT%H:%M:%S")

for i in {1..5}; do
    curl -s -X POST "http://localhost:8000/api/v1/news" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"title\": \"Fresh News Article #$i - $(date +%s)\",
        \"content\": \"This is a fresh news article created at $CURRENT_TIME. It should appear in the /fresh endpoint.\",
        \"summary\": \"Fresh news #$i\",
        \"url\": \"https://example.com/news-$i-$(date +%s)\",
        \"source_id\": 1,
        \"category_id\": 1,
        \"published_at\": \"$CURRENT_TIME\",
        \"sentiment\": \"positive\",
        \"language\": \"en\"
      }" > /dev/null
    echo -n "."
done

echo -e "\n${GREEN}✅ Test data created${NC}"

# Test the fresh news API
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 Backend is ready!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}📊 Testing Fresh News API:${NC}\n"

# Test fresh news endpoint
echo -e "${YELLOW}GET /api/v1/news/fresh${NC}"
curl -s "http://localhost:8000/api/v1/news/fresh" | python3 -m json.tool

echo -e "\n\n${YELLOW}📋 Available Endpoints:${NC}"
echo "Fresh news:     http://localhost:8000/api/v1/news/fresh"
echo "All news:       http://localhost:8000/api/v1/news"
echo "Trending:       http://localhost:8000/api/v1/news/trending"
echo "API Docs:       http://localhost:8000/docs"
echo "Health:         http://localhost:8000/api/v1/health"

echo -e "\n${YELLOW}🛑 To stop the server:${NC}"
echo "kill $BACKEND_PID"

echo -e "\n${GREEN}✅ All done! Backend is running on http://localhost:8000${NC}"

# Keep script running
wait $BACKEND_PID
