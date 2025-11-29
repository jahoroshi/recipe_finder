"""Repository layer for database operations.

This package implements the repository pattern for clean separation of
data access logic from business logic.

Components:
    - BaseRepository: Generic CRUD operations with soft delete support
    - RecipeRepository: Specialized recipe queries and operations
    - VectorRepository: pgvector semantic search operations
    - Pagination: Pagination utilities for list queries
"""

from app.repositories.base import BaseRepository
from app.repositories.pagination import Pagination
from app.repositories.recipe import RecipeRepository
from app.repositories.vector import VectorRepository

__all__ = [
    "BaseRepository",
    "RecipeRepository",
    "VectorRepository",
    "Pagination",
]
