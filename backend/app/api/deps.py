"""Dependency injection for FastAPI endpoints.

Provides reusable dependencies for:
- Database sessions
- Redis clients
- Service instances
- Pagination parameters
- Authentication (future)
"""

from typing import Annotated
from uuid import UUID

from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.gemini_client import GeminiClient
from app.db.redis_client import RedisClient, get_redis
from app.db.session import get_db
from app.repositories.pagination import Pagination
from app.repositories.recipe import RecipeRepository
from app.repositories.vector import VectorRepository
from app.schemas.recipe import RecipeFilters
from app.services.cache import CacheService
from app.services.embedding import EmbeddingService
from app.services.recipe import RecipeService
from app.services.search import SearchService


# ==================== Core Dependencies ====================


async def get_recipe_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> RecipeRepository:
    """Get recipe repository instance.

    Args:
        db: Database session

    Returns:
        RecipeRepository instance
    """
    return RecipeRepository(db)


async def get_vector_repository(
    db: Annotated[AsyncSession, Depends(get_db)]
) -> VectorRepository:
    """Get vector repository instance.

    Args:
        db: Database session

    Returns:
        VectorRepository instance
    """
    return VectorRepository(db)


async def get_cache_service(
    redis: Annotated[RedisClient, Depends(get_redis)]
) -> CacheService:
    """Get cache service instance.

    Args:
        redis: Redis client

    Returns:
        CacheService instance
    """
    return CacheService(redis)


async def get_gemini_client() -> GeminiClient:
    """Get Gemini client instance.

    Returns:
        GeminiClient instance
    """
    from app.config import get_settings

    settings = get_settings()
    return GeminiClient(
        api_key=settings.gemini_api_key,
        embedding_model=settings.gemini_embedding_model,
        text_model=settings.gemini_text_model,
        rate_limit_rpm=settings.gemini_rate_limit_rpm,
        timeout=settings.gemini_timeout,
        max_retries=settings.gemini_max_retries,
    )


async def get_embedding_service(
    gemini: Annotated[GeminiClient, Depends(get_gemini_client)],
    cache: Annotated[CacheService, Depends(get_cache_service)],
) -> EmbeddingService:
    """Get embedding service instance.

    Args:
        gemini: Gemini API client
        cache: Cache service

    Returns:
        EmbeddingService instance
    """
    return EmbeddingService(gemini, cache)


# ==================== Business Service Dependencies ====================


async def get_recipe_service(
    recipe_repo: Annotated[RecipeRepository, Depends(get_recipe_repository)],
    vector_repo: Annotated[VectorRepository, Depends(get_vector_repository)],
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RecipeService:
    """Get recipe service instance with all dependencies.

    Args:
        recipe_repo: Recipe repository
        vector_repo: Vector repository
        embedding_service: Embedding service
        cache_service: Cache service
        db: Database session

    Returns:
        RecipeService instance
    """
    return RecipeService(
        recipe_repo=recipe_repo,
        vector_repo=vector_repo,
        embedding_service=embedding_service,
        cache_service=cache_service,
        session=db,
    )


async def get_search_service(
    recipe_repo: Annotated[RecipeRepository, Depends(get_recipe_repository)],
    vector_repo: Annotated[VectorRepository, Depends(get_vector_repository)],
    embedding_service: Annotated[EmbeddingService, Depends(get_embedding_service)],
    gemini_client: Annotated[GeminiClient, Depends(get_gemini_client)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
) -> SearchService:
    """Get search service instance with all dependencies.

    Args:
        recipe_repo: Recipe repository
        vector_repo: Vector repository
        embedding_service: Embedding service
        gemini_client: Gemini API client
        cache_service: Cache service

    Returns:
        SearchService instance
    """
    return SearchService(
        recipe_repo=recipe_repo,
        vector_repo=vector_repo,
        embedding_service=embedding_service,
        gemini_client=gemini_client,
        cache_service=cache_service,
    )


# ==================== Pagination Dependencies ====================


async def get_pagination(
    page: Annotated[int, Query(ge=1, description="Page number (1-indexed)")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=100, description="Items per page (max 100)")
    ] = 10,
) -> Pagination:
    """Get pagination parameters from query string.

    Args:
        page: Page number (1-indexed)
        page_size: Items per page

    Returns:
        Pagination instance with offset/limit calculated from page parameters
    """
    # Convert page-based pagination to offset-based
    offset = (page - 1) * page_size
    return Pagination(offset=offset, limit=page_size)


async def get_recipe_filters(
    name: Annotated[str | None, Query(description="Filter by name (partial match)")] = None,
    cuisine_type: Annotated[str | None, Query(description="Filter by cuisine type")] = None,
    difficulty: Annotated[str | None, Query(description="Filter by difficulty (easy/medium/hard)")] = None,
    diet_types: Annotated[list[str] | None, Query(description="Filter by diet types")] = None,
    category_ids: Annotated[list[UUID] | None, Query(description="Filter by category IDs")] = None,
    min_prep_time: Annotated[int | None, Query(ge=0, description="Minimum prep time (minutes)")] = None,
    max_prep_time: Annotated[int | None, Query(ge=0, description="Maximum prep time (minutes)")] = None,
    min_cook_time: Annotated[int | None, Query(ge=0, description="Minimum cook time (minutes)")] = None,
    max_cook_time: Annotated[int | None, Query(ge=0, description="Maximum cook time (minutes)")] = None,
    min_servings: Annotated[int | None, Query(gt=0, description="Minimum servings")] = None,
    max_servings: Annotated[int | None, Query(gt=0, description="Maximum servings")] = None,
) -> RecipeFilters:
    """Get recipe filters from query parameters.

    Args:
        name: Filter by name (partial match)
        cuisine_type: Filter by cuisine type
        difficulty: Filter by difficulty level
        diet_types: Filter by diet types (any match)
        category_ids: Filter by category IDs
        min_prep_time: Minimum prep time in minutes
        max_prep_time: Maximum prep time in minutes
        min_cook_time: Minimum cook time in minutes
        max_cook_time: Maximum cook time in minutes
        min_servings: Minimum servings
        max_servings: Maximum servings

    Returns:
        RecipeFilters instance
    """
    from app.db.models import DifficultyLevel

    # Convert difficulty string to enum if provided
    difficulty_enum = None
    if difficulty:
        try:
            difficulty_enum = DifficultyLevel(difficulty.lower())
        except ValueError:
            pass  # Invalid difficulty will be handled by validation

    return RecipeFilters(
        name=name,
        cuisine_type=cuisine_type,
        difficulty=difficulty_enum,
        diet_types=diet_types or [],
        category_ids=category_ids or [],
        min_prep_time=min_prep_time,
        max_prep_time=max_prep_time,
        min_cook_time=min_cook_time,
        max_cook_time=max_cook_time,
        min_servings=min_servings,
        max_servings=max_servings,
    )
