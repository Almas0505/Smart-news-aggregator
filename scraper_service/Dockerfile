# Scraper Service Dockerfile

FROM python:3.11-slim

# Метаданные
LABEL maintainer="Smart News Aggregator Team"
LABEL description="News Scraper Service with Celery"

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    # Для Selenium (опционально)
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Рабочая директория
WORKDIR /app

# Копируем requirements
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копируем код приложения
COPY app/ ./app/
COPY .env.example .env

# Создаем директории
RUN mkdir -p /app/data/images /app/data/cache /app/logs

# Expose порты (если нужен HTTP API)
# EXPOSE 8002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD celery -A app.celery_app inspect ping || exit 1

# По умолчанию запускаем worker + beat
CMD ["celery", "-A", "app.celery_app", "worker", "-B", "--loglevel=info"]

# Альтернативные команды:
# Worker only: celery -A app.celery_app worker --loglevel=info
# Beat only: celery -A app.celery_app beat --loglevel=info
# Flower: celery -A app.celery_app flower --port=5555