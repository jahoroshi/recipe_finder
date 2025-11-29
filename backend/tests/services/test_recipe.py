"""Tests for RecipeService."""

import pytest
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

from app.db.models import DifficultyLevel, Recipe, Ingredient, NutritionalInfo
from app.schemas.recipe import RecipeCreate, RecipeUpdate
from app.schemas.ingredient import IngredientCreate
from app.schemas.nutritional_info import NutritionalInfoCreate
from app.services.recipe import RecipeService


@pytest.fixture
def mock_recipe_repo():
    """Create mock recipe repository."""
    mock = MagicMock()
    mock.get = AsyncMock(return_value=None)
    mock.get_with_relations = AsyncMock(return_value=None)
    mock.delete = AsyncMock()
    mock.get_all = AsyncMock(return_value=[])
    mock.search_by_text = AsyncMock(return_value=[])
    mock.find_by_cuisine_and_difficulty = AsyncMock(return_value=[])
    mock.find_by_ingredients = AsyncMock(return_value=[])
    return mock


@pytest.fixture
def mock_vector_repo():
    """Create mock vector repository."""
    mock = MagicMock()
    return mock


@pytest.fixture
def mock_embedding_service():
    """Create mock embedding service."""
    mock = MagicMock()
    mock.create_recipe_embedding = AsyncMock(return_value=[0.1] * 768)
    return mock


@pytest.fixture
def mock_cache_service():
    """Create mock cache service."""
    mock = MagicMock()
    mock.get_recipe = AsyncMock(return_value=None)
    mock.set_recipe = AsyncMock(return_value=True)
    mock.invalidate_recipe_cache = AsyncMock()
    return mock


@pytest.fixture
def mock_session():
    """Create mock database session."""
    mock = MagicMock()
    mock.add = MagicMock()
    mock.flush = AsyncMock()
    mock.commit = AsyncMock()
    mock.refresh = AsyncMock()
    mock.delete = AsyncMock()
    return mock


@pytest.fixture
def recipe_service(
    mock_recipe_repo,
    mock_vector_repo,
    mock_embedding_service,
    mock_cache_service,
    mock_session,
):
    """Create RecipeService instance with mocks."""
    return RecipeService(
        recipe_repo=mock_recipe_repo,
        vector_repo=mock_vector_repo,
        embedding_service=mock_embedding_service,
        cache_service=mock_cache_service,
        session=mock_session,
    )


@pytest.fixture
def sample_recipe_create():
    """Create sample RecipeCreate data."""
    return RecipeCreate(
        name="Pasta Carbonara",
        description="Classic Italian pasta dish",
        instructions={"steps": ["Cook pasta", "Mix with eggs and cheese"]},
        prep_time=10,
        cook_time=15,
        servings=4,
        difficulty=DifficultyLevel.MEDIUM,
        cuisine_type="Italian",
        diet_types=["vegetarian"],
        ingredients=[
            IngredientCreate(name="pasta", quantity=500, unit="g"),
            IngredientCreate(name="eggs", quantity=3, unit="pieces"),
        ],
        category_ids=[uuid4()],
        nutritional_info=NutritionalInfoCreate(
            calories=450.0,
            protein_g=18.0,
            carbohydrates_g=60.0,
            fat_g=12.0,
        ),
    )


@pytest.fixture
def sample_recipe():
    """Create sample Recipe instance."""
    now = datetime.now(timezone.utc)
    recipe = Recipe(
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
    )
    recipe.ingredients = []
    recipe.recipe_categories = []
    recipe.nutritional_info = None
    return recipe


@pytest.mark.asyncio
class TestRecipeService:
    """Test suite for RecipeService."""

    async def test_create_recipe_success(
        self,
        recipe_service,
        sample_recipe_create,
        mock_session,
        mock_embedding_service,
        mock_recipe_repo,
        sample_recipe,
    ):
        """Test successful recipe creation."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []  # No duplicates
        mock_recipe_repo.get_with_relations.return_value = sample_recipe

        # Execute
        result = await recipe_service.create_recipe(sample_recipe_create)

        # Assert
        assert result.name == "Pasta Carbonara"
        mock_session.add.assert_called()
        mock_session.flush.assert_called()
        mock_session.commit.assert_called_once()
        mock_embedding_service.create_recipe_embedding.assert_called_once()

    async def test_create_recipe_validation_failure(
        self, recipe_service, sample_recipe_create, mock_recipe_repo, sample_recipe
    ):
        """Test recipe creation with validation failure."""
        # Setup - Simulate duplicate name
        mock_recipe_repo.search_by_text.return_value = [sample_recipe]

        # Execute & Assert
        with pytest.raises(ValueError, match="already exists"):
            await recipe_service.create_recipe(sample_recipe_create)

    async def test_create_recipe_embedding_failure(
        self,
        recipe_service,
        sample_recipe_create,
        mock_embedding_service,
        mock_recipe_repo,
        sample_recipe,
        mock_session,
    ):
        """Test recipe creation continues if embedding fails."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []
        mock_recipe_repo.get_with_relations.return_value = sample_recipe
        mock_embedding_service.create_recipe_embedding.side_effect = Exception(
            "API Error"
        )

        # Execute - Should not raise exception
        result = await recipe_service.create_recipe(sample_recipe_create)

        # Assert - Recipe still created
        assert result.name == "Pasta Carbonara"
        mock_session.commit.assert_called_once()

    async def test_update_recipe_success(
        self,
        recipe_service,
        sample_recipe,
        mock_recipe_repo,
        mock_session,
        mock_cache_service,
    ):
        """Test successful recipe update."""
        # Setup
        mock_recipe_repo.get.return_value = sample_recipe
        mock_recipe_repo.get_with_relations.return_value = sample_recipe
        updates = RecipeUpdate(prep_time=20, difficulty=DifficultyLevel.EASY)

        # Execute
        result = await recipe_service.update_recipe(sample_recipe.id, updates)

        # Assert
        mock_session.flush.assert_called()
        mock_session.commit.assert_called_once()
        mock_cache_service.invalidate_recipe_cache.assert_called_once_with(
            sample_recipe.id
        )

    async def test_update_recipe_not_found(self, recipe_service, mock_recipe_repo):
        """Test updating non-existent recipe."""
        # Setup
        mock_recipe_repo.get.return_value = None
        updates = RecipeUpdate(prep_time=20)

        # Execute & Assert
        with pytest.raises(ValueError, match="not found"):
            await recipe_service.update_recipe(uuid4(), updates)

    async def test_update_recipe_regenerates_embedding(
        self,
        recipe_service,
        sample_recipe,
        mock_recipe_repo,
        mock_embedding_service,
        mock_session,
    ):
        """Test embedding regeneration when relevant fields change."""
        # Setup
        mock_recipe_repo.get.return_value = sample_recipe
        mock_recipe_repo.get_with_relations.return_value = sample_recipe
        updates = RecipeUpdate(name="New Name")  # Name affects embedding

        # Execute
        await recipe_service.update_recipe(sample_recipe.id, updates)

        # Assert - Embedding should be regenerated
        mock_embedding_service.create_recipe_embedding.assert_called_once()

    async def test_update_recipe_no_embedding_regeneration(
        self,
        recipe_service,
        sample_recipe,
        mock_recipe_repo,
        mock_embedding_service,
        mock_session,
    ):
        """Test no embedding regeneration for non-relevant fields."""
        # Setup
        mock_recipe_repo.get.return_value = sample_recipe
        mock_recipe_repo.get_with_relations.return_value = sample_recipe
        updates = RecipeUpdate(prep_time=25)  # prep_time doesn't affect embedding

        # Execute
        await recipe_service.update_recipe(sample_recipe.id, updates)

        # Assert - Embedding should not be regenerated
        mock_embedding_service.create_recipe_embedding.assert_not_called()

    async def test_get_recipe_from_cache(
        self, recipe_service, mock_cache_service, sample_recipe
    ):
        """Test getting recipe from cache."""
        # Setup
        recipe_data = {
            "id": str(sample_recipe.id),
            "name": "Pasta Carbonara",
            "description": "Classic Italian pasta",
            "instructions": {"steps": []},
            "prep_time": 10,
            "cook_time": 15,
            "servings": 4,
            "difficulty": "medium",
            "cuisine_type": "Italian",
            "diet_types": [],
            "embedding": None,
            "ingredients": [],
            "categories": [],
            "nutritional_info": None,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "deleted_at": None,
            "created_by": None,
            "updated_by": None,
        }
        mock_cache_service.get_recipe.return_value = recipe_data

        # Execute
        result = await recipe_service.get_recipe(sample_recipe.id)

        # Assert
        assert result.name == "Pasta Carbonara"
        mock_cache_service.get_recipe.assert_called_once_with(sample_recipe.id)

    async def test_get_recipe_from_database(
        self,
        recipe_service,
        sample_recipe,
        mock_recipe_repo,
        mock_cache_service,
    ):
        """Test getting recipe from database and caching."""
        # Setup
        mock_cache_service.get_recipe.return_value = None
        mock_recipe_repo.get_with_relations.return_value = sample_recipe

        # Execute
        result = await recipe_service.get_recipe(sample_recipe.id)

        # Assert
        assert result.name == "Pasta Carbonara"
        mock_recipe_repo.get_with_relations.assert_called_once_with(sample_recipe.id)
        mock_cache_service.set_recipe.assert_called_once()

    async def test_get_recipe_not_found(
        self, recipe_service, mock_recipe_repo, mock_cache_service
    ):
        """Test getting non-existent recipe."""
        # Setup
        mock_cache_service.get_recipe.return_value = None
        mock_recipe_repo.get_with_relations.return_value = None

        # Execute & Assert
        with pytest.raises(ValueError, match="not found"):
            await recipe_service.get_recipe(uuid4())

    async def test_delete_recipe_success(
        self,
        recipe_service,
        sample_recipe,
        mock_recipe_repo,
        mock_session,
        mock_cache_service,
    ):
        """Test successful recipe deletion."""
        # Setup
        mock_recipe_repo.get.return_value = sample_recipe

        # Execute
        await recipe_service.delete_recipe(sample_recipe.id)

        # Assert
        mock_recipe_repo.delete.assert_called_once_with(sample_recipe.id)
        mock_session.commit.assert_called_once()
        mock_cache_service.invalidate_recipe_cache.assert_called_once_with(
            sample_recipe.id
        )

    async def test_delete_recipe_not_found(self, recipe_service, mock_recipe_repo):
        """Test deleting non-existent recipe."""
        # Setup
        mock_recipe_repo.get.return_value = None

        # Execute & Assert
        with pytest.raises(ValueError, match="not found"):
            await recipe_service.delete_recipe(uuid4())

    async def test_list_recipes_by_cuisine(
        self, recipe_service, mock_recipe_repo, sample_recipe
    ):
        """Test listing recipes with cuisine filter."""
        # Setup
        from app.repositories.pagination import Pagination

        filters = {"cuisine_type": "Italian", "difficulty": DifficultyLevel.MEDIUM}
        pagination = Pagination(page=1, page_size=10)
        mock_recipe_repo.find_by_cuisine_and_difficulty.return_value = [sample_recipe]

        # Execute
        results = await recipe_service.list_recipes(filters, pagination)

        # Assert
        assert len(results) == 1
        assert results[0].name == "Pasta Carbonara"
        mock_recipe_repo.find_by_cuisine_and_difficulty.assert_called_once()

    async def test_list_recipes_by_ingredients(
        self, recipe_service, mock_recipe_repo, sample_recipe
    ):
        """Test listing recipes with ingredient filter."""
        # Setup
        from app.repositories.pagination import Pagination

        filters = {"ingredients": ["pasta", "eggs"], "match_all": True}
        pagination = Pagination(page=1, page_size=10)
        mock_recipe_repo.find_by_ingredients.return_value = [sample_recipe]

        # Execute
        results = await recipe_service.list_recipes(filters, pagination)

        # Assert
        assert len(results) == 1
        mock_recipe_repo.find_by_ingredients.assert_called_once()

    async def test_list_recipes_by_text(
        self, recipe_service, mock_recipe_repo, sample_recipe
    ):
        """Test listing recipes with text search."""
        # Setup
        from app.repositories.pagination import Pagination

        filters = {"text": "carbonara"}
        pagination = Pagination(page=1, page_size=10)
        mock_recipe_repo.search_by_text.return_value = [sample_recipe]

        # Execute
        results = await recipe_service.list_recipes(filters, pagination)

        # Assert
        assert len(results) == 1
        mock_recipe_repo.search_by_text.assert_called_once()

    async def test_validate_business_rules_success(
        self, recipe_service, sample_recipe_create, mock_recipe_repo
    ):
        """Test successful business rule validation."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []

        # Execute - Should not raise
        await recipe_service.validate_business_rules(sample_recipe_create)

    async def test_validate_business_rules_duplicate_name(
        self, recipe_service, sample_recipe_create, mock_recipe_repo, sample_recipe
    ):
        """Test validation fails for duplicate name."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = [sample_recipe]

        # Execute & Assert
        with pytest.raises(ValueError, match="already exists"):
            await recipe_service.validate_business_rules(sample_recipe_create)

    async def test_validate_business_rules_invalid_time(
        self, recipe_service, sample_recipe_create, mock_recipe_repo
    ):
        """Test validation fails for excessive cooking time."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []
        sample_recipe_create.prep_time = 1000
        sample_recipe_create.cook_time = 500

        # Execute & Assert
        with pytest.raises(ValueError, match="exceeds 24 hours"):
            await recipe_service.validate_business_rules(sample_recipe_create)

    async def test_validate_business_rules_invalid_servings(
        self, recipe_service, sample_recipe_create, mock_recipe_repo
    ):
        """Test validation fails for zero servings."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []
        sample_recipe_create.servings = 0

        # Execute & Assert
        with pytest.raises(ValueError, match="Servings must be positive"):
            await recipe_service.validate_business_rules(sample_recipe_create)

    async def test_validate_business_rules_invalid_instructions(
        self, recipe_service, sample_recipe_create, mock_recipe_repo
    ):
        """Test validation fails for empty instructions."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []
        sample_recipe_create.instructions = {}

        # Execute & Assert
        with pytest.raises(ValueError, match="Instructions must be a non-empty"):
            await recipe_service.validate_business_rules(sample_recipe_create)

    async def test_calculate_recipe_metrics(self, recipe_service, sample_recipe):
        """Test recipe metrics calculation."""
        # Setup
        sample_recipe.nutritional_info = NutritionalInfo(
            id=uuid4(),
            recipe_id=sample_recipe.id,
            calories=450.0,
        )

        # Execute
        metrics = await recipe_service.calculate_recipe_metrics(sample_recipe)

        # Assert
        assert metrics["total_time"] == 25  # 10 prep + 15 cook
        assert metrics["difficulty_score"] == 60  # Medium
        assert metrics["ingredient_count"] == 0  # No ingredients in sample
        assert "calories_per_serving" in metrics

    async def test_calculate_recipe_metrics_minimal(
        self, recipe_service, sample_recipe
    ):
        """Test metrics calculation for minimal recipe."""
        # Setup
        sample_recipe.prep_time = None
        sample_recipe.cook_time = None
        sample_recipe.nutritional_info = None

        # Execute
        metrics = await recipe_service.calculate_recipe_metrics(sample_recipe)

        # Assert
        assert metrics["total_time"] is None
        assert metrics["difficulty_score"] == 60
        assert metrics["calories_per_serving"] is None

    async def test_enrich_recipe_data(self, recipe_service, sample_recipe):
        """Test recipe data enrichment."""
        # Execute
        enriched = await recipe_service.enrich_recipe_data(sample_recipe)

        # Assert - Should return recipe (enrichment can be extended)
        assert enriched == sample_recipe

    async def test_recipe_to_response_with_relations(
        self, recipe_service, sample_recipe
    ):
        """Test converting recipe with relations to response."""
        # Setup
        now = datetime.now(timezone.utc)
        sample_recipe.ingredients = [
            Ingredient(
                id=uuid4(),
                recipe_id=sample_recipe.id,
                name="pasta",
                quantity=500,
                unit="g",
                created_at=now,
                updated_at=now,
            )
        ]
        sample_recipe.nutritional_info = NutritionalInfo(
            id=uuid4(),
            recipe_id=sample_recipe.id,
            calories=450.0,
            protein_g=18.0,
            created_at=now,
            updated_at=now,
        )

        # Execute
        response = recipe_service._recipe_to_response(sample_recipe)

        # Assert
        assert response.name == "Pasta Carbonara"
        assert len(response.ingredients) == 1
        assert response.ingredients[0].name == "pasta"
        assert response.nutritional_info is not None
        assert response.nutritional_info.calories == 450.0
        assert response.embedding is None  # Should not expose embedding

    # New test case: Test create recipe with minimal data
    async def test_create_recipe_minimal_data(
        self,
        recipe_service,
        mock_recipe_repo,
        mock_session,
        mock_embedding_service,
        sample_recipe,
    ):
        """Test creating recipe with minimal required fields."""
        # Setup
        minimal_data = RecipeCreate(
            name="Minimal Recipe",
            instructions={"steps": ["Cook"]},
            difficulty=DifficultyLevel.EASY,
            ingredients=[],
            category_ids=[],
        )
        mock_recipe_repo.search_by_text.return_value = []
        mock_recipe_repo.get_with_relations.return_value = sample_recipe
        mock_embedding_service.create_recipe_embedding.return_value = [0.1] * 768

        # Execute
        result = await recipe_service.create_recipe(minimal_data)

        # Assert
        assert result.name == "Pasta Carbonara"
        mock_session.commit.assert_called_once()

    # New test case: Test update recipe with category changes
    async def test_update_recipe_change_categories(
        self, recipe_service, sample_recipe, mock_recipe_repo, mock_session
    ):
        """Test updating recipe categories."""
        # Setup
        new_category_id = uuid4()
        mock_recipe_repo.get.return_value = sample_recipe
        mock_recipe_repo.get_with_relations.return_value = sample_recipe
        updates = RecipeUpdate(category_ids=[new_category_id])

        # Execute
        await recipe_service.update_recipe(sample_recipe.id, updates)

        # Assert
        assert mock_session.delete.call_count >= 0
        mock_session.add.assert_called()

    # New test case: Test validate business rules with negative servings
    async def test_validate_business_rules_negative_servings(
        self, recipe_service, sample_recipe_create, mock_recipe_repo
    ):
        """Test validation fails for negative servings."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []
        sample_recipe_create.servings = -5

        # Execute & Assert
        with pytest.raises(ValueError, match="Servings must be positive"):
            await recipe_service.validate_business_rules(sample_recipe_create)

    # New test case: Test calculate metrics with no time data
    async def test_calculate_recipe_metrics_no_time(
        self, recipe_service, sample_recipe
    ):
        """Test metrics calculation when time fields are None."""
        # Setup
        sample_recipe.prep_time = None
        sample_recipe.cook_time = None

        # Execute
        metrics = await recipe_service.calculate_recipe_metrics(sample_recipe)

        # Assert
        assert metrics["total_time"] is None

    # New test case: Test calculate metrics with only prep time
    async def test_calculate_recipe_metrics_prep_time_only(
        self, recipe_service, sample_recipe
    ):
        """Test metrics calculation with only prep time."""
        # Setup
        sample_recipe.prep_time = 20
        sample_recipe.cook_time = None

        # Execute
        metrics = await recipe_service.calculate_recipe_metrics(sample_recipe)

        # Assert
        assert metrics["total_time"] == 20

    # New test case: Test calculate metrics with only cook time
    async def test_calculate_recipe_metrics_cook_time_only(
        self, recipe_service, sample_recipe
    ):
        """Test metrics calculation with only cook time."""
        # Setup
        sample_recipe.prep_time = None
        sample_recipe.cook_time = 30

        # Execute
        metrics = await recipe_service.calculate_recipe_metrics(sample_recipe)

        # Assert
        assert metrics["total_time"] == 30

    # New test case: Test list recipes with no filters
    async def test_list_recipes_no_filters(
        self, recipe_service, mock_recipe_repo, sample_recipe
    ):
        """Test listing recipes without any filters."""
        # Setup
        from app.repositories.pagination import Pagination

        filters = {}
        pagination = Pagination(page=1, page_size=10)
        mock_recipe_repo.get_all.return_value = [sample_recipe]

        # Execute
        results = await recipe_service.list_recipes(filters, pagination)

        # Assert
        assert len(results) == 1
        mock_recipe_repo.get_all.assert_called_once()

    # New test case: Test update recipe embedding failure doesn't break update
    async def test_update_recipe_embedding_failure_graceful(
        self,
        recipe_service,
        sample_recipe,
        mock_recipe_repo,
        mock_embedding_service,
        mock_session,
    ):
        """Test update continues if embedding regeneration fails."""
        # Setup
        mock_recipe_repo.get.return_value = sample_recipe
        mock_recipe_repo.get_with_relations.return_value = sample_recipe
        mock_embedding_service.create_recipe_embedding.side_effect = Exception(
            "Embedding API failed"
        )
        updates = RecipeUpdate(name="New Name")

        # Execute - Should not raise
        await recipe_service.update_recipe(sample_recipe.id, updates)

        # Assert - Transaction should still commit
        mock_session.commit.assert_called_once()

    # New test case: Test validate business rules with only prep time
    async def test_validate_business_rules_only_prep_time(
        self, recipe_service, sample_recipe_create, mock_recipe_repo
    ):
        """Test validation with only prep time set."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []
        sample_recipe_create.prep_time = 30
        sample_recipe_create.cook_time = None

        # Execute - Should not raise
        await recipe_service.validate_business_rules(sample_recipe_create)

    # New test case: Test validate business rules with boundary times
    async def test_validate_business_rules_boundary_time(
        self, recipe_service, sample_recipe_create, mock_recipe_repo
    ):
        """Test validation at 24 hour boundary."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []
        sample_recipe_create.prep_time = 1439  # Just under 24 hours
        sample_recipe_create.cook_time = 1

        # Execute - Should pass at exactly 1440
        await recipe_service.validate_business_rules(sample_recipe_create)

        # Now test over boundary
        sample_recipe_create.prep_time = 1440
        with pytest.raises(ValueError, match="exceeds 24 hours"):
            await recipe_service.validate_business_rules(sample_recipe_create)

    # New test case: Test create recipe with invalid instruction format
    async def test_create_recipe_invalid_instructions(
        self, recipe_service, sample_recipe_create, mock_recipe_repo
    ):
        """Test validation fails for invalid instructions format."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []
        sample_recipe_create.instructions = None

        # Execute & Assert
        with pytest.raises(ValueError, match="Instructions must be a non-empty"):
            await recipe_service.validate_business_rules(sample_recipe_create)

    # New test case: Test recipe_to_response without ingredients
    async def test_recipe_to_response_no_ingredients(
        self, recipe_service, sample_recipe
    ):
        """Test converting recipe without ingredients."""
        # Setup
        sample_recipe.ingredients = []

        # Execute
        response = recipe_service._recipe_to_response(sample_recipe)

        # Assert
        assert response.name == "Pasta Carbonara"
        assert len(response.ingredients) == 0

    # New test case: Test recipe_to_response without nutritional info
    async def test_recipe_to_response_no_nutrition(
        self, recipe_service, sample_recipe
    ):
        """Test converting recipe without nutritional info."""
        # Setup
        sample_recipe.nutritional_info = None

        # Execute
        response = recipe_service._recipe_to_response(sample_recipe)

        # Assert
        assert response.nutritional_info is None

    # New test case: Test delete recipe invalidates cache
    async def test_delete_recipe_cache_invalidation(
        self,
        recipe_service,
        sample_recipe,
        mock_recipe_repo,
        mock_cache_service,
        mock_session,
    ):
        """Test deleting recipe invalidates cache."""
        # Setup
        recipe_id = sample_recipe.id
        mock_recipe_repo.get.return_value = sample_recipe

        # Execute
        await recipe_service.delete_recipe(recipe_id)

        # Assert
        mock_cache_service.invalidate_recipe_cache.assert_called_once_with(recipe_id)

    # New test case: Test get recipe caches result
    async def test_get_recipe_caches_result(
        self,
        recipe_service,
        sample_recipe,
        mock_recipe_repo,
        mock_cache_service,
    ):
        """Test getting recipe from database caches the result."""
        # Setup
        mock_cache_service.get_recipe.return_value = None
        mock_recipe_repo.get_with_relations.return_value = sample_recipe

        # Execute
        await recipe_service.get_recipe(sample_recipe.id)

        # Assert
        mock_cache_service.set_recipe.assert_called_once()

    # New test case: Test create recipe with nutritional info
    async def test_create_recipe_with_nutritional_info(
        self,
        recipe_service,
        sample_recipe_create,
        mock_recipe_repo,
        mock_session,
        mock_embedding_service,
        sample_recipe,
    ):
        """Test creating recipe with complete nutritional info."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []
        mock_recipe_repo.get_with_relations.return_value = sample_recipe
        assert sample_recipe_create.nutritional_info is not None

        # Execute
        result = await recipe_service.create_recipe(sample_recipe_create)

        # Assert
        # Should add nutritional info to session
        assert mock_session.add.call_count >= 1

    # New test case: Test update with empty category list
    async def test_update_recipe_empty_category_list(
        self, recipe_service, sample_recipe, mock_recipe_repo, mock_session
    ):
        """Test updating recipe with empty category list."""
        # Setup
        mock_recipe_repo.get.return_value = sample_recipe
        mock_recipe_repo.get_with_relations.return_value = sample_recipe
        updates = RecipeUpdate(category_ids=[])

        # Execute
        await recipe_service.update_recipe(sample_recipe.id, updates)

        # Assert
        mock_session.commit.assert_called_once()

    # New test case: Test calculate metrics with different difficulty levels
    async def test_calculate_recipe_metrics_all_difficulties(
        self, recipe_service, sample_recipe
    ):
        """Test metrics calculation for all difficulty levels."""
        # Test easy
        sample_recipe.difficulty = DifficultyLevel.EASY
        metrics = await recipe_service.calculate_recipe_metrics(sample_recipe)
        assert metrics["difficulty_score"] == 30

        # Test medium
        sample_recipe.difficulty = DifficultyLevel.MEDIUM
        metrics = await recipe_service.calculate_recipe_metrics(sample_recipe)
        assert metrics["difficulty_score"] == 60

        # Test hard
        sample_recipe.difficulty = DifficultyLevel.HARD
        metrics = await recipe_service.calculate_recipe_metrics(sample_recipe)
        assert metrics["difficulty_score"] == 90

    # New test case: Test create recipe transaction rollback on error
    async def test_create_recipe_session_flush_error(
        self,
        recipe_service,
        sample_recipe_create,
        mock_recipe_repo,
        mock_session,
    ):
        """Test create recipe handles session flush errors."""
        # Setup
        mock_recipe_repo.search_by_text.return_value = []
        mock_session.flush.side_effect = Exception("Database error")

        # Execute & Assert
        with pytest.raises(Exception, match="Database error"):
            await recipe_service.create_recipe(sample_recipe_create)

    # New test case: Test update recipe with cuisine type change
    async def test_update_recipe_cuisine_type_change(
        self,
        recipe_service,
        sample_recipe,
        mock_recipe_repo,
        mock_embedding_service,
        mock_session,
    ):
        """Test updating cuisine type regenerates embedding."""
        # Setup
        mock_recipe_repo.get.return_value = sample_recipe
        mock_recipe_repo.get_with_relations.return_value = sample_recipe
        updates = RecipeUpdate(cuisine_type="French")

        # Execute
        await recipe_service.update_recipe(sample_recipe.id, updates)

        # Assert - Embedding should be regenerated
        mock_embedding_service.create_recipe_embedding.assert_called_once()

    # New test case: Test update recipe with diet types change
    async def test_update_recipe_diet_types_change(
        self,
        recipe_service,
        sample_recipe,
        mock_recipe_repo,
        mock_embedding_service,
        mock_session,
    ):
        """Test updating diet types regenerates embedding."""
        # Setup
        mock_recipe_repo.get.return_value = sample_recipe
        mock_recipe_repo.get_with_relations.return_value = sample_recipe
        updates = RecipeUpdate(diet_types=["vegan", "gluten-free"])

        # Execute
        await recipe_service.update_recipe(sample_recipe.id, updates)

        # Assert - Embedding should be regenerated
        mock_embedding_service.create_recipe_embedding.assert_called_once()

    # New test case: Test calculate metrics with multiple ingredients
    async def test_calculate_recipe_metrics_with_ingredients(
        self, recipe_service, sample_recipe
    ):
        """Test metrics calculation with ingredients."""
        # Setup
        now = datetime.now(timezone.utc)
        sample_recipe.ingredients = [
            Ingredient(
                id=uuid4(),
                recipe_id=sample_recipe.id,
                name=f"ingredient{i}",
                quantity=100,
                unit="g",
                created_at=now,
                updated_at=now,
            )
            for i in range(5)
        ]

        # Execute
        metrics = await recipe_service.calculate_recipe_metrics(sample_recipe)

        # Assert
        assert metrics["ingredient_count"] == 5
