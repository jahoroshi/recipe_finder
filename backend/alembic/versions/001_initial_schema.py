"""Initial schema creation

Revision ID: 001
Revises:
Create Date: 2025-11-09 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all initial tables and relationships."""

    # Create enum for difficulty level using raw SQL
    op.execute("CREATE TYPE difficulty_level AS ENUM ('easy', 'medium', 'hard')")

    # Create categories table (must come first due to self-reference)
    op.create_table(
        'categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(100), nullable=False, unique=True),
        sa.Column('slug', sa.String(100), nullable=False, unique=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('parent_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug'),
        comment='Recipe categories with hierarchical structure'
    )

    # Create recipes table
    op.create_table(
        'recipes',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('instructions', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('prep_time', sa.Integer(), nullable=True),
        sa.Column('cook_time', sa.Integer(), nullable=True),
        sa.Column('servings', sa.Integer(), nullable=True),
        sa.Column('difficulty', postgresql.ENUM('easy', 'medium', 'hard', name='difficulty_level', create_type=False), nullable=False, server_default='medium'),
        sa.Column('cuisine_type', sa.String(100), nullable=True),
        sa.Column('diet_types', postgresql.ARRAY(sa.String()), nullable=False, server_default='{}'),
        sa.Column('embedding', postgresql.ARRAY(sa.Float()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint('prep_time >= 0', name='check_prep_time_positive'),
        sa.CheckConstraint('cook_time >= 0', name='check_cook_time_positive'),
        sa.CheckConstraint('servings > 0', name='check_servings_positive'),
        sa.PrimaryKeyConstraint('id'),
        comment='Recipes with cooking instructions and metadata'
    )

    # Create ingredients table
    op.create_table(
        'ingredients',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=True),
        sa.Column('unit', sa.String(50), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint('quantity >= 0', name='check_quantity_positive'),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='Recipe ingredients with quantities and units'
    )

    # Create recipe_categories junction table
    op.create_table(
        'recipe_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recipe_id', 'category_id', name='uq_recipe_category'),
        comment='Many-to-many relationship between recipes and categories'
    )

    # Create nutritional_info table
    op.create_table(
        'nutritional_info',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column('recipe_id', postgresql.UUID(as_uuid=True), nullable=False, unique=True),
        sa.Column('calories', sa.Float(), nullable=True),
        sa.Column('protein_g', sa.Float(), nullable=True),
        sa.Column('carbohydrates_g', sa.Float(), nullable=True),
        sa.Column('fat_g', sa.Float(), nullable=True),
        sa.Column('fiber_g', sa.Float(), nullable=True),
        sa.Column('sugar_g', sa.Float(), nullable=True),
        sa.Column('sodium_mg', sa.Float(), nullable=True),
        sa.Column('cholesterol_mg', sa.Float(), nullable=True),
        sa.Column('additional_info', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint('calories >= 0', name='check_calories_positive'),
        sa.CheckConstraint('protein_g >= 0', name='check_protein_positive'),
        sa.CheckConstraint('carbohydrates_g >= 0', name='check_carbohydrates_positive'),
        sa.CheckConstraint('fat_g >= 0', name='check_fat_positive'),
        sa.CheckConstraint('fiber_g >= 0', name='check_fiber_positive'),
        sa.CheckConstraint('sugar_g >= 0', name='check_sugar_positive'),
        sa.CheckConstraint('sodium_mg >= 0', name='check_sodium_positive'),
        sa.CheckConstraint('cholesterol_mg >= 0', name='check_cholesterol_positive'),
        sa.ForeignKeyConstraint(['recipe_id'], ['recipes.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('recipe_id'),
        comment='Nutritional information for recipes'
    )


def downgrade() -> None:
    """Drop all tables in reverse order."""
    op.drop_table('nutritional_info')
    op.drop_table('recipe_categories')
    op.drop_table('ingredients')
    op.drop_table('recipes')
    op.drop_table('categories')

    # Drop enum type
    op.execute('DROP TYPE IF EXISTS difficulty_level')
