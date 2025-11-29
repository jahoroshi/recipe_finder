"""Search endpoints for recipe discovery.

Implements:
- POST /search - Hybrid search with workflow execution
- POST /search/semantic - Pure semantic search
- POST /search/filter - Pure filter-based search
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_search_service
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search import SearchService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/search", tags=["search"])


@router.post(
    "",
    response_model=SearchResponse,
    summary="Hybrid recipe search",
    description="Search recipes using hybrid approach (semantic + filters)",
)
async def hybrid_search(
    request: SearchRequest,
    service: Annotated[SearchService, Depends(get_search_service)],
) -> SearchResponse:
    """Perform hybrid search combining semantic and filter-based approaches.

    This endpoint uses the LangGraph workflow to:
    1. Parse the query with Gemini to extract filters
    2. Perform semantic vector search
    3. Perform filter-based search
    4. Merge results using Reciprocal Rank Fusion
    5. Optionally rerank results

    Args:
        request: Search request with query and options
        service: Search service instance

    Returns:
        Search response with ranked results

    Raises:
        HTTPException 400: If query validation fails
        HTTPException 500: If search fails
    """
    try:
        logger.info(f"Hybrid search query: '{request.query}'")

        # Execute hybrid search
        results = await service.hybrid_search(request)

        logger.info(
            f"Hybrid search completed: {results.total} results, "
            f"type: {results.search_type}"
        )

        return results

    except ValueError as exc:
        logger.error(f"Search validation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error(f"Hybrid search failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Search operation failed",
        )


@router.post(
    "/semantic",
    response_model=list[dict],
    summary="Semantic search",
    description="Search recipes using vector embeddings (pure semantic search)",
)
async def semantic_search(
    service: Annotated[SearchService, Depends(get_search_service)],
    query: str,
    limit: int = 10,
) -> list[dict]:
    """Perform pure semantic search using vector embeddings.

    Args:
        query: Search query text
        limit: Maximum number of results
        service: Search service instance

    Returns:
        List of recipes with similarity scores

    Raises:
        HTTPException 400: If query is invalid
        HTTPException 500: If search fails
    """
    try:
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        logger.info(f"Semantic search query: '{query}'")

        # Execute semantic search
        results = await service.semantic_search(query, limit=limit)

        # Format response
        formatted_results = []
        for recipe, score in results:
            formatted_results.append({
                "recipe": service._recipe_to_response(recipe).model_dump(),
                "score": score,
                "distance": 1 - score,
                "match_type": "semantic",
            })

        logger.info(f"Semantic search completed: {len(formatted_results)} results")

        return formatted_results

    except ValueError as exc:
        logger.error(f"Semantic search validation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error(f"Semantic search failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Semantic search operation failed",
        )


@router.post(
    "/filter",
    response_model=list[dict],
    summary="Filter-based search",
    description="Search recipes using attribute filters",
)
async def filter_search(
    service: Annotated[SearchService, Depends(get_search_service)],
    filters: dict,
    limit: int = 10,
) -> list[dict]:
    """Perform pure filter-based search.

    Args:
        filters: Dictionary of filter criteria
        limit: Maximum number of results
        service: Search service instance

    Returns:
        List of recipes matching filters

    Raises:
        HTTPException 400: If filters are invalid
        HTTPException 500: If search fails
    """
    try:
        if not filters:
            raise ValueError("Filters cannot be empty")

        logger.info(f"Filter search with filters: {filters}")

        # Execute filter search
        results = await service.filter_search(filters, limit=limit)

        # Format response
        formatted_results = []
        for recipe, score in results:
            formatted_results.append({
                "recipe": service._recipe_to_response(recipe).model_dump(),
                "score": score,
                "match_type": "filter",
            })

        logger.info(f"Filter search completed: {len(formatted_results)} results")

        return formatted_results

    except ValueError as exc:
        logger.error(f"Filter search validation failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
    except Exception as exc:
        logger.error(f"Filter search failed: {exc}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Filter search operation failed",
        )
