"""Pytest configuration and fixtures."""

import os
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    # Ensure we're using the test .env file
    env_path = Path(__file__).parent.parent / ".env"
    assert env_path.exists(), f".env file not found at {env_path}"


@pytest.fixture
def test_settings_dict():
    """Provide test settings as dictionary."""
    return {
        "app_name": "Test Recipe API",
        "app_version": "1.0.0",
        "debug": True,
        "environment": "development",
        "database_url": "postgresql+asyncpg://postgres:postgres@localhost:5438/recipes",
        "redis_url": "redis://localhost:6381/0",
        "gemini_api_key": "test-api-key-" + "x" * 32,
        "secret_key": "test-secret-key-" + "x" * 32,
        "log_level": "INFO",
    }
