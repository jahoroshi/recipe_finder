"""Main API router combining all endpoint routers."""

from fastapi import APIRouter

from app.api.endpoints import recipes, search

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(recipes.router)
api_router.include_router(search.router)
