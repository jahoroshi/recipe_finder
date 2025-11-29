"""Database session management with async SQLAlchemy."""

from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool, QueuePool

from app.config import get_settings

# Global engine instance
engine: AsyncEngine | None = None
AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get or create the async database engine.

    Returns:
        AsyncEngine instance configured with connection pooling

    Raises:
        RuntimeError: If database is not initialized
    """
    global engine

    if engine is None:
        raise RuntimeError(
            "Database engine not initialized. Call init_db() first."
        )

    return engine


async def init_db() -> None:
    """Initialize database connection pool.

    Creates async SQLAlchemy engine with proper connection pooling
    configuration based on application settings.
    """
    global engine, AsyncSessionLocal

    if engine is not None:
        return  # Already initialized

    settings = get_settings()

    # Choose pool class based on environment
    use_null_pool = settings.is_development and settings.debug

    # Create async engine with connection pooling
    if use_null_pool:
        # NullPool doesn't accept pool-related arguments
        engine = create_async_engine(
            str(settings.database_url),
            echo=settings.database_echo,
            poolclass=NullPool,
        )
    else:
        # QueuePool with proper configuration
        engine = create_async_engine(
            str(settings.database_url),
            echo=settings.database_echo,
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
            pool_timeout=settings.database_pool_timeout,
            pool_recycle=settings.database_pool_recycle,
            pool_pre_ping=True,  # Verify connections before using
            poolclass=QueuePool,
        )

    # Create session factory
    AsyncSessionLocal = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


async def close_db() -> None:
    """Close database connection pool.

    Properly disposes of the database engine and all connections.
    Should be called during application shutdown.
    """
    global engine, AsyncSessionLocal

    if engine is not None:
        await engine.dispose()
        engine = None
        AsyncSessionLocal = None


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for FastAPI to get database session.

    Yields:
        AsyncSession instance for database operations

    Raises:
        RuntimeError: If database is not initialized

    Example:
        ```python
        @app.get("/recipes")
        async def get_recipes(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(Recipe))
            return result.scalars().all()
        ```
    """
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Database not initialized. Call init_db() first."
        )

    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
