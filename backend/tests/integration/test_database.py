"""Integration tests for PostgreSQL database connection."""

import asyncio

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import init_db, close_db, get_db


class TestDatabaseConnection:
    """Test suite for PostgreSQL database connectivity."""

    @pytest.mark.asyncio
    async def test_init_db(self):
        """Test database initialization."""
        await init_db()
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_database_connection(self):
        """Test that database connection can be established."""
        await init_db()

        async for session in get_db():
            assert isinstance(session, AsyncSession)
            assert session is not None
            break

    @pytest.mark.asyncio
    async def test_database_query(self):
        """Test executing a simple query."""
        await init_db()

        async for session in get_db():
            result = await session.execute(text("SELECT 1 as value"))
            row = result.fetchone()

            assert row is not None
            assert row[0] == 1
            break

    @pytest.mark.asyncio
    async def test_database_version(self):
        """Test checking PostgreSQL version."""
        await init_db()

        async for session in get_db():
            result = await session.execute(text("SELECT version()"))
            version = result.scalar()

            assert version is not None
            assert "PostgreSQL" in version
            break

    @pytest.mark.asyncio
    async def test_pgvector_extension(self):
        """Test that pgvector extension is available."""
        await init_db()

        async for session in get_db():
            # Check if pgvector extension exists or can be created
            result = await session.execute(
                text(
                    """
                    SELECT 1 FROM pg_available_extensions
                    WHERE name = 'vector'
                    """
                )
            )
            extension_available = result.scalar()

            # Extension should be available in ankane/pgvector image
            assert extension_available is not None
            break

    @pytest.mark.asyncio
    async def test_transaction_rollback(self):
        """Test transaction rollback on error."""
        await init_db()

        try:
            async for session in get_db():
                # This should cause a rollback
                await session.execute(text("SELECT * FROM nonexistent_table"))
                await session.commit()
        except Exception:
            # Expected to fail
            pass

        # Connection should still be valid after rollback
        async for session in get_db():
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            break

    @pytest.mark.asyncio
    async def test_multiple_sessions(self):
        """Test that multiple sessions can be created."""
        await init_db()

        sessions = []
        async for session in get_db():
            sessions.append(session)
            break

        async for session in get_db():
            sessions.append(session)
            break

        # Should have two different session instances
        assert len(sessions) == 2
        assert sessions[0] is not sessions[1]

    @pytest.mark.asyncio
    async def test_close_db(self):
        """Test database cleanup."""
        await init_db()
        await close_db()
        # Should not raise any exceptions

    @pytest.mark.asyncio
    async def test_database_error_handling(self):
        """Test proper error handling for invalid queries."""
        await init_db()

        with pytest.raises(Exception):
            async for session in get_db():
                await session.execute(text("INVALID SQL QUERY"))
                break

    @pytest.mark.asyncio
    async def test_database_reconnection(self):
        """Test that database can be reinitialized after closing."""
        await init_db()
        await close_db()
        await init_db()

        async for session in get_db():
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            break

        await close_db()

    # New test case: Test concurrent database queries with separate sessions
    @pytest.mark.asyncio
    async def test_concurrent_database_queries(self):
        """Test executing multiple concurrent queries with separate sessions."""
        await init_db()

        async def execute_query(value: int):
            async for session in get_db():
                result = await session.execute(text(f"SELECT {value} as value"))
                return result.scalar()

        # Execute queries concurrently with separate sessions
        results = await asyncio.gather(
            execute_query(1),
            execute_query(2),
            execute_query(3),
        )

        assert results == [1, 2, 3]

    # New test case: Test database current timestamp
    @pytest.mark.asyncio
    async def test_database_current_timestamp(self):
        """Test retrieving current timestamp from database."""
        await init_db()

        async for session in get_db():
            result = await session.execute(text("SELECT CURRENT_TIMESTAMP"))
            timestamp = result.scalar()

            assert timestamp is not None
            break

    # New test case: Test database supports JSON operations
    @pytest.mark.asyncio
    async def test_database_json_support(self):
        """Test that database supports JSON operations."""
        await init_db()

        async for session in get_db():
            # Test JSON building and parsing
            result = await session.execute(
                text("SELECT jsonb_build_object('key', 'value') as json_data")
            )
            json_data = result.scalar()

            assert json_data is not None
            assert 'key' in json_data
            assert json_data['key'] == 'value'
            break

    # New test case: Test database string concatenation
    @pytest.mark.asyncio
    async def test_database_string_operations(self):
        """Test database string concatenation and operations."""
        await init_db()

        async for session in get_db():
            result = await session.execute(
                text("SELECT 'Hello' || ' ' || 'World' as greeting")
            )
            greeting = result.scalar()

            assert greeting == "Hello World"
            break

    # New test case: Test database mathematical operations
    @pytest.mark.asyncio
    async def test_database_math_operations(self):
        """Test database mathematical operations."""
        await init_db()

        async for session in get_db():
            result = await session.execute(
                text("SELECT 5 + 10 as sum, 10 * 2 as product, 100 / 4 as division")
            )
            row = result.fetchone()

            assert row[0] == 15  # sum
            assert row[1] == 20  # product
            assert row[2] == 25  # division
            break

    # New test case: Test database supports CASE statements
    @pytest.mark.asyncio
    async def test_database_case_statement(self):
        """Test database CASE statement support."""
        await init_db()

        async for session in get_db():
            result = await session.execute(
                text("""
                    SELECT CASE
                        WHEN 1 = 1 THEN 'true'
                        ELSE 'false'
                    END as result
                """)
            )
            case_result = result.scalar()

            assert case_result == "true"
            break

    # New test case: Test database array operations
    @pytest.mark.asyncio
    async def test_database_array_support(self):
        """Test database array operations."""
        await init_db()

        async for session in get_db():
            result = await session.execute(
                text("SELECT ARRAY[1, 2, 3, 4, 5] as numbers")
            )
            numbers = result.scalar()

            assert numbers == [1, 2, 3, 4, 5]
            break

    # New test case: Test database generates UUIDs
    @pytest.mark.asyncio
    async def test_database_uuid_generation(self):
        """Test database UUID generation."""
        await init_db()

        async for session in get_db():
            result = await session.execute(text("SELECT gen_random_uuid() as uuid"))
            uuid_value = result.scalar()

            assert uuid_value is not None
            # UUID should be 36 characters (including dashes)
            assert len(str(uuid_value)) == 36
            break

    # New test case: Test database supports subqueries
    @pytest.mark.asyncio
    async def test_database_subquery(self):
        """Test database subquery support."""
        await init_db()

        async for session in get_db():
            result = await session.execute(
                text("SELECT (SELECT 42) as subquery_result")
            )
            subquery_value = result.scalar()

            assert subquery_value == 42
            break

    # New test case: Test database NULL handling
    @pytest.mark.asyncio
    async def test_database_null_handling(self):
        """Test database NULL value handling."""
        await init_db()

        async for session in get_db():
            result = await session.execute(
                text("SELECT NULL as null_value, COALESCE(NULL, 'default') as coalesce_value")
            )
            row = result.fetchone()

            assert row[0] is None
            assert row[1] == "default"
            break

    # New test case: Test database DISTINCT functionality
    @pytest.mark.asyncio
    async def test_database_distinct(self):
        """Test database DISTINCT functionality."""
        await init_db()

        async for session in get_db():
            result = await session.execute(
                text("""
                    SELECT DISTINCT value
                    FROM (VALUES (1), (2), (2), (3), (3), (3)) AS t(value)
                """)
            )
            distinct_values = [row[0] for row in result.fetchall()]

            assert sorted(distinct_values) == [1, 2, 3]
            break

    # New test case: Test database UNION operations
    @pytest.mark.asyncio
    async def test_database_union(self):
        """Test database UNION operations."""
        await init_db()

        async for session in get_db():
            result = await session.execute(
                text("""
                    SELECT 1 as value
                    UNION
                    SELECT 2 as value
                    UNION
                    SELECT 3 as value
                """)
            )
            values = [row[0] for row in result.fetchall()]

            assert sorted(values) == [1, 2, 3]
            break

    # New test case: Test database LIMIT and OFFSET
    @pytest.mark.asyncio
    async def test_database_limit_offset(self):
        """Test database LIMIT and OFFSET functionality."""
        await init_db()

        async for session in get_db():
            result = await session.execute(
                text("""
                    SELECT value
                    FROM (VALUES (1), (2), (3), (4), (5)) AS t(value)
                    ORDER BY value
                    LIMIT 2 OFFSET 2
                """)
            )
            values = [row[0] for row in result.fetchall()]

            assert values == [3, 4]
            break

    # New test case: Test database ORDER BY
    @pytest.mark.asyncio
    async def test_database_order_by(self):
        """Test database ORDER BY functionality."""
        await init_db()

        async for session in get_db():
            # Test ascending order
            result = await session.execute(
                text("""
                    SELECT value
                    FROM (VALUES (3), (1), (4), (1), (5)) AS t(value)
                    ORDER BY value ASC
                """)
            )
            asc_values = [row[0] for row in result.fetchall()]

            assert asc_values == [1, 1, 3, 4, 5]

            # Test descending order
            result = await session.execute(
                text("""
                    SELECT value
                    FROM (VALUES (3), (1), (4), (1), (5)) AS t(value)
                    ORDER BY value DESC
                """)
            )
            desc_values = [row[0] for row in result.fetchall()]

            assert desc_values == [5, 4, 3, 1, 1]
            break

    # New test case: Test database aggregate functions
    @pytest.mark.asyncio
    async def test_database_aggregate_functions(self):
        """Test database aggregate functions (COUNT, SUM, AVG, MIN, MAX)."""
        await init_db()

        async for session in get_db():
            result = await session.execute(
                text("""
                    SELECT
                        COUNT(*) as count,
                        SUM(value) as sum,
                        AVG(value) as avg,
                        MIN(value) as min,
                        MAX(value) as max
                    FROM (VALUES (1), (2), (3), (4), (5)) AS t(value)
                """)
            )
            row = result.fetchone()

            assert row[0] == 5    # count
            assert row[1] == 15   # sum
            assert row[2] == 3    # avg
            assert row[3] == 1    # min
            assert row[4] == 5    # max
            break

    # New test case: Test session isolation
    @pytest.mark.asyncio
    async def test_session_isolation(self):
        """Test that different sessions are isolated."""
        await init_db()

        # Create a temporary table in one session (will be rolled back)
        try:
            async for session1 in get_db():
                await session1.execute(
                    text("CREATE TEMPORARY TABLE temp_test (id INT)")
                )
                await session1.commit()
                break

            # Try to access it from another session (should fail)
            async for session2 in get_db():
                with pytest.raises(Exception):
                    await session2.execute(text("SELECT * FROM temp_test"))
                break
        except Exception:
            # Expected to fail, cleanup
            pass

    # New test case: Test database connection string encoding
    @pytest.mark.asyncio
    async def test_database_encoding(self):
        """Test database connection uses UTF-8 encoding."""
        await init_db()

        async for session in get_db():
            result = await session.execute(text("SHOW server_encoding"))
            encoding = result.scalar()

            assert encoding.upper() == "UTF8"
            break

    # New test case: Test database supports CTEs (Common Table Expressions)
    @pytest.mark.asyncio
    async def test_database_cte(self):
        """Test database supports Common Table Expressions."""
        await init_db()

        async for session in get_db():
            result = await session.execute(
                text("""
                    WITH numbers AS (
                        SELECT generate_series(1, 5) AS num
                    )
                    SELECT SUM(num) as total FROM numbers
                """)
            )
            total = result.scalar()

            assert total == 15  # Sum of 1+2+3+4+5
            break

    # New test case: Test database session commit and rollback
    @pytest.mark.asyncio
    async def test_explicit_commit_and_rollback(self):
        """Test explicit commit and rollback behavior."""
        await init_db()

        async for session in get_db():
            # Commit should work without errors
            await session.commit()

            # Rollback should work without errors
            await session.rollback()

            # Session should still be usable
            result = await session.execute(text("SELECT 1"))
            assert result.scalar() == 1
            break
