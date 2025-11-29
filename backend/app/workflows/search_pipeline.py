"""Search pipeline workflow with LangGraph and Judge pattern.

Implements a hybrid search pipeline that:
1. Parses queries with Gemini
2. Performs parallel semantic and filter searches
3. Merges results using RRF
4. Validates results with judge pattern
5. Optionally reranks results
6. Formats final response
"""

import asyncio
import logging
from typing import Any

from langgraph.graph import StateGraph, END

from app.core.gemini_client import GeminiClient
from app.db.models import Recipe
from app.repositories.recipe import RecipeRepository
from app.repositories.vector import VectorRepository
from app.schemas.search import ParsedQuery
from app.services.cache import CacheService
from app.services.embedding import EmbeddingService
from app.services.search import SearchService
from app.workflows.states import (
    SearchPipelineState,
    JudgeConfig,
    FallbackStrategy,
)

logger = logging.getLogger(__name__)


class SearchPipelineGraph:
    """LangGraph workflow for search pipeline with judge pattern.

    Graph Structure:
        START -> parse_query
        parse_query -> generate_embedding [conditional]
        parse_query -> extract_filters [conditional]
        generate_embedding -> vector_search
        extract_filters -> filter_search
        vector_search -> merge_results
        filter_search -> merge_results
        merge_results -> judge_relevance
        judge_relevance -> rerank [conditional]
        rerank -> format_response
        format_response -> END

    Example:
        ```python
        pipeline = SearchPipelineGraph(
            search_service, embedding_service, gemini_client,
            recipe_repo, vector_repo, cache_service
        )
        result = await pipeline.run({
            "query": "quick italian pasta",
            "judge_config": JudgeConfig(semantic_threshold=0.6)
        })
        ```
    """

    def __init__(
        self,
        search_service: SearchService,
        embedding_service: EmbeddingService,
        gemini_client: GeminiClient,
        recipe_repo: RecipeRepository,
        vector_repo: VectorRepository,
        cache_service: CacheService,
    ):
        """Initialize search pipeline graph.

        Args:
            search_service: Service for search operations
            embedding_service: Service for embedding generation
            gemini_client: Gemini API client
            recipe_repo: Recipe repository
            vector_repo: Vector repository for similarity search
            cache_service: Cache service
        """
        self.search_service = search_service
        self.embedding_service = embedding_service
        self.gemini_client = gemini_client
        self.recipe_repo = recipe_repo
        self.vector_repo = vector_repo
        self.cache_service = cache_service

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow.

        Returns:
            Compiled StateGraph workflow
        """
        workflow = StateGraph(SearchPipelineState)

        # Add nodes
        workflow.add_node("parse_query", self._parse_query_node)
        workflow.add_node("generate_embedding", self._generate_embedding_node)
        workflow.add_node("extract_filters", self._extract_filters_node)
        workflow.add_node("vector_search", self._vector_search_node)
        workflow.add_node("filter_search", self._filter_search_node)
        workflow.add_node("merge_results", self._merge_results_node)
        workflow.add_node("judge_relevance", self._judge_relevance_node)
        workflow.add_node("rerank", self._rerank_node)
        workflow.add_node("format_response", self._format_response_node)

        # Define edges
        workflow.set_entry_point("parse_query")

        # Conditional edges from parse_query
        workflow.add_conditional_edges(
            "parse_query",
            self._route_after_parse,
            {
                "embedding": "generate_embedding",
                "filters": "extract_filters",
                "both": "generate_embedding",  # Will handle parallel execution
            }
        )

        # Edges for embedding path
        workflow.add_edge("generate_embedding", "vector_search")

        # Edges for filter path
        workflow.add_edge("extract_filters", "filter_search")

        # Both paths converge at merge_results
        workflow.add_edge("vector_search", "merge_results")
        workflow.add_edge("filter_search", "merge_results")

        # Judge after merging
        workflow.add_edge("merge_results", "judge_relevance")

        # Conditional edge from judge to rerank
        workflow.add_conditional_edges(
            "judge_relevance",
            self._should_rerank,
            {
                "rerank": "rerank",
                "skip": "format_response",
            }
        )

        # Final edges
        workflow.add_edge("rerank", "format_response")
        workflow.add_edge("format_response", END)

        return workflow.compile()

    async def run(self, initial_state: dict[str, Any]) -> SearchPipelineState:
        """Execute the search pipeline workflow.

        Args:
            initial_state: Initial state with query and configuration

        Returns:
            Final state with search results

        Raises:
            Exception: If workflow execution fails
        """
        try:
            # Set defaults
            if "metadata" not in initial_state:
                initial_state["metadata"] = {}
            if "judge_config" not in initial_state:
                initial_state["judge_config"] = JudgeConfig()

            # Run the graph
            final_state = await self.graph.ainvoke(initial_state)
            return final_state

        except Exception as e:
            logger.error(f"Search pipeline failed: {e}", exc_info=True)
            raise

    # ==================== Node Implementations ====================

    async def _parse_query_node(self, state: SearchPipelineState) -> SearchPipelineState:
        """Parse user query to extract intent and structured filters.

        Args:
            state: Current workflow state

        Returns:
            Updated state with parsed query
        """
        logger.info(f"Parsing query: {state['query']}")

        try:
            parsed_query = await self.search_service.query_understanding(state["query"])

            state["parsed_query"] = {
                "original_query": parsed_query.original_query,
                "ingredients": parsed_query.ingredients,
                "cuisine_type": parsed_query.cuisine_type,
                "diet_types": parsed_query.diet_types,
                "max_prep_time": parsed_query.max_prep_time,
                "max_cook_time": parsed_query.max_cook_time,
                "difficulty": parsed_query.difficulty,
                "semantic_query": parsed_query.semantic_query,
            }

            state["metadata"]["parsed_at"] = "parse_query_node"

            return state

        except Exception as e:
            logger.error(f"Query parsing failed: {e}")
            state["error"] = f"Failed to parse query: {str(e)}"
            return state

    async def _generate_embedding_node(self, state: SearchPipelineState) -> SearchPipelineState:
        """Generate embedding for semantic search.

        Args:
            state: Current workflow state

        Returns:
            Updated state with query embedding
        """
        logger.info("Generating query embedding")

        try:
            semantic_query = state.get("parsed_query", {}).get("semantic_query", state["query"])
            embedding = await self.embedding_service.generate_query_embedding(semantic_query)

            state["embedding"] = embedding
            state["metadata"]["embedding_generated"] = True

            return state

        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            state["embedding"] = None
            state["metadata"]["embedding_generated"] = False
            return state

    async def _extract_filters_node(self, state: SearchPipelineState) -> SearchPipelineState:
        """Extract structured filters from parsed query.

        Args:
            state: Current workflow state

        Returns:
            Updated state with extracted filters
        """
        logger.info("Extracting filters")

        parsed_query = state.get("parsed_query", {})
        filters = {}

        if parsed_query.get("cuisine_type"):
            filters["cuisine_type"] = parsed_query["cuisine_type"]

        if parsed_query.get("difficulty"):
            filters["difficulty"] = parsed_query["difficulty"]

        if parsed_query.get("max_prep_time"):
            filters["max_prep_time"] = parsed_query["max_prep_time"]

        if parsed_query.get("max_cook_time"):
            filters["max_cook_time"] = parsed_query["max_cook_time"]

        if parsed_query.get("diet_types"):
            filters["diet_type"] = parsed_query["diet_types"][0]

        if parsed_query.get("ingredients"):
            filters["ingredients"] = parsed_query["ingredients"]

        state["filters"] = filters
        state["metadata"]["filters_extracted"] = True

        return state

    async def _vector_search_node(self, state: SearchPipelineState) -> SearchPipelineState:
        """Perform semantic vector search.

        Args:
            state: Current workflow state

        Returns:
            Updated state with vector search results
        """
        logger.info("Performing vector search")

        if not state.get("embedding"):
            state["vector_results"] = []
            return state

        try:
            results = await self.vector_repo.similarity_search(
                state["embedding"],
                limit=50,
                distance_metric="cosine"
            )

            state["vector_results"] = [recipe for recipe, _ in results]
            state["metadata"]["vector_count"] = len(results)

            return state

        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            state["vector_results"] = []
            return state

    async def _filter_search_node(self, state: SearchPipelineState) -> SearchPipelineState:
        """Perform filter-based search.

        Args:
            state: Current workflow state

        Returns:
            Updated state with filter search results
        """
        logger.info("Performing filter search")

        filters = state.get("filters", {})
        if not filters:
            state["filter_results"] = []
            return state

        try:
            results = await self.search_service.filter_search(filters, limit=50)
            state["filter_results"] = [recipe for recipe, _ in results]
            state["metadata"]["filter_count"] = len(results)

            return state

        except Exception as e:
            logger.error(f"Filter search failed: {e}")
            state["filter_results"] = []
            return state

    async def _merge_results_node(self, state: SearchPipelineState) -> SearchPipelineState:
        """Merge vector and filter results using RRF.

        Args:
            state: Current workflow state

        Returns:
            Updated state with merged results
        """
        logger.info("Merging search results")

        vector_results = state.get("vector_results", [])
        filter_results = state.get("filter_results", [])

        if not vector_results and not filter_results:
            state["merged_results"] = []
            return state

        # Convert to format expected by RRF
        vector_tuples = [(r, 1.0) for r in vector_results]
        filter_tuples = [(r, 1.0) for r in filter_results]

        if vector_tuples and filter_tuples:
            merged = self.search_service._merge_results_rrf(
                vector_tuples, filter_tuples, k=60
            )
            state["merged_results"] = [recipe for recipe, _ in merged]
        elif vector_tuples:
            state["merged_results"] = vector_results
        else:
            state["merged_results"] = filter_results

        state["metadata"]["merged_count"] = len(state["merged_results"])

        return state

    async def _judge_relevance_node(self, state: SearchPipelineState) -> SearchPipelineState:
        """Judge and filter results based on relevance criteria.

        This is the key Judge Pattern node that validates results against
        configurable quality thresholds.

        Args:
            state: Current workflow state

        Returns:
            Updated state with filtered results and judge metrics
        """
        logger.info("Judging result relevance")

        merged_results = state.get("merged_results", [])
        if not merged_results:
            state["filtered_results"] = []
            state["judge_metrics"] = {}
            state["judge_report"] = {"filtered": 0, "reason": "No results to judge"}
            return state

        judge_config = state.get("judge_config", JudgeConfig())
        parsed_query = state.get("parsed_query", {})
        filters = state.get("filters", {})

        filtered_results = []
        judge_metrics = {
            "total_evaluated": len(merged_results),
            "passed_semantic": 0,
            "passed_filter": 0,
            "passed_dietary": 0,
            "failed_semantic": 0,
            "failed_filter": 0,
            "failed_dietary": 0,
        }

        for recipe in merged_results:
            scores = self._evaluate_recipe(recipe, parsed_query, filters, judge_config)

            # Check if recipe passes all thresholds
            passes = True

            # Semantic threshold check (if embedding exists)
            if state.get("embedding") and scores["semantic_score"] < judge_config.semantic_threshold:
                passes = False
                judge_metrics["failed_semantic"] += 1
            else:
                judge_metrics["passed_semantic"] += 1

            # Filter compliance check
            if scores["filter_compliance"] < judge_config.filter_compliance_min:
                passes = False
                judge_metrics["failed_filter"] += 1
            else:
                judge_metrics["passed_filter"] += 1

            # Dietary compliance check
            if judge_config.dietary_strict_mode and not scores["dietary_compliant"]:
                passes = False
                judge_metrics["failed_dietary"] += 1
            else:
                judge_metrics["passed_dietary"] += 1

            # Overall confidence check
            if scores["confidence"] < judge_config.confidence_threshold:
                passes = False

            if passes:
                filtered_results.append(recipe)

        # Apply min/max results limits
        if len(filtered_results) < judge_config.min_results:
            # Apply fallback strategy
            if judge_config.fallback_strategy == FallbackStrategy.RELAX_THRESHOLDS:
                logger.warning(f"Only {len(filtered_results)} results passed judge, relaxing thresholds")
                filtered_results = merged_results[:judge_config.min_results]
            elif judge_config.fallback_strategy == FallbackStrategy.EMPTY_RESULTS:
                filtered_results = []

        filtered_results = filtered_results[:judge_config.max_results]

        state["filtered_results"] = filtered_results
        state["judge_metrics"] = judge_metrics
        state["judge_report"] = {
            "original_count": len(merged_results),
            "filtered_count": len(filtered_results),
            "removed_count": len(merged_results) - len(filtered_results),
            "metrics": judge_metrics,
            "config": judge_config.model_dump(),
        }

        logger.info(f"Judge filtered {len(merged_results)} -> {len(filtered_results)} results")

        return state

    def _evaluate_recipe(
        self,
        recipe: Recipe,
        parsed_query: dict,
        filters: dict,
        config: JudgeConfig
    ) -> dict[str, Any]:
        """Evaluate a single recipe against judge criteria.

        Args:
            recipe: Recipe to evaluate
            parsed_query: Parsed query components
            filters: Extracted filters
            config: Judge configuration

        Returns:
            Dictionary with evaluation scores
        """
        scores = {
            "semantic_score": 1.0,  # Would need actual cosine similarity
            "filter_compliance": 0.0,
            "ingredient_match": 0.0,
            "dietary_compliant": True,
            "confidence": 0.0,
        }

        # Calculate filter compliance
        matched_filters = 0
        total_filters = len(filters)

        if total_filters > 0:
            if filters.get("cuisine_type") and recipe.cuisine_type == filters["cuisine_type"]:
                matched_filters += 1

            if filters.get("difficulty") and recipe.difficulty.value == filters["difficulty"]:
                matched_filters += 1

            if filters.get("max_prep_time") and recipe.prep_time and recipe.prep_time <= filters["max_prep_time"]:
                matched_filters += 1

            if filters.get("max_cook_time") and recipe.cook_time and recipe.cook_time <= filters["max_cook_time"]:
                matched_filters += 1

            if filters.get("diet_type"):
                if recipe.diet_types and filters["diet_type"] in recipe.diet_types:
                    matched_filters += 1
                else:
                    scores["dietary_compliant"] = False

            scores["filter_compliance"] = matched_filters / total_filters
        else:
            scores["filter_compliance"] = 1.0

        # Calculate ingredient match if applicable
        if parsed_query.get("ingredients"):
            # Would need actual ingredient matching logic
            scores["ingredient_match"] = 0.5

        # Calculate overall confidence
        scores["confidence"] = (
            scores["semantic_score"] * 0.4 +
            scores["filter_compliance"] * 0.4 +
            scores["ingredient_match"] * 0.2
        )

        return scores

    async def _rerank_node(self, state: SearchPipelineState) -> SearchPipelineState:
        """Rerank results using Gemini for improved relevance.

        Args:
            state: Current workflow state

        Returns:
            Updated state with reranked results
        """
        logger.info("Reranking results")

        filtered_results = state.get("filtered_results", [])
        if not filtered_results:
            return state

        try:
            results_with_scores = [(r, 1.0) for r in filtered_results]
            reranked = await self.search_service.result_reranking(
                results_with_scores,
                state["query"]
            )

            state["filtered_results"] = [recipe for recipe, _ in reranked]
            state["metadata"]["reranked"] = True

            return state

        except Exception as e:
            logger.error(f"Reranking failed: {e}")
            state["metadata"]["reranked"] = False
            return state

    async def _format_response_node(self, state: SearchPipelineState) -> SearchPipelineState:
        """Format final response.

        Args:
            state: Current workflow state

        Returns:
            Updated state with final formatted results
        """
        logger.info("Formatting response")

        state["final_results"] = state.get("filtered_results", [])
        state["metadata"]["total_results"] = len(state["final_results"])

        return state

    # ==================== Routing Functions ====================

    def _route_after_parse(self, state: SearchPipelineState) -> str:
        """Determine routing after query parsing.

        Args:
            state: Current workflow state

        Returns:
            Route key for conditional edge
        """
        parsed_query = state.get("parsed_query", {})
        filters = state.get("filters", {})

        has_semantic = bool(parsed_query.get("semantic_query"))
        has_filters = bool(filters)

        if has_semantic and has_filters:
            return "both"
        elif has_semantic:
            return "embedding"
        else:
            return "filters"

    def _should_rerank(self, state: SearchPipelineState) -> str:
        """Determine if reranking should be applied.

        Args:
            state: Current workflow state

        Returns:
            Route key for conditional edge
        """
        filtered_results = state.get("filtered_results", [])
        metadata = state.get("metadata", {})

        # Rerank if we have results and significant filtering occurred
        if filtered_results and len(filtered_results) > 3:
            judge_report = state.get("judge_report", {})
            removed_count = judge_report.get("removed_count", 0)

            if removed_count > 5:
                return "rerank"

        return "skip"
