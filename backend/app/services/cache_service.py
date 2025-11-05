"""Cache service for Redis operations."""

import json
from typing import Optional, Any
import redis.asyncio as redis
from app.core.config import settings
from app.core.logging import get_logger
from app.core.constants import (
    CACHE_TTL_SHORT,
    CACHE_TTL_MEDIUM,
    CACHE_TTL_LONG,
    CACHE_TTL_VERY_LONG
)


logger = get_logger(__name__)


class CacheService:
    """Service for cache operations using Redis."""
    
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = await redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            logger.info("Connected to Redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.redis_client = None
    
    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Disconnected from Redis")
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None
        """
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = CACHE_TTL_MEDIUM
    ) -> bool:
        """Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            serialized = json.dumps(value)
            await self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            await self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False
    
    async def delete_pattern(self, pattern: str) -> int:
        """Delete keys matching pattern.
        
        Args:
            pattern: Key pattern (e.g., "news:*")
            
        Returns:
            Number of deleted keys
        """
        if not self.redis_client:
            return 0
        
        try:
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                keys.append(key)
            
            if keys:
                return await self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache delete pattern error for {pattern}: {e}")
            return 0
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if exists, False otherwise
        """
        if not self.redis_client:
            return False
        
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment counter in cache.
        
        Args:
            key: Cache key
            amount: Amount to increment
            
        Returns:
            New value or None
        """
        if not self.redis_client:
            return None
        
        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None
    
    async def get_or_set(
        self,
        key: str,
        factory_func,
        ttl: int = CACHE_TTL_MEDIUM
    ) -> Optional[Any]:
        """Get from cache or set if not exists.
        
        Args:
            key: Cache key
            factory_func: Async function to generate value
            ttl: Time to live in seconds
            
        Returns:
            Cached or generated value
        """
        # Try to get from cache
        cached_value = await self.get(key)
        if cached_value is not None:
            return cached_value
        
        # Generate new value
        try:
            new_value = await factory_func()
            await self.set(key, new_value, ttl)
            return new_value
        except Exception as e:
            logger.error(f"Cache get_or_set error for key {key}: {e}")
            return None


# Global cache service instance
cache_service = CacheService()


async def get_cache_service() -> CacheService:
    """Get cache service instance.
    
    Returns:
        Cache service instance
    """
    if not cache_service.redis_client:
        await cache_service.connect()
    return cache_service
