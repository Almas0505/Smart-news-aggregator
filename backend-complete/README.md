# Smart News Aggregator - Backend

Полнофункциональный backend для агрегатора новостей на FastAPI с PostgreSQL, Redis, ElasticSearch и RabbitMQ.

## 🚀 Возможности

- ✅ Аутентификация и авторизация (JWT)
- ✅ CRUD операции для пользователей, новостей, категорий
- ✅ Асинхронная работа с базой данных (SQLAlchemy 2.0 + asyncpg)
- ✅ Кэширование через Redis
- ✅ Полнотекстовый поиск через ElasticSearch
- ✅ Очереди задач через RabbitMQ + Celery
- ✅ Database migrations с Alembic
- ✅ API документация (Swagger/OpenAPI)
- ✅ Docker контейнеризация

## 📋 Требования

- Python 3.11+
- Docker и Docker Compose
- PostgreSQL 15
- Redis 7
- RabbitMQ 3
- ElasticSearch 8

## 🛠 Установка

### Вариант 1: С Docker (рекомендуется)

1. Клонируйте репозиторий:
```bash
git clone <repo-url>
cd smart-news-aggregator/backend
```

2. Создайте .env файл:
```bash
cp .env.example .env
# Отредактируйте .env файл под ваши нужды
```

3. Запустите все сервисы:
```bash
make up
# или
docker-compose up -d
```

4. Проверьте логи:
```bash
make logs
# или
docker-compose logs -f backend
```

5. API будет доступен по адресу: `http://localhost:8000`
6. Swagger документация: `http://localhost:8000/docs`
7. RabbitMQ Management: `http://localhost:15672` (guest/guest)

### Вариант 2: Локально (для разработки)

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
make install
# или
pip install -r requirements.txt
```

3. Настройте .env файл для локальной разработки

4. Запустите PostgreSQL, Redis, RabbitMQ, ElasticSearch локально или через Docker:
```bash
docker-compose up -d postgres redis rabbitmq elasticsearch
```

5. Выполните миграции:
```bash
make migrate
# или
alembic upgrade head
```

6. Инициализируйте базу данных:
```bash
make init-db
# или
python -m app.db.init_db
```

7. Запустите сервер разработки:
```bash
make dev
# или
uvicorn app.main:app --reload
```

## 📚 API Endpoints

### Аутентификация

- `POST /api/v1/auth/register` - Регистрация
- `POST /api/v1/auth/login` - Вход
- `POST /api/v1/auth/refresh` - Обновление токена

### Пользователи

- `GET /api/v1/users/me` - Текущий пользователь
- `PUT /api/v1/users/me` - Обновить профиль
- `DELETE /api/v1/users/me` - Удалить аккаунт
- `GET /api/v1/users/{id}` - Получить пользователя (admin)

### Новости (TODO - добавить endpoints)

- `GET /api/v1/news` - Список новостей
- `GET /api/v1/news/{id}` - Одна новость
- `POST /api/v1/news/search` - Поиск
- `GET /api/v1/news/trending` - Популярные
- `GET /api/v1/news/recommended` - Рекомендации

### Категории (TODO - добавить endpoints)

- `GET /api/v1/categories` - Список категорий
- `GET /api/v1/categories/{id}/news` - Новости по категории

## 🗃 Database Schema

### Users
- id, email, hashed_password, full_name
- is_active, is_superuser, role
- created_at, updated_at

### News
- id, title, content, summary, url, image_url
- source_id, category_id
- sentiment, sentiment_score
- published_at, scraped_at
- views_count, bookmarks_count

### Categories
- id, name, slug, description

### Sources
- id, name, url, type (rss/api/web)
- is_active, scrape_interval

### Tags
- id, name

### Entities (Named Entity Recognition)
- id, news_id, entity_type, entity_text, confidence

### Bookmarks
- id, user_id, news_id

### UserPreferences
- id, user_id, category_id, weight

### ReadingHistory
- id, user_id, news_id, read_at, read_duration

## 🔧 Команды Makefile

```bash
make help       # Показать все команды
make install    # Установить зависимости
make dev        # Запустить dev сервер
make up         # Запустить Docker Compose
make down       # Остановить Docker Compose
make logs       # Показать логи
make clean      # Очистить контейнеры и volumes
make test       # Запустить тесты
make migrate    # Выполнить миграции
make revision   # Создать новую миграцию
make init-db    # Инициализировать БД
make format     # Форматировать код (black)
make lint       # Проверить код (flake8, mypy)
```

## 🧪 Тестирование

```bash
make test
# или
pytest tests/ -v --cov=app --cov-report=html
```

## 📝 Миграции БД

Создать новую миграцию:
```bash
make revision
# или
alembic revision --autogenerate -m "Add new table"
```

Применить миграции:
```bash
make migrate
# или
alembic upgrade head
```

Откатить миграцию:
```bash
alembic downgrade -1
```

## 🔐 Безопасность

- Пароли хешируются с помощью bcrypt
- JWT токены для аутентификации
- CORS настроен для разрешенных origins
- Rate limiting (TODO)
- Валидация входных данных через Pydantic

## 📊 Мониторинг

- Логирование в JSON формате (production)
- Health check endpoint: `GET /health`
- Metrics (TODO - Prometheus)

## 🚧 TODO

- [ ] Добавить News endpoints
- [ ] Добавить Categories endpoints
- [ ] Добавить Sources endpoints
- [ ] Добавить Search service (ElasticSearch)
- [ ] Добавить Cache service (Redis)
- [ ] Добавить Recommendation service
- [ ] Добавить ML service integration
- [ ] Добавить WebSocket для real-time updates
- [ ] Добавить Rate limiting middleware
- [ ] Добавить Prometheus metrics
- [ ] Добавить Unit и Integration тесты
- [ ] Добавить CI/CD pipeline

## 📄 Лицензия

MIT

## 👥 Авторы

Smart News Aggregator Team
