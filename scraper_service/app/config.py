"""
Scraper Service Configuration

Все настройки для парсинга новостей.
"""

from pydantic_settings import BaseSettings
from typing import List, Dict, Optional
from pathlib import Path


class Settings(BaseSettings):
    """Settings для Scraper Service."""
    
    # ===== APP SETTINGS =====
    APP_NAME: str = "Smart News Scraper Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # ===== BACKEND API =====
    # URL Backend сервиса для отправки новостей
    BACKEND_URL: str = "http://localhost:8000"
    BACKEND_API_KEY: Optional[str] = None  # Если требуется авторизация
    
    # ===== ML SERVICE =====
    ML_SERVICE_URL: str = "http://localhost:8001"
    
    # ===== CELERY SETTINGS =====
    # Message broker (Redis или RabbitMQ)
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # Task settings
    CELERY_TASK_SERIALIZER: str = "json"
    CELERY_RESULT_SERIALIZER: str = "json"
    CELERY_ACCEPT_CONTENT: List[str] = ["json"]
    CELERY_TIMEZONE: str = "UTC"
    CELERY_ENABLE_UTC: bool = True
    
    # ===== SCRAPING SETTINGS =====
    
    # User Agent
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    
    # Request timeouts
    REQUEST_TIMEOUT: int = 30  # seconds
    
    # Retry settings
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # seconds
    
    # Rate limiting
    REQUESTS_PER_SECOND: float = 2.0  # Max 2 requests/second per source
    CONCURRENT_REQUESTS: int = 16  # Max concurrent requests
    
    # Download delays (вежливый скрапинг)
    DOWNLOAD_DELAY: float = 1.0  # seconds between requests
    
    # ===== SELENIUM SETTINGS =====
    # Для динамических страниц
    SELENIUM_HEADLESS: bool = True
    SELENIUM_TIMEOUT: int = 30
    CHROME_DRIVER_PATH: Optional[str] = None  # Auto-detect if None
    
    # ===== NEWS SOURCES =====
    
    # RSS Feeds
    RSS_FEEDS: Dict[str, str] = {
        "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
        "cnn": "http://rss.cnn.com/rss/edition.rss",
        "reuters": "https://www.reutersagency.com/feed/",
        "techcrunch": "https://techcrunch.com/feed/",
        "engadget": "https://www.engadget.com/rss.xml",
        "espn": "https://www.espn.com/espn/rss/news",
    }
    
    # News APIs
    NEWS_API_KEY: Optional[str] = None  # NewsAPI.org API key
    NEWS_API_SOURCES: List[str] = [
        "bbc-news",
        "cnn",
        "reuters",
        "techcrunch",
        "the-verge",
        "espn"
    ]
    
    # Web scraping sources
    WEB_SCRAPE_URLS: Dict[str, str] = {
        "bbc_tech": "https://www.bbc.com/news/technology",
        "guardian_tech": "https://www.theguardian.com/technology",
    }
    
    # ===== FILTERING SETTINGS =====
    
    # Минимальная длина статьи (слов)
    MIN_ARTICLE_LENGTH: int = 50
    
    # Языки для фильтрации
    ALLOWED_LANGUAGES: List[str] = ["en"]  # English only
    
    # Исключаемые слова в заголовках (спам)
    BLACKLIST_KEYWORDS: List[str] = [
        "advertisement",
        "sponsored",
        "promoted",
    ]
    
    # ===== CONTENT EXTRACTION =====
    
    # Извлекать изображения
    EXTRACT_IMAGES: bool = True
    
    # Максимальный размер изображения (MB)
    MAX_IMAGE_SIZE_MB: int = 5
    
    # Извлекать видео ссылки
    EXTRACT_VIDEOS: bool = False
    
    # ===== STORAGE SETTINGS =====
    
    # Локальное хранилище для изображений
    IMAGES_DIR: Path = Path("./data/images")
    
    # Кеш для предотвращения дубликатов
    CACHE_DIR: Path = Path("./data/cache")
    
    # ===== DEDUPLICATION =====
    
    # Проверять дубликаты по URL
    CHECK_DUPLICATES_BY_URL: bool = True
    
    # Проверять дубликаты по заголовку
    CHECK_DUPLICATES_BY_TITLE: bool = True
    
    # Similarity threshold для дубликатов (0.0-1.0)
    DUPLICATE_SIMILARITY_THRESHOLD: float = 0.9
    
    # ===== SCHEDULING =====
    
    # Как часто парсить (в минутах)
    SCRAPE_INTERVAL_MINUTES: int = 30
    
    # Парсить только новые статьи (за N часов)
    SCRAPE_LAST_N_HOURS: int = 24
    
    # ===== PROCESSING =====
    
    # Отправлять в ML сервис для обработки
    SEND_TO_ML_SERVICE: bool = True
    
    # Batch size для отправки в Backend
    BATCH_SIZE: int = 10
    
    # ===== DATABASE (Local Cache) =====
    
    # SQLite для локального кеша
    DATABASE_URL: str = "sqlite:///./data/scraper_cache.db"
    
    # PostgreSQL (если используем)
    # DATABASE_URL: str = "postgresql://user:password@localhost/scraper_db"
    
    # ===== LOGGING =====
    
    LOG_LEVEL: str = "INFO"  # DEBUG, INFO, WARNING, ERROR
    LOG_FORMAT: str = "json"  # json или text
    LOG_FILE: str = "./logs/scraper.log"
    
    # ===== MONITORING =====
    
    SENTRY_DSN: Optional[str] = None  # Sentry для error tracking
    
    # ===== PROXY SETTINGS (опционально) =====
    
    USE_PROXY: bool = False
    PROXY_URL: Optional[str] = None  # "http://proxy:port"
    PROXY_LIST: List[str] = []  # Ротация прокси
    
    # ===== CATEGORIES MAPPING =====
    
    # Маппинг source → category
    SOURCE_CATEGORY_MAP: Dict[str, str] = {
        "techcrunch": "technology",
        "the-verge": "technology",
        "engadget": "technology",
        "espn": "sports",
        "bbc-sport": "sports",
    }
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False


# ===== GLOBAL INSTANCE =====
settings = Settings()


# ===== HELPER FUNCTIONS =====

def get_rss_feed_url(source_name: str) -> Optional[str]:
    """Получить RSS URL для источника.
    
    Args:
        source_name: Название источника
    
    Returns:
        RSS URL или None
    """
    return settings.RSS_FEEDS.get(source_name)


def get_all_sources() -> List[str]:
    """Получить список всех источников.
    
    Returns:
        Список названий источников
    """
    sources = set()
    
    # RSS feeds
    sources.update(settings.RSS_FEEDS.keys())
    
    # News API sources
    sources.update(settings.NEWS_API_SOURCES)
    
    # Web scrape sources
    sources.update(settings.WEB_SCRAPE_URLS.keys())
    
    return sorted(list(sources))


def is_allowed_language(language: str) -> bool:
    """Проверить разрешен ли язык.
    
    Args:
        language: Код языка (en, ru, и т.д.)
    
    Returns:
        True если разрешен
    """
    return language in settings.ALLOWED_LANGUAGES


def is_blacklisted(title: str) -> bool:
    """Проверить содержит ли заголовок запрещенные слова.
    
    Args:
        title: Заголовок статьи
    
    Returns:
        True если в черном списке
    """
    title_lower = title.lower()
    return any(keyword in title_lower for keyword in settings.BLACKLIST_KEYWORDS)


# ===== USAGE EXAMPLES =====
"""
# Import settings
from app.config import settings

# Use settings
print(settings.APP_NAME)
print(settings.CELERY_BROKER_URL)

# Helper functions
from app.config import get_all_sources, is_blacklisted

sources = get_all_sources()
print(f"Total sources: {len(sources)}")

title = "Advertisement: Buy now!"
if is_blacklisted(title):
    print("Spam detected!")
"""