"""Pytest fixtures for database tests."""

import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings
from app.db.base import Base

settings = get_settings()


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a test database session.

    Creates a new session for each test function and rolls back all changes
    after the test completes.

    Yields:
        AsyncSession for database operations
    """
    # Create async engine
    engine = create_async_engine(
        str(settings.database_url),
        echo=False,
        pool_pre_ping=True,
    )

    # Create session factory
    async_session_factory = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

    # Create session
    async with async_session_factory() as session:
        try:
            yield session
            # Rollback the transaction after the test
            await session.rollback()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Dispose engine
    await engine.dispose()
