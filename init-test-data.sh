#!/bin/bash

# Initialize test data for Smart News Aggregator
# This script creates test data including sources, categories, and news

set -e

echo "🔧 Initializing test data..."

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# API base URL
API_URL="http://localhost:8000/api/v1"

# First, create superuser (if not exists)
echo -e "\n${YELLOW}👤 Creating superuser...${NC}"
docker-compose exec -T backend python -c "
from app.db.session import SessionLocal
from app.db.init_db import init_db
import asyncio

async def main():
    async for db in SessionLocal():
        await init_db(db)
        break

asyncio.run(main())
" || echo "Superuser may already exist"

# Login and get token
echo -e "\n${YELLOW}🔑 Logging in as admin...${NC}"
TOKEN=$(curl -s -X POST "${API_URL}/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@smartnews.com",
    "password": "changethis"
  }' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}❌ Failed to get access token${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Got access token${NC}"

# Create sources
echo -e "\n${YELLOW}📰 Creating news sources...${NC}"

# BBC
curl -s -X POST "${API_URL}/sources" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "BBC News",
    "url": "https://www.bbc.com/news",
    "logo_url": "https://www.bbc.co.uk/favicon.ico",
    "description": "British Broadcasting Corporation",
    "is_active": true,
    "reliability_score": 0.95
  }' > /dev/null

# CNN
curl -s -X POST "${API_URL}/sources" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CNN",
    "url": "https://www.cnn.com",
    "logo_url": "https://www.cnn.com/favicon.ico",
    "description": "Cable News Network",
    "is_active": true,
    "reliability_score": 0.90
  }' > /dev/null

# Reuters
curl -s -X POST "${API_URL}/sources" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Reuters",
    "url": "https://www.reuters.com",
    "logo_url": "https://www.reuters.com/favicon.ico",
    "description": "International news agency",
    "is_active": true,
    "reliability_score": 0.98
  }' > /dev/null

echo -e "${GREEN}✅ Sources created${NC}"

# Create categories
echo -e "\n${YELLOW}📁 Creating categories...${NC}"

for category in "Technology:tech" "Business:business" "Politics:politics" "Sports:sports" "Entertainment:entertainment" "Science:science"; do
    IFS=':' read -r name slug <<< "$category"
    curl -s -X POST "${API_URL}/categories" \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d "{
        \"name\": \"$name\",
        \"slug\": \"$slug\",
        \"description\": \"News about $name\"
      }" > /dev/null
done

echo -e "${GREEN}✅ Categories created${NC}"

# Get source and category IDs
echo -e "\n${YELLOW}📋 Fetching source and category IDs...${NC}"
SOURCES=$(curl -s "${API_URL}/sources")
CATEGORIES=$(curl -s "${API_URL}/categories")

# Create sample news
echo -e "\n${YELLOW}📄 Creating sample news...${NC}"

# Get current datetime in ISO format
CURRENT_DATE=$(date -u +"%Y-%m-%dT%H:%M:%S")
YESTERDAY=$(date -u -d "1 day ago" +"%Y-%m-%dT%H:%M:%S")
TWO_HOURS_AGO=$(date -u -d "2 hours ago" +"%Y-%m-%dT%H:%M:%S")

# News 1 - Fresh tech news
curl -s -X POST "${API_URL}/news" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Breaking: New AI Model Surpasses GPT-4 Performance\",
    \"content\": \"A groundbreaking new AI model has been announced today, demonstrating superior performance across multiple benchmarks compared to GPT-4. The model, developed by researchers at leading tech institutions, shows remarkable improvements in reasoning and language understanding.\",
    \"summary\": \"New AI model outperforms GPT-4 in multiple benchmarks\",
    \"url\": \"https://example.com/ai-breakthrough-2025\",
    \"source_id\": 1,
    \"category_id\": 1,
    \"published_at\": \"${TWO_HOURS_AGO}\",
    \"sentiment\": \"positive\",
    \"language\": \"en\",
    \"image_url\": \"https://via.placeholder.com/800x400/0066cc/ffffff?text=AI+News\"
  }" > /dev/null

# News 2 - Fresh business news
curl -s -X POST "${API_URL}/news" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Major Tech Company Announces Record Quarterly Revenue\",
    \"content\": \"In a surprising turn of events, the company reported a 45% increase in quarterly revenue, beating analyst expectations by a significant margin. The strong performance was driven by cloud services and AI products.\",
    \"summary\": \"Tech giant reports 45% revenue increase in Q3 2025\",
    \"url\": \"https://example.com/tech-revenue-record\",
    \"source_id\": 2,
    \"category_id\": 2,
    \"published_at\": \"${TWO_HOURS_AGO}\",
    \"sentiment\": \"positive\",
    \"language\": \"en\",
    \"image_url\": \"https://via.placeholder.com/800x400/00cc66/ffffff?text=Business+News\"
  }" > /dev/null

# News 3 - Fresh politics news
curl -s -X POST "${API_URL}/news" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"International Climate Summit Reaches Historic Agreement\",
    \"content\": \"World leaders have signed a landmark climate agreement at the international summit, committing to ambitious carbon reduction targets. The agreement includes provisions for supporting developing nations in their transition to renewable energy.\",
    \"summary\": \"World leaders sign historic climate agreement\",
    \"url\": \"https://example.com/climate-summit-2025\",
    \"source_id\": 3,
    \"category_id\": 3,
    \"published_at\": \"${CURRENT_DATE}\",
    \"sentiment\": \"positive\",
    \"language\": \"en\",
    \"image_url\": \"https://via.placeholder.com/800x400/009966/ffffff?text=Politics\"
  }" > /dev/null

# News 4 - Fresh sports news
curl -s -X POST "${API_URL}/news" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Underdog Team Wins Championship in Stunning Upset\",
    \"content\": \"In what many are calling the greatest upset in sports history, the underdog team defeated the reigning champions in a thrilling final match. The victory came down to a last-minute play that left fans in disbelief.\",
    \"summary\": \"Underdog team wins championship against all odds\",
    \"url\": \"https://example.com/sports-upset-2025\",
    \"source_id\": 1,
    \"category_id\": 4,
    \"published_at\": \"${TWO_HOURS_AGO}\",
    \"sentiment\": \"positive\",
    \"language\": \"en\",
    \"image_url\": \"https://via.placeholder.com/800x400/cc6600/ffffff?text=Sports\"
  }" > /dev/null

# News 5 - Old news (yesterday)
curl -s -X POST "${API_URL}/news" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"title\": \"Yesterday's Technology Announcement\",
    \"content\": \"This news article was published yesterday and should not appear in the fresh news feed when filtering for 24 hours.\",
    \"summary\": \"Old news from yesterday\",
    \"url\": \"https://example.com/old-news-yesterday\",
    \"source_id\": 2,
    \"category_id\": 1,
    \"published_at\": \"${YESTERDAY}\",
    \"sentiment\": \"neutral\",
    \"language\": \"en\",
    \"image_url\": \"https://via.placeholder.com/800x400/666666/ffffff?text=Old+News\"
  }" > /dev/null

echo -e "${GREEN}✅ Sample news created${NC}"

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}✅ Test data initialized successfully!${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n${YELLOW}📊 Test the API:${NC}"
echo "Fresh news (last 24h):    curl http://localhost:8000/api/v1/news/fresh"
echo "Fresh news (last 6h):     curl http://localhost:8000/api/v1/news/fresh?hours=6"
echo "Tech fresh news:          curl http://localhost:8000/api/v1/news/fresh?category_id=1"
echo "All news:                 curl http://localhost:8000/api/v1/news"
echo "Trending news:            curl http://localhost:8000/api/v1/news/trending"
