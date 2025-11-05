#!/bin/bash

# Quick Info - Show running services and ports

echo "🚀 Smart News Aggregator - Статус Сервисов"
echo "==========================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}📊 Запущенные Docker контейнеры:${NC}"
echo ""
docker ps --filter "name=smart_news" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" || echo "Нет запущенных контейнеров"

echo ""
echo -e "${BLUE}🔌 Доступные порты:${NC}"
echo ""

# Check each service
check_port() {
    local port=$1
    local service=$2
    if nc -z localhost $port 2>/dev/null; then
        echo -e "${GREEN}✅ $service - http://localhost:$port${NC}"
        return 0
    else
        echo -e "${YELLOW}⏳ $service - порт $port (еще не готов)${NC}"
        return 1
    fi
}

# Check PostgreSQL
if docker ps | grep -q "smart_news_postgres"; then
    echo -e "${GREEN}✅ PostgreSQL - порт 5432 (RUNNING)${NC}"
else
    echo -e "${YELLOW}⏳ PostgreSQL - порт 5432${NC}"
fi

# Check Redis
if docker ps | grep -q "smart_news_redis"; then
    echo -e "${GREEN}✅ Redis - порт 6379 (RUNNING)${NC}"
else
    echo -e "${YELLOW}⏳ Redis - порт 6379${NC}"
fi

echo ""

# Check Backend
if docker ps | grep -q "smart_news_backend"; then
    echo -e "${GREEN}✅ Backend API - http://localhost:8000${NC}"
    echo -e "${GREEN}   📖 Swagger Docs - http://localhost:8000/docs${NC}"
    echo -e "${GREEN}   📰 Fresh News - http://localhost:8000/api/v1/news/fresh${NC}"
else
    echo -e "${YELLOW}⏳ Backend API - порт 8000 (building...)${NC}"
    echo ""
    echo -e "${BLUE}💡 Backend строится. Это может занять 2-5 минут.${NC}"
    echo -e "${BLUE}   Проверьте статус: docker-compose logs -f backend${NC}"
fi

echo ""
echo -e "${BLUE}🛠️  Полезные команды:${NC}"
echo ""
echo "# Проверить логи backend:"
echo "docker-compose logs -f backend"
echo ""
echo "# Проверить статус всех сервисов:"
echo "docker-compose ps"
echo ""
echo "# Остановить все:"
echo "docker-compose down"
echo ""
echo "# Перезапустить backend:"
echo "docker-compose restart backend"
echo ""

echo -e "${BLUE}📚 Документация:${NC}"
echo ""
echo "QUICKSTART_RU.md       - Руководство по запуску"
echo "NEWS_API_SUMMARY.md    - API документация"
echo "NEWS_SCRAPER_GUIDE.md  - Система сбора новостей"
echo ""

echo -e "${YELLOW}⏳ Если backend еще строится, подождите 2-3 минуты...${NC}"
echo ""
