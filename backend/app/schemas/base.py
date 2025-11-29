"""Base Pydantic schemas with common fields."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        use_enum_values=True,
        str_strip_whitespace=True,
    )


class TimestampSchema(BaseSchema):
    """Schema with timestamp fields."""

    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class BaseResponseSchema(TimestampSchema):
    """Base response schema with common fields for all responses."""

    id: UUID = Field(..., description="Unique identifier")
    deleted_at: datetime | None = Field(None, description="Soft delete timestamp")


class PaginationParams(BaseSchema):
    """Common pagination parameters."""

    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(10, ge=1, le=100, description="Maximum number of records to return")


class PaginatedResponse(BaseSchema):
    """Generic paginated response wrapper."""

    total: int = Field(..., ge=0, description="Total number of records")
    skip: int = Field(..., ge=0, description="Number of records skipped")
    limit: int = Field(..., ge=1, description="Maximum number of records returned")
    has_more: bool = Field(..., description="Whether there are more records")
