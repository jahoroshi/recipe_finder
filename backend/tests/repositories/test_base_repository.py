"""Tests for base repository."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DifficultyLevel
from app.repositories.base import BaseRepository
from app.repositories.pagination import Pagination
from tests.repositories.conftest import Recipe


class TestBaseRepository:
    """Test base repository CRUD operations."""

    @pytest.mark.asyncio
    async def test_create(self, db_session: AsyncSession):
        """Test creating an entity."""
        repo = BaseRepository(Recipe, db_session)

        recipe = Recipe(
            id=uuid.uuid4(),
            name="New Recipe",
            description="Test description",
            instructions={"steps": ["Step 1"]},
            difficulty=DifficultyLevel.EASY,
        )

        created = await repo.create(recipe)

        assert created.id is not None
        assert created.name == "New Recipe"
        assert created.created_at is not None
        assert created.deleted_at is None

    @pytest.mark.asyncio
    async def test_get(self, db_session: AsyncSession, sample_recipe: Recipe):
        """Test getting entity by ID."""
        repo = BaseRepository(Recipe, db_session)

        result = await repo.get(sample_recipe.id)

        assert result is not None
        assert result.id == sample_recipe.id
        assert result.name == sample_recipe.name

    @pytest.mark.asyncio
    async def test_get_nonexistent(self, db_session: AsyncSession):
        """Test getting nonexistent entity returns None."""
        repo = BaseRepository(Recipe, db_session)

        result = await repo.get(uuid.uuid4())

        assert result is None

    @pytest.mark.asyncio
    async def test_get_soft_deleted(self, db_session: AsyncSession, sample_recipe: Recipe):
        """Test that soft-deleted entities are not returned by get."""
        repo = BaseRepository(Recipe, db_session)

        # Soft delete the recipe
        await repo.delete(sample_recipe.id)

        # Try to get it
        result = await repo.get(sample_recipe.id)

        assert result is None

    @pytest.mark.asyncio
    async def test_update(self, db_session: AsyncSession, sample_recipe: Recipe):
        """Test updating entity."""
        repo = BaseRepository(Recipe, db_session)

        updates = {"name": "Updated Recipe", "servings": 6}
        updated = await repo.update(sample_recipe.id, updates)

        assert updated.name == "Updated Recipe"
        assert updated.servings == 6
        assert updated.updated_at > sample_recipe.updated_at

    @pytest.mark.asyncio
    async def test_update_nonexistent_raises_error(self, db_session: AsyncSession):
        """Test updating nonexistent entity raises error."""
        repo = BaseRepository(Recipe, db_session)

        with pytest.raises(ValueError, match="not found or is deleted"):
            await repo.update(uuid.uuid4(), {"name": "Test"})

    @pytest.mark.asyncio
    async def test_update_soft_deleted_raises_error(
        self, db_session: AsyncSession, sample_recipe: Recipe
    ):
        """Test updating soft-deleted entity raises error."""
        repo = BaseRepository(Recipe, db_session)

        # Soft delete
        await repo.delete(sample_recipe.id)

        # Try to update
        with pytest.raises(ValueError, match="not found or is deleted"):
            await repo.update(sample_recipe.id, {"name": "Test"})

    @pytest.mark.asyncio
    async def test_delete_soft_delete(
        self, db_session: AsyncSession, sample_recipe: Recipe
    ):
        """Test soft delete sets deleted_at timestamp."""
        repo = BaseRepository(Recipe, db_session)

        await repo.delete(sample_recipe.id)

        # Refresh to get updated state
        await db_session.refresh(sample_recipe)

        assert sample_recipe.deleted_at is not None
        assert isinstance(sample_recipe.deleted_at, datetime)

    @pytest.mark.asyncio
    async def test_delete_nonexistent_raises_error(self, db_session: AsyncSession):
        """Test deleting nonexistent entity raises error."""
        repo = BaseRepository(Recipe, db_session)

        with pytest.raises(ValueError, match="not found or already deleted"):
            await repo.delete(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_delete_already_deleted_raises_error(
        self, db_session: AsyncSession, sample_recipe: Recipe
    ):
        """Test deleting already deleted entity raises error."""
        repo = BaseRepository(Recipe, db_session)

        # First deletion
        await repo.delete(sample_recipe.id)

        # Second deletion should raise error
        with pytest.raises(ValueError, match="not found or already deleted"):
            await repo.delete(sample_recipe.id)

    @pytest.mark.asyncio
    async def test_list_without_filters(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test listing all entities without filters."""
        repo = BaseRepository(Recipe, db_session)

        results = await repo.list()

        assert len(results) == len(sample_recipes)

    @pytest.mark.asyncio
    async def test_list_with_filters(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test listing with filters."""
        repo = BaseRepository(Recipe, db_session)

        results = await repo.list({"difficulty": DifficultyLevel.EASY})

        assert len(results) == 2  # Two easy recipes
        assert all(r.difficulty == DifficultyLevel.EASY for r in results)

    @pytest.mark.asyncio
    async def test_list_with_pagination(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test listing with pagination."""
        repo = BaseRepository(Recipe, db_session)

        pagination = Pagination(offset=0, limit=2)
        results = await repo.list(pagination=pagination)

        assert len(results) == 2

    @pytest.mark.asyncio
    async def test_list_excludes_soft_deleted(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test that list excludes soft-deleted entities."""
        repo = BaseRepository(Recipe, db_session)

        # Delete first recipe
        await repo.delete(sample_recipes[0].id)

        results = await repo.list()

        assert len(results) == len(sample_recipes) - 1
        assert sample_recipes[0].id not in [r.id for r in results]

    @pytest.mark.asyncio
    async def test_count_without_filters(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test counting without filters."""
        repo = BaseRepository(Recipe, db_session)

        count = await repo.count()

        assert count == len(sample_recipes)

    @pytest.mark.asyncio
    async def test_count_with_filters(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test counting with filters."""
        repo = BaseRepository(Recipe, db_session)

        count = await repo.count({"difficulty": DifficultyLevel.EASY})

        assert count == 2

    @pytest.mark.asyncio
    async def test_count_excludes_soft_deleted(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test that count excludes soft-deleted entities."""
        repo = BaseRepository(Recipe, db_session)

        # Delete one recipe
        await repo.delete(sample_recipes[0].id)

        count = await repo.count()

        assert count == len(sample_recipes) - 1

    @pytest.mark.asyncio
    async def test_exists(self, db_session: AsyncSession, sample_recipe: Recipe):
        """Test checking if entity exists."""
        repo = BaseRepository(Recipe, db_session)

        assert await repo.exists(sample_recipe.id)
        assert not await repo.exists(uuid.uuid4())

    @pytest.mark.asyncio
    async def test_exists_soft_deleted(
        self, db_session: AsyncSession, sample_recipe: Recipe
    ):
        """Test that exists returns False for soft-deleted entities."""
        repo = BaseRepository(Recipe, db_session)

        await repo.delete(sample_recipe.id)

        assert not await repo.exists(sample_recipe.id)

    @pytest.mark.asyncio
    async def test_bulk_create(self, db_session: AsyncSession):
        """Test bulk creating entities."""
        repo = BaseRepository(Recipe, db_session)

        recipes = [
            Recipe(
                id=uuid.uuid4(),
                name=f"Recipe {i}",
                instructions={"steps": ["Step 1"]},
                difficulty=DifficultyLevel.EASY,
            )
            for i in range(3)
        ]

        created = await repo.bulk_create(recipes)

        assert len(created) == 3
        assert all(r.id is not None for r in created)
        assert all(r.created_at is not None for r in created)

    @pytest.mark.asyncio
    async def test_bulk_update(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test bulk updating entities."""
        repo = BaseRepository(Recipe, db_session)

        updates = [
            {"id": sample_recipes[0].id, "name": "Updated 1"},
            {"id": sample_recipes[1].id, "name": "Updated 2"},
        ]

        updated = await repo.bulk_update(updates)

        assert len(updated) == 2
        assert updated[0].name == "Updated 1"
        assert updated[1].name == "Updated 2"

    @pytest.mark.asyncio
    async def test_bulk_update_missing_id_raises_error(self, db_session: AsyncSession):
        """Test bulk update with missing ID raises error."""
        repo = BaseRepository(Recipe, db_session)

        updates = [{"name": "Test"}]  # Missing 'id'

        with pytest.raises(ValueError, match="must contain 'id' field"):
            await repo.bulk_update(updates)

    @pytest.mark.asyncio
    async def test_hard_delete(self, db_session: AsyncSession, sample_recipe: Recipe):
        """Test permanent deletion."""
        repo = BaseRepository(Recipe, db_session)

        await repo.hard_delete(sample_recipe.id)

        # Verify it's completely gone
        assert not await repo.exists(sample_recipe.id)
        assert await repo.get(sample_recipe.id) is None

    @pytest.mark.asyncio
    async def test_restore(self, db_session: AsyncSession, sample_recipe: Recipe):
        """Test restoring soft-deleted entity."""
        repo = BaseRepository(Recipe, db_session)

        # Soft delete
        await repo.delete(sample_recipe.id)
        assert not await repo.exists(sample_recipe.id)

        # Restore
        restored = await repo.restore(sample_recipe.id)

        assert restored.deleted_at is None
        assert await repo.exists(sample_recipe.id)

    @pytest.mark.asyncio
    async def test_restore_non_deleted_raises_error(
        self, db_session: AsyncSession, sample_recipe: Recipe
    ):
        """Test restoring non-deleted entity raises error."""
        repo = BaseRepository(Recipe, db_session)

        with pytest.raises(ValueError, match="is not deleted"):
            await repo.restore(sample_recipe.id)

    @pytest.mark.asyncio
    async def test_list_with_in_filter(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test list with IN clause filter."""
        repo = BaseRepository(Recipe, db_session)

        difficulties = [DifficultyLevel.EASY, DifficultyLevel.MEDIUM]
        results = await repo.list({"difficulty": difficulties})

        assert len(results) >= 2
        assert all(r.difficulty in difficulties for r in results)
