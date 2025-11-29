"""Pydantic schemas for Category model."""

from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.base import BaseResponseSchema, BaseSchema


class CategoryBase(BaseSchema):
    """Base category schema with common fields."""

    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    slug: str = Field(..., min_length=1, max_length=100, description="URL-friendly slug")
    description: str | None = Field(None, description="Category description")
    parent_id: UUID | None = Field(None, description="Parent category ID")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and normalize category name."""
        if not v or not v.strip():
            raise ValueError("Category name cannot be empty")
        return v.strip()

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validate slug format (lowercase, hyphens, alphanumeric)."""
        if not v or not v.strip():
            raise ValueError("Slug cannot be empty")
        v = v.strip().lower()
        # Check if slug contains only alphanumeric and hyphens
        if not all(c.isalnum() or c == "-" for c in v):
            raise ValueError("Slug must contain only alphanumeric characters and hyphens")
        return v


class CategoryCreate(CategoryBase):
    """Schema for creating a new category."""

    pass


class CategoryUpdate(BaseSchema):
    """Schema for updating a category.

    All fields are optional for partial updates.
    """

    name: str | None = Field(None, min_length=1, max_length=100, description="Category name")
    slug: str | None = Field(None, min_length=1, max_length=100, description="URL-friendly slug")
    description: str | None = Field(None, description="Category description")
    parent_id: UUID | None = Field(None, description="Parent category ID")


class CategoryResponse(BaseResponseSchema, CategoryBase):
    """Schema for category response.

    Includes all fields from creation plus metadata and relationships.
    """

    # Forward reference for recursive type
    children: list["CategoryResponse"] = Field(
        default_factory=list,
        description="Child categories"
    )


# Resolve forward references for recursive types
CategoryResponse.model_rebuild()
