"""Pagination utilities for repository queries."""

from typing import Any

from pydantic import BaseModel, Field, field_validator


class Pagination(BaseModel):
    """Pagination parameters for list queries.

    Attributes:
        offset: Number of records to skip (default: 0, min: 0)
        limit: Maximum number of records to return (default: 50, max: 100)

    Example:
        ```python
        pagination = Pagination(offset=0, limit=20)
        results = await repository.list({}, pagination)
        ```
    """

    offset: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(
        default=50, ge=1, le=100, description="Maximum records to return"
    )

    @field_validator("offset")
    @classmethod
    def validate_offset(cls, v: int) -> int:
        """Validate offset is non-negative."""
        if v < 0:
            raise ValueError("Offset must be non-negative")
        return v

    @field_validator("limit")
    @classmethod
    def validate_limit(cls, v: int) -> int:
        """Validate limit is within allowed range."""
        if v < 1:
            raise ValueError("Limit must be at least 1")
        if v > 100:
            raise ValueError("Limit cannot exceed 100")
        return v

    def apply(self, query: Any) -> Any:
        """Apply pagination to a SQLAlchemy query.

        Args:
            query: SQLAlchemy query to paginate

        Returns:
            Paginated query with offset and limit applied
        """
        return query.offset(self.offset).limit(self.limit)

    @property
    def page_number(self) -> int:
        """Calculate current page number (1-indexed)."""
        return (self.offset // self.limit) + 1

    def next_offset(self) -> int:
        """Calculate offset for next page."""
        return self.offset + self.limit

    def previous_offset(self) -> int:
        """Calculate offset for previous page."""
        return max(0, self.offset - self.limit)

    class Config:
        """Pydantic configuration."""

        frozen = True
