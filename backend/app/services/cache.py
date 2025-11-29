"""Cache service for Redis operations with recipe-specific caching strategies."""

import hashlib
import json
from typing import Any, Optional
from uuid import UUID

from app.db.redis_client import RedisClient


class CacheService:
    """Service for managing Redis cache operations.

    Implements caching strategies with TTL configuration and pattern-based invalidation.

    Cache Keys Structure:
        - recipe:{id} - Individual recipes (TTL: 1 hour)
        - search:{query_hash} - Search results (TTL: 15 minutes)
        - embedding:{text_hash} - Embeddings (TTL: 24 hours)
        - stats:{type} - Aggregated statistics (TTL: 5 minutes)

    Example:
        ```python
        cache = CacheService(redis_client)
        await cache.set("recipe:123", recipe_data, ttl=3600)
        cached = await cache.get("recipe:123")
        ```
    """

    # TTL constants in seconds
    TTL_RECIPE = 3600  # 1 hour
    TTL_SEARCH = 900  # 15 minutes
    TTL_EMBEDDING = 86400  # 24 hours
    TTL_STATS = 300  # 5 minutes

    def __init__(self, redis_client: RedisClient):
        """Initialize cache service.

        Args:
            redis_client: Redis client instance
        """
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        return await self.redis.get(key)

    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (default: 1 hour)

        Returns:
            True if successful, False otherwise
        """
        return await self.redis.set(key, value, ttl=ttl)

    async def delete(self, key: str) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key to delete

        Returns:
            True if key was deleted, False otherwise
        """
        return await self.redis.delete(key)

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern.

        Args:
            pattern: Pattern to match (e.g., "recipe:*")

        Returns:
            Number of keys deleted
        """
        return await self.redis.delete_pattern(pattern)

    async def invalidate_recipe_cache(self, recipe_id: UUID) -> None:
        """Invalidate all cache entries related to a recipe.

        Deletes:
            - Individual recipe cache
            - Search results (all)
            - Statistics

        Args:
            recipe_id: Recipe UUID
        """
        # Delete specific recipe cache
        await self.delete(f"recipe:{recipe_id}")

        # Invalidate all search results (as they might contain this recipe)
        await self.delete_pattern("search:*")

        # Invalidate statistics
        await self.delete_pattern("stats:*")

    async def get_recipe(self, recipe_id: UUID) -> Optional[dict]:
        """Get cached recipe by ID.

        Args:
            recipe_id: Recipe UUID

        Returns:
            Cached recipe data or None
        """
        return await self.get(f"recipe:{recipe_id}")

    async def set_recipe(self, recipe_id: UUID, recipe_data: dict) -> bool:
        """Cache recipe data.

        Args:
            recipe_id: Recipe UUID
            recipe_data: Recipe data to cache

        Returns:
            True if successful, False otherwise
        """
        return await self.set(f"recipe:{recipe_id}", recipe_data, ttl=self.TTL_RECIPE)

    async def get_search_results(self, query: str, filters: Optional[dict] = None) -> Optional[list]:
        """Get cached search results.

        Args:
            query: Search query
            filters: Optional search filters

        Returns:
            Cached search results or None
        """
        cache_key = self._generate_search_key(query, filters)
        return await self.get(cache_key)

    async def set_search_results(
        self, query: str, results: list, filters: Optional[dict] = None
    ) -> bool:
        """Cache search results.

        Args:
            query: Search query
            results: Search results to cache
            filters: Optional search filters

        Returns:
            True if successful, False otherwise
        """
        cache_key = self._generate_search_key(query, filters)
        return await self.set(cache_key, results, ttl=self.TTL_SEARCH)

    async def get_embedding(self, text: str) -> Optional[list[float]]:
        """Get cached embedding.

        Args:
            text: Text for which embedding was generated

        Returns:
            Cached embedding vector or None
        """
        cache_key = self._generate_embedding_key(text)
        return await self.get(cache_key)

    async def set_embedding(self, text: str, embedding: list[float]) -> bool:
        """Cache embedding vector.

        Args:
            text: Text for which embedding was generated
            embedding: Embedding vector

        Returns:
            True if successful, False otherwise
        """
        cache_key = self._generate_embedding_key(text)
        return await self.set(cache_key, embedding, ttl=self.TTL_EMBEDDING)

    async def get_stats(self, stats_type: str) -> Optional[dict]:
        """Get cached statistics.

        Args:
            stats_type: Type of statistics (e.g., "cuisine", "difficulty")

        Returns:
            Cached statistics or None
        """
        return await self.get(f"stats:{stats_type}")

    async def set_stats(self, stats_type: str, stats_data: dict) -> bool:
        """Cache statistics data.

        Args:
            stats_type: Type of statistics
            stats_data: Statistics data to cache

        Returns:
            True if successful, False otherwise
        """
        return await self.set(f"stats:{stats_type}", stats_data, ttl=self.TTL_STATS)

    def _generate_search_key(self, query: str, filters: Optional[dict] = None) -> str:
        """Generate cache key for search query.

        Creates a hash of query + filters to ensure unique keys for different searches.

        Args:
            query: Search query
            filters: Optional search filters

        Returns:
            Cache key for search
        """
        # Create deterministic string from query and filters
        search_data = {"query": query, "filters": filters or {}}
        search_str = json.dumps(search_data, sort_keys=True)

        # Generate hash
        query_hash = hashlib.sha256(search_str.encode()).hexdigest()[:16]

        return f"search:{query_hash}"

    def _generate_embedding_key(self, text: str) -> str:
        """Generate cache key for embedding.

        Creates a hash of text to ensure consistent keys.

        Args:
            text: Text for embedding

        Returns:
            Cache key for embedding
        """
        text_hash = hashlib.sha256(text.encode()).hexdigest()[:16]
        return f"embedding:{text_hash}"

    async def clear_all(self) -> int:
        """Clear all cache entries.

        Useful for testing and development.

        Returns:
            Number of keys deleted
        """
        return await self.delete_pattern("*")

    async def ping(self) -> bool:
        """Check if Redis is accessible.

        Returns:
            True if Redis is responsive, False otherwise
        """
        return await self.redis.ping()
