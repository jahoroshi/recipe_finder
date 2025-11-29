"""Search service with hybrid search, query parsing, and result reranking."""

import asyncio
import json
from typing import Optional

from app.core.gemini_client import GeminiClient
from app.db.models import Recipe
from app.repositories.pagination import Pagination
from app.repositories.recipe import RecipeRepository
from app.repositories.vector import VectorRepository
from app.schemas.search import ParsedQuery, SearchRequest, SearchResponse, SearchResult
from app.services.cache import CacheService
from app.services.embedding import EmbeddingService


class SearchService:
    """Service for recipe search with hybrid strategies.

    Implements multiple search strategies:
        - Semantic search using vector embeddings
        - Filter-based search using recipe attributes
        - Hybrid search combining both approaches
        - Query understanding with Gemini
        - Result reranking for relevance

    Example:
        ```python
        service = SearchService(
            recipe_repo, vector_repo, embedding_service, gemini_client, cache_service
        )
        results = await service.hybrid_search(search_request)
        ```
    """

    def __init__(
        self,
        recipe_repo: RecipeRepository,
        vector_repo: VectorRepository,
        embedding_service: EmbeddingService,
        gemini_client: GeminiClient,
        cache_service: CacheService,
    ):
        """Initialize search service.

        Args:
            recipe_repo: Repository for recipe queries
            vector_repo: Repository for vector similarity search
            embedding_service: Service for generating embeddings
            gemini_client: Client for Gemini API text generation
            cache_service: Service for caching search results
        """
        self.recipe_repo = recipe_repo
        self.vector_repo = vector_repo
        self.embedding_service = embedding_service
        self.gemini = gemini_client
        self.cache = cache_service

    async def hybrid_search(self, request: SearchRequest) -> SearchResponse:
        """Perform hybrid search combining semantic and filter-based approaches.

        Steps:
            1. Parse query with Gemini to extract structured filters
            2. Generate embedding for semantic search
            3. Execute semantic and filter searches in parallel
            4. Merge results using Reciprocal Rank Fusion (RRF)
            5. Optional reranking with Gemini
            6. Format and return response

        Args:
            request: Search request with query and options

        Returns:
            Search response with ranked results

        Example:
            ```python
            request = SearchRequest(
                query="quick italian pasta under 30 minutes",
                limit=10,
                use_semantic=True,
                use_filters=True
            )
            response = await service.hybrid_search(request)
            ```
        """
        # Check cache first
        cached_results = await self.cache.get_search_results(
            request.query, request.filters
        )
        if cached_results:
            return SearchResponse(**cached_results)

        # Parse query to extract filters and intent
        parsed_query = None
        if request.use_filters:
            parsed_query = await self.query_understanding(request.query)

        # Execute searches sequentially to avoid session concurrency issues
        semantic_results = []
        filter_results = []

        # Semantic search
        if request.use_semantic:
            semantic_results = await self.semantic_search(
                parsed_query.semantic_query if parsed_query else request.query,
                limit=request.limit * 2,  # Get more for merging
            )

        # Filter search
        if request.use_filters and parsed_query:
            filters = self._build_filters(parsed_query, request.filters)
            filter_results = await self.filter_search(filters, limit=request.limit * 2)

        # Merge results using RRF if both search types used
        if semantic_results and filter_results:
            merged_recipes = self._merge_results_rrf(
                semantic_results, filter_results, k=60
            )
        elif semantic_results:
            merged_recipes = semantic_results
        elif filter_results:
            merged_recipes = filter_results
        else:
            merged_recipes = []

        # Limit results
        merged_recipes = merged_recipes[: request.limit]

        # Optional reranking
        if request.use_reranking and merged_recipes:
            merged_recipes = await self.result_reranking(merged_recipes, request.query)

        # Convert to search results
        search_results = []
        for i, (recipe, score) in enumerate(merged_recipes):
            match_type = "hybrid"
            if not request.use_semantic:
                match_type = "filter"
            elif not request.use_filters:
                match_type = "semantic"

            search_results.append(
                SearchResult(
                    recipe=self._recipe_to_response(recipe),
                    score=score,
                    distance=None,
                    match_type=match_type,
                )
            )

        # Build response
        response = SearchResponse(
            query=request.query,
            parsed_query=parsed_query,
            results=search_results,
            total=len(search_results),
            search_type="hybrid" if (request.use_semantic and request.use_filters) else ("semantic" if request.use_semantic else "filter"),
            metadata={
                "semantic_count": len(semantic_results),
                "filter_count": len(filter_results),
                "reranked": request.use_reranking,
            },
        )

        # Cache results (use mode='json' to serialize datetime objects)
        await self.cache.set_search_results(
            request.query, response.model_dump(mode='json'), request.filters
        )

        return response

    async def semantic_search(
        self, query: str, limit: int = 10
    ) -> list[tuple[Recipe, float]]:
        """Perform semantic search using vector embeddings.

        Args:
            query: Search query text
            limit: Maximum number of results

        Returns:
            List of (Recipe, score) tuples ordered by relevance

        Example:
            ```python
            results = await service.semantic_search("spicy thai curry", limit=5)
            ```
        """
        # Generate query embedding
        query_embedding = await self.embedding_service.generate_query_embedding(query)

        # Perform vector similarity search
        results = await self.vector_repo.similarity_search(
            query_embedding, limit=limit, distance_metric="cosine"
        )

        # Convert distances to similarity scores (1 - distance for cosine)
        scored_results = [(recipe, 1 - distance) for recipe, distance in results]

        return scored_results

    async def filter_search(
        self, filters: dict, limit: int = 10
    ) -> list[tuple[Recipe, float]]:
        """Perform filter-based search using recipe attributes.

        Args:
            filters: Dictionary of filter criteria
            limit: Maximum number of results

        Returns:
            List of (Recipe, score) tuples

        Example:
            ```python
            filters = {
                "cuisine_type": "Italian",
                "difficulty": DifficultyLevel.EASY,
                "max_prep_time": 30
            }
            results = await service.filter_search(filters, limit=10)
            ```
        """
        recipes = []

        try:
            # Handle multiple filter combinations
            if "cuisine_type" in filters and "difficulty" in filters:
                recipes = await self.recipe_repo.find_by_cuisine_and_difficulty(
                    cuisine=filters.get("cuisine_type"),
                    difficulty=filters.get("difficulty"),
                    pagination=Pagination(page=1, page_size=limit),
                )
            elif "cuisine_type" in filters:
                recipes = await self.recipe_repo.find_by_cuisine_and_difficulty(
                    cuisine=filters.get("cuisine_type"),
                    difficulty=None,
                    pagination=Pagination(page=1, page_size=limit),
                )
            elif "difficulty" in filters:
                recipes = await self.recipe_repo.find_by_cuisine_and_difficulty(
                    cuisine=None,
                    difficulty=filters.get("difficulty"),
                    pagination=Pagination(page=1, page_size=limit),
                )
            elif any(k in filters for k in ["max_total_time", "max_prep_time", "max_cook_time"]):
                # Calculate max_total_time from max_prep_time and max_cook_time if not provided
                max_total = filters.get("max_total_time")
                if not max_total and ("max_prep_time" in filters or "max_cook_time" in filters):
                    max_prep = filters.get("max_prep_time", 0)
                    max_cook = filters.get("max_cook_time", 0)
                    if max_prep or max_cook:
                        max_total = (max_prep or 999) + (max_cook or 999)

                recipes = await self.recipe_repo.get_recipes_with_time_range(
                    max_total_time=max_total,
                    max_prep_time=filters.get("max_prep_time"),
                    max_cook_time=filters.get("max_cook_time"),
                    pagination=Pagination(page=1, page_size=limit),
                )
            elif "diet_type" in filters or "diet_types" in filters:
                # Handle both singular and plural forms
                diet_type = filters.get("diet_type") or (filters.get("diet_types", [])[0] if filters.get("diet_types") else None)
                if diet_type:
                    try:
                        recipes = await self.recipe_repo.get_recipes_by_diet_type(
                            diet_type=diet_type,
                            pagination=Pagination(page=1, page_size=limit),
                        )
                    except Exception as e:
                        # Fallback to text search if diet type filtering fails
                        recipes = await self.recipe_repo.search_by_text(
                            query=diet_type,
                            pagination=Pagination(page=1, page_size=limit),
                        )
            elif "ingredients" in filters:
                recipes = await self.recipe_repo.find_by_ingredients(
                    ingredients=filters["ingredients"],
                    pagination=Pagination(page=1, page_size=limit),
                    match_all=filters.get("match_all_ingredients", False),
                )
            else:
                # Default: get recent recipes
                recipes = await self.recipe_repo.get_popular_recipes(limit=limit)
        except Exception as e:
            # Log error and return empty results rather than crashing
            print(f"Filter search error: {e}")
            recipes = []

        # Assign uniform scores for filter-based results
        return [(recipe, 1.0) for recipe in recipes]

    async def query_understanding(self, query: str) -> ParsedQuery:
        """Parse and understand search query using Gemini.

        Extracts structured information from natural language queries:
            - Ingredients
            - Cuisine type
            - Diet types
            - Time constraints
            - Difficulty level

        Args:
            query: Natural language search query

        Returns:
            Parsed query with extracted filters

        Example:
            ```python
            parsed = await service.query_understanding(
                "quick vegetarian italian pasta under 30 minutes"
            )
            # ParsedQuery(
            #     cuisine_type="Italian",
            #     diet_types=["vegetarian"],
            #     max_prep_time=30,
            #     ...
            # )
            ```
        """
        prompt = f"""Parse this recipe search query and extract structured information.

IMPORTANT TIME PARSING RULES:
- "under X minutes", "in X minutes", "X minutes or less" = total time constraint (prep + cook combined)
- "quick" or "fast" = under 30 minutes total time
- If time is mentioned without specifying prep/cook, assume it's TOTAL time
- Only use max_prep_time or max_cook_time if explicitly mentioned (e.g., "15 min prep")

Return ONLY a valid JSON object with these fields:
- ingredients: list of ingredient names (empty list if none)
- cuisine_type: detected cuisine type (null if none)
- diet_types: list of diet types like vegetarian, vegan, gluten-free (empty list if none)
- max_total_time: maximum TOTAL time (prep + cook) in minutes (null if none)
- max_prep_time: maximum preparation time in minutes ONLY if specifically mentioned (null if none)
- max_cook_time: maximum cooking time in minutes ONLY if specifically mentioned (null if none)
- difficulty: difficulty level - easy, medium, or hard (null if none)
- semantic_query: simplified query for semantic search (remove time/diet constraints)

Query: "{query}"

Return ONLY valid JSON, no markdown or explanations.
"""

        try:
            response_text = await self.gemini.generate_text(
                prompt, max_output_tokens=512, temperature=0.1
            )

            # Clean response (remove markdown code blocks if present)
            response_text = response_text.strip()
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # Parse JSON
            parsed_data = json.loads(response_text)

            return ParsedQuery(
                original_query=query,
                ingredients=parsed_data.get("ingredients", []),
                cuisine_type=parsed_data.get("cuisine_type"),
                diet_types=parsed_data.get("diet_types", []),
                max_total_time=parsed_data.get("max_total_time"),
                max_prep_time=parsed_data.get("max_prep_time"),
                max_cook_time=parsed_data.get("max_cook_time"),
                difficulty=parsed_data.get("difficulty"),
                semantic_query=parsed_data.get("semantic_query", query),
            )

        except Exception:
            # Fallback to simple parsing on error
            return ParsedQuery(
                original_query=query,
                ingredients=[],
                cuisine_type=None,
                diet_types=[],
                max_total_time=None,
                max_prep_time=None,
                max_cook_time=None,
                difficulty=None,
                semantic_query=query,
            )

    async def result_reranking(
        self, results: list[tuple[Recipe, float]], query: str
    ) -> list[tuple[Recipe, float]]:
        """Rerank search results using Gemini for improved relevance.

        Args:
            results: Initial search results
            query: Original search query

        Returns:
            Reranked results

        Example:
            ```python
            reranked = await service.result_reranking(results, "authentic italian carbonara")
            ```
        """
        if not results:
            return results

        # Limit to top 20 for reranking (to avoid token limits)
        top_results = results[:20]

        # Build prompt with recipe summaries
        recipe_summaries = []
        for i, (recipe, _) in enumerate(top_results):
            summary = f"{i+1}. {recipe.name} - {recipe.description or 'No description'}"
            recipe_summaries.append(summary)

        prompt = f"""Rerank these recipes by relevance to the query: "{query}"

Recipes:
{chr(10).join(recipe_summaries)}

Return ONLY a JSON array of recipe indices (1-{len(top_results)}) in order of relevance (most relevant first).
Example: [3, 1, 5, 2, 4]

Return ONLY the JSON array, no explanations.
"""

        try:
            response_text = await self.gemini.generate_text(
                prompt, max_output_tokens=256, temperature=0.0
            )

            # Parse response
            response_text = response_text.strip()
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            indices = json.loads(response_text)

            # Reorder results based on indices
            reranked = []
            for idx in indices:
                if 1 <= idx <= len(top_results):
                    recipe, score = top_results[idx - 1]
                    # Boost score based on rerank position
                    new_score = score * (1.0 + (len(indices) - indices.index(idx)) / len(indices) * 0.3)
                    reranked.append((recipe, new_score))

            # Add any remaining results that weren't reranked
            for i, result in enumerate(top_results):
                if (i + 1) not in indices:
                    reranked.append(result)

            return reranked

        except Exception:
            # Return original results on error
            return results

    def _merge_results_rrf(
        self,
        semantic_results: list[tuple[Recipe, float]],
        filter_results: list[tuple[Recipe, float]],
        k: int = 60,
    ) -> list[tuple[Recipe, float]]:
        """Merge results using Reciprocal Rank Fusion (RRF).

        RRF formula: score = sum(1 / (k + rank)) for each result list

        Args:
            semantic_results: Results from semantic search
            filter_results: Results from filter search
            k: RRF constant (default: 60)

        Returns:
            Merged and sorted results with combined scores
        """
        rrf_scores = {}
        original_scores = {}
        recipe_lookup = {}

        # Calculate RRF scores and store original scores from semantic results
        for rank, (recipe, score) in enumerate(semantic_results):
            recipe_id = str(recipe.id)
            rrf_scores[recipe_id] = rrf_scores.get(recipe_id, 0) + 1 / (k + rank + 1)
            # Keep the best original score
            if recipe_id not in original_scores or score > original_scores[recipe_id]:
                original_scores[recipe_id] = score
            recipe_lookup[recipe_id] = recipe

        # Add RRF scores and original scores from filter results
        for rank, (recipe, score) in enumerate(filter_results):
            recipe_id = str(recipe.id)
            rrf_scores[recipe_id] = rrf_scores.get(recipe_id, 0) + 1 / (k + rank + 1)
            # Keep the best original score
            if recipe_id not in original_scores or score > original_scores[recipe_id]:
                original_scores[recipe_id] = score
            recipe_lookup[recipe_id] = recipe

        # Combine RRF ranking with original scores
        # Use RRF for ranking but preserve meaningful scores
        combined_scores = {}
        for recipe_id in rrf_scores:
            # Weight: 70% original score, 30% normalized RRF score
            # Normalize RRF scores to 0-1 range
            max_rrf = 2 / (k + 1)  # Maximum possible RRF score (appears at rank 0 in both lists)
            normalized_rrf = rrf_scores[recipe_id] / max_rrf

            original_score = original_scores.get(recipe_id, 0.5)  # Default to 0.5 if no original score
            combined_scores[recipe_id] = (0.7 * original_score) + (0.3 * normalized_rrf)

        # Sort by combined score
        sorted_ids = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

        return [(recipe_lookup[recipe_id], score) for recipe_id, score in sorted_ids]

    def _build_filters(
        self, parsed_query: ParsedQuery, additional_filters: Optional[dict]
    ) -> dict:
        """Build filter dictionary from parsed query and additional filters.

        Args:
            parsed_query: Parsed query components
            additional_filters: Additional user-provided filters

        Returns:
            Combined filter dictionary
        """
        filters = {}

        if parsed_query.cuisine_type:
            filters["cuisine_type"] = parsed_query.cuisine_type

        if parsed_query.difficulty:
            filters["difficulty"] = parsed_query.difficulty

        # Add max_total_time if specified
        if parsed_query.max_total_time:
            filters["max_total_time"] = parsed_query.max_total_time

        if parsed_query.max_prep_time:
            filters["max_prep_time"] = parsed_query.max_prep_time

        if parsed_query.max_cook_time:
            filters["max_cook_time"] = parsed_query.max_cook_time

        if parsed_query.diet_types:
            # Pass diet_types as array for better compatibility
            filters["diet_types"] = parsed_query.diet_types
            # Also include first diet_type for backward compatibility
            filters["diet_type"] = parsed_query.diet_types[0]

        if parsed_query.ingredients:
            filters["ingredients"] = parsed_query.ingredients

        # Merge with additional filters
        if additional_filters:
            filters.update(additional_filters)

        return filters

    def _recipe_to_response(self, recipe: Recipe) -> dict:
        """Convert Recipe model to response dictionary.

        Args:
            recipe: Recipe model instance

        Returns:
            Recipe response dictionary
        """
        from app.schemas.recipe import RecipeResponse

        # Build response (simplified - in production would use proper serialization)
        response = RecipeResponse(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            instructions=recipe.instructions,
            prep_time=recipe.prep_time,
            cook_time=recipe.cook_time,
            servings=recipe.servings,
            difficulty=recipe.difficulty,
            cuisine_type=recipe.cuisine_type,
            diet_types=recipe.diet_types,
            embedding=None,  # Don't include embedding in response
            ingredients=[],  # Would populate from relations
            categories=[],  # Would populate from relations
            nutritional_info=None,  # Would populate from relations
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
            deleted_at=recipe.deleted_at,
            created_by=recipe.created_by,
            updated_by=recipe.updated_by,
        )
        # Return dict with proper JSON serialization
        return response.model_dump(mode='json')
