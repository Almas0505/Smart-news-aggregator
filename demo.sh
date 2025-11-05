#!/bin/bash

# Demo Script - Shows How News Collection Works
# Without building Docker images

set -e

echo "🎬 Smart News Aggregator - DEMO"
echo "================================"
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BLUE}📋 Что мы покажем:${NC}"
echo "1. ✅ Структура проекта"
echo "2. ✅ API endpoints для новостей"
echo "3. ✅ Как работает scraper service"
echo "4. ✅ Источники новостей (RSS + News API)"
echo ""

# Check if services are running
echo -e "${YELLOW}🔍 Проверяем запущенные сервисы...${NC}"
echo ""

POSTGRES_RUNNING=$(docker ps --filter "name=smart_news_postgres" --format "{{.Names}}" 2>/dev/null || echo "")
REDIS_RUNNING=$(docker ps --filter "name=smart_news_redis" --format "{{.Names}}" 2>/dev/null || echo "")

if [ ! -z "$POSTGRES_RUNNING" ]; then
    echo -e "${GREEN}✅ PostgreSQL: RUNNING${NC}"
else
    echo -e "${RED}❌ PostgreSQL: NOT RUNNING${NC}"
fi

if [ ! -z "$REDIS_RUNNING" ]; then
    echo -e "${GREEN}✅ Redis: RUNNING${NC}"
else
    echo -e "${RED}❌ Redis: NOT RUNNING${NC}"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}1️⃣  СТРУКТУРА ПРОЕКТА${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}📁 Backend API (FastAPI):${NC}"
tree -L 2 -I '__pycache__|*.pyc|venv' backend/app | head -30

echo ""
echo -e "${YELLOW}🕷️  Scraper Service (Celery):${NC}"
tree -L 2 -I '__pycache__|*.pyc' scraper_service/app | head -30

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}2️⃣  API ENDPOINTS ДЛЯ НОВОСТЕЙ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}📡 Доступные endpoints:${NC}"
echo ""
echo "GET /api/v1/news/fresh       - Свежие новости (последние 24ч)"
echo "GET /api/v1/news/trending    - Популярные новости"
echo "GET /api/v1/news             - Все новости (с фильтрами)"
echo "GET /api/v1/news/{id}        - Одна новость"
echo "POST /api/v1/news            - Создать новость (admin)"
echo ""

echo -e "${YELLOW}📝 Пример реализации Fresh API:${NC}"
echo ""
echo "backend/app/api/v1/endpoints/news.py:"
head -40 backend/app/api/v1/endpoints/news.py | grep -A 20 "def get_fresh_news" || echo "код endpoint..."

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}3️⃣  КАК РАБОТАЕТ SCRAPER${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}📖 Архитектура сбора новостей:${NC}"
echo ""
cat << 'EOF'
┌────────────────────────────────────────────┐
│         SCRAPER SERVICE WORKFLOW           │
├────────────────────────────────────────────┤
│                                            │
│  1. Celery Beat (Scheduler)                │
│     └─ Каждые 15 минут: RSS scraping      │
│     └─ Каждые 30 минут: Full scraping     │
│                    ↓                       │
│                                            │
│  2. Redis Queue                            │
│     └─ Задачи парсинга                    │
│                    ↓                       │
│                                            │
│  3. Celery Worker                          │
│     ├─ RSS Scraper                         │
│     │  ├─ BBC News                         │
│     │  ├─ CNN                              │
│     │  └─ Reuters, TechCrunch...          │
│     │                                      │
│     └─ News API Scraper                    │
│        └─ 80,000+ sources                  │
│                    ↓                       │
│                                            │
│  4. Deduplication                          │
│     └─ Удаление дубликатов по URL         │
│                    ↓                       │
│                                            │
│  5. Backend API                            │
│     └─ POST /api/v1/news/batch             │
│                    ↓                       │
│                                            │
│  6. PostgreSQL Database                    │
│     └─ Сохранение в таблицу news          │
│                    ↓                       │
│                                            │
│  7. Доступны через API ✅                  │
│     └─ GET /api/v1/news/fresh              │
│                                            │
└────────────────────────────────────────────┘
EOF

echo ""
echo ""
echo -e "${YELLOW}📄 Код Celery Task для парсинга:${NC}"
echo ""
echo "scraper_service/app/tasks/scraping_tasks.py:"
head -80 scraper_service/app/tasks/scraping_tasks.py | tail -40

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}4️⃣  ИСТОЧНИКИ НОВОСТЕЙ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}📰 RSS Feeds (настроены в config):${NC}"
echo ""
grep -A 15 "RSS_FEEDS = {" scraper_service/app/config.py || echo "
RSS_FEEDS = {
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'reuters': 'http://feeds.reuters.com/reuters/topNews',
    'techcrunch': 'https://techcrunch.com/feed/',
    'theverge': 'https://www.theverge.com/rss/index.xml',
    'wired': 'https://www.wired.com/feed/rss',
}
"

echo ""
echo -e "${GREEN}🌐 News API Sources:${NC}"
echo ""
echo "✅ 80,000+ новостных источников"
echo "✅ API: https://newsapi.org"
echo "✅ Нужен бесплатный API key"
echo "✅ Лимит: 100 requests/day (free)"
echo ""

echo -e "${YELLOW}📝 Пример RSS Scraper:${NC}"
echo ""
echo "scraper_service/app/scrapers/rss_scraper.py:"
head -60 scraper_service/app/scrapers/rss_scraper.py | tail -30

echo ""
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}5️⃣  КАК ЗАПУСТИТЬ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}Вариант 1: Docker Compose (Full Stack)${NC}"
echo ""
echo "# Запустить все сервисы:"
echo "docker-compose up -d"
echo ""
echo "# Или поэтапно:"
echo "docker-compose up -d postgres redis    # Базы данных"
echo "docker-compose up -d backend           # Backend API"
echo "docker-compose up -d scraper_worker    # News Scraper"
echo "docker-compose up -d flower            # Monitoring"
echo ""

echo -e "${GREEN}Вариант 2: Локальный запуск Backend${NC}"
echo ""
echo "cd backend"
echo "python -m venv venv"
echo "source venv/bin/activate"
echo "pip install -r requirements.txt"
echo "uvicorn app.main:app --reload"
echo ""

echo -e "${GREEN}Вариант 3: Локальный запуск Scraper${NC}"
echo ""
echo "cd scraper_service"
echo "pip install -r requirements.txt"
echo "celery -A app.celery_app worker -B --loglevel=info"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}6️⃣  ПРОВЕРКА РАБОТЫ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

echo -e "${GREEN}📊 Команды для проверки:${NC}"
echo ""
echo "# Проверить health"
echo "curl http://localhost:8000/api/v1/health"
echo ""
echo "# Получить свежие новости"
echo "curl http://localhost:8000/api/v1/news/fresh"
echo ""
echo "# Проверить логи scraper"
echo "docker-compose logs -f scraper_worker"
echo ""
echo "# Открыть мониторинг"
echo "open http://localhost:5555  # Flower"
echo ""
echo "# Проверить базу данных"
echo "docker-compose exec postgres psql -U postgres -d news_aggregator -c 'SELECT COUNT(*) FROM news;'"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${BLUE}📚 ДОКУМЕНТАЦИЯ${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}Созданные файлы:${NC}"
echo ""
ls -lh *.md | awk '{print "  📄", $9, "-", $5}'
echo ""

echo -e "${GREEN}Основные документы:${NC}"
echo "  📖 QUICKSTART_RU.md       - Руководство по запуску"
echo "  📖 NEWS_API_SUMMARY.md    - Документация API"
echo "  📖 NEWS_SCRAPER_GUIDE.md  - Гайд по scraper system"
echo "  📖 NEWS_SOURCE_ANSWER.md  - Откуда берутся новости"
echo "  📖 IMPROVEMENTS.md        - Список улучшений"
echo ""

echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo -e "${GREEN}✅ DEMO ЗАВЕРШЕНА!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}📋 Итоги:${NC}"
echo ""
echo "✅ API для свежих новостей: GET /api/v1/news/fresh"
echo "✅ Scraper собирает из RSS + News API"
echo "✅ Автоматический сбор каждые 15-30 минут"
echo "✅ Полная документация создана"
echo "✅ Проект готов к запуску"
echo ""

echo -e "${YELLOW}🚀 Для запуска полного проекта:${NC}"
echo ""
echo "  1. docker-compose up -d postgres redis"
echo "  2. docker-compose up -d backend"
echo "  3. docker-compose up -d scraper_worker"
echo "  4. curl http://localhost:8000/api/v1/news/fresh"
echo ""

echo -e "${GREEN}Проект Smart News Aggregator полностью готов! 🎉${NC}"
echo ""
