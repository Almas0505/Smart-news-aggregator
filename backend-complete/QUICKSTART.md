# 🚀 Quick Start Guide - Smart News Aggregator Backend

## Быстрый запуск за 3 шага

### Шаг 1: Подготовка

```bash
cd smart-news-aggregator/backend
cp .env.example .env
```

### Шаг 2: Запуск

```bash
# Используя скрипт
./run.sh

# Или напрямую
docker-compose up -d
```

### Шаг 3: Проверка

Откройте в браузере:
- API: http://localhost:8000
- Документация: http://localhost:8000/docs

## 📝 Первые действия

### 1. Зарегистрировать пользователя

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123",
    "full_name": "John Doe"
  }'
```

### 2. Войти в систему

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePass123"
  }'
```

Ответ:
```json
{
  "access_token": "eyJ0eXAi...",
  "refresh_token": "eyJ0eXAi...",
  "token_type": "bearer"
}
```

### 3. Получить информацию о пользователе

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🛠 Полезные команды

### Docker
```bash
# Остановить
docker-compose down

# Перезапустить
docker-compose restart

# Посмотреть логи
docker-compose logs -f backend

# Очистить всё
docker-compose down -v
```

### База данных
```bash
# Создать миграцию
make revision

# Применить миграции
make migrate

# Подключиться к БД
make db-shell
```

### Разработка
```bash
# Запустить тесты
make test

# Форматировать код
make format

# Проверить код
make lint
```

## 📊 Структура проекта

```
backend/
├── app/
│   ├── api/              # API endpoints
│   ├── core/             # Конфигурация, security
│   ├── db/               # Database
│   ├── models/           # SQLAlchemy модели
│   ├── schemas/          # Pydantic схемы
│   ├── services/         # Бизнес-логика
│   ├── middleware/       # Middleware
│   ├── utils/            # Утилиты
│   └── main.py           # Точка входа
├── alembic/              # Миграции БД
├── tests/                # Тесты
├── docker-compose.yml    # Docker конфигурация
├── Dockerfile            # Docker образ
├── requirements.txt      # Зависимости
├── Makefile             # Команды
└── README.md            # Документация
```

## 🔧 Настройка .env

Основные переменные:

```env
# Database
POSTGRES_SERVER=localhost
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=news_aggregator

# Security
SECRET_KEY=your-secret-key-min-32-chars
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Email (опционально)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

## 🐛 Решение проблем

### Порты заняты
```bash
# Изменить порты в docker-compose.yml
ports:
  - "8001:8000"  # вместо 8000:8000
```

### База данных не инициализируется
```bash
# Пересоздать контейнеры
docker-compose down -v
docker-compose up -d
```

### Ошибки импорта
```bash
# Переустановить зависимости
pip install -r requirements.txt --force-reinstall
```

## 📚 Дополнительные ресурсы

- [Полная документация](README.md)
- [API документация](http://localhost:8000/docs)
- [FastAPI документация](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0](https://docs.sqlalchemy.org/en/20/)

## ✅ Чек-лист для начала работы

- [ ] Установлен Docker и Docker Compose
- [ ] Создан .env файл
- [ ] Запущены все сервисы (docker-compose up -d)
- [ ] Проверен health check (http://localhost:8000/health)
- [ ] Открыта документация (http://localhost:8000/docs)
- [ ] Зарегистрирован тестовый пользователь
- [ ] Получен JWT токен

Готово! Теперь можно начинать разработку 🎉
