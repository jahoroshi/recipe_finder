"""Base repository with generic CRUD operations."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Generic, TypeVar

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import BaseModel
from app.repositories.pagination import Pagination

# Generic type variable bound to BaseModel
T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Generic base repository implementing common CRUD operations.

    Provides standard database operations with soft delete support,
    automatic timestamp management, and query building capabilities.

    Type Parameters:
        T: Model class bound to BaseModel

    Attributes:
        model: SQLAlchemy model class
        session: Async database session

    Example:
        ```python
        class RecipeRepository(BaseRepository[Recipe]):
            def __init__(self, session: AsyncSession):
                super().__init__(Recipe, session)
        ```
    """

    def __init__(self, model: type[T], session: AsyncSession):
        """Initialize repository with model and session.

        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session

    async def create(self, entity: T) -> T:
        """Create a new entity in the database.

        Args:
            entity: Model instance to create

        Returns:
            Created entity with generated ID and timestamps

        Example:
            ```python
            recipe = Recipe(name="Pasta", difficulty=DifficultyLevel.EASY)
            created = await repository.create(recipe)
            ```
        """
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def get(self, id: uuid.UUID) -> T | None:
        """Get entity by ID, respecting soft deletes.

        Args:
            id: UUID of the entity

        Returns:
            Entity if found and not deleted, None otherwise

        Example:
            ```python
            recipe = await repository.get(recipe_id)
            if recipe:
                print(recipe.name)
            ```
        """
        stmt = select(self.model).where(
            self.model.id == id, self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update(self, id: uuid.UUID, updates: dict[str, Any]) -> T:
        """Update entity with provided fields.

        Automatically updates the updated_at timestamp.

        Args:
            id: UUID of the entity to update
            updates: Dictionary of field names and new values

        Returns:
            Updated entity

        Raises:
            ValueError: If entity not found or is deleted

        Example:
            ```python
            updated = await repository.update(
                recipe_id,
                {"name": "New Name", "difficulty": DifficultyLevel.HARD}
            )
            ```
        """
        entity = await self.get(id)
        if entity is None:
            raise ValueError(f"Entity with id {id} not found or is deleted")

        # Update fields
        for key, value in updates.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        # Automatic timestamp update
        entity.updated_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, id: uuid.UUID) -> None:
        """Soft delete entity by setting deleted_at timestamp.

        Args:
            id: UUID of the entity to delete

        Raises:
            ValueError: If entity not found or already deleted

        Example:
            ```python
            await repository.delete(recipe_id)
            ```
        """
        entity = await self.get(id)
        if entity is None:
            raise ValueError(f"Entity with id {id} not found or already deleted")

        entity.deleted_at = datetime.utcnow()
        await self.session.flush()

    async def list(
        self, filters: dict[str, Any] | None = None, pagination: Pagination | None = None
    ) -> list[T]:
        """List entities with optional filtering and pagination.

        Only returns non-deleted entities by default.

        Args:
            filters: Dictionary of filter conditions
            pagination: Pagination parameters

        Returns:
            List of entities matching filters

        Example:
            ```python
            filters = {"difficulty": DifficultyLevel.EASY}
            pagination = Pagination(offset=0, limit=20)
            recipes = await repository.list(filters, pagination)
            ```
        """
        stmt = select(self.model).where(self.model.deleted_at.is_(None))

        # Apply filters
        if filters:
            stmt = self._apply_filters(stmt, filters)

        # Apply pagination
        if pagination:
            stmt = pagination.apply(stmt)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count(self, filters: dict[str, Any] | None = None) -> int:
        """Count entities matching filters.

        Only counts non-deleted entities.

        Args:
            filters: Dictionary of filter conditions

        Returns:
            Count of matching entities

        Example:
            ```python
            count = await repository.count({"difficulty": DifficultyLevel.EASY})
            ```
        """
        stmt = select(func.count(self.model.id)).where(self.model.deleted_at.is_(None))

        if filters:
            stmt = self._apply_filters(stmt, filters)

        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def exists(self, id: uuid.UUID) -> bool:
        """Check if entity exists and is not deleted.

        Args:
            id: UUID of the entity

        Returns:
            True if entity exists and not deleted, False otherwise

        Example:
            ```python
            if await repository.exists(recipe_id):
                print("Recipe exists")
            ```
        """
        stmt = select(func.count(self.model.id)).where(
            self.model.id == id, self.model.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        count = result.scalar_one()
        return count > 0

    async def bulk_create(self, entities: list[T]) -> list[T]:
        """Create multiple entities in a single transaction.

        Args:
            entities: List of model instances to create

        Returns:
            List of created entities with IDs and timestamps

        Example:
            ```python
            recipes = [Recipe(...), Recipe(...), Recipe(...)]
            created = await repository.bulk_create(recipes)
            ```
        """
        self.session.add_all(entities)
        await self.session.flush()

        # Refresh all entities to get generated values
        for entity in entities:
            await self.session.refresh(entity)

        return entities

    async def bulk_update(self, updates: list[dict[str, Any]]) -> list[T]:
        """Update multiple entities in a single transaction.

        Each update dict must contain 'id' key.

        Args:
            updates: List of dicts with 'id' and fields to update

        Returns:
            List of updated entities

        Raises:
            ValueError: If any entity not found or update missing 'id'

        Example:
            ```python
            updates = [
                {"id": uuid1, "name": "New Name 1"},
                {"id": uuid2, "name": "New Name 2"}
            ]
            updated = await repository.bulk_update(updates)
            ```
        """
        updated_entities = []

        for update_data in updates:
            if "id" not in update_data:
                raise ValueError("Update data must contain 'id' field")

            entity_id = update_data.pop("id")
            entity = await self.update(entity_id, update_data)
            updated_entities.append(entity)

        return updated_entities

    def _apply_filters(self, stmt: Any, filters: dict[str, Any]) -> Any:
        """Apply filters to SQLAlchemy statement.

        Supports exact match filtering on model attributes.

        Args:
            stmt: SQLAlchemy select statement
            filters: Dictionary of field names and values

        Returns:
            Statement with filters applied
        """
        for key, value in filters.items():
            if hasattr(self.model, key):
                column = getattr(self.model, key)

                # Handle list values (IN clause)
                if isinstance(value, list):
                    stmt = stmt.where(column.in_(value))
                else:
                    stmt = stmt.where(column == value)

        return stmt

    async def hard_delete(self, id: uuid.UUID) -> None:
        """Permanently delete entity from database.

        WARNING: This operation is irreversible. Use with caution.

        Args:
            id: UUID of the entity to permanently delete

        Raises:
            ValueError: If entity not found

        Example:
            ```python
            await repository.hard_delete(recipe_id)  # Permanent deletion
            ```
        """
        # Get entity without soft delete filter
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        entity = result.scalar_one_or_none()

        if entity is None:
            raise ValueError(f"Entity with id {id} not found")

        await self.session.delete(entity)
        await self.session.flush()

    async def restore(self, id: uuid.UUID) -> T:
        """Restore soft-deleted entity.

        Args:
            id: UUID of the entity to restore

        Returns:
            Restored entity

        Raises:
            ValueError: If entity not found or not deleted

        Example:
            ```python
            restored = await repository.restore(recipe_id)
            ```
        """
        # Get entity including soft-deleted
        stmt = select(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        entity = result.scalar_one_or_none()

        if entity is None:
            raise ValueError(f"Entity with id {id} not found")

        if entity.deleted_at is None:
            raise ValueError(f"Entity with id {id} is not deleted")

        entity.deleted_at = None
        entity.updated_at = datetime.utcnow()

        await self.session.flush()
        await self.session.refresh(entity)
        return entity
