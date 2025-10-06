"""
Scraper Service Main Application

Entry point для управления парсингом новостей.

====== USAGE ======

# CLI commands:
python -m app.main scrape-all        # Парсить все источники
python -m app.main scrape-rss        # Только RSS
python -m app.main scrape-api        # Только News API
python -m app.main scrape bbc        # Конкретный источник
python -m app.main list-sources      # Список источников
python -m app.main test              # Тест парсинга

# Celery commands:
celery -A app.celery_app worker -B --loglevel=info
celery -A app.celery_app flower      # Monitoring UI
"""

import click
import logging
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich import print as rprint

from app.config import settings, get_all_sources
from app.scrapers.rss_scraper import MultiFeedScraper
from app.scrapers.api_scraper import NewsAPIScraper
from app.tasks.scraping_tasks import (
    scrape_all_sources,
    scrape_rss_feeds,
    scrape_source
)


# Setup logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Rich console для красивого вывода
console = Console()


# ===== CLI APPLICATION =====

@click.group()
@click.version_option(version=settings.APP_VERSION)
def cli():
    """Smart News Scraper Service CLI.
    
    Инструмент для парсинга новостей из различных источников.
    """
    pass


# ===== SCRAPING COMMANDS =====

@cli.command()
@click.option('--async', 'use_async', is_flag=True, help='Асинхронный запуск через Celery')
def scrape_all(use_async: bool):
    """Парсить ВСЕ источники новостей."""
    console.print("\n[bold blue]🕷️  Starting full scrape...[/bold blue]\n")
    
    if use_async:
        # Async через Celery
        task = scrape_all_sources.delay()
        console.print(f"[green]✅ Task started: {task.id}[/green]")
        console.print(f"[yellow]Status: {task.status}[/yellow]")
        
        # Ждем результат
        console.print("[yellow]Waiting for results...[/yellow]")
        stats = task.get(timeout=600)  # 10 минут max
        
        display_scrape_stats(stats)
        
    else:
        # Sync запуск
        stats = scrape_all_sources()
        display_scrape_stats(stats)


@cli.command()
def scrape_rss():
    """Парсить только RSS ленты."""
    console.print("\n[bold blue]📰 Scraping RSS feeds...[/bold blue]\n")
    
    scraper = MultiFeedScraper()
    articles = scraper.scrape_all()
    
    console.print(f"[green]✅ Scraped {len(articles)} articles from RSS[/green]\n")
    
    # Показываем примеры
    if articles:
        display_articles_table(articles[:10])


@cli.command()
def scrape_api():
    """Парсить через News API."""
    if not settings.NEWS_API_KEY:
        console.print("[red]❌ NEWS_API_KEY not set![/red]")
        console.print("[yellow]Set it in .env file or environment variables[/yellow]")
        return
    
    console.print("\n[bold blue]📡 Scraping News API...[/bold blue]\n")
    
    scraper = NewsAPIScraper()
    articles = scraper.run()
    
    console.print(f"[green]✅ Scraped {len(articles)} articles from News API[/green]\n")
    
    if articles:
        display_articles_table(articles[:10])


@cli.command()
@click.argument('source_name')
def scrape(source_name: str):
    """Парсить конкретный источник.
    
    Example: python -m app.main scrape bbc
    """
    console.print(f"\n[bold blue]🎯 Scraping {source_name}...[/bold blue]\n")
    
    task = scrape_source.delay(source_name)
    articles_dict = task.get(timeout=120)
    
    console.print(f"[green]✅ Scraped {len(articles_dict)} articles[/green]\n")
    
    if articles_dict:
        # Конвертируем dict обратно в Article для отображения
        from app.scrapers.base_scraper import Article
        articles = [
            Article(
                title=a['title'],
                url=a['url'],
                content=a.get('content', ''),
                source=a.get('source', source_name)
            )
            for a in articles_dict[:10]
        ]
        display_articles_table(articles)


# ===== INFO COMMANDS =====

@cli.command()
def list_sources():
    """Показать список всех доступных источников."""
    console.print("\n[bold blue]📋 Available News Sources[/bold blue]\n")
    
    # RSS Feeds
    console.print("[bold yellow]RSS Feeds:[/bold yellow]")
    for name, url in settings.RSS_FEEDS.items():
        console.print(f"  • {name:20} {url}")
    
    console.print()
    
    # News API
    console.print("[bold yellow]News API Sources:[/bold yellow]")
    for source in settings.NEWS_API_SOURCES:
        console.print(f"  • {source}")
    
    console.print()
    
    total = len(get_all_sources())
    console.print(f"[green]Total sources: {total}[/green]\n")


@cli.command()
def config_info():
    """Показать текущую конфигурацию."""
    console.print("\n[bold blue]⚙️  Configuration[/bold blue]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    table.add_row("App Name", settings.APP_NAME)
    table.add_row("Version", settings.APP_VERSION)
    table.add_row("Debug", str(settings.DEBUG))
    table.add_row("Backend URL", settings.BACKEND_URL)
    table.add_row("ML Service URL", settings.ML_SERVICE_URL)
    table.add_row("Celery Broker", settings.CELERY_BROKER_URL)
    table.add_row("Scrape Interval", f"{settings.SCRAPE_INTERVAL_MINUTES} min")
    table.add_row("Min Article Length", f"{settings.MIN_ARTICLE_LENGTH} words")
    table.add_row("Allowed Languages", ", ".join(settings.ALLOWED_LANGUAGES))
    
    console.print(table)
    console.print()


# ===== TEST COMMANDS =====

@cli.command()
@click.option('--source', default='bbc', help='Источник для теста')
def test(source: str):
    """Тестовый запуск парсинга."""
    console.print(f"\n[bold blue]🧪 Testing scraper: {source}[/bold blue]\n")
    
    try:
        # Пробуем RSS
        rss_url = settings.RSS_FEEDS.get(source)
        if rss_url:
            from app.scrapers.rss_scraper import RSSFeedScraper
            
            scraper = RSSFeedScraper(source, rss_url)
            articles = scraper.run()
            
            console.print(f"[green]✅ RSS test successful: {len(articles)} articles[/green]")
            
            if articles:
                article = articles[0]
                console.print("\n[bold]Sample Article:[/bold]")
                console.print(f"Title: {article.title}")
                console.print(f"URL: {article.url}")
                console.print(f"Published: {article.published_at}")
                console.print(f"Content: {article.content[:200]}...")
        else:
            console.print(f"[red]❌ Source '{source}' not found in RSS feeds[/red]")
            
    except Exception as e:
        console.print(f"[red]❌ Test failed: {e}[/red]")
        logger.exception("Test error")


# ===== CELERY COMMANDS =====

@cli.command()
def worker():
    """Запустить Celery worker."""
    console.print("\n[bold blue]👷 Starting Celery worker...[/bold blue]\n")
    console.print("[yellow]Use: celery -A app.celery_app worker -B --loglevel=info[/yellow]\n")


@cli.command()
def monitor():
    """Запустить Flower мониторинг."""
    console.print("\n[bold blue]🌸 Starting Flower monitor...[/bold blue]\n")
    console.print("[yellow]Use: celery -A app.celery_app flower[/yellow]")
    console.print("[yellow]Open: http://localhost:5555[/yellow]\n")


# ===== UTILITY FUNCTIONS =====

def display_scrape_stats(stats: dict):
    """Показать статистику парсинга."""
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Metric", style="yellow")
    table.add_column("Value", style="green")
    
    table.add_row("Total Articles", str(stats.get('total_articles', 0)))
    table.add_row("RSS Articles", str(stats.get('rss_articles', 0)))
    table.add_row("API Articles", str(stats.get('api_articles', 0)))
    table.add_row("Sent to Backend", str(stats.get('sent_to_backend', 0)))
    table.add_row("Errors", str(stats.get('errors', 0)))
    
    console.print(table)
    console.print()


def display_articles_table(articles: list, max_articles: int = 10):
    """Показать таблицу статей."""
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Title", style="cyan", no_wrap=False, width=50)
    table.add_column("Source", style="green", width=15)
    table.add_column("Published", style="yellow", width=20)
    
    for article in articles[:max_articles]:
        # Обрезаем длинные заголовки
        title = article.title[:47] + "..." if len(article.title) > 50 else article.title
        
        # Форматируем дату
        pub_date = article.published_at.strftime("%Y-%m-%d %H:%M") if article.published_at else "Unknown"
        
        table.add_row(title, article.source, pub_date)
    
    console.print(table)
    console.print()


# ===== MAIN =====

if __name__ == '__main__':
    cli()


# ===== USAGE EXAMPLES =====
"""
# ===== CLI Usage =====

# Scrape all sources
python -m app.main scrape-all

# Async scrape
python -m app.main scrape-all --async

# RSS only
python -m app.main scrape-rss

# News API only
python -m app.main scrape-api

# Specific source
python -m app.main scrape bbc
python -m app.main scrape techcrunch

# List sources
python -m app.main list-sources

# Show config
python -m app.main config-info

# Test scraper
python -m app.main test --source bbc

# Help
python -m app.main --help
python -m app.main scrape --help


# ===== Celery Usage =====

# Start worker (sync)
celery -A app.celery_app worker --loglevel=info

# Start worker + beat (periodic tasks)
celery -A app.celery_app worker -B --loglevel=info

# Start flower monitoring
celery -A app.celery_app flower

# Multiple queues
celery -A app.celery_app worker -Q scraping,processing --loglevel=info

# Concurrency
celery -A app.celery_app worker --concurrency=4
"""