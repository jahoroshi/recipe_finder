"""Tests for Category Pydantic schemas."""

import uuid

import pytest
from pydantic import ValidationError

from app.schemas.category import (
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
)


class TestCategoryCreateSchema:
    """Tests for CategoryCreate schema."""

    def test_valid_category_create(self):
        """Test creating a valid category."""
        category = CategoryCreate(
            name="Desserts",
            slug="desserts",
            description="Sweet treats and baked goods",
        )

        assert category.name == "Desserts"
        assert category.slug == "desserts"
        assert category.description == "Sweet treats and baked goods"

    def test_category_name_required(self):
        """Test that category name is required."""
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="",
                slug="test",
            )

    def test_category_slug_required(self):
        """Test that category slug is required."""
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Test",
                slug="",
            )

    def test_category_name_whitespace_trimming(self):
        """Test that category name whitespace is trimmed."""
        category = CategoryCreate(
            name="  Desserts  ",
            slug="desserts",
        )

        assert category.name == "Desserts"

    def test_category_slug_lowercase_conversion(self):
        """Test that slug is converted to lowercase."""
        category = CategoryCreate(
            name="Desserts",
            slug="DESSERTS",
        )

        assert category.slug == "desserts"

    def test_category_slug_with_hyphens(self):
        """Test slug with hyphens."""
        category = CategoryCreate(
            name="Main Dishes",
            slug="main-dishes",
        )

        assert category.slug == "main-dishes"

    def test_category_slug_alphanumeric(self):
        """Test slug with alphanumeric characters."""
        category = CategoryCreate(
            name="Appetizers 123",
            slug="appetizers-123",
        )

        assert category.slug == "appetizers-123"

    def test_category_slug_invalid_characters(self):
        """Test that slug with invalid characters is rejected."""
        with pytest.raises(ValidationError) as exc_info:
            CategoryCreate(
                name="Test",
                slug="test_category",  # Underscore not allowed
            )

        errors = exc_info.value.errors()
        assert any("slug" in str(error).lower() for error in errors)

    def test_category_slug_with_spaces(self):
        """Test that slug with spaces is rejected."""
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Test",
                slug="test category",
            )

    def test_category_slug_special_chars(self):
        """Test that slug with special characters is rejected."""
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Test",
                slug="test@category",
            )

    def test_category_without_description(self):
        """Test category without description (optional)."""
        category = CategoryCreate(
            name="Desserts",
            slug="desserts",
            description=None,
        )

        assert category.description is None

    def test_category_with_parent_id(self):
        """Test category with parent ID."""
        parent_id = uuid.uuid4()
        category = CategoryCreate(
            name="Cakes",
            slug="cakes",
            parent_id=parent_id,
        )

        assert category.parent_id == parent_id

    def test_category_without_parent_id(self):
        """Test category without parent ID (root category)."""
        category = CategoryCreate(
            name="Main Category",
            slug="main-category",
            parent_id=None,
        )

        assert category.parent_id is None

    # New test case: Unicode in name
    def test_category_unicode_name(self):
        """Test category with unicode characters in name."""
        category = CategoryCreate(
            name="Französisch",
            slug="franzosisch",
        )

        assert category.name == "Französisch"

    # New test case: Emoji in name
    def test_category_emoji_name(self):
        """Test category with emoji in name."""
        category = CategoryCreate(
            name="Desserts 🍰",
            slug="desserts",
        )

        assert "🍰" in category.name

    # New test case: Name max length
    def test_category_name_max_length(self):
        """Test category name at maximum length."""
        long_name = "A" * 100
        category = CategoryCreate(
            name=long_name,
            slug="test",
        )

        assert len(category.name) == 100

    # New test case: Name exceeds max length
    def test_category_name_exceeds_max_length(self):
        """Test that name exceeding max length is rejected."""
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="A" * 101,
                slug="test",
            )

    # New test case: Slug max length
    def test_category_slug_max_length(self):
        """Test slug at maximum length."""
        long_slug = "a" * 100
        category = CategoryCreate(
            name="Test",
            slug=long_slug,
        )

        assert len(category.slug) == 100

    # New test case: Slug exceeds max length
    def test_category_slug_exceeds_max_length(self):
        """Test that slug exceeding max length is rejected."""
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Test",
                slug="a" * 101,
            )

    # New test case: Long description
    def test_category_long_description(self):
        """Test category with very long description."""
        long_desc = "A" * 1000
        category = CategoryCreate(
            name="Test",
            slug="test",
            description=long_desc,
        )

        assert len(category.description) == 1000

    # New test case: Description with special characters
    def test_category_description_special_chars(self):
        """Test category description with special characters."""
        category = CategoryCreate(
            name="Test",
            slug="test",
            description="Category with symbols: @#$%^&*()_+-=[]{}|;:',.<>?/~`",
        )

        assert "@#$%" in category.description

    # New test case: Slug with numbers only
    def test_category_slug_numbers_only(self):
        """Test slug with only numbers."""
        category = CategoryCreate(
            name="Test",
            slug="12345",
        )

        assert category.slug == "12345"

    # New test case: Slug with mixed case gets lowercased
    def test_category_slug_mixed_case(self):
        """Test that mixed case slug is converted to lowercase."""
        category = CategoryCreate(
            name="Test",
            slug="MiXeD-CaSe",
        )

        assert category.slug == "mixed-case"

    # New test case: Multiple hyphens in slug
    def test_category_slug_multiple_hyphens(self):
        """Test slug with multiple consecutive hyphens."""
        category = CategoryCreate(
            name="Test",
            slug="test--category",
        )

        assert category.slug == "test--category"

    # New test case: Slug starting with hyphen
    def test_category_slug_start_hyphen(self):
        """Test slug starting with hyphen."""
        category = CategoryCreate(
            name="Test",
            slug="-test",
        )

        assert category.slug == "-test"

    # New test case: Slug ending with hyphen
    def test_category_slug_end_hyphen(self):
        """Test slug ending with hyphen."""
        category = CategoryCreate(
            name="Test",
            slug="test-",
        )

        assert category.slug == "test-"

    # New test case: Empty string in description
    def test_category_empty_description(self):
        """Test category with empty string description."""
        category = CategoryCreate(
            name="Test",
            slug="test",
            description="",
        )

        assert category.description == ""

    # New test case: Whitespace only name (should fail)
    def test_category_whitespace_only_name(self):
        """Test that whitespace-only name is rejected."""
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="   ",
                slug="test",
            )

    # New test case: Whitespace only slug (should fail)
    def test_category_whitespace_only_slug(self):
        """Test that whitespace-only slug is rejected."""
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Test",
                slug="   ",
            )

    # New test case: Slug with dots (should fail)
    def test_category_slug_with_dots(self):
        """Test that slug with dots is rejected."""
        with pytest.raises(ValidationError):
            CategoryCreate(
                name="Test",
                slug="test.category",
            )

    # New test case: Unicode in description
    def test_category_unicode_description(self):
        """Test category with unicode in description."""
        category = CategoryCreate(
            name="Test",
            slug="test",
            description="Описание на русском языке",
        )

        assert "русском" in category.description


class TestCategoryUpdateSchema:
    """Tests for CategoryUpdate schema."""

    def test_partial_update(self):
        """Test partial update with only some fields."""
        update = CategoryUpdate(
            name="Updated Name",
        )

        assert update.name == "Updated Name"
        assert update.slug is None
        assert update.description is None

    def test_update_all_fields(self):
        """Test updating all fields."""
        parent_id = uuid.uuid4()
        update = CategoryUpdate(
            name="New Category",
            slug="new-category",
            description="New description",
            parent_id=parent_id,
        )

        assert update.name == "New Category"
        assert update.slug == "new-category"
        assert update.description == "New description"
        assert update.parent_id == parent_id

    def test_empty_update(self):
        """Test creating an empty update object."""
        update = CategoryUpdate()

        assert update.name is None
        assert update.slug is None
        assert update.description is None
        assert update.parent_id is None

    def test_update_name_only(self):
        """Test updating only name."""
        update = CategoryUpdate(
            name="New Name",
        )

        assert update.name == "New Name"
        assert update.slug is None

    def test_update_slug_only(self):
        """Test updating only slug."""
        update = CategoryUpdate(
            slug="new-slug",
        )

        assert update.slug == "new-slug"
        assert update.name is None

    def test_update_description_only(self):
        """Test updating only description."""
        update = CategoryUpdate(
            description="New description",
        )

        assert update.description == "New description"

    # New test case: Update with empty name (should fail)
    def test_update_empty_name(self):
        """Test that update with empty name is rejected."""
        with pytest.raises(ValidationError):
            CategoryUpdate(
                name="",
            )

    # New test case: Update with empty slug (should fail)
    def test_update_empty_slug(self):
        """Test that update with empty slug is rejected."""
        with pytest.raises(ValidationError):
            CategoryUpdate(
                slug="",
            )

    # New test case: Update with invalid slug (Note: Update schema doesn't validate slug format)
    def test_update_slug_with_underscore(self):
        """Test that update accepts slug as-is without validation."""
        # Note: Update schema doesn't apply the same validators as Create
        update = CategoryUpdate(
            slug="invalid_slug",
        )

        # Update schema accepts the value without validation
        assert update.slug == "invalid_slug"

    # New test case: Update parent_id to None (removing parent)
    def test_update_remove_parent(self):
        """Test updating parent_id to None."""
        update = CategoryUpdate(
            parent_id=None,
        )

        assert update.parent_id is None

    # New test case: Update with unicode
    def test_update_unicode_name(self):
        """Test update with unicode in name."""
        update = CategoryUpdate(
            name="Café",
        )

        assert update.name == "Café"

    # New test case: Update slug with uppercase (Note: Update schema doesn't lowercase)
    def test_update_slug_uppercase(self):
        """Test that update accepts slug as-is without conversion."""
        # Note: Update schema doesn't apply the same validators as Create
        update = CategoryUpdate(
            slug="UPPERCASE",
        )

        # Update schema accepts the value as-is
        assert update.slug == "UPPERCASE"


class TestCategoryResponseSchema:
    """Tests for CategoryResponse schema."""

    def test_category_response_from_dict(self):
        """Test creating response from dictionary."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        category_id = uuid.uuid4()

        data = {
            "id": category_id,
            "name": "Desserts",
            "slug": "desserts",
            "description": "Sweet treats",
            "parent_id": None,
            "children": [],
            "created_at": now,
            "updated_at": now,
            "deleted_at": None,
        }

        response = CategoryResponse(**data)

        assert response.id == category_id
        assert response.name == "Desserts"
        assert response.slug == "desserts"
        assert len(response.children) == 0

    def test_category_response_minimal(self):
        """Test response with minimal required fields."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = CategoryResponse(
            id=uuid.uuid4(),
            name="Test",
            slug="test",
            description=None,
            parent_id=None,
            children=[],
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert response.name == "Test"
        assert response.description is None

    def test_category_response_with_parent(self):
        """Test response with parent ID."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        parent_id = uuid.uuid4()

        response = CategoryResponse(
            id=uuid.uuid4(),
            name="Cakes",
            slug="cakes",
            description="Baked cakes",
            parent_id=parent_id,
            children=[],
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert response.parent_id == parent_id

    def test_category_response_with_children(self):
        """Test response with child categories."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        child1 = CategoryResponse(
            id=uuid.uuid4(),
            name="Chocolate Cakes",
            slug="chocolate-cakes",
            description=None,
            parent_id=uuid.uuid4(),
            children=[],
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        child2 = CategoryResponse(
            id=uuid.uuid4(),
            name="Vanilla Cakes",
            slug="vanilla-cakes",
            description=None,
            parent_id=uuid.uuid4(),
            children=[],
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        parent = CategoryResponse(
            id=uuid.uuid4(),
            name="Cakes",
            slug="cakes",
            description="All cakes",
            parent_id=None,
            children=[child1, child2],
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert len(parent.children) == 2
        assert parent.children[0].name == "Chocolate Cakes"
        assert parent.children[1].name == "Vanilla Cakes"

    # New test case: Response with nested children (recursive)
    def test_category_response_nested_children(self):
        """Test response with nested child categories."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        grandchild = CategoryResponse(
            id=uuid.uuid4(),
            name="Dark Chocolate Cakes",
            slug="dark-chocolate-cakes",
            description=None,
            parent_id=uuid.uuid4(),
            children=[],
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        child = CategoryResponse(
            id=uuid.uuid4(),
            name="Chocolate Cakes",
            slug="chocolate-cakes",
            description=None,
            parent_id=uuid.uuid4(),
            children=[grandchild],
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        parent = CategoryResponse(
            id=uuid.uuid4(),
            name="Cakes",
            slug="cakes",
            description=None,
            parent_id=None,
            children=[child],
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert len(parent.children) == 1
        assert len(parent.children[0].children) == 1
        assert parent.children[0].children[0].name == "Dark Chocolate Cakes"

    # New test case: Response with soft deletion
    def test_category_response_soft_deleted(self):
        """Test response for soft-deleted category."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = CategoryResponse(
            id=uuid.uuid4(),
            name="Deleted Category",
            slug="deleted-category",
            description=None,
            parent_id=None,
            children=[],
            created_at=now,
            updated_at=now,
            deleted_at=now,
        )

        assert response.deleted_at is not None

    # New test case: Response with unicode
    def test_category_response_unicode(self):
        """Test response with unicode characters."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = CategoryResponse(
            id=uuid.uuid4(),
            name="日本料理",
            slug="japanese-cuisine",
            description="Traditional Japanese food",
            parent_id=None,
            children=[],
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert response.name == "日本料理"

    # New test case: Response with empty children list
    def test_category_response_empty_children(self):
        """Test response with explicitly empty children list."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)

        response = CategoryResponse(
            id=uuid.uuid4(),
            name="Leaf Category",
            slug="leaf-category",
            description="Category with no children",
            parent_id=None,
            children=[],
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert response.children == []
        assert len(response.children) == 0

    # New test case: Response with many children
    def test_category_response_many_children(self):
        """Test response with many child categories."""
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        parent_id = uuid.uuid4()

        children = [
            CategoryResponse(
                id=uuid.uuid4(),
                name=f"Child {i}",
                slug=f"child-{i}",
                description=None,
                parent_id=parent_id,
                children=[],
                created_at=now,
                updated_at=now,
                deleted_at=None,
            )
            for i in range(20)
        ]

        parent = CategoryResponse(
            id=parent_id,
            name="Parent Category",
            slug="parent-category",
            description=None,
            parent_id=None,
            children=children,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )

        assert len(parent.children) == 20
        assert parent.children[0].name == "Child 0"
        assert parent.children[19].name == "Child 19"
