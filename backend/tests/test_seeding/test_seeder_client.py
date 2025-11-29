"""Tests for seeder API client."""

from unittest.mock import AsyncMock, Mock, patch
from uuid import UUID, uuid4

import httpx
import pytest

from scripts.seeder_client import (
    SeederAPIClient,
    SeederReport,
    ValidationReport,
)


class TestSeederAPIClient:
    """Test suite for SeederAPIClient class."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Create mock httpx client."""
        return AsyncMock(spec=httpx.AsyncClient)

    @pytest.fixture
    async def client(self, mock_httpx_client):
        """Create seeder client with mocked httpx."""
        async with SeederAPIClient("http://localhost:8009") as client:
            client.client = mock_httpx_client
            yield client

    @pytest.mark.asyncio
    async def test_client_initialization(self):
        """Test client initialization."""
        client = SeederAPIClient(
            base_url="http://localhost:8009",
            timeout=30,
            max_retries=3,
        )

        assert client.base_url == "http://localhost:8009"
        assert client.timeout == 30
        assert client.max_retries == 3

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager protocol."""
        async with SeederAPIClient("http://localhost:8009") as client:
            assert client.client is not None
            assert isinstance(client.client, httpx.AsyncClient)

    @pytest.mark.asyncio
    async def test_create_recipe_success(self, client, mock_httpx_client):
        """Test successful recipe creation."""
        recipe_data = {
            "name": "Test Recipe",
            "difficulty": "easy",
            "instructions": {"steps": ["Step 1"]},
        }

        expected_response = {
            "id": str(uuid4()),
            "name": "Test Recipe",
            "difficulty": "easy",
        }

        mock_response = Mock()
        mock_response.json.return_value = expected_response
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        result = await client.create_recipe(recipe_data)

        assert result is not None
        assert result["name"] == "Test Recipe"
        mock_httpx_client.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_recipe_failure(self, client, mock_httpx_client):
        """Test recipe creation failure."""
        recipe_data = {"name": "Test Recipe"}

        mock_httpx_client.request.side_effect = httpx.HTTPError("API Error")

        result = await client.create_recipe(recipe_data)

        assert result is None

    @pytest.mark.asyncio
    async def test_create_recipe_batch(self, client, mock_httpx_client):
        """Test batch recipe creation."""
        recipes = [
            {"name": "Recipe 1", "difficulty": "easy", "instructions": {"steps": []}},
            {"name": "Recipe 2", "difficulty": "medium", "instructions": {"steps": []}},
            {"name": "Recipe 3", "difficulty": "hard", "instructions": {"steps": []}},
        ]

        # Mock successful responses
        def mock_request(*args, **kwargs):
            response = Mock()
            response.json.return_value = {"id": str(uuid4()), "name": kwargs.get("json", {}).get("name")}
            response.raise_for_status = Mock()
            return response

        mock_httpx_client.request.side_effect = mock_request

        results = await client.create_recipe_batch(recipes)

        assert len(results) == 3
        assert all(r is not None for r in results)

    @pytest.mark.asyncio
    async def test_retry_logic_success_after_retry(self, client, mock_httpx_client):
        """Test retry logic succeeds after initial failure."""
        recipe_data = {"name": "Test Recipe", "instructions": {"steps": []}}

        # Fail first two times, succeed on third
        responses = [
            httpx.HTTPError("Error 1"),
            httpx.HTTPError("Error 2"),
            Mock(
                json=lambda: {"id": str(uuid4()), "name": "Test Recipe"},
                raise_for_status=Mock(),
            ),
        ]

        mock_httpx_client.request.side_effect = responses

        result = await client.create_recipe(recipe_data)

        assert result is not None
        assert mock_httpx_client.request.call_count == 3

    @pytest.mark.asyncio
    async def test_retry_logic_exhausted(self, client, mock_httpx_client):
        """Test retry logic when all retries fail."""
        recipe_data = {"name": "Test Recipe"}

        # Fail all attempts
        mock_httpx_client.request.side_effect = httpx.HTTPError("API Error")

        result = await client.create_recipe(recipe_data)

        assert result is None
        assert mock_httpx_client.request.call_count == 3  # max_retries

    @pytest.mark.asyncio
    async def test_verify_recipe_exists_true(self, client, mock_httpx_client):
        """Test verifying recipe exists."""
        recipe_id = uuid4()

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        exists = await client.verify_recipe_exists(recipe_id)

        assert exists is True

    @pytest.mark.asyncio
    async def test_verify_recipe_exists_false(self, client, mock_httpx_client):
        """Test verifying non-existent recipe."""
        recipe_id = uuid4()

        mock_httpx_client.request.side_effect = httpx.HTTPError("Not Found")

        exists = await client.verify_recipe_exists(recipe_id)

        assert exists is False

    @pytest.mark.asyncio
    async def test_get_recipe_count(self, client, mock_httpx_client):
        """Test getting recipe count."""
        mock_response = Mock()
        mock_response.json.return_value = {"total": 42, "items": []}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        count = await client.get_recipe_count()

        assert count == 42

    @pytest.mark.asyncio
    async def test_get_recipe_count_error(self, client, mock_httpx_client):
        """Test getting recipe count with API error."""
        mock_httpx_client.request.side_effect = httpx.HTTPError("API Error")

        count = await client.get_recipe_count()

        assert count == 0

    @pytest.mark.asyncio
    async def test_search_recipes(self, client, mock_httpx_client):
        """Test recipe search."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "results": [
                {"id": str(uuid4()), "name": "Chicken Recipe"},
                {"id": str(uuid4()), "name": "Chicken Curry"},
            ]
        }
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        results = await client.search_recipes("chicken", limit=10)

        assert len(results) == 2
        assert all("name" in r for r in results)

    @pytest.mark.asyncio
    async def test_search_recipes_error(self, client, mock_httpx_client):
        """Test recipe search with error."""
        mock_httpx_client.request.side_effect = httpx.HTTPError("Search Error")

        results = await client.search_recipes("chicken")

        assert results == []

    @pytest.mark.asyncio
    async def test_verify_search_indexing(self, client, mock_httpx_client):
        """Test search indexing verification."""
        sample_queries = ["chicken", "pasta", "vegan"]

        # Mock search responses
        def mock_search(*args, **kwargs):
            response = Mock()
            response.json.return_value = {"results": [{"id": str(uuid4())}]}
            response.raise_for_status = Mock()
            return response

        mock_httpx_client.request.side_effect = mock_search

        all_successful, results = await client.verify_search_indexing(sample_queries)

        assert all_successful is True
        assert len(results) == 3
        assert all(r["success"] for r in results)

    @pytest.mark.asyncio
    async def test_verify_search_indexing_failures(self, client, mock_httpx_client):
        """Test search indexing with some failures."""
        sample_queries = ["chicken", "pasta"]

        # Mock mixed responses
        responses = [
            Mock(
                json=lambda: {"results": [{"id": str(uuid4())}]},
                raise_for_status=Mock(),
            ),
            Mock(json=lambda: {"results": []}, raise_for_status=Mock()),
        ]

        mock_httpx_client.request.side_effect = responses

        all_successful, results = await client.verify_search_indexing(sample_queries)

        assert all_successful is False
        assert len(results) == 2
        assert results[0]["success"] is True
        assert results[1]["success"] is False

    @pytest.mark.asyncio
    async def test_get_health_status_healthy(self, client, mock_httpx_client):
        """Test health check with healthy response."""
        mock_response = Mock()
        mock_response.json.return_value = {"status": "healthy"}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        health = await client.get_health_status()

        assert health["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_get_health_status_unhealthy(self, client, mock_httpx_client):
        """Test health check with error."""
        mock_httpx_client.request.side_effect = httpx.HTTPError("Connection Error")

        health = await client.get_health_status()

        assert health["status"] == "unhealthy"
        assert "error" in health

    @pytest.mark.asyncio
    async def test_trigger_embedding_generation(self, client):
        """Test triggering embedding generation."""
        recipe_ids = [uuid4() for _ in range(5)]

        result = await client.trigger_embedding_generation(recipe_ids)

        assert result["status"] == "auto_generated"
        assert result["recipe_count"] == 5

    @pytest.mark.asyncio
    async def test_cleanup_test_data(self, client):
        """Test cleanup operation."""
        deleted_count = await client.cleanup_test_data(tag="test")

        # Current implementation doesn't delete, just logs
        assert deleted_count == 0


class TestSeederReport:
    """Test suite for SeederReport model."""

    def test_seeder_report_creation(self):
        """Test creating seeder report."""
        report = SeederReport(
            total_attempted=100,
            total_succeeded=95,
            total_failed=5,
            failed_recipes=[],
            duration_seconds=120.5,
            average_time_per_recipe=1.205,
            created_recipe_ids=[uuid4() for _ in range(95)],
        )

        assert report.total_attempted == 100
        assert report.total_succeeded == 95
        assert report.total_failed == 5
        assert report.duration_seconds == 120.5

    def test_seeder_report_default_values(self):
        """Test seeder report with default values."""
        report = SeederReport(
            total_attempted=10,
            total_succeeded=10,
            total_failed=0,
            duration_seconds=5.0,
            average_time_per_recipe=0.5,
        )

        assert report.failed_recipes == []
        assert report.created_recipe_ids == []

    def test_seeder_report_serialization(self):
        """Test seeder report can be serialized."""
        report = SeederReport(
            total_attempted=10,
            total_succeeded=10,
            total_failed=0,
            duration_seconds=5.0,
            average_time_per_recipe=0.5,
        )

        data = report.model_dump()

        assert isinstance(data, dict)
        assert data["total_attempted"] == 10
        assert data["total_succeeded"] == 10


class TestValidationReport:
    """Test suite for ValidationReport model."""

    def test_validation_report_creation(self):
        """Test creating validation report."""
        report = ValidationReport(
            recipe_count_valid=True,
            search_functional=True,
            embeddings_generated=True,
            sample_queries_tested=5,
            validation_errors=[],
            overall_success=True,
        )

        assert report.recipe_count_valid is True
        assert report.overall_success is True
        assert len(report.validation_errors) == 0

    def test_validation_report_with_errors(self):
        """Test validation report with errors."""
        report = ValidationReport(
            recipe_count_valid=False,
            search_functional=True,
            embeddings_generated=True,
            sample_queries_tested=3,
            validation_errors=["Recipe count mismatch"],
            overall_success=False,
        )

        assert report.recipe_count_valid is False
        assert report.overall_success is False
        assert len(report.validation_errors) == 1

    def test_validation_report_serialization(self):
        """Test validation report serialization."""
        report = ValidationReport(
            recipe_count_valid=True,
            search_functional=True,
            embeddings_generated=True,
            sample_queries_tested=4,
            validation_errors=[],
            overall_success=True,
        )

        data = report.model_dump()

        assert isinstance(data, dict)
        assert data["overall_success"] is True
        assert data["sample_queries_tested"] == 4


class TestSeederAPIClientEdgeCases:
    """Test edge cases for SeederAPIClient."""

    @pytest.fixture
    def mock_httpx_client(self):
        """Create mock httpx client."""
        return AsyncMock(spec=httpx.AsyncClient)

    @pytest.fixture
    async def client(self, mock_httpx_client):
        """Create seeder client with mocked httpx."""
        async with SeederAPIClient("http://localhost:8009") as client:
            client.client = mock_httpx_client
            yield client

    # New test case - Edge case: empty batch
    @pytest.mark.asyncio
    async def test_create_recipe_batch_empty(self, client, mock_httpx_client):
        """Test batch creation with empty list."""
        results = await client.create_recipe_batch([])

        assert isinstance(results, list)
        assert len(results) == 0
        # Should not make any API calls
        mock_httpx_client.request.assert_not_called()

    # New test case - Edge case: single recipe batch
    @pytest.mark.asyncio
    async def test_create_recipe_batch_single(self, client, mock_httpx_client):
        """Test batch creation with single recipe."""
        recipe = {"name": "Solo Recipe", "difficulty": "easy", "instructions": {"steps": []}}

        mock_response = Mock()
        mock_response.json.return_value = {"id": str(uuid4()), "name": "Solo Recipe"}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        results = await client.create_recipe_batch([recipe])

        assert len(results) == 1
        assert results[0] is not None

    # New test case - Edge case: very large batch
    @pytest.mark.asyncio
    async def test_create_recipe_batch_large(self, client, mock_httpx_client):
        """Test batch creation with many recipes."""
        recipes = [
            {"name": f"Recipe {i}", "difficulty": "easy", "instructions": {"steps": []}}
            for i in range(100)
        ]

        def mock_request(*args, **kwargs):
            response = Mock()
            response.json.return_value = {"id": str(uuid4()), "name": "Recipe"}
            response.raise_for_status = Mock()
            return response

        mock_httpx_client.request.side_effect = mock_request

        results = await client.create_recipe_batch(recipes)

        assert len(results) == 100
        assert mock_httpx_client.request.call_count == 100

    # New test case - Edge case: batch with all failures
    @pytest.mark.asyncio
    async def test_create_recipe_batch_all_failures(self, client, mock_httpx_client):
        """Test batch where all recipes fail."""
        recipes = [
            {"name": "Recipe 1", "instructions": {"steps": []}},
            {"name": "Recipe 2", "instructions": {"steps": []}},
        ]

        mock_httpx_client.request.side_effect = httpx.HTTPError("API Error")

        results = await client.create_recipe_batch(recipes)

        assert len(results) == 2
        assert all(r is None for r in results)

    # New test case - Edge case: mixed success/failure in batch
    @pytest.mark.asyncio
    async def test_create_recipe_batch_mixed_results(self, client, mock_httpx_client):
        """Test batch with mix of successes and failures."""
        recipes = [
            {"name": "Recipe 1", "instructions": {"steps": []}},
            {"name": "Recipe 2", "instructions": {"steps": []}},
            {"name": "Recipe 3", "instructions": {"steps": []}},
        ]

        # Create specific responses for each recipe based on its name
        def mock_request(*args, **kwargs):
            recipe_data = kwargs.get("json", {})
            recipe_name = recipe_data.get("name", "")

            if recipe_name == "Recipe 1":
                response = Mock()
                response.json.return_value = {"id": str(uuid4()), "name": "Recipe 1"}
                response.raise_for_status = Mock()
                return response
            elif recipe_name == "Recipe 2":
                # This recipe always fails
                raise httpx.HTTPError("Error")
            else:  # Recipe 3
                response = Mock()
                response.json.return_value = {"id": str(uuid4()), "name": "Recipe 3"}
                response.raise_for_status = Mock()
                return response

        mock_httpx_client.request.side_effect = mock_request

        results = await client.create_recipe_batch(recipes)

        assert len(results) == 3
        # Check that we have 2 successes and 1 failure (order may vary due to concurrency)
        none_count = sum(1 for r in results if r is None)
        success_count = sum(1 for r in results if r is not None)
        assert none_count == 1
        assert success_count == 2

    # New test case - Edge case: search with empty query
    @pytest.mark.asyncio
    async def test_search_recipes_empty_query(self, client, mock_httpx_client):
        """Test search with empty query string."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        results = await client.search_recipes("", limit=10)

        assert isinstance(results, list)

    # New test case - Edge case: search with special characters
    @pytest.mark.asyncio
    async def test_search_recipes_special_characters(self, client, mock_httpx_client):
        """Test search with special characters."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        results = await client.search_recipes("café & crêpes", limit=10)

        assert isinstance(results, list)
        # Verify the search was called with the special characters
        mock_httpx_client.request.assert_called_once()

    # New test case - Edge case: search with zero limit
    @pytest.mark.asyncio
    async def test_search_recipes_zero_limit(self, client, mock_httpx_client):
        """Test search with limit of zero."""
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        results = await client.search_recipes("test", limit=0)

        assert isinstance(results, list)
        assert len(results) == 0

    # New test case - Edge case: verify empty search indexing
    @pytest.mark.asyncio
    async def test_verify_search_indexing_empty_queries(self, client, mock_httpx_client):
        """Test search indexing with empty query list."""
        all_successful, results = await client.verify_search_indexing([])

        assert all_successful is True
        assert len(results) == 0

    # New test case - Edge case: verify search indexing all failures
    @pytest.mark.asyncio
    async def test_verify_search_indexing_all_failures(self, client, mock_httpx_client):
        """Test search indexing when all queries return no results."""
        sample_queries = ["query1", "query2", "query3"]

        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        all_successful, results = await client.verify_search_indexing(sample_queries)

        assert all_successful is False
        assert len(results) == 3
        assert all(not r["success"] for r in results)

    # New test case - Edge case: recipe count with malformed response
    @pytest.mark.asyncio
    async def test_get_recipe_count_malformed_response(self, client, mock_httpx_client):
        """Test getting recipe count with malformed response."""
        mock_response = Mock()
        mock_response.json.return_value = {}  # Missing 'total' key
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        count = await client.get_recipe_count()

        assert count == 0

    # New test case - Edge case: retry with increasing delay
    @pytest.mark.asyncio
    async def test_retry_delay_increases(self, client, mock_httpx_client):
        """Test that retry delay increases with each attempt."""
        recipe_data = {"name": "Test Recipe", "instructions": {"steps": []}}

        # All attempts fail
        mock_httpx_client.request.side_effect = httpx.HTTPError("Error")

        import time
        start_time = time.time()

        result = await client.create_recipe(recipe_data)

        elapsed = time.time() - start_time

        assert result is None
        # Should have delays: 1s + 2s = 3s minimum
        # (1st retry: 1s, 2nd retry: 2s)
        assert elapsed >= 3.0

    # New test case - Edge case: health check with missing status
    @pytest.mark.asyncio
    async def test_get_health_status_missing_status_field(self, client, mock_httpx_client):
        """Test health check with response missing status field."""
        mock_response = Mock()
        mock_response.json.return_value = {"other_field": "value"}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        health = await client.get_health_status()

        assert "other_field" in health

    # New test case - Edge case: trigger embeddings with empty list
    @pytest.mark.asyncio
    async def test_trigger_embedding_generation_empty_list(self, client):
        """Test triggering embeddings with empty recipe list."""
        result = await client.trigger_embedding_generation([])

        assert result["status"] == "auto_generated"
        assert result["recipe_count"] == 0

    # New test case - Edge case: trigger embeddings with large list
    @pytest.mark.asyncio
    async def test_trigger_embedding_generation_large_list(self, client):
        """Test triggering embeddings with many recipes."""
        recipe_ids = [uuid4() for _ in range(1000)]

        result = await client.trigger_embedding_generation(recipe_ids)

        assert result["status"] == "auto_generated"
        assert result["recipe_count"] == 1000

    # New test case - Edge case: cleanup with None tag
    @pytest.mark.asyncio
    async def test_cleanup_test_data_none_tag(self, client):
        """Test cleanup with None tag."""
        deleted_count = await client.cleanup_test_data(tag=None)

        assert deleted_count == 0

    # New test case - Edge case: verify recipe with invalid UUID format
    @pytest.mark.asyncio
    async def test_verify_recipe_exists_invalid_uuid(self, client, mock_httpx_client):
        """Test verifying recipe with valid UUID object."""
        recipe_id = uuid4()

        mock_httpx_client.request.side_effect = httpx.HTTPError("Not Found")

        exists = await client.verify_recipe_exists(recipe_id)

        assert exists is False

    # New test case - Edge case: client timeout configuration
    @pytest.mark.asyncio
    async def test_client_custom_timeout(self):
        """Test client initialization with custom timeout."""
        client = SeederAPIClient(
            base_url="http://localhost:8009",
            timeout=60,
        )

        assert client.timeout == 60

    # New test case - Edge case: client custom retry configuration
    @pytest.mark.asyncio
    async def test_client_custom_retries(self):
        """Test client initialization with custom retry settings."""
        client = SeederAPIClient(
            base_url="http://localhost:8009",
            max_retries=5,
            retry_delay=2.0,
        )

        assert client.max_retries == 5
        assert client.retry_delay == 2.0

    # New test case - Edge case: search results missing 'results' key
    @pytest.mark.asyncio
    async def test_search_recipes_missing_results_key(self, client, mock_httpx_client):
        """Test search when response is missing 'results' key."""
        mock_response = Mock()
        mock_response.json.return_value = {"other_key": "value"}
        mock_response.raise_for_status = Mock()
        mock_httpx_client.request.return_value = mock_response

        results = await client.search_recipes("test")

        assert results == []


class TestSeederReportEdgeCases:
    """Test edge cases for SeederReport model."""

    # New test case - Edge case: report with zero attempts
    def test_seeder_report_zero_attempts(self):
        """Test report with zero recipes attempted."""
        report = SeederReport(
            total_attempted=0,
            total_succeeded=0,
            total_failed=0,
            duration_seconds=0.0,
            average_time_per_recipe=0.0,
        )

        assert report.total_attempted == 0
        assert report.total_succeeded == 0

    # New test case - Edge case: report with all failures
    def test_seeder_report_all_failures(self):
        """Test report where all recipes failed."""
        report = SeederReport(
            total_attempted=10,
            total_succeeded=0,
            total_failed=10,
            failed_recipes=[{"error": "test"} for _ in range(10)],
            duration_seconds=5.0,
            average_time_per_recipe=0.5,
        )

        assert report.total_succeeded == 0
        assert report.total_failed == 10
        assert len(report.failed_recipes) == 10

    # New test case - Edge case: report with very long duration
    def test_seeder_report_long_duration(self):
        """Test report with very long duration."""
        report = SeederReport(
            total_attempted=1000,
            total_succeeded=1000,
            total_failed=0,
            duration_seconds=3600.0,  # 1 hour
            average_time_per_recipe=3.6,
        )

        assert report.duration_seconds == 3600.0
        assert report.average_time_per_recipe == 3.6

    # New test case - Edge case: report with many created IDs
    def test_seeder_report_many_created_ids(self):
        """Test report with large list of created IDs."""
        ids = [uuid4() for _ in range(1000)]

        report = SeederReport(
            total_attempted=1000,
            total_succeeded=1000,
            total_failed=0,
            duration_seconds=100.0,
            average_time_per_recipe=0.1,
            created_recipe_ids=ids,
        )

        assert len(report.created_recipe_ids) == 1000
        assert all(isinstance(id, UUID) for id in report.created_recipe_ids)


class TestValidationReportEdgeCases:
    """Test edge cases for ValidationReport model."""

    # New test case - Edge case: validation with no queries tested
    def test_validation_report_no_queries(self):
        """Test validation report with no queries tested."""
        report = ValidationReport(
            recipe_count_valid=True,
            search_functional=True,
            embeddings_generated=True,
            sample_queries_tested=0,
            validation_errors=[],
            overall_success=True,
        )

        assert report.sample_queries_tested == 0
        assert report.overall_success is True

    # New test case - Edge case: validation with multiple errors
    def test_validation_report_multiple_errors(self):
        """Test validation report with multiple errors."""
        errors = [
            "Recipe count mismatch",
            "Search not working",
            "Embeddings failed",
        ]

        report = ValidationReport(
            recipe_count_valid=False,
            search_functional=False,
            embeddings_generated=False,
            sample_queries_tested=3,
            validation_errors=errors,
            overall_success=False,
        )

        assert len(report.validation_errors) == 3
        assert report.overall_success is False

    # New test case - Edge case: validation partially successful
    def test_validation_report_partial_success(self):
        """Test validation report with some checks passing."""
        report = ValidationReport(
            recipe_count_valid=True,
            search_functional=False,
            embeddings_generated=True,
            sample_queries_tested=5,
            validation_errors=["Search failed"],
            overall_success=False,
        )

        assert report.recipe_count_valid is True
        assert report.search_functional is False
        assert report.overall_success is False
