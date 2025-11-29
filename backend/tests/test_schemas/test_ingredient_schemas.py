"""Tests for Ingredient Pydantic schemas."""

import uuid

import pytest
from pydantic import ValidationError

from app.schemas.ingredient import (
    IngredientCreate,
    IngredientResponse,
    IngredientUpdate,
)


class TestIngredientCreateSchema:
    """Tests for IngredientCreate schema."""

    def test_valid_ingredient_create(self):
        """Test creating a valid ingredient."""
        ingredient = IngredientCreate(
            name="Flour",
            quantity=2.0,
            unit="cups",
            notes="All-purpose flour",
        )

        assert ingredient.name == "Flour"
        assert ingredient.quantity == 2.0
        assert ingredient.unit == "cups"
        assert ingredient.notes == "All-purpose flour"

    def test_ingredient_name_required(self):
        """Test that ingredient name is required."""
        with pytest.raises(ValidationError):
            IngredientCreate(name="")

    def test_ingredient_empty_name(self):
        """Test that empty ingredient name after strip is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            IngredientCreate(name="   ")

        errors = exc_info.value.errors()
        assert any("name" in str(error) for error in errors)

    def test_ingredient_name_whitespace_trimming(self):
        """Test that ingredient name whitespace is trimmed."""
        ingredient = IngredientCreate(
            name="  Sugar  ",
            quantity=1.0,
        )

        assert ingredient.name == "Sugar"

    def test_ingredient_without_quantity(self):
        """Test ingredient without quantity (optional)."""
        ingredient = IngredientCreate(
            name="Salt",
            quantity=None,
        )

        assert ingredient.name == "Salt"
        assert ingredient.quantity is None

    def test_ingredient_without_unit(self):
        """Test ingredient without unit (optional)."""
        ingredient = IngredientCreate(
            name="Eggs",
            quantity=4,
            unit=None,
        )

        assert ingredient.unit is None

    def test_ingredient_negative_quantity(self):
        """Test that negative quantity is not allowed."""
        with pytest.raises(ValidationError):
            IngredientCreate(
                name="Flour",
                quantity=-2.0,
            )

    def test_ingredient_zero_quantity(self):
        """Test that zero quantity is allowed."""
        ingredient = IngredientCreate(
            name="Garnish",
            quantity=0,
        )

        assert ingredient.quantity == 0

    def test_ingredient_decimal_quantity(self):
        """Test ingredient with decimal quantity."""
        ingredient = IngredientCreate(
            name="Butter",
            quantity=0.25,
            unit="cup",
        )

        assert ingredient.quantity == 0.25

    def test_ingredient_large_quantity(self):
        """Test ingredient with very large quantity."""
        ingredient = IngredientCreate(
            name="Water",
            quantity=10000.0,
            unit="ml",
        )

        assert ingredient.quantity == 10000.0

    def test_ingredient_fractional_quantity(self):
        """Test ingredient with fractional quantity."""
        ingredient = IngredientCreate(
            name="Vanilla",
            quantity=0.0001,
            unit="tsp",
        )

        assert ingredient.quantity == 0.0001

    def test_ingredient_unit_whitespace_trimming(self):
        """Test that unit whitespace is trimmed."""
        ingredient = IngredientCreate(
            name="Milk",
            quantity=1,
            unit="  cup  ",
        )

        assert ingredient.unit == "cup"

    def test_ingredient_empty_unit_becomes_none(self):
        """Test that empty unit string becomes None."""
        ingredient = IngredientCreate(
            name="Ingredient",
            quantity=1,
            unit="   ",
        )

        assert ingredient.unit is None

    def test_ingredient_with_notes(self):
        """Test ingredient with notes."""
        ingredient = IngredientCreate(
            name="Tomatoes",
            quantity=3,
            unit="pieces",
            notes="Fresh, ripe tomatoes",
        )

        assert ingredient.notes == "Fresh, ripe tomatoes"

    # New test case: Unicode in ingredient name
    def test_ingredient_unicode_name(self):
        """Test ingredient with unicode characters in name."""
        ingredient = IngredientCreate(
            name="Café au Lait",
            quantity=1,
            unit="cup",
        )

        assert ingredient.name == "Café au Lait"

    # New test case: Special characters in name
    def test_ingredient_special_chars_name(self):
        """Test ingredient with special characters."""
        ingredient = IngredientCreate(
            name="Salt & Pepper Mix",
            quantity=1,
            unit="tsp",
        )

        assert "&" in ingredient.name

    # New test case: Emoji in ingredient name
    def test_ingredient_with_emoji(self):
        """Test ingredient with emoji in name."""
        ingredient = IngredientCreate(
            name="Chili 🌶️",
            quantity=2,
            unit="pieces",
        )

        assert "🌶️" in ingredient.name

    # New test case: Max length name
    def test_ingredient_name_max_length(self):
        """Test ingredient name at maximum length."""
        long_name = "A" * 255
        ingredient = IngredientCreate(
            name=long_name,
            quantity=1,
        )

        assert len(ingredient.name) == 255

    # New test case: Name exceeds max length
    def test_ingredient_name_exceeds_max_length(self):
        """Test that name exceeding max length is rejected."""
        with pytest.raises(ValidationError):
            IngredientCreate(
                name="A" * 256,
                quantity=1,
            )

    # New test case: Unit max length
    def test_ingredient_unit_max_length(self):
        """Test unit at maximum length."""
        long_unit = "A" * 50
        ingredient = IngredientCreate(
            name="Test",
            quantity=1,
            unit=long_unit,
        )

        assert len(ingredient.unit) == 50

    # New test case: Unit exceeds max length
    def test_ingredient_unit_exceeds_max_length(self):
        """Test that unit exceeding max length is rejected."""
        with pytest.raises(ValidationError):
            IngredientCreate(
                name="Test",
                quantity=1,
                unit="A" * 51,
            )

    # New test case: Long notes
    def test_ingredient_long_notes(self):
        """Test ingredient with very long notes."""
        long_notes = "A" * 1000
        ingredient = IngredientCreate(
            name="Test",
            quantity=1,
            notes=long_notes,
        )

        assert len(ingredient.notes) == 1000

    # New test case: Various common units
    def test_ingredient_common_units(self):
        """Test ingredient with various common units."""
        units = ["g", "kg", "ml", "L", "cup", "tbsp", "tsp", "oz", "lb", "piece", "pinch"]

        for unit in units:
            ingredient = IngredientCreate(
                name="Test",
                quantity=1,
                unit=unit,
            )
            assert ingredient.unit == unit

    # New test case: Integer quantity
    def test_ingredient_integer_quantity(self):
        """Test ingredient with integer quantity."""
        ingredient = IngredientCreate(
            name="Eggs",
            quantity=12,
        )

        assert ingredient.quantity == 12
        assert isinstance(ingredient.quantity, (int, float))

    # New test case: Notes with special characters
    def test_ingredient_notes_special_chars(self):
        """Test ingredient notes with special characters."""
        ingredient = IngredientCreate(
            name="Test",
            quantity=1,
            notes="Use organic! (if available) @home, cost: $5-10",
        )

        assert "@" in ingredient.notes
        assert "$" in ingredient.notes


class TestIngredientUpdateSchema:
    """Tests for IngredientUpdate schema."""

    def test_partial_update(self):
        """Test partial update with only some fields."""
        update = IngredientUpdate(
            name="Updated Name",
        )

        assert update.name == "Updated Name"
        assert update.quantity is None
        assert update.unit is None

    def test_update_all_fields(self):
        """Test updating all fields."""
        update = IngredientUpdate(
            name="New Ingredient",
            quantity=5.0,
            unit="grams",
            notes="Updated notes",
        )

        assert update.name == "New Ingredient"
        assert update.quantity == 5.0
        assert update.unit == "grams"
        assert update.notes == "Updated notes"

    def test_empty_update(self):
        """Test creating an empty update object."""
        update = IngredientUpdate()

        assert update.name is None
        assert update.quantity is None
        assert update.unit is None
        assert update.notes is None

    def test_update_quantity_only(self):
        """Test updating only quantity."""
        update = IngredientUpdate(
            quantity=3.5,
        )

        assert update.quantity == 3.5
        assert update.name is None

    def test_update_unit_only(self):
        """Test updating only unit."""
        update = IngredientUpdate(
            unit="ml",
        )

        assert update.unit == "ml"
        assert update.quantity is None

    # New test case: Update with negative quantity (should fail)
    def test_update_negative_quantity(self):
        """Test that update with negative quantity is rejected."""
        with pytest.raises(ValidationError):
            IngredientUpdate(
                quantity=-5.0,
            )

    # New test case: Update with empty name (should fail)
    def test_update_empty_name(self):
        """Test that update with empty name is rejected."""
        with pytest.raises(ValidationError):
            IngredientUpdate(
                name="",
            )

    # New test case: Update with zero quantity
    def test_update_zero_quantity(self):
        """Test update with zero quantity."""
        update = IngredientUpdate(
            quantity=0,
        )

        assert update.quantity == 0

    # New test case: Update notes to None
    def test_update_notes_to_none(self):
        """Test updating notes to None (clearing notes)."""
        update = IngredientUpdate(
            notes=None,
        )

        assert update.notes is None

    # New test case: Update with unicode
    def test_update_unicode_name(self):
        """Test update with unicode in name."""
        update = IngredientUpdate(
            name="Açúcar",
        )

        assert update.name == "Açúcar"


class TestIngredientResponseSchema:
    """Tests for IngredientResponse schema."""

    def test_ingredient_response_from_dict(self):
        """Test creating response from dictionary."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        ingredient_id = uuid.uuid4()
        recipe_id = uuid.uuid4()

        data = {
            "id": ingredient_id,
            "recipe_id": recipe_id,
            "name": "Flour",
            "quantity": 2.0,
            "unit": "cups",
            "notes": "All-purpose",
            "created_at": now,
            "updated_at": now,
            "deleted_at": None,
        }

        response = IngredientResponse(**data)

        assert response.id == ingredient_id
        assert response.recipe_id == recipe_id
        assert response.name == "Flour"
        assert response.quantity == 2.0

    def test_ingredient_response_minimal(self):
        """Test response with minimal required fields."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = IngredientResponse(
            id=uuid.uuid4(),
            recipe_id=uuid.uuid4(),
            name="Salt",
            quantity=None,
            unit=None,
            notes=None,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert response.name == "Salt"
        assert response.quantity is None
        assert response.unit is None

    # New test case: Response with deleted_at
    def test_ingredient_response_soft_deleted(self):
        """Test response for soft-deleted ingredient."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = IngredientResponse(
            id=uuid.uuid4(),
            recipe_id=uuid.uuid4(),
            name="Deleted Ingredient",
            quantity=1.0,
            unit="cup",
            notes=None,
            created_at=now,
            updated_at=now,
            deleted_at=now,
        )

        assert response.deleted_at is not None
        assert response.deleted_at == now

    # New test case: Response with all fields populated
    def test_ingredient_response_complete(self):
        """Test response with all fields populated."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = IngredientResponse(
            id=uuid.uuid4(),
            recipe_id=uuid.uuid4(),
            name="Premium Olive Oil",
            quantity=0.5,
            unit="cup",
            notes="Extra virgin, cold pressed",
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert response.name == "Premium Olive Oil"
        assert response.quantity == 0.5
        assert response.notes == "Extra virgin, cold pressed"
        assert response.created_at == now
        assert response.updated_at == now

    # New test case: Response with unicode
    def test_ingredient_response_unicode(self):
        """Test response with unicode characters."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = IngredientResponse(
            id=uuid.uuid4(),
            recipe_id=uuid.uuid4(),
            name="Japchae 잡채",
            quantity=200,
            unit="g",
            notes="Korean glass noodles",
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert "잡채" in response.name
        assert response.quantity == 200
