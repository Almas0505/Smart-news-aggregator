"""
News API Scraper

Парсер через News API (newsapi.org).

News API - сервис агрегации новостей от 80000+ источников.
Предоставляет REST API для доступа к новостям.
"""

from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

from newsapi import NewsApiClient
from newsapi.newsapi_exception import NewsAPIException

from app.scrapers.base_scraper import BaseScraper, Article
from app.config import settings


logger = logging.getLogger(__name__)


class NewsAPIScraper(BaseScraper):
    """Парсер через News API.
    
    ====== NEWS API ======
    
    Website: https://newsapi.org
    
    Возможности:
    - 80000+ новостных источников
    - Поиск по ключевым словам
    - Фильтрация по источникам, языку, дате
    - Top headlines
    - Everything (все статьи)
    
    Лимиты FREE плана:
    - 100 requests/day
    - Только последние 30 дней
    - Задержка ~15 минут
    
    API Key:
    Регистрация на newsapi.org → получаем API key
    
    Endpoints:
    1. /top-headlines - главные новости
    2. /everything - все статьи
    3. /sources - список источников
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        sources: Optional[List[str]] = None,
        category: Optional[str] = None,
        country: str = 'us'
    ):
        """Инициализация News API scraper.
        
        Args:
            api_key: API ключ (из settings если не указан)
            sources: Список источников для парсинга
            category: Категория новостей
            country: Код страны (us, gb, и т.д.)
        """
        super().__init__('newsapi', 'https://newsapi.org')
        
        # API key
        self.api_key = api_key or settings.NEWS_API_KEY
        if not self.api_key:
            raise ValueError(
                "NEWS_API_KEY not set! "
                "Get it from https://newsapi.org and set in .env"
            )
        
        # Инициализируем клиент
        try:
            self.client = NewsApiClient(api_key=self.api_key)
        except Exception as e:
            logger.error(f"Failed to initialize NewsAPI client: {e}")
            raise
        
        self.sources = sources or settings.NEWS_API_SOURCES
        self.category = category
        self.country = country
        
        logger.info("NewsAPI scraper initialized")
    
    def scrape(self) -> List[Article]:
        """Парсить новости через News API.
        
        Returns:
            Список статей
        """
        articles = []
        
        # 1. Парсим top headlines
        articles.extend(self._scrape_top_headlines())
        
        # 2. Парсим everything (все статьи)
        # articles.extend(self._scrape_everything())
        
        return articles
    
    def _scrape_top_headlines(self) -> List[Article]:
        """Парсить топ новости.
        
        Returns:
            Список статей
        """
        articles = []
        
        try:
            logger.info("Fetching top headlines from NewsAPI")
            
            # Запрос к API
            response = self.client.get_top_headlines(
                sources=','.join(self.sources),
                language='en',
                page_size=100  # Max 100
            )
            
            # Обрабатываем результаты
            if response['status'] == 'ok':
                for item in response['articles']:
                    article = self._parse_api_article(item)
                    if article:
                        articles.append(article)
            
            logger.info(f"Fetched {len(articles)} top headlines")
            
        except NewsAPIException as e:
            logger.error(f"NewsAPI error: {e}")
        except Exception as e:
            logger.error(f"Error fetching top headlines: {e}")
        
        return articles
    
    def _scrape_everything(
        self,
        query: Optional[str] = None,
        from_date: Optional[datetime] = None
    ) -> List[Article]:
        """Парсить все статьи (с фильтрами).
        
        Args:
            query: Поисковый запрос
            from_date: С какой даты
        
        Returns:
            Список статей
        """
        articles = []
        
        try:
            logger.info("Fetching everything from NewsAPI")
            
            # Дата по умолчанию - последние 24 часа
            if not from_date:
                from_date = datetime.utcnow() - timedelta(hours=24)
            
            # Запрос
            response = self.client.get_everything(
                q=query or 'news',  # Поисковый запрос
                sources=','.join(self.sources),
                language='en',
                from_param=from_date.isoformat(),
                sort_by='publishedAt',  # Сортировка по дате
                page_size=100
            )
            
            if response['status'] == 'ok':
                for item in response['articles']:
                    article = self._parse_api_article(item)
                    if article:
                        articles.append(article)
            
            logger.info(f"Fetched {len(articles)} articles")
            
        except NewsAPIException as e:
            logger.error(f"NewsAPI error: {e}")
        except Exception as e:
            logger.error(f"Error fetching everything: {e}")
        
        return articles
    
    def _parse_api_article(self, item: Dict) -> Optional[Article]:
        """Парсить статью из API response.
        
        Args:
            item: Словарь с данными статьи
        
        Returns:
            Article или None
        """
        # Обязательные поля
        title = item.get('title', '').strip()
        url = item.get('url', '').strip()
        
        if not title or not url:
            return None
        
        # Description
        description = item.get('description', '')
        
        # Content (часто обрезан в free плане)
        content = item.get('content', '')
        
        # Если нет контента, используем description
        if not content or len(content) < 100:
            content = description
        
        # Автор
        author = item.get('author')
        
        # Дата
        published_at = None
        pub_date_str = item.get('publishedAt')
        if pub_date_str:
            try:
                # Format: "2024-01-01T12:00:00Z"
                published_at = datetime.fromisoformat(
                    pub_date_str.replace('Z', '+00:00')
                )
            except:
                pass
        
        # Источник
        source_info = item.get('source', {})
        source_name = source_info.get('id') or source_info.get('name', 'newsapi')
        
        # Изображение
        image_url = item.get('urlToImage')
        
        # Определяем язык
        language = self.detect_language(title + ' ' + content)
        
        # Создаем Article
        article = Article(
            title=self.clean_text(title),
            url=url,
            content=self.clean_text(content),
            summary=self.clean_text(description),
            author=author,
            published_at=published_at or datetime.utcnow(),
            source=source_name,
            category=self.category,
            image_url=image_url,
            language=language
        )
        
        return article
    
    def search(
        self,
        query: str,
        from_date: Optional[datetime] = None,
        to_date: Optional[datetime] = None
    ) -> List[Article]:
        """Поиск новостей по ключевым словам.
        
        Args:
            query: Поисковый запрос
            from_date: С какой даты
            to_date: До какой даты
        
        Returns:
            Список статей
        """
        articles = []
        
        try:
            logger.info(f"Searching NewsAPI: '{query}'")
            
            # Даты по умолчанию
            if not from_date:
                from_date = datetime.utcnow() - timedelta(days=7)
            
            # Запрос
            response = self.client.get_everything(
                q=query,
                language='en',
                from_param=from_date.isoformat(),
                to=to_date.isoformat() if to_date else None,
                sort_by='relevancy',
                page_size=100
            )
            
            if response['status'] == 'ok':
                for item in response['articles']:
                    article = self._parse_api_article(item)
                    if article:
                        articles.append(article)
            
            logger.info(f"Found {len(articles)} articles")
            
        except NewsAPIException as e:
            logger.error(f"NewsAPI error: {e}")
        except Exception as e:
            logger.error(f"Error searching: {e}")
        
        return articles
    
    def get_sources(self) -> List[Dict]:
        """Получить список доступных источников.
        
        Returns:
            Список источников с метаданными
        """
        try:
            response = self.client.get_sources(
                language='en',
                country=self.country
            )
            
            if response['status'] == 'ok':
                return response['sources']
            
        except NewsAPIException as e:
            logger.error(f"NewsAPI error: {e}")
        except Exception as e:
            logger.error(f"Error getting sources: {e}")
        
        return []


# ===== USAGE EXAMPLES =====
"""
# ===== Basic Usage =====

from app.scrapers.api_scraper import NewsAPIScraper

# Инициализация (API key из .env)
scraper = NewsAPIScraper(
    sources=['bbc-news', 'cnn', 'techcrunch']
)

# Парсинг top headlines
articles = scraper.run()

for article in articles:
    print(f"{article.title}")
    print(f"  Source: {article.source}")
    print(f"  Published: {article.published_at}")
    print()


# ===== Search =====

# Поиск по ключевым словам
ai_articles = scraper.search('artificial intelligence')
print(f"Found {len(ai_articles)} AI articles")

# Поиск с датами
from datetime import datetime, timedelta

last_week = datetime.utcnow() - timedelta(days=7)
recent_articles = scraper.search(
    'technology',
    from_date=last_week
)


# ===== Get Sources =====

# Список всех доступных источников
sources = scraper.get_sources()

print("Available sources:")
for source in sources[:10]:  # Первые 10
    print(f"- {source['name']} ({source['id']})")
    print(f"  Category: {source['category']}")
    print(f"  Description: {source['description']}")
    print()


# ===== Category Filtering =====

# Только tech новости
tech_scraper = NewsAPIScraper(
    sources=['techcrunch', 'the-verge', 'wired'],
    category='technology'
)

tech_articles = tech_scraper.run()


# ===== Multiple Categories =====

categories = {
    'technology': ['techcrunch', 'the-verge'],
    'business': ['bloomberg', 'financial-times'],
    'sports': ['espn', 'bbc-sport']
}

all_articles = []

for category, sources in categories.items():
    scraper = NewsAPIScraper(
        sources=sources,
        category=category
    )
    articles = scraper.run()
    all_articles.extend(articles)

print(f"Total articles: {len(all_articles)}")


# ===== Rate Limiting =====

# NewsAPI имеет лимиты:
# - Free: 100 requests/day
# - Developer: 500 requests/day
# - Business: unlimited

# Используйте кеширование!
from diskcache import Cache

cache = Cache('./cache')

@cache.memoize(expire=3600)  # Cache на 1 час
def get_news():
    scraper = NewsAPIScraper()
    return scraper.run()

articles = get_news()  # Закешируется
articles = get_news()  # Из кеша!
"""