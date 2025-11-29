"""Pydantic schemas for Recipe model."""

from uuid import UUID

from pydantic import Field, field_validator

from app.db.models import DifficultyLevel
from app.schemas.base import BaseResponseSchema, BaseSchema, PaginatedResponse
from app.schemas.category import CategoryResponse
from app.schemas.ingredient import IngredientCreate, IngredientResponse
from app.schemas.nutritional_info import (
    NutritionalInfoCreate,
    NutritionalInfoResponse,
)


class RecipeBase(BaseSchema):
    """Base recipe schema with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Recipe name/title")
    description: str | None = Field(None, description="Brief description of the recipe")
    instructions: dict = Field(..., description="Detailed cooking instructions as JSON")
    prep_time: int | None = Field(None, ge=0, description="Preparation time in minutes")
    cook_time: int | None = Field(None, ge=0, description="Cooking time in minutes")
    servings: int | None = Field(None, gt=0, description="Number of servings")
    difficulty: DifficultyLevel = Field(
        default=DifficultyLevel.MEDIUM,
        description="Recipe difficulty level"
    )
    cuisine_type: str | None = Field(None, max_length=100, description="Type of cuisine")
    diet_types: list[str] = Field(default_factory=list, description="Array of diet types")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate and normalize recipe name."""
        if not v or not v.strip():
            raise ValueError("Recipe name cannot be empty")
        return v.strip()

    @field_validator("instructions")
    @classmethod
    def validate_instructions(cls, v: dict) -> dict:
        """Validate instructions format."""
        if not isinstance(v, dict):
            raise ValueError("Instructions must be a dictionary")
        if not v:
            raise ValueError("Instructions cannot be empty")
        return v

    @field_validator("diet_types")
    @classmethod
    def validate_diet_types(cls, v: list[str]) -> list[str]:
        """Validate and normalize diet types."""
        if not isinstance(v, list):
            raise ValueError("Diet types must be a list")
        # Remove empty strings and strip whitespace
        return [dt.strip() for dt in v if dt and dt.strip()]

    @field_validator("cuisine_type")
    @classmethod
    def validate_cuisine_type(cls, v: str | None) -> str | None:
        """Validate and normalize cuisine type."""
        if v is not None:
            v = v.strip()
            if not v:
                return None
        return v


class RecipeCreate(RecipeBase):
    """Schema for creating a new recipe.

    Includes nested creation of ingredients, categories, and nutritional info.
    """

    ingredients: list[IngredientCreate] = Field(
        default_factory=list,
        description="List of ingredients"
    )
    category_ids: list[UUID] = Field(
        default_factory=list,
        description="List of category IDs to associate with recipe"
    )
    nutritional_info: NutritionalInfoCreate | None = Field(
        None,
        description="Nutritional information"
    )

    @field_validator("ingredients")
    @classmethod
    def validate_ingredients(cls, v: list[IngredientCreate]) -> list[IngredientCreate]:
        """Validate ingredients list."""
        if not isinstance(v, list):
            raise ValueError("Ingredients must be a list")
        return v


class RecipeUpdate(BaseSchema):
    """Schema for updating a recipe.

    All fields are optional for partial updates.
    """

    name: str | None = Field(None, min_length=1, max_length=255, description="Recipe name/title")
    description: str | None = Field(None, description="Brief description of the recipe")
    instructions: dict | None = Field(None, description="Detailed cooking instructions as JSON")
    prep_time: int | None = Field(None, ge=0, description="Preparation time in minutes")
    cook_time: int | None = Field(None, ge=0, description="Cooking time in minutes")
    servings: int | None = Field(None, gt=0, description="Number of servings")
    difficulty: DifficultyLevel | None = Field(None, description="Recipe difficulty level")
    cuisine_type: str | None = Field(None, max_length=100, description="Type of cuisine")
    diet_types: list[str] | None = Field(None, description="Array of diet types")
    category_ids: list[UUID] | None = Field(None, description="List of category IDs")


class RecipeResponse(BaseResponseSchema, RecipeBase):
    """Schema for recipe response.

    Includes all fields from creation plus metadata and relationships.
    """

    embedding: list[float] | None = Field(None, description="Vector embedding (if generated)")
    ingredients: list[IngredientResponse] = Field(
        default_factory=list,
        description="List of ingredients"
    )
    categories: list[CategoryResponse] = Field(
        default_factory=list,
        description="List of categories"
    )
    nutritional_info: NutritionalInfoResponse | None = Field(
        None,
        description="Nutritional information"
    )

    @property
    def total_time(self) -> int | None:
        """Calculate total time (prep + cook)."""
        if self.prep_time is not None and self.cook_time is not None:
            return self.prep_time + self.cook_time
        return None


class RecipeListResponse(PaginatedResponse):
    """Paginated response for recipe listings."""

    items: list[RecipeResponse] = Field(..., description="List of recipes")


class RecipeFilters(BaseSchema):
    """Schema for recipe filtering parameters."""

    name: str | None = Field(None, description="Filter by name (partial match)")
    cuisine_type: str | None = Field(None, description="Filter by cuisine type")
    difficulty: DifficultyLevel | None = Field(None, description="Filter by difficulty")
    diet_types: list[str] | None = Field(None, description="Filter by diet types (any match)")
    category_ids: list[UUID] | None = Field(None, description="Filter by category IDs")
    min_prep_time: int | None = Field(None, ge=0, description="Minimum prep time in minutes")
    max_prep_time: int | None = Field(None, ge=0, description="Maximum prep time in minutes")
    min_cook_time: int | None = Field(None, ge=0, description="Minimum cook time in minutes")
    max_cook_time: int | None = Field(None, ge=0, description="Maximum cook time in minutes")
    min_servings: int | None = Field(None, gt=0, description="Minimum servings")
    max_servings: int | None = Field(None, gt=0, description="Maximum servings")

    @field_validator("max_prep_time")
    @classmethod
    def validate_prep_time_range(cls, v: int | None, info) -> int | None:
        """Validate prep time range."""
        if v is not None and "min_prep_time" in info.data:
            min_val = info.data["min_prep_time"]
            if min_val is not None and v < min_val:
                raise ValueError("max_prep_time must be greater than or equal to min_prep_time")
        return v

    @field_validator("max_cook_time")
    @classmethod
    def validate_cook_time_range(cls, v: int | None, info) -> int | None:
        """Validate cook time range."""
        if v is not None and "min_cook_time" in info.data:
            min_val = info.data["min_cook_time"]
            if min_val is not None and v < min_val:
                raise ValueError("max_cook_time must be greater than or equal to min_cook_time")
        return v

    @field_validator("max_servings")
    @classmethod
    def validate_servings_range(cls, v: int | None, info) -> int | None:
        """Validate servings range."""
        if v is not None and "min_servings" in info.data:
            min_val = info.data["min_servings"]
            if min_val is not None and v < min_val:
                raise ValueError("max_servings must be greater than or equal to min_servings")
        return v
