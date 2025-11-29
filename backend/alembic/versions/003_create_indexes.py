"""Create indexes for performance optimization

Revision ID: 003
Revises: 002
Create Date: 2025-11-09 00:00:02.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '003'
down_revision: Union[str, None] = '002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all indexes for optimized querying."""

    # Enable pg_trgm extension for trigram text search
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')

    # ==================== RECIPES TABLE INDEXES ====================

    # B-tree indexes on frequently filtered columns
    op.create_index('ix_recipes_name', 'recipes', ['name'])
    op.create_index('ix_recipes_cuisine_type', 'recipes', ['cuisine_type'])
    op.create_index('ix_recipes_difficulty', 'recipes', ['difficulty'])
    op.create_index('ix_recipes_created_at', 'recipes', ['created_at'])
    op.create_index('ix_recipes_deleted_at', 'recipes', ['deleted_at'])

    # Composite index for common query patterns
    op.create_index(
        'ix_recipes_cuisine_difficulty',
        'recipes',
        ['cuisine_type', 'difficulty']
    )

    # Descending index on created_at for "latest recipes" queries
    op.execute("""
        CREATE INDEX ix_recipes_created_at_desc
        ON recipes (created_at DESC)
    """)

    # GIN index for JSONB instructions field
    op.create_index(
        'ix_recipes_instructions_gin',
        'recipes',
        ['instructions'],
        postgresql_using='gin'
    )

    # GIN index for array diet_types
    op.create_index(
        'ix_recipes_diet_types_gin',
        'recipes',
        ['diet_types'],
        postgresql_using='gin'
    )

    # Trigram GIN index for fuzzy text search on name
    op.execute("""
        CREATE INDEX ix_recipes_name_trgm
        ON recipes USING gin (name gin_trgm_ops)
    """)

    # HNSW index on embedding vector for similarity search
    # Using cosine distance with optimized parameters
    op.execute("""
        CREATE INDEX ix_recipes_embedding_hnsw
        ON recipes USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
    """)

    # ==================== INGREDIENTS TABLE INDEXES ====================

    op.create_index('ix_ingredients_recipe_id', 'ingredients', ['recipe_id'])
    op.create_index('ix_ingredients_name', 'ingredients', ['name'])
    op.create_index('ix_ingredients_deleted_at', 'ingredients', ['deleted_at'])

    # Composite index for recipe + ingredient lookups
    op.create_index(
        'ix_ingredients_recipe_name',
        'ingredients',
        ['recipe_id', 'name']
    )

    # ==================== CATEGORIES TABLE INDEXES ====================

    op.create_index('ix_categories_name', 'categories', ['name'])
    op.create_index('ix_categories_slug', 'categories', ['slug'])
    op.create_index('ix_categories_parent_id', 'categories', ['parent_id'])
    op.create_index('ix_categories_deleted_at', 'categories', ['deleted_at'])

    # ==================== RECIPE_CATEGORIES TABLE INDEXES ====================

    op.create_index('ix_recipe_categories_recipe_id', 'recipe_categories', ['recipe_id'])
    op.create_index('ix_recipe_categories_category_id', 'recipe_categories', ['category_id'])
    op.create_index('ix_recipe_categories_deleted_at', 'recipe_categories', ['deleted_at'])

    # Composite index for junction table queries
    op.create_index(
        'ix_recipe_categories_recipe_category',
        'recipe_categories',
        ['recipe_id', 'category_id']
    )

    # ==================== NUTRITIONAL_INFO TABLE INDEXES ====================

    op.create_index('ix_nutritional_info_recipe_id', 'nutritional_info', ['recipe_id'])
    op.create_index('ix_nutritional_info_deleted_at', 'nutritional_info', ['deleted_at'])

    # GIN index for additional_info JSONB
    op.create_index(
        'ix_nutritional_info_additional_info_gin',
        'nutritional_info',
        ['additional_info'],
        postgresql_using='gin'
    )


def downgrade() -> None:
    """Drop all created indexes."""

    # ==================== NUTRITIONAL_INFO TABLE INDEXES ====================
    op.drop_index('ix_nutritional_info_additional_info_gin', 'nutritional_info')
    op.drop_index('ix_nutritional_info_deleted_at', 'nutritional_info')
    op.drop_index('ix_nutritional_info_recipe_id', 'nutritional_info')

    # ==================== RECIPE_CATEGORIES TABLE INDEXES ====================
    op.drop_index('ix_recipe_categories_recipe_category', 'recipe_categories')
    op.drop_index('ix_recipe_categories_deleted_at', 'recipe_categories')
    op.drop_index('ix_recipe_categories_category_id', 'recipe_categories')
    op.drop_index('ix_recipe_categories_recipe_id', 'recipe_categories')

    # ==================== CATEGORIES TABLE INDEXES ====================
    op.drop_index('ix_categories_deleted_at', 'categories')
    op.drop_index('ix_categories_parent_id', 'categories')
    op.drop_index('ix_categories_slug', 'categories')
    op.drop_index('ix_categories_name', 'categories')

    # ==================== INGREDIENTS TABLE INDEXES ====================
    op.drop_index('ix_ingredients_recipe_name', 'ingredients')
    op.drop_index('ix_ingredients_deleted_at', 'ingredients')
    op.drop_index('ix_ingredients_name', 'ingredients')
    op.drop_index('ix_ingredients_recipe_id', 'ingredients')

    # ==================== RECIPES TABLE INDEXES ====================
    op.execute('DROP INDEX IF EXISTS ix_recipes_embedding_hnsw')
    op.execute('DROP INDEX IF EXISTS ix_recipes_name_trgm')
    op.drop_index('ix_recipes_diet_types_gin', 'recipes')
    op.drop_index('ix_recipes_instructions_gin', 'recipes')
    op.execute('DROP INDEX IF EXISTS ix_recipes_created_at_desc')
    op.drop_index('ix_recipes_cuisine_difficulty', 'recipes')
    op.drop_index('ix_recipes_deleted_at', 'recipes')
    op.drop_index('ix_recipes_created_at', 'recipes')
    op.drop_index('ix_recipes_difficulty', 'recipes')
    op.drop_index('ix_recipes_cuisine_type', 'recipes')
    op.drop_index('ix_recipes_name', 'recipes')

    # Drop extensions (optional, may be used by other tables)
    # op.execute('DROP EXTENSION IF EXISTS pg_trgm')
