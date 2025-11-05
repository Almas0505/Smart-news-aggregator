"""Request context middleware for logging and tracking."""

import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.logging import set_request_context, clear_request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Middleware to set request context for logging."""
    
    def __init__(self, app: ASGIApp):
        """Initialize middleware.
        
        Args:
            app: ASGI application
        """
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next):
        """Set request context before processing.
        
        Args:
            request: FastAPI request
            call_next: Next middleware function
            
        Returns:
            Response with X-Request-ID header
        """
        # Generate or get request ID
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Get user ID if authenticated
        user_id = None
        if hasattr(request.state, 'user') and request.state.user:
            user_id = request.state.user.id
        
        # Set context
        set_request_context(request_id=request_id, user_id=user_id)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id
            
            return response
        finally:
            # Clear context after request
            clear_request_context()
