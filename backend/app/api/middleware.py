"""Custom middleware implementations for FastAPI application.

Provides:
- Request ID generation and propagation
- Request/Response logging with structured logging
- Performance monitoring
- Error handling and formatting
"""

import logging
import time
import uuid
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class RequestIdMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and propagate request IDs.

    Generates a unique request ID for each incoming request and adds it
    to the response headers. Also makes it available in the request state
    for logging and tracing.

    Headers:
        - X-Request-ID: Unique identifier for this request
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request and add request ID.

        Args:
            request: Incoming request
            call_next: Next middleware or route handler

        Returns:
            Response with X-Request-ID header
        """
        # Get or generate request ID
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Store in request state for access in routes/logs
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging.

    Logs:
        - Request method, path, and query parameters
        - Response status code
        - Request duration
        - Client IP address
        - User agent

    Uses structured logging for easy parsing and analysis.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request with logging.

        Args:
            request: Incoming request
            call_next: Next middleware or route handler

        Returns:
            Response from handler
        """
        # Start timer
        start_time = time.time()

        # Extract request details
        request_id = getattr(request.state, "request_id", "unknown")
        method = request.method
        path = request.url.path
        query_params = str(request.url.query) if request.url.query else ""
        client_host = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")

        # Log incoming request
        logger.info(
            "Request started",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "query": query_params,
                "client_host": client_host,
                "user_agent": user_agent,
            },
        )

        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log exception
            duration = time.time() - start_time
            logger.error(
                "Request failed with exception",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "duration_ms": round(duration * 1000, 2),
                    "error": str(exc),
                },
                exc_info=True,
            )
            raise

        # Calculate duration
        duration = time.time() - start_time

        # Log response
        logger.info(
            "Request completed",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "status_code": response.status_code,
                "duration_ms": round(duration * 1000, 2),
            },
        )

        # Add performance header
        response.headers["X-Response-Time"] = f"{duration:.4f}s"

        return response


class PerformanceMonitoringMiddleware(BaseHTTPMiddleware):
    """Middleware for performance monitoring and alerting.

    Tracks:
        - Request duration
        - Slow request detection (> 1 second)
        - Error rate tracking

    Can be extended to send metrics to monitoring services.
    """

    SLOW_REQUEST_THRESHOLD = 1.0  # seconds

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request with performance monitoring.

        Args:
            request: Incoming request
            call_next: Next middleware or route handler

        Returns:
            Response from handler
        """
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.time() - start_time

        # Log slow requests
        if duration > self.SLOW_REQUEST_THRESHOLD:
            request_id = getattr(request.state, "request_id", "unknown")
            logger.warning(
                f"Slow request detected: {request.method} {request.url.path}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                    "duration_ms": round(duration * 1000, 2),
                    "threshold_ms": self.SLOW_REQUEST_THRESHOLD * 1000,
                },
            )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """Middleware for consistent error handling and formatting.

    Catches exceptions and returns properly formatted JSON error responses.
    Ensures clients always receive consistent error structures.

    Error Response Format:
        {
            "error": {
                "message": "Error description",
                "type": "ErrorType",
                "request_id": "uuid",
                "details": {}  # Optional additional details
            }
        }
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process request with error handling.

        Args:
            request: Incoming request
            call_next: Next middleware or route handler

        Returns:
            Response or formatted error response
        """
        try:
            response = await call_next(request)
            return response

        except ValueError as exc:
            # Business logic validation errors
            request_id = getattr(request.state, "request_id", "unknown")
            return JSONResponse(
                status_code=400,
                content={
                    "error": {
                        "message": str(exc),
                        "type": "ValidationError",
                        "request_id": request_id,
                    }
                },
            )

        except PermissionError as exc:
            # Authorization errors
            request_id = getattr(request.state, "request_id", "unknown")
            return JSONResponse(
                status_code=403,
                content={
                    "error": {
                        "message": str(exc),
                        "type": "PermissionError",
                        "request_id": request_id,
                    }
                },
            )

        except KeyError as exc:
            # Resource not found errors
            request_id = getattr(request.state, "request_id", "unknown")
            return JSONResponse(
                status_code=404,
                content={
                    "error": {
                        "message": f"Resource not found: {str(exc)}",
                        "type": "NotFoundError",
                        "request_id": request_id,
                    }
                },
            )

        except TimeoutError as exc:
            # Timeout errors
            request_id = getattr(request.state, "request_id", "unknown")
            return JSONResponse(
                status_code=504,
                content={
                    "error": {
                        "message": "Request timed out",
                        "type": "TimeoutError",
                        "request_id": request_id,
                        "details": {"original_error": str(exc)},
                    }
                },
            )

        except Exception as exc:
            # Catch-all for unexpected errors
            request_id = getattr(request.state, "request_id", "unknown")
            logger.error(
                f"Unhandled exception: {str(exc)}",
                extra={
                    "request_id": request_id,
                    "method": request.method,
                    "path": request.url.path,
                },
                exc_info=True,
            )

            return JSONResponse(
                status_code=500,
                content={
                    "error": {
                        "message": "Internal server error",
                        "type": "InternalError",
                        "request_id": request_id,
                    }
                },
            )
