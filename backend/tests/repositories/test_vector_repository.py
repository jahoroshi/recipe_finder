"""Tests for vector repository.

Note: These tests use SQLite which doesn't support pgvector.
For full vector search testing, use PostgreSQL with pgvector extension.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.pagination import Pagination
from app.repositories.vector import VectorRepository
from tests.repositories.conftest import Recipe


class TestVectorRepository:
    """Test vector repository operations.

    Note: Most vector operations require PostgreSQL with pgvector.
    These tests focus on basic functionality that works with SQLite.
    """

    @pytest.mark.asyncio
    async def test_initialization(self, db_session: AsyncSession):
        """Test vector repository initialization."""
        repo = VectorRepository(db_session)
        assert repo.session == db_session

    @pytest.mark.asyncio
    async def test_similarity_search_validates_dimension(
        self, db_session: AsyncSession
    ):
        """Test similarity search validates embedding dimension."""
        repo = VectorRepository(db_session)

        with pytest.raises(ValueError, match="must be 768 dimensions"):
            await repo.similarity_search([0.1] * 100, limit=10)

    @pytest.mark.asyncio
    async def test_similarity_search_invalid_metric(
        self, db_session: AsyncSession
    ):
        """Test similarity search with invalid distance metric."""
        repo = VectorRepository(db_session)

        embedding = [0.1] * 768

        with pytest.raises(ValueError, match="Invalid distance metric"):
            await repo.similarity_search(
                embedding, limit=10, distance_metric="invalid"
            )

    @pytest.mark.asyncio
    async def test_hybrid_search_validates_dimension(
        self, db_session: AsyncSession
    ):
        """Test hybrid search validates embedding dimension."""
        repo = VectorRepository(db_session)

        with pytest.raises(ValueError, match="must be 768 dimensions"):
            await repo.hybrid_search([0.1] * 100, limit=10)

    @pytest.mark.asyncio
    async def test_hybrid_search_invalid_metric(
        self, db_session: AsyncSession
    ):
        """Test hybrid search with invalid distance metric."""
        repo = VectorRepository(db_session)

        embedding = [0.1] * 768

        with pytest.raises(ValueError, match="Invalid distance metric"):
            await repo.hybrid_search(
                embedding, limit=10, distance_metric="invalid"
            )

    @pytest.mark.asyncio
    async def test_find_similar_recipes_nonexistent(
        self, db_session: AsyncSession
    ):
        """Test finding similar recipes for nonexistent recipe."""
        repo = VectorRepository(db_session)

        with pytest.raises(ValueError, match="not found or is deleted"):
            await repo.find_similar_recipes(uuid.uuid4(), limit=10)

    @pytest.mark.asyncio
    async def test_find_similar_recipes_no_embedding(
        self, db_session: AsyncSession, sample_recipe: Recipe
    ):
        """Test finding similar recipes when recipe has no embedding."""
        repo = VectorRepository(db_session)

        with pytest.raises(ValueError, match="has no embedding"):
            await repo.find_similar_recipes(sample_recipe.id, limit=10)

    @pytest.mark.asyncio
    async def test_batch_update_embeddings_validates_dimension(
        self, db_session: AsyncSession, sample_recipe: Recipe
    ):
        """Test batch update validates embedding dimensions."""
        repo = VectorRepository(db_session)

        updates = [{"id": sample_recipe.id, "embedding": [0.1] * 100}]

        with pytest.raises(ValueError, match="must be 768 dimensions"):
            await repo.batch_update_embeddings(updates)

    @pytest.mark.asyncio
    async def test_batch_update_embeddings_missing_keys(
        self, db_session: AsyncSession, sample_recipe: Recipe
    ):
        """Test batch update validates required keys."""
        repo = VectorRepository(db_session)

        # Missing 'embedding'
        updates = [{"id": sample_recipe.id}]

        with pytest.raises(ValueError, match="must contain 'id' and 'embedding'"):
            await repo.batch_update_embeddings(updates)

        # Missing 'id'
        updates = [{"embedding": [0.1] * 768}]

        with pytest.raises(ValueError, match="must contain 'id' and 'embedding'"):
            await repo.batch_update_embeddings(updates)

    @pytest.mark.asyncio
    async def test_get_recipes_without_embeddings(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test getting recipes without embeddings."""
        repo = VectorRepository(db_session)

        results = await repo.get_recipes_without_embeddings()

        # All sample recipes don't have embeddings
        assert len(results) == len(sample_recipes)
        assert all(r.embedding is None for r in results)

    @pytest.mark.asyncio
    async def test_get_recipes_without_embeddings_pagination(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test getting recipes without embeddings with pagination."""
        repo = VectorRepository(db_session)

        pagination = Pagination(offset=0, limit=1)
        results = await repo.get_recipes_without_embeddings(pagination=pagination)

        assert len(results) == 1

    @pytest.mark.asyncio
    async def test_get_recipes_without_embeddings_after_update(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test that recipes with embeddings are excluded."""
        repo = VectorRepository(db_session)

        # Give one recipe an embedding
        sample_recipes[0].embedding = [0.1] * 768
        await db_session.commit()

        results = await repo.get_recipes_without_embeddings()

        # Should be one less now
        assert len(results) == len(sample_recipes) - 1
        assert sample_recipes[0].id not in [r.id for r in results]

    @pytest.mark.asyncio
    async def test_count_recipes_with_embeddings_none(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test counting when no recipes have embeddings."""
        repo = VectorRepository(db_session)

        with_emb, without_emb = await repo.count_recipes_with_embeddings()

        assert with_emb == 0
        assert without_emb == len(sample_recipes)

    @pytest.mark.asyncio
    async def test_count_recipes_with_embeddings_some(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test counting when some recipes have embeddings."""
        repo = VectorRepository(db_session)

        # Give embeddings to first two recipes
        sample_recipes[0].embedding = [0.1] * 768
        sample_recipes[1].embedding = [0.2] * 768
        await db_session.commit()

        with_emb, without_emb = await repo.count_recipes_with_embeddings()

        assert with_emb == 2
        assert without_emb == len(sample_recipes) - 2

    @pytest.mark.asyncio
    async def test_count_recipes_with_embeddings_all(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test counting when all recipes have embeddings."""
        repo = VectorRepository(db_session)

        # Give embeddings to all recipes
        for i, recipe in enumerate(sample_recipes):
            recipe.embedding = [float(i)] * 768

        await db_session.commit()

        with_emb, without_emb = await repo.count_recipes_with_embeddings()

        assert with_emb == len(sample_recipes)
        assert without_emb == 0

    @pytest.mark.asyncio
    async def test_distance_metrics_parameter_accepted(
        self, db_session: AsyncSession
    ):
        """Test that different distance metrics are accepted."""
        repo = VectorRepository(db_session)
        embedding = [0.1] * 768

        # These should not raise errors for validation
        # (they will fail on SQLite due to missing pgvector, but that's expected)

        metrics = ["cosine", "l2", "inner_product"]

        for metric in metrics:
            try:
                await repo.similarity_search(embedding, limit=10, distance_metric=metric)
            except Exception as e:
                # SQLite won't support the vector operations, but validation should pass
                # Only check that it's not a ValueError about invalid metric
                if "Invalid distance metric" in str(e):
                    pytest.fail(f"Valid metric '{metric}' was rejected")


@pytest.mark.skipif(
    True,  # Skip by default as these require PostgreSQL
    reason="Requires PostgreSQL with pgvector extension"
)
class TestVectorRepositoryWithPgVector:
    """Tests that require actual pgvector support.

    These tests should be run against a PostgreSQL database with pgvector.
    """

    @pytest.mark.asyncio
    async def test_similarity_search_cosine(
        self, db_session: AsyncSession, recipes_with_embeddings: list[Recipe]
    ):
        """Test cosine similarity search."""
        repo = VectorRepository(db_session)

        query_embedding = [0.1] * 768
        results = await repo.similarity_search(
            query_embedding, limit=10, distance_metric="cosine"
        )

        assert isinstance(results, list)
        assert all(isinstance(item, tuple) for item in results)
        assert all(isinstance(item[0], Recipe) for item in results)
        assert all(isinstance(item[1], float) for item in results)

    @pytest.mark.asyncio
    async def test_similarity_search_l2(
        self, db_session: AsyncSession, recipes_with_embeddings: list[Recipe]
    ):
        """Test L2 distance similarity search."""
        repo = VectorRepository(db_session)

        query_embedding = [0.1] * 768
        results = await repo.similarity_search(
            query_embedding, limit=10, distance_metric="l2"
        )

        assert isinstance(results, list)
        assert len(results) <= 10

    @pytest.mark.asyncio
    async def test_hybrid_search_with_filters(
        self, db_session: AsyncSession, recipes_with_embeddings: list[Recipe]
    ):
        """Test hybrid search with additional filters."""
        repo = VectorRepository(db_session)

        query_embedding = [0.1] * 768
        filters = {"cuisine_type": "Italian"}

        results = await repo.hybrid_search(
            query_embedding, filters=filters, limit=10
        )

        assert all(recipe.cuisine_type == "Italian" for recipe, _ in results)

    @pytest.mark.asyncio
    async def test_find_similar_recipes_excludes_self(
        self, db_session: AsyncSession, recipes_with_embeddings: list[Recipe]
    ):
        """Test that find_similar_recipes excludes the reference recipe."""
        repo = VectorRepository(db_session)

        reference_recipe = recipes_with_embeddings[0]
        similar = await repo.find_similar_recipes(reference_recipe.id, limit=10)

        assert reference_recipe.id not in [recipe.id for recipe, _ in similar]

    @pytest.mark.asyncio
    async def test_batch_update_embeddings(
        self, db_session: AsyncSession, sample_recipes: list[Recipe]
    ):
        """Test batch updating embeddings."""
        repo = VectorRepository(db_session)

        updates = [
            {"id": sample_recipes[0].id, "embedding": [0.1] * 768},
            {"id": sample_recipes[1].id, "embedding": [0.2] * 768},
        ]

        await repo.batch_update_embeddings(updates)

        # Verify updates
        await db_session.refresh(sample_recipes[0])
        await db_session.refresh(sample_recipes[1])

        assert sample_recipes[0].embedding is not None
        assert sample_recipes[1].embedding is not None

    @pytest.mark.asyncio
    async def test_reindex_embeddings(
        self, db_session: AsyncSession, recipes_with_embeddings: list[Recipe]
    ):
        """Test clearing all embeddings for reindexing."""
        repo = VectorRepository(db_session)

        cleared_count = await repo.reindex_embeddings()

        assert cleared_count > 0

        # Verify embeddings are cleared
        for recipe in recipes_with_embeddings:
            await db_session.refresh(recipe)
            assert recipe.embedding is None
