"""Metrics middleware for collecting HTTP metrics."""

import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.metrics import (
    http_requests_total,
    http_request_duration_seconds,
    http_requests_in_progress
)
from app.core.logging import get_logger


logger = get_logger(__name__)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect HTTP metrics."""
    
    def __init__(self, app: ASGIApp):
        """Initialize middleware.
        
        Args:
            app: ASGI application
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Process request and collect metrics.
        
        Args:
            request: FastAPI request
            call_next: Next middleware function
            
        Returns:
            Response
        """
        # Get path template for better grouping
        route = request.url.path
        method = request.method
        
        # Track in-progress requests
        http_requests_in_progress.labels(
            method=method,
            endpoint=route
        ).inc()
        
        # Track request start time
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            status_code = response.status_code
            
            # Track request completion
            duration = time.time() - start_time
            
            # Record metrics
            http_requests_total.labels(
                method=method,
                endpoint=route,
                status=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=method,
                endpoint=route
            ).observe(duration)
            
            # Log slow requests
            if duration > 1.0:  # Requests taking more than 1 second
                logger.warning(
                    f"Slow request detected: {method} {route} "
                    f"took {duration:.2f}s (status={status_code})"
                )
            
            return response
            
        except Exception as e:
            # Track errors
            http_requests_total.labels(
                method=method,
                endpoint=route,
                status=500
            ).inc()
            
            logger.error(
                f"Error processing request: {method} {route}",
                exc_info=True
            )
            
            raise
        
        finally:
            # Decrement in-progress counter
            http_requests_in_progress.labels(
                method=method,
                endpoint=route
            ).dec()
