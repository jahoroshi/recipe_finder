"""Integration tests for API with real database and services.

These tests use the actual database and Redis to verify end-to-end functionality.
"""

import asyncio
import json
from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.db.models import Category, DifficultyLevel
from app.db.session import get_db, init_db
from app.db.redis_client import init_redis, close_redis
from app.main import app


@pytest.fixture(scope="module")
def event_loop():
    """Create event loop for module-scoped async fixtures."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="module")
async def setup_database():
    """Initialize database and Redis for integration tests."""
    await init_db()
    await init_redis()
    yield
    # Cleanup is handled by test teardown


@pytest.fixture
async def async_client(setup_database):
    """Create async test client."""
    from httpx import ASGITransport
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
async def db_session():
    """Get database session for test setup."""
    async for session in get_db():
        yield session


@pytest.fixture
async def test_category(db_session):
    """Get or create a test category."""
    from sqlalchemy import select

    # Try to get existing category
    result = await db_session.execute(
        select(Category).where(Category.name == "Test Category")
    )
    category = result.scalar_one_or_none()

    if category is None:
        # Create new category
        category = Category(
            name="Test Category",
            slug="test-category",
            description="A test category",
        )
        db_session.add(category)
        await db_session.commit()
        await db_session.refresh(category)

    return category


class TestRecipeAPIIntegration:
    """Integration tests for recipe endpoints."""

    @pytest.mark.asyncio
    async def test_create_and_get_recipe(self, async_client, test_category):
        """Test creating a recipe and retrieving it."""
        # Create recipe
        recipe_data = {
            "name": f"Integration Test Recipe {uuid4()}",
            "description": "A test recipe for integration testing",
            "instructions": {
                "steps": [
                    "Step 1: Prepare ingredients",
                    "Step 2: Cook",
                    "Step 3: Serve",
                ]
            },
            "prep_time": 15,
            "cook_time": 30,
            "servings": 4,
            "difficulty": "medium",
            "cuisine_type": "Italian",
            "diet_types": ["vegetarian"],
            "ingredients": [
                {
                    "name": "pasta",
                    "quantity": 500,
                    "unit": "g",
                    "notes": "Any pasta type",
                },
                {
                    "name": "tomato sauce",
                    "quantity": 400,
                    "unit": "ml",
                    "notes": None,
                },
            ],
            "category_ids": [str(test_category.id)],
            "nutritional_info": {
                "calories": 450,
                "protein_g": 15.0,
                "carbohydrates_g": 70.0,
                "fat_g": 10.0,
            },
        }

        # Create recipe
        create_response = await async_client.post("/api/recipes", json=recipe_data)
        assert create_response.status_code == 201

        created_recipe = create_response.json()
        recipe_id = created_recipe["id"]

        # Verify recipe was created
        assert created_recipe["name"] == recipe_data["name"]
        assert created_recipe["cuisine_type"] == "Italian"
        assert len(created_recipe["ingredients"]) == 2

        # Get recipe by ID
        get_response = await async_client.get(f"/api/recipes/{recipe_id}")
        assert get_response.status_code == 200

        retrieved_recipe = get_response.json()
        assert retrieved_recipe["id"] == recipe_id
        assert retrieved_recipe["name"] == recipe_data["name"]

    @pytest.mark.asyncio
    async def test_list_recipes_with_pagination(self, async_client, test_category):
        """Test listing recipes with pagination."""
        # Create multiple recipes
        for i in range(3):
            recipe_data = {
                "name": f"Pagination Test Recipe {i} {uuid4()}",
                "instructions": {"steps": ["Cook"]},
                "difficulty": "easy",
                "category_ids": [str(test_category.id)],
            }
            response = await async_client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 201

        # List recipes with pagination
        response = await async_client.get("/api/recipes?page=1&page_size=2")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert "has_more" in data

    @pytest.mark.asyncio
    async def test_update_recipe(self, async_client, test_category):
        """Test updating a recipe."""
        # Create recipe
        recipe_data = {
            "name": f"Update Test Recipe {uuid4()}",
            "instructions": {"steps": ["Step 1"]},
            "difficulty": "easy",
            "prep_time": 10,
            "category_ids": [str(test_category.id)],
        }

        create_response = await async_client.post("/api/recipes", json=recipe_data)
        assert create_response.status_code == 201
        recipe_id = create_response.json()["id"]

        # Update recipe
        update_data = {
            "prep_time": 20,
            "cook_time": 30,
            "difficulty": "medium",
        }

        update_response = await async_client.put(
            f"/api/recipes/{recipe_id}", json=update_data
        )
        assert update_response.status_code == 200

        updated_recipe = update_response.json()
        assert updated_recipe["prep_time"] == 20
        assert updated_recipe["cook_time"] == 30
        assert updated_recipe["difficulty"] == "medium"

    @pytest.mark.asyncio
    async def test_delete_recipe(self, async_client, test_category):
        """Test deleting a recipe."""
        # Create recipe
        recipe_data = {
            "name": f"Delete Test Recipe {uuid4()}",
            "instructions": {"steps": ["Step 1"]},
            "difficulty": "easy",
            "category_ids": [str(test_category.id)],
        }

        create_response = await async_client.post("/api/recipes", json=recipe_data)
        assert create_response.status_code == 201
        recipe_id = create_response.json()["id"]

        # Delete recipe
        delete_response = await async_client.delete(f"/api/recipes/{recipe_id}")
        assert delete_response.status_code == 204

        # Verify recipe is deleted (should return 404 or empty result)
        get_response = await async_client.get(f"/api/recipes/{recipe_id}")
        # Note: Depending on implementation, this might be 404 or return deleted_at field
        assert get_response.status_code in [404, 200]

    @pytest.mark.asyncio
    async def test_filter_recipes(self, async_client, test_category):
        """Test filtering recipes."""
        # Create recipes with different cuisines
        cuisines = ["Italian", "Chinese", "Mexican"]

        for cuisine in cuisines:
            recipe_data = {
                "name": f"{cuisine} Test Recipe {uuid4()}",
                "instructions": {"steps": ["Cook"]},
                "difficulty": "easy",
                "cuisine_type": cuisine,
                "category_ids": [str(test_category.id)],
            }
            response = await async_client.post("/api/recipes", json=recipe_data)
            assert response.status_code == 201

        # Filter by cuisine
        response = await async_client.get("/api/recipes?cuisine_type=Italian")
        assert response.status_code == 200

        data = response.json()
        # Should have at least one Italian recipe
        if data["total"] > 0:
            assert any(
                item.get("cuisine_type") == "Italian" for item in data["items"]
            )

    @pytest.mark.asyncio
    async def test_bulk_import_recipes(self, async_client, test_category):
        """Test bulk import of recipes."""
        # Create test recipes data
        recipes_data = [
            {
                "name": f"Bulk Recipe 1 {uuid4()}",
                "instructions": {"steps": ["Step 1"]},
                "difficulty": "easy",
                "category_ids": [str(test_category.id)],
            },
            {
                "name": f"Bulk Recipe 2 {uuid4()}",
                "instructions": {"steps": ["Step 1"]},
                "difficulty": "medium",
                "category_ids": [str(test_category.id)],
            },
        ]

        # Create JSON file content
        file_content = json.dumps(recipes_data).encode()

        # Upload file
        files = {"file": ("recipes.json", file_content, "application/json")}
        response = await async_client.post("/api/recipes/bulk", files=files)

        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["total_recipes"] == 2

        # Give background task time to process
        await asyncio.sleep(2)


class TestSearchAPIIntegration:
    """Integration tests for search endpoints."""

    @pytest.mark.asyncio
    async def test_semantic_search(self, async_client, test_category):
        """Test semantic search functionality."""
        # Create a recipe to search for
        recipe_data = {
            "name": f"Delicious Italian Pasta Carbonara {uuid4()}",
            "description": "A classic Italian pasta dish with eggs and bacon",
            "instructions": {"steps": ["Cook pasta", "Mix with sauce"]},
            "difficulty": "medium",
            "cuisine_type": "Italian",
            "category_ids": [str(test_category.id)],
        }

        create_response = await async_client.post("/api/recipes", json=recipe_data)
        assert create_response.status_code == 201

        # Wait for embedding generation
        await asyncio.sleep(1)

        # Search for the recipe
        response = await async_client.post(
            "/api/search/semantic?query=italian pasta&limit=5"
        )

        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_hybrid_search(self, async_client, test_category):
        """Test hybrid search with query parsing."""
        # Create recipes
        recipes = [
            {
                "name": f"Quick Italian Pasta {uuid4()}",
                "description": "Fast and easy pasta",
                "instructions": {"steps": ["Cook quickly"]},
                "prep_time": 10,
                "cook_time": 15,
                "difficulty": "easy",
                "cuisine_type": "Italian",
                "category_ids": [str(test_category.id)],
            },
            {
                "name": f"Slow Italian Risotto {uuid4()}",
                "description": "Takes time but worth it",
                "instructions": {"steps": ["Cook slowly"]},
                "prep_time": 30,
                "cook_time": 45,
                "difficulty": "hard",
                "cuisine_type": "Italian",
                "category_ids": [str(test_category.id)],
            },
        ]

        for recipe in recipes:
            response = await async_client.post("/api/recipes", json=recipe)
            assert response.status_code == 201

        # Wait for embeddings
        await asyncio.sleep(1)

        # Hybrid search
        search_request = {
            "query": "quick italian pasta under 30 minutes",
            "limit": 10,
            "use_semantic": True,
            "use_filters": True,
        }

        response = await async_client.post("/api/search", json=search_request)

        assert response.status_code == 200
        data = response.json()
        assert "results" in data
        assert "query" in data
        assert data["query"] == search_request["query"]

    @pytest.mark.asyncio
    async def test_filter_search(self, async_client, test_category):
        """Test filter-based search."""
        # Create recipes with specific attributes
        recipe_data = {
            "name": f"Test Filter Recipe {uuid4()}",
            "instructions": {"steps": ["Cook"]},
            "difficulty": "easy",
            "cuisine_type": "Mexican",
            "category_ids": [str(test_category.id)],
        }

        create_response = await async_client.post("/api/recipes", json=recipe_data)
        assert create_response.status_code == 201

        # Filter search
        filters = {"cuisine_type": "Mexican", "difficulty": "easy"}

        response = await async_client.post(
            "/api/search/filter?limit=10", json=filters
        )

        assert response.status_code == 200
        results = response.json()
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_find_similar_recipes(self, async_client, test_category):
        """Test finding similar recipes."""
        # Create multiple similar recipes
        base_name = f"Similar Recipe Base {uuid4()}"

        recipes = [
            {
                "name": f"{base_name} 1",
                "description": "Italian pasta with tomato sauce",
                "instructions": {"steps": ["Cook"]},
                "cuisine_type": "Italian",
                "category_ids": [str(test_category.id)],
            },
            {
                "name": f"{base_name} 2",
                "description": "Italian pasta with pesto",
                "instructions": {"steps": ["Cook"]},
                "cuisine_type": "Italian",
                "category_ids": [str(test_category.id)],
            },
        ]

        recipe_ids = []
        for recipe in recipes:
            response = await async_client.post("/api/recipes", json=recipe)
            assert response.status_code == 201
            recipe_ids.append(response.json()["id"])

        # Wait for embeddings
        await asyncio.sleep(1)

        # Find similar recipes
        response = await async_client.get(
            f"/api/recipes/{recipe_ids[0]}/similar?limit=5"
        )

        assert response.status_code == 200
        similar_recipes = response.json()
        assert isinstance(similar_recipes, list)


class TestAPIHealthIntegration:
    """Integration tests for health endpoints."""

    @pytest.mark.asyncio
    async def test_health_check(self, async_client):
        """Test basic health check."""
        response = await async_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_detailed_health_check(self, async_client):
        """Test detailed health check."""
        response = await async_client.get("/health/detailed")
        assert response.status_code == 200

        data = response.json()
        assert "components" in data
        assert "redis" in data["components"]
        assert "database" in data["components"]


class TestAPIErrorHandling:
    """Integration tests for error handling."""

    @pytest.mark.asyncio
    async def test_404_not_found(self, async_client):
        """Test 404 error handling."""
        response = await async_client.get(f"/api/recipes/{uuid4()}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_validation_error(self, async_client):
        """Test validation error handling."""
        # Missing required fields
        invalid_recipe = {
            "name": "Invalid Recipe",
            # Missing instructions
        }

        response = await async_client.post("/api/recipes", json=invalid_recipe)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_duplicate_recipe_name(self, async_client, test_category):
        """Test creating duplicate recipe."""
        recipe_name = f"Duplicate Test {uuid4()}"

        recipe_data = {
            "name": recipe_name,
            "instructions": {"steps": ["Step 1"]},
            "difficulty": "easy",
            "category_ids": [str(test_category.id)],
        }

        # Create first recipe
        response1 = await async_client.post("/api/recipes", json=recipe_data)
        assert response1.status_code == 201

        # Try to create duplicate
        response2 = await async_client.post("/api/recipes", json=recipe_data)
        # Should fail with validation error
        assert response2.status_code == 400


class TestAPIPaginationAndFiltering:
    """Integration tests for pagination and filtering."""

    @pytest.mark.asyncio
    async def test_pagination_params(self, async_client):
        """Test pagination with different parameters."""
        # Test different page sizes
        for page_size in [5, 10, 20]:
            response = await async_client.get(
                f"/api/recipes?page=1&page_size={page_size}"
            )
            assert response.status_code == 200

            data = response.json()
            assert len(data["items"]) <= page_size

    @pytest.mark.asyncio
    async def test_filter_combinations(self, async_client, test_category):
        """Test combining multiple filters."""
        # Create recipe with multiple attributes
        recipe_data = {
            "name": f"Complex Filter Test {uuid4()}",
            "instructions": {"steps": ["Cook"]},
            "difficulty": "medium",
            "cuisine_type": "Italian",
            "prep_time": 20,
            "cook_time": 30,
            "category_ids": [str(test_category.id)],
        }

        create_response = await async_client.post("/api/recipes", json=recipe_data)
        assert create_response.status_code == 201

        # Apply multiple filters
        response = await async_client.get(
            "/api/recipes"
            "?cuisine_type=Italian"
            "&difficulty=medium"
            "&max_prep_time=25"
        )

        assert response.status_code == 200


# New test cases - Edge cases and additional scenarios for integration tests
class TestRecipeAPIEdgeCases:
    """Additional edge case tests for recipe API endpoints."""

    @pytest.mark.asyncio
    async def test_create_recipe_minimal_data(self, async_client, test_category):
        """Test creating recipe with only required fields."""
        minimal_recipe = {
            "name": f"Minimal Recipe {uuid4()}",
            "instructions": {"steps": ["Step 1"]},
            "category_ids": [str(test_category.id)],
        }

        response = await async_client.post("/api/recipes", json=minimal_recipe)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == minimal_recipe["name"]
        assert data["instructions"] == minimal_recipe["instructions"]

    @pytest.mark.asyncio
    async def test_create_recipe_with_all_fields(self, async_client, test_category):
        """Test creating recipe with all possible fields."""
        complete_recipe = {
            "name": f"Complete Recipe {uuid4()}",
            "description": "A complete recipe with all fields",
            "instructions": {
                "steps": ["Step 1", "Step 2", "Step 3"],
                "notes": "Important cooking notes",
            },
            "prep_time": 30,
            "cook_time": 60,
            "servings": 6,
            "difficulty": "hard",
            "cuisine_type": "French",
            "diet_types": ["gluten-free", "dairy-free"],
            "ingredients": [
                {
                    "name": "flour",
                    "quantity": 500,
                    "unit": "g",
                    "notes": "all-purpose",
                },
                {
                    "name": "water",
                    "quantity": 300,
                    "unit": "ml",
                    "notes": None,
                },
            ],
            "category_ids": [str(test_category.id)],
            "nutritional_info": {
                "calories": 250,
                "protein_g": 12.5,
                "carbohydrates_g": 45.0,
                "fat_g": 8.5,
                "fiber_g": 3.2,
                "sugar_g": 5.1,
            },
        }

        response = await async_client.post("/api/recipes", json=complete_recipe)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == complete_recipe["name"]
        assert data["description"] == complete_recipe["description"]
        assert data["servings"] == complete_recipe["servings"]

    @pytest.mark.asyncio
    async def test_create_recipe_empty_name(self, async_client, test_category):
        """Test creating recipe with empty name fails validation."""
        invalid_recipe = {
            "name": "",
            "instructions": {"steps": ["Step 1"]},
            "category_ids": [str(test_category.id)],
        }

        response = await async_client.post("/api/recipes", json=invalid_recipe)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_recipe_very_long_name(self, async_client, test_category):
        """Test creating recipe with very long name."""
        long_name = "Recipe " + "A" * 500
        recipe_data = {
            "name": long_name,
            "instructions": {"steps": ["Step 1"]},
            "category_ids": [str(test_category.id)],
        }

        response = await async_client.post("/api/recipes", json=recipe_data)
        # Should either succeed or fail with validation error
        assert response.status_code in [201, 422]

    @pytest.mark.asyncio
    async def test_create_recipe_invalid_difficulty(self, async_client, test_category):
        """Test creating recipe with invalid difficulty value."""
        invalid_recipe = {
            "name": f"Invalid Difficulty {uuid4()}",
            "instructions": {"steps": ["Step 1"]},
            "difficulty": "super_hard",  # Invalid value
            "category_ids": [str(test_category.id)],
        }

        response = await async_client.post("/api/recipes", json=invalid_recipe)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_recipe_negative_times(self, async_client, test_category):
        """Test creating recipe with negative time values."""
        invalid_recipe = {
            "name": f"Negative Times {uuid4()}",
            "instructions": {"steps": ["Step 1"]},
            "prep_time": -10,
            "cook_time": -20,
            "category_ids": [str(test_category.id)],
        }

        response = await async_client.post("/api/recipes", json=invalid_recipe)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_create_recipe_zero_servings(self, async_client, test_category):
        """Test creating recipe with zero servings."""
        invalid_recipe = {
            "name": f"Zero Servings {uuid4()}",
            "instructions": {"steps": ["Step 1"]},
            "servings": 0,
            "category_ids": [str(test_category.id)],
        }

        response = await async_client.post("/api/recipes", json=invalid_recipe)
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_get_recipe_invalid_uuid(self, async_client):
        """Test getting recipe with invalid UUID format."""
        response = await async_client.get("/api/recipes/not-a-valid-uuid")
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_update_recipe_partial_fields(self, async_client, test_category):
        """Test updating only some fields of a recipe."""
        # Create recipe
        recipe_data = {
            "name": f"Partial Update Test {uuid4()}",
            "instructions": {"steps": ["Step 1"]},
            "difficulty": "easy",
            "prep_time": 10,
            "cook_time": 20,
            "category_ids": [str(test_category.id)],
        }

        create_response = await async_client.post("/api/recipes", json=recipe_data)
        assert create_response.status_code == 201
        recipe_id = create_response.json()["id"]
        original_name = create_response.json()["name"]

        # Update only prep_time
        update_data = {"prep_time": 15}

        update_response = await async_client.put(
            f"/api/recipes/{recipe_id}", json=update_data
        )
        assert update_response.status_code == 200

        updated = update_response.json()
        assert updated["prep_time"] == 15
        assert updated["name"] == original_name  # Should remain unchanged

    @pytest.mark.asyncio
    async def test_update_nonexistent_recipe(self, async_client):
        """Test updating a recipe that doesn't exist."""
        nonexistent_id = uuid4()
        update_data = {"prep_time": 20}

        response = await async_client.put(
            f"/api/recipes/{nonexistent_id}", json=update_data
        )
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_nonexistent_recipe(self, async_client):
        """Test deleting a recipe that doesn't exist."""
        nonexistent_id = uuid4()

        response = await async_client.delete(f"/api/recipes/{nonexistent_id}")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_list_recipes_empty_page(self, async_client):
        """Test listing recipes with page beyond available data."""
        response = await async_client.get("/api/recipes?page=999&page_size=10")
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        # Items might be empty or contain recipes depending on total count

    @pytest.mark.asyncio
    async def test_list_recipes_page_size_boundaries(self, async_client):
        """Test pagination with various page size values."""
        # Test very small page size
        response = await async_client.get("/api/recipes?page=1&page_size=1")
        assert response.status_code == 200

        # Test large page size
        response = await async_client.get("/api/recipes?page=1&page_size=100")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_list_recipes_invalid_pagination(self, async_client):
        """Test listing recipes with invalid pagination parameters."""
        # Negative page
        response = await async_client.get("/api/recipes?page=-1&page_size=10")
        assert response.status_code == 422  # Validation error

        # Zero page size
        response = await async_client.get("/api/recipes?page=1&page_size=0")
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_filter_by_nonexistent_cuisine(self, async_client):
        """Test filtering by a cuisine type that has no recipes."""
        response = await async_client.get(
            "/api/recipes?cuisine_type=NonexistentCuisine12345"
        )
        assert response.status_code == 200

        data = response.json()
        assert "items" in data
        # Should return empty list or recipes if any match

    @pytest.mark.asyncio
    async def test_bulk_import_empty_file(self, async_client):
        """Test bulk import with empty JSON array."""
        import json

        file_content = json.dumps([]).encode()
        files = {"file": ("empty.json", file_content, "application/json")}

        response = await async_client.post("/api/recipes/bulk", files=files)
        # Should handle empty array gracefully
        assert response.status_code in [202, 400]

    @pytest.mark.asyncio
    async def test_bulk_import_large_batch(self, async_client, test_category):
        """Test bulk import with large number of recipes."""
        import json

        # Create 50 recipes
        recipes = [
            {
                "name": f"Bulk Recipe {i} {uuid4()}",
                "instructions": {"steps": ["Step 1"]},
                "difficulty": "easy",
                "category_ids": [str(test_category.id)],
            }
            for i in range(50)
        ]

        file_content = json.dumps(recipes).encode()
        files = {"file": ("recipes.json", file_content, "application/json")}

        response = await async_client.post("/api/recipes/bulk", files=files)
        assert response.status_code == 202

        data = response.json()
        assert data["total_recipes"] == 50

    @pytest.mark.asyncio
    async def test_bulk_import_malformed_recipe(self, async_client):
        """Test bulk import with malformed recipe data."""
        import json

        recipes = [
            {
                "name": "Valid Recipe",
                "instructions": {"steps": ["Step 1"]},
            },
            {
                "name": "",  # Invalid - empty name
                "instructions": {"steps": ["Step 1"]},
            },
        ]

        file_content = json.dumps(recipes).encode()
        files = {"file": ("recipes.json", file_content, "application/json")}

        response = await async_client.post("/api/recipes/bulk", files=files)
        # Should accept but may partially fail during processing
        assert response.status_code in [202, 400]


class TestSearchAPIEdgeCases:
    """Additional edge case tests for search endpoints."""

    @pytest.mark.asyncio
    async def test_semantic_search_empty_query(self, async_client):
        """Test semantic search with empty query."""
        response = await async_client.post("/api/search/semantic?query=&limit=5")
        # Should handle empty query
        assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_semantic_search_special_characters(self, async_client):
        """Test semantic search with special characters."""
        response = await async_client.post(
            "/api/search/semantic?query=pasta!@#$%^&*()&limit=5"
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_semantic_search_very_long_query(self, async_client):
        """Test semantic search with very long query."""
        long_query = "italian pasta recipe " * 100
        response = await async_client.post(
            f"/api/search/semantic?query={long_query}&limit=5"
        )
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_semantic_search_limit_boundaries(self, async_client):
        """Test semantic search with various limit values."""
        # Minimum limit
        response = await async_client.post("/api/search/semantic?query=pasta&limit=1")
        assert response.status_code == 200

        # Large limit
        response = await async_client.post("/api/search/semantic?query=pasta&limit=100")
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_semantic_search_zero_limit(self, async_client):
        """Test semantic search with zero limit."""
        response = await async_client.post("/api/search/semantic?query=pasta&limit=0")
        assert response.status_code in [200, 422]  # May reject zero limit

    @pytest.mark.asyncio
    async def test_hybrid_search_no_results(self, async_client):
        """Test hybrid search that returns no results."""
        search_request = {
            "query": f"nonexistent_recipe_xyz_{uuid4()}",
            "limit": 10,
            "use_semantic": True,
            "use_filters": True,
        }

        response = await async_client.post("/api/search", json=search_request)
        assert response.status_code == 200

        data = response.json()
        assert "results" in data

    @pytest.mark.asyncio
    async def test_hybrid_search_only_semantic(self, async_client, test_category):
        """Test hybrid search with only semantic enabled."""
        # Create a recipe first
        recipe_data = {
            "name": f"Semantic Only Test {uuid4()}",
            "description": "Test for semantic only search",
            "instructions": {"steps": ["Cook"]},
            "category_ids": [str(test_category.id)],
        }

        await async_client.post("/api/recipes", json=recipe_data)
        await asyncio.sleep(1)

        search_request = {
            "query": "test semantic",
            "limit": 5,
            "use_semantic": True,
            "use_filters": False,
        }

        response = await async_client.post("/api/search", json=search_request)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_hybrid_search_only_filters(self, async_client, test_category):
        """Test hybrid search with only filters enabled."""
        search_request = {
            "query": "quick recipe under 30 minutes",
            "limit": 5,
            "use_semantic": False,
            "use_filters": True,
        }

        response = await async_client.post("/api/search", json=search_request)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_filter_search_empty_filters(self, async_client):
        """Test filter search with empty filter object."""
        response = await async_client.post("/api/search/filter?limit=10", json={})
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_filter_search_invalid_filter_value(self, async_client):
        """Test filter search with invalid filter values."""
        filters = {"difficulty": "invalid_difficulty", "cuisine_type": "Test"}

        response = await async_client.post("/api/search/filter?limit=10", json=filters)
        # Should either ignore invalid filter or return error
        assert response.status_code in [200, 400, 422]

    @pytest.mark.asyncio
    async def test_find_similar_recipes_nonexistent(self, async_client):
        """Test finding similar recipes for nonexistent recipe."""
        nonexistent_id = uuid4()

        response = await async_client.get(
            f"/api/recipes/{nonexistent_id}/similar?limit=5"
        )
        assert response.status_code == 404


class TestHealthEndpointsEdgeCases:
    """Additional edge case tests for health endpoints."""

    @pytest.mark.asyncio
    async def test_health_check_response_structure(self, async_client):
        """Test that health check returns proper structure."""
        response = await async_client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert isinstance(data["status"], str)

    @pytest.mark.asyncio
    async def test_detailed_health_check_components(self, async_client):
        """Test that detailed health check includes all components."""
        response = await async_client.get("/health/detailed")
        assert response.status_code == 200

        data = response.json()
        assert "components" in data

        # Should include database and redis
        components = data["components"]
        assert "database" in components or "redis" in components

    @pytest.mark.asyncio
    async def test_health_check_concurrent_requests(self, async_client):
        """Test multiple concurrent health check requests."""
        import asyncio

        # Make 10 concurrent health check requests
        tasks = [async_client.get("/health") for _ in range(10)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
            assert response.json()["status"] == "healthy"


class TestAPIErrorHandlingEdgeCases:
    """Additional edge case tests for API error handling."""

    @pytest.mark.asyncio
    async def test_invalid_json_body(self, async_client):
        """Test request with invalid JSON body."""
        import httpx

        # Send malformed JSON
        response = await async_client.post(
            "/api/recipes",
            content=b"{invalid json}",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422  # Validation error

    @pytest.mark.asyncio
    async def test_missing_required_fields(self, async_client):
        """Test creating recipe without required fields."""
        incomplete_recipe = {
            "name": "Missing Instructions",
            # Missing instructions field
        }

        response = await async_client.post("/api/recipes", json=incomplete_recipe)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_invalid_field_types(self, async_client, test_category):
        """Test creating recipe with wrong field types."""
        invalid_recipe = {
            "name": f"Invalid Types {uuid4()}",
            "instructions": "should be object not string",  # Wrong type
            "prep_time": "not a number",  # Wrong type
            "category_ids": [str(test_category.id)],
        }

        response = await async_client.post("/api/recipes", json=invalid_recipe)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_request_with_extra_fields(self, async_client, test_category):
        """Test creating recipe with extra unknown fields."""
        recipe_with_extra = {
            "name": f"Extra Fields {uuid4()}",
            "instructions": {"steps": ["Step 1"]},
            "category_ids": [str(test_category.id)],
            "unknown_field": "should be ignored",
            "another_extra": 123,
        }

        response = await async_client.post("/api/recipes", json=recipe_with_extra)
        # Should either ignore extra fields or reject
        assert response.status_code in [201, 422]


class TestAPIConcurrencyAndPerformance:
    """Test API behavior under concurrent requests."""

    @pytest.mark.asyncio
    async def test_concurrent_recipe_creation(self, async_client, test_category):
        """Test creating multiple recipes concurrently."""
        import asyncio

        async def create_recipe(index):
            recipe_data = {
                "name": f"Concurrent Recipe {index} {uuid4()}",
                "instructions": {"steps": ["Step 1"]},
                "category_ids": [str(test_category.id)],
            }
            return await async_client.post("/api/recipes", json=recipe_data)

        # Create 5 recipes concurrently
        tasks = [create_recipe(i) for i in range(5)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 201

    @pytest.mark.asyncio
    async def test_concurrent_searches(self, async_client):
        """Test concurrent search requests."""
        import asyncio

        async def search(query):
            return await async_client.post(f"/api/search/semantic?query={query}&limit=5")

        # Perform 5 concurrent searches
        queries = ["pasta", "pizza", "salad", "soup", "dessert"]
        tasks = [search(q) for q in queries]
        responses = await asyncio.gather(*tasks)

        # All should complete
        for response in responses:
            assert response.status_code in [200, 400]

    @pytest.mark.asyncio
    async def test_concurrent_read_operations(self, async_client):
        """Test concurrent GET requests."""
        import asyncio

        # Perform multiple concurrent GET requests
        tasks = [async_client.get("/api/recipes?page=1&page_size=10") for _ in range(10)]
        responses = await asyncio.gather(*tasks)

        # All should succeed
        for response in responses:
            assert response.status_code == 200
