"""Tests for workflow state schemas."""

import pytest
from pydantic import ValidationError

from app.workflows.states import (
    JudgeConfig,
    FallbackStrategy,
    SearchPipelineState,
    RecipeProcessingState,
)


class TestJudgeConfig:
    """Test suite for JudgeConfig schema."""

    def test_judge_config_defaults(self):
        """Test JudgeConfig initializes with proper defaults."""
        config = JudgeConfig()

        assert config.semantic_threshold == 0.0
        assert config.filter_compliance_min == 0.0
        assert config.ingredient_match_min == 0.0
        assert config.dietary_strict_mode is True
        assert config.confidence_threshold == 0.0
        assert config.min_results == 0
        assert config.max_results == 100
        assert config.fallback_strategy == FallbackStrategy.RELAX_THRESHOLDS

    def test_judge_config_custom_values(self):
        """Test JudgeConfig accepts custom values."""
        config = JudgeConfig(
            semantic_threshold=0.7,
            filter_compliance_min=0.8,
            ingredient_match_min=0.6,
            dietary_strict_mode=False,
            confidence_threshold=0.5,
            min_results=5,
            max_results=50,
            fallback_strategy=FallbackStrategy.EMPTY_RESULTS,
        )

        assert config.semantic_threshold == 0.7
        assert config.filter_compliance_min == 0.8
        assert config.ingredient_match_min == 0.6
        assert config.dietary_strict_mode is False
        assert config.confidence_threshold == 0.5
        assert config.min_results == 5
        assert config.max_results == 50
        assert config.fallback_strategy == FallbackStrategy.EMPTY_RESULTS

    def test_judge_config_validates_threshold_range(self):
        """Test JudgeConfig validates threshold values are in 0-1 range."""
        # Valid thresholds
        config = JudgeConfig(semantic_threshold=0.5)
        assert config.semantic_threshold == 0.5

        config = JudgeConfig(semantic_threshold=0.0)
        assert config.semantic_threshold == 0.0

        config = JudgeConfig(semantic_threshold=1.0)
        assert config.semantic_threshold == 1.0

        # Invalid thresholds
        with pytest.raises(ValidationError):
            JudgeConfig(semantic_threshold=1.5)

        with pytest.raises(ValidationError):
            JudgeConfig(semantic_threshold=-0.1)

    def test_judge_config_validates_min_results(self):
        """Test JudgeConfig validates min_results is non-negative."""
        config = JudgeConfig(min_results=0)
        assert config.min_results == 0

        config = JudgeConfig(min_results=10)
        assert config.min_results == 10

        with pytest.raises(ValidationError):
            JudgeConfig(min_results=-1)

    def test_judge_config_validates_max_results(self):
        """Test JudgeConfig validates max_results is positive."""
        config = JudgeConfig(max_results=1)
        assert config.max_results == 1

        config = JudgeConfig(max_results=100)
        assert config.max_results == 100

        with pytest.raises(ValidationError):
            JudgeConfig(max_results=0)

        with pytest.raises(ValidationError):
            JudgeConfig(max_results=-1)

    def test_judge_config_fallback_strategies(self):
        """Test JudgeConfig accepts all fallback strategies."""
        config = JudgeConfig(fallback_strategy=FallbackStrategy.RELAX_THRESHOLDS)
        assert config.fallback_strategy == FallbackStrategy.RELAX_THRESHOLDS

        config = JudgeConfig(fallback_strategy=FallbackStrategy.EMPTY_RESULTS)
        assert config.fallback_strategy == FallbackStrategy.EMPTY_RESULTS

        config = JudgeConfig(fallback_strategy=FallbackStrategy.SUGGEST_ALTERNATIVES)
        assert config.fallback_strategy == FallbackStrategy.SUGGEST_ALTERNATIVES

    def test_judge_config_model_dump(self):
        """Test JudgeConfig can be serialized to dict."""
        config = JudgeConfig(
            semantic_threshold=0.8,
            min_results=5,
        )

        dumped = config.model_dump()

        assert isinstance(dumped, dict)
        assert dumped["semantic_threshold"] == 0.8
        assert dumped["min_results"] == 5

    def test_judge_config_strict_mode_defaults_true(self):
        """Test dietary_strict_mode defaults to True for safety."""
        config = JudgeConfig()
        assert config.dietary_strict_mode is True


class TestFallbackStrategy:
    """Test suite for FallbackStrategy enum."""

    def test_fallback_strategy_values(self):
        """Test FallbackStrategy has expected values."""
        assert FallbackStrategy.RELAX_THRESHOLDS == "RELAX_THRESHOLDS"
        assert FallbackStrategy.EMPTY_RESULTS == "EMPTY_RESULTS"
        assert FallbackStrategy.SUGGEST_ALTERNATIVES == "SUGGEST_ALTERNATIVES"

    def test_fallback_strategy_is_string_enum(self):
        """Test FallbackStrategy is a string enum."""
        strategy = FallbackStrategy.RELAX_THRESHOLDS
        assert isinstance(strategy, str)
        assert isinstance(strategy.value, str)


class TestSearchPipelineState:
    """Test suite for SearchPipelineState TypedDict."""

    def test_search_pipeline_state_structure(self):
        """Test SearchPipelineState has expected structure."""
        # TypedDict doesn't enforce runtime validation, but we can verify structure
        state: SearchPipelineState = {
            "query": "test query",
            "parsed_query": {},
            "filters": {},
            "embedding": None,
            "vector_results": [],
            "filter_results": [],
            "merged_results": [],
            "judge_metrics": {},
            "filtered_results": [],
            "judge_report": {},
            "final_results": [],
            "metadata": {},
            "judge_config": JudgeConfig(),
            "error": None,
        }

        assert state["query"] == "test query"
        assert isinstance(state["parsed_query"], dict)
        assert isinstance(state["filters"], dict)

    def test_search_pipeline_state_partial(self):
        """Test SearchPipelineState allows partial initialization."""
        # TypedDict with total=False allows partial states
        state: SearchPipelineState = {
            "query": "test",
        }

        assert state["query"] == "test"

    def test_search_pipeline_state_with_results(self):
        """Test SearchPipelineState can hold search results."""
        from app.db.models import Recipe, DifficultyLevel
        from uuid import uuid4

        recipe = Recipe(
            id=uuid4(),
            name="Test Recipe",
            description="Test",
            instructions={"steps": []},
            difficulty=DifficultyLevel.EASY,
        )

        state: SearchPipelineState = {
            "query": "test",
            "vector_results": [recipe],
            "filter_results": [recipe],
            "merged_results": [recipe],
            "filtered_results": [recipe],
            "final_results": [recipe],
        }

        assert len(state["vector_results"]) == 1
        assert state["vector_results"][0].name == "Test Recipe"


class TestRecipeProcessingState:
    """Test suite for RecipeProcessingState TypedDict."""

    def test_recipe_processing_state_structure(self):
        """Test RecipeProcessingState has expected structure."""
        state: RecipeProcessingState = {
            "recipe_data": {},
            "validation_errors": [],
            "extracted_entities": {},
            "embedding": [],
            "enriched_data": {},
            "nutritional_info": {},
            "recipe_id": None,
            "error": None,
        }

        assert isinstance(state["recipe_data"], dict)
        assert isinstance(state["validation_errors"], list)
        assert isinstance(state["extracted_entities"], dict)

    def test_recipe_processing_state_partial(self):
        """Test RecipeProcessingState allows partial initialization."""
        state: RecipeProcessingState = {
            "recipe_data": {"name": "Test Recipe"},
        }

        assert state["recipe_data"]["name"] == "Test Recipe"

    def test_recipe_processing_state_with_errors(self):
        """Test RecipeProcessingState can track errors."""
        state: RecipeProcessingState = {
            "recipe_data": {},
            "validation_errors": ["Name is required", "Invalid prep time"],
            "error": "Validation failed",
        }

        assert len(state["validation_errors"]) == 2
        assert state["error"] == "Validation failed"

    def test_recipe_processing_state_with_embedding(self):
        """Test RecipeProcessingState can store embedding vector."""
        embedding = [0.1] * 768

        state: RecipeProcessingState = {
            "recipe_data": {},
            "embedding": embedding,
        }

        assert len(state["embedding"]) == 768
        assert state["embedding"][0] == 0.1


class TestStateIntegration:
    """Integration tests for state schemas."""

    def test_judge_config_in_search_state(self):
        """Test JudgeConfig integrates properly with SearchPipelineState."""
        judge_config = JudgeConfig(
            semantic_threshold=0.7,
            min_results=5,
        )

        state: SearchPipelineState = {
            "query": "test",
            "judge_config": judge_config,
            "metadata": {
                "config_used": judge_config.model_dump(),
            },
        }

        assert state["judge_config"].semantic_threshold == 0.7
        assert state["metadata"]["config_used"]["semantic_threshold"] == 0.7

    def test_judge_report_structure(self):
        """Test judge_report field has expected structure."""
        state: SearchPipelineState = {
            "query": "test",
            "judge_report": {
                "original_count": 10,
                "filtered_count": 5,
                "removed_count": 5,
                "metrics": {
                    "total_evaluated": 10,
                    "passed_semantic": 8,
                    "passed_filter": 6,
                },
                "config": JudgeConfig().model_dump(),
            },
        }

        report = state["judge_report"]
        assert report["original_count"] == 10
        assert report["filtered_count"] == 5
        assert report["removed_count"] == 5
        assert "metrics" in report
        assert "config" in report

    def test_metadata_field_flexibility(self):
        """Test metadata field can store arbitrary data."""
        state: SearchPipelineState = {
            "query": "test",
            "metadata": {
                "parsed_at": "parse_query_node",
                "embedding_generated": True,
                "vector_count": 10,
                "filter_count": 5,
                "merged_count": 12,
                "reranked": False,
                "total_results": 12,
                "custom_field": "custom_value",
            },
        }

        metadata = state["metadata"]
        assert metadata["parsed_at"] == "parse_query_node"
        assert metadata["embedding_generated"] is True
        assert metadata["vector_count"] == 10
        assert metadata["custom_field"] == "custom_value"


# New test case - Edge cases and boundary conditions
class TestJudgeConfigEdgeCases:
    """Test suite for JudgeConfig edge cases and boundary conditions."""

    def test_all_thresholds_at_boundary_zero(self):
        """Test all thresholds can be set to 0.0 (minimum boundary)."""
        config = JudgeConfig(
            semantic_threshold=0.0,
            filter_compliance_min=0.0,
            ingredient_match_min=0.0,
            confidence_threshold=0.0,
        )

        assert config.semantic_threshold == 0.0
        assert config.filter_compliance_min == 0.0
        assert config.ingredient_match_min == 0.0
        assert config.confidence_threshold == 0.0

    def test_all_thresholds_at_boundary_one(self):
        """Test all thresholds can be set to 1.0 (maximum boundary)."""
        config = JudgeConfig(
            semantic_threshold=1.0,
            filter_compliance_min=1.0,
            ingredient_match_min=1.0,
            confidence_threshold=1.0,
        )

        assert config.semantic_threshold == 1.0
        assert config.filter_compliance_min == 1.0
        assert config.ingredient_match_min == 1.0
        assert config.confidence_threshold == 1.0

    def test_threshold_validation_just_above_upper_bound(self):
        """Test threshold validation fails just above 1.0."""
        with pytest.raises(ValidationError):
            JudgeConfig(semantic_threshold=1.001)

        with pytest.raises(ValidationError):
            JudgeConfig(filter_compliance_min=1.1)

        with pytest.raises(ValidationError):
            JudgeConfig(ingredient_match_min=2.0)

    def test_threshold_validation_just_below_lower_bound(self):
        """Test threshold validation fails just below 0.0."""
        with pytest.raises(ValidationError):
            JudgeConfig(semantic_threshold=-0.001)

        with pytest.raises(ValidationError):
            JudgeConfig(filter_compliance_min=-0.1)

        with pytest.raises(ValidationError):
            JudgeConfig(confidence_threshold=-1.0)

    def test_min_results_equals_max_results(self):
        """Test min_results can equal max_results (exact count)."""
        config = JudgeConfig(min_results=5, max_results=5)

        assert config.min_results == 5
        assert config.max_results == 5

    def test_min_results_zero_max_results_one(self):
        """Test edge case with min=0, max=1."""
        config = JudgeConfig(min_results=0, max_results=1)

        assert config.min_results == 0
        assert config.max_results == 1

    def test_max_results_boundary_minimum(self):
        """Test max_results boundary at minimum value of 1."""
        config = JudgeConfig(max_results=1)
        assert config.max_results == 1

    def test_max_results_large_value(self):
        """Test max_results handles large values."""
        config = JudgeConfig(max_results=10000)
        assert config.max_results == 10000

    def test_invalid_fallback_strategy_string(self):
        """Test invalid fallback strategy string is rejected."""
        with pytest.raises(ValidationError):
            JudgeConfig(fallback_strategy="INVALID_STRATEGY")

    def test_all_fallback_strategies_are_valid(self):
        """Test each fallback strategy value is valid."""
        for strategy in FallbackStrategy:
            config = JudgeConfig(fallback_strategy=strategy)
            assert config.fallback_strategy == strategy

    def test_strict_dietary_mode_combinations(self):
        """Test dietary_strict_mode with various threshold combinations."""
        # Strict dietary with permissive thresholds
        config = JudgeConfig(
            dietary_strict_mode=True,
            semantic_threshold=0.0,
            filter_compliance_min=0.0,
        )
        assert config.dietary_strict_mode is True

        # Relaxed dietary with strict thresholds
        config = JudgeConfig(
            dietary_strict_mode=False,
            semantic_threshold=0.9,
            filter_compliance_min=0.9,
        )
        assert config.dietary_strict_mode is False

    def test_config_serialization_deserialization(self):
        """Test JudgeConfig can be serialized and deserialized."""
        original = JudgeConfig(
            semantic_threshold=0.75,
            min_results=3,
            max_results=20,
            fallback_strategy=FallbackStrategy.SUGGEST_ALTERNATIVES,
        )

        # Serialize
        dumped = original.model_dump()

        # Deserialize
        restored = JudgeConfig(**dumped)

        assert restored.semantic_threshold == original.semantic_threshold
        assert restored.min_results == original.min_results
        assert restored.max_results == original.max_results
        assert restored.fallback_strategy == original.fallback_strategy

    def test_config_with_empty_dict_initialization(self):
        """Test JudgeConfig can be created with empty dict (all defaults)."""
        config = JudgeConfig(**{})

        assert config.semantic_threshold == 0.0
        assert config.min_results == 0
        assert config.max_results == 100

    def test_extreme_min_max_results_difference(self):
        """Test extreme difference between min and max results."""
        config = JudgeConfig(min_results=0, max_results=10000)

        assert config.min_results == 0
        assert config.max_results == 10000


# New test case - SearchPipelineState edge cases
class TestSearchPipelineStateEdgeCases:
    """Test suite for SearchPipelineState edge cases."""

    def test_state_with_null_values(self):
        """Test SearchPipelineState handles null/None values properly."""
        state: SearchPipelineState = {
            "query": "test",
            "embedding": None,
            "error": None,
            "judge_config": JudgeConfig(),
            "parsed_query": {},
            "filters": {},
            "vector_results": [],
            "filter_results": [],
        }

        assert state["embedding"] is None
        assert state["error"] is None

    def test_state_with_empty_results_lists(self):
        """Test SearchPipelineState with all empty result lists."""
        state: SearchPipelineState = {
            "query": "test",
            "vector_results": [],
            "filter_results": [],
            "merged_results": [],
            "filtered_results": [],
            "final_results": [],
        }

        assert len(state["vector_results"]) == 0
        assert len(state["filter_results"]) == 0
        assert len(state["merged_results"]) == 0

    def test_state_with_error_and_partial_results(self):
        """Test SearchPipelineState with error but partial results present."""
        from app.db.models import Recipe, DifficultyLevel
        from uuid import uuid4

        recipe = Recipe(
            id=uuid4(),
            name="Test",
            description="Test",
            instructions={},
            difficulty=DifficultyLevel.EASY,
        )

        state: SearchPipelineState = {
            "query": "test",
            "error": "Vector search failed",
            "vector_results": [recipe],  # Partial success
            "filter_results": [],  # Failed part
        }

        assert state["error"] == "Vector search failed"
        assert len(state["vector_results"]) == 1

    def test_judge_report_with_zero_results(self):
        """Test judge_report structure when no results processed."""
        state: SearchPipelineState = {
            "query": "test",
            "judge_report": {
                "original_count": 0,
                "filtered_count": 0,
                "removed_count": 0,
                "metrics": {},
            },
        }

        assert state["judge_report"]["original_count"] == 0
        assert state["judge_report"]["filtered_count"] == 0

    def test_judge_report_all_results_filtered(self):
        """Test judge_report when all results were filtered out."""
        state: SearchPipelineState = {
            "query": "test",
            "judge_report": {
                "original_count": 100,
                "filtered_count": 0,
                "removed_count": 100,
                "reason": "All failed threshold check",
            },
        }

        assert state["judge_report"]["removed_count"] == 100
        assert state["judge_report"]["filtered_count"] == 0


# New test case - RecipeProcessingState edge cases
class TestRecipeProcessingStateEdgeCases:
    """Test suite for RecipeProcessingState edge cases."""

    def test_state_with_multiple_validation_errors(self):
        """Test RecipeProcessingState with many validation errors."""
        state: RecipeProcessingState = {
            "recipe_data": {},
            "validation_errors": [
                "Name is required",
                "Description is required",
                "Instructions are invalid",
                "Prep time must be positive",
                "Cook time must be positive",
                "Servings must be positive",
            ],
            "error": "Multiple validation failures",
        }

        assert len(state["validation_errors"]) == 6

    def test_state_with_empty_embedding(self):
        """Test RecipeProcessingState with empty embedding list."""
        state: RecipeProcessingState = {
            "recipe_data": {},
            "embedding": [],
        }

        assert len(state["embedding"]) == 0

    def test_state_with_very_large_embedding(self):
        """Test RecipeProcessingState with large embedding vector."""
        embedding = [0.1] * 1536  # Larger embedding dimension

        state: RecipeProcessingState = {
            "recipe_data": {},
            "embedding": embedding,
        }

        assert len(state["embedding"]) == 1536

    def test_state_successful_processing_all_fields(self):
        """Test RecipeProcessingState with all successful fields populated."""
        from uuid import uuid4

        recipe_id = uuid4()

        state: RecipeProcessingState = {
            "recipe_data": {"name": "Test Recipe"},
            "validation_errors": [],
            "extracted_entities": {"ingredients": ["pasta"]},
            "embedding": [0.1] * 768,
            "enriched_data": {"tags": ["quick"]},
            "nutritional_info": {"calories": 500},
            "recipe_id": recipe_id,
            "error": None,
        }

        assert state["recipe_id"] == recipe_id
        assert len(state["validation_errors"]) == 0
        assert state["error"] is None


# New test case - FallbackStrategy enum edge cases
class TestFallbackStrategyEdgeCases:
    """Test suite for FallbackStrategy enum edge cases."""

    def test_fallback_strategy_equality(self):
        """Test FallbackStrategy equality comparisons."""
        assert FallbackStrategy.RELAX_THRESHOLDS == FallbackStrategy.RELAX_THRESHOLDS
        assert FallbackStrategy.EMPTY_RESULTS != FallbackStrategy.SUGGEST_ALTERNATIVES

    def test_fallback_strategy_in_collection(self):
        """Test FallbackStrategy can be used in collections."""
        strategies = [
            FallbackStrategy.RELAX_THRESHOLDS,
            FallbackStrategy.EMPTY_RESULTS,
        ]

        assert FallbackStrategy.RELAX_THRESHOLDS in strategies
        assert FallbackStrategy.SUGGEST_ALTERNATIVES not in strategies

    def test_fallback_strategy_iteration(self):
        """Test FallbackStrategy can be iterated."""
        strategies = list(FallbackStrategy)

        assert len(strategies) == 3
        assert FallbackStrategy.RELAX_THRESHOLDS in strategies
        assert FallbackStrategy.EMPTY_RESULTS in strategies
        assert FallbackStrategy.SUGGEST_ALTERNATIVES in strategies

    def test_fallback_strategy_string_conversion(self):
        """Test FallbackStrategy converts to string properly."""
        strategy = FallbackStrategy.RELAX_THRESHOLDS

        # String representation includes enum name
        assert "RELAX_THRESHOLDS" in str(strategy)
        # Value is just the string
        assert strategy.value == "RELAX_THRESHOLDS"
        # Can compare directly with string
        assert strategy == "RELAX_THRESHOLDS"
