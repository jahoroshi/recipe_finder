"""Tests for SQLAlchemy models."""

import uuid
from datetime import datetime

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Category,
    DifficultyLevel,
    Ingredient,
    NutritionalInfo,
    Recipe,
    RecipeCategory,
)


class TestRecipeModel:
    """Tests for Recipe model."""

    @pytest.mark.asyncio
    async def test_create_recipe(self, db_session: AsyncSession):
        """Test creating a recipe with all required fields."""
        recipe = Recipe(
            name="Test Recipe",
            description="A test recipe",
            instructions={"steps": ["Step 1", "Step 2"]},
            prep_time=10,
            cook_time=20,
            servings=4,
            difficulty=DifficultyLevel.EASY,
            cuisine_type="Italian",
            diet_types=["vegetarian"],
        )

        db_session.add(recipe)
        await db_session.commit()
        await db_session.refresh(recipe)

        assert recipe.id is not None
        assert isinstance(recipe.id, uuid.UUID)
        assert recipe.name == "Test Recipe"
        assert recipe.difficulty == DifficultyLevel.EASY
        assert recipe.diet_types == ["vegetarian"]
        assert isinstance(recipe.created_at, datetime)
        assert isinstance(recipe.updated_at, datetime)

    @pytest.mark.asyncio
    async def test_recipe_with_embedding(self, db_session: AsyncSession):
        """Test creating a recipe with vector embedding."""
        # Create a 768-dimensional embedding
        embedding = [0.1] * 768

        recipe = Recipe(
            name="Recipe with Embedding",
            instructions={"steps": ["Mix", "Bake"]},
            difficulty=DifficultyLevel.MEDIUM,
            embedding=embedding,
        )

        db_session.add(recipe)
        await db_session.commit()
        await db_session.refresh(recipe)

        assert recipe.embedding is not None
        assert len(recipe.embedding) == 768
        assert recipe.embedding[0] == pytest.approx(0.1)

    @pytest.mark.asyncio
    async def test_recipe_soft_delete(self, db_session: AsyncSession):
        """Test soft delete functionality."""
        recipe = Recipe(
            name="To Delete",
            instructions={"steps": ["Test"]},
            difficulty=DifficultyLevel.EASY,
        )

        db_session.add(recipe)
        await db_session.commit()
        await db_session.refresh(recipe)

        assert recipe.deleted_at is None
        assert not recipe.is_deleted

        # Soft delete
        recipe.deleted_at = datetime.now()
        await db_session.commit()
        await db_session.refresh(recipe)

        assert recipe.deleted_at is not None
        assert recipe.is_deleted

    @pytest.mark.asyncio
    async def test_recipe_with_ingredients(self, db_session: AsyncSession):
        """Test recipe with related ingredients."""
        recipe = Recipe(
            name="Recipe with Ingredients",
            instructions={"steps": ["Test"]},
            difficulty=DifficultyLevel.EASY,
        )

        # Add ingredients
        ingredient1 = Ingredient(
            recipe=recipe,
            name="Flour",
            quantity=2.0,
            unit="cups",
        )
        ingredient2 = Ingredient(
            recipe=recipe,
            name="Sugar",
            quantity=1.0,
            unit="cup",
        )

        db_session.add(recipe)
        await db_session.commit()
        await db_session.refresh(recipe)

        assert len(recipe.ingredients) == 2
        assert recipe.ingredients[0].name in ["Flour", "Sugar"]
        assert recipe.ingredients[0].recipe_id == recipe.id


class TestIngredientModel:
    """Tests for Ingredient model."""

    @pytest.mark.asyncio
    async def test_create_ingredient(self, db_session: AsyncSession):
        """Test creating an ingredient."""
        recipe = Recipe(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            difficulty=DifficultyLevel.EASY,
        )
        db_session.add(recipe)
        await db_session.commit()

        ingredient = Ingredient(
            recipe_id=recipe.id,
            name="Tomato",
            quantity=3.0,
            unit="pieces",
            notes="Fresh tomatoes",
        )

        db_session.add(ingredient)
        await db_session.commit()
        await db_session.refresh(ingredient)

        assert ingredient.id is not None
        assert ingredient.name == "Tomato"
        assert ingredient.quantity == 3.0
        assert ingredient.unit == "pieces"
        assert ingredient.recipe_id == recipe.id

    @pytest.mark.asyncio
    async def test_ingredient_cascade_delete(self, db_session: AsyncSession):
        """Test that ingredients are deleted when recipe is deleted."""
        recipe = Recipe(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            difficulty=DifficultyLevel.EASY,
        )
        ingredient = Ingredient(
            recipe=recipe,
            name="Test Ingredient",
            quantity=1.0,
        )

        db_session.add(recipe)
        await db_session.commit()

        recipe_id = recipe.id
        ingredient_id = ingredient.id

        # Delete recipe
        await db_session.delete(recipe)
        await db_session.commit()

        # Check ingredient is also deleted
        result = await db_session.execute(
            select(Ingredient).where(Ingredient.id == ingredient_id)
        )
        deleted_ingredient = result.scalar_one_or_none()
        assert deleted_ingredient is None


class TestCategoryModel:
    """Tests for Category model."""

    @pytest.mark.asyncio
    async def test_create_category(self, db_session: AsyncSession):
        """Test creating a category."""
        category = Category(
            name="Desserts",
            slug="desserts",
            description="Sweet treats",
        )

        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

        assert category.id is not None
        assert category.name == "Desserts"
        assert category.slug == "desserts"

    @pytest.mark.asyncio
    async def test_category_hierarchy(self, db_session: AsyncSession):
        """Test hierarchical category structure."""
        parent = Category(
            name="Desserts",
            slug="desserts",
            description="Sweet treats",
        )

        child1 = Category(
            name="Cakes",
            slug="cakes",
            description="Baked cakes",
            parent=parent,
        )

        child2 = Category(
            name="Cookies",
            slug="cookies",
            description="Baked cookies",
            parent=parent,
        )

        db_session.add(parent)
        await db_session.commit()
        await db_session.refresh(parent)

        assert len(parent.children) == 2
        assert parent.parent is None
        assert child1.parent_id == parent.id
        assert child2.parent_id == parent.id

    @pytest.mark.asyncio
    async def test_category_unique_constraints(self, db_session: AsyncSession):
        """Test unique constraints on name and slug."""
        category1 = Category(
            name="Test Category",
            slug="test-category",
        )

        db_session.add(category1)
        await db_session.commit()

        # Try to create duplicate
        category2 = Category(
            name="Test Category",
            slug="test-category-2",
        )

        db_session.add(category2)

        with pytest.raises(Exception):  # Will raise IntegrityError
            await db_session.commit()


class TestNutritionalInfoModel:
    """Tests for NutritionalInfo model."""

    @pytest.mark.asyncio
    async def test_create_nutritional_info(self, db_session: AsyncSession):
        """Test creating nutritional information."""
        recipe = Recipe(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            difficulty=DifficultyLevel.EASY,
        )
        db_session.add(recipe)
        await db_session.commit()

        nutrition = NutritionalInfo(
            recipe_id=recipe.id,
            calories=250.0,
            protein_g=10.0,
            carbohydrates_g=30.0,
            fat_g=8.0,
            fiber_g=5.0,
            sugar_g=10.0,
            sodium_mg=200.0,
            cholesterol_mg=15.0,
            additional_info={"vitamins": {"A": "10%", "C": "20%"}},
        )

        db_session.add(nutrition)
        await db_session.commit()
        await db_session.refresh(nutrition)

        assert nutrition.id is not None
        assert nutrition.calories == 250.0
        assert nutrition.protein_g == 10.0
        assert nutrition.additional_info == {"vitamins": {"A": "10%", "C": "20%"}}

    @pytest.mark.asyncio
    async def test_nutritional_info_one_to_one(self, db_session: AsyncSession):
        """Test one-to-one relationship with recipe."""
        recipe = Recipe(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            difficulty=DifficultyLevel.EASY,
        )

        nutrition = NutritionalInfo(
            recipe=recipe,
            calories=200.0,
            protein_g=5.0,
        )

        db_session.add(recipe)
        await db_session.commit()
        await db_session.refresh(recipe)

        assert recipe.nutritional_info is not None
        assert recipe.nutritional_info.calories == 200.0
        assert recipe.nutritional_info.recipe_id == recipe.id


class TestRecipeCategoryModel:
    """Tests for RecipeCategory junction table."""

    @pytest.mark.asyncio
    async def test_recipe_category_relationship(self, db_session: AsyncSession):
        """Test many-to-many relationship between recipes and categories."""
        recipe = Recipe(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            difficulty=DifficultyLevel.EASY,
        )

        category1 = Category(name="Category 1", slug="category-1")
        category2 = Category(name="Category 2", slug="category-2")

        db_session.add_all([recipe, category1, category2])
        await db_session.commit()

        # Create relationships
        rc1 = RecipeCategory(recipe_id=recipe.id, category_id=category1.id)
        rc2 = RecipeCategory(recipe_id=recipe.id, category_id=category2.id)

        db_session.add_all([rc1, rc2])
        await db_session.commit()
        await db_session.refresh(recipe)

        assert len(recipe.recipe_categories) == 2

    @pytest.mark.asyncio
    async def test_recipe_category_unique_constraint(self, db_session: AsyncSession):
        """Test unique constraint on recipe-category pair."""
        recipe = Recipe(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            difficulty=DifficultyLevel.EASY,
        )
        category = Category(name="Test Category", slug="test-category")

        db_session.add_all([recipe, category])
        await db_session.commit()

        rc1 = RecipeCategory(recipe_id=recipe.id, category_id=category.id)
        db_session.add(rc1)
        await db_session.commit()

        # Try to create duplicate
        rc2 = RecipeCategory(recipe_id=recipe.id, category_id=category.id)
        db_session.add(rc2)

        with pytest.raises(Exception):  # Will raise IntegrityError
            await db_session.commit()


class TestBaseModel:
    """Tests for BaseModel functionality."""

    @pytest.mark.asyncio
    async def test_to_dict(self, db_session: AsyncSession):
        """Test to_dict method."""
        recipe = Recipe(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            difficulty=DifficultyLevel.EASY,
        )

        db_session.add(recipe)
        await db_session.commit()
        await db_session.refresh(recipe)

        recipe_dict = recipe.to_dict()

        assert isinstance(recipe_dict, dict)
        assert recipe_dict["name"] == "Test Recipe"
        assert "id" in recipe_dict
        assert "created_at" in recipe_dict

    @pytest.mark.asyncio
    async def test_repr(self, db_session: AsyncSession):
        """Test __repr__ method."""
        recipe = Recipe(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            difficulty=DifficultyLevel.EASY,
        )

        db_session.add(recipe)
        await db_session.commit()
        await db_session.refresh(recipe)

        repr_str = repr(recipe)
        assert "Recipe" in repr_str
        assert str(recipe.id) in repr_str
