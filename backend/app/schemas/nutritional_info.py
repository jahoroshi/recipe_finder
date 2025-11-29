"""Pydantic schemas for NutritionalInfo model."""

from uuid import UUID

from pydantic import Field, field_validator

from app.schemas.base import BaseResponseSchema, BaseSchema


class NutritionalInfoBase(BaseSchema):
    """Base nutritional info schema with common fields."""

    calories: float | None = Field(None, ge=0, description="Calories per serving")
    protein_g: float | None = Field(None, ge=0, description="Protein in grams")
    carbohydrates_g: float | None = Field(None, ge=0, description="Carbohydrates in grams")
    fat_g: float | None = Field(None, ge=0, description="Fat in grams")
    fiber_g: float | None = Field(None, ge=0, description="Fiber in grams")
    sugar_g: float | None = Field(None, ge=0, description="Sugar in grams")
    sodium_mg: float | None = Field(None, ge=0, description="Sodium in milligrams")
    cholesterol_mg: float | None = Field(None, ge=0, description="Cholesterol in milligrams")
    additional_info: dict | None = Field(None, description="Additional nutritional data")

    @field_validator("additional_info")
    @classmethod
    def validate_additional_info(cls, v: dict | None) -> dict | None:
        """Validate additional info is a dictionary."""
        if v is not None and not isinstance(v, dict):
            raise ValueError("additional_info must be a dictionary")
        return v


class NutritionalInfoCreate(NutritionalInfoBase):
    """Schema for creating nutritional information.

    Used when creating nutritional info as part of a recipe.
    """

    pass


class NutritionalInfoUpdate(BaseSchema):
    """Schema for updating nutritional information.

    All fields are optional for partial updates.
    """

    calories: float | None = Field(None, ge=0, description="Calories per serving")
    protein_g: float | None = Field(None, ge=0, description="Protein in grams")
    carbohydrates_g: float | None = Field(None, ge=0, description="Carbohydrates in grams")
    fat_g: float | None = Field(None, ge=0, description="Fat in grams")
    fiber_g: float | None = Field(None, ge=0, description="Fiber in grams")
    sugar_g: float | None = Field(None, ge=0, description="Sugar in grams")
    sodium_mg: float | None = Field(None, ge=0, description="Sodium in milligrams")
    cholesterol_mg: float | None = Field(None, ge=0, description="Cholesterol in milligrams")
    additional_info: dict | None = Field(None, description="Additional nutritional data")


class NutritionalInfoResponse(BaseResponseSchema, NutritionalInfoBase):
    """Schema for nutritional info response.

    Includes all fields from creation plus metadata.
    """

    recipe_id: UUID = Field(..., description="Recipe ID this nutritional info belongs to")
