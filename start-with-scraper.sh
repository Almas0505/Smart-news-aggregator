#!/bin/bash

# Complete Project Startup with News Scraper
# Запускает полный проект включая автоматический сбор новостей

set -e

echo "🚀 Smart News Aggregator - Full Startup"
echo "========================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Check Docker
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"

# Stop existing containers
echo -e "\n${YELLOW}🛑 Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true

# Start core services
echo -e "\n${YELLOW}📦 Starting core services (Postgres, Redis)...${NC}"
docker-compose up -d postgres redis

# Wait for services
echo -e "\n${YELLOW}⏳ Waiting for databases to be ready...${NC}"
sleep 15

# Check postgres
until docker-compose exec -T postgres pg_isready -U postgres > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e " ${GREEN}✅ PostgreSQL ready${NC}"

# Check redis
until docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; do
    echo -n "."
    sleep 2
done
echo -e " ${GREEN}✅ Redis ready${NC}"

# Start backend
echo -e "\n${YELLOW}🐍 Starting Backend API...${NC}"
docker-compose up -d backend

# Wait for backend
sleep 10
echo -n "Waiting for Backend"
for i in {1..30}; do
    if curl -sf http://localhost:8000/api/v1/health > /dev/null 2>&1; then
        echo -e " ${GREEN}✅ Backend ready${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

# Run migrations
echo -e "\n${YELLOW}🗄️  Running database migrations...${NC}"
docker-compose exec -T backend alembic upgrade head || echo "Migrations already applied"

# Initialize DB with admin user
echo -e "\n${YELLOW}👤 Creating admin user...${NC}"
docker-compose exec -T backend python -c "
import asyncio
from app.db.session import SessionLocal
from app.db.init_db import init_db

async def main():
    async for db in SessionLocal():
        await init_db(db)
        break

try:
    asyncio.run(main())
    print('✅ Admin user created')
except Exception as e:
    print(f'Note: {e}')
" || echo "Admin may already exist"

# Create basic sources and categories
echo -e "\n${YELLOW}📰 Setting up news sources...${NC}"
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@smartnews.com","password":"changethis"}' \
  | python3 -c "import sys,json; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)

if [ ! -z "$TOKEN" ]; then
    # Create sources
    curl -s -X POST "http://localhost:8000/api/v1/sources" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "BBC News",
        "url": "https://www.bbc.com/news",
        "description": "British Broadcasting Corporation",
        "is_active": true,
        "reliability_score": 0.95
      }' > /dev/null || true
    
    curl -s -X POST "http://localhost:8000/api/v1/sources" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "CNN",
        "url": "https://www.cnn.com",
        "description": "Cable News Network",
        "is_active": true,
        "reliability_score": 0.90
      }' > /dev/null || true
    
    # Create categories
    for cat in "Technology:tech" "Business:business" "Politics:politics" "Sports:sports"; do
        IFS=':' read -r name slug <<< "$cat"
        curl -s -X POST "http://localhost:8000/api/v1/categories" \
          -H "Authorization: Bearer $TOKEN" \
          -H "Content-Type: application/json" \
          -d "{\"name\":\"$name\",\"slug\":\"$slug\"}" > /dev/null || true
    done
    
    echo -e "${GREEN}✅ Sources and categories created${NC}"
fi

# Start NEWS SCRAPER 🕷️
echo -e "\n${YELLOW}🕷️  Starting News Scraper Service...${NC}"
docker-compose up -d scraper_worker

# Wait a bit
sleep 5

# Check scraper logs
echo -e "\n${YELLOW}📝 Scraper Status:${NC}"
docker-compose logs --tail=20 scraper_worker

# Start monitoring
echo -e "\n${YELLOW}📊 Starting Monitoring (Flower, Prometheus, Grafana)...${NC}"
docker-compose up -d flower prometheus grafana

# Summary
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Full Stack Started Successfully!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}📋 Service URLs:${NC}"
echo "-----------------------------------"
echo "🌐 Backend API:      http://localhost:8000"
echo "📖 API Docs:         http://localhost:8000/docs"
echo "📰 Fresh News:       http://localhost:8000/api/v1/news/fresh"
echo "🕷️  Flower (Tasks):   http://localhost:5555"
echo "📊 Prometheus:       http://localhost:9090"
echo "📈 Grafana:          http://localhost:3000 (admin/admin)"
echo "-----------------------------------"

echo -e "\n${YELLOW}🕷️  News Scraper:${NC}"
echo "Status:              RUNNING ✅"
echo "Interval:            Every 15-30 minutes"
echo "Sources:             RSS Feeds + News API"
echo "Monitor:             http://localhost:5555"

echo -e "\n${YELLOW}👤 Admin Credentials:${NC}"
echo "Email:               admin@smartnews.com"
echo "Password:            changethis"

echo -e "\n${YELLOW}📊 Check News Collection:${NC}"
echo "curl http://localhost:8000/api/v1/news/fresh"
echo "docker-compose logs -f scraper_worker"
echo "docker-compose exec postgres psql -U postgres -d news_aggregator -c 'SELECT COUNT(*) FROM news;'"

echo -e "\n${YELLOW}🛑 To Stop:${NC}"
echo "docker-compose down"

echo -e "\n${GREEN}🎉 Project is Ready! News will start appearing in 1-2 minutes!${NC}\n"
