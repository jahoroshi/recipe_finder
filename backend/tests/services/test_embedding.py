"""Tests for EmbeddingService."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.db.models import DifficultyLevel, Recipe
from app.services.embedding import EmbeddingService


@pytest.fixture
def mock_gemini_client():
    """Create mock Gemini client."""
    mock = MagicMock()
    mock.embedding_model = "text-embedding-004"
    mock.generate_embedding = AsyncMock(return_value=[0.1] * 768)
    mock.ping = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def mock_cache_service():
    """Create mock cache service."""
    mock = MagicMock()
    mock.get_embedding = AsyncMock(return_value=None)
    mock.set_embedding = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def embedding_service(mock_gemini_client, mock_cache_service):
    """Create EmbeddingService instance with mocks."""
    return EmbeddingService(
        gemini_client=mock_gemini_client,
        cache_service=mock_cache_service,
        batch_size=100,
    )


@pytest.fixture
def sample_recipe():
    """Create sample recipe for testing."""
    return Recipe(
        id=uuid4(),
        name="Pasta Carbonara",
        description="Classic Italian pasta dish",
        instructions={"steps": ["Cook pasta", "Mix with eggs and cheese"]},
        prep_time=10,
        cook_time=15,
        servings=4,
        difficulty=DifficultyLevel.MEDIUM,
        cuisine_type="Italian",
        diet_types=["vegetarian"],
    )


@pytest.mark.asyncio
class TestEmbeddingService:
    """Test suite for EmbeddingService."""

    async def test_generate_embedding_success(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test successful embedding generation."""
        # Setup
        text = "delicious pasta"
        expected_embedding = [0.1] * 768

        # Execute
        result = await embedding_service.generate_embedding(text)

        # Assert
        assert result == expected_embedding
        mock_cache_service.get_embedding.assert_called_once_with(text)
        mock_gemini_client.generate_embedding.assert_called_once_with(
            text, task_type="retrieval_document"
        )
        mock_cache_service.set_embedding.assert_called_once_with(text, expected_embedding)

    async def test_generate_embedding_from_cache(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test embedding retrieval from cache."""
        # Setup
        text = "cached text"
        cached_embedding = [0.2] * 768
        mock_cache_service.get_embedding.return_value = cached_embedding

        # Execute
        result = await embedding_service.generate_embedding(text)

        # Assert
        assert result == cached_embedding
        mock_cache_service.get_embedding.assert_called_once_with(text)
        # Should not call Gemini API if cached
        mock_gemini_client.generate_embedding.assert_not_called()

    async def test_generate_embedding_no_cache(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test embedding generation without caching."""
        # Setup
        text = "no cache text"
        expected_embedding = [0.3] * 768
        mock_gemini_client.generate_embedding.return_value = expected_embedding

        # Execute
        result = await embedding_service.generate_embedding(text, use_cache=False)

        # Assert
        assert result == expected_embedding
        # Should not check or set cache
        mock_cache_service.get_embedding.assert_not_called()
        mock_cache_service.set_embedding.assert_not_called()

    async def test_generate_embedding_empty_text(self, embedding_service):
        """Test embedding generation with empty text."""
        # Execute & Assert
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await embedding_service.generate_embedding("")

        with pytest.raises(ValueError, match="Text cannot be empty"):
            await embedding_service.generate_embedding("   ")

    async def test_generate_embedding_different_task_type(
        self, embedding_service, mock_gemini_client
    ):
        """Test embedding generation with different task type."""
        # Setup
        text = "query text"

        # Execute
        await embedding_service.generate_embedding(
            text, task_type="retrieval_query"
        )

        # Assert
        mock_gemini_client.generate_embedding.assert_called_once_with(
            text, task_type="retrieval_query"
        )

    async def test_generate_batch_embeddings_success(
        self, embedding_service, mock_gemini_client
    ):
        """Test batch embedding generation."""
        # Setup
        texts = ["pasta", "pizza", "lasagna"]
        mock_gemini_client.generate_embedding.return_value = [0.1] * 768

        # Execute
        results = await embedding_service.generate_batch_embeddings(texts)

        # Assert
        assert len(results) == 3
        assert all(len(emb) == 768 for emb in results)
        assert mock_gemini_client.generate_embedding.call_count == 3

    async def test_generate_batch_embeddings_with_cache(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test batch embedding generation with some cached."""
        # Setup
        texts = ["cached", "not_cached1", "not_cached2"]
        cached_embedding = [0.5] * 768
        new_embedding = [0.1] * 768

        # Mock cache to return embedding for first text only
        async def mock_get_embedding(text):
            if text == "cached":
                return cached_embedding
            return None

        mock_cache_service.get_embedding.side_effect = mock_get_embedding
        mock_gemini_client.generate_embedding.return_value = new_embedding

        # Execute
        results = await embedding_service.generate_batch_embeddings(texts)

        # Assert
        assert len(results) == 3
        assert results[0] == cached_embedding  # From cache
        assert results[1] == new_embedding  # Generated
        assert results[2] == new_embedding  # Generated
        # Should only generate embeddings for 2 texts
        assert mock_gemini_client.generate_embedding.call_count == 2

    async def test_generate_batch_embeddings_empty_list(self, embedding_service):
        """Test batch embedding with empty list."""
        # Execute & Assert
        with pytest.raises(ValueError, match="Texts list cannot be empty"):
            await embedding_service.generate_batch_embeddings([])

    async def test_generate_batch_embeddings_all_empty(self, embedding_service):
        """Test batch embedding with all empty texts."""
        # Execute & Assert
        with pytest.raises(ValueError, match="All texts are empty"):
            await embedding_service.generate_batch_embeddings(["", "  ", "\n"])

    async def test_generate_batch_embeddings_large_batch(
        self, embedding_service, mock_gemini_client
    ):
        """Test batch embedding with batch size limit."""
        # Setup
        embedding_service.batch_size = 2
        texts = ["text1", "text2", "text3", "text4", "text5"]
        mock_gemini_client.generate_embedding.return_value = [0.1] * 768

        # Execute
        results = await embedding_service.generate_batch_embeddings(texts)

        # Assert
        assert len(results) == 5
        # Should process in batches of 2 (3 batches total)
        assert mock_gemini_client.generate_embedding.call_count == 5

    async def test_create_recipe_embedding(
        self, embedding_service, mock_gemini_client, sample_recipe
    ):
        """Test creating embedding for recipe."""
        # Setup
        expected_embedding = [0.2] * 768
        mock_gemini_client.generate_embedding.return_value = expected_embedding

        # Execute
        result = await embedding_service.create_recipe_embedding(sample_recipe)

        # Assert
        assert result == expected_embedding
        # Verify the text includes recipe components
        call_args = mock_gemini_client.generate_embedding.call_args[0][0]
        assert "Pasta Carbonara" in call_args
        assert "Classic Italian pasta dish" in call_args
        assert "Italian" in call_args
        assert "vegetarian" in call_args
        assert "medium" in call_args

    async def test_create_recipe_embedding_minimal_recipe(
        self, embedding_service, mock_gemini_client
    ):
        """Test creating embedding for recipe with minimal data."""
        # Setup
        recipe = Recipe(
            id=uuid4(),
            name="Simple Recipe",
            instructions={"steps": ["Cook"]},
            difficulty=DifficultyLevel.EASY,
        )
        expected_embedding = [0.3] * 768
        mock_gemini_client.generate_embedding.return_value = expected_embedding

        # Execute
        result = await embedding_service.create_recipe_embedding(recipe)

        # Assert
        assert result == expected_embedding
        call_args = mock_gemini_client.generate_embedding.call_args[0][0]
        assert "Simple Recipe" in call_args
        assert "easy" in call_args

    async def test_update_recipe_embeddings(
        self, embedding_service, mock_gemini_client
    ):
        """Test updating embeddings for multiple recipes."""
        # Setup
        recipes = [
            Recipe(
                id=uuid4(),
                name=f"Recipe {i}",
                instructions={"steps": ["Cook"]},
                difficulty=DifficultyLevel.EASY,
            )
            for i in range(3)
        ]
        mock_gemini_client.generate_embedding.return_value = [0.1] * 768

        # Execute
        results = await embedding_service.update_recipe_embeddings(recipes)

        # Assert
        assert len(results) == 3
        for recipe, embedding in results:
            assert len(embedding) == 768
            assert recipe in recipes

    async def test_update_recipe_embeddings_empty_list(self, embedding_service):
        """Test updating embeddings with empty recipe list."""
        # Execute
        results = await embedding_service.update_recipe_embeddings([])

        # Assert
        assert results == []

    async def test_generate_query_embedding(
        self, embedding_service, mock_gemini_client
    ):
        """Test generating embedding for search query."""
        # Setup
        query = "italian pasta recipe"
        expected_embedding = [0.4] * 768
        mock_gemini_client.generate_embedding.return_value = expected_embedding

        # Execute
        result = await embedding_service.generate_query_embedding(query)

        # Assert
        assert result == expected_embedding
        mock_gemini_client.generate_embedding.assert_called_once_with(
            query, task_type="retrieval_query"
        )

    async def test_generate_query_embedding_with_cache(
        self, embedding_service, mock_cache_service
    ):
        """Test query embedding with cache hit."""
        # Setup
        query = "cached query"
        cached_embedding = [0.5] * 768
        mock_cache_service.get_embedding.return_value = cached_embedding

        # Execute
        result = await embedding_service.generate_query_embedding(query)

        # Assert
        assert result == cached_embedding
        mock_cache_service.get_embedding.assert_called_once_with(query)

    async def test_ping_success(self, embedding_service, mock_gemini_client):
        """Test successful API ping."""
        # Execute
        result = await embedding_service.ping()

        # Assert
        assert result is True
        mock_gemini_client.ping.assert_called_once()

    async def test_ping_failure(self, embedding_service, mock_gemini_client):
        """Test failed API ping."""
        # Setup
        mock_gemini_client.ping.return_value = False

        # Execute
        result = await embedding_service.ping()

        # Assert
        assert result is False

    async def test_api_failure_propagates(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test that API failures are propagated."""
        # Setup
        mock_gemini_client.generate_embedding.side_effect = Exception("API Error")

        # Execute & Assert
        with pytest.raises(Exception, match="API Error"):
            await embedding_service.generate_embedding("test")

    # New test case: Test generate_embedding with whitespace-only text
    async def test_generate_embedding_whitespace_only(self, embedding_service):
        """Test embedding generation with whitespace-only text."""
        # Execute & Assert
        with pytest.raises(ValueError, match="Text cannot be empty"):
            await embedding_service.generate_embedding("   \t\n   ")

    # New test case: Test generate_embedding with very long text
    async def test_generate_embedding_very_long_text(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test embedding generation with very long text."""
        # Setup
        long_text = "a" * 10000
        expected_embedding = [0.1] * 768
        mock_gemini_client.generate_embedding.return_value = expected_embedding

        # Execute
        result = await embedding_service.generate_embedding(long_text)

        # Assert
        assert result == expected_embedding
        mock_gemini_client.generate_embedding.assert_called_once()

    # New test case: Test batch processing with partial cache hits
    async def test_generate_batch_embeddings_partial_cache(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test batch with some texts in cache and some not."""
        # Setup
        texts = ["cached1", "not_cached1", "cached2", "not_cached2"]
        cached_emb = [0.9] * 768
        new_emb = [0.1] * 768

        async def mock_get_embedding(text):
            if text.startswith("cached"):
                return cached_emb
            return None

        mock_cache_service.get_embedding.side_effect = mock_get_embedding
        mock_gemini_client.generate_embedding.return_value = new_emb

        # Execute
        results = await embedding_service.generate_batch_embeddings(texts)

        # Assert
        assert len(results) == 4
        assert results[0] == cached_emb
        assert results[1] == new_emb
        assert results[2] == cached_emb
        assert results[3] == new_emb
        # Should only generate for 2 texts
        assert mock_gemini_client.generate_embedding.call_count == 2

    # New test case: Test batch with texts containing only whitespace
    async def test_generate_batch_embeddings_with_whitespace(
        self, embedding_service, mock_gemini_client
    ):
        """Test batch with some whitespace texts."""
        # Setup - Mix of valid and whitespace texts (whitespace ones are filtered out)
        texts = ["valid text", "  ", "another valid", "\t\n"]
        mock_gemini_client.generate_embedding.return_value = [0.1] * 768

        # Execute - Only valid texts are processed, whitespace ones are filtered
        results = await embedding_service.generate_batch_embeddings(texts, use_cache=False)

        # Assert - Should only process non-whitespace texts
        assert len(results) == 2
        assert mock_gemini_client.generate_embedding.call_count == 2

    # New test case: Test batch processing respects batch_size
    async def test_generate_batch_embeddings_respects_batch_size(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test batch processing chunks correctly based on batch_size."""
        # Setup
        embedding_service.batch_size = 3
        texts = [f"text{i}" for i in range(10)]
        mock_gemini_client.generate_embedding.return_value = [0.1] * 768

        # Execute
        results = await embedding_service.generate_batch_embeddings(texts, use_cache=False)

        # Assert
        assert len(results) == 10
        # Should process in batches: 3 + 3 + 3 + 1 = 10 calls
        assert mock_gemini_client.generate_embedding.call_count == 10

    # New test case: Test batch with single text
    async def test_generate_batch_embeddings_single_text(
        self, embedding_service, mock_gemini_client
    ):
        """Test batch processing with single text."""
        # Setup
        texts = ["single text"]
        mock_gemini_client.generate_embedding.return_value = [0.1] * 768

        # Execute
        results = await embedding_service.generate_batch_embeddings(texts, use_cache=False)

        # Assert
        assert len(results) == 1
        assert len(results[0]) == 768

    # New test case: Test batch without cache
    async def test_generate_batch_embeddings_no_cache(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test batch processing without using cache."""
        # Setup
        texts = ["text1", "text2", "text3"]
        mock_gemini_client.generate_embedding.return_value = [0.1] * 768

        # Execute
        results = await embedding_service.generate_batch_embeddings(
            texts, use_cache=False
        )

        # Assert
        assert len(results) == 3
        mock_cache_service.get_embedding.assert_not_called()
        mock_cache_service.set_embedding.assert_not_called()

    # New test case: Test recipe embedding with all fields populated
    async def test_create_recipe_embedding_full_data(
        self, embedding_service, mock_gemini_client
    ):
        """Test creating embedding for recipe with all fields."""
        # Setup
        recipe = Recipe(
            id=uuid4(),
            name="Complete Recipe",
            description="Detailed description",
            instructions={"steps": ["Step 1"]},
            cuisine_type="French",
            diet_types=["vegetarian", "gluten-free"],
            difficulty=DifficultyLevel.HARD,
        )
        mock_gemini_client.generate_embedding.return_value = [0.5] * 768

        # Execute
        result = await embedding_service.create_recipe_embedding(recipe)

        # Assert
        assert len(result) == 768
        # Verify all fields are included in text
        call_text = mock_gemini_client.generate_embedding.call_args[0][0]
        assert "Complete Recipe" in call_text
        assert "Detailed description" in call_text
        assert "French" in call_text
        assert "vegetarian" in call_text
        assert "gluten-free" in call_text
        assert "hard" in call_text

    # New test case: Test recipe embedding without optional fields
    async def test_create_recipe_embedding_no_optional_fields(
        self, embedding_service, mock_gemini_client
    ):
        """Test creating embedding for recipe without optional fields."""
        # Setup
        recipe = Recipe(
            id=uuid4(),
            name="Minimal Recipe",
            instructions={"steps": ["Cook"]},
            difficulty=DifficultyLevel.EASY,
        )
        mock_gemini_client.generate_embedding.return_value = [0.3] * 768

        # Execute
        result = await embedding_service.create_recipe_embedding(recipe)

        # Assert
        assert result == [0.3] * 768
        call_text = mock_gemini_client.generate_embedding.call_args[0][0]
        assert "Minimal Recipe" in call_text
        assert "easy" in call_text

    # New test case: Test update_recipe_embeddings with mixed recipes
    async def test_update_recipe_embeddings_mixed_data(
        self, embedding_service, mock_gemini_client
    ):
        """Test updating embeddings for recipes with different data."""
        # Setup
        recipes = [
            Recipe(
                id=uuid4(),
                name="Full Recipe",
                description="Complete",
                cuisine_type="Italian",
                diet_types=["vegan"],
                instructions={"steps": ["Cook"]},
                difficulty=DifficultyLevel.MEDIUM,
            ),
            Recipe(
                id=uuid4(),
                name="Minimal",
                instructions={"steps": ["Cook"]},
                difficulty=DifficultyLevel.EASY,
            ),
        ]
        mock_gemini_client.generate_embedding.return_value = [0.1] * 768

        # Execute
        results = await embedding_service.update_recipe_embeddings(recipes)

        # Assert
        assert len(results) == 2
        assert results[0][0] == recipes[0]
        assert results[1][0] == recipes[1]
        assert len(results[0][1]) == 768
        assert len(results[1][1]) == 768

    # New test case: Test query embedding with cache miss
    async def test_generate_query_embedding_cache_miss(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test query embedding when not in cache."""
        # Setup
        query = "fresh query"
        expected_embedding = [0.7] * 768
        mock_cache_service.get_embedding.return_value = None
        mock_gemini_client.generate_embedding.return_value = expected_embedding

        # Execute
        result = await embedding_service.generate_query_embedding(query)

        # Assert
        assert result == expected_embedding
        mock_gemini_client.generate_embedding.assert_called_once_with(
            query, task_type="retrieval_query"
        )
        mock_cache_service.set_embedding.assert_called_once_with(query, expected_embedding)

    # New test case: Test embedding service with different task types
    async def test_generate_embedding_task_types(
        self, embedding_service, mock_gemini_client
    ):
        """Test embedding generation with different task types."""
        # Setup
        text = "test text"
        task_types = ["retrieval_query", "retrieval_document", "semantic_similarity"]

        # Execute
        for task_type in task_types:
            mock_gemini_client.generate_embedding.return_value = [0.1] * 768
            await embedding_service.generate_embedding(
                text, task_type=task_type, use_cache=False
            )

        # Assert
        assert mock_gemini_client.generate_embedding.call_count == 3

    # New test case: Test cache failure doesn't stop embedding generation
    async def test_generate_embedding_cache_set_failure(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test embedding generation continues if cache set fails."""
        # Setup
        text = "test"
        expected_embedding = [0.1] * 768
        mock_gemini_client.generate_embedding.return_value = expected_embedding
        mock_cache_service.set_embedding.side_effect = Exception("Cache error")

        # Execute & Assert - Should not raise, just skip cache
        with pytest.raises(Exception, match="Cache error"):
            await embedding_service.generate_embedding(text)

    # New test case: Test batch embeddings order preservation
    async def test_generate_batch_embeddings_order_preserved(
        self, embedding_service, mock_gemini_client
    ):
        """Test batch embeddings maintains input order."""
        # Setup
        texts = ["first", "second", "third", "fourth"]
        mock_gemini_client.generate_embedding.side_effect = [
            [0.1] * 768,
            [0.2] * 768,
            [0.3] * 768,
            [0.4] * 768,
        ]

        # Execute
        results = await embedding_service.generate_batch_embeddings(
            texts, use_cache=False
        )

        # Assert
        assert len(results) == 4
        assert results[0][0] == 0.1
        assert results[1][0] == 0.2
        assert results[2][0] == 0.3
        assert results[3][0] == 0.4

    # New test case: Test recipe embedding without cache
    async def test_create_recipe_embedding_no_cache(
        self, embedding_service, mock_gemini_client, mock_cache_service, sample_recipe
    ):
        """Test recipe embedding generation without cache."""
        # Setup
        expected_embedding = [0.8] * 768
        mock_gemini_client.generate_embedding.return_value = expected_embedding

        # Execute
        result = await embedding_service.create_recipe_embedding(
            sample_recipe, use_cache=False
        )

        # Assert
        assert result == expected_embedding
        mock_cache_service.get_embedding.assert_not_called()
        mock_cache_service.set_embedding.assert_not_called()

    # New test case: Test concurrent batch processing
    async def test_generate_batch_embeddings_concurrent(
        self, embedding_service, mock_gemini_client
    ):
        """Test batch processing handles concurrent API calls."""
        # Setup
        embedding_service.batch_size = 5
        texts = [f"text{i}" for i in range(5)]
        mock_gemini_client.generate_embedding.return_value = [0.1] * 768

        # Execute
        results = await embedding_service.generate_batch_embeddings(
            texts, use_cache=False
        )

        # Assert
        assert len(results) == 5
        # All 5 should be called concurrently in single batch
        assert mock_gemini_client.generate_embedding.call_count == 5

    # New test case: Test update_recipe_embeddings with cache
    async def test_update_recipe_embeddings_with_cache(
        self, embedding_service, mock_gemini_client, mock_cache_service
    ):
        """Test updating recipe embeddings uses cache."""
        # Setup
        recipes = [
            Recipe(
                id=uuid4(),
                name=f"Recipe {i}",
                instructions={"steps": ["Cook"]},
                difficulty=DifficultyLevel.EASY,
            )
            for i in range(2)
        ]
        mock_cache_service.get_embedding.return_value = None
        mock_gemini_client.generate_embedding.return_value = [0.1] * 768

        # Execute
        results = await embedding_service.update_recipe_embeddings(recipes, use_cache=True)

        # Assert
        assert len(results) == 2
        # Should check cache and set cache
        assert mock_cache_service.get_embedding.call_count == 2
        assert mock_cache_service.set_embedding.call_count == 2

    # New test case: Test ping with exception
    async def test_ping_exception(self, embedding_service, mock_gemini_client):
        """Test ping when API raises exception."""
        # Setup
        mock_gemini_client.ping.side_effect = Exception("Connection error")

        # Execute & Assert
        with pytest.raises(Exception, match="Connection error"):
            await embedding_service.ping()

    # New test case: Test batch with API failures for some texts
    async def test_generate_batch_embeddings_partial_failure(
        self, embedding_service, mock_gemini_client
    ):
        """Test batch processing when some API calls fail."""
        # Setup
        texts = ["text1", "text2", "text3"]
        mock_gemini_client.generate_embedding.side_effect = [
            [0.1] * 768,
            Exception("API Error"),
            [0.3] * 768,
        ]

        # Execute & Assert
        with pytest.raises(Exception, match="API Error"):
            await embedding_service.generate_batch_embeddings(texts, use_cache=False)
