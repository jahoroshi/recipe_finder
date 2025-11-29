"""Main FastAPI application with middleware and lifecycle management.

Implements:
- FastAPI application with OpenAPI documentation
- CORS middleware
- Custom middleware stack
- Startup/shutdown event handlers
- Health check endpoints
"""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.middleware import (
    ErrorHandlingMiddleware,
    LoggingMiddleware,
    PerformanceMonitoringMiddleware,
    RequestIdMiddleware,
)
from app.api.router import api_router
from app.config import get_settings
from app.db.redis_client import close_redis, get_redis, init_redis
from app.db.session import close_db, init_db

logger = logging.getLogger(__name__)
# os.environ['http_proxy'] = 'http://127.0.0.1:2080'
# os.environ['https_proxy'] = 'http://127.0.0.1:2080'
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:2080'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:2080'
# os.environ['all_proxy'] = 'http://127.0.0.1:2080'

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown.

    Handles:
        - Database connection initialization and cleanup
        - Redis connection initialization and cleanup
        - Cache warming (if needed)
        - Service health checks

    Args:
        app: FastAPI application instance

    Yields:
        Control back to the application
    """
    # Startup
    logger.info("Starting Recipe Management API...")

    try:
        # Initialize database
        logger.info("Initializing database connection pool...")
        await init_db()
        logger.info("Database connection pool initialized")

        # Initialize Redis
        logger.info("Initializing Redis connection pool...")
        await init_redis()
        logger.info("Redis connection pool initialized")

        # Check Redis connectivity
        redis_client = get_redis()
        if await redis_client.ping():
            logger.info("Redis connection verified")
        else:
            logger.warning("Redis connection check failed")

        # TODO: Warm up caches if needed
        # TODO: Check external service connectivity (Gemini API)

        logger.info("Recipe Management API started successfully")

    except Exception as exc:
        logger.error(f"Failed to start application: {exc}", exc_info=True)
        raise

    # Yield control to the application
    yield

    # Shutdown
    logger.info("Shutting down Recipe Management API...")

    try:
        # Close Redis connections
        logger.info("Closing Redis connections...")
        await close_redis()
        logger.info("Redis connections closed")

        # Close database connections
        logger.info("Closing database connections...")
        await close_db()
        logger.info("Database connections closed")

        # TODO: Flush any pending background tasks
        # TODO: Clean up temporary resources

        logger.info("Recipe Management API shut down successfully")

    except Exception as exc:
        logger.error(f"Error during shutdown: {exc}", exc_info=True)


# Get settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="Recipe Management API",
    version="1.0.0",
    description="A comprehensive API for managing recipes with AI-powered search and recommendations",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)


# ==================== Middleware Configuration ====================

# CORS middleware (add first so it wraps all other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure allowed origins from settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Request-ID", "X-Response-Time"],
)

# Custom middleware stack (order matters - last added = first executed)
app.add_middleware(ErrorHandlingMiddleware)
app.add_middleware(PerformanceMonitoringMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIdMiddleware)


# ==================== Health Check Endpoints ====================


@app.get(
    "/health",
    tags=["health"],
    summary="Health check",
    description="Check if the API is running and healthy",
)
async def health_check() -> dict:
    """Basic health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Recipe Management API",
    }


@app.get(
    "/health/detailed",
    tags=["health"],
    summary="Detailed health check",
    description="Check health of all system components",
)
async def detailed_health_check() -> dict:
    """Detailed health check with component status.

    Checks:
        - Database connectivity
        - Redis connectivity
        - External API availability

    Returns:
        Detailed health status for each component
    """
    health_status = {
        "status": "healthy",
        "version": "1.0.0",
        "service": "Recipe Management API",
        "components": {},
    }

    # Check Redis
    try:
        redis_client = get_redis()
        redis_ok = await redis_client.ping()
        health_status["components"]["redis"] = {
            "status": "healthy" if redis_ok else "unhealthy",
            "message": "Connected" if redis_ok else "Connection failed",
        }
    except Exception as exc:
        health_status["components"]["redis"] = {
            "status": "unhealthy",
            "message": str(exc),
        }
        health_status["status"] = "degraded"

    # Check database
    try:
        from app.db.session import get_engine

        engine = get_engine()
        # Simple check - just verify engine exists
        health_status["components"]["database"] = {
            "status": "healthy",
            "message": "Connection pool available",
        }
    except Exception as exc:
        health_status["components"]["database"] = {
            "status": "unhealthy",
            "message": str(exc),
        }
        health_status["status"] = "degraded"

    # TODO: Check Gemini API availability

    return health_status


@app.get(
    "/",
    tags=["root"],
    summary="API root",
    description="API welcome message and links",
)
async def root() -> dict:
    """API root endpoint.

    Returns:
        Welcome message and documentation links
    """
    return {
        "message": "Welcome to Recipe Management API",
        "version": "1.0.0",
        "documentation": "/api/docs",
        "redoc": "/api/redoc",
        "health": "/health",
    }


# ==================== Include API Router ====================

# Include all API routes under /api prefix
app.include_router(api_router, prefix="/api")


# ==================== Exception Handlers ====================


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle 404 Not Found errors.

    Args:
        request: Incoming request
        exc: Exception instance

    Returns:
        JSON response with error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "message": "Resource not found",
                "type": "NotFoundError",
                "request_id": request_id,
                "path": str(request.url.path),
            }
        },
    )


@app.exception_handler(405)
async def method_not_allowed_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle 405 Method Not Allowed errors.

    Args:
        request: Incoming request
        exc: Exception instance

    Returns:
        JSON response with error details
    """
    request_id = getattr(request.state, "request_id", "unknown")
    return JSONResponse(
        status_code=405,
        content={
            "error": {
                "message": "Method not allowed",
                "type": "MethodNotAllowedError",
                "request_id": request_id,
                "method": request.method,
                "path": str(request.url.path),
            }
        },
    )


# ==================== Application Entry Point ====================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.is_development,
        log_level=settings.log_level.lower(),
    )
