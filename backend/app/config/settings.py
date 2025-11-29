"""Application settings and configuration management."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All settings are loaded from the .env file located at the project root.
    Implements validation for database connections, Redis, and Gemini API credentials.
    """

    # Determine the project root directory and .env file path
    _project_root = Path(__file__).resolve().parent.parent.parent
    _env_file = _project_root / ".env"

    model_config = SettingsConfigDict(
        env_file=str(_env_file),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application Settings
    app_name: str = Field(default="Recipe Management API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode flag")
    environment: str = Field(default="production", description="Environment (development/staging/production)")

    # Database Settings
    database_url: PostgresDsn = Field(
        ...,
        description="PostgreSQL database URL with async driver (asyncpg)"
    )
    database_pool_size: int = Field(default=5, ge=1, le=50, description="Database connection pool size")
    database_max_overflow: int = Field(default=10, ge=0, le=50, description="Max overflow for connection pool")
    database_pool_timeout: int = Field(default=30, ge=1, description="Connection pool timeout in seconds")
    database_pool_recycle: int = Field(default=3600, ge=60, description="Connection recycle time in seconds")
    database_echo: bool = Field(default=False, description="Echo SQL statements")

    # Redis Settings
    redis_url: RedisDsn = Field(
        ...,
        description="Redis connection URL"
    )
    redis_max_connections: int = Field(default=10, ge=1, le=100, description="Max Redis connections")
    redis_socket_timeout: int = Field(default=5, ge=1, description="Redis socket timeout in seconds")
    redis_socket_connect_timeout: int = Field(default=5, ge=1, description="Redis socket connect timeout")
    redis_decode_responses: bool = Field(default=True, description="Decode Redis responses to strings")

    # Cache TTL Settings
    cache_ttl_default: int = Field(default=3600, ge=0, description="Default cache TTL in seconds (1 hour)")
    cache_ttl_search: int = Field(default=900, ge=0, description="Search results cache TTL (15 minutes)")
    cache_ttl_embedding: int = Field(default=86400, ge=0, description="Embedding cache TTL (24 hours)")
    cache_ttl_stats: int = Field(default=300, ge=0, description="Stats cache TTL (5 minutes)")

    # Gemini API Settings
    gemini_api_key: str = Field(..., description="Google Gemini API key")
    gemini_embedding_model: str = Field(
        default="models/text-embedding-004",
        description="Gemini embedding model name"
    )
    gemini_text_model: str = Field(
        default="gemini-2.0-flash-exp",
        description="Gemini text generation model name"
    )
    gemini_rate_limit_rpm: int = Field(
        default=60,
        ge=1,
        description="Gemini API rate limit (requests per minute)"
    )
    gemini_timeout: int = Field(default=30, ge=1, description="Gemini API timeout in seconds")
    gemini_max_retries: int = Field(default=3, ge=0, description="Max retry attempts for Gemini API")

    # API Settings
    api_host: str = Field(default="0.0.0.0", description="API host")
    api_port: int = Field(default=8009, ge=1, le=65535, description="API port")
    api_prefix: str = Field(default="/api/v1", description="API prefix for all endpoints")

    # Security Settings
    secret_key: str = Field(..., min_length=32, description="Secret key for JWT and encryption")

    # Logging Settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="json",
        description="Log format (json/text)"
    )

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is one of the allowed values."""
        allowed_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in allowed_levels:
            raise ValueError(f"Log level must be one of {allowed_levels}")
        return v_upper

    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment is one of the allowed values."""
        allowed_envs = {"development", "staging", "production"}
        v_lower = v.lower()
        if v_lower not in allowed_envs:
            raise ValueError(f"Environment must be one of {allowed_envs}")
        return v_lower

    @field_validator("log_format")
    @classmethod
    def validate_log_format(cls, v: str) -> str:
        """Validate log format is one of the allowed values."""
        allowed_formats = {"json", "text"}
        v_lower = v.lower()
        if v_lower not in allowed_formats:
            raise ValueError(f"Log format must be one of {allowed_formats}")
        return v_lower

    @property
    def database_url_sync(self) -> str:
        """Get synchronous database URL (for Alembic migrations).

        Returns:
            Database URL with psycopg driver instead of asyncpg
        """
        url = str(self.database_url)
        # Replace asyncpg with psycopg for synchronous operations
        if "+asyncpg" in url:
            return url.replace("+asyncpg", "+psycopg")
        elif "postgresql://" in url and "+psycopg" not in url:
            # Handle case where URL doesn't have a specific driver
            return url.replace("postgresql://", "postgresql+psycopg://")
        return url

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.

    This function uses lru_cache to ensure settings are only loaded once
    and reused across the application lifecycle.

    Returns:
        Settings instance with validated configuration
    """
    return Settings()
