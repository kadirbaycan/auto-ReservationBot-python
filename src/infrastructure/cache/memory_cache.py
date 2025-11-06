"""In-Memory Cache Implementation"""

import asyncio
from typing import Any, Optional, Dict
from datetime import datetime, timedelta
import json

from src.domain.interfaces import ICacheService


class MemoryCache(ICacheService):
    """In-memory cache implementation (for development/testing)."""

    def __init__(self):
        self._cache: Dict[str, tuple[Any, Optional[datetime]]] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        async with self._lock:
            if key not in self._cache:
                return None

            value, expiry = self._cache[key]

            # Check if expired
            if expiry and datetime.utcnow() > expiry:
                del self._cache[key]
                return None

            return value

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        async with self._lock:
            expiry = datetime.utcnow() + timedelta(seconds=ttl) if ttl > 0 else None
            self._cache[key] = (value, expiry)
            return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                return True
            return False

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        value = await self.get(key)
        return value is not None

    async def clear(self, pattern: str = None) -> int:
        """Clear cache (optionally by pattern)."""
        async with self._lock:
            if pattern is None:
                count = len(self._cache)
                self._cache.clear()
                return count

            # Simple pattern matching (startswith)
            keys_to_delete = [k for k in self._cache.keys() if k.startswith(pattern.rstrip("*"))]
            for key in keys_to_delete:
                del self._cache[key]

            return len(keys_to_delete)

    async def cleanup_expired(self) -> int:
        """Remove expired entries."""
        async with self._lock:
            now = datetime.utcnow()
            keys_to_delete = [
                key
                for key, (_, expiry) in self._cache.items()
                if expiry and now > expiry
            ]

            for key in keys_to_delete:
                del self._cache[key]

            return len(keys_to_delete)
