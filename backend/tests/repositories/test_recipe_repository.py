"""Tests for recipe repository specialized methods."""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DifficultyLevel
from app.repositories.pagination import Pagination
from app.repositories.recipe import RecipeRepository
from tests.repositories.conftest import Ingredient, Recipe


class TestRecipeRepository:
    """Test recipe repository specialized methods."""

    @pytest.mark.asyncio
    async def test_find_by_ingredients_single_match(
        self, db_session: AsyncSession, recipe_with_ingredients: Recipe
    ):
        """Test finding recipes by single ingredient."""
        repo = RecipeRepository(db_session)

        results = await repo.find_by_ingredients(["pasta"])

        assert len(results) >= 1
        assert any(r.id == recipe_with_ingredients.id for r in results)

    @pytest.mark.asyncio
    async def test_find_by_ingredients_multiple_or(
        self, db_session: AsyncSession, recipe_with_ingredients: Recipe
    ):
        """Test finding recipes with any of multiple ingredients (OR)."""
        repo = RecipeRepository(db_session)

        results = await repo.find_by_ingredients(["pasta", "eggs"], match_all=False)

        assert len(results) >= 1
        assert any(r.id == recipe_with_ingredients.id for r in results)

    @pytest.mark.asyncio
    async def test_find_by_ingredients_multiple_and(
        self, db_session: AsyncSession, recipe_with_ingredients: Recipe
    ):
        """Test finding recipes with all ingredients (AND)."""
        repo = RecipeRepository(db_session)

        # Recipe has pasta, eggs, and parmesan
        results = await repo.find_by_ingredients(
            ["pasta", "eggs"], match_all=True
        )

        assert len(results) >= 1
        assert any(r.id == recipe_with_ingredients.id for r in results)

    @pytest.mark.asyncio
    async def test_find_by_ingredients_no_match(
        self, db_session: AsyncSession, recipe_with_ingredients: Recipe
    ):
        """Test finding recipes with non-existent ingredient."""
        repo = RecipeRepository(db_session)

        results = await repo.find_by_ingredients(["chocolate"])

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_find_by_ingredients_with_pagination(
        self, db_session: AsyncSession, recipe_with_ingredients: Recipe
    ):
        """Test finding recipes by ingredients with pagination."""
        repo = RecipeRepository(db_session)

        pagination = Pagination(offset=0, limit=1)
        results = await repo.find_by_ingredients(["pasta"], pagination=pagination)

        assert len(results) <= 1

    @pytest.mark.asyncio
    async def test_find_by_cuisine_and_difficulty_both(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test finding by both cuisine and difficulty."""
        repo = RecipeRepository(db_session)

        results = await repo.find_by_cuisine_and_difficulty(
            cuisine="Italian", difficulty=DifficultyLevel.EASY
        )

        assert len(results) >= 1
        assert all(r.cuisine_type == "Italian" for r in results)
        assert all(r.difficulty == DifficultyLevel.EASY for r in results)

    @pytest.mark.asyncio
    async def test_find_by_cuisine_only(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test finding by cuisine only."""
        repo = RecipeRepository(db_session)

        results = await repo.find_by_cuisine_and_difficulty(cuisine="Italian")

        assert len(results) >= 1
        assert all(r.cuisine_type == "Italian" for r in results)

    @pytest.mark.asyncio
    async def test_find_by_difficulty_only(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test finding by difficulty only."""
        repo = RecipeRepository(db_session)

        results = await repo.find_by_cuisine_and_difficulty(
            difficulty=DifficultyLevel.EASY
        )

        assert len(results) >= 2
        assert all(r.difficulty == DifficultyLevel.EASY for r in results)

    @pytest.mark.asyncio
    async def test_find_by_cuisine_and_difficulty_no_match(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test finding with no matching recipes."""
        repo = RecipeRepository(db_session)

        results = await repo.find_by_cuisine_and_difficulty(
            cuisine="NonExistent", difficulty=DifficultyLevel.EASY
        )

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_get_with_relations(
        self, db_session: AsyncSession, recipe_with_relations: Recipe
    ):
        """Test getting recipe with all relations eagerly loaded."""
        repo = RecipeRepository(db_session)

        result = await repo.get_with_relations(recipe_with_relations.id)

        assert result is not None
        assert result.id == recipe_with_relations.id

        # Relations should be loaded
        assert len(result.ingredients) > 0
        assert len(result.recipe_categories) > 0
        assert result.nutritional_info is not None

    @pytest.mark.asyncio
    async def test_get_with_relations_nonexistent(self, db_session: AsyncSession):
        """Test getting nonexistent recipe with relations."""
        repo = RecipeRepository(db_session)

        result = await repo.get_with_relations(uuid.uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_update_embedding(
        self, db_session: AsyncSession, sample_recipe: Recipe
    ):
        """Test updating recipe embedding."""
        repo = RecipeRepository(db_session)

        embedding = [0.1] * 768  # Valid 768-dimensional embedding
        await repo.update_embedding(sample_recipe.id, embedding)

        # Refresh and verify
        await db_session.refresh(sample_recipe)
        assert sample_recipe.embedding == embedding

    @pytest.mark.asyncio
    async def test_update_embedding_wrong_dimension(
        self, db_session: AsyncSession, sample_recipe: Recipe
    ):
        """Test updating embedding with wrong dimensions raises error."""
        repo = RecipeRepository(db_session)

        embedding = [0.1] * 100  # Wrong dimension

        with pytest.raises(ValueError, match="must be 768 dimensions"):
            await repo.update_embedding(sample_recipe.id, embedding)

    @pytest.mark.asyncio
    async def test_update_embedding_nonexistent_recipe(self, db_session: AsyncSession):
        """Test updating embedding for nonexistent recipe raises error."""
        repo = RecipeRepository(db_session)

        embedding = [0.1] * 768

        with pytest.raises(ValueError, match="not found or is deleted"):
            await repo.update_embedding(uuid.uuid4(), embedding)

    @pytest.mark.asyncio
    async def test_get_popular_recipes(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test getting popular recipes."""
        repo = RecipeRepository(db_session)

        results = await repo.get_popular_recipes(limit=10)

        assert len(results) <= 10
        assert len(results) == len(sample_recipes)

        # Should be ordered by created_at desc (newest first)
        if len(results) > 1:
            assert results[0].created_at >= results[-1].created_at

    @pytest.mark.asyncio
    async def test_get_popular_recipes_with_cuisine(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test getting popular recipes filtered by cuisine."""
        repo = RecipeRepository(db_session)

        results = await repo.get_popular_recipes(limit=10, cuisine="Italian")

        assert all(r.cuisine_type == "Italian" for r in results)

    @pytest.mark.asyncio
    async def test_get_popular_recipes_limit_enforcement(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test that get_popular_recipes enforces max limit of 100."""
        repo = RecipeRepository(db_session)

        # Request more than 100, should cap at 100
        results = await repo.get_popular_recipes(limit=200)

        # Can't have more than what exists, but limit should be applied
        assert len(results) <= 100

    @pytest.mark.asyncio
    async def test_search_by_text_name_match(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test text search matching recipe name."""
        repo = RecipeRepository(db_session)

        results = await repo.search_by_text("Pasta")

        assert len(results) >= 1
        assert any("Pasta" in r.name for r in results)

    @pytest.mark.asyncio
    async def test_search_by_text_description_match(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test text search matching recipe description."""
        repo = RecipeRepository(db_session)

        results = await repo.search_by_text("Simple")

        assert len(results) >= 1
        assert any("Simple" in (r.description or "") for r in results)

    @pytest.mark.asyncio
    async def test_search_by_text_case_insensitive(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test text search is case insensitive."""
        repo = RecipeRepository(db_session)

        results_lower = await repo.search_by_text("pasta")
        results_upper = await repo.search_by_text("PASTA")

        assert len(results_lower) == len(results_upper)

    @pytest.mark.asyncio
    async def test_search_by_text_no_match(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test text search with no matches."""
        repo = RecipeRepository(db_session)

        results = await repo.search_by_text("NonExistentRecipe12345")

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_get_recipes_by_diet_type(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test getting recipes by diet type."""
        repo = RecipeRepository(db_session)

        results = await repo.get_recipes_by_diet_type("vegetarian")

        assert len(results) >= 1
        assert all("vegetarian" in r.diet_types for r in results)

    @pytest.mark.asyncio
    async def test_get_recipes_by_diet_type_vegan(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test getting vegan recipes."""
        repo = RecipeRepository(db_session)

        results = await repo.get_recipes_by_diet_type("vegan")

        assert len(results) >= 1
        assert all("vegan" in r.diet_types for r in results)

    @pytest.mark.asyncio
    async def test_get_recipes_with_time_range_total(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test getting recipes within total time limit."""
        repo = RecipeRepository(db_session)

        results = await repo.get_recipes_with_time_range(max_total_time=20)

        assert len(results) >= 1
        assert all(
            (r.prep_time or 0) + (r.cook_time or 0) <= 20 for r in results
        )

    @pytest.mark.asyncio
    async def test_get_recipes_with_time_range_prep(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test getting recipes within prep time limit."""
        repo = RecipeRepository(db_session)

        results = await repo.get_recipes_with_time_range(max_prep_time=15)

        assert len(results) >= 1
        assert all((r.prep_time or 0) <= 15 for r in results)

    @pytest.mark.asyncio
    async def test_get_recipes_with_time_range_cook(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test getting recipes within cook time limit."""
        repo = RecipeRepository(db_session)

        results = await repo.get_recipes_with_time_range(max_cook_time=30)

        assert len(results) >= 1
        assert all((r.cook_time or 0) <= 30 for r in results)

    @pytest.mark.asyncio
    async def test_count_by_cuisine(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test counting recipes by cuisine."""
        repo = RecipeRepository(db_session)

        counts = await repo.count_by_cuisine()

        assert isinstance(counts, dict)
        assert "Italian" in counts
        assert counts["Italian"] >= 1

    @pytest.mark.asyncio
    async def test_count_by_difficulty(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test counting recipes by difficulty."""
        repo = RecipeRepository(db_session)

        counts = await repo.count_by_difficulty()

        assert isinstance(counts, dict)
        assert "easy" in counts
        assert "hard" in counts
        assert counts["easy"] >= 2

    @pytest.mark.asyncio
    async def test_bulk_update_embeddings(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test bulk updating embeddings."""
        repo = RecipeRepository(db_session)

        updates = [
            {"id": sample_recipes[0].id, "embedding": [0.1] * 768},
            {"id": sample_recipes[1].id, "embedding": [0.2] * 768},
        ]

        await repo.bulk_update_embeddings(updates)

        # Verify updates
        await db_session.refresh(sample_recipes[0])
        await db_session.refresh(sample_recipes[1])

        assert sample_recipes[0].embedding == [0.1] * 768
        assert sample_recipes[1].embedding == [0.2] * 768

    @pytest.mark.asyncio
    async def test_bulk_update_embeddings_wrong_dimension(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test bulk update with wrong embedding dimension raises error."""
        repo = RecipeRepository(db_session)

        updates = [{"id": sample_recipes[0].id, "embedding": [0.1] * 100}]

        with pytest.raises(ValueError, match="must be 768 dimensions"):
            await repo.bulk_update_embeddings(updates)

    @pytest.mark.asyncio
    async def test_bulk_update_embeddings_missing_keys(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test bulk update with missing keys raises error."""
        repo = RecipeRepository(db_session)

        updates = [{"id": sample_recipes[0].id}]  # Missing 'embedding'

        with pytest.raises(ValueError, match="must contain 'id' and 'embedding'"):
            await repo.bulk_update_embeddings(updates)
