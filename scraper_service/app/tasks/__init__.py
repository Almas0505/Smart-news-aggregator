"""
Tasks Module

Celery задачи для Scraper Service.
"""

from app.tasks.scraping_tasks import (
    scrape_all_sources,
    scrape_rss_feeds,
    scrape_news_api,
    scrape_source,
    send_articles_to_backend
)

from app.tasks.processing_tasks import (
    process_article,
    process_articles_batch,
    classify_article,
    analyze_sentiment,
    extract_entities,
    generate_summary
)

from app.tasks.cleanup_tasks import (
    cleanup_old_data,
    cleanup_cache,
    cleanup_celery_results,
    check_disk_space
)


__all__ = [
    # Scraping
    "scrape_all_sources",
    "scrape_rss_feeds",
    "scrape_news_api",
    "scrape_source",
    "send_articles_to_backend",
    
    # Processing
    "process_article",
    "process_articles_batch",
    "classify_article",
    "analyze_sentiment",
    "extract_entities",
    "generate_summary",
    
    # Cleanup
    "cleanup_old_data",
    "cleanup_cache",
    "cleanup_celery_results",
    "check_disk_space",
]