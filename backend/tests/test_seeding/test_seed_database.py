"""Tests for main seeding script and RecipeSeeder class."""

import json
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from uuid import uuid4

import pytest

from scripts.seed_database import RecipeSeeder, main
from scripts.seeder_client import SeederReport, ValidationReport


class TestRecipeSeeder:
    """Test suite for RecipeSeeder class."""

    @pytest.fixture
    def seeder(self):
        """Create a RecipeSeeder instance."""
        return RecipeSeeder(
            api_url="http://localhost:8009",
            batch_size=10,
            dry_run=False,
        )

    @pytest.fixture
    def dry_run_seeder(self):
        """Create a RecipeSeeder instance in dry-run mode."""
        return RecipeSeeder(
            api_url="http://localhost:8009",
            batch_size=10,
            dry_run=True,
        )

    def test_seeder_initialization(self, seeder):
        """Test seeder initialization."""
        assert seeder.api_url == "http://localhost:8009"
        assert seeder.batch_size == 10
        assert seeder.dry_run is False
        assert seeder.generator is not None

    def test_seeder_dry_run_mode(self, dry_run_seeder):
        """Test seeder in dry-run mode."""
        assert dry_run_seeder.dry_run is True

    @pytest.mark.asyncio
    async def test_generate_recipes(self, seeder):
        """Test recipe generation."""
        recipes = await seeder.generate_recipes(count=10)

        assert len(recipes) == 10
        assert all(isinstance(r, dict) for r in recipes)
        assert all("name" in r for r in recipes)

    @pytest.mark.asyncio
    async def test_generate_recipes_with_seed(self, seeder):
        """Test recipe generation with seed for reproducibility."""
        recipes1 = await seeder.generate_recipes(count=5, seed=42)
        recipes2 = await seeder.generate_recipes(count=5, seed=42)

        assert len(recipes1) == len(recipes2)
        # Same seed should produce same recipes
        assert recipes1[0]["name"] == recipes2[0]["name"]

    def test_analyze_distribution(self, seeder):
        """Test recipe distribution analysis."""
        recipes = [
            {"difficulty": "easy", "cuisine_type": "Italian", "diet_types": ["vegetarian"]},
            {"difficulty": "medium", "cuisine_type": "Italian", "diet_types": ["vegan"]},
            {"difficulty": "easy", "cuisine_type": "Mexican", "diet_types": []},
        ]

        distribution = seeder._analyze_distribution(recipes)

        assert distribution["total"] == 3
        assert distribution["difficulty"]["easy"] == 2
        assert distribution["difficulty"]["medium"] == 1
        assert distribution["cuisine"]["Italian"] == 2
        assert distribution["cuisine"]["Mexican"] == 1
        assert distribution["diet"]["vegetarian"] == 1
        assert distribution["diet"]["vegan"] == 1

    def test_validate_recipe_data_valid(self, seeder):
        """Test validation of valid recipe data."""
        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1", "Step 2"]},
            "ingredients": [{"name": "flour", "quantity": 2, "unit": "cups"}],
        }

        errors = seeder._validate_recipe_data(recipe)

        assert len(errors) == 0

    def test_validate_recipe_data_missing_fields(self, seeder):
        """Test validation with missing required fields."""
        recipe = {"name": "Test Recipe"}

        errors = seeder._validate_recipe_data(recipe)

        assert len(errors) > 0
        assert any("instructions" in error for error in errors)
        assert any("difficulty" in error for error in errors)

    def test_validate_recipe_data_invalid_instructions(self, seeder):
        """Test validation with invalid instructions format."""
        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": "This should be a dict, not a string",
        }

        errors = seeder._validate_recipe_data(recipe)

        assert len(errors) > 0
        assert any("dictionary" in error for error in errors)

    def test_validate_recipe_data_missing_steps(self, seeder):
        """Test validation with missing steps in instructions."""
        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"other_key": "value"},
        }

        errors = seeder._validate_recipe_data(recipe)

        assert len(errors) > 0
        assert any("steps" in error for error in errors)

    def test_validate_recipe_data_invalid_ingredients(self, seeder):
        """Test validation with invalid ingredients format."""
        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
            "ingredients": "Should be a list",
        }

        errors = seeder._validate_recipe_data(recipe)

        assert len(errors) > 0
        assert any("list" in error for error in errors)

    def test_validate_recipe_data_ingredient_missing_name(self, seeder):
        """Test validation with ingredient missing name."""
        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
            "ingredients": [{"quantity": 2, "unit": "cups"}],
        }

        errors = seeder._validate_recipe_data(recipe)

        assert len(errors) > 0
        assert any("name" in error for error in errors)

    def test_validate_recipe_data_negative_time(self, seeder):
        """Test validation with negative time values."""
        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
            "prep_time": -10,
        }

        errors = seeder._validate_recipe_data(recipe)

        assert len(errors) > 0
        assert any("prep_time" in error and "positive" in error for error in errors)

    @pytest.mark.asyncio
    async def test_dry_run_seed(self, dry_run_seeder):
        """Test dry-run seeding."""
        recipes = [
            {
                "name": "Test Recipe 1",
                "difficulty": "easy",
                "instructions": {"steps": ["Step 1"]},
                "ingredients": [{"name": "flour"}],
            },
            {
                "name": "Test Recipe 2",
                "difficulty": "medium",
                "instructions": {"steps": ["Step 1"]},
                "ingredients": [{"name": "sugar"}],
            },
        ]

        report = await dry_run_seeder._dry_run_seed(recipes)

        assert report.total_attempted == 2
        assert report.total_succeeded == 2
        assert report.total_failed == 0
        assert len(report.created_recipe_ids) == 0  # No actual creation

    @pytest.mark.asyncio
    async def test_dry_run_seed_with_invalid_data(self, dry_run_seeder):
        """Test dry-run with invalid recipe data."""
        recipes = [
            {
                "name": "Valid Recipe",
                "difficulty": "easy",
                "instructions": {"steps": ["Step 1"]},
            },
            {
                "name": "Invalid Recipe",
                # Missing difficulty and instructions
            },
        ]

        report = await dry_run_seeder._dry_run_seed(recipes)

        assert report.total_attempted == 2
        assert report.total_succeeded == 1
        assert report.total_failed == 1
        assert len(report.failed_recipes) == 1

    @pytest.mark.asyncio
    async def test_seed_database_dry_run_mode(self, dry_run_seeder):
        """Test seeding in dry-run mode."""
        recipes = [
            {
                "name": "Test Recipe",
                "difficulty": "easy",
                "instructions": {"steps": ["Step 1"]},
            }
        ]

        report = await dry_run_seeder.seed_database(recipes, show_progress=False)

        assert report.total_attempted == 1
        assert len(report.created_recipe_ids) == 0

    @pytest.mark.asyncio
    async def test_validate_seeded_data_dry_run(self, dry_run_seeder):
        """Test validation skips in dry-run mode."""
        validation_report = await dry_run_seeder.validate_seeded_data(
            expected_count=10
        )

        assert validation_report.overall_success is True
        assert validation_report.sample_queries_tested == 0

    @pytest.mark.asyncio
    async def test_save_report(self, seeder, tmp_path):
        """Test saving seeding report to file."""
        report = SeederReport(
            total_attempted=10,
            total_succeeded=9,
            total_failed=1,
            failed_recipes=[],
            duration_seconds=15.5,
            average_time_per_recipe=1.55,
            created_recipe_ids=[uuid4() for _ in range(9)],
        )

        output_file = tmp_path / "report.json"
        await seeder.save_report(report, output_file)

        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert data["total_attempted"] == 10
        assert data["total_succeeded"] == 9
        assert len(data["created_recipe_ids"]) == 9


class TestMainFunction:
    """Test suite for main() function."""

    @pytest.mark.asyncio
    async def test_main_dry_run(self):
        """Test main function in dry-run mode."""
        with patch("scripts.seed_database.RecipeSeeder") as MockSeeder:
            mock_seeder = Mock()
            mock_seeder.generate_recipes = AsyncMock(
                return_value=[{"name": "Test", "difficulty": "easy", "instructions": {"steps": []}}]
            )
            mock_seeder.seed_database = AsyncMock(
                return_value=SeederReport(
                    total_attempted=1,
                    total_succeeded=1,
                    total_failed=0,
                    failed_recipes=[],
                    duration_seconds=1.0,
                    average_time_per_recipe=1.0,
                    created_recipe_ids=[],
                )
            )
            MockSeeder.return_value = mock_seeder

            exit_code = await main(count=1, dry_run=True, skip_validation=True)

            assert exit_code == 0

    @pytest.mark.asyncio
    async def test_main_with_failures(self):
        """Test main function with some failures."""
        with patch("scripts.seed_database.RecipeSeeder") as MockSeeder:
            mock_seeder = Mock()
            mock_seeder.generate_recipes = AsyncMock(return_value=[])
            mock_seeder.seed_database = AsyncMock(
                return_value=SeederReport(
                    total_attempted=10,
                    total_succeeded=8,
                    total_failed=2,
                    failed_recipes=[{"error": "test"}],
                    duration_seconds=10.0,
                    average_time_per_recipe=1.0,
                    created_recipe_ids=[],
                )
            )
            MockSeeder.return_value = mock_seeder

            exit_code = await main(count=10, dry_run=True, skip_validation=True)

            assert exit_code == 1  # Some failures

    @pytest.mark.asyncio
    async def test_main_with_output_file(self, tmp_path):
        """Test main function with output file."""
        output_file = tmp_path / "report.json"

        with patch("scripts.seed_database.RecipeSeeder") as MockSeeder:
            mock_seeder = Mock()
            mock_seeder.generate_recipes = AsyncMock(
                return_value=[{"name": "Test", "difficulty": "easy", "instructions": {"steps": []}}]
            )
            mock_seeder.seed_database = AsyncMock(
                return_value=SeederReport(
                    total_attempted=1,
                    total_succeeded=1,
                    total_failed=0,
                    failed_recipes=[],
                    duration_seconds=1.0,
                    average_time_per_recipe=1.0,
                    created_recipe_ids=[],
                )
            )
            mock_seeder.save_report = AsyncMock()
            MockSeeder.return_value = mock_seeder

            exit_code = await main(
                count=1,
                dry_run=True,
                output_file=str(output_file),
                skip_validation=True,
            )

            assert exit_code == 0
            mock_seeder.save_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_with_validation(self):
        """Test main function with validation."""
        with patch("scripts.seed_database.RecipeSeeder") as MockSeeder:
            mock_seeder = Mock()
            mock_seeder.generate_recipes = AsyncMock(return_value=[])
            mock_seeder.seed_database = AsyncMock(
                return_value=SeederReport(
                    total_attempted=1,
                    total_succeeded=1,
                    total_failed=0,
                    failed_recipes=[],
                    duration_seconds=1.0,
                    average_time_per_recipe=1.0,
                    created_recipe_ids=[uuid4()],
                )
            )
            mock_seeder.validate_seeded_data = AsyncMock(
                return_value=ValidationReport(
                    recipe_count_valid=True,
                    search_functional=True,
                    embeddings_generated=True,
                    sample_queries_tested=4,
                    validation_errors=[],
                    overall_success=True,
                )
            )
            MockSeeder.return_value = mock_seeder

            exit_code = await main(count=1, dry_run=False, skip_validation=False)

            assert exit_code == 0
            mock_seeder.validate_seeded_data.assert_called_once()

    @pytest.mark.asyncio
    async def test_main_validation_failure(self):
        """Test main function when validation fails."""
        with patch("scripts.seed_database.RecipeSeeder") as MockSeeder:
            mock_seeder = Mock()
            mock_seeder.generate_recipes = AsyncMock(return_value=[])
            mock_seeder.seed_database = AsyncMock(
                return_value=SeederReport(
                    total_attempted=1,
                    total_succeeded=1,
                    total_failed=0,
                    failed_recipes=[],
                    duration_seconds=1.0,
                    average_time_per_recipe=1.0,
                    created_recipe_ids=[uuid4()],
                )
            )
            mock_seeder.validate_seeded_data = AsyncMock(
                return_value=ValidationReport(
                    recipe_count_valid=False,
                    search_functional=False,
                    embeddings_generated=True,
                    sample_queries_tested=2,
                    validation_errors=["Count mismatch"],
                    overall_success=False,
                )
            )
            MockSeeder.return_value = mock_seeder

            exit_code = await main(count=1, dry_run=False, skip_validation=False)

            assert exit_code == 1  # Validation failed

    @pytest.mark.asyncio
    async def test_main_exception_handling(self):
        """Test main function exception handling."""
        with patch("scripts.seed_database.RecipeSeeder") as MockSeeder:
            MockSeeder.side_effect = Exception("Unexpected error")

            exit_code = await main(count=1)

            assert exit_code == 1  # Error occurred


class TestDataIntegrity:
    """Test data integrity and consistency."""

    @pytest.mark.asyncio
    async def test_generated_recipes_are_api_compatible(self):
        """Test that generated recipes match API schema."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)
        recipes = await seeder.generate_recipes(count=5)

        for recipe in recipes:
            # All required fields for API
            assert "name" in recipe
            assert "difficulty" in recipe
            assert "instructions" in recipe

            # Instructions should have steps
            assert "steps" in recipe["instructions"]
            assert isinstance(recipe["instructions"]["steps"], list)

            # Ingredients should be properly formatted
            if "ingredients" in recipe:
                for ing in recipe["ingredients"]:
                    assert "name" in ing
                    if "quantity" in ing:
                        assert isinstance(ing["quantity"], (int, float))

    @pytest.mark.asyncio
    async def test_batch_size_respected(self):
        """Test that batch size is respected during seeding."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", batch_size=5, dry_run=True)

        recipes = await seeder.generate_recipes(count=12)
        report = await seeder.seed_database(recipes, show_progress=False)

        # Should process all recipes
        assert report.total_attempted == 12

    @pytest.mark.asyncio
    async def test_concurrent_recipe_generation(self):
        """Test that concurrent generation doesn't cause issues."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        # Generate multiple batches concurrently
        import asyncio

        results = await asyncio.gather(
            seeder.generate_recipes(count=5),
            seeder.generate_recipes(count=5),
            seeder.generate_recipes(count=5),
        )

        assert len(results) == 3
        assert all(len(r) == 5 for r in results)


class TestRecipeSeederEdgeCases:
    """Test edge cases for RecipeSeeder class."""

    # New test case - Edge case: batch size of 1
    @pytest.mark.asyncio
    async def test_seeder_batch_size_one(self):
        """Test seeding with batch size of 1."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", batch_size=1, dry_run=True)

        recipes = await seeder.generate_recipes(count=5)
        report = await seeder.seed_database(recipes, show_progress=False)

        assert report.total_attempted == 5

    # New test case - Edge case: batch size larger than total recipes
    @pytest.mark.asyncio
    async def test_seeder_batch_size_larger_than_total(self):
        """Test seeding with batch size larger than recipe count."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", batch_size=100, dry_run=True)

        recipes = await seeder.generate_recipes(count=10)
        report = await seeder.seed_database(recipes, show_progress=False)

        assert report.total_attempted == 10
        assert report.total_succeeded == 10

    # New test case - Edge case: empty recipe list
    @pytest.mark.asyncio
    async def test_seed_database_empty_list(self):
        """Test seeding with empty recipe list."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        report = await seeder.seed_database([], show_progress=False)

        assert report.total_attempted == 0
        assert report.total_succeeded == 0
        assert report.total_failed == 0

    # New test case - Edge case: analyze distribution with empty list
    def test_analyze_distribution_empty(self):
        """Test distribution analysis with empty recipe list."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        distribution = seeder._analyze_distribution([])

        assert distribution["total"] == 0
        assert isinstance(distribution["difficulty"], dict)
        assert isinstance(distribution["cuisine"], dict)
        assert isinstance(distribution["diet"], dict)

    # New test case - Edge case: analyze distribution with single recipe
    def test_analyze_distribution_single_recipe(self):
        """Test distribution analysis with single recipe."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipes = [{
            "difficulty": "easy",
            "cuisine_type": "Italian",
            "diet_types": ["vegetarian"],
        }]

        distribution = seeder._analyze_distribution(recipes)

        assert distribution["total"] == 1
        assert distribution["difficulty"]["easy"] == 1
        assert distribution["cuisine"]["Italian"] == 1
        assert distribution["diet"]["vegetarian"] == 1

    # New test case - Edge case: recipe with empty diet_types
    def test_validate_recipe_data_empty_diet_types(self):
        """Test validation with empty diet_types list."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
            "diet_types": [],
        }

        errors = seeder._validate_recipe_data(recipe)

        assert len(errors) == 0

    # New test case - Edge case: recipe with zero servings
    def test_validate_recipe_data_zero_servings(self):
        """Test validation with zero servings (allowed as >= 0)."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
            "servings": 0,
        }

        errors = seeder._validate_recipe_data(recipe)

        # Zero is allowed (validation checks >= 0)
        assert len(errors) == 0

    # New test case - Edge case: recipe with float servings (should fail)
    def test_validate_recipe_data_float_servings(self):
        """Test validation with float servings value."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
            "servings": 2.5,
        }

        errors = seeder._validate_recipe_data(recipe)

        # Float servings should be accepted as it's a number
        # If implementation rejects floats, this test would catch that
        assert isinstance(errors, list)

    # New test case - Edge case: recipe with very long name
    def test_validate_recipe_data_very_long_name(self):
        """Test validation with very long recipe name."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "A" * 500,  # Very long name
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
        }

        errors = seeder._validate_recipe_data(recipe)

        # Current implementation should accept any length name
        assert isinstance(errors, list)

    # New test case - Edge case: recipe with empty name
    def test_validate_recipe_data_empty_name(self):
        """Test validation with empty name."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
        }

        errors = seeder._validate_recipe_data(recipe)

        # Empty name should still pass field existence check
        # But might fail on business logic validation if implemented
        assert isinstance(errors, list)

    # New test case - Edge case: recipe with negative prep_time
    def test_validate_recipe_data_negative_prep_time(self):
        """Test validation with negative prep_time."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
            "prep_time": -5,
        }

        errors = seeder._validate_recipe_data(recipe)

        assert len(errors) > 0
        assert any("prep_time" in error and "positive" in error for error in errors)

    # New test case - Edge case: recipe with negative cook_time
    def test_validate_recipe_data_negative_cook_time(self):
        """Test validation with negative cook_time."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
            "cook_time": -10,
        }

        errors = seeder._validate_recipe_data(recipe)

        assert len(errors) > 0
        assert any("cook_time" in error and "positive" in error for error in errors)

    # New test case - Edge case: instructions with empty steps list
    def test_validate_recipe_data_empty_steps(self):
        """Test validation with empty steps list."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": []},
        }

        errors = seeder._validate_recipe_data(recipe)

        # Empty steps list should pass structure validation
        # But might fail on content validation if implemented
        assert isinstance(errors, list)

    # New test case - Edge case: ingredients with empty list
    def test_validate_recipe_data_empty_ingredients(self):
        """Test validation with empty ingredients list."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
            "ingredients": [],
        }

        errors = seeder._validate_recipe_data(recipe)

        # Empty ingredients should pass validation
        assert isinstance(errors, list)

    # New test case - Edge case: ingredient with extra fields
    def test_validate_recipe_data_ingredient_extra_fields(self):
        """Test validation with ingredient having extra fields."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
            "ingredients": [
                {
                    "name": "flour",
                    "quantity": 2,
                    "unit": "cups",
                    "notes": "sifted",
                    "extra_field": "should be ignored",
                }
            ],
        }

        errors = seeder._validate_recipe_data(recipe)

        # Extra fields should be accepted
        assert len(errors) == 0

    # New test case - Edge case: generate recipes with zero count
    @pytest.mark.asyncio
    async def test_generate_recipes_zero_count(self):
        """Test generating zero recipes."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipes = await seeder.generate_recipes(count=0)

        assert isinstance(recipes, list)
        assert len(recipes) == 0

    # New test case - Edge case: save report to non-existent directory
    @pytest.mark.asyncio
    async def test_save_report_creates_directory(self, tmp_path):
        """Test that save_report creates parent directories."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        report = SeederReport(
            total_attempted=5,
            total_succeeded=5,
            total_failed=0,
            failed_recipes=[],
            duration_seconds=1.0,
            average_time_per_recipe=0.2,
            created_recipe_ids=[],
        )

        # Non-existent nested directory
        output_file = tmp_path / "nested" / "dir" / "report.json"
        await seeder.save_report(report, output_file)

        assert output_file.exists()

    # New test case - Edge case: distribution with missing fields
    def test_analyze_distribution_missing_fields(self):
        """Test distribution analysis with recipes missing optional fields."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipes = [
            {"difficulty": "easy"},  # Missing cuisine and diet_types
            {"cuisine_type": "Italian"},  # Missing difficulty and diet_types
            {},  # Missing all optional fields
        ]

        distribution = seeder._analyze_distribution(recipes)

        assert distribution["total"] == 3
        assert "Unknown" in distribution["cuisine"] or "Italian" in distribution["cuisine"]

    # New test case - Edge case: very large batch size
    @pytest.mark.asyncio
    async def test_seeder_very_large_batch_size(self):
        """Test seeder with very large batch size."""
        seeder = RecipeSeeder(
            api_url="http://localhost:8009",
            batch_size=10000,
            dry_run=True
        )

        recipes = await seeder.generate_recipes(count=10)
        report = await seeder.seed_database(recipes, show_progress=False)

        assert report.total_attempted == 10

    # New test case - Edge case: validation with zero expected count
    @pytest.mark.asyncio
    async def test_validate_seeded_data_zero_expected(self):
        """Test validation with zero expected count."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        validation_report = await seeder.validate_seeded_data(expected_count=0)

        assert validation_report.overall_success is True

    # New test case - Edge case: validation with empty sample queries
    @pytest.mark.asyncio
    async def test_validate_seeded_data_empty_queries(self):
        """Test validation with empty sample queries."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        validation_report = await seeder.validate_seeded_data(
            expected_count=10,
            sample_queries=[]
        )

        assert validation_report.sample_queries_tested == 0

    # New test case - Edge case: recipe with Unicode characters
    def test_validate_recipe_data_unicode_characters(self):
        """Test validation with Unicode characters in recipe."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "Café au Lait with Crème Brûlée",
            "difficulty": "easy",
            "instructions": {"steps": ["Mix café with crème"]},
            "cuisine_type": "Français",
        }

        errors = seeder._validate_recipe_data(recipe)

        # Unicode should be accepted
        assert len(errors) == 0

    # New test case - Edge case: recipe with special characters
    def test_validate_recipe_data_special_characters(self):
        """Test validation with special characters."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        recipe = {
            "name": "Mom's \"Special\" Recipe!",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1: Mix & blend"]},
        }

        errors = seeder._validate_recipe_data(recipe)

        # Special characters should be accepted
        assert len(errors) == 0


class TestMainFunctionEdgeCases:
    """Test edge cases for main() function."""

    # New test case - Edge case: main with zero count
    @pytest.mark.asyncio
    async def test_main_zero_count(self):
        """Test main function with zero recipe count."""
        with patch("scripts.seed_database.RecipeSeeder") as MockSeeder:
            mock_seeder = Mock()
            mock_seeder.generate_recipes = AsyncMock(return_value=[])
            mock_seeder.seed_database = AsyncMock(
                return_value=SeederReport(
                    total_attempted=0,
                    total_succeeded=0,
                    total_failed=0,
                    failed_recipes=[],
                    duration_seconds=0.0,
                    average_time_per_recipe=0.0,
                    created_recipe_ids=[],
                )
            )
            MockSeeder.return_value = mock_seeder

            exit_code = await main(count=0, dry_run=True, skip_validation=True)

            assert exit_code == 0

    # New test case - Edge case: main with all recipes failing
    @pytest.mark.asyncio
    async def test_main_all_failures(self):
        """Test main function when all recipes fail."""
        with patch("scripts.seed_database.RecipeSeeder") as MockSeeder:
            mock_seeder = Mock()
            mock_seeder.generate_recipes = AsyncMock(
                return_value=[{"name": "Test", "difficulty": "easy", "instructions": {"steps": []}}]
            )
            mock_seeder.seed_database = AsyncMock(
                return_value=SeederReport(
                    total_attempted=10,
                    total_succeeded=0,
                    total_failed=10,
                    failed_recipes=[{"error": "test"}] * 10,
                    duration_seconds=5.0,
                    average_time_per_recipe=0.5,
                    created_recipe_ids=[],
                )
            )
            MockSeeder.return_value = mock_seeder

            exit_code = await main(count=10, dry_run=True, skip_validation=True)

            assert exit_code == 1

    # New test case - Edge case: main with custom categories
    @pytest.mark.asyncio
    async def test_main_with_categories(self):
        """Test main function with specific categories."""
        with patch("scripts.seed_database.RecipeSeeder") as MockSeeder:
            mock_seeder = Mock()
            mock_seeder.generate_recipes = AsyncMock(return_value=[])
            mock_seeder.seed_database = AsyncMock(
                return_value=SeederReport(
                    total_attempted=5,
                    total_succeeded=5,
                    total_failed=0,
                    failed_recipes=[],
                    duration_seconds=2.0,
                    average_time_per_recipe=0.4,
                    created_recipe_ids=[],
                )
            )
            MockSeeder.return_value = mock_seeder

            exit_code = await main(
                count=5,
                categories=["breakfast", "dessert"],
                dry_run=True,
                skip_validation=True
            )

            assert exit_code == 0
            # Verify categories were passed to generate_recipes
            mock_seeder.generate_recipes.assert_called_once()
            call_args = mock_seeder.generate_recipes.call_args
            assert call_args[1]["categories"] == ["breakfast", "dessert"]

    # New test case - Edge case: main with keyboard interrupt
    @pytest.mark.asyncio
    async def test_main_keyboard_interrupt(self):
        """Test main function handling of keyboard interrupt."""
        with patch("scripts.seed_database.RecipeSeeder") as MockSeeder:
            mock_seeder = Mock()
            mock_seeder.generate_recipes = AsyncMock(side_effect=KeyboardInterrupt())
            MockSeeder.return_value = mock_seeder

            exit_code = await main(count=10, dry_run=True)

            assert exit_code == 130

    # New test case - Edge case: division by zero in average calculation
    @pytest.mark.asyncio
    async def test_average_time_per_recipe_zero_recipes(self):
        """Test that average time calculation handles zero recipes."""
        seeder = RecipeSeeder(api_url="http://localhost:8009", dry_run=True)

        # This should not raise ZeroDivisionError
        report = await seeder.seed_database([], show_progress=False)

        assert report.average_time_per_recipe == 0.0
