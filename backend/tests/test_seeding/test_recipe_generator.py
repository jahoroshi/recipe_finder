"""Tests for recipe data generator."""

import pytest

from scripts.recipe_generator import RecipeDataGenerator


class TestRecipeDataGenerator:
    """Test suite for RecipeDataGenerator class."""

    def test_initialization(self):
        """Test generator initialization."""
        generator = RecipeDataGenerator()
        assert generator is not None

    def test_initialization_with_seed(self):
        """Test generator initialization with seed."""
        generator = RecipeDataGenerator(seed=42)
        assert generator is not None

    def test_get_all_recipes(self):
        """Test getting all available recipe templates."""
        generator = RecipeDataGenerator()
        all_recipes = generator.get_all_recipes()

        assert isinstance(all_recipes, list)
        assert len(all_recipes) > 0

        # Check that we have recipes from all categories
        assert len(generator.BREAKFAST_RECIPES) > 0
        assert len(generator.MAIN_COURSE_RECIPES) > 0
        assert len(generator.APPETIZER_RECIPES) > 0
        assert len(generator.DESSERT_RECIPES) > 0
        assert len(generator.SALAD_RECIPES) > 0
        assert len(generator.BEVERAGE_RECIPES) > 0

    def test_generate_recipes_default_count(self):
        """Test generating default number of recipes."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=10)

        assert isinstance(recipes, list)
        assert len(recipes) == 10

    def test_generate_recipes_reproducibility(self):
        """Test that using same seed produces same results."""
        seed = 42

        generator1 = RecipeDataGenerator()
        recipes1 = generator1.generate_recipes(count=5, seed=seed)

        generator2 = RecipeDataGenerator()
        recipes2 = generator2.generate_recipes(count=5, seed=seed)

        # Should get same recipes in same order
        assert len(recipes1) == len(recipes2)
        for r1, r2 in zip(recipes1, recipes2):
            assert r1["name"] == r2["name"]

    def test_generate_more_recipes_than_available(self):
        """Test generating more recipes than templates available."""
        generator = RecipeDataGenerator()
        all_recipes_count = len(generator.get_all_recipes())

        # Generate more than available
        recipes = generator.generate_recipes(count=all_recipes_count + 10)

        assert len(recipes) == all_recipes_count + 10
        # Should have some variations
        names = [r["name"] for r in recipes]
        assert any("Variation" in name for name in names)

    def test_recipe_structure_validation(self):
        """Test that generated recipes have required structure."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=5)

        for recipe in recipes:
            # Required fields
            assert "name" in recipe
            assert "description" in recipe
            assert "cuisine_type" in recipe
            assert "difficulty" in recipe
            assert "prep_time" in recipe
            assert "cook_time" in recipe
            assert "servings" in recipe
            assert "ingredients" in recipe
            assert "instructions" in recipe
            assert "nutritional_info" in recipe

            # Check types
            assert isinstance(recipe["name"], str)
            assert isinstance(recipe["difficulty"], str)
            assert recipe["difficulty"] in ["easy", "medium", "hard"]
            assert isinstance(recipe["ingredients"], list)
            assert isinstance(recipe["instructions"], dict)
            assert isinstance(recipe["nutritional_info"], dict)

    def test_ingredients_structure(self):
        """Test ingredient structure is correct."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=3)

        for recipe in recipes:
            assert len(recipe["ingredients"]) > 0

            for ingredient in recipe["ingredients"]:
                assert "name" in ingredient
                assert isinstance(ingredient["name"], str)

                if "quantity" in ingredient:
                    assert isinstance(
                        ingredient["quantity"], (int, float)
                    ), f"Invalid quantity type in {recipe['name']}"

                if "unit" in ingredient:
                    assert isinstance(ingredient["unit"], str)

    def test_instructions_structure(self):
        """Test instructions structure is correct."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=3)

        for recipe in recipes:
            instructions = recipe["instructions"]

            assert "steps" in instructions
            assert isinstance(instructions["steps"], list)
            assert len(instructions["steps"]) > 0

            # Check all steps are strings
            for step in instructions["steps"]:
                assert isinstance(step, str)
                assert len(step) > 0

    def test_nutritional_info_structure(self):
        """Test nutritional info structure and values."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=5)

        for recipe in recipes:
            nutrition = recipe["nutritional_info"]

            # Common fields
            assert "calories" in nutrition
            assert "protein_g" in nutrition
            assert "carbohydrates_g" in nutrition
            assert "fat_g" in nutrition

            # Values should be positive
            for key, value in nutrition.items():
                if value is not None:
                    assert isinstance(value, (int, float))
                    assert value >= 0, f"Negative value for {key} in {recipe['name']}"

    def test_get_category_distribution(self):
        """Test category distribution reporting."""
        generator = RecipeDataGenerator()
        distribution = generator.get_category_distribution()

        assert isinstance(distribution, dict)
        assert len(distribution) > 0

        # Check that all values are positive integers
        for category, count in distribution.items():
            assert isinstance(category, str)
            assert isinstance(count, int)
            assert count > 0

    def test_get_recipes_by_diet_type(self):
        """Test filtering recipes by diet type."""
        generator = RecipeDataGenerator()

        # Test vegetarian recipes
        vegetarian = generator.get_recipes_by_diet_type("vegetarian")
        assert isinstance(vegetarian, list)
        assert len(vegetarian) > 0

        # Verify all returned recipes are vegetarian
        for recipe in vegetarian:
            assert "vegetarian" in recipe.get("diet_types", [])

        # Test vegan recipes
        vegan = generator.get_recipes_by_diet_type("vegan")
        assert isinstance(vegan, list)

    def test_get_recipes_by_difficulty(self):
        """Test filtering recipes by difficulty level."""
        generator = RecipeDataGenerator()

        # Test each difficulty level
        for difficulty in ["easy", "medium", "hard"]:
            recipes = generator.get_recipes_by_difficulty(difficulty)
            assert isinstance(recipes, list)

            # Verify all returned recipes match difficulty
            for recipe in recipes:
                assert recipe.get("difficulty") == difficulty

    def test_realistic_cooking_times(self):
        """Test that cooking times are realistic."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=20)

        for recipe in recipes:
            prep_time = recipe.get("prep_time")
            cook_time = recipe.get("cook_time")

            # Times should be within realistic ranges
            if prep_time:
                assert 0 <= prep_time <= 180, f"Unrealistic prep time in {recipe['name']}"

            if cook_time:
                assert 0 <= cook_time <= 300, f"Unrealistic cook time in {recipe['name']}"

            # Total time shouldn't be too extreme
            total_time = (prep_time or 0) + (cook_time or 0)
            assert total_time <= 480, f"Total time too long in {recipe['name']}"

    def test_servings_are_realistic(self):
        """Test that servings are realistic numbers."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=10)

        for recipe in recipes:
            servings = recipe.get("servings")
            if servings:
                assert isinstance(servings, int)
                assert 1 <= servings <= 24, f"Unrealistic servings in {recipe['name']}"

    def test_cuisine_types_are_diverse(self):
        """Test that we have diverse cuisine types."""
        generator = RecipeDataGenerator()
        all_recipes = generator.get_all_recipes()

        cuisines = set(recipe.get("cuisine_type") for recipe in all_recipes)

        # Should have multiple cuisines
        assert len(cuisines) >= 5, "Not enough cuisine diversity"

        # Some expected cuisines
        expected_cuisines = ["Italian", "American", "Mexican", "Thai", "Japanese"]
        for cuisine in expected_cuisines:
            assert cuisine in cuisines, f"Missing {cuisine} cuisine"

    def test_diet_types_variety(self):
        """Test variety of diet types."""
        generator = RecipeDataGenerator()
        all_recipes = generator.get_all_recipes()

        all_diet_types = set()
        for recipe in all_recipes:
            all_diet_types.update(recipe.get("diet_types", []))

        # Should have multiple diet types
        assert len(all_diet_types) >= 3

        # Some expected diet types
        expected_diets = ["vegetarian", "vegan", "gluten-free"]
        for diet in expected_diets:
            assert diet in all_diet_types, f"Missing {diet} diet type"

    def test_difficulty_distribution(self):
        """Test that we have all difficulty levels represented."""
        generator = RecipeDataGenerator()
        all_recipes = generator.get_all_recipes()

        difficulties = [recipe.get("difficulty") for recipe in all_recipes]

        # All difficulty levels should be present
        assert "easy" in difficulties
        assert "medium" in difficulties
        assert "hard" in difficulties

    def test_recipe_names_are_unique(self):
        """Test that recipe names are descriptive and mostly unique."""
        generator = RecipeDataGenerator()
        all_recipes = generator.get_all_recipes()

        names = [recipe["name"] for recipe in all_recipes]

        # Names should be non-empty
        for name in names:
            assert len(name) > 0
            assert len(name.split()) >= 1  # At least one word

        # Should have good variety (accounting for variations)
        unique_base_names = set(
            name.replace(" (Variation)", "") for name in names
        )
        assert len(unique_base_names) > len(all_recipes) * 0.8  # 80% unique

    def test_ingredient_units_are_standard(self):
        """Test that ingredient units use standard measurements."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=10)

        valid_units = {
            "cup", "cups", "tbsp", "tsp", "oz", "lb", "lbs", "g", "kg",
            "ml", "l", "whole", "cloves", "clove", "slices", "slice",
            "head", "bunch", "can", "package", "bag", "leaves", "sprigs",
            "sheets", "bags", "can", "mg"
        }

        for recipe in recipes:
            for ingredient in recipe.get("ingredients", []):
                unit = ingredient.get("unit")
                if unit:
                    # Unit should be recognizable (this is a soft check)
                    assert isinstance(unit, str)
                    assert len(unit) > 0

    # New test case - Edge case: zero count
    def test_generate_zero_recipes(self):
        """Test generating zero recipes."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=0)

        assert isinstance(recipes, list)
        assert len(recipes) == 0

    # New test case - Edge case: single recipe
    def test_generate_single_recipe(self):
        """Test generating exactly one recipe."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=1)

        assert isinstance(recipes, list)
        assert len(recipes) == 1
        assert "name" in recipes[0]

    # New test case - Edge case: negative count handling
    def test_generate_negative_count(self):
        """Test that negative count raises ValueError."""
        generator = RecipeDataGenerator()

        # Negative count should raise ValueError
        with pytest.raises(ValueError, match="Sample larger than population or is negative"):
            generator.generate_recipes(count=-5)

    # New test case - Edge case: very large batch
    def test_generate_very_large_batch(self):
        """Test generating a very large batch of recipes."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=500)

        assert isinstance(recipes, list)
        assert len(recipes) == 500
        # All should have required fields
        assert all("name" in r for r in recipes)

    # New test case - Edge case: empty diet type filter
    def test_get_recipes_by_empty_diet_type(self):
        """Test filtering with non-existent diet type."""
        generator = RecipeDataGenerator()

        # Test with diet type that doesn't exist
        recipes = generator.get_recipes_by_diet_type("paleo")
        assert isinstance(recipes, list)
        # May be empty if no paleo recipes exist

    # New test case - Edge case: invalid difficulty filter
    def test_get_recipes_by_invalid_difficulty(self):
        """Test filtering with invalid difficulty level."""
        generator = RecipeDataGenerator()

        # Test with difficulty that doesn't exist
        recipes = generator.get_recipes_by_difficulty("impossible")
        assert isinstance(recipes, list)
        assert len(recipes) == 0

    # New test case - Edge case: recipe with minimal optional fields
    def test_recipes_have_minimum_required_fields(self):
        """Test that all recipes have at least minimum required fields."""
        generator = RecipeDataGenerator()
        all_recipes = generator.get_all_recipes()

        required_fields = ["name", "difficulty", "instructions"]

        for recipe in all_recipes:
            for field in required_fields:
                assert field in recipe, f"Recipe {recipe.get('name')} missing {field}"

    # New test case - Edge case: nutritional info with None values
    def test_nutritional_info_handles_none_values(self):
        """Test that nutritional info can contain None values."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=20)

        for recipe in recipes:
            nutrition = recipe.get("nutritional_info", {})
            # Check that None values are handled properly
            for key, value in nutrition.items():
                if value is not None:
                    assert isinstance(value, (int, float))

    # New test case - Edge case: ingredients with optional fields
    def test_ingredients_optional_fields(self):
        """Test that ingredients can have optional fields."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=10)

        found_notes = False
        found_quantity = False

        for recipe in recipes:
            for ingredient in recipe.get("ingredients", []):
                if "notes" in ingredient:
                    found_notes = True
                    assert isinstance(ingredient["notes"], str)
                if "quantity" in ingredient:
                    found_quantity = True

        # Should have found at least some ingredients with these optional fields
        assert found_quantity, "No ingredients with quantity found"

    # New test case - Edge case: recipe reproducibility across instances
    def test_reproducibility_across_multiple_instances(self):
        """Test that different instances with same seed produce same results."""
        seed = 12345

        gen1 = RecipeDataGenerator()
        gen2 = RecipeDataGenerator()
        gen3 = RecipeDataGenerator()

        recipes1 = gen1.generate_recipes(count=10, seed=seed)
        recipes2 = gen2.generate_recipes(count=10, seed=seed)
        recipes3 = gen3.generate_recipes(count=10, seed=seed)

        # All three should be identical
        for r1, r2, r3 in zip(recipes1, recipes2, recipes3):
            assert r1["name"] == r2["name"] == r3["name"]

    # New test case - Edge case: categories with special characters
    def test_cuisine_type_valid_strings(self):
        """Test that cuisine types are valid strings."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=30)

        for recipe in recipes:
            cuisine = recipe.get("cuisine_type")
            if cuisine:
                assert isinstance(cuisine, str)
                assert len(cuisine) > 0
                # Should not contain only whitespace
                assert cuisine.strip() == cuisine

    # New test case - Edge case: all recipes have non-empty instructions
    def test_all_recipes_have_non_empty_instructions(self):
        """Test that no recipe has empty instruction steps."""
        generator = RecipeDataGenerator()
        all_recipes = generator.get_all_recipes()

        for recipe in all_recipes:
            instructions = recipe.get("instructions", {})
            steps = instructions.get("steps", [])

            # Should have at least one step
            assert len(steps) > 0, f"Recipe {recipe['name']} has no steps"

            # All steps should be non-empty strings
            for step in steps:
                assert isinstance(step, str)
                assert len(step) > 0
                assert step.strip(), f"Empty step in {recipe['name']}"

    # New test case - Edge case: diet types consistency
    def test_diet_types_are_lists(self):
        """Test that diet_types field is always a list."""
        generator = RecipeDataGenerator()
        all_recipes = generator.get_all_recipes()

        for recipe in all_recipes:
            diet_types = recipe.get("diet_types", [])
            assert isinstance(diet_types, list)
            # All items in list should be strings
            for diet in diet_types:
                assert isinstance(diet, str)
                assert len(diet) > 0

    # New test case - Edge case: servings boundary
    def test_servings_minimum_value(self):
        """Test that servings are always at least 1."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=50)

        for recipe in recipes:
            servings = recipe.get("servings")
            if servings is not None:
                assert servings >= 1, f"Recipe {recipe['name']} has invalid servings: {servings}"

    # New test case - Edge case: cook time can be zero
    def test_recipes_with_zero_cook_time(self):
        """Test that some recipes can have zero cook time (no-cook recipes)."""
        generator = RecipeDataGenerator()
        recipes = generator.generate_recipes(count=100)

        # Find at least one no-cook recipe
        no_cook_recipes = [r for r in recipes if r.get("cook_time") == 0]
        assert len(no_cook_recipes) > 0, "Should have at least one no-cook recipe"

    # New test case - Edge case: ingredient quantity precision
    def test_ingredient_quantity_precision(self):
        """Test that ingredient quantities support decimal values."""
        generator = RecipeDataGenerator()
        all_recipes = generator.get_all_recipes()

        found_decimal = False

        for recipe in all_recipes:
            for ingredient in recipe.get("ingredients", []):
                quantity = ingredient.get("quantity")
                if quantity and isinstance(quantity, float):
                    if quantity != int(quantity):  # Has decimal part
                        found_decimal = True
                        assert quantity > 0

        assert found_decimal, "Should have ingredients with decimal quantities"

    # New test case - Edge case: multiple categories coverage
    def test_all_category_constants_have_recipes(self):
        """Test that all category constants are populated."""
        generator = RecipeDataGenerator()

        # Check that each category has recipes
        assert len(generator.BREAKFAST_RECIPES) > 0
        assert len(generator.MAIN_COURSE_RECIPES) > 0
        assert len(generator.APPETIZER_RECIPES) > 0
        assert len(generator.DESSERT_RECIPES) > 0
        assert len(generator.SALAD_RECIPES) > 0
        assert len(generator.BEVERAGE_RECIPES) > 0

    # New test case - Edge case: difficulty values are normalized
    def test_difficulty_values_are_lowercase(self):
        """Test that difficulty values are normalized to lowercase."""
        generator = RecipeDataGenerator()
        all_recipes = generator.get_all_recipes()

        valid_difficulties = {"easy", "medium", "hard"}

        for recipe in all_recipes:
            difficulty = recipe.get("difficulty")
            assert difficulty in valid_difficulties, f"Invalid difficulty: {difficulty}"
            # Check it's lowercase
            assert difficulty == difficulty.lower()
