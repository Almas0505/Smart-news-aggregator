"""
Base Scraper

Базовый класс для всех парсеров новостей.

Все специфичные парсеры наследуются от этого класса.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging
import hashlib
from urllib.parse import urlparse
import time

import requests
from bs4 import BeautifulSoup
from langdetect import detect, LangDetectException

from app.config import settings


logger = logging.getLogger(__name__)


# ===== DATA MODELS =====

class Article:
    """Модель статьи."""
    
    def __init__(
        self,
        title: str,
        url: str,
        content: str = "",
        summary: str = "",
        author: Optional[str] = None,
        published_at: Optional[datetime] = None,
        source: str = "",
        category: Optional[str] = None,
        image_url: Optional[str] = None,
        language: str = "en",
        tags: Optional[List[str]] = None
    ):
        """Инициализация статьи.
        
        Args:
            title: Заголовок
            url: URL статьи (уникальный идентификатор)
            content: Полный текст
            summary: Краткое описание
            author: Автор
            published_at: Дата публикации
            source: Источник (bbc, cnn, и т.д.)
            category: Категория (technology, sports, и т.д.)
            image_url: URL главного изображения
            language: Язык статьи
            tags: Теги/ключевые слова
        """
        self.title = title
        self.url = url
        self.content = content
        self.summary = summary
        self.author = author
        self.published_at = published_at or datetime.utcnow()
        self.source = source
        self.category = category
        self.image_url = image_url
        self.language = language
        self.tags = tags or []
        
        # Генерируем hash для дедупликации
        self.content_hash = self._generate_hash()
        
        # Метаданные
        self.scraped_at = datetime.utcnow()
    
    def _generate_hash(self) -> str:
        """Генерировать hash статьи для проверки дубликатов.
        
        Returns:
            MD5 hash
        """
        # Используем title + url для уникальности
        content = f"{self.title}{self.url}".encode('utf-8')
        return hashlib.md5(content).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        """Конвертировать в словарь для API.
        
        Returns:
            Словарь с данными статьи
        """
        return {
            'title': self.title,
            'url': self.url,
            'content': self.content,
            'summary': self.summary,
            'author': self.author,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'source': self.source,
            'category': self.category,
            'image_url': self.image_url,
            'language': self.language,
            'tags': self.tags,
            'content_hash': self.content_hash,
            'scraped_at': self.scraped_at.isoformat()
        }
    
    def is_valid(self) -> bool:
        """Проверить валидность статьи.
        
        Returns:
            True если статья валидна
        """
        # Обязательные поля
        if not self.title or not self.url:
            return False
        
        # Минимальная длина контента
        word_count = len(self.content.split())
        if word_count < settings.MIN_ARTICLE_LENGTH:
            return False
        
        # Проверка языка
        if not settings.is_allowed_language(self.language):
            return False
        
        # Проверка черного списка
        if settings.is_blacklisted(self.title):
            return False
        
        return True
    
    def __repr__(self) -> str:
        return f"Article(title='{self.title[:50]}...', source='{self.source}')"


# ===== BASE SCRAPER CLASS =====

class BaseScraper(ABC):
    """Базовый класс для всех парсеров.
    
    Все парсеры должны наследоваться от этого класса и
    реализовывать метод scrape().
    """
    
    def __init__(
        self,
        source_name: str,
        source_url: Optional[str] = None
    ):
        """Инициализация парсера.
        
        Args:
            source_name: Название источника (bbc, cnn, и т.д.)
            source_url: URL источника
        """
        self.source_name = source_name
        self.source_url = source_url
        self.session = self._create_session()
        
        logger.info(f"Initialized scraper: {source_name}")
    
    def _create_session(self) -> requests.Session:
        """Создать HTTP session с настройками.
        
        Returns:
            Configured session
        """
        session = requests.Session()
        
        # Headers
        session.headers.update({
            'User-Agent': settings.USER_AGENT,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Proxy (если используется)
        if settings.USE_PROXY and settings.PROXY_URL:
            session.proxies = {
                'http': settings.PROXY_URL,
                'https': settings.PROXY_URL
            }
        
        return session
    
    def fetch_page(
        self,
        url: str,
        retry: int = 0
    ) -> Optional[str]:
        """Загрузить HTML страницы.
        
        Args:
            url: URL страницы
            retry: Номер попытки (для рекурсии)
        
        Returns:
            HTML content или None
        """
        try:
            logger.debug(f"Fetching: {url}")
            
            response = self.session.get(
                url,
                timeout=settings.REQUEST_TIMEOUT
            )
            
            response.raise_for_status()
            
            # Задержка для вежливого скрапинга
            time.sleep(settings.DOWNLOAD_DELAY)
            
            return response.text
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            
            # Retry logic
            if retry < settings.MAX_RETRIES:
                logger.info(f"Retrying... (attempt {retry + 1}/{settings.MAX_RETRIES})")
                time.sleep(settings.RETRY_DELAY)
                return self.fetch_page(url, retry + 1)
            
            return None
    
    def parse_html(self, html: str) -> BeautifulSoup:
        """Парсить HTML через BeautifulSoup.
        
        Args:
            html: HTML content
        
        Returns:
            BeautifulSoup object
        """
        return BeautifulSoup(html, 'lxml')
    
    def extract_domain(self, url: str) -> str:
        """Извлечь домен из URL.
        
        Args:
            url: URL
        
        Returns:
            Domain name
        """
        parsed = urlparse(url)
        return parsed.netloc
    
    def detect_language(self, text: str) -> str:
        """Определить язык текста.
        
        Args:
            text: Текст
        
        Returns:
            Код языка (en, ru, и т.д.)
        """
        try:
            return detect(text)
        except LangDetectException:
            return "unknown"
    
    def clean_text(self, text: str) -> str:
        """Очистить текст от лишних символов.
        
        Args:
            text: Исходный текст
        
        Returns:
            Очищенный текст
        """
        # Убираем множественные пробелы
        text = ' '.join(text.split())
        
        # Убираем лишние переносы строк
        text = text.replace('\n\n\n', '\n\n')
        
        return text.strip()
    
    def is_recent(
        self,
        published_at: datetime,
        hours: int = None
    ) -> bool:
        """Проверить что статья свежая.
        
        Args:
            published_at: Дата публикации
            hours: Максимальный возраст в часах
        
        Returns:
            True если статья свежая
        """
        if hours is None:
            hours = settings.SCRAPE_LAST_N_HOURS
        
        age = datetime.utcnow() - published_at
        return age < timedelta(hours=hours)
    
    def validate_article(self, article: Article) -> bool:
        """Валидировать статью.
        
        Args:
            article: Статья
        
        Returns:
            True если валидна
        """
        return article.is_valid()
    
    @abstractmethod
    def scrape(self) -> List[Article]:
        """Парсить новости из источника.
        
        Этот метод ДОЛЖЕН быть реализован в подклассе!
        
        Returns:
            Список статей
        """
        raise NotImplementedError("Subclass must implement scrape() method")
    
    def run(self) -> List[Article]:
        """Запустить парсинг с валидацией.
        
        Returns:
            Список валидных статей
        """
        logger.info(f"Starting scrape: {self.source_name}")
        
        try:
            # Парсим
            articles = self.scrape()
            
            logger.info(f"Scraped {len(articles)} articles")
            
            # Фильтруем невалидные
            valid_articles = [a for a in articles if self.validate_article(a)]
            
            logger.info(f"Valid articles: {len(valid_articles)}")
            
            return valid_articles
            
        except Exception as e:
            logger.error(f"Scrape failed for {self.source_name}: {e}")
            return []
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(source='{self.source_name}')"


# ===== USAGE EXAMPLES =====
"""
# ===== Создание своего парсера =====

from app.scrapers.base_scraper import BaseScraper, Article

class MyCustomScraper(BaseScraper):
    '''Кастомный парсер для сайта.'''
    
    def __init__(self):
        super().__init__(
            source_name='mysite',
            source_url='https://example.com'
        )
    
    def scrape(self) -> List[Article]:
        '''Парсинг новостей.'''
        articles = []
        
        # 1. Загружаем страницу
        html = self.fetch_page(self.source_url)
        if not html:
            return articles
        
        # 2. Парсим HTML
        soup = self.parse_html(html)
        
        # 3. Находим статьи
        for item in soup.find_all('article'):
            title = item.find('h2').text
            url = item.find('a')['href']
            content = item.find('p').text
            
            # 4. Создаем Article
            article = Article(
                title=self.clean_text(title),
                url=url,
                content=self.clean_text(content),
                source=self.source_name,
                language=self.detect_language(content)
            )
            
            articles.append(article)
        
        return articles


# ===== Использование =====

scraper = MyCustomScraper()
articles = scraper.run()

for article in articles:
    print(f"{article.title} - {article.url}")
    print(article.to_dict())
"""