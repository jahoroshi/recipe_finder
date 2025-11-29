"""Pydantic schemas for Ingredient model."""

from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.base import BaseResponseSchema, BaseSchema


class IngredientBase(BaseSchema):
    """Base ingredient schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Ingredient name")
    quantity: float | None = Field(None, ge=0, description="Quantity amount")
    unit: str | None = Field(None, max_length=50, description="Unit of measurement")
    notes: str | None = Field(None, description="Additional notes")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and normalize ingredient name."""
        if not v or not v.strip():
            raise ValueError("Ingredient name cannot be empty")
        return v.strip()

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, v: str | None) -> str | None:
        """Validate and normalize unit."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class IngredientCreate(IngredientBase):
    """Schema for creating a new ingredient.

    Used when creating ingredients as part of a recipe.
    """

    pass


class IngredientUpdate(BaseSchema):
    """Schema for updating an ingredient.

    All fields are optional for partial updates.
    """

    name: str | None = Field(None, min_length=1, max_length=255, description="Ingredient name")
    quantity: float | None = Field(None, ge=0, description="Quantity amount")
    unit: str | None = Field(None, max_length=50, description="Unit of measurement")
    notes: str | None = Field(None, description="Additional notes")


class IngredientResponse(BaseResponseSchema, IngredientBase):
    """Schema for ingredient response.

    Includes all fields from creation plus metadata.
    """

    recipe_id: UUID = Field(..., description="Recipe ID this ingredient belongs to")
