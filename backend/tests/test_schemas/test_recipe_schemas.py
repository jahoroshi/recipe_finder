"""Tests for Recipe Pydantic schemas."""

import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.db.models import DifficultyLevel
from app.schemas.recipe import (
    RecipeCreate,
    RecipeFilters,
    RecipeResponse,
    RecipeUpdate,
)
from app.schemas.ingredient import IngredientCreate
from app.schemas.nutritional_info import NutritionalInfoCreate


class TestRecipeCreateSchema:
    """Tests for RecipeCreate schema."""

    def test_valid_recipe_create(self):
        """Test creating a valid recipe."""
        recipe = RecipeCreate(
            name="Pasta Carbonara",
            description="Classic Italian pasta dish",
            instructions={"steps": ["Boil pasta", "Mix eggs", "Combine"]},
            prep_time=10,
            cook_time=20,
            servings=4,
            difficulty=DifficultyLevel.MEDIUM,
            cuisine_type="Italian",
            diet_types=[""],
            ingredients=[
                IngredientCreate(name="Pasta", quantity=500, unit="g"),
                IngredientCreate(name="Eggs", quantity=4, unit="pieces"),
            ],
            category_ids=[],
        )

        assert recipe.name == "Pasta Carbonara"
        assert recipe.prep_time == 10
        assert len(recipe.ingredients) == 2
        assert recipe.difficulty == DifficultyLevel.MEDIUM

    def test_recipe_name_required(self):
        """Test that recipe name is required."""
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(
                name="",
                instructions={"steps": ["Test"]},
            )

        errors = exc_info.value.errors()
        assert any("name" in str(error) for error in errors)

    def test_recipe_instructions_required(self):
        """Test that instructions are required."""
        with pytest.raises(ValidationError) as exc_info:
            RecipeCreate(
                name="Test Recipe",
                instructions={},
            )

        errors = exc_info.value.errors()
        assert any("instructions" in str(error) for error in errors)

    def test_recipe_instructions_must_be_dict(self):
        """Test that instructions must be a dictionary."""
        with pytest.raises(ValidationError):
            RecipeCreate(
                name="Test Recipe",
                instructions="Not a dict",  # type: ignore
            )

    def test_negative_prep_time(self):
        """Test that negative prep time is not allowed."""
        with pytest.raises(ValidationError):
            RecipeCreate(
                name="Test Recipe",
                instructions={"steps": ["Test"]},
                prep_time=-10,
            )

    def test_zero_servings(self):
        """Test that zero servings is not allowed."""
        with pytest.raises(ValidationError):
            RecipeCreate(
                name="Test Recipe",
                instructions={"steps": ["Test"]},
                servings=0,
            )

    def test_diet_types_cleanup(self):
        """Test that empty diet types are removed."""
        recipe = RecipeCreate(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            diet_types=["vegetarian", "", "  ", "vegan"],
        )

        assert "vegetarian" in recipe.diet_types
        assert "vegan" in recipe.diet_types
        assert "" not in recipe.diet_types

    def test_name_whitespace_trimming(self):
        """Test that name whitespace is trimmed."""
        recipe = RecipeCreate(
            name="  Test Recipe  ",
            instructions={"steps": ["Test"]},
        )

        assert recipe.name == "Test Recipe"

    def test_recipe_with_nutritional_info(self):
        """Test recipe with nutritional information."""
        recipe = RecipeCreate(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            nutritional_info=NutritionalInfoCreate(
                calories=250.0,
                protein_g=10.0,
                carbohydrates_g=30.0,
            ),
        )

        assert recipe.nutritional_info is not None
        assert recipe.nutritional_info.calories == 250.0


class TestRecipeUpdateSchema:
    """Tests for RecipeUpdate schema."""

    def test_partial_update(self):
        """Test partial update with only some fields."""
        update = RecipeUpdate(
            name="Updated Name",
        )

        assert update.name == "Updated Name"
        assert update.prep_time is None
        assert update.difficulty is None

    def test_update_all_fields(self):
        """Test updating all fields."""
        update = RecipeUpdate(
            name="Updated Recipe",
            description="New description",
            instructions={"steps": ["New step"]},
            prep_time=15,
            cook_time=25,
            servings=6,
            difficulty=DifficultyLevel.HARD,
            cuisine_type="French",
            diet_types=["gluten-free"],
        )

        assert update.name == "Updated Recipe"
        assert update.difficulty == DifficultyLevel.HARD
        assert update.diet_types == ["gluten-free"]

    def test_empty_update(self):
        """Test creating an empty update object."""
        update = RecipeUpdate()

        assert update.name is None
        assert update.prep_time is None


class TestRecipeResponseSchema:
    """Tests for RecipeResponse schema."""

    def test_recipe_response_from_dict(self):
        """Test creating response from dictionary."""
        now = datetime.now(timezone.utc)
        recipe_id = uuid.uuid4()

        data = {
            "id": recipe_id,
            "name": "Test Recipe",
            "description": "A test recipe",
            "instructions": {"steps": ["Test"]},
            "prep_time": 10,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "medium",
            "cuisine_type": "Italian",
            "diet_types": ["vegetarian"],
            "embedding": None,
            "ingredients": [],
            "categories": [],
            "nutritional_info": None,
            "created_at": now,
            "updated_at": now,
            "deleted_at": None,
        }

        response = RecipeResponse(**data)

        assert response.id == recipe_id
        assert response.name == "Test Recipe"
        assert response.difficulty == "medium"

    def test_total_time_property(self):
        """Test total_time calculated property."""
        now = datetime.now(timezone.utc)

        recipe = RecipeResponse(
            id=uuid.uuid4(),
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            prep_time=10,
            cook_time=20,
            difficulty=DifficultyLevel.EASY,
            diet_types=[],
            created_at=now,
            updated_at=now,
        )

        assert recipe.total_time == 30

    def test_total_time_with_missing_times(self):
        """Test total_time when times are missing."""
        now = datetime.now(timezone.utc)

        recipe = RecipeResponse(
            id=uuid.uuid4(),
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            prep_time=None,
            cook_time=20,
            difficulty=DifficultyLevel.EASY,
            diet_types=[],
            created_at=now,
            updated_at=now,
        )

        assert recipe.total_time is None


class TestRecipeFiltersSchema:
    """Tests for RecipeFilters schema."""

    def test_valid_filters(self):
        """Test creating valid filters."""
        filters = RecipeFilters(
            name="pasta",
            cuisine_type="Italian",
            difficulty=DifficultyLevel.EASY,
            min_prep_time=10,
            max_prep_time=30,
        )

        assert filters.name == "pasta"
        assert filters.cuisine_type == "Italian"
        assert filters.min_prep_time == 10
        assert filters.max_prep_time == 30

    def test_prep_time_range_validation(self):
        """Test that max_prep_time must be >= min_prep_time."""
        with pytest.raises(ValidationError) as exc_info:
            RecipeFilters(
                min_prep_time=30,
                max_prep_time=10,
            )

        errors = exc_info.value.errors()
        assert any("max_prep_time" in str(error) for error in errors)

    def test_cook_time_range_validation(self):
        """Test that max_cook_time must be >= min_cook_time."""
        with pytest.raises(ValidationError):
            RecipeFilters(
                min_cook_time=60,
                max_cook_time=30,
            )

    def test_servings_range_validation(self):
        """Test that max_servings must be >= min_servings."""
        with pytest.raises(ValidationError):
            RecipeFilters(
                min_servings=10,
                max_servings=5,
            )

    def test_empty_filters(self):
        """Test creating filters with no values."""
        filters = RecipeFilters()

        assert filters.name is None
        assert filters.cuisine_type is None
        assert filters.difficulty is None

    def test_diet_types_filter(self):
        """Test filtering by diet types."""
        filters = RecipeFilters(
            diet_types=["vegetarian", "vegan"],
        )

        assert len(filters.diet_types) == 2
        assert "vegetarian" in filters.diet_types

    def test_category_ids_filter(self):
        """Test filtering by category IDs."""
        cat_id1 = uuid.uuid4()
        cat_id2 = uuid.uuid4()

        filters = RecipeFilters(
            category_ids=[cat_id1, cat_id2],
        )

        assert len(filters.category_ids) == 2
        assert cat_id1 in filters.category_ids

    # New test case: Unicode and internationalization
    def test_recipe_with_unicode_characters(self):
        """Test recipe with unicode characters in name and description."""
        recipe = RecipeCreate(
            name="Тарамасалата",  # Greek salad in Cyrillic
            description="Délicieuse recette française avec des accents é è ê",
            instructions={"steps": ["准备材料", "混合", "享用"]},  # Chinese steps
            cuisine_type="日本料理",  # Japanese cuisine
        )

        assert recipe.name == "Тарамасалата"
        assert "é" in recipe.description
        assert "准备材料" in recipe.instructions["steps"]

    # New test case: Emoji in recipe
    def test_recipe_with_emoji(self):
        """Test recipe with emoji characters."""
        recipe = RecipeCreate(
            name="Pasta 🍝",
            description="A delicious meal! 😋👨‍🍳",
            instructions={"steps": ["Step 1 🔥", "Step 2 🍴"]},
        )

        assert "🍝" in recipe.name
        assert "😋" in recipe.description

    # New test case: Very long recipe name (boundary)
    def test_recipe_name_max_length(self):
        """Test recipe name at maximum length boundary."""
        long_name = "A" * 255
        recipe = RecipeCreate(
            name=long_name,
            instructions={"steps": ["Test"]},
        )

        assert len(recipe.name) == 255
        assert recipe.name == long_name

    # New test case: Extremely long name (should fail)
    def test_recipe_name_exceeds_max_length(self):
        """Test that excessively long recipe name fails validation."""
        with pytest.raises(ValidationError):
            RecipeCreate(
                name="A" * 256,
                instructions={"steps": ["Test"]},
            )

    # New test case: Complex instructions structure
    def test_recipe_complex_instructions(self):
        """Test recipe with complex nested instructions."""
        complex_instructions = {
            "steps": [
                {"order": 1, "text": "Prepare ingredients", "time": 5},
                {"order": 2, "text": "Mix everything", "time": 10},
            ],
            "tips": ["Use fresh ingredients", "Don't overcook"],
            "equipment": ["pot", "spoon", "bowl"],
        }

        recipe = RecipeCreate(
            name="Test Recipe",
            instructions=complex_instructions,
        )

        assert recipe.instructions["steps"][0]["order"] == 1
        assert len(recipe.instructions["tips"]) == 2
        assert "pot" in recipe.instructions["equipment"]

    # New test case: Empty instructions dictionary (edge case)
    def test_empty_instructions_dict_validation(self):
        """Test that empty instructions dict is rejected."""
        with pytest.raises(ValidationError):
            RecipeCreate(
                name="Test Recipe",
                instructions={},
            )

    # New test case: Maximum values for time fields
    def test_recipe_extreme_time_values(self):
        """Test recipe with very large time values."""
        recipe = RecipeCreate(
            name="Slow Cooked Masterpiece",
            instructions={"steps": ["Cook slowly"]},
            prep_time=1440,  # 24 hours
            cook_time=10080,  # 1 week in minutes
        )

        assert recipe.prep_time == 1440
        assert recipe.cook_time == 10080

    # New test case: Negative cook time
    def test_negative_cook_time(self):
        """Test that negative cook time is not allowed."""
        with pytest.raises(ValidationError):
            RecipeCreate(
                name="Test Recipe",
                instructions={"steps": ["Test"]},
                cook_time=-5,
            )

    # New test case: Negative servings
    def test_negative_servings(self):
        """Test that negative servings are not allowed."""
        with pytest.raises(ValidationError):
            RecipeCreate(
                name="Test Recipe",
                instructions={"steps": ["Test"]},
                servings=-2,
            )

    # New test case: Very large servings number
    def test_large_servings_value(self):
        """Test recipe with large servings number."""
        recipe = RecipeCreate(
            name="Banquet Recipe",
            instructions={"steps": ["Test"]},
            servings=1000,
        )

        assert recipe.servings == 1000

    # New test case: All difficulty levels
    def test_all_difficulty_levels(self):
        """Test recipe creation with all difficulty levels."""
        for difficulty in [DifficultyLevel.EASY, DifficultyLevel.MEDIUM, DifficultyLevel.HARD]:
            recipe = RecipeCreate(
                name=f"Recipe {difficulty.value}",
                instructions={"steps": ["Test"]},
                difficulty=difficulty,
            )
            assert recipe.difficulty == difficulty

    # New test case: Invalid difficulty level
    def test_invalid_difficulty_level(self):
        """Test that invalid difficulty level is rejected."""
        with pytest.raises(ValidationError):
            RecipeCreate(
                name="Test Recipe",
                instructions={"steps": ["Test"]},
                difficulty="very_easy",  # type: ignore
            )

    # New test case: Multiple diet types
    def test_multiple_diet_types(self):
        """Test recipe with multiple diet types."""
        diet_types = ["vegetarian", "vegan", "gluten-free", "dairy-free", "low-carb"]
        recipe = RecipeCreate(
            name="Health Recipe",
            instructions={"steps": ["Test"]},
            diet_types=diet_types,
        )

        assert len(recipe.diet_types) == 5
        assert all(dt in recipe.diet_types for dt in diet_types)

    # New test case: Diet types with mixed case
    def test_diet_types_case_preservation(self):
        """Test that diet types case is preserved."""
        recipe = RecipeCreate(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            diet_types=["Vegetarian", "VEGAN", "gluten-free"],
        )

        assert "Vegetarian" in recipe.diet_types
        assert "VEGAN" in recipe.diet_types

    # New test case: Description with special characters
    def test_recipe_description_special_chars(self):
        """Test recipe with special characters in description."""
        recipe = RecipeCreate(
            name="Test Recipe",
            description="Recipe with special chars: @#$%^&*()_+-=[]{}|;:',.<>?/~`",
            instructions={"steps": ["Test"]},
        )

        assert "@#$%^&*" in recipe.description

    # New test case: Cuisine type with spaces
    def test_cuisine_type_with_spaces(self):
        """Test cuisine type with spaces."""
        recipe = RecipeCreate(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            cuisine_type="Middle Eastern",
        )

        assert recipe.cuisine_type == "Middle Eastern"

    # New test case: Many ingredients
    def test_recipe_with_many_ingredients(self):
        """Test recipe with large number of ingredients."""
        ingredients = [
            IngredientCreate(name=f"Ingredient {i}", quantity=i, unit="g")
            for i in range(50)
        ]

        recipe = RecipeCreate(
            name="Complex Recipe",
            instructions={"steps": ["Test"]},
            ingredients=ingredients,
        )

        assert len(recipe.ingredients) == 50

    # New test case: Ingredients with no unit
    def test_ingredient_without_unit(self):
        """Test ingredient without unit of measurement."""
        recipe = RecipeCreate(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            ingredients=[
                IngredientCreate(name="Salt", quantity=2, unit=None),
            ],
        )

        assert recipe.ingredients[0].unit is None
        assert recipe.ingredients[0].quantity == 2

    # New test case: Ingredients with decimal quantities
    def test_ingredient_decimal_quantities(self):
        """Test ingredients with decimal quantities."""
        recipe = RecipeCreate(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            ingredients=[
                IngredientCreate(name="Flour", quantity=2.5, unit="cups"),
                IngredientCreate(name="Sugar", quantity=0.125, unit="tsp"),
            ],
        )

        assert recipe.ingredients[0].quantity == 2.5
        assert recipe.ingredients[1].quantity == 0.125

    # New test case: Update with invalid negative time
    def test_update_invalid_negative_time(self):
        """Test that update with negative time is rejected."""
        with pytest.raises(ValidationError):
            RecipeUpdate(
                prep_time=-10,
            )

    # New test case: Update with empty string name
    def test_update_empty_name(self):
        """Test that update with empty name is rejected."""
        with pytest.raises(ValidationError):
            RecipeUpdate(
                name="",
            )

    # New test case: Update with only whitespace
    def test_update_whitespace_only_name(self):
        """Test that update with whitespace-only name is rejected."""
        with pytest.raises(ValidationError):
            RecipeUpdate(
                name="   ",
            )

    # New test case: Response with all fields populated
    def test_recipe_response_complete(self):
        """Test recipe response with all fields populated."""
        now = datetime.now(timezone.utc)
        recipe_id = uuid.uuid4()
        cat_id = uuid.uuid4()

        data = {
            "id": recipe_id,
            "name": "Complete Recipe",
            "description": "Full description",
            "instructions": {"steps": ["Step 1", "Step 2"]},
            "prep_time": 15,
            "cook_time": 30,
            "servings": 4,
            "difficulty": "hard",
            "cuisine_type": "French",
            "diet_types": ["vegetarian", "gluten-free"],
            "embedding": [0.1] * 768,
            "ingredients": [],
            "categories": [],
            "nutritional_info": None,
            "created_at": now,
            "updated_at": now,
            "deleted_at": None,
        }

        response = RecipeResponse(**data)

        assert response.total_time == 45
        assert len(response.diet_types) == 2
        assert len(response.embedding) == 768

    # New test case: Filter with boundary values
    def test_filters_boundary_values(self):
        """Test filters with boundary values."""
        filters = RecipeFilters(
            min_prep_time=0,
            max_prep_time=0,
            min_cook_time=0,
            max_cook_time=0,
            min_servings=1,
            max_servings=1,
        )

        assert filters.min_prep_time == 0
        assert filters.max_servings == 1

    # New test case: Filter with very large values
    def test_filters_large_values(self):
        """Test filters with very large time values."""
        filters = RecipeFilters(
            min_prep_time=0,
            max_prep_time=10000,
            min_cook_time=0,
            max_cook_time=50000,
        )

        assert filters.max_cook_time == 50000

    # New test case: Recipe with zero prep time but cook time present
    def test_recipe_zero_prep_time(self):
        """Test recipe with zero prep time but cook time present."""
        recipe = RecipeCreate(
            name="No Prep Recipe",
            instructions={"steps": ["Just cook"]},
            prep_time=0,
            cook_time=20,
        )

        assert recipe.prep_time == 0
        assert recipe.cook_time == 20

    # New test case: Recipe with only prep time
    def test_recipe_only_prep_time(self):
        """Test recipe with only prep time, no cooking."""
        recipe = RecipeCreate(
            name="No Cook Recipe",
            instructions={"steps": ["Prepare"]},
            prep_time=10,
            cook_time=None,
        )

        assert recipe.prep_time == 10
        assert recipe.cook_time is None

    # New test case: Nutritional info with complete data
    def test_recipe_complete_nutritional_info(self):
        """Test recipe with complete nutritional information."""
        recipe = RecipeCreate(
            name="Healthy Recipe",
            instructions={"steps": ["Test"]},
            nutritional_info=NutritionalInfoCreate(
                calories=350.5,
                protein_g=25.0,
                carbohydrates_g=45.0,
                fat_g=12.5,
                fiber_g=8.0,
                sugar_g=5.0,
                sodium_mg=450.0,
                cholesterol_mg=20.0,
                additional_info={"vitamins": {"A": "15%", "C": "30%", "D": "10%"}},
            ),
        )

        assert recipe.nutritional_info.calories == 350.5
        assert recipe.nutritional_info.additional_info["vitamins"]["C"] == "30%"

    # New test case: Empty category_ids
    def test_recipe_empty_category_ids(self):
        """Test recipe with empty category IDs list."""
        recipe = RecipeCreate(
            name="Test Recipe",
            instructions={"steps": ["Test"]},
            category_ids=[],
        )

        assert recipe.category_ids == []

    # New test case: Multiple category IDs
    def test_recipe_multiple_category_ids(self):
        """Test recipe with multiple category IDs."""
        cat_ids = [uuid.uuid4() for _ in range(5)]
        recipe = RecipeCreate(
            name="Multi-Category Recipe",
            instructions={"steps": ["Test"]},
            category_ids=cat_ids,
        )

        assert len(recipe.category_ids) == 5
        assert all(cid in recipe.category_ids for cid in cat_ids)

    # New test case: Filter with negative ranges (should fail)
    def test_filter_negative_min_values(self):
        """Test that negative filter values are rejected."""
        with pytest.raises(ValidationError):
            RecipeFilters(
                min_prep_time=-5,
            )

    # New test case: Instructions with string values in list
    def test_recipe_instructions_simple_list(self):
        """Test recipe with simple string list in instructions."""
        recipe = RecipeCreate(
            name="Simple Recipe",
            instructions={"steps": ["Step 1", "Step 2", "Step 3"]},
        )

        assert len(recipe.instructions["steps"]) == 3
        assert isinstance(recipe.instructions["steps"][0], str)
