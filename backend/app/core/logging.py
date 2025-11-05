"""Logging configuration with context and structured logging."""

import logging
import sys
import contextvars
from typing import Any, Dict, Optional
from pythonjsonlogger import jsonlogger

from app.core.config import settings


# Context variables for request tracking
request_id_ctx = contextvars.ContextVar('request_id', default=None)
user_id_ctx = contextvars.ContextVar('user_id', default=None)


class ContextFilter(logging.Filter):
    """Filter to add context information to log records."""
    
    def filter(self, record):
        """Add context variables to log record.
        
        Args:
            record: Log record
            
        Returns:
            True (always process the record)
        """
        record.request_id = request_id_ctx.get()
        record.user_id = user_id_ctx.get()
        return True


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]) -> None:
        """Add custom fields to log record.
        
        Args:
            log_record: Log record dict to be modified
            record: Original log record
            message_dict: Message dictionary
        """
        super().add_fields(log_record, record, message_dict)
        
        # Add timestamp in ISO format
        log_record['timestamp'] = self.formatTime(record, self.datefmt)
        
        # Add level name
        log_record['level'] = record.levelname
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add context if available
        if hasattr(record, 'request_id') and record.request_id:
            log_record['request_id'] = record.request_id
        
        if hasattr(record, 'user_id') and record.user_id:
            log_record['user_id'] = record.user_id
        
        # Add file info
        log_record['file'] = f"{record.filename}:{record.lineno}"
        
        # Add function name
        log_record['function'] = record.funcName
        
        # Add environment
        log_record['environment'] = settings.ENVIRONMENT


def setup_logging() -> None:
    """Setup application logging with context support."""
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))
    
    # Remove existing handlers
    logger.handlers = []
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    
    # Add context filter
    context_filter = ContextFilter()
    console_handler.addFilter(context_filter)
    
    if settings.LOG_FORMAT == "json":
        # JSON formatter for production
        formatter = CustomJsonFormatter(
            "%(timestamp)s %(level)s %(name)s %(message)s"
        )
    else:
        # Detailed formatter for development
        formatter = logging.Formatter(
            "%(asctime)s - [%(request_id)s] - %(name)s - %(levelname)s - "
            "%(filename)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Configure third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger instance.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def set_request_context(request_id: Optional[str] = None, user_id: Optional[int] = None) -> None:
    """Set request context for logging.
    
    Args:
        request_id: Unique request identifier
        user_id: User ID if authenticated
    """
    if request_id:
        request_id_ctx.set(request_id)
    if user_id:
        user_id_ctx.set(user_id)


def clear_request_context() -> None:
    """Clear request context."""
    request_id_ctx.set(None)
    user_id_ctx.set(None)


class LoggerAdapter(logging.LoggerAdapter):
    """Adapter to add extra context to logs."""
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Process log message with extra context.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
            
        Returns:
            Tuple of (message, kwargs)
        """
        # Add context to extra
        extra = kwargs.get('extra', {})
        
        request_id = request_id_ctx.get()
        if request_id:
            extra['request_id'] = request_id
        
        user_id = user_id_ctx.get()
        if user_id:
            extra['user_id'] = user_id
        
        kwargs['extra'] = extra
        
        return msg, kwargs


def get_context_logger(name: str, **kwargs) -> LoggerAdapter:
    """Get logger with context support.
    
    Args:
        name: Logger name
        **kwargs: Additional context
        
    Returns:
        Logger adapter with context
    """
    logger = logging.getLogger(name)
    return LoggerAdapter(logger, kwargs)
