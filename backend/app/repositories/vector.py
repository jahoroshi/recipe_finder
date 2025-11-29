"""Vector search repository using pgvector for semantic similarity."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Recipe
from app.repositories.pagination import Pagination


class VectorRepository:
    """Repository for vector similarity search operations using pgvector.

    Implements semantic search using cosine similarity, L2 distance,
    and inner product distance operators provided by pgvector extension.

    Distance Operators:
        <->  : L2 distance (Euclidean)
        <#>  : Negative inner product
        <=>  : Cosine distance

    Example:
        ```python
        async with get_db() as session:
            repo = VectorRepository(session)
            similar = await repo.similarity_search(query_embedding, limit=10)
        ```
    """

    def __init__(self, session: AsyncSession):
        """Initialize vector repository.

        Args:
            session: Async database session
        """
        self.session = session

    async def similarity_search(
        self,
        embedding: list[float],
        limit: int = 10,
        distance_metric: str = "cosine",
    ) -> list[tuple[Recipe, float]]:
        """Find most similar recipes using vector similarity.

        Args:
            embedding: Query embedding vector (768 dimensions)
            limit: Maximum number of results to return
            distance_metric: Distance metric to use ("cosine", "l2", or "inner_product")

        Returns:
            List of (Recipe, distance) tuples ordered by similarity

        Raises:
            ValueError: If embedding dimension mismatch or invalid metric

        Example:
            ```python
            query_embedding = generate_embedding("pasta carbonara")
            results = await repo.similarity_search(query_embedding, limit=5)
            for recipe, distance in results:
                print(f"{recipe.name}: {distance}")
            ```
        """
        if len(embedding) != 768:
            raise ValueError(f"Embedding must be 768 dimensions, got {len(embedding)}")

        # Select distance operator based on metric
        if distance_metric == "cosine":
            distance_op = "<=>"
        elif distance_metric == "l2":
            distance_op = "<->"
        elif distance_metric == "inner_product":
            distance_op = "<#>"
        else:
            raise ValueError(
                f"Invalid distance metric: {distance_metric}. "
                "Must be 'cosine', 'l2', or 'inner_product'"
            )

        # Build query with vector distance
        stmt = text(
            f"""
            SELECT id, name, description, instructions, prep_time, cook_time,
                   servings, difficulty, cuisine_type, diet_types, embedding,
                   created_at, updated_at, deleted_at, created_by, updated_by,
                   embedding {distance_op} :embedding AS distance
            FROM recipes
            WHERE deleted_at IS NULL
              AND embedding IS NOT NULL
            ORDER BY distance
            LIMIT :limit
            """
        )

        result = await self.session.execute(
            stmt, {"embedding": str(embedding), "limit": limit}
        )

        # Convert rows to Recipe objects with distance
        recipes_with_distance = []
        for row in result.all():
            recipe = Recipe(
                id=row.id,
                name=row.name,
                description=row.description,
                instructions=row.instructions,
                prep_time=row.prep_time,
                cook_time=row.cook_time,
                servings=row.servings,
                difficulty=row.difficulty,
                cuisine_type=row.cuisine_type,
                diet_types=row.diet_types,
                embedding=row.embedding,
                created_at=row.created_at,
                updated_at=row.updated_at,
                deleted_at=row.deleted_at,
                created_by=row.created_by,
                updated_by=row.updated_by,
            )
            recipes_with_distance.append((recipe, row.distance))

        return recipes_with_distance

    async def hybrid_search(
        self,
        embedding: list[float],
        filters: dict[str, Any] | None = None,
        limit: int = 10,
        distance_metric: str = "cosine",
    ) -> list[tuple[Recipe, float]]:
        """Hybrid search combining vector similarity with attribute filters.

        Args:
            embedding: Query embedding vector (768 dimensions)
            filters: Additional filters (e.g., {"cuisine_type": "Italian"})
            limit: Maximum number of results to return
            distance_metric: Distance metric to use

        Returns:
            List of (Recipe, distance) tuples matching filters and similarity

        Example:
            ```python
            # Find similar Italian recipes
            results = await repo.hybrid_search(
                embedding,
                filters={"cuisine_type": "Italian", "difficulty": DifficultyLevel.EASY},
                limit=10
            )
            ```
        """
        if len(embedding) != 768:
            raise ValueError(f"Embedding must be 768 dimensions, got {len(embedding)}")

        # Select distance operator
        if distance_metric == "cosine":
            distance_op = "<=>"
        elif distance_metric == "l2":
            distance_op = "<->"
        elif distance_metric == "inner_product":
            distance_op = "<#>"
        else:
            raise ValueError(f"Invalid distance metric: {distance_metric}")

        # Start with base query
        stmt = select(Recipe).where(
            and_(Recipe.deleted_at.is_(None), Recipe.embedding.isnot(None))
        )

        # Apply filters
        if filters:
            for key, value in filters.items():
                if hasattr(Recipe, key):
                    column = getattr(Recipe, key)
                    if isinstance(value, list):
                        stmt = stmt.where(column.in_(value))
                    else:
                        stmt = stmt.where(column == value)

        # Add distance calculation and ordering
        stmt = stmt.add_columns(
            Recipe.embedding.op(distance_op)(embedding).label("distance")
        ).order_by(text("distance"))

        stmt = stmt.limit(limit)

        result = await self.session.execute(stmt)
        recipes_with_distance = [(row[0], row[1]) for row in result.all()]
        return recipes_with_distance

    async def find_similar_recipes(
        self,
        recipe_id: uuid.UUID,
        limit: int = 10,
        distance_metric: str = "cosine",
    ) -> list[tuple[Recipe, float]]:
        """Find recipes similar to a given recipe.

        Args:
            recipe_id: UUID of the reference recipe
            limit: Maximum number of similar recipes to return
            distance_metric: Distance metric to use

        Returns:
            List of (Recipe, distance) tuples excluding the reference recipe

        Raises:
            ValueError: If recipe not found or has no embedding

        Example:
            ```python
            similar = await repo.find_similar_recipes(recipe_id, limit=5)
            for recipe, distance in similar:
                print(f"Similar: {recipe.name} (distance: {distance})")
            ```
        """
        # Get the reference recipe's embedding
        stmt = select(Recipe).where(
            Recipe.id == recipe_id, Recipe.deleted_at.is_(None)
        )
        result = await self.session.execute(stmt)
        reference_recipe = result.scalar_one_or_none()

        if reference_recipe is None:
            raise ValueError(f"Recipe with id {recipe_id} not found or is deleted")

        if reference_recipe.embedding is None:
            raise ValueError(f"Recipe with id {recipe_id} has no embedding")

        # Find similar recipes (excluding the reference recipe)
        similar_recipes = await self.similarity_search(
            reference_recipe.embedding,
            limit=limit + 1,  # +1 because reference will be in results
            distance_metric=distance_metric,
        )

        # Filter out the reference recipe itself
        return [
            (recipe, distance)
            for recipe, distance in similar_recipes
            if recipe.id != recipe_id
        ][:limit]

    async def batch_update_embeddings(
        self, updates: list[dict[str, Any]]
    ) -> None:
        """Batch update embeddings for multiple recipes efficiently.

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
            await repo.batch_update_embeddings(updates)
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

            # Update using raw SQL for efficiency
            stmt = text(
                """
                UPDATE recipes
                SET embedding = :embedding,
                    updated_at = NOW()
                WHERE id = :id AND deleted_at IS NULL
                """
            )

            await self.session.execute(
                stmt,
                {"id": update_data["id"], "embedding": str(embedding)},
            )

        await self.session.flush()

    async def reindex_embeddings(self) -> int:
        """Clear all embeddings to trigger re-indexing.

        Useful when switching embedding models or fixing corrupted embeddings.

        Returns:
            Number of recipes that had embeddings cleared

        Example:
            ```python
            cleared_count = await repo.reindex_embeddings()
            print(f"Cleared {cleared_count} embeddings")
            ```
        """
        stmt = text(
            """
            UPDATE recipes
            SET embedding = NULL,
                updated_at = NOW()
            WHERE deleted_at IS NULL
              AND embedding IS NOT NULL
            """
        )

        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.rowcount

    async def get_recipes_without_embeddings(
        self, pagination: Pagination | None = None
    ) -> list[Recipe]:
        """Get recipes that don't have embeddings yet.

        Useful for batch processing and embedding generation.

        Args:
            pagination: Optional pagination parameters

        Returns:
            List of recipes without embeddings

        Example:
            ```python
            pending = await repo.get_recipes_without_embeddings()
            for recipe in pending:
                embedding = generate_embedding(recipe)
                await repo.batch_update_embeddings([
                    {"id": recipe.id, "embedding": embedding}
                ])
            ```
        """
        stmt = select(Recipe).where(
            Recipe.deleted_at.is_(None), Recipe.embedding.is_(None)
        )

        if pagination:
            stmt = pagination.apply(stmt)

        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def count_recipes_with_embeddings(self) -> tuple[int, int]:
        """Count recipes with and without embeddings.

        Returns:
            Tuple of (count_with_embeddings, count_without_embeddings)

        Example:
            ```python
            with_emb, without_emb = await repo.count_recipes_with_embeddings()
            print(f"Indexed: {with_emb}, Pending: {without_emb}")
            ```
        """
        # Count with embeddings
        stmt_with = select(Recipe.id).where(
            Recipe.deleted_at.is_(None), Recipe.embedding.isnot(None)
        )
        result_with = await self.session.execute(stmt_with)
        count_with = len(result_with.all())

        # Count without embeddings
        stmt_without = select(Recipe.id).where(
            Recipe.deleted_at.is_(None), Recipe.embedding.is_(None)
        )
        result_without = await self.session.execute(stmt_without)
        count_without = len(result_without.all())

        return count_with, count_without
