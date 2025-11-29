"""Tests for pagination utility."""

import pytest
from pydantic import ValidationError

from app.repositories.pagination import Pagination


class TestPagination:
    """Test pagination class functionality."""

    def test_default_values(self):
        """Test pagination default values."""
        pagination = Pagination()
        assert pagination.offset == 0
        assert pagination.limit == 50

    def test_custom_values(self):
        """Test pagination with custom values."""
        pagination = Pagination(offset=10, limit=20)
        assert pagination.offset == 10
        assert pagination.limit == 20

    def test_negative_offset_raises_error(self):
        """Test that negative offset raises validation error."""
        with pytest.raises(ValidationError):
            Pagination(offset=-1)

    def test_zero_limit_raises_error(self):
        """Test that zero limit raises validation error."""
        with pytest.raises(ValidationError):
            Pagination(limit=0)

    def test_limit_exceeds_max_raises_error(self):
        """Test that limit exceeding 100 raises validation error."""
        with pytest.raises(ValidationError):
            Pagination(limit=101)

    def test_limit_at_max_allowed(self):
        """Test that limit of exactly 100 is allowed."""
        pagination = Pagination(limit=100)
        assert pagination.limit == 100

    def test_page_number_calculation(self):
        """Test page number calculation."""
        # First page
        assert Pagination(offset=0, limit=10).page_number == 1

        # Second page
        assert Pagination(offset=10, limit=10).page_number == 2

        # Third page
        assert Pagination(offset=20, limit=10).page_number == 3

    def test_next_offset(self):
        """Test next offset calculation."""
        pagination = Pagination(offset=0, limit=10)
        assert pagination.next_offset() == 10

        pagination = Pagination(offset=10, limit=20)
        assert pagination.next_offset() == 30

    def test_previous_offset(self):
        """Test previous offset calculation."""
        # Can go back
        pagination = Pagination(offset=20, limit=10)
        assert pagination.previous_offset() == 10

        # First page, stays at 0
        pagination = Pagination(offset=0, limit=10)
        assert pagination.previous_offset() == 0

        # Partial page, goes to 0
        pagination = Pagination(offset=5, limit=10)
        assert pagination.previous_offset() == 0

    def test_immutability(self):
        """Test that pagination is immutable (frozen)."""
        pagination = Pagination(offset=10, limit=20)

        with pytest.raises(ValidationError):
            pagination.offset = 20  # Should raise error due to frozen=True

    def test_edge_case_large_offset(self):
        """Test pagination with large offset."""
        pagination = Pagination(offset=10000, limit=50)
        assert pagination.offset == 10000
        assert pagination.page_number == 201

    def test_edge_case_minimum_limit(self):
        """Test pagination with minimum limit."""
        pagination = Pagination(offset=0, limit=1)
        assert pagination.limit == 1
        assert pagination.next_offset() == 1
