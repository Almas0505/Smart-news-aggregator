"""
Scraping Tasks

Celery задачи для парсинга новостей.

====== TASKS ======

1. scrape_all_sources - парсить все источники
2. scrape_rss_feeds - только RSS
3. scrape_news_api - только News API
4. scrape_source - конкретный источник
5. send_articles_to_backend - отправка в Backend API
"""

from typing import List, Dict, Optional
import logging
from datetime import datetime

from app.celery_app import app
from app.scrapers.rss_scraper import MultiFeedScraper
from app.scrapers.api_scraper import NewsAPIScraper
from app.scrapers.base_scraper import Article
from app.config import settings
import httpx


logger = logging.getLogger(__name__)


# ===== MAIN SCRAPING TASKS =====

@app.task(
    name='app.tasks.scraping_tasks.scrape_all_sources',
    bind=True,
    max_retries=3,
    soft_time_limit=20 * 60  # 20 минут
)
def scrape_all_sources(self) -> Dict[str, int]:
    """Парсить ВСЕ источники новостей.
    
    Эта задача запускается периодически (каждые 30 минут).
    
    Returns:
        Статистика парсинга
        
    Example result:
        {
            'total_articles': 150,
            'rss_articles': 100,
            'api_articles': 50,
            'sent_to_backend': 145,
            'errors': 5
        }
    """
    logger.info("="*60)
    logger.info("STARTING FULL SCRAPE")
    logger.info("="*60)
    
    stats = {
        'total_articles': 0,
        'rss_articles': 0,
        'api_articles': 0,
        'sent_to_backend': 0,
        'errors': 0,
        'start_time': datetime.utcnow().isoformat()
    }
    
    all_articles = []
    
    try:
        # 1. RSS Feeds
        logger.info("1/2 Scraping RSS feeds...")
        rss_articles = scrape_rss_feeds()
        all_articles.extend(rss_articles)
        stats['rss_articles'] = len(rss_articles)
        logger.info(f"✅ RSS: {len(rss_articles)} articles")
        
    except Exception as e:
        logger.error(f"❌ RSS scraping failed: {e}")
        stats['errors'] += 1
    
    try:
        # 2. News API (если есть API key)
        if settings.NEWS_API_KEY:
            logger.info("2/2 Scraping News API...")
            api_articles = scrape_news_api()
            all_articles.extend(api_articles)
            stats['api_articles'] = len(api_articles)
            logger.info(f"✅ News API: {len(api_articles)} articles")
        else:
            logger.info("⚠️ News API key not set, skipping")
            
    except Exception as e:
        logger.error(f"❌ News API scraping failed: {e}")
        stats['errors'] += 1
    
    # 3. Обработка и отправка
    stats['total_articles'] = len(all_articles)
    
    if all_articles:
        logger.info(f"Processing {len(all_articles)} articles...")
        
        # Дедупликация
        unique_articles = deduplicate_articles(all_articles)
        logger.info(f"After dedup: {len(unique_articles)} unique articles")
        
        # Отправка в Backend
        try:
            sent_count = send_articles_to_backend(unique_articles)
            stats['sent_to_backend'] = sent_count
            logger.info(f"✅ Sent {sent_count} articles to backend")
        except Exception as e:
            logger.error(f"❌ Failed to send to backend: {e}")
            stats['errors'] += 1
    
    stats['end_time'] = datetime.utcnow().isoformat()
    
    logger.info("="*60)
    logger.info("SCRAPE COMPLETE")
    logger.info(f"Total: {stats['total_articles']} | "
                f"Sent: {stats['sent_to_backend']} | "
                f"Errors: {stats['errors']}")
    logger.info("="*60)
    
    return stats


@app.task(
    name='app.tasks.scraping_tasks.scrape_rss_feeds',
    bind=True
)
def scrape_rss_feeds(self) -> List[Dict]:
    """Парсить только RSS ленты.
    
    Returns:
        Список статей (dict format)
    """
    logger.info("Scraping RSS feeds...")
    
    try:
        scraper = MultiFeedScraper()
        articles = scraper.scrape_all()
        
        logger.info(f"Scraped {len(articles)} articles from RSS")
        
        # Конвертируем в dict для сериализации
        return [article.to_dict() for article in articles]
        
    except Exception as e:
        logger.error(f"RSS scraping error: {e}")
        raise


@app.task(
    name='app.tasks.scraping_tasks.scrape_news_api',
    bind=True
)
def scrape_news_api(self) -> List[Dict]:
    """Парсить News API.
    
    Returns:
        Список статей (dict format)
    """
    logger.info("Scraping News API...")
    
    if not settings.NEWS_API_KEY:
        logger.warning("NEWS_API_KEY not set, skipping")
        return []
    
    try:
        scraper = NewsAPIScraper()
        articles = scraper.run()
        
        logger.info(f"Scraped {len(articles)} articles from News API")
        
        return [article.to_dict() for article in articles]
        
    except Exception as e:
        logger.error(f"News API scraping error: {e}")
        raise


@app.task(
    name='app.tasks.scraping_tasks.scrape_source',
    bind=True
)
def scrape_source(self, source_name: str) -> List[Dict]:
    """Парсить конкретный источник.
    
    Args:
        source_name: Название источника (bbc, cnn, и т.д.)
    
    Returns:
        Список статей
    """
    logger.info(f"Scraping source: {source_name}")
    
    articles = []
    
    try:
        # Пробуем RSS
        rss_url = settings.RSS_FEEDS.get(source_name)
        if rss_url:
            from app.scrapers.rss_scraper import RSSFeedScraper
            scraper = RSSFeedScraper(source_name, rss_url)
            articles = scraper.run()
        
        # Если не RSS, пробуем через News API
        elif source_name in settings.NEWS_API_SOURCES:
            scraper = NewsAPIScraper(sources=[source_name])
            articles = scraper.run()
        
        else:
            logger.warning(f"Source not found: {source_name}")
            return []
        
        logger.info(f"Scraped {len(articles)} articles from {source_name}")
        
        return [article.to_dict() for article in articles]
        
    except Exception as e:
        logger.error(f"Error scraping {source_name}: {e}")
        raise


# ===== BACKEND INTEGRATION =====

@app.task(
    name='app.tasks.scraping_tasks.send_articles_to_backend',
    bind=True,
    max_retries=5,
    retry_backoff=True
)
def send_articles_to_backend(self, articles: List[Dict]) -> int:
    """Отправить статьи в Backend API.
    
    Args:
        articles: Список статей (dict format)
    
    Returns:
        Количество успешно отправленных
        
    Raises:
        self.retry: При ошибке отправки
    """
    if not articles:
        return 0
    
    logger.info(f"Sending {len(articles)} articles to backend...")
    
    # Backend API URL
    backend_url = f"{settings.BACKEND_URL}/api/v1/news/batch"
    
    # Разбиваем на батчи
    batch_size = settings.BATCH_SIZE
    batches = [
        articles[i:i + batch_size]
        for i in range(0, len(articles), batch_size)
    ]
    
    sent_count = 0
    
    try:
        # Используем httpx для async requests
        with httpx.Client(timeout=30.0) as client:
            for i, batch in enumerate(batches):
                logger.info(f"Sending batch {i+1}/{len(batches)}...")
                
                # Prepare payload
                payload = {
                    'articles': batch
                }
                
                # Headers
                headers = {
                    'Content-Type': 'application/json'
                }
                
                # API key если есть
                if settings.BACKEND_API_KEY:
                    headers['X-API-Key'] = settings.BACKEND_API_KEY
                
                # POST request
                response = client.post(
                    backend_url,
                    json=payload,
                    headers=headers
                )
                
                response.raise_for_status()
                
                result = response.json()
                sent_count += result.get('created', len(batch))
                
                logger.info(f"✅ Batch {i+1} sent successfully")
        
        logger.info(f"✅ Total sent: {sent_count}/{len(articles)}")
        
        return sent_count
        
    except httpx.HTTPError as exc:
        logger.error(f"HTTP error sending to backend: {exc}")
        # Retry с экспоненциальной задержкой
        raise self.retry(exc=exc, countdown=60)
        
    except Exception as exc:
        logger.error(f"Error sending to backend: {exc}")
        raise self.retry(exc=exc, countdown=60)


# ===== HELPER FUNCTIONS =====

def deduplicate_articles(articles: List[Article]) -> List[Article]:
    """Удалить дубликаты статей.
    
    Проверяет по:
    1. URL (абсолютный)
    2. Content hash (если URLs разные)
    
    Args:
        articles: Список статей
    
    Returns:
        Уникальные статьи
    """
    seen_urls = set()
    seen_hashes = set()
    unique = []
    
    for article in articles:
        # Проверка по URL
        if settings.CHECK_DUPLICATES_BY_URL:
            if article.url in seen_urls:
                logger.debug(f"Duplicate URL: {article.url}")
                continue
            seen_urls.add(article.url)
        
        # Проверка по hash
        if settings.CHECK_DUPLICATES_BY_TITLE:
            if article.content_hash in seen_hashes:
                logger.debug(f"Duplicate content: {article.title}")
                continue
            seen_hashes.add(article.content_hash)
        
        unique.append(article)
    
    logger.info(f"Deduplication: {len(articles)} → {len(unique)}")
    
    return unique


# ===== USAGE EXAMPLES =====
"""
# ===== Вызов задач =====

from app.tasks.scraping_tasks import (
    scrape_all_sources,
    scrape_rss_feeds,
    scrape_source
)

# Sync (блокирует)
result = scrape_all_sources()
print(result)

# Async (не блокирует)
task = scrape_all_sources.delay()
print(f"Task ID: {task.id}")
print(f"Status: {task.status}")

# Получить результат
result = task.get(timeout=600)  # Ждать до 10 минут


# ===== RSS only =====

task = scrape_rss_feeds.delay()
articles = task.get()
print(f"Got {len(articles)} articles")


# ===== Specific source =====

task = scrape_source.delay('bbc')
articles = task.get()


# ===== Отправка в backend =====

from app.tasks.scraping_tasks import send_articles_to_backend

articles = [
    {
        'title': 'Test Article',
        'url': 'https://example.com/article',
        'content': 'Content...',
        # ... другие поля
    }
]

task = send_articles_to_backend.delay(articles)
sent_count = task.get()
print(f"Sent {sent_count} articles")


# ===== Проверка статуса =====

task = scrape_all_sources.delay()

while task.status != 'SUCCESS':
    print(f"Status: {task.status}")
    time.sleep(5)

result = task.result
print(f"Stats: {result}")


# ===== Retry вручную =====

from celery import current_app

# Retry конкретной задачи
task_id = 'abc123'
current_app.control.revoke(task_id)
task = scrape_all_sources.apply_async(task_id=task_id)
"""