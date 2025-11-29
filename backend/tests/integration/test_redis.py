"""Integration tests for Redis connection."""

import asyncio

import pytest

from app.db.redis_client import init_redis, close_redis, get_redis, RedisClient


@pytest.fixture(scope="function", autouse=True)
async def redis_client_lifecycle():
    """Initialize and cleanup Redis client for each test."""
    await init_redis()
    yield
    try:
        await close_redis()
    except RuntimeError:
        # Ignore event loop closed errors in cleanup
        pass


class TestRedisConnection:
    """Test suite for Redis connectivity."""

    @pytest.mark.asyncio
    async def test_init_redis(self):
        """Test Redis initialization."""
        # Already initialized by fixture
        redis = get_redis()
        assert redis is not None

    @pytest.mark.asyncio
    async def test_redis_connection(self):
        """Test that Redis connection can be established."""
        redis = get_redis()
        assert isinstance(redis, RedisClient)

    @pytest.mark.asyncio
    async def test_redis_ping(self):
        """Test Redis server connectivity."""
        redis = get_redis()
        result = await redis.ping()

        assert result is True

    @pytest.mark.asyncio
    async def test_redis_set_get(self):
        """Test basic Redis set and get operations."""
        redis = get_redis()
        test_key = "test:unit:key"
        test_value = "test_value"

        # Set value
        success = await redis.set(test_key, test_value, ttl=60)
        assert success is True

        # Get value
        value = await redis.get(test_key)
        assert value == test_value

        # Cleanup
        await redis.delete(test_key)

    @pytest.mark.asyncio
    async def test_redis_set_get_json(self):
        """Test Redis operations with JSON data."""
        redis = get_redis()
        test_key = "test:unit:json"
        test_data = {"name": "Test Recipe", "ingredients": ["flour", "sugar"]}

        # Set JSON data
        success = await redis.set(test_key, test_data, ttl=60)
        assert success is True

        # Get JSON data
        value = await redis.get(test_key)
        assert value == test_data

        # Cleanup
        await redis.delete(test_key)

    @pytest.mark.asyncio
    async def test_redis_delete(self):
        """Test Redis delete operation."""
        redis = get_redis()
        test_key = "test:unit:delete"

        # Set value
        await redis.set(test_key, "test", ttl=60)

        # Delete value
        success = await redis.delete(test_key)
        assert success is True

        # Verify deletion
        value = await redis.get(test_key)
        assert value is None

    @pytest.mark.asyncio
    async def test_redis_exists(self):
        """Test Redis exists operation."""
        redis = get_redis()
        test_key = "test:unit:exists"

        # Key should not exist initially
        exists = await redis.exists(test_key)
        assert exists is False

        # Set value
        await redis.set(test_key, "test", ttl=60)

        # Key should now exist
        exists = await redis.exists(test_key)
        assert exists is True

        # Cleanup
        await redis.delete(test_key)

    @pytest.mark.asyncio
    async def test_redis_ttl_expiry(self):
        """Test Redis TTL and automatic expiry."""
        redis = get_redis()
        test_key = "test:unit:ttl"

        # Set value with short TTL
        await redis.set(test_key, "test", ttl=1)

        # Value should exist
        value = await redis.get(test_key)
        assert value == "test"

        # Wait for expiry
        await asyncio.sleep(2)

        # Value should be gone
        value = await redis.get(test_key)
        assert value is None

    @pytest.mark.asyncio
    async def test_redis_delete_pattern(self):
        """Test Redis pattern-based deletion."""
        redis = get_redis()
        pattern = "test:unit:pattern:*"

        # Create multiple keys with pattern
        keys = [f"test:unit:pattern:{i}" for i in range(5)]
        for key in keys:
            await redis.set(key, f"value_{key}", ttl=60)

        # Delete all keys matching pattern
        deleted = await redis.delete_pattern(pattern)
        assert deleted == 5

        # Verify all keys are deleted
        for key in keys:
            exists = await redis.exists(key)
            assert exists is False

    @pytest.mark.asyncio
    async def test_redis_concurrent_operations(self):
        """Test concurrent Redis operations."""
        redis = get_redis()

        async def set_and_get(index: int):
            key = f"test:unit:concurrent:{index}"
            await redis.set(key, f"value_{index}", ttl=60)
            value = await redis.get(key)
            await redis.delete(key)
            return value == f"value_{index}"

        # Run 10 concurrent operations
        results = await asyncio.gather(*[set_and_get(i) for i in range(10)])

        # All operations should succeed
        assert all(results)

    @pytest.mark.asyncio
    async def test_redis_none_value_handling(self):
        """Test Redis handling of non-existent keys."""
        redis = get_redis()
        test_key = "test:unit:nonexistent"

        # Get non-existent key
        value = await redis.get(test_key)
        assert value is None

        # Delete non-existent key
        success = await redis.delete(test_key)
        assert success is False

    @pytest.mark.asyncio
    async def test_redis_error_resilience(self):
        """Test Redis error handling doesn't break the client."""
        redis = get_redis()

        # These operations should not raise exceptions
        # even if there are issues (they return False/None)
        await redis.get("test:key")
        await redis.set("test:key", "value", ttl=60)
        await redis.delete("test:key")

    # New test case: Test Redis with empty string value
    @pytest.mark.asyncio
    async def test_redis_empty_string_value(self):
        """Test Redis can store and retrieve empty strings."""
        redis = get_redis()
        test_key = "test:unit:empty_string"

        # Set empty string
        success = await redis.set(test_key, "", ttl=60)
        assert success is True

        # Get empty string
        value = await redis.get(test_key)
        assert value == ""

        # Cleanup
        await redis.delete(test_key)

    # New test case: Test Redis with large values
    @pytest.mark.asyncio
    async def test_redis_large_value(self):
        """Test Redis can handle large values."""
        redis = get_redis()
        test_key = "test:unit:large_value"

        # Create a large string (1MB)
        large_value = "x" * (1024 * 1024)

        # Set large value
        success = await redis.set(test_key, large_value, ttl=60)
        assert success is True

        # Get large value
        value = await redis.get(test_key)
        assert value == large_value
        assert len(value) == len(large_value)

        # Cleanup
        await redis.delete(test_key)

    # New test case: Test Redis with complex JSON structures
    @pytest.mark.asyncio
    async def test_redis_complex_json(self):
        """Test Redis with nested JSON structures."""
        redis = get_redis()
        test_key = "test:unit:complex_json"

        complex_data = {
            "recipe": {
                "name": "Chocolate Cake",
                "ingredients": [
                    {"name": "flour", "amount": 200, "unit": "g"},
                    {"name": "sugar", "amount": 150, "unit": "g"},
                ],
                "steps": ["Mix", "Bake", "Cool"],
                "metadata": {
                    "difficulty": "medium",
                    "time": 45,
                    "servings": 8,
                },
            }
        }

        # Set complex JSON
        success = await redis.set(test_key, complex_data, ttl=60)
        assert success is True

        # Get complex JSON
        value = await redis.get(test_key)
        assert value == complex_data
        assert value["recipe"]["name"] == "Chocolate Cake"
        assert len(value["recipe"]["ingredients"]) == 2

        # Cleanup
        await redis.delete(test_key)

    # New test case: Test Redis with numeric values
    @pytest.mark.asyncio
    async def test_redis_numeric_values(self):
        """Test Redis with various numeric types."""
        redis = get_redis()

        test_cases = [
            ("test:unit:int", 42),
            ("test:unit:float", 3.14159),
            ("test:unit:negative", -100),
            ("test:unit:zero", 0),
        ]

        for key, value in test_cases:
            # Set numeric value
            success = await redis.set(key, value, ttl=60)
            assert success is True

            # Get numeric value
            retrieved = await redis.get(key)
            assert retrieved == value

            # Cleanup
            await redis.delete(key)

    # New test case: Test Redis with boolean values
    @pytest.mark.asyncio
    async def test_redis_boolean_values(self):
        """Test Redis with boolean values."""
        redis = get_redis()

        # Test True
        await redis.set("test:unit:bool_true", True, ttl=60)
        value = await redis.get("test:unit:bool_true")
        assert value is True

        # Test False
        await redis.set("test:unit:bool_false", False, ttl=60)
        value = await redis.get("test:unit:bool_false")
        assert value is False

        # Cleanup
        await redis.delete("test:unit:bool_true")
        await redis.delete("test:unit:bool_false")

    # New test case: Test Redis with list values
    @pytest.mark.asyncio
    async def test_redis_list_values(self):
        """Test Redis with list values."""
        redis = get_redis()
        test_key = "test:unit:list"

        list_value = [1, 2, 3, "four", 5.5, True, None]

        # Set list
        success = await redis.set(test_key, list_value, ttl=60)
        assert success is True

        # Get list
        value = await redis.get(test_key)
        assert value == list_value

        # Cleanup
        await redis.delete(test_key)

    # New test case: Test Redis set operation without TTL
    @pytest.mark.asyncio
    async def test_redis_set_without_ttl(self):
        """Test Redis set operation without explicit TTL."""
        redis = get_redis()
        test_key = "test:unit:no_ttl"

        # Set without TTL (should use default or no expiration)
        success = await redis.set(test_key, "persistent_value")
        assert success is True

        # Value should exist
        value = await redis.get(test_key)
        assert value == "persistent_value"

        # Cleanup
        await redis.delete(test_key)

    # New test case: Test Redis delete multiple times
    @pytest.mark.asyncio
    async def test_redis_delete_idempotent(self):
        """Test that deleting the same key multiple times is safe."""
        redis = get_redis()
        test_key = "test:unit:delete_idempotent"

        # Set and delete
        await redis.set(test_key, "value", ttl=60)
        success1 = await redis.delete(test_key)
        assert success1 is True

        # Delete again (should return False)
        success2 = await redis.delete(test_key)
        assert success2 is False

        # Delete yet again (should still return False)
        success3 = await redis.delete(test_key)
        assert success3 is False

    # New test case: Test Redis pattern deletion with no matches
    @pytest.mark.asyncio
    async def test_redis_delete_pattern_no_matches(self):
        """Test Redis pattern deletion with no matching keys."""
        redis = get_redis()

        # Delete pattern that doesn't match anything
        deleted = await redis.delete_pattern("test:unit:nonexistent:*")
        assert deleted == 0

    # New test case: Test Redis exists with multiple keys
    @pytest.mark.asyncio
    async def test_redis_exists_multiple_keys(self):
        """Test Redis exists operation with multiple different keys."""
        redis = get_redis()
        keys = [f"test:unit:exists_multi:{i}" for i in range(3)]

        # Initially, none should exist
        for key in keys:
            assert await redis.exists(key) is False

        # Set all keys
        for key in keys:
            await redis.set(key, "value", ttl=60)

        # Now all should exist
        for key in keys:
            assert await redis.exists(key) is True

        # Cleanup
        for key in keys:
            await redis.delete(key)

    # New test case: Test Redis overwrite existing key
    @pytest.mark.asyncio
    async def test_redis_overwrite_key(self):
        """Test that setting an existing key overwrites the value."""
        redis = get_redis()
        test_key = "test:unit:overwrite"

        # Set initial value
        await redis.set(test_key, "initial", ttl=60)
        assert await redis.get(test_key) == "initial"

        # Overwrite with new value
        await redis.set(test_key, "updated", ttl=60)
        assert await redis.get(test_key) == "updated"

        # Overwrite with different type
        await redis.set(test_key, 123, ttl=60)
        assert await redis.get(test_key) == 123

        # Cleanup
        await redis.delete(test_key)

    # New test case: Test Redis with special characters in keys
    @pytest.mark.asyncio
    async def test_redis_special_characters_in_keys(self):
        """Test Redis with special characters in keys."""
        redis = get_redis()

        special_keys = [
            "test:unit:special:colon",
            "test:unit:special-dash",
            "test:unit:special_underscore",
            "test:unit:special.dot",
        ]

        for key in special_keys:
            await redis.set(key, "value", ttl=60)
            value = await redis.get(key)
            assert value == "value"
            await redis.delete(key)

    # New test case: Test Redis with Unicode values
    @pytest.mark.asyncio
    async def test_redis_unicode_values(self):
        """Test Redis with Unicode and international characters."""
        redis = get_redis()
        test_key = "test:unit:unicode"

        unicode_value = "Hello 世界 🌍 Привет مرحبا"

        # Set Unicode value
        await redis.set(test_key, unicode_value, ttl=60)

        # Get Unicode value
        value = await redis.get(test_key)
        assert value == unicode_value

        # Cleanup
        await redis.delete(test_key)

    # New test case: Test Redis concurrent writes to same key
    @pytest.mark.asyncio
    async def test_redis_concurrent_writes_same_key(self):
        """Test concurrent writes to the same key."""
        redis = get_redis()
        test_key = "test:unit:concurrent_write"

        async def write_value(value: int):
            await redis.set(test_key, value, ttl=60)

        # Write different values concurrently
        await asyncio.gather(*[write_value(i) for i in range(10)])

        # Key should exist with one of the values
        value = await redis.get(test_key)
        assert value is not None
        assert 0 <= value <= 9

        # Cleanup
        await redis.delete(test_key)

    # New test case: Test Redis pattern deletion with partial matches
    @pytest.mark.asyncio
    async def test_redis_delete_pattern_partial(self):
        """Test Redis pattern deletion with subset of keys."""
        redis = get_redis()

        # Create keys with different patterns
        pattern1_keys = [f"test:unit:pattern1:{i}" for i in range(3)]
        pattern2_keys = [f"test:unit:pattern2:{i}" for i in range(3)]

        # Set all keys
        for key in pattern1_keys + pattern2_keys:
            await redis.set(key, "value", ttl=60)

        # Delete only pattern1 keys
        deleted = await redis.delete_pattern("test:unit:pattern1:*")
        assert deleted == 3

        # Verify pattern1 keys are deleted
        for key in pattern1_keys:
            assert await redis.exists(key) is False

        # Verify pattern2 keys still exist
        for key in pattern2_keys:
            assert await redis.exists(key) is True

        # Cleanup
        await redis.delete_pattern("test:unit:pattern2:*")

    # New test case: Test Redis TTL with very short duration
    @pytest.mark.asyncio
    async def test_redis_very_short_ttl(self):
        """Test Redis with very short TTL (edge case)."""
        redis = get_redis()
        test_key = "test:unit:short_ttl"

        # Set with 1 second TTL
        await redis.set(test_key, "ephemeral", ttl=1)

        # Should exist immediately
        assert await redis.exists(test_key) is True

        # Wait for expiration
        await asyncio.sleep(1.5)

        # Should be gone
        assert await redis.exists(test_key) is False

    # New test case: Test Redis connection health check multiple times
    @pytest.mark.asyncio
    async def test_redis_ping_multiple_times(self):
        """Test Redis ping operation multiple times."""
        redis = get_redis()

        # Ping multiple times should all succeed
        for _ in range(5):
            result = await redis.ping()
            assert result is True

    # New test case: Test Redis with None value in complex structure
    @pytest.mark.asyncio
    async def test_redis_none_in_complex_structure(self):
        """Test Redis handling None values in complex structures."""
        redis = get_redis()
        test_key = "test:unit:none_complex"

        complex_data = {
            "field1": "value1",
            "field2": None,
            "field3": [1, None, 3],
            "field4": {"nested": None},
        }

        # Set complex data with None values
        await redis.set(test_key, complex_data, ttl=60)

        # Get and verify
        value = await redis.get(test_key)
        assert value == complex_data
        assert value["field2"] is None
        assert value["field3"][1] is None
        assert value["field4"]["nested"] is None

        # Cleanup
        await redis.delete(test_key)

    # New test case: Test Redis concurrent pattern deletions
    @pytest.mark.asyncio
    async def test_redis_concurrent_pattern_deletions(self):
        """Test concurrent pattern-based deletions."""
        redis = get_redis()

        # Create multiple sets of keys
        patterns = [f"test:unit:conc_del_{i}" for i in range(3)]

        for pattern in patterns:
            for j in range(5):
                await redis.set(f"{pattern}:{j}", "value", ttl=60)

        # Delete all patterns concurrently
        results = await asyncio.gather(*[
            redis.delete_pattern(f"{pattern}:*") for pattern in patterns
        ])

        # Each should have deleted 5 keys
        assert all(result == 5 for result in results)

    # New test case: Test Redis get operations on non-existent keys
    @pytest.mark.asyncio
    async def test_redis_get_nonexistent_multiple(self):
        """Test multiple get operations on non-existent keys."""
        redis = get_redis()

        keys = [f"test:unit:nonexistent_{i}" for i in range(5)]

        # All should return None
        for key in keys:
            value = await redis.get(key)
            assert value is None
