"""Tests for the multi database manager utility functions."""

import asyncio
import sys
from pathlib import Path


# Ensure the application package is importable when tests run from the repo root
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))


from app.core.multi_database_manager import (  # noqa: E402  (import after sys.path mutation)
    DatabaseConfig,
    DatabaseType,
    MultiDatabaseManager,
)


def test_sqlite_query_with_dictionary_parameters(tmp_path):
    """Dictionary parameters should work for both positional and named SQLite queries."""

    async def run_test():
        manager = MultiDatabaseManager()
        db_path = tmp_path / "test.db"

        config = DatabaseConfig(
            name="test_sqlite",
            type=DatabaseType.SQLITE,
            host="localhost",
            port=0,
            database=str(db_path),
            username="",
            password="",
        )

        added = await manager.add_database(config)
        assert added is True

        # Create schema and insert data using positional placeholders with a dictionary
        await manager.execute_query(
            "test_sqlite",
            "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, category TEXT)",
        )

        await manager.execute_query(
            "test_sqlite",
            "INSERT INTO items (name, category) VALUES (?, ?)",
            {"name": "Hammer", "category": "tools"},
        )

        # Query using named placeholders
        result = await manager.execute_query(
            "test_sqlite",
            "SELECT name FROM items WHERE category = :category",
            {"category": "tools"},
        )

        assert result.success is True
        assert result.row_count == 1
        assert result.data[0]["name"] == "Hammer"

        await manager.close_all_connections()

    asyncio.run(run_test())


def test_search_across_databases_returns_results(tmp_path):
    """Search should return rows when the SQLite metadata matches the query."""

    async def run_test():
        manager = MultiDatabaseManager()
        db_path = tmp_path / "search.db"

        config = DatabaseConfig(
            name="search_sqlite",
            type=DatabaseType.SQLITE,
            host="localhost",
            port=0,
            database=str(db_path),
            username="",
            password="",
        )

        await manager.add_database(config)

        await manager.execute_query(
            "search_sqlite",
            "CREATE TABLE widgets (id INTEGER PRIMARY KEY, description TEXT)",
        )

        results = await manager.search_across_databases("widgets")

        assert "search_sqlite" in results
        assert any(row["table_name"] == "widgets" for row in results["search_sqlite"])

        await manager.close_all_connections()

    asyncio.run(run_test())
