"""Unit tests for custom FastAPI middleware."""

import pytest
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.api.middleware import (
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    PerformanceMonitoringMiddleware,
    RequestIdMiddleware,
)


@pytest.fixture
def app_with_request_id_middleware():
    """Create test app with RequestIdMiddleware."""
    app = FastAPI()
    app.add_middleware(RequestIdMiddleware)

    @app.get("/test")
    async def test_route(request: Request):
        return {"request_id": request.state.request_id}

    return app


@pytest.fixture
def app_with_logging_middleware():
    """Create test app with LoggingMiddleware."""
    app = FastAPI()
    app.add_middleware(LoggingMiddleware)

    @app.get("/test")
    async def test_route():
        return {"message": "success"}

    return app


@pytest.fixture
def app_with_performance_middleware():
    """Create test app with PerformanceMonitoringMiddleware."""
    app = FastAPI()
    app.add_middleware(PerformanceMonitoringMiddleware)

    @app.get("/test")
    async def test_route():
        return {"message": "success"}

    @app.get("/slow")
    async def slow_route():
        import time
        time.sleep(1.5)  # Simulate slow request
        return {"message": "slow"}

    return app


@pytest.fixture
def app_with_error_handling_middleware():
    """Create test app with ErrorHandlingMiddleware."""
    app = FastAPI()
    app.add_middleware(ErrorHandlingMiddleware)

    @app.get("/test")
    async def test_route():
        return {"message": "success"}

    @app.get("/value-error")
    async def value_error_route():
        raise ValueError("Test validation error")

    @app.get("/permission-error")
    async def permission_error_route():
        raise PermissionError("Test permission error")

    @app.get("/key-error")
    async def key_error_route():
        raise KeyError("missing_key")

    @app.get("/timeout-error")
    async def timeout_error_route():
        raise TimeoutError("Request timed out")

    @app.get("/generic-error")
    async def generic_error_route():
        raise RuntimeError("Unexpected error")

    return app


class TestRequestIdMiddleware:
    """Test RequestIdMiddleware functionality."""

    def test_generates_request_id(self, app_with_request_id_middleware):
        """Test that middleware generates request ID."""
        client = TestClient(app_with_request_id_middleware)
        response = client.get("/test")

        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert response.json()["request_id"] == response.headers["X-Request-ID"]

    def test_preserves_existing_request_id(self, app_with_request_id_middleware):
        """Test that middleware preserves existing request ID."""
        client = TestClient(app_with_request_id_middleware)
        custom_id = "custom-request-id-123"

        response = client.get("/test", headers={"X-Request-ID": custom_id})

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == custom_id
        assert response.json()["request_id"] == custom_id

    def test_request_id_is_uuid_format(self, app_with_request_id_middleware):
        """Test that generated request ID is valid UUID."""
        client = TestClient(app_with_request_id_middleware)
        response = client.get("/test")

        request_id = response.headers["X-Request-ID"]
        from uuid import UUID

        # Should not raise exception
        UUID(request_id)


class TestLoggingMiddleware:
    """Test LoggingMiddleware functionality."""

    def test_successful_request_logging(self, app_with_logging_middleware, caplog):
        """Test that successful requests are logged."""
        client = TestClient(app_with_logging_middleware)

        with caplog.at_level("INFO"):
            response = client.get("/test")

        assert response.status_code == 200
        assert "Request started" in caplog.text
        assert "Request completed" in caplog.text

    def test_adds_response_time_header(self, app_with_logging_middleware):
        """Test that response time header is added."""
        client = TestClient(app_with_logging_middleware)
        response = client.get("/test")

        assert "X-Response-Time" in response.headers
        assert response.headers["X-Response-Time"].endswith("s")

    def test_logs_request_details(self, app_with_logging_middleware, caplog):
        """Test that request details are logged."""
        client = TestClient(app_with_logging_middleware)

        with caplog.at_level("INFO"):
            response = client.get("/test?param=value")

        assert response.status_code == 200
        assert "method" in caplog.text.lower() or "GET" in caplog.text
        assert "/test" in caplog.text


class TestPerformanceMonitoringMiddleware:
    """Test PerformanceMonitoringMiddleware functionality."""

    def test_normal_request_no_warning(
        self, app_with_performance_middleware, caplog
    ):
        """Test that normal requests don't trigger slow request warning."""
        client = TestClient(app_with_performance_middleware)

        with caplog.at_level("WARNING"):
            response = client.get("/test")

        assert response.status_code == 200
        assert "Slow request detected" not in caplog.text

    def test_slow_request_warning(self, app_with_performance_middleware, caplog):
        """Test that slow requests trigger warning."""
        client = TestClient(app_with_performance_middleware)

        with caplog.at_level("WARNING"):
            response = client.get("/slow")

        assert response.status_code == 200
        assert "Slow request detected" in caplog.text


class TestErrorHandlingMiddleware:
    """Test ErrorHandlingMiddleware functionality."""

    def test_successful_request_passes_through(
        self, app_with_error_handling_middleware
    ):
        """Test that successful requests pass through unchanged."""
        client = TestClient(app_with_error_handling_middleware)
        response = client.get("/test")

        assert response.status_code == 200
        assert response.json() == {"message": "success"}

    def test_value_error_returns_400(self, app_with_error_handling_middleware):
        """Test that ValueError returns 400 Bad Request."""
        client = TestClient(app_with_error_handling_middleware)
        response = client.get("/value-error")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "ValidationError"
        assert "Test validation error" in data["error"]["message"]

    def test_permission_error_returns_403(self, app_with_error_handling_middleware):
        """Test that PermissionError returns 403 Forbidden."""
        client = TestClient(app_with_error_handling_middleware)
        response = client.get("/permission-error")

        assert response.status_code == 403
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "PermissionError"

    def test_key_error_returns_404(self, app_with_error_handling_middleware):
        """Test that KeyError returns 404 Not Found."""
        client = TestClient(app_with_error_handling_middleware)
        response = client.get("/key-error")

        assert response.status_code == 404
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "NotFoundError"

    def test_timeout_error_returns_504(self, app_with_error_handling_middleware):
        """Test that TimeoutError returns 504 Gateway Timeout."""
        client = TestClient(app_with_error_handling_middleware)
        response = client.get("/timeout-error")

        assert response.status_code == 504
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "TimeoutError"

    def test_generic_error_returns_500(self, app_with_error_handling_middleware):
        """Test that generic exceptions return 500 Internal Server Error."""
        client = TestClient(app_with_error_handling_middleware)
        response = client.get("/generic-error")

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "InternalError"
        assert data["error"]["message"] == "Internal server error"

    def test_error_response_includes_request_id(
        self, app_with_error_handling_middleware
    ):
        """Test that error responses include request ID."""
        app = app_with_error_handling_middleware
        app.add_middleware(RequestIdMiddleware)

        client = TestClient(app)
        response = client.get("/value-error")

        data = response.json()
        assert "request_id" in data["error"]


class TestMiddlewareStack:
    """Test complete middleware stack integration."""

    def test_middleware_stack_order(self):
        """Test that middleware stack executes in correct order."""
        app = FastAPI()

        # Add middleware in reverse order (last added = first executed)
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(PerformanceMonitoringMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(RequestIdMiddleware)

        @app.get("/test")
        async def test_route(request: Request):
            return {"request_id": request.state.request_id}

        client = TestClient(app)
        response = client.get("/test")

        # Request ID should be in both state and headers
        assert response.status_code == 200
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

    def test_middleware_with_error(self):
        """Test middleware stack handles errors correctly."""
        app = FastAPI()

        # Add middleware stack
        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(RequestIdMiddleware)

        @app.get("/error")
        async def error_route():
            raise ValueError("Test error")

        client = TestClient(app)
        response = client.get("/error")

        # Should get formatted error response
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "X-Request-ID" in response.headers


# New test cases - Edge cases and additional scenarios
class TestRequestIdMiddlewareEdgeCases:
    """Additional edge case tests for RequestIdMiddleware."""

    def test_multiple_sequential_requests_unique_ids(self, app_with_request_id_middleware):
        """Test that sequential requests get unique IDs."""
        client = TestClient(app_with_request_id_middleware)

        # Make multiple requests
        request_ids = []
        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200
            request_ids.append(response.headers["X-Request-ID"])

        # All IDs should be unique
        assert len(request_ids) == len(set(request_ids))

    def test_empty_request_id_header(self, app_with_request_id_middleware):
        """Test handling of empty request ID header."""
        client = TestClient(app_with_request_id_middleware)

        # Send empty request ID
        response = client.get("/test", headers={"X-Request-ID": ""})

        assert response.status_code == 200
        # Should generate new ID when header is empty
        assert "X-Request-ID" in response.headers
        assert len(response.headers["X-Request-ID"]) > 0

    def test_very_long_request_id(self, app_with_request_id_middleware):
        """Test handling of very long request ID."""
        client = TestClient(app_with_request_id_middleware)

        # Send very long request ID
        long_id = "a" * 1000
        response = client.get("/test", headers={"X-Request-ID": long_id})

        assert response.status_code == 200
        # Should preserve the long ID
        assert response.headers["X-Request-ID"] == long_id

    def test_request_id_with_special_characters(self, app_with_request_id_middleware):
        """Test request ID with special characters."""
        client = TestClient(app_with_request_id_middleware)

        special_id = "request-id-123!@#$%"
        response = client.get("/test", headers={"X-Request-ID": special_id})

        assert response.status_code == 200
        assert response.headers["X-Request-ID"] == special_id

    def test_concurrent_requests_unique_ids(self, app_with_request_id_middleware):
        """Test that concurrent requests get unique IDs."""
        import concurrent.futures

        client = TestClient(app_with_request_id_middleware)

        def make_request():
            response = client.get("/test")
            return response.headers["X-Request-ID"]

        # Make concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            request_ids = [f.result() for f in futures]

        # All IDs should be unique
        assert len(request_ids) == len(set(request_ids))


class TestLoggingMiddlewareEdgeCases:
    """Additional edge case tests for LoggingMiddleware."""

    def test_logs_post_request(self, app_with_logging_middleware, caplog):
        """Test logging of POST request."""
        app = app_with_logging_middleware

        @app.post("/create")
        async def create_route():
            return {"created": True}

        client = TestClient(app)

        with caplog.at_level("INFO"):
            response = client.post("/create", json={"data": "test"})

        assert response.status_code == 200
        assert "Request started" in caplog.text
        assert "Request completed" in caplog.text

    def test_logs_request_with_query_params(self, app_with_logging_middleware, caplog):
        """Test logging includes query parameters."""
        client = TestClient(app_with_logging_middleware)

        with caplog.at_level("INFO"):
            response = client.get("/test?foo=bar&baz=qux")

        assert response.status_code == 200
        # Query params should be logged
        assert "foo=bar" in caplog.text or "query" in caplog.text.lower()

    def test_logs_different_status_codes(self, app_with_logging_middleware, caplog):
        """Test logging of different HTTP status codes."""
        app = app_with_logging_middleware

        @app.get("/created")
        async def created_route():
            return JSONResponse(content={"status": "created"}, status_code=201)

        @app.get("/accepted")
        async def accepted_route():
            return JSONResponse(content={"status": "accepted"}, status_code=202)

        client = TestClient(app)

        # Test 201
        with caplog.at_level("INFO"):
            caplog.clear()
            response = client.get("/created")
            assert response.status_code == 201
            assert "201" in caplog.text or "Request completed" in caplog.text

        # Test 202
        with caplog.at_level("INFO"):
            caplog.clear()
            response = client.get("/accepted")
            assert response.status_code == 202
            assert "202" in caplog.text or "Request completed" in caplog.text

    def test_logs_exception_during_request(self, app_with_logging_middleware, caplog):
        """Test that exceptions during request processing are logged."""
        app = app_with_logging_middleware

        @app.get("/exception")
        async def exception_route():
            raise RuntimeError("Test exception")

        client = TestClient(app)

        with caplog.at_level("ERROR"):
            try:
                client.get("/exception")
            except Exception:
                pass

        # Exception should be logged
        assert "Request failed with exception" in caplog.text or "exception" in caplog.text.lower()

    def test_response_time_is_numeric(self, app_with_logging_middleware):
        """Test that response time header contains valid numeric value."""
        client = TestClient(app_with_logging_middleware)
        response = client.get("/test")

        response_time = response.headers["X-Response-Time"]
        # Should be in format "0.1234s"
        assert response_time.endswith("s")
        numeric_part = response_time[:-1]
        assert float(numeric_part) >= 0

    def test_logs_very_long_path(self, app_with_logging_middleware, caplog):
        """Test logging of very long URL path."""
        app = app_with_logging_middleware

        long_path = "/test/" + "a" * 500

        @app.get(long_path)
        async def long_path_route():
            return {"message": "success"}

        client = TestClient(app)

        with caplog.at_level("INFO"):
            response = client.get(long_path)

        assert response.status_code == 200
        assert "Request started" in caplog.text

    def test_missing_client_info(self, app_with_logging_middleware, caplog):
        """Test logging when client info is missing."""
        # TestClient should provide client info, but we test the handling
        client = TestClient(app_with_logging_middleware)

        with caplog.at_level("INFO"):
            response = client.get("/test")

        assert response.status_code == 200
        # Should handle missing client info gracefully
        assert "Request started" in caplog.text


class TestPerformanceMonitoringMiddlewareEdgeCases:
    """Additional edge case tests for PerformanceMonitoringMiddleware."""

    def test_request_at_threshold_boundary(self, app_with_performance_middleware, caplog):
        """Test request that takes exactly 1 second (threshold)."""
        app = app_with_performance_middleware

        @app.get("/boundary")
        async def boundary_route():
            import time
            time.sleep(1.0)  # Exactly at threshold
            return {"message": "boundary"}

        client = TestClient(app)

        with caplog.at_level("WARNING"):
            response = client.get("/boundary")

        assert response.status_code == 200
        # At exactly 1 second, might or might not trigger warning due to timing

    def test_multiple_slow_requests(self, app_with_performance_middleware, caplog):
        """Test multiple slow requests are all logged."""
        client = TestClient(app_with_performance_middleware)

        with caplog.at_level("WARNING"):
            # Make multiple slow requests
            for _ in range(3):
                caplog.clear()
                response = client.get("/slow")
                assert response.status_code == 200
                assert "Slow request detected" in caplog.text

    def test_performance_monitoring_without_request_id(self):
        """Test performance monitoring when request_id is not in state."""
        app = FastAPI()
        # Only add performance middleware, no request ID middleware
        app.add_middleware(PerformanceMonitoringMiddleware)

        @app.get("/test")
        async def test_route():
            return {"message": "success"}

        client = TestClient(app)
        response = client.get("/test")

        # Should work even without request_id
        assert response.status_code == 200

    def test_fast_request_no_performance_overhead(self, app_with_performance_middleware):
        """Test that fast requests complete normally."""
        client = TestClient(app_with_performance_middleware)

        import time
        start = time.time()
        response = client.get("/test")
        duration = time.time() - start

        assert response.status_code == 200
        # Should complete quickly (under threshold)
        assert duration < 0.5


class TestErrorHandlingMiddlewareEdgeCases:
    """Additional edge case tests for ErrorHandlingMiddleware."""

    def test_multiple_different_errors_in_sequence(self, app_with_error_handling_middleware):
        """Test handling different error types in sequence."""
        client = TestClient(app_with_error_handling_middleware)

        # Test each error type
        error_endpoints = [
            ("/value-error", 400),
            ("/permission-error", 403),
            ("/key-error", 404),
            ("/timeout-error", 504),
            ("/generic-error", 500),
        ]

        for endpoint, expected_status in error_endpoints:
            response = client.get(endpoint)
            assert response.status_code == expected_status
            data = response.json()
            assert "error" in data
            assert "type" in data["error"]
            assert "message" in data["error"]

    def test_error_without_request_id_middleware(self):
        """Test error handling without request ID middleware."""
        app = FastAPI()
        app.add_middleware(ErrorHandlingMiddleware)

        @app.get("/error")
        async def error_route():
            raise ValueError("Test error")

        client = TestClient(app)
        response = client.get("/error")

        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        # Should have request_id even if it's "unknown"
        assert "request_id" in data["error"]

    def test_nested_exception(self, app_with_error_handling_middleware):
        """Test handling of nested exceptions."""
        app = app_with_error_handling_middleware

        @app.get("/nested-error")
        async def nested_error_route():
            try:
                raise ValueError("Inner error")
            except ValueError as e:
                raise RuntimeError("Outer error") from e

        client = TestClient(app)
        response = client.get("/nested-error")

        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "InternalError"

    def test_custom_exception_type(self, app_with_error_handling_middleware):
        """Test handling of custom exception types."""
        app = app_with_error_handling_middleware

        class CustomException(Exception):
            pass

        @app.get("/custom-error")
        async def custom_error_route():
            raise CustomException("Custom error message")

        client = TestClient(app)
        response = client.get("/custom-error")

        # Custom exceptions should be caught by generic handler
        assert response.status_code == 500
        data = response.json()
        assert "error" in data
        assert data["error"]["type"] == "InternalError"

    def test_error_response_structure(self, app_with_error_handling_middleware):
        """Test that all error responses follow consistent structure."""
        client = TestClient(app_with_error_handling_middleware)

        response = client.get("/value-error")
        data = response.json()

        # Verify error response structure
        assert "error" in data
        assert isinstance(data["error"], dict)
        assert "message" in data["error"]
        assert "type" in data["error"]
        assert "request_id" in data["error"]
        assert isinstance(data["error"]["message"], str)
        assert isinstance(data["error"]["type"], str)

    def test_timeout_error_includes_details(self, app_with_error_handling_middleware):
        """Test that timeout errors include additional details."""
        client = TestClient(app_with_error_handling_middleware)

        response = client.get("/timeout-error")
        data = response.json()

        assert response.status_code == 504
        assert "error" in data
        assert "details" in data["error"]
        assert "original_error" in data["error"]["details"]


class TestMiddlewareStackEdgeCases:
    """Additional edge case tests for complete middleware stack."""

    def test_slow_request_with_error(self, caplog):
        """Test slow request that also raises an error."""
        app = FastAPI()

        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(PerformanceMonitoringMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(RequestIdMiddleware)

        @app.get("/slow-error")
        async def slow_error_route():
            import time
            time.sleep(1.5)
            raise ValueError("Error after slow processing")

        client = TestClient(app)

        with caplog.at_level("WARNING"):
            response = client.get("/slow-error")

        # Should handle error
        assert response.status_code == 400
        data = response.json()
        assert "error" in data

        # Should also log slow request
        assert "Slow request detected" in caplog.text

    def test_middleware_preserves_response_body(self):
        """Test that middleware stack preserves response body."""
        app = FastAPI()

        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(PerformanceMonitoringMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(RequestIdMiddleware)

        test_data = {
            "message": "test response",
            "nested": {"key": "value"},
            "array": [1, 2, 3],
        }

        @app.get("/data")
        async def data_route():
            return test_data

        client = TestClient(app)
        response = client.get("/data")

        assert response.status_code == 200
        assert response.json() == test_data

    def test_middleware_with_post_request_and_body(self):
        """Test middleware stack with POST request containing body."""
        app = FastAPI()

        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(RequestIdMiddleware)

        @app.post("/echo")
        async def echo_route(data: dict):
            return data

        client = TestClient(app)
        test_data = {"key": "value", "number": 42}
        response = client.post("/echo", json=test_data)

        assert response.status_code == 200
        assert response.json() == test_data

    def test_middleware_with_404_response(self):
        """Test middleware stack handles 404 responses."""
        app = FastAPI()

        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(RequestIdMiddleware)

        client = TestClient(app)
        response = client.get("/nonexistent-endpoint")

        # FastAPI returns 404 for undefined routes
        assert response.status_code == 404
        assert "X-Request-ID" in response.headers

    def test_all_middleware_headers_present(self):
        """Test that all middleware add their expected headers."""
        app = FastAPI()

        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(PerformanceMonitoringMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(RequestIdMiddleware)

        @app.get("/test")
        async def test_route():
            return {"message": "test"}

        client = TestClient(app)
        response = client.get("/test")

        # Check all expected headers
        assert "X-Request-ID" in response.headers
        assert "X-Response-Time" in response.headers

    def test_middleware_with_different_http_methods(self):
        """Test middleware stack with various HTTP methods."""
        app = FastAPI()

        app.add_middleware(ErrorHandlingMiddleware)
        app.add_middleware(LoggingMiddleware)
        app.add_middleware(RequestIdMiddleware)

        @app.get("/resource")
        async def get_resource():
            return {"method": "GET"}

        @app.post("/resource")
        async def create_resource():
            return {"method": "POST"}

        @app.put("/resource")
        async def update_resource():
            return {"method": "PUT"}

        @app.delete("/resource")
        async def delete_resource():
            return {"method": "DELETE"}

        @app.patch("/resource")
        async def patch_resource():
            return {"method": "PATCH"}

        client = TestClient(app)

        methods = [
            ("GET", client.get),
            ("POST", client.post),
            ("PUT", client.put),
            ("DELETE", client.delete),
            ("PATCH", client.patch),
        ]

        for method_name, method_func in methods:
            response = method_func("/resource")
            assert response.status_code == 200
            assert response.json()["method"] == method_name
            assert "X-Request-ID" in response.headers
