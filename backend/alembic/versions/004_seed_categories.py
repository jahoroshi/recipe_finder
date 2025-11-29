"""Seed initial categories

Revision ID: 004
Revises: 003
Create Date: 2025-11-09 00:00:03.000000

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Seed initial category data."""

    # Create a temporary connection for bulk insert
    conn = op.get_bind()

    # Define category data: (id, name, slug, description, parent_id)
    categories_data = [
        # Top-level categories
        (uuid.uuid4(), 'Breakfast', 'breakfast', 'Morning meal recipes', None),
        (uuid.uuid4(), 'Lunch', 'lunch', 'Midday meal recipes', None),
        (uuid.uuid4(), 'Dinner', 'dinner', 'Evening meal recipes', None),
        (uuid.uuid4(), 'Desserts', 'desserts', 'Sweet treats and desserts', None),
        (uuid.uuid4(), 'Appetizers', 'appetizers', 'Starters and small plates', None),
        (uuid.uuid4(), 'Beverages', 'beverages', 'Drinks and cocktails', None),
        (uuid.uuid4(), 'Snacks', 'snacks', 'Quick bites and snacks', None),
        (uuid.uuid4(), 'Salads', 'salads', 'Fresh salads and bowls', None),
        (uuid.uuid4(), 'Soups', 'soups', 'Hot and cold soups', None),
        (uuid.uuid4(), 'Main Courses', 'main-courses', 'Primary dishes', None),
        (uuid.uuid4(), 'Side Dishes', 'side-dishes', 'Accompaniments', None),
        (uuid.uuid4(), 'Baking', 'baking', 'Baked goods', None),
    ]

    # Store IDs for parent references
    category_map = {cat[1]: cat[0] for cat in categories_data}

    # Add some child categories
    child_categories = [
        # Breakfast subcategories
        (uuid.uuid4(), 'Pancakes & Waffles', 'pancakes-waffles', 'Fluffy breakfast favorites', category_map['Breakfast']),
        (uuid.uuid4(), 'Eggs', 'eggs', 'Egg-based breakfast dishes', category_map['Breakfast']),
        (uuid.uuid4(), 'Smoothies', 'smoothies', 'Blended breakfast drinks', category_map['Breakfast']),

        # Desserts subcategories
        (uuid.uuid4(), 'Cakes', 'cakes', 'Layer cakes and sheet cakes', category_map['Desserts']),
        (uuid.uuid4(), 'Cookies', 'cookies', 'Baked cookies and bars', category_map['Desserts']),
        (uuid.uuid4(), 'Ice Cream', 'ice-cream', 'Frozen desserts', category_map['Desserts']),
        (uuid.uuid4(), 'Pies', 'pies', 'Sweet and savory pies', category_map['Desserts']),

        # Main Courses subcategories
        (uuid.uuid4(), 'Pasta', 'pasta', 'Pasta dishes', category_map['Main Courses']),
        (uuid.uuid4(), 'Chicken', 'chicken', 'Chicken recipes', category_map['Main Courses']),
        (uuid.uuid4(), 'Beef', 'beef', 'Beef recipes', category_map['Main Courses']),
        (uuid.uuid4(), 'Seafood', 'seafood', 'Fish and seafood', category_map['Main Courses']),
        (uuid.uuid4(), 'Vegetarian', 'vegetarian', 'Meatless main dishes', category_map['Main Courses']),

        # Baking subcategories
        (uuid.uuid4(), 'Breads', 'breads', 'Homemade breads', category_map['Baking']),
        (uuid.uuid4(), 'Muffins', 'muffins', 'Muffins and quick breads', category_map['Baking']),
        (uuid.uuid4(), 'Pastries', 'pastries', 'Flaky pastries', category_map['Baking']),
    ]

    # Combine all categories
    all_categories = categories_data + child_categories

    # Get current timestamp
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc)

    # Prepare bulk insert data
    categories_insert = [
        {
            'id': str(cat[0]),
            'name': cat[1],
            'slug': cat[2],
            'description': cat[3],
            'parent_id': str(cat[4]) if cat[4] is not None else None,
            'created_at': now,
            'updated_at': now,
        }
        for cat in all_categories
    ]

    # Bulk insert
    op.bulk_insert(
        sa.table(
            'categories',
            sa.column('id', postgresql.UUID),
            sa.column('name', sa.String),
            sa.column('slug', sa.String),
            sa.column('description', sa.Text),
            sa.column('parent_id', postgresql.UUID),
            sa.column('created_at', sa.DateTime),
            sa.column('updated_at', sa.DateTime),
        ),
        categories_insert
    )


def downgrade() -> None:
    """Remove seeded categories."""

    # Delete all categories (cascades will handle relationships)
    op.execute("DELETE FROM categories WHERE TRUE")
