"""Redis Cache Implementation"""

import json
from typing import Any, Optional
import os

from src.domain.interfaces import ICacheService

try:
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    aioredis = None


class RedisCache(ICacheService):
    """Redis cache implementation (production-ready)."""

    def __init__(self, redis_url: str = None):
        if not REDIS_AVAILABLE:
            raise ImportError("redis package not installed. Install: pip install redis[hiredis]")

        self.redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        if self.redis is None:
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
                max_connections=20,
            )

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()
            self.redis = None

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        await self.connect()
        value = await self.redis.get(key)

        if value is None:
            return None

        try:
            # Try to deserialize JSON
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            # Return as-is if not JSON
            return value

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        await self.connect()

        # Serialize to JSON if not a string
        if not isinstance(value, str):
            value = json.dumps(value)

        if ttl > 0:
            await self.redis.setex(key, ttl, value)
        else:
            await self.redis.set(key, value)

        return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        await self.connect()
        result = await self.redis.delete(key)
        return result > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        await self.connect()
        result = await self.redis.exists(key)
        return result > 0

    async def clear(self, pattern: str = None) -> int:
        """Clear cache (optionally by pattern)."""
        await self.connect()

        if pattern is None:
            # Clear entire database
            await self.redis.flushdb()
            return -1  # Unknown count

        # Delete by pattern
        keys = []
        async for key in self.redis.scan_iter(match=pattern):
            keys.append(key)

        if keys:
            deleted = await self.redis.delete(*keys)
            return deleted

        return 0

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter."""
        await self.connect()
        return await self.redis.incrby(key, amount)

    async def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on existing key."""
        await self.connect()
        result = await self.redis.expire(key, ttl)
        return result
