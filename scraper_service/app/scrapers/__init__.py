"""
Scrapers Module

Парсеры для различных источников новостей.
"""

from app.scrapers.base_scraper import BaseScraper, Article
from app.scrapers.rss_scraper import RSSFeedScraper, MultiFeedScraper
from app.scrapers.api_scraper import NewsAPIScraper


__all__ = [
    "BaseScraper",
    "Article",
    "RSSFeedScraper",
    "MultiFeedScraper",
    "NewsAPIScraper",
]