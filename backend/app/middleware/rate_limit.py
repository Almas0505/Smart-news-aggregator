"""Rate limiting middleware for API protection."""

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import get_logger


logger = get_logger(__name__)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"],
    storage_uri=settings.REDIS_URL,
    strategy="fixed-window",
)


async def rate_limit_exceeded_handler(
    request: Request, 
    exc: RateLimitExceeded
) -> JSONResponse:
    """Handle rate limit exceeded errors.
    
    Args:
        request: FastAPI request object
        exc: RateLimitExceeded exception
        
    Returns:
        JSON response with 429 status code
    """
    logger.warning(
        f"Rate limit exceeded for {get_remote_address(request)} "
        f"on {request.url.path}"
    )
    
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit_exceeded",
            "detail": "Too many requests. Please try again later.",
            "retry_after": exc.detail
        },
        headers={"Retry-After": str(exc.detail)}
    )


def get_rate_limit_key(request: Request) -> str:
    """Get rate limit key from request.
    
    Uses IP address by default, but can be extended to use
    API keys or user IDs for authenticated requests.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Rate limit key string
    """
    # Check if user is authenticated
    if hasattr(request.state, "user") and request.state.user:
        return f"user:{request.state.user.id}"
    
    # Fall back to IP address
    return get_remote_address(request)


# Custom rate limit decorators for different endpoints
def rate_limit_auth(func):
    """Rate limit for authentication endpoints (stricter)."""
    return limiter.limit("5/minute")(func)


def rate_limit_api(func):
    """Rate limit for general API endpoints."""
    return limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")(func)


def rate_limit_public(func):
    """Rate limit for public endpoints (more lenient)."""
    return limiter.limit("100/minute")(func)
