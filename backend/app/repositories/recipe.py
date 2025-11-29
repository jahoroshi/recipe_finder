"""Recipe repository with specialized query methods."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import DifficultyLevel, Ingredient, Recipe, RecipeCategory
from app.repositories.base import BaseRepository
from app.repositories.pagination import Pagination


class RecipeRepository(BaseRepository[Recipe]):
    """Specialized repository for Recipe model.

    Extends base repository with recipe-specific query methods including
    ingredient-based search, full-text search, and optimized relation loading.

    Example:
        ```python
        async with get_db() as session:
            repo = RecipeRepository(session)
            recipes = await repo.find_by_cuisine_and_difficulty("Italian", DifficultyLevel.EASY)
        ```
    """

    def __init__(self, session: AsyncSession):
        """Initialize recipe repository.

        Args:
            session: Async database session
        """
        super().__init__(Recipe, session)

    async def find_by_ingredients(
        self,
        ingredients: list[str],
        pagination: Pagination | None = None,
        match_all: bool = False,
    ) -> list[Recipe]:
        """Find recipes containing specified ingredients.

        Args:
            ingredients: List of ingredient names to search for
            pagination: Optional pagination parameters
            match_all: If True, recipe must contain all ingredients.
                      If False, recipe must contain at least one ingredient.

        Returns:
            List of recipes matching ingredient criteria

        Example:
            ```python
            # Recipes with tomato OR garlic
            recipes = await repo.find_by_ingredients(["tomato", "garlic"])

            # Recipes with tomato AND garlic
            recipes = await repo.find_by_ingredients(
                ["tomato", "garlic"], match_all=True
            )
            ```
        """
        if match_all:
            # Recipe must contain ALL ingredients
            stmt = (
                select(Recipe)
                .join(Ingredient)
                .where(
                    and_(
                        Recipe.deleted_at.is_(None),
                        Ingredient.name.in_(ingredients),
                    )
                )
                .group_by(Recipe.id)
                .having(func.count(Ingredient.id) == len(ingredients))
            )
        else:
            # Recipe must contain AT LEAST ONE ingredient
            stmt = (
                select(Recipe)
                .join(Ingredient)
                .where(
                    and_(
                        Recipe.deleted_at.is_(None),
                        Ingredient.name.in_(ingredients),
                    )
                )
                .distinct()
            )

        if pagination:
            stmt = pagination.apply(stmt)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def find_by_cuisine_and_difficulty(
        self,
        cuisine: str | None = None,
        difficulty: DifficultyLevel | None = None,
        pagination: Pagination | None = None,
    ) -> list[Recipe]:
        """Find recipes by cuisine type and/or difficulty level.

        Args:
            cuisine: Cuisine type to filter by (optional)
            difficulty: Difficulty level to filter by (optional)
            pagination: Optional pagination parameters

        Returns:
            List of matching recipes

        Example:
            ```python
            # Italian recipes
            recipes = await repo.find_by_cuisine_and_difficulty(cuisine="Italian")

            # Easy recipes
            recipes = await repo.find_by_cuisine_and_difficulty(
                difficulty=DifficultyLevel.EASY
            )

            # Easy Italian recipes
            recipes = await repo.find_by_cuisine_and_difficulty(
                cuisine="Italian",
                difficulty=DifficultyLevel.EASY
            )
            ```
        """
        stmt = select(Recipe).where(Recipe.deleted_at.is_(None))

        if cuisine:
            stmt = stmt.where(Recipe.cuisine_type == cuisine)

        if difficulty:
            stmt = stmt.where(Recipe.difficulty == difficulty)

        if pagination:
            stmt = pagination.apply(stmt)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_with_relations(self, id: uuid.UUID) -> Recipe | None:
        """Get recipe with all relations eagerly loaded.

        Loads ingredients, categories, and nutritional info in a single query
        using joined loading for optimal performance.

        Args:
            id: Recipe UUID

        Returns:
            Recipe with all relations loaded, or None if not found

        Example:
            ```python
            recipe = await repo.get_with_relations(recipe_id)
            if recipe:
                print(recipe.ingredients)  # Already loaded, no extra query
                print(recipe.nutritional_info)  # Already loaded
            ```
        """
        stmt = (
            select(Recipe)
            .options(
                selectinload(Recipe.ingredients),
                selectinload(Recipe.recipe_categories).selectinload(RecipeCategory.category),
                selectinload(Recipe.nutritional_info),
            )
            .where(Recipe.id == id, Recipe.deleted_at.is_(None))
        )

        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_embedding(
        self, id: uuid.UUID, embedding: list[float]
    ) -> None:
        """Update recipe's vector embedding.

        Args:
            id: Recipe UUID
            embedding: Vector embedding (768 dimensions)

        Raises:
            ValueError: If recipe not found or embedding dimension mismatch

        Example:
            ```python
            embedding = generate_embedding(recipe.name + " " + recipe.description)
            await repo.update_embedding(recipe_id, embedding)
            ```
        """
        if len(embedding) != 768:
            raise ValueError(f"Embedding must be 768 dimensions, got {len(embedding)}")

        recipe = await self.get(id)
        if recipe is None:
            raise ValueError(f"Recipe with id {id} not found or is deleted")

        recipe.embedding = embedding
        await self.session.flush()

    async def get_popular_recipes(
        self, limit: int = 10, cuisine: str | None = None
    ) -> list[Recipe]:
        """Get most popular recipes ordered by creation date.

        Args:
            limit: Maximum number of recipes to return (max 100)
            cuisine: Optional cuisine type filter

        Returns:
            List of popular recipes

        Example:
            ```python
            # Top 10 recipes
            popular = await repo.get_popular_recipes(limit=10)

            # Top 10 Italian recipes
            popular = await repo.get_popular_recipes(limit=10, cuisine="Italian")
            ```
        """
        if limit > 100:
            limit = 100

        stmt = (
            select(Recipe)
            .where(Recipe.deleted_at.is_(None))
            .order_by(Recipe.created_at.desc())
            .limit(limit)
        )

        if cuisine:
            stmt = stmt.where(Recipe.cuisine_type == cuisine)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_text(
        self,
        query: str,
        pagination: Pagination | None = None,
    ) -> list[Recipe]:
        """Full-text search on recipe name and description.

        Uses PostgreSQL's ILIKE for case-insensitive partial matching.

        Args:
            query: Search query string
            pagination: Optional pagination parameters

        Returns:
            List of recipes matching search query

        Example:
            ```python
            results = await repo.search_by_text("pasta carbonara")
            ```
        """
        search_pattern = f"%{query}%"

        stmt = select(Recipe).where(
            and_(
                Recipe.deleted_at.is_(None),
                or_(
                    Recipe.name.ilike(search_pattern),
                    Recipe.description.ilike(search_pattern),
                ),
            )
        )

        if pagination:
            stmt = pagination.apply(stmt)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recipes_by_diet_type(
        self,
        diet_type: str,
        pagination: Pagination | None = None,
    ) -> list[Recipe]:
        """Get recipes filtered by diet type.

        Args:
            diet_type: Diet type (e.g., "vegetarian", "vegan", "gluten-free")
            pagination: Optional pagination parameters

        Returns:
            List of recipes with specified diet type

        Example:
            ```python
            vegetarian = await repo.get_recipes_by_diet_type("vegetarian")
            ```
        """
        from sqlalchemy import func, cast, String

        # Use JSON functions for PostgreSQL compatibility
        # This works with both PostgreSQL and SQLite
        stmt = select(Recipe).where(
            and_(
                Recipe.deleted_at.is_(None),
                # Use JSON-based search for diet_types array
                func.json_extract(
                    cast(Recipe.diet_types, String),
                    '$'
                ).like(f'%"{diet_type}"%')
            )
        )

        if pagination:
            stmt = pagination.apply(stmt)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_recipes_with_time_range(
        self,
        max_total_time: int | None = None,
        max_prep_time: int | None = None,
        max_cook_time: int | None = None,
        pagination: Pagination | None = None,
    ) -> list[Recipe]:
        """Get recipes within specified time constraints.

        Args:
            max_total_time: Maximum total time (prep + cook) in minutes
            max_prep_time: Maximum prep time in minutes
            max_cook_time: Maximum cook time in minutes (0 means no cooking time)
            pagination: Optional pagination parameters

        Returns:
            List of recipes within time constraints

        Example:
            ```python
            # Recipes that take max 30 minutes total
            quick = await repo.get_recipes_with_time_range(max_total_time=30)

            # Recipes with max 15 min prep time
            easy_prep = await repo.get_recipes_with_time_range(max_prep_time=15)

            # Recipes with no cooking time (prep only)
            no_cook = await repo.get_recipes_with_time_range(max_cook_time=0)
            ```
        """
        stmt = select(Recipe).where(Recipe.deleted_at.is_(None))

        if max_prep_time is not None:
            stmt = stmt.where(Recipe.prep_time <= max_prep_time)

        if max_cook_time is not None:
            # Special handling for max_cook_time=0 (recipes with no cooking)
            if max_cook_time == 0:
                stmt = stmt.where(Recipe.cook_time == 0)
            else:
                stmt = stmt.where(Recipe.cook_time <= max_cook_time)

        if max_total_time is not None:
            stmt = stmt.where(
                (Recipe.prep_time + Recipe.cook_time) <= max_total_time
            )

        if pagination:
            stmt = pagination.apply(stmt)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_by_cuisine(self) -> dict[str, int]:
        """Get recipe count grouped by cuisine type.

        Returns:
            Dictionary mapping cuisine types to recipe counts

        Example:
            ```python
            stats = await repo.count_by_cuisine()
            # {"Italian": 15, "Chinese": 10, "Mexican": 8}
            ```
        """
        stmt = (
            select(Recipe.cuisine_type, func.count(Recipe.id))
            .where(Recipe.deleted_at.is_(None), Recipe.cuisine_type.isnot(None))
            .group_by(Recipe.cuisine_type)
        )

        result = await self.session.execute(stmt)
        return {cuisine: count for cuisine, count in result.all()}

    async def count_by_difficulty(self) -> dict[str, int]:
        """Get recipe count grouped by difficulty level.

        Returns:
            Dictionary mapping difficulty levels to recipe counts

        Example:
            ```python
            stats = await repo.count_by_difficulty()
            # {"easy": 20, "medium": 15, "hard": 5}
            ```
        """
        stmt = (
            select(Recipe.difficulty, func.count(Recipe.id))
            .where(Recipe.deleted_at.is_(None))
            .group_by(Recipe.difficulty)
        )

        result = await self.session.execute(stmt)
        return {difficulty.value: count for difficulty, count in result.all()}

    async def bulk_update_embeddings(
        self, updates: list[dict[str, Any]]
    ) -> None:
        """Bulk update recipe embeddings efficiently.

        Args:
            updates: List of dicts with 'id' and 'embedding' keys

        Raises:
            ValueError: If update data invalid or embedding dimension mismatch

        Example:
            ```python
            updates = [
                {"id": uuid1, "embedding": [0.1, 0.2, ...]},
                {"id": uuid2, "embedding": [0.3, 0.4, ...]},
            ]
            await repo.bulk_update_embeddings(updates)
            ```
        """
        for update_data in updates:
            if "id" not in update_data or "embedding" not in update_data:
                raise ValueError("Update must contain 'id' and 'embedding' keys")

            embedding = update_data["embedding"]
            if len(embedding) != 768:
                raise ValueError(
                    f"Embedding must be 768 dimensions, got {len(embedding)}"
                )

            await self.update_embedding(update_data["id"], embedding)
