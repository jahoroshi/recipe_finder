"""Fixtures for workflow tests."""

from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from app.db.models import Recipe, DifficultyLevel
from app.workflows.states import JudgeConfig


@pytest.fixture
def mock_gemini_client():
    """Create mock Gemini client."""
    client = Mock()
    client.generate_text = AsyncMock(return_value='{"ingredients": [], "cuisine_type": "Italian", "diet_types": [], "max_prep_time": null, "max_cook_time": null, "difficulty": null, "semantic_query": "pasta"}')
    client.generate_embedding = AsyncMock(return_value=[0.1] * 768)
    client.embedding_model = "gemini-embedding-001"
    return client


@pytest.fixture
def mock_recipe_repo():
    """Create mock recipe repository."""
    repo = Mock()
    repo.find_by_cuisine_and_difficulty = AsyncMock(return_value=[])
    repo.get_recipes_with_time_range = AsyncMock(return_value=[])
    repo.get_recipes_by_diet_type = AsyncMock(return_value=[])
    repo.find_by_ingredients = AsyncMock(return_value=[])
    repo.get_popular_recipes = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_vector_repo():
    """Create mock vector repository."""
    repo = Mock()
    repo.similarity_search = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_cache_service():
    """Create mock cache service."""
    cache = Mock()
    cache.get_search_results = AsyncMock(return_value=None)
    cache.set_search_results = AsyncMock(return_value=None)
    cache.get_embedding = AsyncMock(return_value=None)
    cache.set_embedding = AsyncMock(return_value=None)
    return cache


@pytest.fixture
def mock_embedding_service(mock_gemini_client, mock_cache_service):
    """Create mock embedding service."""
    from app.services.embedding import EmbeddingService

    service = EmbeddingService(
        gemini_client=mock_gemini_client,
        cache_service=mock_cache_service,
    )
    return service


@pytest.fixture
def mock_search_service(
    mock_recipe_repo,
    mock_vector_repo,
    mock_embedding_service,
    mock_gemini_client,
    mock_cache_service,
):
    """Create mock search service."""
    from app.services.search import SearchService

    service = SearchService(
        recipe_repo=mock_recipe_repo,
        vector_repo=mock_vector_repo,
        embedding_service=mock_embedding_service,
        gemini_client=mock_gemini_client,
        cache_service=mock_cache_service,
    )
    return service


@pytest.fixture
def sample_recipes():
    """Create sample recipe fixtures."""
    recipes = []

    # Italian pasta recipe
    recipe1 = Recipe(
        id=uuid4(),
        name="Spaghetti Carbonara",
        description="Classic Italian pasta with eggs and bacon",
        instructions={"steps": ["Cook pasta", "Mix eggs", "Combine"]},
        prep_time=10,
        cook_time=20,
        servings=4,
        difficulty=DifficultyLevel.EASY,
        cuisine_type="Italian",
        diet_types=[],
        embedding=[0.2] * 768,
    )
    recipes.append(recipe1)

    # Vegetarian recipe
    recipe2 = Recipe(
        id=uuid4(),
        name="Vegetable Stir Fry",
        description="Quick and healthy vegetarian dish",
        instructions={"steps": ["Cut vegetables", "Stir fry"]},
        prep_time=15,
        cook_time=10,
        servings=2,
        difficulty=DifficultyLevel.EASY,
        cuisine_type="Asian",
        diet_types=["vegetarian", "vegan"],
        embedding=[0.3] * 768,
    )
    recipes.append(recipe2)

    # Complex recipe
    recipe3 = Recipe(
        id=uuid4(),
        name="Beef Wellington",
        description="Sophisticated British dish",
        instructions={"steps": ["Prepare beef", "Make pastry", "Bake"]},
        prep_time=60,
        cook_time=45,
        servings=6,
        difficulty=DifficultyLevel.HARD,
        cuisine_type="British",
        diet_types=[],
        embedding=[0.4] * 768,
    )
    recipes.append(recipe3)

    # Quick recipe
    recipe4 = Recipe(
        id=uuid4(),
        name="Caesar Salad",
        description="Fresh and quick salad",
        instructions={"steps": ["Chop lettuce", "Make dressing", "Toss"]},
        prep_time=10,
        cook_time=0,
        servings=2,
        difficulty=DifficultyLevel.EASY,
        cuisine_type="American",
        diet_types=["vegetarian"],
        embedding=[0.5] * 768,
    )
    recipes.append(recipe4)

    # Gluten-free recipe
    recipe5 = Recipe(
        id=uuid4(),
        name="Quinoa Bowl",
        description="Healthy gluten-free bowl",
        instructions={"steps": ["Cook quinoa", "Add toppings"]},
        prep_time=5,
        cook_time=15,
        servings=1,
        difficulty=DifficultyLevel.EASY,
        cuisine_type="Modern",
        diet_types=["vegetarian", "vegan", "gluten-free"],
        embedding=[0.6] * 768,
    )
    recipes.append(recipe5)

    return recipes


@pytest.fixture
def default_judge_config():
    """Create default judge configuration."""
    return JudgeConfig(
        semantic_threshold=0.0,
        filter_compliance_min=0.0,
        ingredient_match_min=0.0,
        dietary_strict_mode=False,
        confidence_threshold=0.0,
        min_results=0,
        max_results=100,
    )


@pytest.fixture
def strict_judge_config():
    """Create strict judge configuration."""
    return JudgeConfig(
        semantic_threshold=0.7,
        filter_compliance_min=0.8,
        ingredient_match_min=0.5,
        dietary_strict_mode=True,
        confidence_threshold=0.6,
        min_results=1,
        max_results=10,
    )
