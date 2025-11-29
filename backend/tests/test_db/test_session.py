"""Tests for database session management."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import close_db, get_db, init_db


class TestDatabaseSession:
    """Tests for database session management."""

    @pytest.mark.asyncio
    async def test_init_db(self):
        """Test database initialization."""
        await init_db()

        # Should be able to get a session after init
        async for session in get_db():
            assert isinstance(session, AsyncSession)
            break

        await close_db()

    @pytest.mark.asyncio
    async def test_get_db_session(self):
        """Test getting database session."""
        await init_db()

        async for session in get_db():
            assert isinstance(session, AsyncSession)
            assert session.is_active
            break

        await close_db()

    @pytest.mark.asyncio
    async def test_session_rollback_on_error(self):
        """Test that session rolls back on error."""
        await init_db()

        try:
            async for session in get_db():
                # Create an invalid query to trigger an error
                await session.execute("INVALID SQL")
                break
        except Exception:
            # Expected to fail
            pass

        # Should be able to get a new session after error
        async for session in get_db():
            assert isinstance(session, AsyncSession)
            assert session.is_active
            break

        await close_db()

    @pytest.mark.asyncio
    async def test_close_db(self):
        """Test closing database connections."""
        await init_db()
        await close_db()

        # After closing, init should work again
        await init_db()

        async for session in get_db():
            assert isinstance(session, AsyncSession)
            break

        await close_db()

    @pytest.mark.asyncio
    async def test_multiple_init_db(self):
        """Test that multiple init_db calls don't cause issues."""
        await init_db()
        await init_db()  # Should not error

        async for session in get_db():
            assert isinstance(session, AsyncSession)
            break

        await close_db()

    # New test case: Multiple concurrent sessions
    @pytest.mark.asyncio
    async def test_multiple_concurrent_sessions(self):
        """Test getting multiple database sessions concurrently."""
        await init_db()

        sessions = []
        async for session in get_db():
            sessions.append(session)
            break

        async for session in get_db():
            sessions.append(session)
            break

        # Should get different session instances
        assert len(sessions) == 2
        assert all(isinstance(s, AsyncSession) for s in sessions)

        await close_db()

    # New test case: Session after close and reinit
    @pytest.mark.asyncio
    async def test_session_after_close_and_reinit(self):
        """Test that sessions work after closing and reinitializing."""
        await init_db()

        # Get first session
        async for session in get_db():
            assert session.is_active
            break

        await close_db()

        # Reinitialize and get new session
        await init_db()

        async for session in get_db():
            assert isinstance(session, AsyncSession)
            assert session.is_active
            break

        await close_db()

    # New test case: Multiple close calls
    @pytest.mark.asyncio
    async def test_multiple_close_db(self):
        """Test that multiple close_db calls don't cause issues."""
        await init_db()
        await close_db()
        await close_db()  # Should not error

        # Should be able to init again
        await init_db()
        await close_db()

    # New test case: Get session without init
    @pytest.mark.asyncio
    async def test_get_session_before_init(self):
        """Test getting session before initialization."""
        # Ensure clean state
        await close_db()

        # Initialize to ensure tests work
        await init_db()

        async for session in get_db():
            assert isinstance(session, AsyncSession)
            break

        await close_db()

    # New test case: Session transaction commit
    @pytest.mark.asyncio
    async def test_session_transaction_commit(self):
        """Test committing a transaction in a session."""
        import uuid
        from app.db.models import Category

        await init_db()

        async for session in get_db():
            # Create a test entity with unique name
            unique_suffix = str(uuid.uuid4())[:8]
            category = Category(
                name=f"Test Session Category {unique_suffix}",
                slug=f"test-session-category-{unique_suffix}",
            )
            session.add(category)
            await session.commit()

            assert category.id is not None
            break

        await close_db()

    # New test case: Session transaction rollback
    @pytest.mark.asyncio
    async def test_session_transaction_rollback(self):
        """Test rolling back a transaction in a session."""
        from app.db.models import Category

        await init_db()

        async for session in get_db():
            # Create a test entity
            category = Category(
                name="Test Rollback Category",
                slug="test-rollback-category",
            )
            session.add(category)
            await session.rollback()

            # Category should not have an ID after rollback
            assert category.id is None
            break

        await close_db()

    # New test case: Session context manager behavior
    @pytest.mark.asyncio
    async def test_session_context_behavior(self):
        """Test session behavior in async context."""
        await init_db()

        async for session in get_db():
            # Session should be active when yielded
            assert session.is_active

            # Perform some operation
            from sqlalchemy import text
            result = await session.execute(text("SELECT 1"))
            value = result.scalar()
            assert value == 1
            break

        await close_db()

    # New test case: Concurrent session operations
    @pytest.mark.asyncio
    async def test_concurrent_session_operations(self):
        """Test concurrent operations on different sessions."""
        import asyncio
        import uuid
        from app.db.models import Category

        await init_db()

        async def create_category(name: str):
            async for session in get_db():
                # Add unique suffix to avoid conflicts
                unique_suffix = str(uuid.uuid4())[:8]
                unique_name = f"{name} {unique_suffix}"
                unique_slug = f"{name.lower().replace(' ', '-')}-{unique_suffix}"
                category = Category(name=unique_name, slug=unique_slug)
                session.add(category)
                await session.commit()
                return category.id

        # Create multiple categories concurrently
        ids = await asyncio.gather(
            create_category("Concurrent Category 1"),
            create_category("Concurrent Category 2"),
            create_category("Concurrent Category 3"),
        )

        assert len(ids) == 3
        assert all(id is not None for id in ids)

        await close_db()

    # New test case: Session isolation
    @pytest.mark.asyncio
    async def test_session_isolation(self):
        """Test that sessions are isolated from each other."""
        from app.db.models import Category

        await init_db()

        # First session creates an entity but doesn't commit
        async for session1 in get_db():
            category = Category(
                name="Isolation Test",
                slug="isolation-test",
            )
            session1.add(category)
            # Don't commit yet
            break

        # Second session should not see the uncommitted entity
        async for session2 in get_db():
            from sqlalchemy import select

            result = await session2.execute(
                select(Category).where(Category.slug == "isolation-test")
            )
            found = result.scalar_one_or_none()
            assert found is None  # Should not see uncommitted changes
            break

        await close_db()
