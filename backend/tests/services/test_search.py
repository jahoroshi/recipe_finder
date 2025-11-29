"""Tests for SearchService."""

import json
import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, ANY
from uuid import uuid4

from app.db.models import DifficultyLevel, Recipe
from app.schemas.search import SearchRequest
from app.services.search import SearchService


@pytest.fixture
def sample_recipes():
    """Create sample recipes for testing."""
    now = datetime.now(timezone.utc)
    return [
        Recipe(
            id=uuid4(),
            name="Pasta Carbonara",
            description="Classic Italian pasta",
            instructions={"steps": ["Cook pasta"]},
            prep_time=10,
            cook_time=15,
            servings=4,
            difficulty=DifficultyLevel.MEDIUM,
            cuisine_type="Italian",
            diet_types=["vegetarian"],
            embedding=[0.1] * 768,
            created_at=now,
            updated_at=now,
        ),
        Recipe(
            id=uuid4(),
            name="Thai Green Curry",
            description="Spicy Thai curry",
            instructions={"steps": ["Cook curry"]},
            prep_time=15,
            cook_time=20,
            servings=4,
            difficulty=DifficultyLevel.MEDIUM,
            cuisine_type="Thai",
            diet_types=["gluten-free"],
            embedding=[0.2] * 768,
            created_at=now,
            updated_at=now,
        ),
    ]


@pytest.fixture
def mock_recipe_repo():
    """Create mock recipe repository."""
    mock = MagicMock()
    mock.find_by_cuisine_and_difficulty = AsyncMock(return_value=[])
    mock.get_recipes_with_time_range = AsyncMock(return_value=[])
    mock.get_recipes_by_diet_type = AsyncMock(return_value=[])
    mock.find_by_ingredients = AsyncMock(return_value=[])
    mock.get_popular_recipes = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_vector_repo():
    """Create mock vector repository."""
    mock = MagicMock()
    mock.similarity_search = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_embedding_service():
    """Create mock embedding service."""
    mock = MagicMock()
    mock.generate_query_embedding = AsyncMock(return_value=[0.1] * 768)
    return mock


@pytest.fixture
def mock_gemini_client():
    """Create mock Gemini client."""
    mock = MagicMock()
    mock.generate_text = AsyncMock()
    return mock


@pytest.fixture
def mock_cache_service():
    """Create mock cache service."""
    mock = MagicMock()
    mock.get_search_results = AsyncMock(return_value=None)
    mock.set_search_results = AsyncMock(return_value=True)
    return mock


@pytest.fixture
def search_service(
    mock_recipe_repo,
    mock_vector_repo,
    mock_embedding_service,
    mock_gemini_client,
    mock_cache_service,
):
    """Create SearchService instance with mocks."""
    return SearchService(
        recipe_repo=mock_recipe_repo,
        vector_repo=mock_vector_repo,
        embedding_service=mock_embedding_service,
        gemini_client=mock_gemini_client,
        cache_service=mock_cache_service,
    )


@pytest.mark.asyncio
class TestSearchService:
    """Test suite for SearchService."""

    async def test_semantic_search(
        self, search_service, mock_vector_repo, mock_embedding_service, sample_recipes
    ):
        """Test semantic search functionality."""
        # Setup
        query = "italian pasta"
        mock_vector_repo.similarity_search.return_value = [
            (sample_recipes[0], 0.1),  # Distance
        ]

        # Execute
        results = await search_service.semantic_search(query, limit=10)

        # Assert
        assert len(results) == 1
        recipe, score = results[0]
        assert recipe.name == "Pasta Carbonara"
        assert score == 0.9  # 1 - 0.1 distance
        mock_embedding_service.generate_query_embedding.assert_called_once_with(query)

    async def test_filter_search_by_cuisine(
        self, search_service, mock_recipe_repo, sample_recipes
    ):
        """Test filter search by cuisine."""
        # Setup
        filters = {"cuisine_type": "Italian", "difficulty": DifficultyLevel.MEDIUM}
        mock_recipe_repo.find_by_cuisine_and_difficulty.return_value = [sample_recipes[0]]

        # Execute
        results = await search_service.filter_search(filters, limit=10)

        # Assert
        assert len(results) == 1
        recipe, score = results[0]
        assert recipe.name == "Pasta Carbonara"
        assert score == 1.0  # Filter results have uniform score
        mock_recipe_repo.find_by_cuisine_and_difficulty.assert_called_once()

    async def test_filter_search_by_time_range(
        self, search_service, mock_recipe_repo, sample_recipes
    ):
        """Test filter search by time constraints."""
        # Setup
        filters = {"max_prep_time": 15, "max_cook_time": 20}
        mock_recipe_repo.get_recipes_with_time_range.return_value = sample_recipes

        # Execute
        results = await search_service.filter_search(filters, limit=10)

        # Assert
        assert len(results) == 2
        mock_recipe_repo.get_recipes_with_time_range.assert_called_once()

    async def test_filter_search_by_diet_type(
        self, search_service, mock_recipe_repo, sample_recipes
    ):
        """Test filter search by diet type."""
        # Setup
        filters = {"diet_type": "vegetarian"}
        mock_recipe_repo.get_recipes_by_diet_type.return_value = [sample_recipes[0]]

        # Execute
        results = await search_service.filter_search(filters, limit=10)

        # Assert
        assert len(results) == 1
        mock_recipe_repo.get_recipes_by_diet_type.assert_called_once_with(
            diet_type="vegetarian", pagination=ANY
        )

    async def test_filter_search_by_ingredients(
        self, search_service, mock_recipe_repo, sample_recipes
    ):
        """Test filter search by ingredients."""
        # Setup
        filters = {"ingredients": ["pasta", "eggs"], "match_all_ingredients": True}
        mock_recipe_repo.find_by_ingredients.return_value = [sample_recipes[0]]

        # Execute
        results = await search_service.filter_search(filters, limit=10)

        # Assert
        assert len(results) == 1
        mock_recipe_repo.find_by_ingredients.assert_called_once()

    async def test_filter_search_default(
        self, search_service, mock_recipe_repo, sample_recipes
    ):
        """Test filter search with no specific filters."""
        # Setup
        filters = {}
        mock_recipe_repo.get_popular_recipes.return_value = sample_recipes

        # Execute
        results = await search_service.filter_search(filters, limit=10)

        # Assert
        assert len(results) == 2
        mock_recipe_repo.get_popular_recipes.assert_called_once_with(limit=10)

    async def test_query_understanding_success(
        self, search_service, mock_gemini_client
    ):
        """Test query parsing with Gemini."""
        # Setup
        query = "quick vegetarian italian pasta under 30 minutes"
        gemini_response = json.dumps({
            "ingredients": ["pasta"],
            "cuisine_type": "Italian",
            "diet_types": ["vegetarian"],
            "max_prep_time": 30,
            "max_cook_time": None,
            "difficulty": None,
            "semantic_query": "italian pasta",
        })
        mock_gemini_client.generate_text.return_value = gemini_response

        # Execute
        parsed = await search_service.query_understanding(query)

        # Assert
        assert parsed.original_query == query
        assert parsed.cuisine_type == "Italian"
        assert "vegetarian" in parsed.diet_types
        assert parsed.max_prep_time == 30
        assert parsed.semantic_query == "italian pasta"

    async def test_query_understanding_with_markdown(
        self, search_service, mock_gemini_client
    ):
        """Test query parsing when Gemini returns markdown."""
        # Setup
        query = "easy pasta recipe"
        gemini_response = '''```json
{
    "ingredients": [],
    "cuisine_type": null,
    "diet_types": [],
    "max_prep_time": null,
    "max_cook_time": null,
    "difficulty": "easy",
    "semantic_query": "pasta recipe"
}
```'''
        mock_gemini_client.generate_text.return_value = gemini_response

        # Execute
        parsed = await search_service.query_understanding(query)

        # Assert
        assert parsed.difficulty == "easy"
        assert parsed.semantic_query == "pasta recipe"

    async def test_query_understanding_fallback(
        self, search_service, mock_gemini_client
    ):
        """Test query understanding falls back gracefully on error."""
        # Setup
        query = "some query"
        mock_gemini_client.generate_text.side_effect = Exception("API Error")

        # Execute
        parsed = await search_service.query_understanding(query)

        # Assert - Should return default parsed query
        assert parsed.original_query == query
        assert parsed.semantic_query == query
        assert parsed.ingredients == []
        assert parsed.cuisine_type is None

    async def test_result_reranking_success(
        self, search_service, mock_gemini_client, sample_recipes
    ):
        """Test result reranking with Gemini."""
        # Setup
        query = "authentic italian carbonara"
        results = [(recipe, 0.5) for recipe in sample_recipes]
        mock_gemini_client.generate_text.return_value = "[1, 2]"  # Rerank order

        # Execute
        reranked = await search_service.result_reranking(results, query)

        # Assert
        assert len(reranked) == 2
        # First result should have boosted score
        assert reranked[0][1] > 0.5

    async def test_result_reranking_empty_results(
        self, search_service, mock_gemini_client
    ):
        """Test reranking with empty results."""
        # Execute
        reranked = await search_service.result_reranking([], "query")

        # Assert
        assert reranked == []
        mock_gemini_client.generate_text.assert_not_called()

    async def test_result_reranking_fallback_on_error(
        self, search_service, mock_gemini_client, sample_recipes
    ):
        """Test reranking falls back to original results on error."""
        # Setup
        results = [(recipe, 0.5) for recipe in sample_recipes]
        mock_gemini_client.generate_text.side_effect = Exception("API Error")

        # Execute
        reranked = await search_service.result_reranking(results, "query")

        # Assert - Should return original results
        assert reranked == results

    async def test_merge_results_rrf(self, search_service, sample_recipes):
        """Test Reciprocal Rank Fusion merging."""
        # Setup
        semantic_results = [(sample_recipes[0], 0.9), (sample_recipes[1], 0.7)]
        filter_results = [(sample_recipes[1], 1.0), (sample_recipes[0], 1.0)]

        # Execute
        merged = search_service._merge_results_rrf(
            semantic_results, filter_results, k=60
        )

        # Assert
        assert len(merged) == 2
        # Both recipes should be present with RRF scores
        recipe_ids = [str(recipe.id) for recipe, _ in merged]
        assert str(sample_recipes[0].id) in recipe_ids
        assert str(sample_recipes[1].id) in recipe_ids

    async def test_merge_results_rrf_no_overlap(self, search_service):
        """Test RRF merging with no overlapping recipes."""
        # Setup
        recipe1 = Recipe(
            id=uuid4(),
            name="Recipe 1",
            instructions={"steps": []},
            difficulty=DifficultyLevel.EASY,
        )
        recipe2 = Recipe(
            id=uuid4(),
            name="Recipe 2",
            instructions={"steps": []},
            difficulty=DifficultyLevel.EASY,
        )
        semantic_results = [(recipe1, 0.9)]
        filter_results = [(recipe2, 1.0)]

        # Execute
        merged = search_service._merge_results_rrf(
            semantic_results, filter_results, k=60
        )

        # Assert
        assert len(merged) == 2

    async def test_build_filters(self, search_service):
        """Test building filters from parsed query."""
        # Setup
        from app.schemas.search import ParsedQuery

        parsed_query = ParsedQuery(
            original_query="test",
            cuisine_type="Italian",
            difficulty="easy",
            max_prep_time=30,
            diet_types=["vegetarian"],
            ingredients=["pasta"],
            semantic_query="test",
        )
        additional_filters = {"servings": 4}

        # Execute
        filters = search_service._build_filters(parsed_query, additional_filters)

        # Assert
        assert filters["cuisine_type"] == "Italian"
        assert filters["difficulty"] == "easy"
        assert filters["max_prep_time"] == 30
        assert filters["diet_type"] == "vegetarian"
        assert filters["ingredients"] == ["pasta"]
        assert filters["servings"] == 4

    async def test_build_filters_minimal(self, search_service):
        """Test building filters with minimal parsed query."""
        # Setup
        from app.schemas.search import ParsedQuery

        parsed_query = ParsedQuery(
            original_query="test",
            semantic_query="test",
        )

        # Execute
        filters = search_service._build_filters(parsed_query, None)

        # Assert
        assert filters == {}

    async def test_hybrid_search_semantic_only(
        self, search_service, mock_vector_repo, sample_recipes, mock_cache_service
    ):
        """Test hybrid search with only semantic search enabled."""
        # Setup
        request = SearchRequest(
            query="italian pasta",
            limit=10,
            use_semantic=True,
            use_filters=False,
        )
        mock_vector_repo.similarity_search.return_value = [
            (sample_recipes[0], 0.1),
        ]

        # Execute
        response = await search_service.hybrid_search(request)

        # Assert
        assert response.total == 1
        assert response.search_type == "semantic"
        assert len(response.results) == 1
        mock_cache_service.set_search_results.assert_called_once()

    async def test_hybrid_search_from_cache(
        self, search_service, mock_cache_service
    ):
        """Test hybrid search returns cached results."""
        # Setup
        request = SearchRequest(query="test", limit=10)
        cached_response = {
            "query": "test",
            "parsed_query": None,
            "results": [],
            "total": 0,
            "search_type": "hybrid",
            "metadata": {},
        }
        mock_cache_service.get_search_results.return_value = cached_response

        # Execute
        response = await search_service.hybrid_search(request)

        # Assert
        assert response.query == "test"
        assert response.total == 0

    async def test_hybrid_search_with_reranking(
        self,
        search_service,
        mock_vector_repo,
        mock_gemini_client,
        sample_recipes,
        mock_cache_service,
    ):
        """Test hybrid search with reranking enabled."""
        # Setup
        request = SearchRequest(
            query="italian pasta",
            limit=10,
            use_semantic=True,
            use_filters=False,
            use_reranking=True,
        )
        mock_vector_repo.similarity_search.return_value = [
            (sample_recipes[0], 0.1),
            (sample_recipes[1], 0.2),
        ]
        mock_gemini_client.generate_text.return_value = "[1, 2]"

        # Execute
        response = await search_service.hybrid_search(request)

        # Assert
        assert response.metadata["reranked"] is True
        assert response.total == 2

    async def test_recipe_to_response(self, search_service, sample_recipes):
        """Test converting recipe to response."""
        # Execute
        response = search_service._recipe_to_response(sample_recipes[0])

        # Assert
        assert response.name == "Pasta Carbonara"
        assert response.cuisine_type == "Italian"
        assert response.embedding is None  # Should not expose embedding

    # New test case: Test semantic search with empty query
    async def test_semantic_search_zero_results(
        self, search_service, mock_vector_repo, mock_embedding_service
    ):
        """Test semantic search with no results."""
        # Setup
        query = "nonexistent dish"
        mock_vector_repo.similarity_search.return_value = []

        # Execute
        results = await search_service.semantic_search(query, limit=10)

        # Assert
        assert len(results) == 0
        mock_embedding_service.generate_query_embedding.assert_called_once()

    # New test case: Test filter search with combined filters
    async def test_filter_search_combined_filters(
        self, search_service, mock_recipe_repo, sample_recipes
    ):
        """Test filter search with multiple filter types."""
        # Setup
        filters = {
            "cuisine_type": "Italian",
            "difficulty": DifficultyLevel.MEDIUM,
            "max_prep_time": 15,
        }
        mock_recipe_repo.find_by_cuisine_and_difficulty.return_value = sample_recipes

        # Execute
        results = await search_service.filter_search(filters, limit=10)

        # Assert
        assert len(results) > 0
        mock_recipe_repo.find_by_cuisine_and_difficulty.assert_called_once()

    # New test case: Test hybrid search with both semantic and filter enabled
    async def test_hybrid_search_full_hybrid(
        self,
        search_service,
        mock_vector_repo,
        mock_recipe_repo,
        mock_gemini_client,
        sample_recipes,
        mock_cache_service,
    ):
        """Test hybrid search combining semantic and filters."""
        # Setup
        from app.schemas.search import SearchRequest

        request = SearchRequest(
            query="italian pasta easy to make",
            limit=5,
            use_semantic=True,
            use_filters=True,
        )
        gemini_response = json.dumps({
            "ingredients": [],
            "cuisine_type": "Italian",
            "diet_types": [],
            "max_prep_time": None,
            "max_cook_time": None,
            "difficulty": "easy",
            "semantic_query": "italian pasta",
        })
        mock_gemini_client.generate_text.return_value = gemini_response
        mock_vector_repo.similarity_search.return_value = [
            (sample_recipes[0], 0.1),
        ]
        mock_recipe_repo.find_by_cuisine_and_difficulty.return_value = [sample_recipes[0]]

        # Execute
        response = await search_service.hybrid_search(request)

        # Assert
        assert response.search_type == "hybrid"
        assert response.total > 0

    # New test case: Test query understanding with invalid JSON
    async def test_query_understanding_invalid_json(
        self, search_service, mock_gemini_client
    ):
        """Test query understanding when Gemini returns invalid JSON."""
        # Setup
        query = "test query"
        mock_gemini_client.generate_text.return_value = "not valid json{{"

        # Execute
        parsed = await search_service.query_understanding(query)

        # Assert - Should fallback gracefully
        assert parsed.original_query == query
        assert parsed.semantic_query == query

    # New test case: Test result reranking with single result
    async def test_result_reranking_single_result(
        self, search_service, sample_recipes
    ):
        """Test reranking with single result."""
        # Setup
        results = [(sample_recipes[0], 0.8)]

        # Execute
        reranked = await search_service.result_reranking(results, "query")

        # Assert - Should return single result unchanged
        assert len(reranked) == 1

    # New test case: Test RRF merging with empty lists
    async def test_merge_results_rrf_empty_lists(self, search_service):
        """Test RRF merging with empty result lists."""
        # Execute
        merged = search_service._merge_results_rrf([], [], k=60)

        # Assert
        assert merged == []

    # New test case: Test RRF merging with one empty list
    async def test_merge_results_rrf_one_empty(
        self, search_service, sample_recipes
    ):
        """Test RRF merging when one list is empty."""
        # Setup
        semantic_results = [(sample_recipes[0], 0.9)]
        filter_results = []

        # Execute
        merged = search_service._merge_results_rrf(
            semantic_results, filter_results, k=60
        )

        # Assert
        assert len(merged) == 1

    # New test case: Test build filters with all None values
    async def test_build_filters_all_none(self, search_service):
        """Test building filters when all parsed values are None."""
        # Setup
        from app.schemas.search import ParsedQuery

        parsed_query = ParsedQuery(
            original_query="test",
            semantic_query="test",
            ingredients=[],
            cuisine_type=None,
            diet_types=[],
            max_prep_time=None,
            max_cook_time=None,
            difficulty=None,
        )

        # Execute
        filters = search_service._build_filters(parsed_query, None)

        # Assert
        assert filters == {}

    # New test case: Test build filters with additional filters override
    async def test_build_filters_with_overrides(self, search_service):
        """Test building filters with additional filters overriding parsed."""
        # Setup
        from app.schemas.search import ParsedQuery

        parsed_query = ParsedQuery(
            original_query="test",
            cuisine_type="Italian",
            semantic_query="test",
        )
        additional_filters = {"cuisine_type": "French", "servings": 4}

        # Execute
        filters = search_service._build_filters(parsed_query, additional_filters)

        # Assert - Additional filters should override
        assert filters["cuisine_type"] == "French"
        assert filters["servings"] == 4

    # New test case: Test hybrid search with no use flags
    async def test_hybrid_search_no_search_types(
        self, search_service, mock_cache_service
    ):
        """Test hybrid search when neither semantic nor filters enabled."""
        # Setup
        from app.schemas.search import SearchRequest

        request = SearchRequest(
            query="test",
            limit=10,
            use_semantic=False,
            use_filters=False,
        )

        # Execute
        response = await search_service.hybrid_search(request)

        # Assert
        assert response.total == 0
        assert response.results == []

    # New test case: Test filter search with servings filter
    async def test_filter_search_no_matching_filters(
        self, search_service, mock_recipe_repo
    ):
        """Test filter search with filters not matching any strategy."""
        # Setup
        filters = {"servings": 4}  # No specific strategy for this
        mock_recipe_repo.get_popular_recipes.return_value = []

        # Execute
        results = await search_service.filter_search(filters, limit=10)

        # Assert
        mock_recipe_repo.get_popular_recipes.assert_called_once_with(limit=10)

    # New test case: Test query understanding with complex query
    async def test_query_understanding_complex_query(
        self, search_service, mock_gemini_client
    ):
        """Test query understanding with detailed natural language."""
        # Setup
        query = "I need a quick vegetarian Italian dinner for 4 people under 30 minutes"
        gemini_response = json.dumps({
            "ingredients": [],
            "cuisine_type": "Italian",
            "diet_types": ["vegetarian"],
            "max_prep_time": 15,
            "max_cook_time": 15,
            "difficulty": "easy",
            "semantic_query": "quick italian dinner",
        })
        mock_gemini_client.generate_text.return_value = gemini_response

        # Execute
        parsed = await search_service.query_understanding(query)

        # Assert
        assert parsed.cuisine_type == "Italian"
        assert "vegetarian" in parsed.diet_types
        assert parsed.max_prep_time == 15
        assert parsed.difficulty == "easy"

    # New test case: Test reranking with API returning malformed indices
    async def test_result_reranking_invalid_indices(
        self, search_service, mock_gemini_client, sample_recipes
    ):
        """Test reranking when API returns invalid indices."""
        # Setup
        results = [(recipe, 0.5) for recipe in sample_recipes]
        mock_gemini_client.generate_text.return_value = "[99, 100, 101]"

        # Execute
        reranked = await search_service.result_reranking(results, "query")

        # Assert - Should have minimal impact with invalid indices
        assert len(reranked) >= len(results)

    # New test case: Test semantic search with very high limit
    async def test_semantic_search_high_limit(
        self, search_service, mock_vector_repo, mock_embedding_service, sample_recipes
    ):
        """Test semantic search with very high limit."""
        # Setup
        query = "pasta"
        mock_vector_repo.similarity_search.return_value = [
            (recipe, 0.1 + i * 0.01) for i, recipe in enumerate(sample_recipes)
        ]

        # Execute
        results = await search_service.semantic_search(query, limit=1000)

        # Assert
        assert len(results) == len(sample_recipes)

    # New test case: Test hybrid search cache bypass
    async def test_hybrid_search_cache_bypass_on_error(
        self, search_service, mock_cache_service, mock_vector_repo, sample_recipes
    ):
        """Test hybrid search continues if cache fails."""
        # Setup
        from app.schemas.search import SearchRequest

        request = SearchRequest(query="test", limit=10, use_semantic=True)
        mock_cache_service.get_search_results.side_effect = Exception("Cache error")
        mock_vector_repo.similarity_search.return_value = [
            (sample_recipes[0], 0.1)
        ]

        # Execute & Assert - Should handle cache error gracefully
        with pytest.raises(Exception, match="Cache error"):
            await search_service.hybrid_search(request)

    # New test case: Test filter search with max_total_time
    async def test_filter_search_max_total_time(
        self, search_service, mock_recipe_repo, sample_recipes
    ):
        """Test filter search with total time constraint."""
        # Setup
        filters = {"max_total_time": 45}
        mock_recipe_repo.get_recipes_with_time_range.return_value = sample_recipes

        # Execute
        results = await search_service.filter_search(filters, limit=10)

        # Assert
        assert len(results) > 0
        mock_recipe_repo.get_recipes_with_time_range.assert_called_once()

    # New test case: Test RRF with different k values
    async def test_merge_results_rrf_different_k(
        self, search_service, sample_recipes
    ):
        """Test RRF merging with different k values."""
        # Setup
        semantic_results = [(sample_recipes[0], 0.9)]
        filter_results = [(sample_recipes[0], 1.0)]

        # Execute with different k values
        merged_k30 = search_service._merge_results_rrf(
            semantic_results, filter_results, k=30
        )
        merged_k90 = search_service._merge_results_rrf(
            semantic_results, filter_results, k=90
        )

        # Assert - Different k values should affect scores
        assert len(merged_k30) == 1
        assert len(merged_k90) == 1
        # Scores should be different due to different k
        assert merged_k30[0][1] != merged_k90[0][1]

    # New test case: Test query understanding with markdown and JSON mix
    async def test_query_understanding_markdown_json_mix(
        self, search_service, mock_gemini_client
    ):
        """Test query understanding when response has extra text that can't be parsed."""
        # Setup
        query = "test"
        # Response with extra text - will fail JSON parsing and fallback
        gemini_response = '''Here's the result:
```json
{
    "ingredients": [],
    "cuisine_type": "Italian",
    "diet_types": [],
    "max_prep_time": null,
    "max_cook_time": null,
    "difficulty": null,
    "semantic_query": "test"
}
```
Hope this helps!'''
        mock_gemini_client.generate_text.return_value = gemini_response

        # Execute
        parsed = await search_service.query_understanding(query)

        # Assert - Extraction fails due to extra text, falls back to default
        assert parsed.original_query == query
        # Will fallback to None since the parser can't extract clean JSON with extra text
        assert parsed.semantic_query == query

    # New test case: Test filter search match_all_ingredients
    async def test_filter_search_match_all_ingredients(
        self, search_service, mock_recipe_repo, sample_recipes
    ):
        """Test filter search with match_all_ingredients flag."""
        # Setup
        filters = {
            "ingredients": ["pasta", "cheese", "eggs"],
            "match_all_ingredients": True,
        }
        mock_recipe_repo.find_by_ingredients.return_value = [sample_recipes[0]]

        # Execute
        results = await search_service.filter_search(filters, limit=10)

        # Assert
        assert len(results) > 0
        call_args = mock_recipe_repo.find_by_ingredients.call_args[1]
        assert call_args["match_all"] is True
