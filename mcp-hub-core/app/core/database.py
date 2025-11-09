"""Database initialization and management for MCP Hub Core."""

import os
import sqlite3
from contextlib import closing
from typing import Any, Dict, List

DB_PATH = os.getenv("MCP_DB_PATH", "mcp.db")


def _ensure_db_directory(path: str) -> None:
    """Ensure the directory for the SQLite database exists."""

    directory = os.path.dirname(os.path.abspath(path))
    if directory and not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def _get_sqlite_uri(path: str) -> str:
    """Return a sqlite URI for the provided path."""

    return f"sqlite:///{os.path.abspath(path)}"


def init_db() -> None:
    """Initialize the MCP database with required tables."""

    try:
        _ensure_db_directory(DB_PATH)

        with closing(sqlite3.connect(DB_PATH)) as conn, closing(conn.cursor()) as cursor:
            # Create servers table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    uri TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create tools table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_name TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    parameters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_name) REFERENCES servers (name),
                    UNIQUE (server_name, name)
                )
            ''')

            # Create resources table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_name TEXT NOT NULL,
                    name TEXT NOT NULL,
                    uri TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_name) REFERENCES servers (name),
                    UNIQUE (server_name, name)
                )
            ''')

            # Insert default servers if they don't exist
            default_servers = [
                ("sqlite", _get_sqlite_uri(DB_PATH), 1),
                ("filesystem", "file:///", 1),
                ("memory", "memory://", 1),
            ]

            for server in default_servers:
                cursor.execute('''
                    INSERT OR IGNORE INTO servers (name, uri, enabled)
                    VALUES (?, ?, ?)
                ''', server)

            # Insert default tools
            default_tools = [
                ("sqlite", "query_database", "Execute SQL queries on the database", '{"query": {"type": "string", "required": true}}'),
                ("sqlite", "list_tables", "List all tables in the database", "{}"),
                ("sqlite", "describe_table", "Get table schema information", '{"table_name": {"type": "string", "required": true}}'),
                (
                    "sqlite",
                    "get_table_data",
                    "Get sample data from a table",
                    '{"table_name": {"type": "string", "required": true}, "limit": {"type": "integer", "default": 10}}',
                ),
                ("filesystem", "read_file", "Read contents of a file", '{"path": {"type": "string", "required": true}}'),
                (
                    "filesystem",
                    "write_file",
                    "Write content to a file",
                    '{"path": {"type": "string", "required": true}, "content": {"type": "string", "required": true}}',
                ),
                ("filesystem", "list_directory", "List files and directories", '{"path": {"type": "string", "required": true}}'),
                (
                    "memory",
                    "store_memory",
                    "Store information in memory",
                    '{"key": {"type": "string", "required": true}, "value": {"type": "string", "required": true}}',
                ),
                ("memory", "retrieve_memory", "Retrieve information from memory", '{"key": {"type": "string", "required": true}}'),
                ("memory", "list_memories", "List all stored memories", "{}"),
            ]

            for tool in default_tools:
                cursor.execute('''
                    INSERT OR IGNORE INTO tools (server_name, name, description, parameters)
                    VALUES (?, ?, ?, ?)
                ''', tool)

            # Insert default resources
            default_resources = [
                ("sqlite", "mcp_database", _get_sqlite_uri(DB_PATH)),
                ("filesystem", "file_system", "/"),
                ("memory", "memory_store", "memory://"),
            ]

            for resource in default_resources:
                cursor.execute('''
                    INSERT OR IGNORE INTO resources (server_name, name, uri)
                    VALUES (?, ?, ?)
                ''', resource)

            conn.commit()

        print("✅ Database initialized successfully")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise


def get_connection() -> sqlite3.Connection:
    """Get database connection."""

    _ensure_db_directory(DB_PATH)
    return sqlite3.connect(DB_PATH)


def execute_query(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Execute a query and return results as list of dictionaries."""

    try:
        with closing(get_connection()) as conn, closing(conn.cursor()) as cursor:
            cursor.execute(query, params)

            # Get column names
            columns = [description[0] for description in cursor.description] if cursor.description else []

            # Fetch results
            rows = cursor.fetchall()

            # Convert to list of dictionaries
            results: List[Dict[str, Any]] = []
            for row in rows:
                results.append(dict(zip(columns, row)))

            return results

    except Exception as e:
        print(f"Database query error: {e}")
        return []


def execute_update(query: str, params: tuple = ()) -> int:
    """Execute an update query and return number of affected rows."""

    try:
        with closing(get_connection()) as conn, closing(conn.cursor()) as cursor:
            cursor.execute(query, params)
            conn.commit()
            affected_rows = cursor.rowcount
            return affected_rows

    except Exception as e:
        print(f"Database update error: {e}")
        return 0
