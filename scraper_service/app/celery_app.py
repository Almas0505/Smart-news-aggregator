"""
Celery Application

Конфигурация Celery для асинхронного парсинга новостей.

====== ЧТО ТАКОЕ CELERY? ======

Celery - distributed task queue для Python.

Компоненты:
1. **Broker** - message queue (Redis/RabbitMQ)
2. **Worker** - выполняет задачи
3. **Beat** - scheduler для периодических задач
4. **Backend** - хранит результаты

Зачем нужен для парсинга:
- Асинхронный парсинг (не блокирует приложение)
- Периодический запуск (каждые 30 минут)
- Retry механизм при ошибках
- Масштабируемость (можно добавить больше workers)

====== АРХИТЕКТУРА ======

```
┌─────────┐        ┌─────────┐        ┌─────────┐
│ Producer│───────▶│  Broker │───────▶│ Worker  │
│ (API)   │ Task   │ (Redis) │ Task   │ (Celery)│
└─────────┘        └─────────┘        └─────────┘
                        │                   │
                        │                   ▼
                   ┌────▼────┐         ┌─────────┐
                   │  Beat   │         │ Backend │
                   │Scheduler│         │ (Redis) │
                   └─────────┘         └─────────┘
```

====== WORKFLOW ======

1. Beat отправляет task каждые 30 минут
2. Task попадает в Redis queue
3. Worker берет task из queue
4. Worker парсит новости
5. Результат сохраняется в Backend
6. Backend API отправляет данные в основную БД
"""

from celery import Celery
from celery.schedules import crontab
import logging

from app.config import settings


logger = logging.getLogger(__name__)


# ===== CREATE CELERY APP =====

app = Celery(
    'scraper_service',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        'app.tasks.scraping_tasks',
        'app.tasks.processing_tasks',
        'app.tasks.cleanup_tasks'
    ]
)


# ===== CELERY CONFIGURATION =====

app.conf.update(
    # Serialization
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    
    # Timezone
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    
    # Task settings
    task_track_started=True,  # Отслеживать начало выполнения
    task_time_limit=30 * 60,  # 30 минут max
    task_soft_time_limit=25 * 60,  # 25 минут soft limit
    
    # Result settings
    result_expires=3600,  # Результаты хранятся 1 час
    result_persistent=True,
    
    # Worker settings
    worker_prefetch_multiplier=1,  # Брать по 1 задаче
    worker_max_tasks_per_child=100,  # Рестарт после 100 задач
    
    # Rate limiting
    task_default_rate_limit='10/m',  # 10 задач в минуту
    
    # Retry settings
    task_autoretry_for=(Exception,),
    task_retry_kwargs={'max_retries': 3},
    task_retry_backoff=True,
    task_retry_backoff_max=600,
    task_retry_jitter=True,
)


# ===== BEAT SCHEDULE (Periodic Tasks) =====

app.conf.beat_schedule = {
    # Парсинг всех источников каждые 30 минут
    'scrape-all-sources': {
        'task': 'app.tasks.scraping_tasks.scrape_all_sources',
        'schedule': settings.SCRAPE_INTERVAL_MINUTES * 60.0,  # в секундах
        'options': {
            'expires': 15 * 60,  # Expire через 15 минут
        }
    },
    
    # Парсинг RSS каждые 15 минут (быстрее чем остальные)
    'scrape-rss-feeds': {
        'task': 'app.tasks.scraping_tasks.scrape_rss_feeds',
        'schedule': 15 * 60.0,  # 15 минут
    },
    
    # Очистка старых данных каждый день в 3:00
    'cleanup-old-data': {
        'task': 'app.tasks.cleanup_tasks.cleanup_old_data',
        'schedule': crontab(hour=3, minute=0),
    },
    
    # Очистка кеша каждые 6 часов
    'cleanup-cache': {
        'task': 'app.tasks.cleanup_tasks.cleanup_cache',
        'schedule': crontab(minute=0, hour='*/6'),
    },
}


# ===== TASK ROUTES =====
# Направлять разные задачи на разные queues

app.conf.task_routes = {
    'app.tasks.scraping_tasks.*': {
        'queue': 'scraping',
        'routing_key': 'scraping.tasks',
    },
    'app.tasks.processing_tasks.*': {
        'queue': 'processing',
        'routing_key': 'processing.tasks',
    },
    'app.tasks.cleanup_tasks.*': {
        'queue': 'cleanup',
        'routing_key': 'cleanup.tasks',
    },
}


# ===== LOGGING =====

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Setup logging после конфигурации."""
    logger.info("Celery app configured successfully")
    logger.info(f"Broker: {settings.CELERY_BROKER_URL}")
    logger.info(f"Backend: {settings.CELERY_RESULT_BACKEND}")


# ===== USAGE EXAMPLES =====
"""
# ===== Running Celery =====

# 1. Start Worker
celery -A app.celery_app worker --loglevel=info

# 2. Start Beat (scheduler)
celery -A app.celery_app beat --loglevel=info

# 3. Start Worker + Beat together
celery -A app.celery_app worker -B --loglevel=info

# 4. Multiple queues
celery -A app.celery_app worker -Q scraping,processing --loglevel=info


# ===== Monitoring =====

# Flower - web monitoring tool
celery -A app.celery_app flower

# Open browser: http://localhost:5555


# ===== Calling Tasks =====

from app.tasks.scraping_tasks import scrape_rss_feeds

# Synchronous (блокирует)
result = scrape_rss_feeds()

# Asynchronous (не блокирует)
task = scrape_rss_feeds.delay()

# Check status
print(task.status)  # PENDING, STARTED, SUCCESS, FAILURE

# Get result
result = task.get(timeout=60)


# ===== Retry Task =====

from app.celery_app import app

@app.task(bind=True, max_retries=3)
def my_task(self):
    try:
        # Do something
        pass
    except Exception as exc:
        # Retry after 60 seconds
        raise self.retry(exc=exc, countdown=60)


# ===== Chain Tasks =====

from celery import chain

# Task1 → Task2 → Task3
workflow = chain(
    scrape_rss_feeds.s(),
    process_articles.s(),
    send_to_backend.s()
)

result = workflow.apply_async()


# ===== Group Tasks =====

from celery import group

# Выполнить несколько задач параллельно
job = group([
    scrape_source.s('bbc'),
    scrape_source.s('cnn'),
    scrape_source.s('reuters'),
])

result = job.apply_async()


# ===== Production Tips =====

# 1. Use supervisor/systemd для auto-restart
# 2. Monitor с помощью Flower
# 3. Set proper concurrency:
#    celery -A app.celery_app worker --concurrency=4
# 4. Use different queues for different task types
# 5. Enable result backend только если нужны результаты
# 6. Regular cleanup старых результатов
"""