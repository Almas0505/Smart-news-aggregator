"""Prometheus metrics for monitoring."""

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, generate_latest
from functools import wraps
import time


# Create registry
REGISTRY = CollectorRegistry()

# HTTP Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status'],
    registry=REGISTRY
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    registry=REGISTRY
)

http_requests_in_progress = Gauge(
    'http_requests_in_progress',
    'HTTP requests in progress',
    ['method', 'endpoint'],
    registry=REGISTRY
)

# Database Metrics
db_queries_total = Counter(
    'db_queries_total',
    'Total database queries',
    ['operation', 'table'],
    registry=REGISTRY
)

db_query_duration_seconds = Histogram(
    'db_query_duration_seconds',
    'Database query duration',
    ['operation', 'table'],
    registry=REGISTRY
)

db_connections_active = Gauge(
    'db_connections_active',
    'Active database connections',
    registry=REGISTRY
)

# Cache Metrics
cache_hits_total = Counter(
    'cache_hits_total',
    'Total cache hits',
    ['cache_key_prefix'],
    registry=REGISTRY
)

cache_misses_total = Counter(
    'cache_misses_total',
    'Total cache misses',
    ['cache_key_prefix'],
    registry=REGISTRY
)

cache_operation_duration_seconds = Histogram(
    'cache_operation_duration_seconds',
    'Cache operation duration',
    ['operation'],
    registry=REGISTRY
)

# Application Metrics
news_created_total = Counter(
    'news_created_total',
    'Total news articles created',
    ['source', 'category'],
    registry=REGISTRY
)

news_views_total = Counter(
    'news_views_total',
    'Total news views',
    registry=REGISTRY
)

users_registered_total = Counter(
    'users_registered_total',
    'Total users registered',
    registry=REGISTRY
)

active_users = Gauge(
    'active_users',
    'Currently active users',
    registry=REGISTRY
)

# Authentication Metrics
auth_attempts_total = Counter(
    'auth_attempts_total',
    'Total authentication attempts',
    ['result'],  # success, failure, rate_limited
    registry=REGISTRY
)

tokens_issued_total = Counter(
    'tokens_issued_total',
    'Total JWT tokens issued',
    ['token_type'],  # access, refresh
    registry=REGISTRY
)

# Rate Limiting Metrics
rate_limit_hits_total = Counter(
    'rate_limit_hits_total',
    'Total rate limit hits',
    ['endpoint'],
    registry=REGISTRY
)

# ML Service Metrics
ml_predictions_total = Counter(
    'ml_predictions_total',
    'Total ML predictions',
    ['model_type'],  # classification, sentiment, entity_extraction
    registry=REGISTRY
)

ml_prediction_duration_seconds = Histogram(
    'ml_prediction_duration_seconds',
    'ML prediction duration',
    ['model_type'],
    registry=REGISTRY
)

# Scraping Metrics
scraper_runs_total = Counter(
    'scraper_runs_total',
    'Total scraper runs',
    ['source', 'status'],  # success, failure
    registry=REGISTRY
)

scraper_articles_scraped = Counter(
    'scraper_articles_scraped',
    'Total articles scraped',
    ['source'],
    registry=REGISTRY
)

scraper_duration_seconds = Histogram(
    'scraper_duration_seconds',
    'Scraper run duration',
    ['source'],
    registry=REGISTRY
)

# Error Metrics
errors_total = Counter(
    'errors_total',
    'Total errors',
    ['error_type', 'endpoint'],
    registry=REGISTRY
)


def track_time(histogram):
    """Decorator to track execution time.
    
    Args:
        histogram: Prometheus histogram metric
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                histogram.observe(duration)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                histogram.observe(duration)
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def get_metrics():
    """Get current metrics in Prometheus format.
    
    Returns:
        Metrics string in Prometheus format
    """
    return generate_latest(REGISTRY)
