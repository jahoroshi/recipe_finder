"""Add pgvector extension and convert embedding column

Revision ID: 002
Revises: 001
Create Date: 2025-11-09 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Install pgvector extension and convert embedding column to vector type."""

    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')

    # Convert the embedding column from ARRAY to vector(768)
    # First drop the existing column
    op.drop_column('recipes', 'embedding')

    # Then add it back with the vector type
    op.execute("""
        ALTER TABLE recipes
        ADD COLUMN embedding vector(768)
    """)

    # Add comment
    op.execute("""
        COMMENT ON COLUMN recipes.embedding IS
        'Vector embedding for semantic search (768 dimensions)'
    """)


def downgrade() -> None:
    """Remove pgvector extension and revert embedding column."""

    # Convert back to ARRAY
    op.drop_column('recipes', 'embedding')

    # Add back as ARRAY
    op.execute("""
        ALTER TABLE recipes
        ADD COLUMN embedding float[]
    """)

    # Drop pgvector extension
    op.execute('DROP EXTENSION IF EXISTS vector')
