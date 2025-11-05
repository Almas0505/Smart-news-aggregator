# 🎯 ПОЛНЫЙ ОТВЕТ: Откуда Берутся Новости

## ✅ Вопрос Решен!

Да, вы абсолютно правы - **новости должны откуда-то браться**! 

Проект Smart News Aggregator имеет **полноценную систему автоматического сбора новостей**.

---

## 📡 Откуда Появляются Новости

### **Система Сбора (Scraper Service)** 🕷️

Новости собираются **автоматически** из двух источников:

#### 1. **RSS Feeds** (Основной) 📰
- **Что это:** Официальные новостные ленты от сайтов
- **Источники:**
  - BBC News (http://feeds.bbci.co.uk/news/rss.xml)
  - CNN (http://rss.cnn.com/rss/edition.rss)
  - Reuters
  - TechCrunch
  - The Verge
  - Wired
  - и другие...

- **Как работает:**
  ```python
  # Автоматически каждые 15 минут
  scraper.fetch('http://feeds.bbci.co.uk/news/rss.xml')
  → Парсит XML
  → Извлекает: title, content, url, date
  → Сохраняет в базу данных
  ```

- **Плюсы:**
  - ✅ Бесплатно
  - ✅ Надежно
  - ✅ Официально
  - ✅ Без лимитов

#### 2. **News API** (Дополнительный) 🌐
- **Что это:** Сервис агрегации от 80,000+ источников
- **Website:** https://newsapi.org
- **Как работает:**
  ```python
  # Каждые 30 минут
  client.get_top_headlines(sources='bbc-news,cnn')
  → REST API запрос
  → JSON ответ с новостями
  → Сохранение в БД
  ```

- **Лимиты (Free):**
  - 100 запросов/день
  - Нужен API key (бесплатная регистрация)

---

## 🔄 Процесс Сбора Новостей

```
1. SCHEDULER (Celery Beat)
   ↓
   Каждые 15 мин → Запускает RSS scraping
   Каждые 30 мин → Запускает полный scraping
   ↓

2. CELERY WORKER
   ↓
   Получает задачу из Redis queue
   ↓

3. RSS SCRAPER
   ↓
   Парсит RSS feeds → Получает 80-150 статей
   ↓

4. NEWS API SCRAPER (если настроен)
   ↓
   Запрашивает News API → Получает 50-100 статей
   ↓

5. DEDUPLICATION
   ↓
   Удаляет дубликаты по URL и content hash
   → 130-200 уникальных статей
   ↓

6. SEND TO BACKEND
   ↓
   POST /api/v1/news/batch
   → Сохранение в PostgreSQL
   ↓

7. ГОТОВО! ✅
   Новости доступны через /api/v1/news/fresh
```

---

## 🚀 Как Запустить Сбор Новостей

### **Простой Способ:**

```bash
cd /mnt/c/Projects/smart-news-aggregator

# Запустить полный проект со scraper
./start-with-scraper.sh
```

Этот скрипт:
1. ✅ Запустит PostgreSQL и Redis
2. ✅ Запустит Backend API
3. ✅ Запустит News Scraper Service
4. ✅ Настроит автоматический сбор новостей
5. ✅ Создаст источники и категории
6. ✅ Запустит мониторинг (Flower)

**Новости начнут появляться через 1-2 минуты!**

### **Ручной Способ:**

```bash
# 1. Запустить базовые сервисы
docker-compose up -d postgres redis backend

# 2. Дождаться их готовности
sleep 20

# 3. Запустить scraper
docker-compose up -d scraper_worker

# 4. Проверить логи
docker-compose logs -f scraper_worker
```

---

## 📊 Проверка Работы Scraper

### **1. Через Логи:**
```bash
docker-compose logs -f scraper_worker

# Вы увидите:
# [INFO] STARTING FULL SCRAPE
# [INFO] Scraping RSS feeds...
# [INFO] Fetched 45 articles from BBC
# [INFO] Fetched 38 articles from CNN
# [INFO] ✅ RSS: 83 articles
# [INFO] ✅ Sent 80 articles to backend
# [INFO] SCRAPE COMPLETE
```

### **2. Через Flower Web UI:**
```bash
docker-compose up -d flower
open http://localhost:5555

# Увидите:
# - Активные задачи
# - История выполнения
# - Статистика
```

### **3. Через API:**
```bash
# Получить свежие новости
curl http://localhost:8000/api/v1/news/fresh

# Должны вернуться новости!
```

### **4. Через Базу Данных:**
```bash
# Проверить количество новостей
docker-compose exec postgres psql -U postgres -d news_aggregator -c \
  "SELECT COUNT(*) FROM news;"

# Последние новости
docker-compose exec postgres psql -U postgres -d news_aggregator -c \
  "SELECT title, published_at FROM news ORDER BY published_at DESC LIMIT 5;"
```

---

## ⚙️ Настройка Scraper

### **Изменить Интервал Сбора:**

**Файл:** `scraper_service/app/celery_app.py`

```python
app.conf.beat_schedule = {
    'scrape-all-sources': {
        'task': 'app.tasks.scraping_tasks.scrape_all_sources',
        'schedule': 30 * 60.0,  # 30 минут (изменить на нужное)
    },
}
```

### **Добавить Новый RSS Feed:**

**Файл:** `scraper_service/app/config.py`

```python
RSS_FEEDS = {
    'bbc': 'http://feeds.bbci.co.uk/news/rss.xml',
    'cnn': 'http://rss.cnn.com/rss/edition.rss',
    
    # Добавить новый:
    'your_source': 'https://your-site.com/rss.xml'
}
```

### **Настроить News API:**

1. **Получить API Key:**
   - Перейти на https://newsapi.org
   - Зарегистрироваться (бесплатно)
   - Скопировать API Key

2. **Добавить в .env:**
   ```bash
   # scraper_service/.env или docker-compose.yml
   NEWS_API_KEY=your-api-key-here
   ```

3. **Перезапустить:**
   ```bash
   docker-compose restart scraper_worker
   ```

---

## 📁 Структура Scraper Service

```
scraper_service/
├── app/
│   ├── celery_app.py          # Celery конфигурация + scheduler
│   ├── config.py              # Настройки (RSS feeds, intervals)
│   │
│   ├── scrapers/              # Парсеры
│   │   ├── base_scraper.py    # Базовый класс
│   │   ├── rss_scraper.py     # RSS парсер
│   │   └── api_scraper.py     # News API парсер
│   │
│   ├── tasks/                 # Celery задачи
│   │   ├── scraping_tasks.py  # Основные задачи парсинга
│   │   ├── processing_tasks.py
│   │   └── cleanup_tasks.py
│   │
│   └── utils/                 # Вспомогательные функции
│
├── requirements.txt           # Зависимости
└── Dockerfile
```

---

## 🎯 Итоговая Схема

```
┌──────────────────────────────────────────┐
│         НОВОСТИ БЕРУТСЯ ИЗ:              │
├──────────────────────────────────────────┤
│                                          │
│  1. RSS FEEDS (каждые 15 мин)           │
│     ├─ BBC News                          │
│     ├─ CNN                               │
│     ├─ Reuters                           │
│     └─ TechCrunch, etc.                  │
│                                          │
│  2. NEWS API (каждые 30 мин)            │
│     └─ 80,000+ источников                │
│                                          │
│            ▼                             │
│                                          │
│  3. SCRAPER SERVICE                      │
│     ├─ Celery Worker (парсинг)          │
│     ├─ Celery Beat (scheduler)          │
│     └─ Redis (queue)                     │
│                                          │
│            ▼                             │
│                                          │
│  4. DEDUPLICATION                        │
│     └─ Удаление дубликатов               │
│                                          │
│            ▼                             │
│                                          │
│  5. BACKEND API                          │
│     └─ POST /api/v1/news/batch           │
│                                          │
│            ▼                             │
│                                          │
│  6. PostgreSQL DATABASE                  │
│     └─ Таблица news                      │
│                                          │
│            ▼                             │
│                                          │
│  7. ДОСТУПНЫ ЧЕРЕЗ API ✅                │
│     └─ GET /api/v1/news/fresh            │
│                                          │
└──────────────────────────────────────────┘
```

---

## ✅ Финальный Ответ

**Новости берутся из:**
1. ✅ **RSS Feeds** (BBC, CNN, Reuters, etc.) - автоматически каждые 15 минут
2. ✅ **News API** (80,000+ источников) - опционально каждые 30 минут

**Система работает:**
- ✅ Полностью автоматически
- ✅ В фоновом режиме (Celery)
- ✅ С дедупликацией
- ✅ С retry при ошибках
- ✅ С мониторингом (Flower)

**Для запуска:**
```bash
./start-with-scraper.sh
```

**Проверка:**
```bash
curl http://localhost:8000/api/v1/news/fresh
```

---

## 📚 Документация

Созданные файлы:
1. **`NEWS_SCRAPER_GUIDE.md`** - Полный гайд по scraper system
2. **`start-with-scraper.sh`** - Скрипт запуска со scraper
3. **`NEWS_API_SUMMARY.md`** - Документация API
4. **`QUICKSTART_RU.md`** - Руководство по запуску

---

**Проект полностью готов к работе!** 🚀

Новости будут автоматически собираться и обновляться каждые 15-30 минут после запуска scraper service.
