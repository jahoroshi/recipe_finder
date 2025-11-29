"""Unit tests for configuration management."""

import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.config.settings import Settings, get_settings


class TestSettings:
    """Test suite for Settings class."""

    def test_settings_load_from_env_file(self):
        """Test that settings load correctly from .env file."""
        settings = get_settings()

        assert settings.app_name == "Recipe Management API"
        assert settings.app_version == "1.0.0"
        assert isinstance(settings.debug, bool)
        assert settings.environment in ["development", "staging", "production"]

    def test_database_url_validation(self):
        """Test database URL is valid PostgreSQL URL with asyncpg."""
        settings = get_settings()

        assert str(settings.database_url).startswith("postgresql+asyncpg://")
        assert "localhost:5438" in str(settings.database_url)
        assert "recipes" in str(settings.database_url)

    def test_database_url_sync_property(self):
        """Test synchronous database URL removes asyncpg driver."""
        settings = get_settings()

        sync_url = settings.database_url_sync
        assert "+asyncpg" not in sync_url
        assert sync_url.startswith("postgresql://")

    def test_redis_url_validation(self):
        """Test Redis URL is valid."""
        settings = get_settings()

        assert str(settings.redis_url).startswith("redis://")
        assert "localhost:6381" in str(settings.redis_url)

    def test_gemini_api_key_required(self):
        """Test Gemini API key is loaded from environment."""
        settings = get_settings()

        assert settings.gemini_api_key
        assert len(settings.gemini_api_key) > 0

    def test_secret_key_validation(self):
        """Test secret key meets minimum length requirement."""
        settings = get_settings()

        assert settings.secret_key
        assert len(settings.secret_key) >= 32

    def test_log_level_validation(self):
        """Test log level is valid."""
        settings = get_settings()

        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        assert settings.log_level in valid_levels

    def test_environment_validation(self):
        """Test environment is valid."""
        settings = get_settings()

        valid_envs = {"development", "staging", "production"}
        assert settings.environment in valid_envs

    def test_database_pool_settings(self):
        """Test database pool settings have valid values."""
        settings = get_settings()

        assert 1 <= settings.database_pool_size <= 50
        assert 0 <= settings.database_max_overflow <= 50
        assert settings.database_pool_timeout >= 1
        assert settings.database_pool_recycle >= 60

    def test_redis_connection_settings(self):
        """Test Redis connection settings have valid values."""
        settings = get_settings()

        assert 1 <= settings.redis_max_connections <= 100
        assert settings.redis_socket_timeout >= 1
        assert settings.redis_socket_connect_timeout >= 1

    def test_cache_ttl_settings(self):
        """Test cache TTL settings are non-negative."""
        settings = get_settings()

        assert settings.cache_ttl_default >= 0
        assert settings.cache_ttl_search >= 0
        assert settings.cache_ttl_embedding >= 0
        assert settings.cache_ttl_stats >= 0

    def test_gemini_rate_limit_settings(self):
        """Test Gemini API rate limit settings."""
        settings = get_settings()

        assert settings.gemini_rate_limit_rpm >= 1
        assert settings.gemini_timeout >= 1
        assert settings.gemini_max_retries >= 0

    def test_api_settings(self):
        """Test API configuration settings."""
        settings = get_settings()

        assert settings.api_host
        assert 1 <= settings.api_port <= 65535
        assert settings.api_prefix.startswith("/")

    def test_is_development_property(self):
        """Test is_development property."""
        settings = get_settings()

        if settings.environment == "development":
            assert settings.is_development
            assert not settings.is_production
        else:
            assert not settings.is_development

    def test_is_production_property(self):
        """Test is_production property."""
        settings = get_settings()

        if settings.environment == "production":
            assert settings.is_production
            assert not settings.is_development
        else:
            assert not settings.is_production

    def test_settings_caching(self):
        """Test that get_settings returns cached instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_invalid_log_level_raises_error(self, monkeypatch):
        """Test that invalid log level raises validation error."""
        monkeypatch.setenv("LOG_LEVEL", "INVALID")

        # Clear cache
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "log_level" in str(exc_info.value).lower()

        # Restore valid value
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        get_settings.cache_clear()

    def test_invalid_environment_raises_error(self, monkeypatch):
        """Test that invalid environment raises validation error."""
        monkeypatch.setenv("ENVIRONMENT", "invalid")

        # Clear cache
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "environment" in str(exc_info.value).lower()

        # Restore valid value
        monkeypatch.setenv("ENVIRONMENT", "development")
        get_settings.cache_clear()

    def test_gemini_model_names(self):
        """Test Gemini model names are configured."""
        settings = get_settings()

        assert settings.gemini_embedding_model
        assert settings.gemini_text_model
        assert "embed" in settings.gemini_embedding_model.lower() or "text" in settings.gemini_embedding_model.lower()

    # New test case: Test invalid database pool size
    def test_invalid_database_pool_size_raises_error(self, monkeypatch):
        """Test that invalid database pool size raises validation error."""
        # Test pool size too small
        monkeypatch.setenv("DATABASE_POOL_SIZE", "0")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "database_pool_size" in str(exc_info.value).lower()

        # Test pool size too large
        monkeypatch.setenv("DATABASE_POOL_SIZE", "51")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "database_pool_size" in str(exc_info.value).lower()

        # Restore valid value
        monkeypatch.setenv("DATABASE_POOL_SIZE", "5")
        get_settings.cache_clear()

    # New test case: Test invalid API port
    def test_invalid_api_port_raises_error(self, monkeypatch):
        """Test that invalid API port raises validation error."""
        # Test port too small
        monkeypatch.setenv("API_PORT", "0")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "api_port" in str(exc_info.value).lower()

        # Test port too large
        monkeypatch.setenv("API_PORT", "65536")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "api_port" in str(exc_info.value).lower()

        # Restore valid value
        monkeypatch.setenv("API_PORT", "8009")
        get_settings.cache_clear()

    # New test case: Test secret key minimum length
    def test_secret_key_too_short_raises_error(self, monkeypatch):
        """Test that secret key below minimum length raises validation error."""
        monkeypatch.setenv("SECRET_KEY", "short")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "secret_key" in str(exc_info.value).lower()

        # Restore valid value (at least 32 chars)
        monkeypatch.setenv("SECRET_KEY", "a" * 32)
        get_settings.cache_clear()

    # New test case: Test invalid log format
    def test_invalid_log_format_raises_error(self, monkeypatch):
        """Test that invalid log format raises validation error."""
        monkeypatch.setenv("LOG_FORMAT", "xml")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "log_format" in str(exc_info.value).lower()

        # Restore valid value
        monkeypatch.setenv("LOG_FORMAT", "json")
        get_settings.cache_clear()

    # New test case: Test cache TTL boundary values
    def test_cache_ttl_negative_value_raises_error(self, monkeypatch):
        """Test that negative cache TTL raises validation error."""
        monkeypatch.setenv("CACHE_TTL_DEFAULT", "-1")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "cache_ttl_default" in str(exc_info.value).lower()

        # Restore valid value
        monkeypatch.setenv("CACHE_TTL_DEFAULT", "3600")
        get_settings.cache_clear()

    # New test case: Test zero cache TTL is valid
    def test_cache_ttl_zero_is_valid(self, monkeypatch):
        """Test that zero cache TTL is valid (no caching)."""
        monkeypatch.setenv("CACHE_TTL_DEFAULT", "0")
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.cache_ttl_default == 0

        # Restore default
        monkeypatch.setenv("CACHE_TTL_DEFAULT", "3600")
        get_settings.cache_clear()

    # New test case: Test database pool timeout boundary
    def test_database_pool_timeout_minimum(self, monkeypatch):
        """Test that database pool timeout must be at least 1."""
        monkeypatch.setenv("DATABASE_POOL_TIMEOUT", "0")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "database_pool_timeout" in str(exc_info.value).lower()

        # Restore valid value
        monkeypatch.setenv("DATABASE_POOL_TIMEOUT", "30")
        get_settings.cache_clear()

    # New test case: Test database pool recycle minimum
    def test_database_pool_recycle_minimum(self, monkeypatch):
        """Test that database pool recycle must be at least 60 seconds."""
        monkeypatch.setenv("DATABASE_POOL_RECYCLE", "59")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "database_pool_recycle" in str(exc_info.value).lower()

        # Restore valid value
        monkeypatch.setenv("DATABASE_POOL_RECYCLE", "3600")
        get_settings.cache_clear()

    # New test case: Test Redis max connections boundary
    def test_redis_max_connections_boundary(self, monkeypatch):
        """Test Redis max connections boundary validation."""
        # Test too small
        monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "0")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "redis_max_connections" in str(exc_info.value).lower()

        # Test too large
        monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "101")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "redis_max_connections" in str(exc_info.value).lower()

        # Restore valid value
        monkeypatch.setenv("REDIS_MAX_CONNECTIONS", "10")
        get_settings.cache_clear()

    # New test case: Test Gemini rate limit minimum
    def test_gemini_rate_limit_minimum(self, monkeypatch):
        """Test that Gemini rate limit must be at least 1."""
        monkeypatch.setenv("GEMINI_RATE_LIMIT_RPM", "0")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "gemini_rate_limit_rpm" in str(exc_info.value).lower()

        # Restore valid value
        monkeypatch.setenv("GEMINI_RATE_LIMIT_RPM", "60")
        get_settings.cache_clear()

    # New test case: Test Gemini timeout minimum
    def test_gemini_timeout_minimum(self, monkeypatch):
        """Test that Gemini timeout must be at least 1 second."""
        monkeypatch.setenv("GEMINI_TIMEOUT", "0")
        get_settings.cache_clear()

        with pytest.raises(ValidationError) as exc_info:
            get_settings()

        assert "gemini_timeout" in str(exc_info.value).lower()

        # Restore valid value
        monkeypatch.setenv("GEMINI_TIMEOUT", "30")
        get_settings.cache_clear()

    # New test case: Test environment case insensitivity
    def test_environment_case_insensitive(self, monkeypatch):
        """Test that environment value is case insensitive."""
        # Test uppercase
        monkeypatch.setenv("ENVIRONMENT", "PRODUCTION")
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.environment == "production"

        # Test mixed case
        monkeypatch.setenv("ENVIRONMENT", "DeVeLoPmEnT")
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.environment == "development"

        # Restore default
        monkeypatch.setenv("ENVIRONMENT", "development")
        get_settings.cache_clear()

    # New test case: Test log level case insensitivity
    def test_log_level_case_insensitive(self, monkeypatch):
        """Test that log level value is case insensitive."""
        # Test lowercase
        monkeypatch.setenv("LOG_LEVEL", "debug")
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.log_level == "DEBUG"

        # Test mixed case
        monkeypatch.setenv("LOG_LEVEL", "WaRnInG")
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.log_level == "WARNING"

        # Restore default
        monkeypatch.setenv("LOG_LEVEL", "INFO")
        get_settings.cache_clear()

    # New test case: Test API prefix must start with slash
    def test_api_prefix_format(self):
        """Test that API prefix starts with forward slash."""
        settings = get_settings()

        assert settings.api_prefix.startswith("/")
        assert not settings.api_prefix.endswith("/")

    # New test case: Test database URL contains required components
    def test_database_url_components(self):
        """Test that database URL contains all required components."""
        settings = get_settings()

        db_url = str(settings.database_url)
        assert "postgresql" in db_url
        assert "+asyncpg" in db_url
        assert "@" in db_url  # Has credentials
        assert ":" in db_url  # Has port

    # New test case: Test Redis URL components
    def test_redis_url_components(self):
        """Test that Redis URL contains all required components."""
        settings = get_settings()

        redis_url = str(settings.redis_url)
        assert redis_url.startswith("redis://")
        assert ":" in redis_url  # Has port

    # New test case: Test debug flag type
    def test_debug_flag_is_boolean(self):
        """Test that debug flag is a boolean."""
        settings = get_settings()

        assert isinstance(settings.debug, bool)

    # New test case: Test database echo flag type
    def test_database_echo_is_boolean(self):
        """Test that database echo flag is a boolean."""
        settings = get_settings()

        assert isinstance(settings.database_echo, bool)

    # New test case: Test Redis decode responses flag type
    def test_redis_decode_responses_is_boolean(self):
        """Test that Redis decode responses flag is a boolean."""
        settings = get_settings()

        assert isinstance(settings.redis_decode_responses, bool)

    # New test case: Test all required fields are present
    def test_all_required_fields_present(self):
        """Test that all required configuration fields are present."""
        settings = get_settings()

        # Test required fields
        assert settings.database_url is not None
        assert settings.redis_url is not None
        assert settings.gemini_api_key is not None
        assert settings.secret_key is not None

    # New test case: Test staging environment
    def test_staging_environment_properties(self, monkeypatch):
        """Test properties for staging environment."""
        monkeypatch.setenv("ENVIRONMENT", "staging")
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.environment == "staging"
        assert not settings.is_development
        assert not settings.is_production

        # Restore default
        monkeypatch.setenv("ENVIRONMENT", "development")
        get_settings.cache_clear()

    # New test case: Test Gemini max retries can be zero
    def test_gemini_max_retries_zero_is_valid(self, monkeypatch):
        """Test that Gemini max retries can be zero (no retries)."""
        monkeypatch.setenv("GEMINI_MAX_RETRIES", "0")
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.gemini_max_retries == 0

        # Restore default
        monkeypatch.setenv("GEMINI_MAX_RETRIES", "3")
        get_settings.cache_clear()

    # New test case: Test all cache TTL settings are independent
    def test_cache_ttl_settings_independence(self, monkeypatch):
        """Test that different cache TTL settings are independent."""
        monkeypatch.setenv("CACHE_TTL_DEFAULT", "1000")
        monkeypatch.setenv("CACHE_TTL_SEARCH", "2000")
        monkeypatch.setenv("CACHE_TTL_EMBEDDING", "3000")
        monkeypatch.setenv("CACHE_TTL_STATS", "4000")
        get_settings.cache_clear()

        settings = get_settings()
        assert settings.cache_ttl_default == 1000
        assert settings.cache_ttl_search == 2000
        assert settings.cache_ttl_embedding == 3000
        assert settings.cache_ttl_stats == 4000

        # Restore defaults
        monkeypatch.setenv("CACHE_TTL_DEFAULT", "3600")
        monkeypatch.setenv("CACHE_TTL_SEARCH", "900")
        monkeypatch.setenv("CACHE_TTL_EMBEDDING", "86400")
        monkeypatch.setenv("CACHE_TTL_STATS", "300")
        get_settings.cache_clear()
