"""Recipe endpoints for CRUD operations and bulk import.

Implements:
- POST /recipes - Create new recipe
- GET /recipes - List recipes with filters and pagination
- GET /recipes/{id} - Get single recipe by ID
- PUT /recipes/{id} - Update existing recipe
- DELETE /recipes/{id} - Delete recipe (soft delete)
- POST /recipes/bulk - Bulk import recipes (background task)
- GET /recipes/{id}/similar - Find similar recipes
"""

import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, UploadFile, File, status
from pydantic import ValidationError

from app.api.deps import (
    get_pagination,
    get_recipe_filters,
    get_recipe_service,
    get_search_service,
)
from app.repositories.pagination import Pagination
from app.schemas.recipe import (
    RecipeCreate,
    RecipeFilters,
    RecipeListResponse,
    RecipeResponse,
    RecipeUpdate,
)
from app.schemas.search import SearchResult
from app.services.recipe import RecipeService
from app.services.search import SearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post(
    "",
    response_model=RecipeResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new recipe",
    description="Create a new recipe with ingredients, categories, and nutritional info",
)
async def create_recipe(
    recipe: RecipeCreate,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeResponse:
    """Create a new recipe.

    Args:
        recipe: Recipe creation data
        service: Recipe service instance

    Returns:
        Created recipe with generated ID and timestamps

    Raises:
        HTTPException 400: If validation fails
        HTTPException 500: If creation fails
    """
    try:
        logger.info(f"Creating recipe: {recipe.name}")
        created_recipe = await service.create_recipe(recipe)
        logger.info(f"Recipe created successfully: {created_recipe.id}")
        return created_recipe

    except ValueError as exc:
        logger.error(f"Recipe creation validation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error(f"Recipe creation failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create recipe",
        )


@router.get(
    "",
    response_model=RecipeListResponse,
    summary="List recipes",
    description="List recipes with optional filters and pagination",
)
async def list_recipes(
    filters: Annotated[RecipeFilters, Depends(get_recipe_filters)],
    pagination: Annotated[Pagination, Depends(get_pagination)],
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeListResponse:
    """List recipes with filters and pagination.

    Args:
        filters: Recipe filter parameters
        pagination: Pagination parameters
        service: Recipe service instance

    Returns:
        Paginated list of recipes matching filters
    """
    try:
        logger.info(
            f"Listing recipes with filters: {filters.model_dump(exclude_none=True)}, "
            f"offset: {pagination.offset}, limit: {pagination.limit}"
        )

        # Convert filters to dictionary
        filter_dict = filters.model_dump(exclude_none=True)

        # Get recipes and total count
        recipes = await service.list_recipes(filter_dict, pagination)

        # Get accurate total count using service method
        total_count = await service.count_recipes(filter_dict)

        # Build response with correct pagination fields
        response = RecipeListResponse(
            items=recipes,
            total=total_count,
            skip=pagination.offset,
            limit=pagination.limit,
            has_more=(pagination.offset + len(recipes)) < total_count,
        )

        logger.info(f"Found {len(recipes)} recipes")
        return response

    except Exception as exc:
        logger.error(f"Recipe listing failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list recipes",
        )


@router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get recipe by ID",
    description="Retrieve a single recipe by its UUID",
)
async def get_recipe(
    recipe_id: UUID,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeResponse:
    """Get recipe by ID.

    Args:
        recipe_id: Recipe UUID
        service: Recipe service instance

    Returns:
        Recipe details

    Raises:
        HTTPException 404: If recipe not found
    """
    try:
        logger.info(f"Getting recipe: {recipe_id}")
        recipe = await service.get_recipe(recipe_id)
        return recipe

    except ValueError as exc:
        logger.error(f"Recipe not found: {recipe_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error(f"Failed to get recipe {recipe_id}: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve recipe",
        )


@router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Update recipe",
    description="Update an existing recipe (partial updates supported)",
)
async def update_recipe(
    recipe_id: UUID,
    updates: RecipeUpdate,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> RecipeResponse:
    """Update an existing recipe.

    Args:
        recipe_id: Recipe UUID
        updates: Recipe update data (partial)
        service: Recipe service instance

    Returns:
        Updated recipe

    Raises:
        HTTPException 404: If recipe not found
        HTTPException 400: If validation fails
    """
    try:
        logger.info(f"Updating recipe: {recipe_id}")
        updated_recipe = await service.update_recipe(recipe_id, updates)
        logger.info(f"Recipe updated successfully: {recipe_id}")
        return updated_recipe

    except ValueError as exc:
        # Could be not found or validation error
        error_msg = str(exc)
        if "not found" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error_msg,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg,
            )
    except Exception as exc:
        logger.error(f"Recipe update failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update recipe",
        )


@router.delete(
    "/{recipe_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete recipe",
    description="Soft delete a recipe by marking it as deleted",
)
async def delete_recipe(
    recipe_id: UUID,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> None:
    """Delete a recipe (soft delete).

    Args:
        recipe_id: Recipe UUID
        service: Recipe service instance

    Raises:
        HTTPException 404: If recipe not found
    """
    try:
        logger.info(f"Deleting recipe: {recipe_id}")
        await service.delete_recipe(recipe_id)
        logger.info(f"Recipe deleted successfully: {recipe_id}")

    except ValueError as exc:
        logger.error(f"Recipe not found for deletion: {recipe_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error(f"Recipe deletion failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete recipe",
        )


@router.get(
    "/{recipe_id}/similar",
    response_model=list[SearchResult],
    summary="Find similar recipes",
    description="Find recipes similar to the given recipe using vector embeddings",
)
async def find_similar_recipes(
    recipe_id: UUID,
    recipe_service: Annotated[RecipeService, Depends(get_recipe_service)],
    search_service: Annotated[SearchService, Depends(get_search_service)],
    limit: int = 10,
) -> list[SearchResult]:
    """Find similar recipes based on vector similarity.

    Args:
        recipe_id: Recipe UUID to find similar recipes for
        limit: Maximum number of similar recipes to return
        recipe_service: Recipe service instance
        search_service: Search service instance

    Returns:
        List of similar recipes with similarity scores

    Raises:
        HTTPException 404: If recipe not found
    """
    try:
        logger.info(f"Finding similar recipes for: {recipe_id}")

        # Get the source recipe
        recipe = await recipe_service.get_recipe(recipe_id)

        # Use the recipe name and description for semantic search
        search_query = f"{recipe.name} {recipe.description or ''}"

        # Perform semantic search
        results = await search_service.semantic_search(search_query, limit=limit + 1)

        # Filter out the source recipe and build response
        similar_results = []
        for recipe_result, score in results:
            if recipe_result.id != recipe_id:
                similar_results.append(
                    SearchResult(
                        recipe=search_service._recipe_to_response(recipe_result),
                        score=score,
                        distance=1 - score,  # Convert similarity to distance
                        match_type="semantic",
                    )
                )

            if len(similar_results) >= limit:
                break

        logger.info(f"Found {len(similar_results)} similar recipes")
        return similar_results

    except ValueError as exc:
        logger.error(f"Recipe not found: {recipe_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error(f"Similar recipe search failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to find similar recipes",
        )


# Background task for bulk import
async def process_bulk_import(
    recipes_data: list[dict],
    service: RecipeService,
    job_id: str,
) -> None:
    """Background task to process bulk recipe import.

    Args:
        recipes_data: List of recipe dictionaries to import
        service: Recipe service instance
        job_id: Unique job identifier for tracking
    """
    logger.info(f"Starting bulk import job {job_id} with {len(recipes_data)} recipes")

    success_count = 0
    error_count = 0
    errors = []

    for idx, recipe_dict in enumerate(recipes_data):
        try:
            # Validate and create recipe
            recipe_create = RecipeCreate(**recipe_dict)
            await service.create_recipe(recipe_create)
            success_count += 1

        except (ValidationError, ValueError) as exc:
            error_count += 1
            errors.append({
                "index": idx,
                "recipe": recipe_dict.get("name", "unknown"),
                "error": str(exc),
            })
            logger.warning(f"Failed to import recipe {idx}: {exc}")

        except Exception as exc:
            error_count += 1
            errors.append({
                "index": idx,
                "recipe": recipe_dict.get("name", "unknown"),
                "error": f"Unexpected error: {str(exc)}",
            })
            logger.error(f"Unexpected error importing recipe {idx}: {exc}")

    logger.info(
        f"Bulk import job {job_id} completed: "
        f"{success_count} success, {error_count} errors"
    )

    # TODO: Store results in cache/database for job status retrieval
    # For now, just log completion


@router.post(
    "/bulk",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Bulk import recipes",
    description="Import multiple recipes from JSON file (processed in background)",
)
async def bulk_import_recipes(
    file: Annotated[UploadFile, File(description="JSON file with recipe array")],
    background_tasks: BackgroundTasks,
    service: Annotated[RecipeService, Depends(get_recipe_service)],
) -> dict:
    """Bulk import recipes from JSON file.

    Args:
        file: Uploaded JSON file with array of recipes
        background_tasks: FastAPI background tasks
        service: Recipe service instance

    Returns:
        Job ID for tracking import progress

    Raises:
        HTTPException 400: If file format is invalid
    """
    try:
        # Validate file type
        if not file.filename or not file.filename.endswith(".json"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be a JSON file",
            )

        # Read and parse JSON
        content = await file.read()
        import json

        try:
            recipes_data = json.loads(content)
        except json.JSONDecodeError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON format: {str(exc)}",
            )

        # Validate it's a list
        if not isinstance(recipes_data, list):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="JSON must contain an array of recipes",
            )

        # Generate job ID
        import uuid
        job_id = str(uuid.uuid4())

        # Queue background task
        background_tasks.add_task(
            process_bulk_import,
            recipes_data,
            service,
            job_id,
        )

        logger.info(f"Queued bulk import job {job_id} with {len(recipes_data)} recipes")

        return {
            "job_id": job_id,
            "status": "accepted",
            "total_recipes": len(recipes_data),
            "message": "Bulk import started. Results will be processed in the background.",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"Bulk import failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start bulk import",
        )
