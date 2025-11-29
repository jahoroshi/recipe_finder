"""Redis client management for caching and session storage."""

import json
from typing import Any, Optional

import redis.asyncio as redis
from redis.asyncio import Redis
from redis.asyncio.connection import ConnectionPool

from app.config import get_settings

# Global Redis client instance
_redis_client: Optional[Redis] = None
_connection_pool: Optional[ConnectionPool] = None


class RedisClient:
    """Redis client wrapper with common caching operations.

    Provides high-level methods for caching, with automatic JSON
    serialization/deserialization and error handling.
    """

    def __init__(self, client: Redis):
        """Initialize Redis client wrapper.

        Args:
            client: Redis client instance
        """
        self._client = client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value (deserialized from JSON) or None if not found
        """
        try:
            value = await self._client.get(key)
            if value is None:
                return None

            # Try to deserialize JSON, return raw string if fails
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            # Log error but don't raise - cache failures shouldn't break the app
            print(f"Redis GET error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """Set value in cache with optional TTL.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds (None for no expiry)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Serialize value to JSON
            if isinstance(value, (dict, list)):
                serialized = json.dumps(value)
            elif isinstance(value, str):
                serialized = value
            else:
                serialized = json.dumps(value)

            if ttl is not None:
                await self._client.setex(key, ttl, serialized)
            else:
                await self._client.set(key, serialized)

            return True
        except Exception as e:
            print(f"Redis SET error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False otherwise
        """
        try:
            result = await self._client.delete(key)
            return result > 0
        except Exception as e:
            print(f"Redis DELETE error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.

        Args:
            pattern: Pattern to match (e.g., "recipe:*")

        Returns:
            Number of keys deleted
        """
        try:
            cursor = 0
            deleted = 0

            while True:
                cursor, keys = await self._client.scan(
                    cursor=cursor,
                    match=pattern,
                    count=100
                )

                if keys:
                    deleted += await self._client.delete(*keys)

                if cursor == 0:
                    break

            return deleted
        except Exception as e:
            print(f"Redis DELETE PATTERN error for pattern {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache.

        Args:
            key: Cache key to check

        Returns:
            True if key exists, False otherwise
        """
        try:
            result = await self._client.exists(key)
            return result > 0
        except Exception as e:
            print(f"Redis EXISTS error for key {key}: {e}")
            return False

    async def ping(self) -> bool:
        """Ping Redis server to check connectivity.

        Returns:
            True if Redis is responsive, False otherwise
        """
        try:
            return await self._client.ping()
        except Exception:
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        await self._client.aclose()


async def init_redis() -> None:
    """Initialize Redis connection pool.

    Creates Redis client with connection pooling based on application settings.
    """
    global _redis_client, _connection_pool

    if _redis_client is not None:
        return  # Already initialized

    settings = get_settings()

    # Create connection pool
    _connection_pool = ConnectionPool.from_url(
        str(settings.redis_url),
        max_connections=settings.redis_max_connections,
        socket_timeout=settings.redis_socket_timeout,
        socket_connect_timeout=settings.redis_socket_connect_timeout,
        decode_responses=settings.redis_decode_responses,
    )

    # Create Redis client
    _redis_client = Redis(connection_pool=_connection_pool)


async def close_redis() -> None:
    """Close Redis connection pool.

    Properly closes Redis client and connection pool.
    Should be called during application shutdown.
    """
    global _redis_client, _connection_pool

    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None

    if _connection_pool is not None:
        await _connection_pool.aclose()
        _connection_pool = None


def get_redis() -> RedisClient:
    """Get Redis client instance.

    Returns:
        RedisClient wrapper instance

    Raises:
        RuntimeError: If Redis is not initialized

    Example:
        ```python
        @app.get("/recipes/{id}")
        async def get_recipe(
            id: str,
            redis: RedisClient = Depends(get_redis)
        ):
            cached = await redis.get(f"recipe:{id}")
            if cached:
                return cached
            # ... fetch from database and cache
        ```
    """
    if _redis_client is None:
        raise RuntimeError(
            "Redis client not initialized. Call init_redis() first."
        )

    return RedisClient(_redis_client)
