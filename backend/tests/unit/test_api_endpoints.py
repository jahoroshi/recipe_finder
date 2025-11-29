"""Unit tests for API endpoints (mocked dependencies)."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.db.models import DifficultyLevel
from app.main import app
from app.schemas.recipe import RecipeResponse
from app.schemas.search import SearchResponse, SearchResult


@pytest.fixture
def client():
    """Create test client."""
    # Override all database dependencies for unit tests
    from app.api.deps import get_db, get_redis

    def mock_get_db():
        return Mock()

    def mock_get_redis():
        return Mock()

    app.dependency_overrides[get_db] = mock_get_db
    app.dependency_overrides[get_redis] = mock_get_redis

    client = TestClient(app)
    yield client

    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
def mock_recipe_response():
    """Create mock recipe response."""
    recipe_id = uuid4()
    return RecipeResponse(
        id=recipe_id,
        name="Test Pasta",
        description="A delicious test pasta",
        instructions={"steps": ["Cook pasta", "Add sauce"]},
        prep_time=15,
        cook_time=20,
        servings=4,
        difficulty=DifficultyLevel.MEDIUM,
        cuisine_type="Italian",
        diet_types=["vegetarian"],
        ingredients=[],
        categories=[],
        nutritional_info=None,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        deleted_at=None,
        created_by=None,
        updated_by=None,
    )


class TestRecipeEndpoints:
    """Test recipe CRUD endpoints."""

    def test_create_recipe_success(self, client, mock_recipe_response):
        """Test successful recipe creation."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.create_recipe.return_value = mock_recipe_response
        mock_get_service.return_value = mock_service

        # Make request
        recipe_data = {
            "name": "Test Pasta",
            "description": "A delicious test pasta",
            "instructions": {"steps": ["Cook pasta", "Add sauce"]},
            "prep_time": 15,
            "cook_time": 20,
            "servings": 4,
            "difficulty": "medium",
            "cuisine_type": "Italian",
            "diet_types": ["vegetarian"],
            "ingredients": [],
            "category_ids": [],
        }

        response = client.post("/api/recipes", json=recipe_data)

        # Assertions
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Pasta"
        assert data["cuisine_type"] == "Italian"

    @patch("app.api.endpoints.recipes.get_recipe_service")
    def test_create_recipe_validation_error(self, mock_get_service, client):
        """Test recipe creation with validation error."""
        # Setup mock to raise ValueError
        mock_service = AsyncMock()
        mock_service.create_recipe.side_effect = ValueError("Recipe name already exists")
        mock_get_service.return_value = mock_service

        # Make request
        recipe_data = {
            "name": "Duplicate Recipe",
            "instructions": {"steps": ["Step 1"]},
            "difficulty": "medium",
        }

        response = client.post("/api/recipes", json=recipe_data)

        # Assertions
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data

    @patch("app.api.endpoints.recipes.get_recipe_service")
    def test_get_recipe_success(self, mock_get_service, client, mock_recipe_response):
        """Test successful recipe retrieval."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.get_recipe.return_value = mock_recipe_response
        mock_get_service.return_value = mock_service

        # Make request
        recipe_id = mock_recipe_response.id
        response = client.get(f"/api/recipes/{recipe_id}")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(recipe_id)
        assert data["name"] == "Test Pasta"

    @patch("app.api.endpoints.recipes.get_recipe_service")
    def test_get_recipe_not_found(self, mock_get_service, client):
        """Test recipe retrieval when not found."""
        # Setup mock to raise ValueError
        mock_service = AsyncMock()
        mock_service.get_recipe.side_effect = ValueError("Recipe not found")
        mock_get_service.return_value = mock_service

        # Make request
        recipe_id = uuid4()
        response = client.get(f"/api/recipes/{recipe_id}")

        # Assertions
        assert response.status_code == 404

    @patch("app.api.endpoints.recipes.get_recipe_service")
    def test_list_recipes_with_filters(self, mock_get_service, client, mock_recipe_response):
        """Test recipe listing with filters."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.list_recipes.return_value = [mock_recipe_response]
        mock_get_service.return_value = mock_service

        # Make request with filters
        response = client.get(
            "/api/recipes",
            params={
                "cuisine_type": "Italian",
                "difficulty": "medium",
                "page": 1,
                "page_size": 10,
            },
        )

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 1
        assert data["total"] == 1

    @patch("app.api.endpoints.recipes.get_recipe_service")
    def test_update_recipe_success(self, mock_get_service, client, mock_recipe_response):
        """Test successful recipe update."""
        # Setup mock
        updated_recipe = mock_recipe_response.model_copy()
        updated_recipe.prep_time = 25
        mock_service = AsyncMock()
        mock_service.update_recipe.return_value = updated_recipe
        mock_get_service.return_value = mock_service

        # Make request
        recipe_id = mock_recipe_response.id
        update_data = {"prep_time": 25}

        response = client.put(f"/api/recipes/{recipe_id}", json=update_data)

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["prep_time"] == 25

    @patch("app.api.endpoints.recipes.get_recipe_service")
    def test_update_recipe_not_found(self, mock_get_service, client):
        """Test recipe update when not found."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.update_recipe.side_effect = ValueError("Recipe not found")
        mock_get_service.return_value = mock_service

        # Make request
        recipe_id = uuid4()
        update_data = {"prep_time": 25}

        response = client.put(f"/api/recipes/{recipe_id}", json=update_data)

        # Assertions
        assert response.status_code == 404

    @patch("app.api.endpoints.recipes.get_recipe_service")
    def test_delete_recipe_success(self, mock_get_service, client):
        """Test successful recipe deletion."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.delete_recipe.return_value = None
        mock_get_service.return_value = mock_service

        # Make request
        recipe_id = uuid4()
        response = client.delete(f"/api/recipes/{recipe_id}")

        # Assertions
        assert response.status_code == 204

    @patch("app.api.endpoints.recipes.get_recipe_service")
    def test_delete_recipe_not_found(self, mock_get_service, client):
        """Test recipe deletion when not found."""
        # Setup mock
        mock_service = AsyncMock()
        mock_service.delete_recipe.side_effect = ValueError("Recipe not found")
        mock_get_service.return_value = mock_service

        # Make request
        recipe_id = uuid4()
        response = client.delete(f"/api/recipes/{recipe_id}")

        # Assertions
        assert response.status_code == 404

    @patch("app.api.endpoints.recipes.get_recipe_service")
    @patch("app.api.endpoints.recipes.get_search_service")
    def test_find_similar_recipes(
        self, mock_get_search_service, mock_get_recipe_service, client, mock_recipe_response
    ):
        """Test finding similar recipes."""
        # Setup mocks
        mock_recipe_service = AsyncMock()
        mock_recipe_service.get_recipe.return_value = mock_recipe_response
        mock_get_recipe_service.return_value = mock_recipe_service

        # Create similar recipe
        similar_recipe = mock_recipe_response.model_copy()
        similar_recipe.id = uuid4()
        similar_recipe.name = "Similar Pasta"

        # Mock Recipe object for search service
        from app.db.models import Recipe
        mock_similar_db_recipe = Mock(spec=Recipe)
        mock_similar_db_recipe.id = similar_recipe.id
        mock_similar_db_recipe.name = similar_recipe.name
        mock_similar_db_recipe.description = similar_recipe.description
        mock_similar_db_recipe.instructions = similar_recipe.instructions
        mock_similar_db_recipe.prep_time = similar_recipe.prep_time
        mock_similar_db_recipe.cook_time = similar_recipe.cook_time
        mock_similar_db_recipe.servings = similar_recipe.servings
        mock_similar_db_recipe.difficulty = similar_recipe.difficulty
        mock_similar_db_recipe.cuisine_type = similar_recipe.cuisine_type
        mock_similar_db_recipe.diet_types = similar_recipe.diet_types
        mock_similar_db_recipe.created_at = similar_recipe.created_at
        mock_similar_db_recipe.updated_at = similar_recipe.updated_at
        mock_similar_db_recipe.deleted_at = None
        mock_similar_db_recipe.created_by = None
        mock_similar_db_recipe.updated_by = None

        mock_search_service = AsyncMock()
        mock_search_service.semantic_search.return_value = [
            (mock_similar_db_recipe, 0.85)
        ]
        mock_search_service._recipe_to_response.return_value = similar_recipe
        mock_get_search_service.return_value = mock_search_service

        # Make request
        recipe_id = mock_recipe_response.id
        response = client.get(f"/api/recipes/{recipe_id}/similar")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @patch("app.api.endpoints.recipes.get_recipe_service")
    def test_bulk_import_success(self, mock_get_service, client):
        """Test successful bulk import."""
        # Setup mock
        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service

        # Create test file content
        import json
        import io

        recipes_data = [
            {
                "name": "Recipe 1",
                "instructions": {"steps": ["Step 1"]},
                "difficulty": "easy",
            },
            {
                "name": "Recipe 2",
                "instructions": {"steps": ["Step 1"]},
                "difficulty": "medium",
            },
        ]

        file_content = json.dumps(recipes_data).encode()
        files = {"file": ("recipes.json", io.BytesIO(file_content), "application/json")}

        # Make request
        response = client.post("/api/recipes/bulk", files=files)

        # Assertions
        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "accepted"
        assert data["total_recipes"] == 2

    def test_bulk_import_invalid_file_type(self, client):
        """Test bulk import with invalid file type."""
        import io

        file_content = b"not json content"
        files = {"file": ("recipes.txt", io.BytesIO(file_content), "text/plain")}

        response = client.post("/api/recipes/bulk", files=files)

        assert response.status_code == 400

    @patch("app.api.endpoints.recipes.get_recipe_service")
    def test_bulk_import_invalid_json(self, mock_get_service, client):
        """Test bulk import with invalid JSON."""
        import io

        mock_service = AsyncMock()
        mock_get_service.return_value = mock_service

        file_content = b"{invalid json}"
        files = {"file": ("recipes.json", io.BytesIO(file_content), "application/json")}

        response = client.post("/api/recipes/bulk", files=files)

        assert response.status_code == 400


class TestSearchEndpoints:
    """Test search endpoints."""

    @patch("app.api.endpoints.search.get_search_service")
    def test_hybrid_search_success(self, mock_get_service, client, mock_recipe_response):
        """Test successful hybrid search."""
        # Setup mock
        search_result = SearchResult(
            recipe=mock_recipe_response,
            score=0.95,
            distance=0.05,
            match_type="hybrid",
        )

        search_response = SearchResponse(
            query="italian pasta",
            parsed_query=None,
            results=[search_result],
            total=1,
            search_type="hybrid",
            metadata={},
        )

        mock_service = AsyncMock()
        mock_service.hybrid_search.return_value = search_response
        mock_get_service.return_value = mock_service

        # Make request
        search_data = {
            "query": "italian pasta",
            "limit": 10,
            "use_semantic": True,
            "use_filters": True,
        }

        response = client.post("/api/search", json=search_data)

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "italian pasta"
        assert data["total"] == 1
        assert len(data["results"]) == 1

    @patch("app.api.endpoints.search.get_search_service")
    def test_hybrid_search_empty_query(self, mock_get_service, client):
        """Test hybrid search with empty query."""
        mock_service = AsyncMock()
        mock_service.hybrid_search.side_effect = ValueError("Query cannot be empty")
        mock_get_service.return_value = mock_service

        search_data = {"query": "", "limit": 10}

        response = client.post("/api/search", json=search_data)

        assert response.status_code == 400

    @patch("app.api.endpoints.search.get_search_service")
    def test_semantic_search_success(self, mock_get_service, client, mock_recipe_response):
        """Test successful semantic search."""
        # Mock Recipe object
        from app.db.models import Recipe
        mock_recipe = Mock(spec=Recipe)
        mock_recipe.id = mock_recipe_response.id
        mock_recipe.name = mock_recipe_response.name
        mock_recipe.description = mock_recipe_response.description
        mock_recipe.instructions = mock_recipe_response.instructions
        mock_recipe.prep_time = mock_recipe_response.prep_time
        mock_recipe.cook_time = mock_recipe_response.cook_time
        mock_recipe.servings = mock_recipe_response.servings
        mock_recipe.difficulty = mock_recipe_response.difficulty
        mock_recipe.cuisine_type = mock_recipe_response.cuisine_type
        mock_recipe.diet_types = mock_recipe_response.diet_types
        mock_recipe.created_at = mock_recipe_response.created_at
        mock_recipe.updated_at = mock_recipe_response.updated_at
        mock_recipe.deleted_at = None
        mock_recipe.created_by = None
        mock_recipe.updated_by = None

        # Setup mock
        mock_service = AsyncMock()
        mock_service.semantic_search.return_value = [(mock_recipe, 0.92)]
        mock_service._recipe_to_response.return_value = mock_recipe_response
        mock_get_service.return_value = mock_service

        # Make request
        response = client.post("/api/search/semantic?query=pasta&limit=5")

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["score"] == 0.92

    @patch("app.api.endpoints.search.get_search_service")
    def test_filter_search_success(self, mock_get_service, client, mock_recipe_response):
        """Test successful filter search."""
        # Mock Recipe object
        from app.db.models import Recipe
        mock_recipe = Mock(spec=Recipe)
        mock_recipe.id = mock_recipe_response.id
        mock_recipe.name = mock_recipe_response.name
        mock_recipe.description = mock_recipe_response.description
        mock_recipe.instructions = mock_recipe_response.instructions
        mock_recipe.prep_time = mock_recipe_response.prep_time
        mock_recipe.cook_time = mock_recipe_response.cook_time
        mock_recipe.servings = mock_recipe_response.servings
        mock_recipe.difficulty = mock_recipe_response.difficulty
        mock_recipe.cuisine_type = mock_recipe_response.cuisine_type
        mock_recipe.diet_types = mock_recipe_response.diet_types
        mock_recipe.created_at = mock_recipe_response.created_at
        mock_recipe.updated_at = mock_recipe_response.updated_at
        mock_recipe.deleted_at = None
        mock_recipe.created_by = None
        mock_recipe.updated_by = None

        # Setup mock
        mock_service = AsyncMock()
        mock_service.filter_search.return_value = [(mock_recipe, 1.0)]
        mock_service._recipe_to_response.return_value = mock_recipe_response
        mock_get_service.return_value = mock_service

        # Make request
        filters = {"cuisine_type": "Italian", "difficulty": "medium"}
        response = client.post("/api/search/filter?limit=10", json=filters)

        # Assertions
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_basic_health_check(self, client):
        """Test basic health check endpoint."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data

    @patch("app.main.get_redis")
    @patch("app.main.get_engine")
    def test_detailed_health_check(self, mock_get_engine, mock_get_redis, client):
        """Test detailed health check endpoint."""
        # Setup mocks
        mock_redis_client = AsyncMock()
        mock_redis_client.ping.return_value = True
        mock_get_redis.return_value = mock_redis_client

        mock_engine = Mock()
        mock_get_engine.return_value = mock_engine

        response = client.get("/health/detailed")

        assert response.status_code == 200
        data = response.json()
        assert "components" in data
        assert "redis" in data["components"]
        assert "database" in data["components"]

    def test_root_endpoint(self, client):
        """Test API root endpoint."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "documentation" in data
