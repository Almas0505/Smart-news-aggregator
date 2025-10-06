# Scraper Service Dockerfile for Smart News Aggregator
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY scraper_service/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY scraper_service/ .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Health check (for Celery worker)
HEALTHCHECK --interval=60s --timeout=10s --start-period=10s --retries=3 \
    CMD celery -A app.celery_app inspect ping -d celery@$HOSTNAME || exit 1

# Default command (can be overridden in docker-compose)
CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info"]
