"""
Cleanup Tasks

Задачи очистки старых данных, кеша, логов.

====== CLEANUP TASKS ======

1. cleanup_old_data - удаление старых данных
2. cleanup_cache - очистка кеша
3. cleanup_old_images - удаление старых изображений
4. cleanup_celery_results - очистка результатов Celery
"""

import os
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict
import logging

from app.celery_app import app
from app.config import settings


logger = logging.getLogger(__name__)


# ===== MAIN CLEANUP TASK =====

@app.task(
    name='app.tasks.cleanup_tasks.cleanup_old_data',
    bind=True
)
def cleanup_old_data(self, days_old: int = 7) -> Dict:
    """Очистка старых данных.
    
    Args:
        days_old: Удалить данные старше N дней
    
    Returns:
        Статистика очистки
    """
    logger.info("="*60)
    logger.info(f"CLEANUP: Removing data older than {days_old} days")
    logger.info("="*60)
    
    stats = {
        'images_deleted': 0,
        'cache_cleared': 0,
        'logs_cleaned': 0,
        'start_time': datetime.utcnow().isoformat()
    }
    
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    try:
        # 1. Очистка изображений
        images_deleted = cleanup_old_images(cutoff_date)
        stats['images_deleted'] = images_deleted
        logger.info(f"✅ Deleted {images_deleted} old images")
        
    except Exception as e:
        logger.error(f"Error cleaning images: {e}")
    
    try:
        # 2. Очистка кеша
        cache_cleared = cleanup_cache()
        stats['cache_cleared'] = cache_cleared
        logger.info(f"✅ Cleared {cache_cleared} cache files")
        
    except Exception as e:
        logger.error(f"Error cleaning cache: {e}")
    
    try:
        # 3. Очистка логов
        logs_cleaned = cleanup_old_logs(cutoff_date)
        stats['logs_cleaned'] = logs_cleaned
        logger.info(f"✅ Cleaned {logs_cleaned} old log files")
        
    except Exception as e:
        logger.error(f"Error cleaning logs: {e}")
    
    stats['end_time'] = datetime.utcnow().isoformat()
    
    logger.info("="*60)
    logger.info("CLEANUP COMPLETE")
    logger.info(f"Images: {stats['images_deleted']} | "
                f"Cache: {stats['cache_cleared']} | "
                f"Logs: {stats['logs_cleaned']}")
    logger.info("="*60)
    
    return stats


# ===== IMAGE CLEANUP =====

def cleanup_old_images(cutoff_date: datetime) -> int:
    """Удалить старые изображения.
    
    Args:
        cutoff_date: Удалить файлы старше этой даты
    
    Returns:
        Количество удаленных файлов
    """
    images_dir = settings.IMAGES_DIR
    
    if not os.path.exists(images_dir):
        return 0
    
    deleted_count = 0
    
    for root, dirs, files in os.walk(images_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            
            # Проверяем время модификации
            mod_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if mod_time < cutoff_date:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                    logger.debug(f"Deleted: {filepath}")
                except Exception as e:
                    logger.error(f"Error deleting {filepath}: {e}")
    
    return deleted_count


# ===== CACHE CLEANUP =====

@app.task(
    name='app.tasks.cleanup_tasks.cleanup_cache',
    bind=True
)
def cleanup_cache(self) -> int:
    """Очистить весь кеш.
    
    Returns:
        Количество очищенных файлов
    """
    cache_dir = settings.CACHE_DIR
    
    if not os.path.exists(cache_dir):
        return 0
    
    logger.info(f"Cleaning cache directory: {cache_dir}")
    
    deleted_count = 0
    
    try:
        # Удаляем все файлы в кеше
        for root, dirs, files in os.walk(cache_dir):
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"Error deleting cache file: {e}")
        
        logger.info(f"✅ Cache cleared: {deleted_count} files")
        
    except Exception as e:
        logger.error(f"Error cleaning cache: {e}")
    
    return deleted_count


def clear_specific_cache(cache_key: str) -> bool:
    """Очистить конкретный кеш по ключу.
    
    Args:
        cache_key: Ключ кеша
    
    Returns:
        True если успешно
    """
    try:
        # Если используем diskcache
        from diskcache import Cache
        
        cache = Cache(str(settings.CACHE_DIR))
        
        if cache_key in cache:
            del cache[cache_key]
            logger.info(f"Cache key deleted: {cache_key}")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error clearing cache key: {e}")
        return False


# ===== LOG CLEANUP =====

def cleanup_old_logs(cutoff_date: datetime) -> int:
    """Удалить старые log файлы.
    
    Args:
        cutoff_date: Удалить логи старше этой даты
    
    Returns:
        Количество удаленных файлов
    """
    log_dir = Path(settings.LOG_FILE).parent
    
    if not log_dir.exists():
        return 0
    
    deleted_count = 0
    
    # Находим все .log файлы
    for log_file in log_dir.glob('*.log*'):
        try:
            mod_time = datetime.fromtimestamp(log_file.stat().st_mtime)
            
            if mod_time < cutoff_date:
                log_file.unlink()
                deleted_count += 1
                logger.debug(f"Deleted log: {log_file}")
                
        except Exception as e:
            logger.error(f"Error deleting log {log_file}: {e}")
    
    return deleted_count


# ===== CELERY RESULTS CLEANUP =====

@app.task(
    name='app.tasks.cleanup_tasks.cleanup_celery_results',
    bind=True
)
def cleanup_celery_results(self, days_old: int = 1) -> int:
    """Очистить старые результаты Celery.
    
    Args:
        days_old: Удалить результаты старше N дней
    
    Returns:
        Количество удаленных результатов
    """
    logger.info(f"Cleaning Celery results older than {days_old} days")
    
    try:
        from celery.result import AsyncResult
        from datetime import datetime, timedelta
        
        # Получаем все task IDs из backend
        # Note: это зависит от backend (Redis/RabbitMQ)
        
        # Для Redis backend:
        if 'redis' in settings.CELERY_RESULT_BACKEND:
            import redis
            
            # Парсим Redis URL
            from urllib.parse import urlparse
            parsed = urlparse(settings.CELERY_RESULT_BACKEND)
            
            r = redis.Redis(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 6379,
                db=int(parsed.path[1:]) if parsed.path else 0
            )
            
            # Удаляем старые ключи
            deleted = 0
            cutoff = datetime.utcnow() - timedelta(days=days_old)
            
            # Все ключи celery-task-meta-*
            pattern = "celery-task-meta-*"
            
            for key in r.scan_iter(match=pattern):
                try:
                    # Проверяем TTL
                    ttl = r.ttl(key)
                    if ttl == -1:  # No expiration
                        r.delete(key)
                        deleted += 1
                except Exception as e:
                    logger.error(f"Error deleting key {key}: {e}")
            
            logger.info(f"✅ Deleted {deleted} old Celery results")
            return deleted
        
        return 0
        
    except Exception as e:
        logger.error(f"Error cleaning Celery results: {e}")
        return 0


# ===== DISK SPACE CHECK =====

@app.task(
    name='app.tasks.cleanup_tasks.check_disk_space',
    bind=True
)
def check_disk_space(self) -> Dict:
    """Проверить свободное место на диске.
    
    Returns:
        Информация о диске
    """
    try:
        disk_usage = shutil.disk_usage('/')
        
        total_gb = disk_usage.total / (1024**3)
        used_gb = disk_usage.used / (1024**3)
        free_gb = disk_usage.free / (1024**3)
        percent_used = (used_gb / total_gb) * 100
        
        info = {
            'total_gb': round(total_gb, 2),
            'used_gb': round(used_gb, 2),
            'free_gb': round(free_gb, 2),
            'percent_used': round(percent_used, 2)
        }
        
        # Warning если мало места
        if percent_used > 90:
            logger.warning(f"⚠️ Disk space low: {percent_used}% used!")
        elif percent_used > 80:
            logger.info(f"Disk usage: {percent_used}%")
        
        return info
        
    except Exception as e:
        logger.error(f"Error checking disk space: {e}")
        return {}


# ===== USAGE EXAMPLES =====
"""
# ===== Manual Cleanup =====

from app.tasks.cleanup_tasks import (
    cleanup_old_data,
    cleanup_cache,
    cleanup_celery_results
)

# Очистить данные старше 7 дней
task = cleanup_old_data.delay(days_old=7)
stats = task.get()
print(stats)

# Очистить весь кеш
task = cleanup_cache.delay()
cleared = task.get()
print(f"Cleared {cleared} cache files")

# Очистить результаты Celery старше 1 дня
task = cleanup_celery_results.delay(days_old=1)
deleted = task.get()


# ===== Check Disk Space =====

from app.tasks.cleanup_tasks import check_disk_space

task = check_disk_space.delay()
info = task.get()
print(f"Disk: {info['free_gb']} GB free ({info['percent_used']}% used)")


# ===== Scheduled Cleanup =====

# Эти задачи запускаются автоматически по расписанию (в celery_app.py):

# cleanup_old_data - каждый день в 3:00
# cleanup_cache - каждые 6 часов
# cleanup_celery_results - каждый час


# ===== Custom Cleanup =====

from app.tasks.cleanup_tasks import clear_specific_cache

# Очистить конкретный кеш
success = clear_specific_cache('news_bbc_20240115')
if success:
    print("Cache cleared")
"""