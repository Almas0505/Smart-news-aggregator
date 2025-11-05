# Grafana Dashboards для Smart News Aggregator

## 📊 Созданные Dashboard'ы

### 1. **Backend API Dashboard** (`backend-api.json`)
Мониторинг производительности Backend API:
- **Request Rate** - количество запросов в секунду по endpoint'ам
- **Request Duration (p95)** - латентность запросов (95-й перцентиль)
- **Error Rate** - количество ошибок 5xx
- **Active Requests** - активные запросы в данный момент
- **Total Requests** - общее количество запросов
- **CPU Usage** - использование процессора
- **Memory Usage** - использование памяти
- **News Created/Views** - статистика по новостям
- **Users Registered** - новые пользователи
- **Cache Hit Rate** - эффективность кэша Redis

### 2. **Database Performance Dashboard** (`database.json`)
Мониторинг PostgreSQL:
- **Database Connections** - активные и idle соединения
- **Query Duration (p95)** - длительность запросов
- **Queries Per Second** - количество запросов к БД
- **Database Size** - размер базы данных
- **Active/Idle Queries** - статистика активных запросов
- **Transaction Rate** - commits и rollbacks
- **Cache Hit Ratio** - эффективность кэша PostgreSQL

### 3. **ML Service Dashboard** (`ml-service.json`)
Мониторинг ML сервиса:
- **Predictions Per Second** - предсказания в секунду по типам моделей
- **Prediction Latency (p95)** - латентность предсказаний
- **Model Load Time** - время загрузки моделей
- **Cache Hit Rate** - эффективность кэша embeddings
- **Total Predictions** - общее количество предсказаний
- **Active Models** - количество загруженных моделей
- **NER/Sentiment/Embeddings** - статистика по типам задач
- **Classification Accuracy** - точность классификатора
- **CPU/Memory Usage** - использование ресурсов

### 4. **Scraper Service Dashboard** (`scraper.json`)
Мониторинг Scraper сервиса:
- **Articles Scraped Per Hour** - собранные статьи по источникам
- **Scraper Run Duration** - длительность скрейпинга
- **Scraper Errors** - ошибки по источникам и типам
- **Total Articles Today** - всего статей за сегодня
- **Active Scrapers** - активные задачи Celery
- **Source Health Status** - статус источников новостей
- **Celery Tasks** - pending/running задачи
- **Celery Workers** - количество воркеров
- **Task Success Rate** - процент успешных задач
- **RSS Feeds Processed** - обработано RSS лент
- **News API Calls** - вызовы News API
- **Duplicate Articles Skipped** - пропущено дубликатов
- **Rate Limit Delays** - задержки из-за rate limiting

### 5. **System Overview Dashboard** (`overview.json`)
Общий обзор системы:
- **System Health** - статус всех сервисов (UP/DOWN)
- **Total Requests/sec** - общий RPS системы
- **Response Time (p95/p99)** - латентность системы
- **Business Metrics** - общее количество новостей, активные пользователи
- **Resource Usage** - CPU и Memory по сервисам
- **Error Rates** - ошибки 5xx и ошибки scraper'ов

---

## 🚀 Установка и Настройка

### 1. Docker Compose Configuration

Добавьте Grafana в `docker-compose.yml`:

```yaml
services:
  grafana:
    image: grafana/grafana:10.2.0
    container_name: grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_USER=admin
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_SERVER_ROOT_URL=http://localhost:3001
    volumes:
      - ./infrastructure/monitoring/grafana/provisioning:/etc/grafana/provisioning
      - ./infrastructure/monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - grafana-data:/var/lib/grafana
    networks:
      - smart-news-network
    depends_on:
      - prometheus

volumes:
  grafana-data:
```

### 2. Запуск Grafana

```bash
# Запуск всех сервисов включая Grafana
docker-compose up -d grafana

# Проверка статуса
docker-compose ps grafana

# Логи
docker-compose logs -f grafana
```

### 3. Доступ к Grafana

Откройте браузер: `http://localhost:3001`
- **Username**: `admin`
- **Password**: `admin123`

### 4. Автоматическая Загрузка Dashboard'ов

Dashboard'ы загружаются автоматически через provisioning:
- Файл конфигурации: `provisioning/dashboards/dashboards.yml`
- Dashboard JSON: `dashboards/*.json`
- Datasource: `provisioning/datasources/prometheus.yml`

---

## 📈 Использование Dashboard'ов

### Навигация

1. **Home** → **Dashboards** → **Smart News**
2. Выберите нужный dashboard:
   - Backend API
   - Database Performance
   - ML Service
   - Scraper Service
   - System Overview

### Фильтры и Временные Интервалы

- **Time Range**: Верхний правый угол (Last 15 minutes, Last 1 hour, etc.)
- **Refresh**: Автообновление каждые 30 секунд (настраивается)
- **Variables**: Некоторые dashboard'ы поддерживают фильтры (source, model_type)

### Алерты (Alert Rules)

Рекомендуемые алерты:

#### Backend API Alerts
```yaml
# High Error Rate
- alert: HighErrorRate
  expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.05
  for: 5m
  labels:
    severity: critical
  annotations:
    summary: "High 5xx error rate detected"

# High Response Time
- alert: HighResponseTime
  expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High response time (p95 > 2s)"
```

#### Database Alerts
```yaml
# High Connection Usage
- alert: HighDBConnections
  expr: db_connections_active > 80
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High database connection usage"

# Slow Queries
- alert: SlowQueries
  expr: histogram_quantile(0.95, rate(db_query_duration_seconds_bucket[5m])) > 1
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "Slow database queries detected"
```

#### Scraper Alerts
```yaml
# High Scraper Error Rate
- alert: HighScraperErrorRate
  expr: rate(scraper_errors_total[5m]) > 0.1
  for: 10m
  labels:
    severity: warning
  annotations:
    summary: "High scraper error rate"

# No Articles Scraped
- alert: NoArticlesScraped
  expr: increase(scraper_articles_scraped_total[1h]) == 0
  for: 2h
  labels:
    severity: critical
  annotations:
    summary: "No articles scraped in the last 2 hours"
```

---

## 🔧 Кастомизация Dashboard'ов

### Добавление Панели

1. Откройте dashboard
2. Нажмите **Add panel** → **Add new panel**
3. Выберите тип визуализации (Graph, Stat, Gauge, Table)
4. Настройте запрос Prometheus
5. **Save dashboard**

### Экспорт Dashboard

```bash
# В Grafana UI
Settings (⚙️) → JSON Model → Copy to clipboard

# Сохранить в файл
cat > custom-dashboard.json
# Paste JSON
```

### Импорт Dashboard

```bash
# Копируйте JSON файл в папку dashboards
cp custom-dashboard.json infrastructure/monitoring/grafana/dashboards/

# Перезапустите Grafana
docker-compose restart grafana
```

---

## 📊 Prometheus Metrics Reference

### Backend Metrics
```
http_requests_total - Total HTTP requests
http_request_duration_seconds - Request duration histogram
http_requests_in_progress - Active requests
news_created_total - Total news articles created
news_views_total - Total article views
users_registered_total - Total registered users
cache_hits_total - Cache hits
cache_misses_total - Cache misses
```

### Database Metrics
```
db_connections_active - Active DB connections
db_connections_idle - Idle DB connections
db_queries_total - Total database queries
db_query_duration_seconds - Query duration histogram
pg_database_size_bytes - Database size
pg_stat_activity_count - Active/idle queries count
```

### ML Service Metrics
```
ml_predictions_total - Total predictions by model type
ml_prediction_duration_seconds - Prediction duration histogram
ml_model_load_seconds - Model loading time
ml_cache_hits_total - Embedding cache hits
ml_classification_accuracy - Classification accuracy
```

### Scraper Metrics
```
scraper_articles_scraped_total - Articles scraped by source
scraper_run_duration_seconds - Scraper run duration
scraper_errors_total - Scraper errors by type
scraper_active_tasks - Active Celery tasks
celery_tasks_pending - Pending tasks
celery_tasks_running - Running tasks
celery_workers_online - Online workers
```

---

## 🛠️ Troubleshooting

### Dashboard не загружается

```bash
# Проверьте логи Grafana
docker-compose logs grafana | grep -i error

# Проверьте provisioning конфигурацию
docker exec -it grafana cat /etc/grafana/provisioning/dashboards/dashboards.yml

# Проверьте доступность файлов
docker exec -it grafana ls -la /etc/grafana/provisioning/dashboards/
```

### Нет данных на графиках

```bash
# Проверьте подключение к Prometheus
curl http://localhost:3001/api/datasources/proxy/1/api/v1/query?query=up

# Проверьте статус Prometheus
curl http://localhost:9090/-/healthy

# Проверьте targets в Prometheus
http://localhost:9090/targets
```

### Метрики не собираются

```bash
# Проверьте эндпоинт метрик в сервисе
curl http://localhost:8000/metrics

# Проверьте конфигурацию Prometheus
docker exec -it prometheus cat /etc/prometheus/prometheus.yml

# Перезагрузите Prometheus
docker-compose restart prometheus
```

---

## 📚 Дополнительные Ресурсы

- [Grafana Documentation](https://grafana.com/docs/)
- [Prometheus Query Language](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Dashboard Best Practices](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/best-practices/)
- [Alert Rules Configuration](https://grafana.com/docs/grafana/latest/alerting/)

---

## ✅ Проверка Работы

```bash
# 1. Запустите все сервисы
docker-compose up -d

# 2. Откройте Grafana
open http://localhost:3001

# 3. Проверьте datasource
# Settings → Data Sources → Prometheus → Test

# 4. Откройте System Overview dashboard
# Home → Dashboards → Smart News → System Overview

# 5. Проверьте метрики
# Должны быть видны графики с данными из Prometheus
```

---

**Created**: 2024
**Status**: ✅ Production Ready
**Version**: 1.0.0
