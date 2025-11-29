"""API client for database seeding operations."""

import asyncio
import logging
from typing import Any
from uuid import UUID

import httpx
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class SeederReport(BaseModel):
    """Report of seeding operation results."""

    total_attempted: int = Field(..., description="Total recipes attempted to seed")
    total_succeeded: int = Field(..., description="Successfully seeded recipes")
    total_failed: int = Field(..., description="Failed recipe creations")
    failed_recipes: list[dict[str, Any]] = Field(
        default_factory=list, description="Details of failed recipes"
    )
    duration_seconds: float = Field(..., description="Total seeding duration")
    average_time_per_recipe: float = Field(
        ..., description="Average time per recipe in seconds"
    )
    created_recipe_ids: list[UUID] = Field(
        default_factory=list, description="IDs of successfully created recipes"
    )


class ValidationReport(BaseModel):
    """Report of post-seeding validation."""

    recipe_count_valid: bool = Field(..., description="Recipe count matches expected")
    search_functional: bool = Field(..., description="Search is working")
    embeddings_generated: bool = Field(
        ..., description="Embeddings were generated"
    )
    sample_queries_tested: int = Field(..., description="Number of queries tested")
    validation_errors: list[str] = Field(
        default_factory=list, description="Any validation errors"
    )
    overall_success: bool = Field(..., description="Overall validation success")


class SeederAPIClient:
    """Client for interacting with Recipe Management API during seeding."""

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize seeder API client.

        Args:
            base_url: Base URL of the API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.client: httpx.AsyncClient | None = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={"Content-Type": "application/json"},
            trust_env=False,  # Don't use proxy env vars for localhost
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    async def _retry_request(
        self,
        method: str,
        endpoint: str,
        **kwargs,
    ) -> httpx.Response:
        """Execute request with retry logic.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters

        Returns:
            Response object

        Raises:
            httpx.HTTPError: If all retries fail
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(method, endpoint, **kwargs)
                response.raise_for_status()
                return response
            except httpx.HTTPError as e:
                last_error = e
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}"
                )

                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                else:
                    logger.error(f"All retry attempts failed for {endpoint}")

        raise last_error

    async def create_recipe(self, recipe_data: dict[str, Any]) -> dict[str, Any] | None:
        """Create a single recipe.

        Args:
            recipe_data: Recipe data dictionary

        Returns:
            Created recipe data or None if failed
        """
        try:
            response = await self._retry_request(
                "POST",
                "/api/recipes",
                json=recipe_data,
            )
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Failed to create recipe '{recipe_data.get('name')}': {e}")
            return None

    async def create_recipe_batch(
        self, recipes: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Create multiple recipes in batch.

        Args:
            recipes: List of recipe data dictionaries

        Returns:
            List of results with success/failure info
        """
        results = []

        # Create tasks for concurrent execution
        tasks = [self.create_recipe(recipe) for recipe in recipes]

        # Execute with progress tracking
        for i, task in enumerate(asyncio.as_completed(tasks), 1):
            result = await task
            results.append(result)
            logger.info(f"Processed {i}/{len(recipes)} recipes")

        return results

    async def verify_recipe_exists(self, recipe_id: UUID) -> bool:
        """Verify a recipe exists by ID.

        Args:
            recipe_id: Recipe UUID

        Returns:
            True if recipe exists, False otherwise
        """
        try:
            response = await self._retry_request("GET", f"/api/recipes/{recipe_id}")
            return response.status_code == 200
        except httpx.HTTPError:
            return False

    async def get_recipe_count(self) -> int:
        """Get total number of recipes in database.

        Returns:
            Number of recipes
        """
        try:
            response = await self._retry_request(
                "GET", "/api/recipes", params={"limit": 1}
            )
            data = response.json()
            return data.get("total", 0)
        except httpx.HTTPError as e:
            logger.error(f"Failed to get recipe count: {e}")
            return 0

    async def search_recipes(
        self, query: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """Search for recipes using hybrid search.

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of recipe results
        """
        try:
            response = await self._retry_request(
                "POST",
                "/api/search",
                json={"query": query, "limit": limit},
            )
            data = response.json()
            return data.get("results", [])
        except httpx.HTTPError as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []

    async def trigger_embedding_generation(
        self, recipe_ids: list[UUID]
    ) -> dict[str, Any]:
        """Trigger embedding generation for recipes.

        Note: This might be handled automatically by the API workflow.

        Args:
            recipe_ids: List of recipe IDs

        Returns:
            Status of embedding generation
        """
        # For this implementation, embeddings are generated automatically
        # during recipe creation via LangGraph workflow
        logger.info(
            f"Embeddings should be auto-generated for {len(recipe_ids)} recipes"
        )
        return {"status": "auto_generated", "recipe_count": len(recipe_ids)}

    async def verify_search_indexing(
        self, sample_queries: list[str]
    ) -> tuple[bool, list[dict[str, Any]]]:
        """Verify search functionality with sample queries.

        Args:
            sample_queries: List of test queries

        Returns:
            Tuple of (all_successful, results)
        """
        results = []
        all_successful = True

        for query in sample_queries:
            search_results = await self.search_recipes(query, limit=5)
            success = len(search_results) > 0

            results.append(
                {
                    "query": query,
                    "success": success,
                    "result_count": len(search_results),
                }
            )

            if not success:
                all_successful = False
                logger.warning(f"Search query '{query}' returned no results")

        return all_successful, results

    async def get_health_status(self) -> dict[str, Any]:
        """Check API health status.

        Returns:
            Health status information
        """
        try:
            response = await self._retry_request("GET", "/health")
            return response.json()
        except httpx.HTTPError as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def cleanup_test_data(self, tag: str = None) -> int:
        """Clean up test data (if supported by API).

        Args:
            tag: Optional tag to identify test data

        Returns:
            Number of records deleted
        """
        # This would require API endpoint support
        # For now, we'll log that cleanup is not implemented
        logger.warning("Cleanup endpoint not implemented - manual cleanup required")
        return 0
