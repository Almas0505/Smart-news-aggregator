# 🕷️ Как Работает Сбор Новостей - Smart News Aggregator

## 📌 Откуда Берутся Новости?

Система использует **2 основных источника** для сбора новостей:

### 1. **RSS Feeds** (Основной источник) 📰
- Бесплатный и надежный
- Официальные новостные ленты от сайтов
- Обновляются каждые **15 минут**
- Автоматический парсинг XML

### 2. **News API** (Дополнительный) 🌐
- Агрегатор от 80,000+ источников
- Требует API key (бесплатно 100 запросов/день)
- Обновляется каждые **30 минут**
- REST API интеграция

---

## 🏗️ Архитектура Системы Сбора

```
┌──────────────────────────────────────────────────────┐
│                  SCRAPER SERVICE                      │
│                                                       │
│  ┌─────────────┐         ┌─────────────┐            │
│  │   Celery    │────────▶│   Redis     │            │
│  │   Beat      │ Tasks   │   Broker    │            │
│  │ (Scheduler) │         └─────────────┘            │
│  └─────────────┘                │                    │
│                                  │                    │
│                                  ▼                    │
│                         ┌──────────────┐             │
│                         │ Celery Worker│             │
│                         └──────────────┘             │
│                                  │                    │
│         ┌────────────────────────┼──────────┐        │
│         │                        │          │        │
│         ▼                        ▼          ▼        │
│  ┌────────────┐         ┌────────────┐  ┌────────┐  │
│  │ RSS Scraper│         │ API Scraper│  │ Others │  │
│  └────────────┘         └────────────┘  └────────┘  │
│         │                        │                    │
│         └────────────┬───────────┘                    │
│                      │                                │
│                      ▼                                │
│              ┌──────────────┐                        │
│              │ Deduplication│                        │
│              └──────────────┘                        │
│                      │                                │
│                      ▼                                │
│              ┌──────────────┐                        │
│              │ Send to API  │                        │
│              └──────────────┘                        │
└──────────────────────┼───────────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │    BACKEND API          │
         │  POST /api/v1/news/batch│
         └─────────────────────────┘
                       │
                       ▼
         ┌─────────────────────────┐
         │    PostgreSQL           │
         │  (News Database)        │
         └─────────────────────────┘
```

---

## ⚙️ Как Это Работает

### 1. **Scheduler (Celery Beat)**
- Запускается автоматически при старте
- Каждые **15 минут** запускает RSS scraping
- Каждые **30 минут** запускает полный scraping (RSS + API)
- Настройки в `scraper_service/app/celery_app.py`

### 2. **Workers (Celery Workers)**
- Получают задачи из Redis queue
- Выполняют парсинг параллельно
- Обрабатывают ошибки и retry
- Логируют все операции

### 3. **RSS Scraper**
**Файл:** `scraper_service/app/scrapers/rss_scraper.py`

**Что делает:**
```python
# 1. Загружает RSS feed
feed = feedparser.parse('http://feeds.bbci.co.uk/news/rss.xml')

# 2. Парсит каждую статью
for entry in feed.entries:
    article = Article(
        title=entry.title,
        url=entry.link,
        content=entry.description,
        published_at=entry.published_parsed
    )

# 3. Возвращает список статей
return articles
```

**Источники RSS:**
- BBC News
- CNN
- Reuters
- TechCrunch
- The Verge
- Wired
- (настраиваются в config.py)

### 4. **News API Scraper**
**Файл:** `scraper_service/app/scrapers/api_scraper.py`

**Что делает:**
```python
# 1. Подключается к News API
client = NewsApiClient(api_key=settings.NEWS_API_KEY)

# 2. Получает top headlines
response = client.get_top_headlines(
    sources='bbc-news,cnn,techcrunch',
    language='en',
    page_size=100
)

# 3. Конвертирует в Article objects
articles = [parse_article(item) for item in response['articles']]

# 4. Возвращает статьи
return articles
```

### 5. **Deduplication (Удаление дубликатов)**
```python
# Проверка по URL и content hash
seen_urls = set()
unique_articles = []

for article in articles:
    if article.url not in seen_urls:
        unique_articles.append(article)
        seen_urls.add(article.url)
```

### 6. **Отправка в Backend**
```python
# Отправка batch запросом
response = requests.post(
    'http://backend:8000/api/v1/news/batch',
    json={'articles': articles}
)
```

---

## 🚀 Как Запустить Scraper

### Вариант 1: Через Docker Compose (Рекомендуется)

```bash
cd /mnt/c/Projects/smart-news-aggregator

# 1. Запустить scraper worker
docker-compose up -d scraper_worker

# 2. Проверить логи
docker-compose logs -f scraper_worker

# 3. Проверить статус через Flower (web UI)
docker-compose up -d flower
open http://localhost:5555
```

### Вариант 2: Локальный Запуск

```bash
cd scraper_service

# 1. Установить зависимости
pip install -r requirements.txt

# 2. Настроить .env
export CELERY_BROKER_URL="redis://localhost:6379/0"
export BACKEND_URL="http://localhost:8000"
export NEWS_API_KEY="your-api-key-here"

# 3. Запустить worker + beat
celery -A app.celery_app worker -B --loglevel=info
```

### Вариант 3: Ручной Запуск Задачи

```python
# В Python shell или скрипте
from scraper_service.app.tasks.scraping_tasks import scrape_all_sources

# Запустить парсинг сейчас
result = scrape_all_sources.delay()

# Проверить статус
print(result.status)  # PENDING, STARTED, SUCCESS

# Получить результат
stats = result.get(timeout=600)
print(stats)
# Output:
# {
#     'total_articles': 150,
#     'rss_articles': 100,
#     'api_articles': 50,
#     'sent_to_backend': 145,
#     'errors': 5
# }
```

---

## 🔧 Настройка Источников

### Добавить RSS Feed

**Файл:** `scraper_service/app/config.py`

```python
RSS_FEEDS = {
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    'techcrunch': 'https://techcrunch.com/feed/',
    
    # Добавить новый источник:
    'your_source': 'https://your-site.com/rss.xml'
}
```

### Добавить News API Source

```python
NEWS_API_SOURCES = [
    'bbc-news',
    'cnn',
    'techcrunch',
    'the-verge',
    
    # Добавить новый:
    'your-source-id'  # ID из newsapi.org/sources
]
```

### Настроить Интервал Парсинга

```python
# В celery_app.py

app.conf.beat_schedule = {
    'scrape-all-sources': {
        'task': 'app.tasks.scraping_tasks.scrape_all_sources',
        'schedule': 30 * 60.0,  # Изменить на нужный интервал (в секундах)
    },
}
```

---

## 📊 Мониторинг Scraper

### 1. Flower Web UI

```bash
# Запустить Flower
docker-compose up -d flower

# Открыть в браузере
open http://localhost:5555
```

**Возможности Flower:**
- ✅ Просмотр активных задач
- ✅ История выполнения
- ✅ Статистика успеха/ошибок
- ✅ Графики производительности
- ✅ Управление workers

### 2. Логи

```bash
# Просмотр логов scraper
docker-compose logs -f scraper_worker

# Фильтрация по уровню
docker-compose logs scraper_worker | grep ERROR

# Последние 100 строк
docker-compose logs --tail=100 scraper_worker
```

### 3. Redis CLI

```bash
# Проверить очередь задач
docker-compose exec redis redis-cli

> KEYS celery*
> LLEN celery  # Количество задач в очереди
```

---

## 🧪 Тестирование Scraper

### Тест 1: Запустить Парсинг Вручную

```bash
# Создать скрипт test_scraper.py
cat > test_scraper.py << 'EOF'
from scraper_service.app.tasks.scraping_tasks import scrape_all_sources
import time

print("Starting scrape...")
task = scrape_all_sources.delay()
print(f"Task ID: {task.id}")

while task.status != 'SUCCESS':
    print(f"Status: {task.status}")
    if task.status == 'FAILURE':
        print(f"Error: {task.result}")
        break
    time.sleep(5)

if task.status == 'SUCCESS':
    stats = task.result
    print("\n✅ Scrape Complete!")
    print(f"Total articles: {stats['total_articles']}")
    print(f"Sent to backend: {stats['sent_to_backend']}")
EOF

python test_scraper.py
```

### Тест 2: Проверить RSS Parser

```bash
cat > test_rss.py << 'EOF'
from scraper_service.app.scrapers.rss_scraper import RSSFeedScraper

# Парсим BBC RSS
scraper = RSSFeedScraper(
    source_name='bbc',
    feed_url='http://feeds.bbci.co.uk/news/rss.xml'
)

articles = scraper.run()
print(f"Parsed {len(articles)} articles from BBC")

for article in articles[:5]:  # Первые 5
    print(f"\n- {article.title}")
    print(f"  URL: {article.url}")
    print(f"  Published: {article.published_at}")
EOF

python test_rss.py
```

### Тест 3: Проверить News API

```bash
cat > test_newsapi.py << 'EOF'
from scraper_service.app.scrapers.api_scraper import NewsAPIScraper
import os

# Установить API key
os.environ['NEWS_API_KEY'] = 'your-api-key-here'

scraper = NewsAPIScraper(
    sources=['bbc-news', 'cnn']
)

articles = scraper.run()
print(f"Parsed {len(articles)} articles from News API")

for article in articles[:5]:
    print(f"\n- {article.title}")
    print(f"  Source: {article.source}")
EOF

python test_newsapi.py
```

---

## 🔑 Получить News API Key

1. **Перейти на сайт:**
   https://newsapi.org

2. **Зарегистрироваться:**
   - Email
   - Password
   - Выбрать Free план

3. **Получить API Key:**
   - После регистрации → Dashboard
   - Скопировать API Key

4. **Добавить в .env:**
   ```bash
   # scraper_service/.env
   NEWS_API_KEY=your-api-key-here
   ```

**Лимиты Free плана:**
- 100 запросов/день
- Только последние 30 дней
- Задержка ~15 минут

---

## 📈 Ожидаемые Результаты

### При Успешном Запуске:

**Логи scraper_worker:**
```
[2025-10-20 15:00:00] INFO: ============================================================
[2025-10-20 15:00:00] INFO: STARTING FULL SCRAPE
[2025-10-20 15:00:00] INFO: ============================================================
[2025-10-20 15:00:01] INFO: 1/2 Scraping RSS feeds...
[2025-10-20 15:00:05] INFO: Fetched 45 articles from bbc
[2025-10-20 15:00:08] INFO: Fetched 38 articles from cnn
[2025-10-20 15:00:12] INFO: ✅ RSS: 83 articles
[2025-10-20 15:00:13] INFO: 2/2 Scraping News API...
[2025-10-20 15:00:18] INFO: ✅ News API: 67 articles
[2025-10-20 15:00:19] INFO: Processing 150 articles...
[2025-10-20 15:00:20] INFO: After dedup: 145 unique articles
[2025-10-20 15:00:25] INFO: ✅ Sent 145 articles to backend
[2025-10-20 15:00:25] INFO: ============================================================
[2025-10-20 15:00:25] INFO: SCRAPE COMPLETE
[2025-10-20 15:00:25] INFO: Total: 150 | Sent: 145 | Errors: 0
[2025-10-20 15:00:25] INFO: ============================================================
```

### В Базе Данных:

```bash
# Проверить количество новостей
docker-compose exec postgres psql -U postgres -d news_aggregator -c \
  "SELECT COUNT(*) FROM news;"

# Последние новости
docker-compose exec postgres psql -U postgres -d news_aggregator -c \
  "SELECT title, source, published_at FROM news ORDER BY published_at DESC LIMIT 5;"
```

### Через API:

```bash
# Получить свежие новости
curl http://localhost:8000/api/v1/news/fresh | jq '.[].title'

# Output:
# "Breaking: Major Tech Announcement"
# "Latest Political Development"
# "Sports: Championship Results"
# ...
```

---

## ❓ Troubleshooting

### Проблема: Scraper не запускается

**Решение:**
```bash
# 1. Проверить Redis
docker-compose exec redis redis-cli ping
# Должно вернуть: PONG

# 2. Проверить логи
docker-compose logs scraper_worker

# 3. Перезапустить
docker-compose restart scraper_worker
```

### Проблема: Нет новостей в базе

**Решение:**
```bash
# 1. Проверить, что backend работает
curl http://localhost:8000/api/v1/health

# 2. Проверить логи scraper на ошибки отправки
docker-compose logs scraper_worker | grep "sending to backend"

# 3. Запустить парсинг вручную
docker-compose exec scraper_worker python -c "
from app.tasks.scraping_tasks import scrape_all_sources
result = scrape_all_sources()
print(result)
"
```

### Проблема: News API ошибка 401

**Решение:**
```bash
# API key неверный или не установлен
# 1. Проверить .env
cat scraper_service/.env | grep NEWS_API_KEY

# 2. Получить новый ключ на newsapi.org

# 3. Обновить .env и перезапустить
docker-compose restart scraper_worker
```

---

## ✅ Checklist Запуска Scraper

- [ ] Redis запущен и доступен
- [ ] Backend API запущен
- [ ] База данных PostgreSQL работает
- [ ] RSS feeds настроены в config.py
- [ ] (Опционально) News API key установлен
- [ ] Scraper worker запущен
- [ ] Celery beat (scheduler) запущен
- [ ] Flower UI доступен (опционально)
- [ ] Логи scraper показывают успешный парсинг
- [ ] Новости появляются в базе данных
- [ ] API `/fresh` возвращает новости

---

## 🎯 Итог

**Новости автоматически собираются:**
- ✅ Каждые 15 минут (RSS)
- ✅ Каждые 30 минут (полный scrape)
- ✅ Дедупликация автоматическая
- ✅ Отправка в backend автоматическая
- ✅ Retry при ошибках

**Для запуска просто:**
```bash
docker-compose up -d scraper_worker
```

**Новости начнут появляться через 30 секунд - 2 минуты!** 🚀

---

**Документ:** NEWS_SCRAPER_GUIDE.md  
**Дата:** 20 октября 2025  
**Версия:** 1.0
