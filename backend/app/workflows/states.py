"""State schemas for LangGraph workflows."""

from enum import Enum
from typing import Any, TypedDict

from pydantic import BaseModel, Field

from app.db.models import Recipe


class FallbackStrategy(str, Enum):
    """Strategy to use when judge filters too many results."""

    RELAX_THRESHOLDS = "RELAX_THRESHOLDS"
    EMPTY_RESULTS = "EMPTY_RESULTS"
    SUGGEST_ALTERNATIVES = "SUGGEST_ALTERNATIVES"


class JudgeConfig(BaseModel):
    """Configuration for the judge relevance node.

    Defines thresholds and behavior for filtering search results.

    Attributes:
        semantic_threshold: Minimum cosine similarity score (0.0-1.0)
        filter_compliance_min: Minimum filter match ratio (0.0-1.0)
        ingredient_match_min: Minimum ingredient match ratio (0.0-1.0)
        dietary_strict_mode: Strict validation for dietary requirements
        confidence_threshold: Minimum confidence score (0.0-1.0)
        min_results: Minimum number of results to return
        max_results: Maximum number of results to return
        fallback_strategy: Strategy when filtering removes too many results
    """

    semantic_threshold: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum cosine similarity score for semantic search"
    )
    filter_compliance_min: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum percentage of matched filters"
    )
    ingredient_match_min: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum ingredient match ratio for ingredient queries"
    )
    dietary_strict_mode: bool = Field(
        default=True,
        description="Strictly enforce dietary restrictions"
    )
    confidence_threshold: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Minimum overall confidence score"
    )
    min_results: int = Field(
        default=0,
        ge=0,
        description="Minimum number of results to keep"
    )
    max_results: int = Field(
        default=100,
        ge=1,
        description="Maximum number of results to return"
    )
    fallback_strategy: FallbackStrategy = Field(
        default=FallbackStrategy.RELAX_THRESHOLDS,
        description="Strategy when too many results are filtered"
    )


class SearchPipelineState(TypedDict, total=False):
    """State schema for search pipeline workflow.

    Tracks the state through all nodes in the search pipeline.

    Attributes:
        query: Original search query from user
        parsed_query: Structured query parsed by Gemini
        filters: Extracted filter criteria
        embedding: Query embedding vector
        vector_results: Results from semantic vector search
        filter_results: Results from filter-based search
        merged_results: Combined results using RRF
        judge_metrics: Relevance metrics from judge node
        filtered_results: Results after judge filtering
        judge_report: Detailed report from judge evaluation
        final_results: Final ranked results
        metadata: Additional workflow metadata
        judge_config: Configuration for judge node
        error: Error message if workflow fails
    """

    query: str
    parsed_query: dict[str, Any]
    filters: dict[str, Any]
    embedding: list[float] | None
    vector_results: list[Recipe]
    filter_results: list[Recipe]
    merged_results: list[Recipe]
    judge_metrics: dict[str, float]
    filtered_results: list[Recipe]
    judge_report: dict[str, Any]
    final_results: list[Recipe]
    metadata: dict[str, Any]
    judge_config: JudgeConfig
    error: str | None


class RecipeProcessingState(TypedDict, total=False):
    """State schema for recipe processing workflow.

    Tracks the state through recipe creation and enrichment pipeline.

    Attributes:
        recipe_data: Input recipe data
        validation_errors: List of validation errors
        extracted_entities: Entities extracted from recipe
        embedding: Generated recipe embedding
        enriched_data: Enriched recipe metadata
        nutritional_info: Calculated nutritional information
        recipe_id: ID of created/updated recipe
        error: Error message if workflow fails
    """

    recipe_data: dict[str, Any]
    validation_errors: list[str]
    extracted_entities: dict[str, Any]
    embedding: list[float]
    enriched_data: dict[str, Any]
    nutritional_info: dict[str, Any]
    recipe_id: str | None
    error: str | None
