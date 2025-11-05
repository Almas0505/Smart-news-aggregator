# 🚀 Руководство по Запуску Smart News Aggregator

## Быстрый Старт

### Вариант 1: Запуск через Docker Compose (Рекомендуется)

#### Требования:
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM минимум
- 10GB свободного места

#### Шаги:

1. **Клонировать репозиторий:**
```bash
git clone https://github.com/Almas0505/Smart-news-aggregator.git
cd Smart-news-aggregator
```

2. **Создать .env файл для backend:**
```bash
cd backend
cp .env.example .env
# Отредактировать .env при необходимости
cd ..
```

3. **Запустить все сервисы:**
```bash
# Вариант A: Полный стек (все сервисы)
docker-compose up -d

# Вариант B: Только backend для тестирования
docker-compose up -d postgres redis backend
```

4. **Дождаться готовности сервисов:**
```bash
# Проверить статус
docker-compose ps

# Посмотреть логи
docker-compose logs -f backend
```

5. **Инициализировать базу данных:**
```bash
# Применить миграции
docker-compose exec backend alembic upgrade head

# Создать админ пользователя (автоматически при первом запуске)
# Email: admin@smartnews.com
# Password: changethis
```

6. **Протестировать API:**
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Получить fresh новости
curl http://localhost:8000/api/v1/news/fresh

# Открыть документацию
open http://localhost:8000/docs
```

---

### Вариант 2: Ручной Запуск (Для Разработки)

#### Требования:
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- pip

#### Шаги:

1. **Запустить базы данных:**
```bash
# Только postgres и redis через docker
docker-compose up -d postgres redis
```

2. **Настроить Python окружение:**
```bash
cd backend

# Создать virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установить зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

3. **Настроить .env для локального запуска:**
```bash
cat > .env.local << EOF
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=news_aggregator
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/news_aggregator

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_URL=redis://localhost:6379/0

SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
DEBUG=True
EOF

# Экспортировать переменные
export $(grep -v '^#' .env.local | xargs)
```

4. **Запустить миграции:**
```bash
alembic upgrade head
```

5. **Запустить сервер:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

6. **В другом терминале - создать тестовые данные:**
```bash
# Запустить скрипт инициализации
python scripts/init_test_data.py
```

---

## 📡 API Endpoints для Новостей

### 1. **GET /api/v1/news/fresh** - Свежие новости ⭐

Получить свежие новости за указанный период времени.

**Параметры:**
- `hours` (int, optional) - Окно времени в часах (по умолчанию 24, максимум 168 = 7 дней)
- `limit` (int, optional) - Количество новостей (по умолчанию 20, максимум 100)
- `category_id` (int, optional) - Фильтр по категории

**Примеры:**
```bash
# Свежие новости за последние 24 часа
curl http://localhost:8000/api/v1/news/fresh

# За последние 6 часов
curl http://localhost:8000/api/v1/news/fresh?hours=6

# Ограничение до 10 новостей
curl http://localhost:8000/api/v1/news/fresh?limit=10

# Только технологические новости за последние 12 часов
curl "http://localhost:8000/api/v1/news/fresh?hours=12&category_id=1&limit=5"

# С форматированием JSON
curl http://localhost:8000/api/v1/news/fresh | jq .
```

**Ответ:**
```json
[
  {
    "id": 1,
    "title": "Breaking: New AI Model Surpasses GPT-4",
    "summary": "Revolutionary AI breakthrough...",
    "url": "https://example.com/article",
    "published_at": "2025-10-20T15:30:00Z",
    "source": {
      "id": 1,
      "name": "BBC News"
    },
    "category": {
      "id": 1,
      "name": "Technology"
    },
    "sentiment": "positive",
    "views_count": 1523
  }
]
```

---

### 2. **GET /api/v1/news** - Все новости с фильтрами

Получить список новостей с пагинацией и фильтрами.

**Параметры:**
- `skip` (int) - Пропустить N новостей (по умолчанию 0)
- `limit` (int) - Количество новостей (по умолчанию 20, max 100)
- `category_id` (int, optional) - Фильтр по категории
- `source_id` (int, optional) - Фильтр по источнику
- `sentiment` (string, optional) - Фильтр по настроению (positive/negative/neutral)

**Примеры:**
```bash
# Первая страница (20 новостей)
curl "http://localhost:8000/api/v1/news?skip=0&limit=20"

# Только позитивные новости
curl "http://localhost:8000/api/v1/news?sentiment=positive"

# Новости из BBC
curl "http://localhost:8000/api/v1/news?source_id=1"
```

---

### 3. **GET /api/v1/news/trending** - Популярные новости

Получить популярные новости за последние 24 часа.

**Параметры:**
- `limit` (int) - Количество новостей (по умолчанию 10, max 50)

**Примеры:**
```bash
# Топ 10 популярных новостей
curl http://localhost:8000/api/v1/news/trending

# Топ 5
curl "http://localhost:8000/api/v1/news/trending?limit=5"
```

---

### 4. **GET /api/v1/news/{id}** - Одна новость

Получить детальную информацию о конкретной новости.

**Примеры:**
```bash
# Получить новость с ID=1
curl http://localhost:8000/api/v1/news/1

# С подробностями
curl http://localhost:8000/api/v1/news/1 | jq .
```

---

### 5. **POST /api/v1/news** - Создать новость (Admin Only)

Создать новую новость (требуется авторизация администратора).

**Примеры:**
```bash
# 1. Получить токен
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@smartnews.com","password":"changethis"}' \
  | jq -r '.access_token')

# 2. Создать новость
curl -X POST "http://localhost:8000/api/v1/news" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New Article Title",
    "content": "Full article content here...",
    "summary": "Brief summary",
    "url": "https://example.com/article",
    "source_id": 1,
    "category_id": 1,
    "published_at": "2025-10-20T15:00:00Z",
    "sentiment": "positive",
    "language": "en"
  }'
```

---

## 🧪 Тестирование Fresh API

### Создать Тестовые Данные:

```python
# scripts/create_test_news.py
import requests
from datetime import datetime, timedelta

API_URL = "http://localhost:8000/api/v1"

# 1. Login
response = requests.post(f"{API_URL}/auth/login", json={
    "email": "admin@smartnews.com",
    "password": "changethis"
})
token = response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Create fresh news
now = datetime.utcnow()
for i in range(5):
    requests.post(f"{API_URL}/news", headers=headers, json={
        "title": f"Fresh News #{i+1}",
        "content": f"Content for news {i+1}",
        "summary": f"Summary {i+1}",
        "url": f"https://example.com/news-{i+1}",
        "source_id": 1,
        "category_id": 1,
        "published_at": (now - timedelta(hours=i)).isoformat() + "Z",
        "sentiment": "positive",
        "language": "en"
    })

print("✅ Created 5 fresh news articles!")

# 3. Test fresh API
response = requests.get(f"{API_URL}/news/fresh?hours=24&limit=10")
print(f"\n📰 Fresh news count: {len(response.json())}")
for news in response.json():
    print(f"  - {news['title']} ({news['published_at']})")
```

Запуск:
```bash
python scripts/create_test_news.py
```

---

## 📊 Мониторинг и Метрики

После запуска доступны:

- **API Docs**: http://localhost:8000/docs
- **Prometheus Metrics**: http://localhost:8000/metrics
- **Health Check**: http://localhost:8000/api/v1/health

---

## 🐛 Troubleshooting

### Backend не запускается

```bash
# Проверить логи
docker-compose logs backend

# Проверить подключение к базе
docker-compose exec postgres psql -U postgres -d news_aggregator -c "SELECT 1;"

# Пересоздать контейнеры
docker-compose down -v
docker-compose up -d
```

### Fresh API возвращает пустой массив

```bash
# 1. Проверить есть ли новости в БД
docker-compose exec postgres psql -U postgres -d news_aggregator -c \
  "SELECT id, title, published_at FROM news ORDER BY published_at DESC LIMIT 5;"

# 2. Создать тестовые новости через API (см. выше)

# 3. Проверить фильтр по времени
curl "http://localhost:8000/api/v1/news/fresh?hours=168"  # 7 дней
```

### Ошибки авторизации

```bash
# Пересоздать админ пользователя
docker-compose exec backend python -c "
import asyncio
from app.db.session import SessionLocal
from app.db.init_db import init_db

async def main():
    async for db in SessionLocal():
        await init_db(db)
        break

asyncio.run(main())
"
```

---

## 📝 Полезные Команды

```bash
# Просмотр всех эндпоинтов
curl http://localhost:8000/openapi.json | jq '.paths | keys'

# Статистика БД
docker-compose exec postgres psql -U postgres -d news_aggregator -c \
  "SELECT 
    (SELECT COUNT(*) FROM news) as total_news,
    (SELECT COUNT(*) FROM news WHERE published_at > NOW() - INTERVAL '24 hours') as fresh_news_24h,
    (SELECT COUNT(*) FROM sources) as sources,
    (SELECT COUNT(*) FROM categories) as categories;"

# Очистить кэш Redis
docker-compose exec redis redis-cli FLUSHALL

# Перезапустить только backend
docker-compose restart backend

# Просмотр метрик
curl http://localhost:8000/metrics | grep http_requests_total
```

---

## ✅ Проверка Работоспособности

```bash
# 1. Health check
curl http://localhost:8000/api/v1/health
# Ожидается: {"status": "healthy"}

# 2. Fresh news
curl http://localhost:8000/api/v1/news/fresh
# Ожидается: JSON массив новостей

# 3. API docs
curl -I http://localhost:8000/docs
# Ожидается: HTTP/1.1 200 OK
```

---

## 🎯 Итог

API для свежих новостей полностью реализован и готов к использованию!

**Ключевые моменты:**
- ✅ Endpoint `/api/v1/news/fresh` реализован
- ✅ Поддерживает фильтры по времени, категориям и лимиту
- ✅ Возвращает новости отсортированные по дате (новейшие первыми)
- ✅ Использует кэширование для оптимизации
- ✅ Полная документация доступна в Swagger UI

**Следующие шаги:**
1. Настроить scraper для автоматического сбора новостей
2. Интегрировать Elasticsearch для полнотекстового поиска
3. Добавить real-time обновления через WebSockets
4. Настроить мониторинг и алерты

---

**Автор**: AI Assistant  
**Дата**: 20 октября 2025  
**Версия**: 1.0
