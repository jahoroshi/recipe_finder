"""Database models for the Recipe Management API."""

import enum
import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY,
    CheckConstraint,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

if TYPE_CHECKING:
    pass


class DifficultyLevel(str, enum.Enum):
    """Enumeration for recipe difficulty levels."""

    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class Recipe(BaseModel):
    """Recipe model representing a cooking recipe.

    Attributes:
        name: Recipe name/title
        description: Brief description of the recipe
        instructions: Detailed cooking instructions stored as JSONB
        prep_time: Preparation time in minutes
        cook_time: Cooking time in minutes
        servings: Number of servings
        difficulty: Recipe difficulty level
        cuisine_type: Type of cuisine (e.g., Italian, Chinese)
        diet_types: Array of diet types (vegetarian, vegan, gluten-free, etc.)
        embedding: Vector embedding for semantic search (768 dimensions)
        ingredients: Related ingredients
        categories: Related categories
        nutritional_info: Nutritional information
    """

    __tablename__ = "recipes"

    # Basic Information
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Recipe name/title"
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Brief description of the recipe"
    )

    instructions: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
        comment="Detailed cooking instructions as JSON"
    )

    # Time and Serving Information
    prep_time: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Preparation time in minutes"
    )

    cook_time: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Cooking time in minutes"
    )

    servings: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        comment="Number of servings"
    )

    # Classification
    difficulty: Mapped[DifficultyLevel] = mapped_column(
        Enum(DifficultyLevel, name="difficulty_level", values_callable=lambda x: [e.value for e in x]),
        nullable=False,
        default=DifficultyLevel.MEDIUM,
        index=True,
        comment="Recipe difficulty level"
    )

    cuisine_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
        comment="Type of cuisine"
    )

    diet_types: Mapped[list[str]] = mapped_column(
        ARRAY(String),
        nullable=False,
        default=list,
        comment="Array of diet types (vegetarian, vegan, etc.)"
    )

    # Vector Embedding for Semantic Search
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(768),
        nullable=True,
        comment="Vector embedding for semantic search (768 dimensions)"
    )

    # Relationships
    ingredients: Mapped[list["Ingredient"]] = relationship(
        "Ingredient",
        back_populates="recipe",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    recipe_categories: Mapped[list["RecipeCategory"]] = relationship(
        "RecipeCategory",
        back_populates="recipe",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    nutritional_info: Mapped["NutritionalInfo | None"] = relationship(
        "NutritionalInfo",
        back_populates="recipe",
        cascade="all, delete-orphan",
        uselist=False,
        lazy="selectin"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("prep_time >= 0", name="check_prep_time_positive"),
        CheckConstraint("cook_time >= 0", name="check_cook_time_positive"),
        CheckConstraint("servings > 0", name="check_servings_positive"),
        Index("ix_recipes_name_trgm", "name", postgresql_using="gin", postgresql_ops={"name": "gin_trgm_ops"}),
        Index("ix_recipes_cuisine_difficulty", "cuisine_type", "difficulty"),
        Index("ix_recipes_created_at_desc", "created_at", postgresql_using="btree", postgresql_ops={"created_at": "DESC"}),
    )

    def __repr__(self) -> str:
        """String representation of the recipe."""
        return f"<Recipe(id={self.id}, name='{self.name}', difficulty={self.difficulty.value})>"


class Ingredient(BaseModel):
    """Ingredient model for recipe ingredients.

    Attributes:
        recipe_id: Foreign key to the recipe
        name: Ingredient name
        quantity: Quantity amount
        unit: Unit of measurement
        notes: Additional notes about the ingredient
        recipe: Related recipe
    """

    __tablename__ = "ingredients"

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to recipe"
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="Ingredient name"
    )

    quantity: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Quantity amount"
    )

    unit: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Unit of measurement"
    )

    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Additional notes about the ingredient"
    )

    # Relationships
    recipe: Mapped["Recipe"] = relationship(
        "Recipe",
        back_populates="ingredients"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("quantity >= 0", name="check_quantity_positive"),
        Index("ix_ingredients_recipe_name", "recipe_id", "name"),
    )

    def __repr__(self) -> str:
        """String representation of the ingredient."""
        return f"<Ingredient(id={self.id}, name='{self.name}', quantity={self.quantity} {self.unit})>"


class Category(BaseModel):
    """Category model for recipe categorization with hierarchical support.

    Supports hierarchical categories with parent-child relationships.

    Attributes:
        name: Category name
        slug: URL-friendly slug
        description: Category description
        parent_id: Parent category ID for hierarchical structure
        parent: Parent category
        children: Child categories
        recipe_categories: Related recipe categories
    """

    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="Category name"
    )

    slug: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True,
        comment="URL-friendly slug"
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="Category description"
    )

    # Hierarchical structure
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="Parent category ID for hierarchical structure"
    )

    # Relationships
    parent: Mapped["Category | None"] = relationship(
        "Category",
        remote_side="Category.id",
        back_populates="children",
        lazy="selectin"
    )

    children: Mapped[list["Category"]] = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    recipe_categories: Mapped[list["RecipeCategory"]] = relationship(
        "RecipeCategory",
        back_populates="category",
        cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        """String representation of the category."""
        return f"<Category(id={self.id}, name='{self.name}', slug='{self.slug}')>"


class RecipeCategory(BaseModel):
    """Junction table for many-to-many relationship between recipes and categories.

    Attributes:
        recipe_id: Foreign key to recipe
        category_id: Foreign key to category
        recipe: Related recipe
        category: Related category
    """

    __tablename__ = "recipe_categories"

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to recipe"
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Foreign key to category"
    )

    # Relationships
    recipe: Mapped["Recipe"] = relationship(
        "Recipe",
        back_populates="recipe_categories"
    )

    category: Mapped["Category"] = relationship(
        "Category",
        back_populates="recipe_categories"
    )

    # Constraints
    __table_args__ = (
        UniqueConstraint("recipe_id", "category_id", name="uq_recipe_category"),
        Index("ix_recipe_categories_recipe_category", "recipe_id", "category_id"),
    )

    def __repr__(self) -> str:
        """String representation of the recipe-category relationship."""
        return f"<RecipeCategory(recipe_id={self.recipe_id}, category_id={self.category_id})>"


class NutritionalInfo(BaseModel):
    """Nutritional information for recipes.

    One-to-one relationship with Recipe.

    Attributes:
        recipe_id: Foreign key to recipe (unique)
        calories: Calories per serving
        protein_g: Protein in grams
        carbohydrates_g: Carbohydrates in grams
        fat_g: Fat in grams
        fiber_g: Fiber in grams
        sugar_g: Sugar in grams
        sodium_mg: Sodium in milligrams
        cholesterol_mg: Cholesterol in milligrams
        additional_info: Additional nutritional data as JSONB
        recipe: Related recipe
    """

    __tablename__ = "nutritional_info"

    recipe_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
        comment="Foreign key to recipe (one-to-one)"
    )

    calories: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Calories per serving"
    )

    protein_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Protein in grams"
    )

    carbohydrates_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Carbohydrates in grams"
    )

    fat_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Fat in grams"
    )

    fiber_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Fiber in grams"
    )

    sugar_g: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Sugar in grams"
    )

    sodium_mg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Sodium in milligrams"
    )

    cholesterol_mg: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
        comment="Cholesterol in milligrams"
    )

    additional_info: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default=dict,
        comment="Additional nutritional data as JSON"
    )

    # Relationships
    recipe: Mapped["Recipe"] = relationship(
        "Recipe",
        back_populates="nutritional_info"
    )

    # Constraints
    __table_args__ = (
        CheckConstraint("calories >= 0", name="check_calories_positive"),
        CheckConstraint("protein_g >= 0", name="check_protein_positive"),
        CheckConstraint("carbohydrates_g >= 0", name="check_carbohydrates_positive"),
        CheckConstraint("fat_g >= 0", name="check_fat_positive"),
        CheckConstraint("fiber_g >= 0", name="check_fiber_positive"),
        CheckConstraint("sugar_g >= 0", name="check_sugar_positive"),
        CheckConstraint("sodium_mg >= 0", name="check_sodium_positive"),
        CheckConstraint("cholesterol_mg >= 0", name="check_cholesterol_positive"),
    )

    def __repr__(self) -> str:
        """String representation of nutritional info."""
        return f"<NutritionalInfo(recipe_id={self.recipe_id}, calories={self.calories})>"
