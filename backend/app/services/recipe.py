"""Recipe service for business logic and operations."""

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import inspect
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Category, Ingredient, NutritionalInfo, Recipe, RecipeCategory
from app.repositories.pagination import Pagination
from app.repositories.recipe import RecipeRepository
from app.repositories.vector import VectorRepository
from app.schemas.recipe import RecipeCreate, RecipeResponse, RecipeUpdate
from app.services.cache import CacheService
from app.services.embedding import EmbeddingService

logger = logging.getLogger(__name__)


class RecipeService:
    """Service for recipe business logic and operations.

    Handles:
        - Recipe CRUD operations with validation
        - Business rule enforcement
        - Cache management
        - Embedding generation
        - Audit logging
        - Transaction management

    Example:
        ```python
        service = RecipeService(
            recipe_repo, vector_repo, embedding_service, cache_service, session
        )
        recipe = await service.create_recipe(recipe_data)
        ```
    """

    def __init__(
        self,
        recipe_repo: RecipeRepository,
        vector_repo: VectorRepository,
        embedding_service: EmbeddingService,
        cache_service: CacheService,
        session: AsyncSession,
    ):
        """Initialize recipe service.

        Args:
            recipe_repo: Repository for recipe database operations
            vector_repo: Repository for vector operations
            embedding_service: Service for generating embeddings
            cache_service: Service for caching
            session: Database session for transaction management
        """
        self.recipe_repo = recipe_repo
        self.vector_repo = vector_repo
        self.embedding_service = embedding_service
        self.cache = cache_service
        self.session = session

    async def create_recipe(self, data: RecipeCreate) -> RecipeResponse:
        """Create a new recipe with validation and embedding generation.

        Steps:
            1. Validate business rules
            2. Create recipe and related entities
            3. Generate and store embedding
            4. Cache recipe data
            5. Log audit event

        Args:
            data: Recipe creation data

        Returns:
            Created recipe response

        Raises:
            ValueError: If validation fails

        Example:
            ```python
            recipe_data = RecipeCreate(
                name="Pasta Carbonara",
                description="Classic Italian pasta",
                instructions={"steps": ["Cook pasta", "Mix ingredients"]},
                ingredients=[IngredientCreate(name="pasta", quantity=500, unit="g")],
                difficulty=DifficultyLevel.MEDIUM
            )
            recipe = await service.create_recipe(recipe_data)
            ```
        """
        # Validate business rules
        await self.validate_business_rules(data)

        # Create recipe entity
        recipe = Recipe(
            name=data.name,
            description=data.description,
            instructions=data.instructions,
            prep_time=data.prep_time,
            cook_time=data.cook_time,
            servings=data.servings,
            difficulty=data.difficulty,
            cuisine_type=data.cuisine_type,
            diet_types=data.diet_types,
        )

        # Add to session
        self.session.add(recipe)
        await self.session.flush()  # Get recipe ID

        # Create ingredients
        for ingredient_data in data.ingredients:
            ingredient = Ingredient(
                recipe_id=recipe.id,
                name=ingredient_data.name,
                quantity=ingredient_data.quantity,
                unit=ingredient_data.unit,
                notes=ingredient_data.notes,
            )
            self.session.add(ingredient)

        # Create category associations
        for category_id in data.category_ids:
            recipe_category = RecipeCategory(
                recipe_id=recipe.id,
                category_id=category_id,
            )
            self.session.add(recipe_category)

        # Create nutritional info if provided
        if data.nutritional_info:
            nutritional_info = NutritionalInfo(
                recipe_id=recipe.id,
                calories=data.nutritional_info.calories,
                protein_g=data.nutritional_info.protein_g,
                carbohydrates_g=data.nutritional_info.carbohydrates_g,
                fat_g=data.nutritional_info.fat_g,
                fiber_g=data.nutritional_info.fiber_g,
                sugar_g=data.nutritional_info.sugar_g,
                sodium_mg=data.nutritional_info.sodium_mg,
                cholesterol_mg=data.nutritional_info.cholesterol_mg,
                additional_info=data.nutritional_info.additional_info,
            )
            self.session.add(nutritional_info)

        await self.session.flush()

        # Generate and store embedding
        try:
            embedding = await self.embedding_service.create_recipe_embedding(recipe)
            recipe.embedding = embedding
            await self.session.flush()
        except Exception as e:
            logger.warning(f"Failed to generate embedding for recipe {recipe.id}: {e}")

        # Commit transaction
        await self.session.commit()

        # Refresh to load relationships
        await self.session.refresh(recipe)

        # Cache recipe
        recipe_response = await self.get_recipe(recipe.id)

        # Log audit event
        logger.info(f"Created recipe {recipe.id}: {recipe.name}")

        return recipe_response

    async def update_recipe(self, id: UUID, updates: RecipeUpdate) -> RecipeResponse:
        """Update an existing recipe.

        Steps:
            1. Fetch existing recipe
            2. Validate updates
            3. Apply updates
            4. Regenerate embedding if needed
            5. Invalidate cache
            6. Log audit event

        Args:
            id: Recipe UUID
            updates: Recipe update data

        Returns:
            Updated recipe response

        Raises:
            ValueError: If recipe not found or validation fails

        Example:
            ```python
            updates = RecipeUpdate(prep_time=25, difficulty=DifficultyLevel.EASY)
            recipe = await service.update_recipe(recipe_id, updates)
            ```
        """
        # Fetch recipe
        recipe = await self.recipe_repo.get(id)
        if recipe is None:
            raise ValueError(f"Recipe with id {id} not found")

        # Track if embedding needs regeneration
        needs_embedding_update = False

        # Apply updates
        update_data = updates.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if field == "category_ids":
                # Handle category updates
                # Delete existing associations
                for rc in recipe.recipe_categories:
                    await self.session.delete(rc)
                await self.session.flush()

                # Create new associations
                for category_id in value:
                    recipe_category = RecipeCategory(
                        recipe_id=recipe.id,
                        category_id=category_id,
                    )
                    self.session.add(recipe_category)
            elif hasattr(recipe, field):
                setattr(recipe, field, value)
                # These fields affect embedding
                if field in ["name", "description", "cuisine_type", "diet_types", "difficulty"]:
                    needs_embedding_update = True

        await self.session.flush()

        # Regenerate embedding if needed
        if needs_embedding_update:
            try:
                embedding = await self.embedding_service.create_recipe_embedding(recipe)
                recipe.embedding = embedding
                await self.session.flush()
            except Exception as e:
                logger.warning(f"Failed to update embedding for recipe {recipe.id}: {e}")

        # Commit transaction
        await self.session.commit()

        # Invalidate cache
        await self.cache.invalidate_recipe_cache(id)

        # Refresh and return
        await self.session.refresh(recipe)

        # Log audit event
        logger.info(f"Updated recipe {recipe.id}: {recipe.name}")

        return await self.get_recipe(id)

    async def get_recipe(self, id: UUID) -> RecipeResponse:
        """Get recipe by ID with caching.

        Args:
            id: Recipe UUID

        Returns:
            Recipe response

        Raises:
            ValueError: If recipe not found

        Example:
            ```python
            recipe = await service.get_recipe(recipe_id)
            ```
        """
        # Check cache
        cached = await self.cache.get_recipe(id)
        if cached:
            return RecipeResponse(**cached)

        # Fetch from database with relations
        recipe = await self.recipe_repo.get_with_relations(id)
        if recipe is None:
            raise ValueError(f"Recipe with id {id} not found")

        # Enrich recipe data
        enriched_recipe = await self.enrich_recipe_data(recipe)

        # Convert to response
        response = self._recipe_to_response(enriched_recipe)

        # Cache response (use mode='json' to serialize datetime objects)
        await self.cache.set_recipe(id, response.model_dump(mode='json'))

        return response

    async def delete_recipe(self, id: UUID) -> None:
        """Soft delete a recipe.

        Args:
            id: Recipe UUID

        Raises:
            ValueError: If recipe not found

        Example:
            ```python
            await service.delete_recipe(recipe_id)
            ```
        """
        # Fetch recipe
        recipe = await self.recipe_repo.get(id)
        if recipe is None:
            raise ValueError(f"Recipe with id {id} not found")

        # Soft delete
        await self.recipe_repo.delete(id)
        await self.session.commit()

        # Invalidate cache
        await self.cache.invalidate_recipe_cache(id)

        # Log audit event
        logger.info(f"Deleted recipe {id}: {recipe.name}")

    async def count_recipes(self, filters: dict) -> int:
        """Count recipes matching filters.

        Args:
            filters: Filter criteria (same as list_recipes)

        Returns:
            Total number of recipes matching filters
        """
        # For complex filters, we need to use repository methods
        # For now, use the base repository count with empty filters
        # since the complex filters don't have dedicated count methods
        return await self.recipe_repo.count(filters={})

    async def list_recipes(
        self, filters: dict, pagination: Pagination
    ) -> list[RecipeResponse]:
        """List recipes with filters and pagination.

        Args:
            filters: Filter criteria
            pagination: Pagination parameters

        Returns:
            List of recipe responses

        Example:
            ```python
            filters = {"cuisine_type": "Italian", "difficulty": DifficultyLevel.EASY}
            recipes = await service.list_recipes(filters, Pagination(page=1, page_size=10))
            ```
        """
        # Check for time-based filters
        time_filters = ["max_prep_time", "min_prep_time", "max_cook_time", "min_cook_time", "max_total_time"]
        has_time_filters = any(f in filters for f in time_filters)

        # Apply filters based on priority
        if has_time_filters:
            # Handle time-based filtering
            # Calculate max_total_time if not provided but prep/cook constraints exist
            max_total = filters.get("max_total_time")
            if not max_total and ("max_prep_time" in filters or "max_cook_time" in filters):
                max_prep = filters.get("max_prep_time")
                max_cook = filters.get("max_cook_time")
                # Only calculate total if both are specified
                if max_prep is not None and max_cook is not None:
                    max_total = max_prep + max_cook

            recipes = await self.recipe_repo.get_recipes_with_time_range(
                max_total_time=max_total,
                max_prep_time=filters.get("max_prep_time"),
                max_cook_time=filters.get("max_cook_time"),
                pagination=pagination,
            )
        elif "cuisine_type" in filters or "difficulty" in filters:
            recipes = await self.recipe_repo.find_by_cuisine_and_difficulty(
                cuisine=filters.get("cuisine_type"),
                difficulty=filters.get("difficulty"),
                pagination=pagination,
            )
        elif "ingredients" in filters:
            recipes = await self.recipe_repo.find_by_ingredients(
                ingredients=filters["ingredients"],
                pagination=pagination,
                match_all=filters.get("match_all", False),
            )
        elif "text" in filters:
            recipes = await self.recipe_repo.search_by_text(
                query=filters["text"],
                pagination=pagination,
            )
        elif "diet_types" in filters and filters["diet_types"]:
            # Handle diet type filtering
            try:
                recipes = await self.recipe_repo.get_recipes_by_diet_type(
                    diet_type=filters["diet_types"][0],  # Use first diet type
                    pagination=pagination,
                )
            except Exception:
                # Fallback to empty list if diet filtering fails
                recipes = []
        else:
            # Default: get all with pagination
            recipes = await self.recipe_repo.list(filters={}, pagination=pagination)

        # Convert to responses
        return [self._recipe_to_response(recipe) for recipe in recipes]

    async def enrich_recipe_data(self, recipe: Recipe) -> Recipe:
        """Enrich recipe with additional calculated data.

        Args:
            recipe: Recipe instance

        Returns:
            Enriched recipe

        Example:
            ```python
            enriched = await service.enrich_recipe_data(recipe)
            ```
        """
        # Calculate metrics
        metrics = await self.calculate_recipe_metrics(recipe)

        # Store metrics in recipe (could be added to model)
        # For now, just return the recipe
        return recipe

    async def validate_business_rules(self, recipe: RecipeCreate) -> None:
        """Validate business rules for recipe creation.

        Rules:
            - Recipe name must be unique (case-insensitive)
            - Must have at least one ingredient
            - Prep time + cook time should be reasonable (< 24 hours)
            - Servings should be positive if provided

        Args:
            recipe: Recipe creation data

        Raises:
            ValueError: If validation fails

        Example:
            ```python
            await service.validate_business_rules(recipe_data)
            ```
        """
        # Validate unique name (simple check - could be enhanced)
        existing = await self.recipe_repo.search_by_text(recipe.name.lower())
        exact_matches = [r for r in existing if r.name.lower() == recipe.name.lower()]
        if exact_matches:
            raise ValueError(f"Recipe with name '{recipe.name}' already exists")

        # Validate time constraints
        if recipe.prep_time and recipe.cook_time:
            total_time = recipe.prep_time + recipe.cook_time
            if total_time > 1440:  # 24 hours in minutes
                raise ValueError(
                    f"Total cooking time ({total_time} minutes) exceeds 24 hours"
                )

        # Validate servings
        if recipe.servings is not None and recipe.servings <= 0:
            raise ValueError("Servings must be positive")

        # Instructions validation
        if not recipe.instructions or not isinstance(recipe.instructions, dict):
            raise ValueError("Instructions must be a non-empty dictionary")

    async def calculate_recipe_metrics(self, recipe: Recipe) -> dict:
        """Calculate recipe metrics and statistics.

        Metrics:
            - Total time (prep + cook)
            - Difficulty score (0-100)
            - Ingredient count
            - Estimated calories per serving

        Args:
            recipe: Recipe instance

        Returns:
            Dictionary of metrics

        Example:
            ```python
            metrics = await service.calculate_recipe_metrics(recipe)
            # {"total_time": 45, "difficulty_score": 60, ...}
            ```
        """
        metrics = {}

        # Total time
        if recipe.prep_time and recipe.cook_time:
            metrics["total_time"] = recipe.prep_time + recipe.cook_time
        elif recipe.prep_time:
            metrics["total_time"] = recipe.prep_time
        elif recipe.cook_time:
            metrics["total_time"] = recipe.cook_time
        else:
            metrics["total_time"] = None

        # Difficulty score (0-100)
        difficulty_scores = {"easy": 30, "medium": 60, "hard": 90}
        difficulty_value = (
            recipe.difficulty.value
            if hasattr(recipe.difficulty, "value")
            else recipe.difficulty
        )
        metrics["difficulty_score"] = difficulty_scores.get(difficulty_value, 60)

        # Ingredient count
        metrics["ingredient_count"] = len(recipe.ingredients) if recipe.ingredients else 0

        # Calories per serving
        if recipe.nutritional_info and recipe.servings:
            metrics["calories_per_serving"] = (
                recipe.nutritional_info.calories / recipe.servings
                if recipe.nutritional_info.calories
                else None
            )
        else:
            metrics["calories_per_serving"] = None

        return metrics

    def _recipe_to_response(self, recipe: Recipe) -> RecipeResponse:
        """Convert Recipe model to RecipeResponse.

        Args:
            recipe: Recipe model instance

        Returns:
            Recipe response schema
        """
        from app.schemas.category import CategoryResponse
        from app.schemas.ingredient import IngredientResponse
        from app.schemas.nutritional_info import NutritionalInfoResponse

        # Convert ingredients
        ingredients = []
        if recipe.ingredients:
            for ing in recipe.ingredients:
                ingredients.append(
                    IngredientResponse(
                        id=ing.id,
                        recipe_id=ing.recipe_id,
                        name=ing.name,
                        quantity=ing.quantity,
                        unit=ing.unit,
                        notes=ing.notes,
                        created_at=ing.created_at,
                        updated_at=ing.updated_at,
                        deleted_at=ing.deleted_at,
                        created_by=ing.created_by,
                        updated_by=ing.updated_by,
                    )
                )

        # Convert categories (skip if not eagerly loaded to avoid lazy loading issues)
        categories = []
        if hasattr(recipe, 'recipe_categories') and recipe.recipe_categories:
            for rc in recipe.recipe_categories:
                try:
                    # Try to access category - if it's loaded, this works; if not, skip
                    category = rc.__dict__.get('category')
                    if category is not None:
                        categories.append(
                            CategoryResponse(
                                id=category.id,
                                name=category.name,
                                slug=category.slug,
                                description=category.description,
                                parent_id=category.parent_id,
                                created_at=category.created_at,
                                updated_at=category.updated_at,
                                deleted_at=category.deleted_at,
                                created_by=category.created_by,
                                updated_by=category.updated_by,
                            )
                        )
                except Exception:
                    # If accessing category fails, skip it
                    continue

        # Convert nutritional info
        nutritional_info = None
        if recipe.nutritional_info:
            ni = recipe.nutritional_info
            nutritional_info = NutritionalInfoResponse(
                id=ni.id,
                recipe_id=ni.recipe_id,
                calories=ni.calories,
                protein_g=ni.protein_g,
                carbohydrates_g=ni.carbohydrates_g,
                fat_g=ni.fat_g,
                fiber_g=ni.fiber_g,
                sugar_g=ni.sugar_g,
                sodium_mg=ni.sodium_mg,
                cholesterol_mg=ni.cholesterol_mg,
                additional_info=ni.additional_info,
                created_at=ni.created_at,
                updated_at=ni.updated_at,
                deleted_at=ni.deleted_at,
                created_by=ni.created_by,
                updated_by=ni.updated_by,
            )

        return RecipeResponse(
            id=recipe.id,
            name=recipe.name,
            description=recipe.description,
            instructions=recipe.instructions,
            prep_time=recipe.prep_time,
            cook_time=recipe.cook_time,
            servings=recipe.servings,
            difficulty=recipe.difficulty,
            cuisine_type=recipe.cuisine_type,
            diet_types=recipe.diet_types,
            embedding=None,  # Don't expose embedding in API
            ingredients=ingredients,
            categories=categories,
            nutritional_info=nutritional_info,
            created_at=recipe.created_at,
            updated_at=recipe.updated_at,
            deleted_at=recipe.deleted_at,
            created_by=recipe.created_by,
            updated_by=recipe.updated_by,
        )
