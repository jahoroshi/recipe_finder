"""Pydantic schemas for search functionality."""

from typing import Optional

from pydantic import Field, field_validator

from app.schemas.base import BaseSchema
from app.schemas.recipe import RecipeResponse


class ParsedQuery(BaseSchema):
    """Schema for parsed query from Gemini."""

    original_query: str = Field(..., description="Original search query")
    ingredients: list[str] = Field(
        default_factory=list, description="Extracted ingredient names"
    )
    cuisine_type: Optional[str] = Field(None, description="Detected cuisine type")
    diet_types: list[str] = Field(
        default_factory=list, description="Detected diet types"
    )
    max_total_time: Optional[int] = Field(
        None, description="Maximum total time (prep + cook) in minutes"
    )
    max_prep_time: Optional[int] = Field(
        None, description="Maximum preparation time in minutes"
    )
    max_cook_time: Optional[int] = Field(
        None, description="Maximum cooking time in minutes"
    )
    difficulty: Optional[str] = Field(None, description="Desired difficulty level")
    semantic_query: str = Field(..., description="Cleaned query for semantic search")


class SearchRequest(BaseSchema):
    """Schema for search request."""

    query: str = Field(..., min_length=1, description="Search query text")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of results")
    use_semantic: bool = Field(True, description="Use semantic vector search")
    use_filters: bool = Field(True, description="Use filter-based search")
    use_reranking: bool = Field(False, description="Apply reranking to results")
    filters: Optional[dict] = Field(None, description="Additional filter criteria")

    @field_validator("query")
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Validate and normalize search query."""
        if not v or not v.strip():
            raise ValueError("Query cannot be empty")
        return v.strip()


class SearchResult(BaseSchema):
    """Schema for individual search result."""

    recipe: RecipeResponse = Field(..., description="Recipe data")
    score: float = Field(..., description="Relevance score (0-1, higher is better)")
    distance: Optional[float] = Field(None, description="Vector distance (if applicable)")
    match_type: str = Field(
        ..., description="Match type (semantic, filter, hybrid)"
    )


class SearchResponse(BaseSchema):
    """Schema for search response."""

    query: str = Field(..., description="Original search query")
    parsed_query: Optional[ParsedQuery] = Field(
        None, description="Parsed query components"
    )
    results: list[SearchResult] = Field(..., description="Search results")
    total: int = Field(..., description="Total number of results")
    search_type: str = Field(..., description="Type of search performed")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    @property
    def has_results(self) -> bool:
        """Check if search returned any results."""
        return self.total > 0
