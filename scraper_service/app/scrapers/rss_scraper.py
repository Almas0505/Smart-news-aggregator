"""
RSS Feed Scraper

Парсер для RSS/Atom лент новостей.

RSS (Really Simple Syndication) - стандартный формат для распространения новостей.
Большинство новостных сайтов предоставляют RSS ленты.
"""

import feedparser
from typing import List, Optional
from datetime import datetime
import logging

from app.scrapers.base_scraper import BaseScraper, Article
from app.config import settings


logger = logging.getLogger(__name__)


class RSSFeedScraper(BaseScraper):
    """Парсер RSS/Atom лент.
    
    ====== ЧТО ТАКОЕ RSS? ======
    
    RSS - XML формат для публикации обновлений.
    
    Структура RSS:
    ```xml
    <rss version="2.0">
      <channel>
        <title>Site Name</title>
        <item>
          <title>Article Title</title>
          <link>https://example.com/article</link>
          <description>Article summary...</description>
          <pubDate>Mon, 01 Jan 2024 12:00:00 GMT</pubDate>
          <author>John Doe</author>
        </item>
      </channel>
    </rss>
    ```
    
    Преимущества RSS:
    + Стандартизированный формат
    + Не нужен HTML parsing
    + Официально поддерживается сайтами
    + Быстрый и надежный
    
    Библиотека feedparser:
    - Автоматически определяет формат (RSS/Atom)
    - Парсит даты
    - Обрабатывает ошибки
    """
    
    def __init__(
        self,
        source_name: str,
        feed_url: str,
        category: Optional[str] = None
    ):
        """Инициализация RSS парсера.
        
        Args:
            source_name: Название источника (bbc, cnn)
            feed_url: URL RSS ленты
            category: Категория новостей (опционально)
        """
        super().__init__(source_name, feed_url)
        self.feed_url = feed_url
        self.category = category
        
        logger.info(f"RSS scraper initialized: {source_name}")
    
    def parse_date(self, date_string: str) -> Optional[datetime]:
        """Парсить дату из RSS.
        
        Args:
            date_string: Строка с датой
        
        Returns:
            datetime object или None
        """
        try:
            # feedparser автоматически парсит даты
            # Возвращает struct_time
            import time
            time_struct = feedparser._parse_date(date_string)
            if time_struct:
                return datetime(*time_struct[:6])
        except:
            pass
        
        return None
    
    def scrape(self) -> List[Article]:
        """Парсить RSS ленту.
        
        Returns:
            Список статей
        """
        articles = []
        
        try:
            logger.info(f"Fetching RSS feed: {self.feed_url}")
            
            # Парсим RSS feed
            # feedparser автоматически загружает и парсит
            feed = feedparser.parse(self.feed_url)
            
            # Проверяем на ошибки
            if feed.bozo:  # bozo = есть ошибки парсинга
                logger.warning(f"RSS feed has errors: {feed.bozo_exception}")
            
            # Итерируемся по записям
            for entry in feed.entries:
                try:
                    article = self._parse_entry(entry)
                    if article:
                        articles.append(article)
                        
                except Exception as e:
                    logger.error(f"Error parsing entry: {e}")
                    continue
            
            logger.info(f"Parsed {len(articles)} articles from RSS")
            
        except Exception as e:
            logger.error(f"Error fetching RSS feed: {e}")
        
        return articles
    
    def _parse_entry(self, entry) -> Optional[Article]:
        """Парсить одну запись RSS.
        
        Args:
            entry: feedparser entry object
        
        Returns:
            Article или None
        """
        # Заголовок (обязательное поле)
        title = entry.get('title', '').strip()
        if not title:
            return None
        
        # URL (обязательное поле)
        url = entry.get('link', '').strip()
        if not url:
            return None
        
        # Описание/summary
        summary = entry.get('summary', '') or entry.get('description', '')
        summary = self.clean_text(summary)
        
        # Полный контент (если доступен)
        content = ''
        if hasattr(entry, 'content'):
            content = entry.content[0].value if entry.content else ''
        
        # Если нет полного контента, используем summary
        if not content:
            content = summary
        
        content = self.clean_text(content)
        
        # Автор
        author = entry.get('author', None)
        
        # Дата публикации
        published_at = None
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            try:
                published_at = datetime(*entry.published_parsed[:6])
            except:
                pass
        
        # Если нет даты, используем текущую
        if not published_at:
            published_at = datetime.utcnow()
        
        # Проверяем свежесть
        if not self.is_recent(published_at):
            logger.debug(f"Skipping old article: {title}")
            return None
        
        # Изображение
        image_url = None
        
        # Пробуем разные поля
        if hasattr(entry, 'media_content'):
            # Media RSS extension
            media = entry.media_content[0] if entry.media_content else None
            if media:
                image_url = media.get('url')
        
        if not image_url and hasattr(entry, 'media_thumbnail'):
            # Thumbnail
            thumbnail = entry.media_thumbnail[0] if entry.media_thumbnail else None
            if thumbnail:
                image_url = thumbnail.get('url')
        
        if not image_url and hasattr(entry, 'enclosures'):
            # Enclosures (attachments)
            for enclosure in entry.enclosures:
                if enclosure.get('type', '').startswith('image/'):
                    image_url = enclosure.get('href')
                    break
        
        # Теги
        tags = []
        if hasattr(entry, 'tags'):
            tags = [tag.term for tag in entry.tags if hasattr(tag, 'term')]
        
        # Определяем язык
        language = self.detect_language(title + ' ' + content)
        
        # Создаем Article
        article = Article(
            title=title,
            url=url,
            content=content,
            summary=summary,
            author=author,
            published_at=published_at,
            source=self.source_name,
            category=self.category,
            image_url=image_url,
            language=language,
            tags=tags
        )
        
        return article


# ===== MULTI-FEED SCRAPER =====

class MultiFeedScraper:
    """Парсер для множества RSS лент одновременно."""
    
    def __init__(self):
        """Инициализация."""
        self.scrapers = []
        self._setup_scrapers()
    
    def _setup_scrapers(self):
        """Настроить парсеры для всех RSS лент из config."""
        for source_name, feed_url in settings.RSS_FEEDS.items():
            # Определяем категорию если есть в маппинге
            category = settings.SOURCE_CATEGORY_MAP.get(source_name)
            
            scraper = RSSFeedScraper(
                source_name=source_name,
                feed_url=feed_url,
                category=category
            )
            
            self.scrapers.append(scraper)
        
        logger.info(f"Initialized {len(self.scrapers)} RSS scrapers")
    
    def scrape_all(self) -> List[Article]:
        """Парсить все RSS ленты.
        
        Returns:
            Список всех статей
        """
        all_articles = []
        
        for scraper in self.scrapers:
            try:
                articles = scraper.run()
                all_articles.extend(articles)
                
                logger.info(
                    f"Scraped {len(articles)} articles from {scraper.source_name}"
                )
                
            except Exception as e:
                logger.error(f"Error scraping {scraper.source_name}: {e}")
                continue
        
        logger.info(f"Total articles scraped: {len(all_articles)}")
        
        return all_articles
    
    def scrape_source(self, source_name: str) -> List[Article]:
        """Парсить конкретный источник.
        
        Args:
            source_name: Название источника
        
        Returns:
            Список статей
        """
        for scraper in self.scrapers:
            if scraper.source_name == source_name:
                return scraper.run()
        
        logger.warning(f"Source not found: {source_name}")
        return []


# ===== USAGE EXAMPLES =====
"""
# ===== Single Feed =====

from app.scrapers.rss_scraper import RSSFeedScraper

# BBC News RSS
scraper = RSSFeedScraper(
    source_name='bbc',
    feed_url='http://feeds.bbci.co.uk/news/rss.xml',
    category='news'
)

articles = scraper.run()

for article in articles:
    print(f"{article.title}")
    print(f"  URL: {article.url}")
    print(f"  Published: {article.published_at}")
    print(f"  Author: {article.author}")
    print()


# ===== Multiple Feeds =====

from app.scrapers.rss_scraper import MultiFeedScraper

# Парсим все RSS feeds из config
multi_scraper = MultiFeedScraper()

# Все источники
all_articles = multi_scraper.scrape_all()
print(f"Total articles: {len(all_articles)}")

# Конкретный источник
bbc_articles = multi_scraper.scrape_source('bbc')
print(f"BBC articles: {len(bbc_articles)}")


# ===== Группировка по источникам =====

from collections import defaultdict

articles_by_source = defaultdict(list)

for article in all_articles:
    articles_by_source[article.source].append(article)

for source, articles in articles_by_source.items():
    print(f"{source}: {len(articles)} articles")


# ===== Фильтрация =====

# Только tech новости
tech_articles = [
    a for a in all_articles
    if a.category == 'technology'
]

# Только свежие (последние 6 часов)
from datetime import datetime, timedelta

recent_cutoff = datetime.utcnow() - timedelta(hours=6)
recent_articles = [
    a for a in all_articles
    if a.published_at > recent_cutoff
]

# С изображениями
articles_with_images = [
    a for a in all_articles
    if a.image_url
]
"""