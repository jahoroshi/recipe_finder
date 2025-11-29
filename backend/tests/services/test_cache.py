"""Tests for CacheService."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from app.services.cache import CacheService


@pytest.fixture
def mock_redis_client():
    """Create mock Redis client."""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.set = AsyncMock(return_value=True)
    mock.delete = AsyncMock(return_value=True)
    mock.delete_pattern = AsyncMock(return_value=5)
    mock.ping = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def cache_service(mock_redis_client):
    """Create CacheService instance with mock Redis."""
    return CacheService(mock_redis_client)


@pytest.mark.asyncio
class TestCacheService:
    """Test suite for CacheService."""

    async def test_get(self, cache_service, mock_redis_client):
        """Test getting value from cache."""
        # Setup
        mock_redis_client.get.return_value = {"key": "value"}

        # Execute
        result = await cache_service.get("test_key")

        # Assert
        assert result == {"key": "value"}
        mock_redis_client.get.assert_called_once_with("test_key")

    async def test_set(self, cache_service, mock_redis_client):
        """Test setting value in cache."""
        # Setup
        data = {"name": "test"}
        ttl = 3600

        # Execute
        result = await cache_service.set("test_key", data, ttl=ttl)

        # Assert
        assert result is True
        mock_redis_client.set.assert_called_once_with("test_key", data, ttl=ttl)

    async def test_delete(self, cache_service, mock_redis_client):
        """Test deleting key from cache."""
        # Execute
        result = await cache_service.delete("test_key")

        # Assert
        assert result is True
        mock_redis_client.delete.assert_called_once_with("test_key")

    async def test_delete_pattern(self, cache_service, mock_redis_client):
        """Test deleting keys by pattern."""
        # Execute
        deleted_count = await cache_service.delete_pattern("recipe:*")

        # Assert
        assert deleted_count == 5
        mock_redis_client.delete_pattern.assert_called_once_with("recipe:*")

    async def test_get_recipe(self, cache_service, mock_redis_client):
        """Test getting cached recipe."""
        # Setup
        recipe_id = uuid4()
        recipe_data = {"name": "Pasta", "description": "Delicious"}
        mock_redis_client.get.return_value = recipe_data

        # Execute
        result = await cache_service.get_recipe(recipe_id)

        # Assert
        assert result == recipe_data
        mock_redis_client.get.assert_called_once_with(f"recipe:{recipe_id}")

    async def test_set_recipe(self, cache_service, mock_redis_client):
        """Test caching recipe data."""
        # Setup
        recipe_id = uuid4()
        recipe_data = {"name": "Pasta", "description": "Delicious"}

        # Execute
        result = await cache_service.set_recipe(recipe_id, recipe_data)

        # Assert
        assert result is True
        mock_redis_client.set.assert_called_once_with(
            f"recipe:{recipe_id}", recipe_data, ttl=CacheService.TTL_RECIPE
        )

    async def test_get_search_results(self, cache_service, mock_redis_client):
        """Test getting cached search results."""
        # Setup
        query = "italian pasta"
        filters = {"cuisine_type": "Italian"}
        mock_redis_client.get.return_value = [{"name": "Carbonara"}]

        # Execute
        result = await cache_service.get_search_results(query, filters)

        # Assert
        assert result == [{"name": "Carbonara"}]
        # Verify the call was made (exact key will be hashed)
        assert mock_redis_client.get.call_count == 1

    async def test_set_search_results(self, cache_service, mock_redis_client):
        """Test caching search results."""
        # Setup
        query = "italian pasta"
        results = [{"name": "Carbonara"}, {"name": "Amatriciana"}]
        filters = {"cuisine_type": "Italian"}

        # Execute
        result = await cache_service.set_search_results(query, results, filters)

        # Assert
        assert result is True
        assert mock_redis_client.set.call_count == 1
        # Verify TTL was set correctly
        call_args = mock_redis_client.set.call_args
        assert call_args[1]["ttl"] == CacheService.TTL_SEARCH

    async def test_get_embedding(self, cache_service, mock_redis_client):
        """Test getting cached embedding."""
        # Setup
        text = "delicious pasta"
        embedding = [0.1, 0.2, 0.3]
        mock_redis_client.get.return_value = embedding

        # Execute
        result = await cache_service.get_embedding(text)

        # Assert
        assert result == embedding
        assert mock_redis_client.get.call_count == 1

    async def test_set_embedding(self, cache_service, mock_redis_client):
        """Test caching embedding."""
        # Setup
        text = "delicious pasta"
        embedding = [0.1] * 768

        # Execute
        result = await cache_service.set_embedding(text, embedding)

        # Assert
        assert result is True
        assert mock_redis_client.set.call_count == 1
        call_args = mock_redis_client.set.call_args
        assert call_args[1]["ttl"] == CacheService.TTL_EMBEDDING

    async def test_get_stats(self, cache_service, mock_redis_client):
        """Test getting cached statistics."""
        # Setup
        stats_data = {"Italian": 10, "Chinese": 5}
        mock_redis_client.get.return_value = stats_data

        # Execute
        result = await cache_service.get_stats("cuisine")

        # Assert
        assert result == stats_data
        mock_redis_client.get.assert_called_once_with("stats:cuisine")

    async def test_set_stats(self, cache_service, mock_redis_client):
        """Test caching statistics."""
        # Setup
        stats_data = {"Italian": 10, "Chinese": 5}

        # Execute
        result = await cache_service.set_stats("cuisine", stats_data)

        # Assert
        assert result is True
        mock_redis_client.set.assert_called_once_with(
            "stats:cuisine", stats_data, ttl=CacheService.TTL_STATS
        )

    async def test_invalidate_recipe_cache(self, cache_service, mock_redis_client):
        """Test invalidating recipe cache."""
        # Setup
        recipe_id = uuid4()

        # Execute
        await cache_service.invalidate_recipe_cache(recipe_id)

        # Assert
        # Should delete recipe, search results, and stats
        assert mock_redis_client.delete.call_count == 1
        assert mock_redis_client.delete_pattern.call_count == 2

        # Verify correct patterns were deleted
        delete_calls = [call[0][0] for call in mock_redis_client.delete.call_args_list]
        assert f"recipe:{recipe_id}" in delete_calls

        pattern_calls = [call[0][0] for call in mock_redis_client.delete_pattern.call_args_list]
        assert "search:*" in pattern_calls
        assert "stats:*" in pattern_calls

    async def test_generate_search_key_consistent(self, cache_service):
        """Test search key generation is consistent."""
        # Setup
        query = "pasta carbonara"
        filters = {"cuisine_type": "Italian", "difficulty": "easy"}

        # Execute
        key1 = cache_service._generate_search_key(query, filters)
        key2 = cache_service._generate_search_key(query, filters)

        # Assert - Same query and filters should produce same key
        assert key1 == key2
        assert key1.startswith("search:")

    async def test_generate_search_key_different_queries(self, cache_service):
        """Test different queries generate different keys."""
        # Execute
        key1 = cache_service._generate_search_key("pasta", {"cuisine_type": "Italian"})
        key2 = cache_service._generate_search_key("pizza", {"cuisine_type": "Italian"})

        # Assert
        assert key1 != key2

    async def test_generate_embedding_key_consistent(self, cache_service):
        """Test embedding key generation is consistent."""
        # Setup
        text = "delicious italian pasta"

        # Execute
        key1 = cache_service._generate_embedding_key(text)
        key2 = cache_service._generate_embedding_key(text)

        # Assert
        assert key1 == key2
        assert key1.startswith("embedding:")

    async def test_clear_all(self, cache_service, mock_redis_client):
        """Test clearing all cache entries."""
        # Setup
        mock_redis_client.delete_pattern.return_value = 100

        # Execute
        deleted_count = await cache_service.clear_all()

        # Assert
        assert deleted_count == 100
        mock_redis_client.delete_pattern.assert_called_once_with("*")

    async def test_ping(self, cache_service, mock_redis_client):
        """Test Redis connectivity check."""
        # Execute
        result = await cache_service.ping()

        # Assert
        assert result is True
        mock_redis_client.ping.assert_called_once()

    async def test_ping_failure(self, cache_service, mock_redis_client):
        """Test Redis ping failure."""
        # Setup
        mock_redis_client.ping.return_value = False

        # Execute
        result = await cache_service.ping()

        # Assert
        assert result is False

    # New test case: Test cache operations with None value
    async def test_get_returns_none_for_missing_key(
        self, cache_service, mock_redis_client
    ):
        """Test getting non-existent key returns None."""
        # Setup
        mock_redis_client.get.return_value = None

        # Execute
        result = await cache_service.get("non_existent_key")

        # Assert
        assert result is None
        mock_redis_client.get.assert_called_once_with("non_existent_key")

    # New test case: Test cache with empty string key
    async def test_set_with_empty_value(self, cache_service, mock_redis_client):
        """Test setting empty value in cache."""
        # Setup
        mock_redis_client.set.return_value = True

        # Execute
        result = await cache_service.set("key", "", ttl=100)

        # Assert
        assert result is True
        mock_redis_client.set.assert_called_once_with("key", "", ttl=100)

    # New test case: Test cache with very large TTL
    async def test_set_with_large_ttl(self, cache_service, mock_redis_client):
        """Test setting value with very large TTL."""
        # Setup
        large_ttl = 86400 * 365  # 1 year
        mock_redis_client.set.return_value = True

        # Execute
        result = await cache_service.set("key", "value", ttl=large_ttl)

        # Assert
        assert result is True
        call_args = mock_redis_client.set.call_args
        assert call_args[1]["ttl"] == large_ttl

    # New test case: Test delete non-existent key
    async def test_delete_non_existent_key(self, cache_service, mock_redis_client):
        """Test deleting non-existent key returns False."""
        # Setup
        mock_redis_client.delete.return_value = False

        # Execute
        result = await cache_service.delete("non_existent")

        # Assert
        assert result is False

    # New test case: Test delete_pattern with no matches
    async def test_delete_pattern_no_matches(self, cache_service, mock_redis_client):
        """Test deleting pattern with no matches."""
        # Setup
        mock_redis_client.delete_pattern.return_value = 0

        # Execute
        deleted_count = await cache_service.delete_pattern("nonexistent:*")

        # Assert
        assert deleted_count == 0

    # New test case: Test search key generation with empty filters
    async def test_generate_search_key_with_empty_filters(self, cache_service):
        """Test search key generation with empty filters."""
        # Setup
        query = "test query"

        # Execute
        key1 = cache_service._generate_search_key(query, {})
        key2 = cache_service._generate_search_key(query, None)

        # Assert - Empty dict and None both normalize to {} in implementation, so same key
        assert key1 == key2  # Both convert to {} internally
        assert key1.startswith("search:")
        assert key2.startswith("search:")

    # New test case: Test search key generation with complex filters
    async def test_generate_search_key_with_complex_filters(self, cache_service):
        """Test search key generation with nested filters."""
        # Setup
        query = "pasta"
        filters = {
            "cuisine_type": "Italian",
            "difficulty": "easy",
            "diet_types": ["vegetarian", "gluten-free"],
            "max_time": 30,
        }

        # Execute
        key1 = cache_service._generate_search_key(query, filters)
        key2 = cache_service._generate_search_key(query, filters)

        # Assert - Same filters should produce same key
        assert key1 == key2
        assert len(key1) > len("search:")

    # New test case: Test search key generation order independence
    async def test_generate_search_key_filter_order_independent(self, cache_service):
        """Test search key is same regardless of filter dict order."""
        # Setup
        query = "pasta"
        filters1 = {"a": 1, "b": 2, "c": 3}
        filters2 = {"c": 3, "a": 1, "b": 2}

        # Execute
        key1 = cache_service._generate_search_key(query, filters1)
        key2 = cache_service._generate_search_key(query, filters2)

        # Assert - Different dict order should produce same key
        assert key1 == key2

    # New test case: Test embedding key with special characters
    async def test_generate_embedding_key_with_special_chars(self, cache_service):
        """Test embedding key generation with special characters."""
        # Setup
        text1 = "pasta with cheese & eggs!"
        text2 = "pasta with cheese & eggs!"

        # Execute
        key1 = cache_service._generate_embedding_key(text1)
        key2 = cache_service._generate_embedding_key(text2)

        # Assert
        assert key1 == key2
        assert key1.startswith("embedding:")

    # New test case: Test embedding key with unicode
    async def test_generate_embedding_key_with_unicode(self, cache_service):
        """Test embedding key generation with unicode characters."""
        # Setup
        text = "pasta carbonara с сыром"  # Mixed languages

        # Execute
        key = cache_service._generate_embedding_key(text)

        # Assert
        assert key.startswith("embedding:")
        assert len(key) > len("embedding:")

    # New test case: Test cache invalidation cascade
    async def test_invalidate_recipe_cache_multiple_calls(
        self, cache_service, mock_redis_client
    ):
        """Test invalidating recipe cache multiple times."""
        # Setup
        recipe_id = uuid4()
        mock_redis_client.delete.return_value = True
        mock_redis_client.delete_pattern.return_value = 10

        # Execute
        await cache_service.invalidate_recipe_cache(recipe_id)
        await cache_service.invalidate_recipe_cache(recipe_id)

        # Assert - Should be called twice
        assert mock_redis_client.delete.call_count == 2
        assert mock_redis_client.delete_pattern.call_count == 4

    # New test case: Test get_recipe with None
    async def test_get_recipe_returns_none(self, cache_service, mock_redis_client):
        """Test getting non-existent recipe returns None."""
        # Setup
        recipe_id = uuid4()
        mock_redis_client.get.return_value = None

        # Execute
        result = await cache_service.get_recipe(recipe_id)

        # Assert
        assert result is None

    # New test case: Test set_recipe with complex data
    async def test_set_recipe_with_nested_data(self, cache_service, mock_redis_client):
        """Test caching recipe with nested data structures."""
        # Setup
        recipe_id = uuid4()
        recipe_data = {
            "name": "Complex Recipe",
            "ingredients": [
                {"name": "pasta", "quantity": 500},
                {"name": "cheese", "quantity": 100},
            ],
            "metadata": {"tags": ["italian", "vegetarian"], "rating": 4.5},
        }
        mock_redis_client.set.return_value = True

        # Execute
        result = await cache_service.set_recipe(recipe_id, recipe_data)

        # Assert
        assert result is True
        mock_redis_client.set.assert_called_once_with(
            f"recipe:{recipe_id}", recipe_data, ttl=CacheService.TTL_RECIPE
        )

    # New test case: Test search results caching with None filters
    async def test_get_search_results_with_none_filters(
        self, cache_service, mock_redis_client
    ):
        """Test getting search results with None filters."""
        # Setup
        query = "test"
        mock_redis_client.get.return_value = None

        # Execute
        result = await cache_service.get_search_results(query, None)

        # Assert
        assert result is None
        assert mock_redis_client.get.call_count == 1

    # New test case: Test embedding with very long text
    async def test_set_embedding_with_long_text(
        self, cache_service, mock_redis_client
    ):
        """Test caching embedding for very long text."""
        # Setup
        long_text = "pasta " * 1000  # Very long text
        embedding = [0.1] * 768
        mock_redis_client.set.return_value = True

        # Execute
        result = await cache_service.set_embedding(long_text, embedding)

        # Assert
        assert result is True
        assert mock_redis_client.set.call_count == 1

    # New test case: Test get_stats with different stat types
    async def test_get_stats_different_types(self, cache_service, mock_redis_client):
        """Test getting different types of statistics."""
        # Setup
        mock_redis_client.get.return_value = {"value": 100}

        # Execute
        cuisine_stats = await cache_service.get_stats("cuisine")
        difficulty_stats = await cache_service.get_stats("difficulty")

        # Assert
        assert cuisine_stats == {"value": 100}
        assert difficulty_stats == {"value": 100}
        assert mock_redis_client.get.call_count == 2

    # New test case: Test clear_all with large number of keys
    async def test_clear_all_large_cache(self, cache_service, mock_redis_client):
        """Test clearing cache with many entries."""
        # Setup
        mock_redis_client.delete_pattern.return_value = 10000

        # Execute
        deleted_count = await cache_service.clear_all()

        # Assert
        assert deleted_count == 10000
        mock_redis_client.delete_pattern.assert_called_once_with("*")

    # New test case: Test Redis connection failure handling
    async def test_ping_raises_exception(self, cache_service, mock_redis_client):
        """Test ping when Redis raises exception."""
        # Setup
        mock_redis_client.ping.side_effect = Exception("Connection failed")

        # Execute & Assert
        with pytest.raises(Exception, match="Connection failed"):
            await cache_service.ping()

    # New test case: Test set operation failure
    async def test_set_operation_failure(self, cache_service, mock_redis_client):
        """Test set operation returns False on failure."""
        # Setup
        mock_redis_client.set.return_value = False

        # Execute
        result = await cache_service.set("key", "value", ttl=100)

        # Assert
        assert result is False

    # New test case: Test embedding key collision resistance
    async def test_embedding_key_different_texts(self, cache_service):
        """Test that different texts generate different keys."""
        # Setup
        text1 = "pasta carbonara"
        text2 = "carbonara pasta"

        # Execute
        key1 = cache_service._generate_embedding_key(text1)
        key2 = cache_service._generate_embedding_key(text2)

        # Assert
        assert key1 != key2

    # New test case: Test hash consistency across service instances
    async def test_search_key_consistency_across_instances(self, mock_redis_client):
        """Test search key generation is consistent across service instances."""
        # Setup
        service1 = CacheService(mock_redis_client)
        service2 = CacheService(mock_redis_client)
        query = "test query"
        filters = {"cuisine": "Italian"}

        # Execute
        key1 = service1._generate_search_key(query, filters)
        key2 = service2._generate_search_key(query, filters)

        # Assert
        assert key1 == key2
