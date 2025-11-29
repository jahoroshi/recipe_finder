"""Tests for NutritionalInfo Pydantic schemas."""

import uuid

import pytest
from pydantic import ValidationError

from app.schemas.nutritional_info import (
    NutritionalInfoCreate,
    NutritionalInfoResponse,
    NutritionalInfoUpdate,
)


class TestNutritionalInfoCreateSchema:
    """Tests for NutritionalInfoCreate schema."""

    def test_valid_nutritional_info_create(self):
        """Test creating valid nutritional information."""
        nutrition = NutritionalInfoCreate(
            calories=250.0,
            protein_g=10.0,
            carbohydrates_g=30.0,
            fat_g=8.0,
            fiber_g=5.0,
            sugar_g=10.0,
            sodium_mg=200.0,
            cholesterol_mg=15.0,
        )

        assert nutrition.calories == 250.0
        assert nutrition.protein_g == 10.0
        assert nutrition.carbohydrates_g == 30.0

    def test_nutritional_info_all_none(self):
        """Test nutritional info with all fields None (optional)."""
        nutrition = NutritionalInfoCreate()

        assert nutrition.calories is None
        assert nutrition.protein_g is None
        assert nutrition.carbohydrates_g is None

    def test_nutritional_info_with_additional_info(self):
        """Test nutritional info with additional data."""
        nutrition = NutritionalInfoCreate(
            calories=300.0,
            additional_info={"vitamins": {"A": "10%", "C": "20%"}},
        )

        assert nutrition.additional_info["vitamins"]["A"] == "10%"
        assert nutrition.additional_info["vitamins"]["C"] == "20%"

    def test_negative_calories(self):
        """Test that negative calories are not allowed."""
        with pytest.raises(ValidationError):
            NutritionalInfoCreate(
                calories=-100.0,
            )

    def test_negative_protein(self):
        """Test that negative protein is not allowed."""
        with pytest.raises(ValidationError):
            NutritionalInfoCreate(
                protein_g=-5.0,
            )

    def test_negative_carbohydrates(self):
        """Test that negative carbohydrates are not allowed."""
        with pytest.raises(ValidationError):
            NutritionalInfoCreate(
                carbohydrates_g=-10.0,
            )

    def test_negative_fat(self):
        """Test that negative fat is not allowed."""
        with pytest.raises(ValidationError):
            NutritionalInfoCreate(
                fat_g=-3.0,
            )

    def test_negative_fiber(self):
        """Test that negative fiber is not allowed."""
        with pytest.raises(ValidationError):
            NutritionalInfoCreate(
                fiber_g=-2.0,
            )

    def test_negative_sugar(self):
        """Test that negative sugar is not allowed."""
        with pytest.raises(ValidationError):
            NutritionalInfoCreate(
                sugar_g=-5.0,
            )

    def test_negative_sodium(self):
        """Test that negative sodium is not allowed."""
        with pytest.raises(ValidationError):
            NutritionalInfoCreate(
                sodium_mg=-100.0,
            )

    def test_negative_cholesterol(self):
        """Test that negative cholesterol is not allowed."""
        with pytest.raises(ValidationError):
            NutritionalInfoCreate(
                cholesterol_mg=-10.0,
            )

    def test_zero_values(self):
        """Test that zero values are allowed."""
        nutrition = NutritionalInfoCreate(
            calories=0,
            protein_g=0,
            carbohydrates_g=0,
            fat_g=0,
            fiber_g=0,
            sugar_g=0,
            sodium_mg=0,
            cholesterol_mg=0,
        )

        assert nutrition.calories == 0
        assert nutrition.protein_g == 0

    def test_decimal_values(self):
        """Test nutritional info with decimal values."""
        nutrition = NutritionalInfoCreate(
            calories=250.75,
            protein_g=10.25,
            carbohydrates_g=30.5,
            fat_g=8.125,
        )

        assert nutrition.calories == 250.75
        assert nutrition.protein_g == 10.25

    def test_very_small_values(self):
        """Test nutritional info with very small values."""
        nutrition = NutritionalInfoCreate(
            protein_g=0.001,
            fiber_g=0.0001,
        )

        assert nutrition.protein_g == 0.001
        assert nutrition.fiber_g == 0.0001

    def test_very_large_values(self):
        """Test nutritional info with very large values."""
        nutrition = NutritionalInfoCreate(
            calories=10000.0,
            sodium_mg=50000.0,
        )

        assert nutrition.calories == 10000.0
        assert nutrition.sodium_mg == 50000.0

    # New test case: Additional info not a dict (should fail)
    def test_additional_info_not_dict(self):
        """Test that non-dict additional_info is rejected."""
        with pytest.raises(ValidationError):
            NutritionalInfoCreate(
                additional_info="not a dict",  # type: ignore
            )

    # New test case: Complex additional info structure
    def test_complex_additional_info(self):
        """Test nutritional info with complex additional data."""
        nutrition = NutritionalInfoCreate(
            calories=300.0,
            additional_info={
                "vitamins": {
                    "A": {"amount": "500 IU", "dv_percentage": "10%"},
                    "C": {"amount": "60 mg", "dv_percentage": "100%"},
                },
                "minerals": {
                    "calcium": "300 mg",
                    "iron": "2 mg",
                },
                "allergens": ["milk", "eggs"],
                "health_claims": "Low sodium",
            },
        )

        assert nutrition.additional_info["vitamins"]["A"]["amount"] == "500 IU"
        assert nutrition.additional_info["minerals"]["calcium"] == "300 mg"
        assert "milk" in nutrition.additional_info["allergens"]

    # New test case: Empty additional info dict
    def test_empty_additional_info_dict(self):
        """Test nutritional info with empty additional info dict."""
        nutrition = NutritionalInfoCreate(
            calories=100.0,
            additional_info={},
        )

        assert nutrition.additional_info == {}

    # New test case: Only some fields populated
    def test_partial_nutritional_info(self):
        """Test nutritional info with only some fields populated."""
        nutrition = NutritionalInfoCreate(
            calories=200.0,
            protein_g=15.0,
            # Other fields None
        )

        assert nutrition.calories == 200.0
        assert nutrition.protein_g == 15.0
        assert nutrition.carbohydrates_g is None
        assert nutrition.fat_g is None

    # New test case: Integer values (should work as floats)
    def test_integer_values(self):
        """Test nutritional info with integer values."""
        nutrition = NutritionalInfoCreate(
            calories=250,
            protein_g=10,
            carbohydrates_g=30,
        )

        assert nutrition.calories == 250
        assert nutrition.protein_g == 10
        assert isinstance(nutrition.calories, (int, float))

    # New test case: Additional info with unicode
    def test_additional_info_unicode(self):
        """Test additional info with unicode characters."""
        nutrition = NutritionalInfoCreate(
            calories=100.0,
            additional_info={
                "note": "Información nutricional",
                "警告": "Contains nuts",
            },
        )

        assert "Información" in nutrition.additional_info["note"]
        assert nutrition.additional_info["警告"] == "Contains nuts"

    # New test case: Additional info with nested lists
    def test_additional_info_nested_lists(self):
        """Test additional info with nested lists."""
        nutrition = NutritionalInfoCreate(
            calories=150.0,
            additional_info={
                "allergens": ["peanuts", "tree nuts", "soy"],
                "certifications": ["organic", "non-gmo", "kosher"],
            },
        )

        assert len(nutrition.additional_info["allergens"]) == 3
        assert "organic" in nutrition.additional_info["certifications"]

    # New test case: Additional info with numbers
    def test_additional_info_with_numbers(self):
        """Test additional info with numeric values."""
        nutrition = NutritionalInfoCreate(
            calories=200.0,
            additional_info={
                "serving_size": 100,
                "servings_per_container": 4,
                "vitamin_d_mcg": 5.5,
            },
        )

        assert nutrition.additional_info["serving_size"] == 100
        assert nutrition.additional_info["vitamin_d_mcg"] == 5.5


class TestNutritionalInfoUpdateSchema:
    """Tests for NutritionalInfoUpdate schema."""

    def test_partial_update(self):
        """Test partial update with only some fields."""
        update = NutritionalInfoUpdate(
            calories=300.0,
        )

        assert update.calories == 300.0
        assert update.protein_g is None

    def test_update_all_fields(self):
        """Test updating all fields."""
        update = NutritionalInfoUpdate(
            calories=350.0,
            protein_g=20.0,
            carbohydrates_g=40.0,
            fat_g=12.0,
            fiber_g=8.0,
            sugar_g=15.0,
            sodium_mg=300.0,
            cholesterol_mg=25.0,
            additional_info={"new": "data"},
        )

        assert update.calories == 350.0
        assert update.protein_g == 20.0
        assert update.additional_info["new"] == "data"

    def test_empty_update(self):
        """Test creating an empty update object."""
        update = NutritionalInfoUpdate()

        assert update.calories is None
        assert update.protein_g is None
        assert update.additional_info is None

    def test_update_single_field(self):
        """Test updating a single field."""
        update = NutritionalInfoUpdate(
            protein_g=25.0,
        )

        assert update.protein_g == 25.0
        assert update.calories is None

    # New test case: Update with negative value (should fail)
    def test_update_negative_calories(self):
        """Test that update with negative calories is rejected."""
        with pytest.raises(ValidationError):
            NutritionalInfoUpdate(
                calories=-100.0,
            )

    # New test case: Update with zero
    def test_update_to_zero(self):
        """Test updating to zero values."""
        update = NutritionalInfoUpdate(
            calories=0,
            protein_g=0,
        )

        assert update.calories == 0
        assert update.protein_g == 0

    # New test case: Update additional info only
    def test_update_additional_info_only(self):
        """Test updating only additional info."""
        update = NutritionalInfoUpdate(
            additional_info={"updated": "value"},
        )

        assert update.additional_info["updated"] == "value"
        assert update.calories is None

    # New test case: Clear additional info
    def test_update_clear_additional_info(self):
        """Test clearing additional info by setting to None."""
        update = NutritionalInfoUpdate(
            additional_info=None,
        )

        assert update.additional_info is None

    # New test case: Update with decimal values
    def test_update_decimal_values(self):
        """Test update with decimal values."""
        update = NutritionalInfoUpdate(
            calories=123.45,
            protein_g=6.789,
        )

        assert update.calories == 123.45
        assert update.protein_g == 6.789


class TestNutritionalInfoResponseSchema:
    """Tests for NutritionalInfoResponse schema."""

    def test_nutritional_info_response_from_dict(self):
        """Test creating response from dictionary."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        nutrition_id = uuid.uuid4()
        recipe_id = uuid.uuid4()

        data = {
            "id": nutrition_id,
            "recipe_id": recipe_id,
            "calories": 250.0,
            "protein_g": 10.0,
            "carbohydrates_g": 30.0,
            "fat_g": 8.0,
            "fiber_g": 5.0,
            "sugar_g": 10.0,
            "sodium_mg": 200.0,
            "cholesterol_mg": 15.0,
            "additional_info": {"vitamins": {"C": "20%"}},
            "created_at": now,
            "updated_at": now,
            "deleted_at": None,
        }

        response = NutritionalInfoResponse(**data)

        assert response.id == nutrition_id
        assert response.recipe_id == recipe_id
        assert response.calories == 250.0
        assert response.additional_info["vitamins"]["C"] == "20%"

    def test_nutritional_info_response_minimal(self):
        """Test response with minimal required fields."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = NutritionalInfoResponse(
            id=uuid.uuid4(),
            recipe_id=uuid.uuid4(),
            calories=None,
            protein_g=None,
            carbohydrates_g=None,
            fat_g=None,
            fiber_g=None,
            sugar_g=None,
            sodium_mg=None,
            cholesterol_mg=None,
            additional_info=None,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert response.calories is None
        assert response.protein_g is None

    # New test case: Response with soft deletion
    def test_nutritional_info_response_soft_deleted(self):
        """Test response for soft-deleted nutritional info."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = NutritionalInfoResponse(
            id=uuid.uuid4(),
            recipe_id=uuid.uuid4(),
            calories=200.0,
            protein_g=10.0,
            carbohydrates_g=25.0,
            fat_g=5.0,
            fiber_g=3.0,
            sugar_g=8.0,
            sodium_mg=150.0,
            cholesterol_mg=10.0,
            additional_info=None,
            created_at=now,
            updated_at=now,
            deleted_at=now,
        )

        assert response.deleted_at is not None
        assert response.deleted_at == now

    # New test case: Response with complete data
    def test_nutritional_info_response_complete(self):
        """Test response with all fields populated."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = NutritionalInfoResponse(
            id=uuid.uuid4(),
            recipe_id=uuid.uuid4(),
            calories=350.0,
            protein_g=25.0,
            carbohydrates_g=45.0,
            fat_g=12.0,
            fiber_g=8.0,
            sugar_g=15.0,
            sodium_mg=450.0,
            cholesterol_mg=30.0,
            additional_info={
                "vitamins": {"A": "15%", "C": "30%", "D": "10%"},
                "minerals": {"calcium": "20%", "iron": "15%"},
            },
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert response.calories == 350.0
        assert response.protein_g == 25.0
        assert len(response.additional_info["vitamins"]) == 3
        assert response.created_at == now

    # New test case: Response with zero values
    def test_nutritional_info_response_zero_values(self):
        """Test response with zero nutritional values."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = NutritionalInfoResponse(
            id=uuid.uuid4(),
            recipe_id=uuid.uuid4(),
            calories=0,
            protein_g=0,
            carbohydrates_g=0,
            fat_g=0,
            fiber_g=0,
            sugar_g=0,
            sodium_mg=0,
            cholesterol_mg=0,
            additional_info=None,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert response.calories == 0
        assert response.sodium_mg == 0

    # New test case: Response with unicode in additional info
    def test_nutritional_info_response_unicode(self):
        """Test response with unicode in additional info."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = NutritionalInfoResponse(
            id=uuid.uuid4(),
            recipe_id=uuid.uuid4(),
            calories=200.0,
            protein_g=10.0,
            carbohydrates_g=25.0,
            fat_g=8.0,
            fiber_g=4.0,
            sugar_g=12.0,
            sodium_mg=300.0,
            cholesterol_mg=20.0,
            additional_info={
                "description": "Información nutricional completa",
                "notes": "健康に良い",
            },
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert "Información" in response.additional_info["description"]
        assert "健康に良い" == response.additional_info["notes"]

    # New test case: Response with partial data
    def test_nutritional_info_response_partial(self):
        """Test response with only some nutritional fields populated."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = NutritionalInfoResponse(
            id=uuid.uuid4(),
            recipe_id=uuid.uuid4(),
            calories=180.0,
            protein_g=8.0,
            carbohydrates_g=None,
            fat_g=None,
            fiber_g=None,
            sugar_g=None,
            sodium_mg=250.0,
            cholesterol_mg=None,
            additional_info=None,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert response.calories == 180.0
        assert response.protein_g == 8.0
        assert response.carbohydrates_g is None
        assert response.fat_g is None
