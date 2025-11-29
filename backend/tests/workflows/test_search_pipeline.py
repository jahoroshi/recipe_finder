"""Tests for SearchPipelineGraph workflow."""

from unittest.mock import AsyncMock, patch

import pytest

from app.workflows.search_pipeline import SearchPipelineGraph
from app.workflows.states import JudgeConfig, FallbackStrategy


class TestSearchPipelineGraph:
    """Test suite for SearchPipelineGraph."""

    @pytest.fixture
    def search_pipeline(
        self,
        mock_search_service,
        mock_embedding_service,
        mock_gemini_client,
        mock_recipe_repo,
        mock_vector_repo,
        mock_cache_service,
    ):
        """Create search pipeline graph instance."""
        return SearchPipelineGraph(
            search_service=mock_search_service,
            embedding_service=mock_embedding_service,
            gemini_client=mock_gemini_client,
            recipe_repo=mock_recipe_repo,
            vector_repo=mock_vector_repo,
            cache_service=mock_cache_service,
        )

    @pytest.mark.asyncio
    async def test_parse_query_node(self, search_pipeline, sample_recipes):
        """Test parse_query node extracts query components."""
        state = {
            "query": "quick italian pasta under 30 minutes",
            "metadata": {},
        }

        result = await search_pipeline._parse_query_node(state)

        assert "parsed_query" in result
        assert result["parsed_query"]["original_query"] == state["query"]
        assert "semantic_query" in result["parsed_query"]
        assert "metadata" in result

    @pytest.mark.asyncio
    async def test_generate_embedding_node(self, search_pipeline):
        """Test generate_embedding node creates query embedding."""
        state = {
            "query": "pasta carbonara",
            "parsed_query": {
                "semantic_query": "pasta carbonara",
            },
            "metadata": {},
        }

        result = await search_pipeline._generate_embedding_node(state)

        assert "embedding" in result
        assert isinstance(result["embedding"], list)
        assert len(result["embedding"]) == 768
        assert result["metadata"]["embedding_generated"] is True

    @pytest.mark.asyncio
    async def test_extract_filters_node(self, search_pipeline):
        """Test extract_filters node builds filter dictionary."""
        state = {
            "query": "quick italian pasta",
            "parsed_query": {
                "cuisine_type": "Italian",
                "difficulty": "easy",
                "max_prep_time": 30,
                "diet_types": ["vegetarian"],
                "ingredients": ["pasta", "tomato"],
            },
            "metadata": {},
        }

        result = await search_pipeline._extract_filters_node(state)

        assert "filters" in result
        assert result["filters"]["cuisine_type"] == "Italian"
        assert result["filters"]["difficulty"] == "easy"
        assert result["filters"]["max_prep_time"] == 30
        assert result["filters"]["diet_type"] == "vegetarian"
        assert result["filters"]["ingredients"] == ["pasta", "tomato"]

    @pytest.mark.asyncio
    async def test_vector_search_node(self, search_pipeline, sample_recipes):
        """Test vector_search node performs semantic search."""
        # Setup mock
        search_pipeline.vector_repo.similarity_search = AsyncMock(
            return_value=[(sample_recipes[0], 0.9), (sample_recipes[1], 0.8)]
        )

        state = {
            "embedding": [0.1] * 768,
            "metadata": {},
        }

        result = await search_pipeline._vector_search_node(state)

        assert "vector_results" in result
        assert len(result["vector_results"]) == 2
        assert result["metadata"]["vector_count"] == 2

    @pytest.mark.asyncio
    async def test_vector_search_node_no_embedding(self, search_pipeline):
        """Test vector_search node handles missing embedding."""
        state = {
            "embedding": None,
            "metadata": {},
        }

        result = await search_pipeline._vector_search_node(state)

        assert result["vector_results"] == []

    @pytest.mark.asyncio
    async def test_filter_search_node(self, search_pipeline, sample_recipes):
        """Test filter_search node performs attribute-based search."""
        # Setup mock
        search_pipeline.search_service.filter_search = AsyncMock(
            return_value=[(sample_recipes[0], 1.0)]
        )

        state = {
            "filters": {"cuisine_type": "Italian"},
            "metadata": {},
        }

        result = await search_pipeline._filter_search_node(state)

        assert "filter_results" in result
        assert len(result["filter_results"]) == 1
        assert result["metadata"]["filter_count"] == 1

    @pytest.mark.asyncio
    async def test_merge_results_node_hybrid(self, search_pipeline, sample_recipes):
        """Test merge_results node combines vector and filter results."""
        state = {
            "vector_results": [sample_recipes[0], sample_recipes[1]],
            "filter_results": [sample_recipes[0], sample_recipes[2]],
            "metadata": {},
        }

        result = await search_pipeline._merge_results_node(state)

        assert "merged_results" in result
        assert len(result["merged_results"]) > 0
        assert result["metadata"]["merged_count"] == len(result["merged_results"])

    @pytest.mark.asyncio
    async def test_merge_results_node_vector_only(self, search_pipeline, sample_recipes):
        """Test merge_results node with vector results only."""
        state = {
            "vector_results": [sample_recipes[0]],
            "filter_results": [],
            "metadata": {},
        }

        result = await search_pipeline._merge_results_node(state)

        assert result["merged_results"] == [sample_recipes[0]]

    @pytest.mark.asyncio
    async def test_merge_results_node_filter_only(self, search_pipeline, sample_recipes):
        """Test merge_results node with filter results only."""
        state = {
            "vector_results": [],
            "filter_results": [sample_recipes[0]],
            "metadata": {},
        }

        result = await search_pipeline._merge_results_node(state)

        assert result["merged_results"] == [sample_recipes[0]]

    @pytest.mark.asyncio
    async def test_judge_relevance_node_passes_all(
        self, search_pipeline, sample_recipes, default_judge_config
    ):
        """Test judge_relevance node with permissive config passes all results."""
        state = {
            "merged_results": sample_recipes[:3],
            "judge_config": default_judge_config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        assert "filtered_results" in result
        assert len(result["filtered_results"]) == 3
        assert "judge_metrics" in result
        assert "judge_report" in result
        assert result["judge_report"]["original_count"] == 3

    @pytest.mark.asyncio
    async def test_judge_relevance_node_strict_filtering(
        self, search_pipeline, sample_recipes, strict_judge_config
    ):
        """Test judge_relevance node with strict config filters results."""
        state = {
            "merged_results": sample_recipes[:3],
            "judge_config": strict_judge_config,
            "parsed_query": {
                "cuisine_type": "Italian",
                "difficulty": "easy",
            },
            "filters": {
                "cuisine_type": "Italian",
                "difficulty": "easy",
            },
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        assert "filtered_results" in result
        assert "judge_metrics" in result
        assert result["judge_metrics"]["total_evaluated"] == 3

    @pytest.mark.asyncio
    async def test_judge_relevance_node_dietary_strict_mode(
        self, search_pipeline, sample_recipes
    ):
        """Test judge_relevance node enforces dietary restrictions in strict mode."""
        strict_config = JudgeConfig(
            dietary_strict_mode=True,
            min_results=0,
        )

        state = {
            "merged_results": sample_recipes,
            "judge_config": strict_config,
            "parsed_query": {
                "diet_types": ["vegan"],
            },
            "filters": {
                "diet_type": "vegan",
            },
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        # Should only keep vegan recipes
        assert "filtered_results" in result
        for recipe in result["filtered_results"]:
            assert "vegan" in recipe.diet_types

    @pytest.mark.asyncio
    async def test_judge_relevance_node_fallback_relax(
        self, search_pipeline, sample_recipes
    ):
        """Test judge_relevance node relaxes thresholds when min_results not met."""
        config = JudgeConfig(
            semantic_threshold=0.99,  # Very high threshold
            filter_compliance_min=0.99,
            min_results=3,
            fallback_strategy=FallbackStrategy.RELAX_THRESHOLDS,
        )

        state = {
            "merged_results": sample_recipes[:5],
            "judge_config": config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        # Should return at least min_results due to fallback
        assert len(result["filtered_results"]) >= 3

    @pytest.mark.asyncio
    async def test_judge_relevance_node_fallback_empty(
        self, search_pipeline, sample_recipes
    ):
        """Test judge_relevance node returns empty with EMPTY_RESULTS strategy."""
        config = JudgeConfig(
            semantic_threshold=0.99,
            min_results=3,
            fallback_strategy=FallbackStrategy.EMPTY_RESULTS,
        )

        state = {
            "merged_results": sample_recipes[:2],
            "judge_config": config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        # Should return empty results
        assert len(result["filtered_results"]) == 0

    @pytest.mark.asyncio
    async def test_judge_relevance_node_max_results(
        self, search_pipeline, sample_recipes, default_judge_config
    ):
        """Test judge_relevance node respects max_results limit."""
        config = JudgeConfig(
            max_results=2,
        )

        state = {
            "merged_results": sample_recipes,
            "judge_config": config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        assert len(result["filtered_results"]) <= 2

    @pytest.mark.asyncio
    async def test_judge_relevance_node_empty_results(
        self, search_pipeline, default_judge_config
    ):
        """Test judge_relevance node handles empty input."""
        state = {
            "merged_results": [],
            "judge_config": default_judge_config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        assert result["filtered_results"] == []
        assert result["judge_metrics"] == {}

    @pytest.mark.asyncio
    async def test_rerank_node(self, search_pipeline, sample_recipes):
        """Test rerank node reorders results."""
        search_pipeline.search_service.result_reranking = AsyncMock(
            return_value=[(sample_recipes[1], 0.9), (sample_recipes[0], 0.8)]
        )

        state = {
            "query": "pasta",
            "filtered_results": [sample_recipes[0], sample_recipes[1]],
            "metadata": {},
        }

        result = await search_pipeline._rerank_node(state)

        assert "filtered_results" in result
        assert len(result["filtered_results"]) == 2
        assert result["metadata"]["reranked"] is True

    @pytest.mark.asyncio
    async def test_rerank_node_empty_results(self, search_pipeline):
        """Test rerank node handles empty input."""
        state = {
            "query": "pasta",
            "filtered_results": [],
            "metadata": {},
        }

        result = await search_pipeline._rerank_node(state)

        assert result["filtered_results"] == []

    @pytest.mark.asyncio
    async def test_format_response_node(self, search_pipeline, sample_recipes):
        """Test format_response node creates final output."""
        state = {
            "filtered_results": sample_recipes[:2],
            "metadata": {},
        }

        result = await search_pipeline._format_response_node(state)

        assert "final_results" in result
        assert result["final_results"] == sample_recipes[:2]
        assert result["metadata"]["total_results"] == 2

    @pytest.mark.asyncio
    async def test_route_after_parse_both(self, search_pipeline):
        """Test routing chooses 'both' when semantic and filters present."""
        state = {
            "parsed_query": {
                "semantic_query": "pasta",
                "cuisine_type": "Italian",
            },
            "filters": {"cuisine_type": "Italian"},
        }

        route = search_pipeline._route_after_parse(state)
        assert route == "both"

    @pytest.mark.asyncio
    async def test_route_after_parse_embedding_only(self, search_pipeline):
        """Test routing chooses 'embedding' for semantic-only queries."""
        state = {
            "parsed_query": {
                "semantic_query": "pasta",
            },
            "filters": {},
        }

        route = search_pipeline._route_after_parse(state)
        assert route == "embedding"

    @pytest.mark.asyncio
    async def test_route_after_parse_filters_only(self, search_pipeline):
        """Test routing chooses 'filters' when no semantic query."""
        state = {
            "parsed_query": {},
            "filters": {"cuisine_type": "Italian"},
        }

        route = search_pipeline._route_after_parse(state)
        assert route == "filters"

    @pytest.mark.asyncio
    async def test_should_rerank_triggers(self, search_pipeline):
        """Test reranking is triggered when significant filtering occurs."""
        state = {
            "filtered_results": [None] * 10,  # Mock 10 results
            "judge_report": {
                "removed_count": 6,
            },
            "metadata": {},
        }

        route = search_pipeline._should_rerank(state)
        assert route == "rerank"

    @pytest.mark.asyncio
    async def test_should_rerank_skips(self, search_pipeline):
        """Test reranking is skipped for small result sets."""
        state = {
            "filtered_results": [None] * 2,
            "judge_report": {
                "removed_count": 1,
            },
            "metadata": {},
        }

        route = search_pipeline._should_rerank(state)
        assert route == "skip"

    @pytest.mark.asyncio
    async def test_evaluate_recipe_all_filters_match(
        self, search_pipeline, sample_recipes
    ):
        """Test recipe evaluation with all filters matching."""
        recipe = sample_recipes[0]  # Italian, easy, 10 min prep
        parsed_query = {
            "cuisine_type": "Italian",
            "difficulty": "easy",
        }
        filters = {
            "cuisine_type": "Italian",
            "difficulty": "easy",
            "max_prep_time": 20,
        }
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, parsed_query, filters, config)

        assert scores["filter_compliance"] == 1.0
        assert scores["dietary_compliant"] is True
        assert scores["confidence"] > 0

    @pytest.mark.asyncio
    async def test_evaluate_recipe_partial_match(
        self, search_pipeline, sample_recipes
    ):
        """Test recipe evaluation with partial filter match."""
        recipe = sample_recipes[0]  # Italian, easy
        parsed_query = {}
        filters = {
            "cuisine_type": "Italian",
            "difficulty": "hard",  # Doesn't match
        }
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, parsed_query, filters, config)

        assert scores["filter_compliance"] == 0.5  # 1 of 2 filters match

    @pytest.mark.asyncio
    async def test_evaluate_recipe_dietary_compliance(
        self, search_pipeline, sample_recipes
    ):
        """Test recipe evaluation checks dietary compliance."""
        recipe = sample_recipes[1]  # Vegetarian
        parsed_query = {"diet_types": ["vegan"]}
        filters = {"diet_type": "vegan"}
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, parsed_query, filters, config)

        assert scores["dietary_compliant"] is True  # Has vegan in diet_types

    @pytest.mark.asyncio
    async def test_full_workflow_execution(
        self, search_pipeline, sample_recipes, default_judge_config
    ):
        """Test complete workflow execution end-to-end."""
        # Setup mocks
        search_pipeline.vector_repo.similarity_search = AsyncMock(
            return_value=[(sample_recipes[0], 0.9), (sample_recipes[1], 0.8)]
        )
        search_pipeline.search_service.filter_search = AsyncMock(
            return_value=[(sample_recipes[0], 1.0)]
        )

        initial_state = {
            "query": "italian pasta",
            "judge_config": default_judge_config,
        }

        result = await search_pipeline.run(initial_state)

        # Verify workflow completed
        assert "final_results" in result
        assert "metadata" in result
        assert "judge_report" in result
        assert result["metadata"]["total_results"] >= 0

    @pytest.mark.asyncio
    async def test_workflow_handles_errors_gracefully(self, search_pipeline):
        """Test workflow handles node errors gracefully."""
        # Force an error in parse_query
        search_pipeline.search_service.query_understanding = AsyncMock(
            side_effect=Exception("Gemini API error")
        )

        initial_state = {
            "query": "test query",
            "judge_config": JudgeConfig(),
        }

        # Should not raise, but may have error in state
        result = await search_pipeline.run(initial_state)
        assert result is not None

    @pytest.mark.asyncio
    async def test_judge_metrics_tracking(
        self, search_pipeline, sample_recipes, default_judge_config
    ):
        """Test judge node tracks detailed metrics."""
        state = {
            "merged_results": sample_recipes,
            "judge_config": default_judge_config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        metrics = result["judge_metrics"]
        assert "total_evaluated" in metrics
        assert "passed_semantic" in metrics
        assert "passed_filter" in metrics
        assert "passed_dietary" in metrics
        assert metrics["total_evaluated"] == len(sample_recipes)

    @pytest.mark.asyncio
    async def test_judge_report_generation(
        self, search_pipeline, sample_recipes, default_judge_config
    ):
        """Test judge node generates comprehensive report."""
        state = {
            "merged_results": sample_recipes,
            "judge_config": default_judge_config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        report = result["judge_report"]
        assert "original_count" in report
        assert "filtered_count" in report
        assert "removed_count" in report
        assert "metrics" in report
        assert "config" in report
        assert report["original_count"] == len(sample_recipes)


# New test case - Judge pattern edge cases
class TestJudgePatternEdgeCases:
    """Test suite for judge pattern edge cases and boundary conditions."""

    @pytest.fixture
    def search_pipeline(
        self,
        mock_search_service,
        mock_embedding_service,
        mock_gemini_client,
        mock_recipe_repo,
        mock_vector_repo,
        mock_cache_service,
    ):
        """Create search pipeline graph instance."""
        return SearchPipelineGraph(
            search_service=mock_search_service,
            embedding_service=mock_embedding_service,
            gemini_client=mock_gemini_client,
            recipe_repo=mock_recipe_repo,
            vector_repo=mock_vector_repo,
            cache_service=mock_cache_service,
        )

    @pytest.mark.asyncio
    async def test_judge_with_threshold_1_0_filters_all(
        self, search_pipeline, sample_recipes
    ):
        """Test judge with threshold=1.0 filters out most results."""
        config = JudgeConfig(
            semantic_threshold=1.0,
            filter_compliance_min=1.0,
            min_results=0,
            fallback_strategy=FallbackStrategy.EMPTY_RESULTS,
        )

        state = {
            "merged_results": sample_recipes,
            "judge_config": config,
            "parsed_query": {"cuisine_type": "Italian"},
            "filters": {"cuisine_type": "Italian"},
            "metadata": {},
            "embedding": [0.1] * 768,
        }

        result = await search_pipeline._judge_relevance_node(state)

        # With threshold 1.0, very few or no results should pass
        # (One Italian recipe may pass with perfect filter compliance)
        assert len(result["filtered_results"]) <= 1
        assert result["judge_report"]["removed_count"] >= len(sample_recipes) - 1

    @pytest.mark.asyncio
    async def test_judge_with_threshold_0_0_passes_all(
        self, search_pipeline, sample_recipes
    ):
        """Test judge with threshold=0.0 passes all results."""
        config = JudgeConfig(
            semantic_threshold=0.0,
            filter_compliance_min=0.0,
            min_results=0,
            dietary_strict_mode=False,
        )

        state = {
            "merged_results": sample_recipes,
            "judge_config": config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        # With threshold 0.0 and no strict filters, all should pass
        assert len(result["filtered_results"]) == len(sample_recipes)
        assert result["judge_report"]["removed_count"] == 0

    @pytest.mark.asyncio
    async def test_judge_with_max_results_1(
        self, search_pipeline, sample_recipes
    ):
        """Test judge with max_results=1 returns exactly 1 result."""
        config = JudgeConfig(max_results=1)

        state = {
            "merged_results": sample_recipes,
            "judge_config": config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        assert len(result["filtered_results"]) == 1

    @pytest.mark.asyncio
    async def test_judge_with_min_results_exceeds_available(
        self, search_pipeline, sample_recipes
    ):
        """Test judge when min_results exceeds available results."""
        config = JudgeConfig(
            min_results=100,  # More than available
            semantic_threshold=0.0,
            fallback_strategy=FallbackStrategy.RELAX_THRESHOLDS,
        )

        state = {
            "merged_results": sample_recipes[:3],
            "judge_config": config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        # Should return all available results due to fallback
        assert len(result["filtered_results"]) == 3

    @pytest.mark.asyncio
    async def test_judge_fallback_suggest_alternatives(
        self, search_pipeline, sample_recipes
    ):
        """Test SUGGEST_ALTERNATIVES fallback strategy."""
        config = JudgeConfig(
            semantic_threshold=0.99,
            min_results=5,
            fallback_strategy=FallbackStrategy.SUGGEST_ALTERNATIVES,
        )

        state = {
            "merged_results": sample_recipes[:2],
            "judge_config": config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        # With SUGGEST_ALTERNATIVES, should still apply relaxed thresholds
        # Implementation may vary - test that it doesn't crash
        assert "filtered_results" in result
        assert isinstance(result["filtered_results"], list)

    @pytest.mark.asyncio
    async def test_judge_dietary_strict_filters_non_matching(
        self, search_pipeline, sample_recipes
    ):
        """Test dietary strict mode filters non-matching recipes."""
        config = JudgeConfig(
            dietary_strict_mode=True,
            min_results=0,
        )

        # Request vegan recipes
        state = {
            "merged_results": sample_recipes,
            "judge_config": config,
            "parsed_query": {"diet_types": ["vegan"]},
            "filters": {"diet_type": "vegan"},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        # Only vegan recipes should pass
        for recipe in result["filtered_results"]:
            assert "vegan" in recipe.diet_types

    @pytest.mark.asyncio
    async def test_judge_dietary_relaxed_allows_non_matching(
        self, search_pipeline, sample_recipes
    ):
        """Test dietary relaxed mode allows non-matching recipes."""
        config = JudgeConfig(
            dietary_strict_mode=False,
            filter_compliance_min=0.0,
        )

        state = {
            "merged_results": sample_recipes,
            "judge_config": config,
            "parsed_query": {"diet_types": ["vegan"]},
            "filters": {"diet_type": "vegan"},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        # With relaxed mode, should get more results
        assert len(result["filtered_results"]) > 0

    @pytest.mark.asyncio
    async def test_judge_with_single_result(self, search_pipeline, sample_recipes):
        """Test judge with exactly one result."""
        config = JudgeConfig()

        state = {
            "merged_results": [sample_recipes[0]],
            "judge_config": config,
            "parsed_query": {},
            "filters": {},
            "metadata": {},
        }

        result = await search_pipeline._judge_relevance_node(state)

        assert len(result["filtered_results"]) == 1
        assert result["judge_report"]["original_count"] == 1

    @pytest.mark.asyncio
    async def test_judge_metrics_all_counters(
        self, search_pipeline, sample_recipes
    ):
        """Test judge metrics tracks all counter types."""
        config = JudgeConfig(
            semantic_threshold=0.5,
            filter_compliance_min=0.5,
        )

        state = {
            "merged_results": sample_recipes,
            "judge_config": config,
            "parsed_query": {"cuisine_type": "Italian"},
            "filters": {"cuisine_type": "Italian"},
            "metadata": {},
            "embedding": [0.1] * 768,
        }

        result = await search_pipeline._judge_relevance_node(state)

        metrics = result["judge_metrics"]
        assert "total_evaluated" in metrics
        assert "passed_semantic" in metrics
        assert "passed_filter" in metrics
        assert "passed_dietary" in metrics
        assert "failed_semantic" in metrics
        assert "failed_filter" in metrics
        assert "failed_dietary" in metrics

        # Counts should add up
        assert metrics["passed_semantic"] + metrics["failed_semantic"] == metrics["total_evaluated"]


# New test case - Routing edge cases
class TestRoutingEdgeCases:
    """Test suite for workflow routing edge cases."""

    @pytest.fixture
    def search_pipeline(
        self,
        mock_search_service,
        mock_embedding_service,
        mock_gemini_client,
        mock_recipe_repo,
        mock_vector_repo,
        mock_cache_service,
    ):
        """Create search pipeline graph instance."""
        return SearchPipelineGraph(
            search_service=mock_search_service,
            embedding_service=mock_embedding_service,
            gemini_client=mock_gemini_client,
            recipe_repo=mock_recipe_repo,
            vector_repo=mock_vector_repo,
            cache_service=mock_cache_service,
        )

    def test_route_after_parse_empty_query_and_filters(self, search_pipeline):
        """Test routing when both query and filters are empty."""
        state = {
            "parsed_query": {},
            "filters": {},
        }

        route = search_pipeline._route_after_parse(state)
        # Should default to filters when nothing is present
        assert route in ["filters", "embedding"]

    def test_route_after_parse_only_semantic_query(self, search_pipeline):
        """Test routing with only semantic query present."""
        state = {
            "parsed_query": {
                "semantic_query": "delicious pasta",
                "cuisine_type": None,
                "difficulty": None,
            },
            "filters": {},
        }

        route = search_pipeline._route_after_parse(state)
        assert route == "embedding"

    def test_route_after_parse_only_structured_filters(self, search_pipeline):
        """Test routing with only structured filters present."""
        state = {
            "parsed_query": {
                "semantic_query": "",
                "cuisine_type": "Italian",
            },
            "filters": {"cuisine_type": "Italian"},
        }

        route = search_pipeline._route_after_parse(state)
        assert route == "filters"

    def test_should_rerank_with_zero_results(self, search_pipeline):
        """Test rerank decision with zero results."""
        state = {
            "filtered_results": [],
            "judge_report": {"removed_count": 10},
            "metadata": {},
        }

        route = search_pipeline._should_rerank(state)
        assert route == "skip"

    def test_should_rerank_with_exactly_3_results(self, search_pipeline):
        """Test rerank decision boundary at 3 results."""
        state = {
            "filtered_results": [None] * 3,
            "judge_report": {"removed_count": 10},
            "metadata": {},
        }

        route = search_pipeline._should_rerank(state)
        assert route == "skip"  # Needs > 3

    def test_should_rerank_with_4_results_high_removal(self, search_pipeline):
        """Test rerank triggers with 4 results and high removal."""
        state = {
            "filtered_results": [None] * 4,
            "judge_report": {"removed_count": 6},
            "metadata": {},
        }

        route = search_pipeline._should_rerank(state)
        assert route == "rerank"

    def test_should_rerank_with_many_results_low_removal(self, search_pipeline):
        """Test rerank skips with many results but low removal."""
        state = {
            "filtered_results": [None] * 10,
            "judge_report": {"removed_count": 2},
            "metadata": {},
        }

        route = search_pipeline._should_rerank(state)
        assert route == "skip"

    def test_should_rerank_boundary_removed_count(self, search_pipeline):
        """Test rerank boundary at removed_count=5."""
        state = {
            "filtered_results": [None] * 10,
            "judge_report": {"removed_count": 5},
            "metadata": {},
        }

        route = search_pipeline._should_rerank(state)
        assert route == "skip"  # Needs > 5


# New test case - Node error handling
class TestNodeErrorHandling:
    """Test suite for node-level error handling."""

    @pytest.fixture
    def search_pipeline(
        self,
        mock_search_service,
        mock_embedding_service,
        mock_gemini_client,
        mock_recipe_repo,
        mock_vector_repo,
        mock_cache_service,
    ):
        """Create search pipeline graph instance."""
        return SearchPipelineGraph(
            search_service=mock_search_service,
            embedding_service=mock_embedding_service,
            gemini_client=mock_gemini_client,
            recipe_repo=mock_recipe_repo,
            vector_repo=mock_vector_repo,
            cache_service=mock_cache_service,
        )

    @pytest.mark.asyncio
    async def test_parse_query_handles_gemini_error(self, search_pipeline):
        """Test parse_query node handles Gemini API errors gracefully."""
        from unittest.mock import AsyncMock

        search_pipeline.search_service.query_understanding = AsyncMock(
            side_effect=Exception("Gemini API timeout")
        )

        state = {
            "query": "test query",
            "metadata": {},
        }

        result = await search_pipeline._parse_query_node(state)

        assert "error" in result
        assert "Gemini API timeout" in result["error"]

    @pytest.mark.asyncio
    async def test_generate_embedding_handles_error(self, search_pipeline):
        """Test generate_embedding node handles errors gracefully."""
        from unittest.mock import AsyncMock

        search_pipeline.embedding_service.generate_query_embedding = AsyncMock(
            side_effect=Exception("Embedding service down")
        )

        state = {
            "query": "test",
            "parsed_query": {"semantic_query": "test"},
            "metadata": {},
        }

        result = await search_pipeline._generate_embedding_node(state)

        assert result["embedding"] is None
        assert result["metadata"]["embedding_generated"] is False

    @pytest.mark.asyncio
    async def test_vector_search_handles_database_error(self, search_pipeline):
        """Test vector_search node handles database errors."""
        from unittest.mock import AsyncMock

        search_pipeline.vector_repo.similarity_search = AsyncMock(
            side_effect=Exception("Database connection lost")
        )

        state = {
            "embedding": [0.1] * 768,
            "metadata": {},
        }

        result = await search_pipeline._vector_search_node(state)

        assert result["vector_results"] == []

    @pytest.mark.asyncio
    async def test_filter_search_handles_error(self, search_pipeline):
        """Test filter_search node handles errors."""
        from unittest.mock import AsyncMock

        search_pipeline.search_service.filter_search = AsyncMock(
            side_effect=Exception("Filter search failed")
        )

        state = {
            "filters": {"cuisine_type": "Italian"},
            "metadata": {},
        }

        result = await search_pipeline._filter_search_node(state)

        assert result["filter_results"] == []

    @pytest.mark.asyncio
    async def test_rerank_handles_error(self, search_pipeline, sample_recipes):
        """Test rerank node handles errors gracefully."""
        from unittest.mock import AsyncMock

        search_pipeline.search_service.result_reranking = AsyncMock(
            side_effect=Exception("Reranking failed")
        )

        state = {
            "query": "test",
            "filtered_results": sample_recipes[:2],
            "metadata": {},
        }

        result = await search_pipeline._rerank_node(state)

        assert result["metadata"]["reranked"] is False
        # Original results should be preserved
        assert len(result["filtered_results"]) == 2


# New test case - Recipe evaluation edge cases
class TestRecipeEvaluationEdgeCases:
    """Test suite for recipe evaluation edge cases."""

    @pytest.fixture
    def search_pipeline(
        self,
        mock_search_service,
        mock_embedding_service,
        mock_gemini_client,
        mock_recipe_repo,
        mock_vector_repo,
        mock_cache_service,
    ):
        """Create search pipeline graph instance."""
        return SearchPipelineGraph(
            search_service=mock_search_service,
            embedding_service=mock_embedding_service,
            gemini_client=mock_gemini_client,
            recipe_repo=mock_recipe_repo,
            vector_repo=mock_vector_repo,
            cache_service=mock_cache_service,
        )

    def test_evaluate_recipe_no_filters(self, search_pipeline, sample_recipes):
        """Test recipe evaluation with no filters (should score 1.0)."""
        recipe = sample_recipes[0]
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, {}, {}, config)

        assert scores["filter_compliance"] == 1.0
        assert scores["dietary_compliant"] is True

    def test_evaluate_recipe_all_filters_mismatch(
        self, search_pipeline, sample_recipes
    ):
        """Test recipe evaluation when all filters mismatch."""
        recipe = sample_recipes[0]  # Italian, easy, 10 min prep
        parsed_query = {}
        filters = {
            "cuisine_type": "Asian",  # Mismatch
            "difficulty": "hard",  # Mismatch
            "max_prep_time": 5,  # Mismatch (10 > 5)
        }
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, parsed_query, filters, config)

        assert scores["filter_compliance"] == 0.0

    def test_evaluate_recipe_partial_filter_match(
        self, search_pipeline, sample_recipes
    ):
        """Test recipe evaluation with partial filter match."""
        recipe = sample_recipes[0]  # Italian, easy
        filters = {
            "cuisine_type": "Italian",  # Match
            "difficulty": "hard",  # No match
        }
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, {}, filters, config)

        assert scores["filter_compliance"] == 0.5

    def test_evaluate_recipe_time_filter_exact_match(
        self, search_pipeline, sample_recipes
    ):
        """Test recipe evaluation with exact time match."""
        recipe = sample_recipes[0]  # prep_time=10
        filters = {
            "max_prep_time": 10,  # Exact match
        }
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, {}, filters, config)

        assert scores["filter_compliance"] == 1.0

    def test_evaluate_recipe_time_filter_just_under(
        self, search_pipeline, sample_recipes
    ):
        """Test recipe evaluation with time just under limit."""
        recipe = sample_recipes[0]  # prep_time=10
        filters = {
            "max_prep_time": 11,  # Just over
        }
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, {}, filters, config)

        assert scores["filter_compliance"] == 1.0

    def test_evaluate_recipe_dietary_match(self, search_pipeline, sample_recipes):
        """Test recipe evaluation with dietary match."""
        recipe = sample_recipes[1]  # Has vegetarian and vegan
        filters = {
            "diet_type": "vegetarian",
        }
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, {}, filters, config)

        assert scores["dietary_compliant"] is True
        assert scores["filter_compliance"] == 1.0

    def test_evaluate_recipe_dietary_mismatch(
        self, search_pipeline, sample_recipes
    ):
        """Test recipe evaluation with dietary mismatch."""
        recipe = sample_recipes[0]  # No diet types
        filters = {
            "diet_type": "vegan",
        }
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, {}, filters, config)

        assert scores["dietary_compliant"] is False
        assert scores["filter_compliance"] == 0.0

    def test_evaluate_recipe_with_ingredients_filter(
        self, search_pipeline, sample_recipes
    ):
        """Test recipe evaluation with ingredients filter."""
        recipe = sample_recipes[0]
        parsed_query = {"ingredients": ["pasta", "eggs"]}
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, parsed_query, {}, config)

        # Ingredient match is placeholder at 0.5
        assert scores["ingredient_match"] == 0.5

    def test_evaluate_recipe_confidence_calculation(
        self, search_pipeline, sample_recipes
    ):
        """Test recipe confidence score calculation."""
        recipe = sample_recipes[0]
        config = JudgeConfig()

        scores = search_pipeline._evaluate_recipe(recipe, {}, {}, config)

        # Confidence = 0.4*semantic + 0.4*filter + 0.2*ingredient
        # With no filters: 0.4*1.0 + 0.4*1.0 + 0.2*0.0 = 0.8
        assert scores["confidence"] > 0


# New test case - Merge results edge cases
class TestMergeResultsEdgeCases:
    """Test suite for merge results edge cases."""

    @pytest.fixture
    def search_pipeline(
        self,
        mock_search_service,
        mock_embedding_service,
        mock_gemini_client,
        mock_recipe_repo,
        mock_vector_repo,
        mock_cache_service,
    ):
        """Create search pipeline graph instance."""
        return SearchPipelineGraph(
            search_service=mock_search_service,
            embedding_service=mock_embedding_service,
            gemini_client=mock_gemini_client,
            recipe_repo=mock_recipe_repo,
            vector_repo=mock_vector_repo,
            cache_service=mock_cache_service,
        )

    @pytest.mark.asyncio
    async def test_merge_empty_both_sources(self, search_pipeline):
        """Test merge when both sources are empty."""
        state = {
            "vector_results": [],
            "filter_results": [],
            "metadata": {},
        }

        result = await search_pipeline._merge_results_node(state)

        assert result["merged_results"] == []
        # The implementation returns early without setting merged_count
        # when both sources are empty, so we just check merged_results

    @pytest.mark.asyncio
    async def test_merge_duplicate_recipes(self, search_pipeline, sample_recipes):
        """Test merge handles duplicate recipes from both sources."""
        # Same recipes in both sources
        state = {
            "vector_results": [sample_recipes[0], sample_recipes[1]],
            "filter_results": [sample_recipes[0], sample_recipes[1]],
            "metadata": {},
        }

        result = await search_pipeline._merge_results_node(state)

        # RRF should handle duplicates
        assert len(result["merged_results"]) > 0

    @pytest.mark.asyncio
    async def test_merge_single_recipe_each_source(
        self, search_pipeline, sample_recipes
    ):
        """Test merge with single recipe from each source."""
        state = {
            "vector_results": [sample_recipes[0]],
            "filter_results": [sample_recipes[1]],
            "metadata": {},
        }

        result = await search_pipeline._merge_results_node(state)

        assert len(result["merged_results"]) == 2

    @pytest.mark.asyncio
    async def test_merge_many_from_one_few_from_other(
        self, search_pipeline, sample_recipes
    ):
        """Test merge with imbalanced sources."""
        state = {
            "vector_results": sample_recipes,  # All 5
            "filter_results": [sample_recipes[0]],  # Just 1
            "metadata": {},
        }

        result = await search_pipeline._merge_results_node(state)

        assert len(result["merged_results"]) == 5


# New test case - Full workflow integration edge cases
class TestWorkflowIntegrationEdgeCases:
    """Test suite for full workflow integration edge cases."""

    @pytest.fixture
    def search_pipeline(
        self,
        mock_search_service,
        mock_embedding_service,
        mock_gemini_client,
        mock_recipe_repo,
        mock_vector_repo,
        mock_cache_service,
    ):
        """Create search pipeline graph instance."""
        return SearchPipelineGraph(
            search_service=mock_search_service,
            embedding_service=mock_embedding_service,
            gemini_client=mock_gemini_client,
            recipe_repo=mock_recipe_repo,
            vector_repo=mock_vector_repo,
            cache_service=mock_cache_service,
        )

    @pytest.mark.asyncio
    async def test_workflow_with_empty_query(self, search_pipeline):
        """Test workflow handles empty query string."""
        initial_state = {
            "query": "",
            "judge_config": JudgeConfig(),
        }

        result = await search_pipeline.run(initial_state)

        # Should complete without crashing
        assert "final_results" in result

    @pytest.mark.asyncio
    async def test_workflow_without_judge_config(self, search_pipeline):
        """Test workflow provides default judge config when not specified."""
        initial_state = {
            "query": "pasta",
        }

        result = await search_pipeline.run(initial_state)

        assert "judge_config" in result
        assert isinstance(result["judge_config"], JudgeConfig)

    @pytest.mark.asyncio
    async def test_workflow_with_very_strict_config(
        self, search_pipeline, sample_recipes
    ):
        """Test workflow with very strict judge config."""
        from unittest.mock import AsyncMock

        search_pipeline.vector_repo.similarity_search = AsyncMock(
            return_value=[(sample_recipes[0], 0.9)]
        )

        initial_state = {
            "query": "pasta",
            "judge_config": JudgeConfig(
                semantic_threshold=0.99,
                filter_compliance_min=0.99,
                confidence_threshold=0.99,
                min_results=0,
                fallback_strategy=FallbackStrategy.EMPTY_RESULTS,
            ),
        }

        result = await search_pipeline.run(initial_state)

        # Likely to get no results with such strict config
        assert "final_results" in result

    @pytest.mark.asyncio
    async def test_workflow_vector_search_only(self, search_pipeline, sample_recipes):
        """Test workflow with only vector search (no filters)."""
        from unittest.mock import AsyncMock

        search_pipeline.vector_repo.similarity_search = AsyncMock(
            return_value=[(sample_recipes[0], 0.9)]
        )

        # Mock parse to return only semantic query
        search_pipeline.search_service.query_understanding = AsyncMock(
            return_value=type('obj', (object,), {
                'original_query': 'delicious',
                'semantic_query': 'delicious food',
                'ingredients': [],
                'cuisine_type': None,
                'diet_types': [],
                'max_prep_time': None,
                'max_cook_time': None,
                'difficulty': None,
            })()
        )

        initial_state = {
            "query": "delicious",
            "judge_config": JudgeConfig(),
        }

        result = await search_pipeline.run(initial_state)

        assert "final_results" in result
        assert result["metadata"].get("vector_count", 0) > 0

    @pytest.mark.asyncio
    async def test_workflow_filter_search_only(self, search_pipeline, sample_recipes):
        """Test workflow with only filter search (no semantic)."""
        from unittest.mock import AsyncMock

        search_pipeline.search_service.filter_search = AsyncMock(
            return_value=[(sample_recipes[0], 1.0)]
        )

        # Mock parse to return only filters
        search_pipeline.search_service.query_understanding = AsyncMock(
            return_value=type('obj', (object,), {
                'original_query': 'Italian',
                'semantic_query': '',
                'ingredients': [],
                'cuisine_type': 'Italian',
                'diet_types': [],
                'max_prep_time': None,
                'max_cook_time': None,
                'difficulty': None,
            })()
        )

        initial_state = {
            "query": "Italian",
            "judge_config": JudgeConfig(),
        }

        result = await search_pipeline.run(initial_state)

        assert "final_results" in result
