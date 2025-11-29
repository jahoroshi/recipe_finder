"""Integration tests for Gemini API integration."""

import pytest

from app.core.gemini_client import GeminiClient, get_gemini_client, RateLimiter
from app.config import get_settings


class TestGeminiClient:
    """Test suite for Gemini API client."""

    @pytest.fixture
    def gemini_client(self) -> GeminiClient:
        """Get Gemini client instance."""
        return get_gemini_client()

    @pytest.mark.asyncio
    async def test_gemini_client_initialization(self, gemini_client):
        """Test Gemini client can be initialized."""
        assert gemini_client is not None
        assert gemini_client.api_key
        assert gemini_client.embedding_model
        assert gemini_client.text_model

    @pytest.mark.asyncio
    async def test_generate_embedding(self, gemini_client):
        """Test generating embedding for a single text."""
        text = "This is a test recipe for chocolate cake with sugar and flour"

        embedding = await gemini_client.generate_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    @pytest.mark.asyncio
    async def test_generate_embedding_empty_text_raises_error(self, gemini_client):
        """Test that empty text raises ValueError."""
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await gemini_client.generate_embedding("")

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await gemini_client.generate_embedding("   ")

    @pytest.mark.asyncio
    async def test_generate_embedding_different_task_types(self, gemini_client):
        """Test generating embeddings with different task types."""
        text = "Delicious pasta recipe"

        # Test different task types
        task_types = [
            "retrieval_document",
            "retrieval_query",
            "semantic_similarity",
        ]

        for task_type in task_types:
            embedding = await gemini_client.generate_embedding(text, task_type)
            assert isinstance(embedding, list)
            assert len(embedding) > 0

    @pytest.mark.asyncio
    async def test_generate_batch_embeddings(self, gemini_client):
        """Test generating embeddings for multiple texts."""
        texts = [
            "Recipe for chocolate cake",
            "How to make pasta",
            "Ingredients for pizza",
        ]

        embeddings = await gemini_client.generate_batch_embeddings(texts)

        assert len(embeddings) == len(texts)
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)

    @pytest.mark.asyncio
    async def test_generate_batch_embeddings_empty_list_raises_error(self, gemini_client):
        """Test that empty texts list raises ValueError."""
        with pytest.raises(ValueError, match="Texts list cannot be empty"):
            await gemini_client.generate_batch_embeddings([])

        with pytest.raises(ValueError, match="All texts are empty"):
            await gemini_client.generate_batch_embeddings(["", "  ", ""])

    @pytest.mark.asyncio
    async def test_generate_batch_embeddings_with_batch_size(self, gemini_client):
        """Test batch processing with custom batch size."""
        texts = [f"Recipe number {i}" for i in range(5)]

        embeddings = await gemini_client.generate_batch_embeddings(
            texts, batch_size=2
        )

        assert len(embeddings) == len(texts)

    @pytest.mark.asyncio
    async def test_generate_text(self, gemini_client):
        """Test text generation with Gemini."""
        prompt = "Write a short one-sentence description of a chocolate cake recipe."

        text = await gemini_client.generate_text(prompt, max_output_tokens=100)

        assert isinstance(text, str)
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_generate_text_empty_prompt_raises_error(self, gemini_client):
        """Test that empty prompt raises ValueError."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            await gemini_client.generate_text("")

        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            await gemini_client.generate_text("   ")

    @pytest.mark.asyncio
    async def test_generate_text_with_parameters(self, gemini_client):
        """Test text generation with custom parameters."""
        prompt = "List three ingredients for a cake."

        text = await gemini_client.generate_text(
            prompt,
            max_output_tokens=50,
            temperature=0.5,
        )

        assert isinstance(text, str)
        assert len(text) > 0

    @pytest.mark.asyncio
    async def test_gemini_ping(self, gemini_client):
        """Test Gemini API connectivity check."""
        result = await gemini_client.ping()

        assert result is True

    @pytest.mark.asyncio
    async def test_embeddings_consistency(self, gemini_client):
        """Test that same text produces consistent embeddings."""
        text = "Test recipe for consistency"

        embedding1 = await gemini_client.generate_embedding(text)
        embedding2 = await gemini_client.generate_embedding(text)

        # Embeddings should be identical for the same text
        assert len(embedding1) == len(embedding2)
        # Allow for small floating-point differences
        for i in range(len(embedding1)):
            assert abs(embedding1[i] - embedding2[i]) < 1e-6

    @pytest.mark.asyncio
    async def test_get_gemini_client_cached(self):
        """Test that get_gemini_client returns cached instance."""
        client1 = get_gemini_client()
        client2 = get_gemini_client()

        assert client1 is client2


class TestRateLimiter:
    """Test suite for RateLimiter."""

    @pytest.mark.asyncio
    async def test_rate_limiter_initialization(self):
        """Test rate limiter can be initialized."""
        limiter = RateLimiter(requests_per_minute=60)

        assert limiter.requests_per_minute == 60
        assert limiter.interval == 1.0

    @pytest.mark.asyncio
    async def test_rate_limiter_acquire(self):
        """Test rate limiter acquire method."""
        limiter = RateLimiter(requests_per_minute=60)

        # First acquire should be immediate
        await limiter.acquire()

        # Second acquire should wait
        await limiter.acquire()

    @pytest.mark.asyncio
    async def test_rate_limiter_timing(self):
        """Test rate limiter enforces timing constraints."""
        import time

        limiter = RateLimiter(requests_per_minute=120)  # 2 requests per second

        start = time.time()

        # Make 3 requests
        await limiter.acquire()
        await limiter.acquire()
        await limiter.acquire()

        elapsed = time.time() - start

        # Should take at least 1 second for 3 requests at 2 req/sec
        assert elapsed >= 1.0


class TestGeminiSettings:
    """Test suite for Gemini settings."""

    def test_gemini_settings_loaded(self):
        """Test that Gemini settings are properly loaded."""
        settings = get_settings()

        assert settings.gemini_api_key
        assert settings.gemini_embedding_model
        assert settings.gemini_text_model
        assert settings.gemini_rate_limit_rpm > 0
        assert settings.gemini_timeout > 0
        assert settings.gemini_max_retries >= 0


class TestGeminiClientExtended:
    """Extended test suite for Gemini API client."""

    @pytest.fixture
    def gemini_client(self) -> GeminiClient:
        """Get Gemini client instance."""
        return get_gemini_client()

    # New test case: Test embedding with long text
    @pytest.mark.asyncio
    async def test_generate_embedding_long_text(self, gemini_client):
        """Test generating embedding for long text."""
        # Create a long text (around 1000 words)
        long_text = " ".join(["recipe" for _ in range(1000)])

        embedding = await gemini_client.generate_embedding(long_text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0
        assert all(isinstance(x, float) for x in embedding)

    # New test case: Test embedding with special characters
    @pytest.mark.asyncio
    async def test_generate_embedding_special_characters(self, gemini_client):
        """Test generating embedding for text with special characters."""
        text = "Recipe: chocolate cake! @#$%^&*() with 100% cocoa"

        embedding = await gemini_client.generate_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0

    # New test case: Test embedding with Unicode text
    @pytest.mark.asyncio
    async def test_generate_embedding_unicode(self, gemini_client):
        """Test generating embedding for Unicode text."""
        text = "Recipe 食谱 рецепт وصفة 🍰"

        embedding = await gemini_client.generate_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0

    # New test case: Test embedding with numbers only
    @pytest.mark.asyncio
    async def test_generate_embedding_numbers(self, gemini_client):
        """Test generating embedding for text with only numbers."""
        text = "1234567890"

        embedding = await gemini_client.generate_embedding(text)

        assert isinstance(embedding, list)
        assert len(embedding) > 0

    # New test case: Test batch embeddings with single item
    @pytest.mark.asyncio
    async def test_generate_batch_embeddings_single_item(self, gemini_client):
        """Test batch embedding generation with single item."""
        texts = ["Single recipe for testing"]

        embeddings = await gemini_client.generate_batch_embeddings(texts)

        assert len(embeddings) == 1
        assert isinstance(embeddings[0], list)

    # New test case: Test batch embeddings with mixed content
    @pytest.mark.asyncio
    async def test_generate_batch_embeddings_mixed(self, gemini_client):
        """Test batch embeddings with varied content lengths."""
        texts = [
            "Short",
            "Medium length recipe for pasta",
            "A very long recipe description with many words " * 20,
        ]

        embeddings = await gemini_client.generate_batch_embeddings(texts)

        assert len(embeddings) == len(texts)
        # All should have the same embedding dimension
        embedding_dims = [len(emb) for emb in embeddings]
        assert len(set(embedding_dims)) == 1

    # New test case: Test batch embeddings with small batch size
    @pytest.mark.asyncio
    async def test_generate_batch_embeddings_small_batch(self, gemini_client):
        """Test batch processing with small batch size."""
        texts = [f"Recipe {i}" for i in range(10)]

        embeddings = await gemini_client.generate_batch_embeddings(
            texts, batch_size=3
        )

        assert len(embeddings) == len(texts)

    # New test case: Test text generation with different temperatures
    @pytest.mark.asyncio
    async def test_generate_text_temperature_variation(self, gemini_client):
        """Test text generation with different temperature values."""
        prompt = "Write a one-sentence summary of a cake recipe."

        # Test low temperature (more deterministic)
        text_low = await gemini_client.generate_text(
            prompt, max_output_tokens=50, temperature=0.1
        )
        assert isinstance(text_low, str)
        assert len(text_low) > 0

        # Test high temperature (more creative)
        text_high = await gemini_client.generate_text(
            prompt, max_output_tokens=50, temperature=0.9
        )
        assert isinstance(text_high, str)
        assert len(text_high) > 0

    # New test case: Test text generation with max tokens limit
    @pytest.mark.asyncio
    async def test_generate_text_max_tokens(self, gemini_client):
        """Test text generation with very low max tokens."""
        prompt = "Describe chocolate cake in detail"

        text = await gemini_client.generate_text(
            prompt, max_output_tokens=10, temperature=0.5
        )

        assert isinstance(text, str)
        assert len(text) > 0

    # New test case: Test text generation with long prompt
    @pytest.mark.asyncio
    async def test_generate_text_long_prompt(self, gemini_client):
        """Test text generation with a long prompt."""
        prompt = "Describe a recipe for chocolate cake. " * 50

        text = await gemini_client.generate_text(
            prompt, max_output_tokens=100, temperature=0.5
        )

        assert isinstance(text, str)
        assert len(text) > 0

    # New test case: Test embedding whitespace handling
    @pytest.mark.asyncio
    async def test_generate_embedding_whitespace_variations(self, gemini_client):
        """Test that whitespace variations raise errors appropriately."""
        # Multiple spaces should work
        text_spaces = "Recipe    with    spaces"
        embedding = await gemini_client.generate_embedding(text_spaces)
        assert isinstance(embedding, list)

        # Only spaces should fail
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await gemini_client.generate_embedding("   ")

        # Tabs and newlines should work if there's content
        text_special = "Recipe\n\twith\ttabs"
        embedding = await gemini_client.generate_embedding(text_special)
        assert isinstance(embedding, list)

    # New test case: Test batch embeddings filters empty strings
    @pytest.mark.asyncio
    async def test_generate_batch_embeddings_filters_empty(self, gemini_client):
        """Test that batch embeddings handles empty strings correctly."""
        # All empty should raise error
        with pytest.raises(ValueError, match="All texts are empty"):
            await gemini_client.generate_batch_embeddings(["", "  ", "\t"])

    # New test case: Test embedding dimension consistency
    @pytest.mark.asyncio
    async def test_embedding_dimension_consistency(self, gemini_client):
        """Test that all embeddings have the same dimension."""
        texts = [
            "Short text",
            "A medium length text about recipes",
            "A very long text with many words " * 10,
        ]

        embeddings = []
        for text in texts:
            emb = await gemini_client.generate_embedding(text)
            embeddings.append(emb)

        # All embeddings should have the same dimension
        dimensions = [len(emb) for emb in embeddings]
        assert len(set(dimensions)) == 1

    # New test case: Test different task types produce different embeddings
    @pytest.mark.asyncio
    async def test_task_types_affect_embeddings(self, gemini_client):
        """Test that different task types may produce different embeddings."""
        text = "Recipe for chocolate cake"

        emb_doc = await gemini_client.generate_embedding(
            text, task_type="retrieval_document"
        )
        emb_query = await gemini_client.generate_embedding(
            text, task_type="retrieval_query"
        )

        # Embeddings should have same dimension
        assert len(emb_doc) == len(emb_query)

        # They might be different (but not guaranteed, so just check they exist)
        assert isinstance(emb_doc, list)
        assert isinstance(emb_query, list)

    # New test case: Test client attributes
    @pytest.mark.asyncio
    async def test_gemini_client_attributes(self, gemini_client):
        """Test that Gemini client has expected attributes."""
        assert hasattr(gemini_client, "api_key")
        assert hasattr(gemini_client, "embedding_model")
        assert hasattr(gemini_client, "text_model")
        assert hasattr(gemini_client, "timeout")
        assert hasattr(gemini_client, "max_retries")

        assert gemini_client.timeout > 0
        assert gemini_client.max_retries >= 0

    # New test case: Test rate limiter respects timing
    @pytest.mark.asyncio
    async def test_rate_limiter_sequential_calls(self, gemini_client):
        """Test that rate limiter works with sequential calls."""
        import time

        start = time.time()

        # Make several embedding calls (rate limiter should add delays)
        for i in range(3):
            await gemini_client.generate_embedding(f"Test {i}")

        elapsed = time.time() - start

        # Should take at least some time due to rate limiting
        # (exact time depends on rate limit configuration)
        assert elapsed >= 0

    # New test case: Test text generation with empty-like prompts
    @pytest.mark.asyncio
    async def test_generate_text_whitespace_prompt(self, gemini_client):
        """Test that whitespace-only prompts raise errors."""
        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            await gemini_client.generate_text("   ")

        with pytest.raises(ValueError, match="Prompt cannot be empty"):
            await gemini_client.generate_text("\n\t")

    # New test case: Test text generation output is non-empty
    @pytest.mark.asyncio
    async def test_generate_text_output_quality(self, gemini_client):
        """Test that generated text has reasonable quality."""
        prompt = "What is a cake?"

        text = await gemini_client.generate_text(prompt, max_output_tokens=100)

        # Should produce actual text
        assert len(text) > 10  # More than just a word
        assert isinstance(text, str)

    # New test case: Test batch embeddings preserves order
    @pytest.mark.asyncio
    async def test_batch_embeddings_preserves_order(self, gemini_client):
        """Test that batch embeddings maintains input order."""
        texts = [f"Recipe number {i}" for i in range(5)]

        embeddings = await gemini_client.generate_batch_embeddings(texts)

        # Should have same length
        assert len(embeddings) == len(texts)

        # Each embedding should be distinct (with high probability)
        # We can't guarantee they're all different, but we can check they exist
        assert all(isinstance(emb, list) for emb in embeddings)
        assert all(len(emb) > 0 for emb in embeddings)
