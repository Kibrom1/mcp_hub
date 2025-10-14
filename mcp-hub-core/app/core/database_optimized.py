"""
Optimized database management with connection pooling and proper transaction handling
"""

import sqlite3
import threading
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Generator
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Optimized database manager with connection pooling"""
    
    def __init__(self, db_path: str = 'mcp.db', max_connections: int = 10):
        self.db_path = db_path
        self.max_connections = max_connections
        self._connections = []
        self._lock = threading.Lock()
        self._initialize_database()
    
    def _initialize_database(self):
        """Initialize database with proper schema and indexes"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Enable WAL mode for better concurrency
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
            cursor.execute("PRAGMA cache_size=10000")
            cursor.execute("PRAGMA temp_store=MEMORY")
            
            # Create tables with proper indexes
            self._create_tables(cursor)
            self._create_indexes(cursor)
            self._insert_default_data(cursor)
            
            conn.commit()
    
    def _create_tables(self, cursor):
        """Create database tables with optimized schema"""
        tables = [
            '''
            CREATE TABLE IF NOT EXISTS servers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                uri TEXT NOT NULL,
                enabled BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_name TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                parameters TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_name) REFERENCES servers (name),
                UNIQUE (server_name, name)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_name TEXT NOT NULL,
                name TEXT NOT NULL,
                uri TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (server_name) REFERENCES servers (name),
                UNIQUE (server_name, name)
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT,
                message TEXT NOT NULL,
                response TEXT,
                provider TEXT,
                tokens_used INTEGER,
                response_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''',
            '''
            CREATE TABLE IF NOT EXISTS tool_executions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT NOT NULL,
                server_name TEXT NOT NULL,
                arguments TEXT,
                result TEXT,
                success BOOLEAN,
                execution_time REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            '''
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
    
    def _create_indexes(self, cursor):
        """Create database indexes for better performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_servers_name ON servers(name)",
            "CREATE INDEX IF NOT EXISTS idx_servers_enabled ON servers(enabled)",
            "CREATE INDEX IF NOT EXISTS idx_tools_server ON tools(server_name)",
            "CREATE INDEX IF NOT EXISTS idx_tools_name ON tools(name)",
            "CREATE INDEX IF NOT EXISTS idx_resources_server ON resources(server_name)",
            "CREATE INDEX IF NOT EXISTS idx_memory_key ON memory(key)",
            "CREATE INDEX IF NOT EXISTS idx_chat_history_user ON chat_history(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_chat_history_created ON chat_history(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_tool_executions_tool ON tool_executions(tool_name)",
            "CREATE INDEX IF NOT EXISTS idx_tool_executions_created ON tool_executions(created_at)"
        ]
        
        for index_sql in indexes:
            cursor.execute(index_sql)
    
    def _insert_default_data(self, cursor):
        """Insert default data with proper error handling"""
        try:
            # Default servers
            default_servers = [
                ('sqlite', 'sqlite://mcp.db', 1),
                ('filesystem', 'file:///', 1),
                ('memory', 'memory://', 1),
            ]
            
            for server in default_servers:
                cursor.execute('''
                    INSERT OR IGNORE INTO servers (name, uri, enabled)
                    VALUES (?, ?, ?)
                ''', server)
            
            # Default tools
            default_tools = [
                ('sqlite', 'query_database', 'Execute SQL queries on the database', '{"query": {"type": "string", "required": true}}'),
                ('sqlite', 'list_tables', 'List all tables in the database', '{}'),
                ('sqlite', 'describe_table', 'Get table schema information', '{"table_name": {"type": "string", "required": true}}'),
                ('sqlite', 'get_table_data', 'Get sample data from a table', '{"table_name": {"type": "string", "required": true}, "limit": {"type": "integer", "default": 10}}'),
                ('filesystem', 'read_file', 'Read contents of a file', '{"path": {"type": "string", "required": true}}'),
                ('filesystem', 'write_file', 'Write content to a file', '{"path": {"type": "string", "required": true}, "content": {"type": "string", "required": true}}'),
                ('filesystem', 'list_directory', 'List files and directories', '{"path": {"type": "string", "required": true}}'),
                ('memory', 'store_memory', 'Store information in memory', '{"key": {"type": "string", "required": true}, "value": {"type": "string", "required": true}}'),
                ('memory', 'retrieve_memory', 'Retrieve information from memory', '{"key": {"type": "string", "required": true}}'),
                ('memory', 'list_memories', 'List all stored memories', '{}'),
            ]
            
            for tool in default_tools:
                cursor.execute('''
                    INSERT OR IGNORE INTO tools (server_name, name, description, parameters)
                    VALUES (?, ?, ?, ?)
                ''', tool)
            
            # Default resources
            default_resources = [
                ('sqlite', 'mcp_database', 'sqlite://mcp.db'),
                ('filesystem', 'file_system', '/'),
                ('memory', 'memory_store', 'memory://'),
            ]
            
            for resource in default_resources:
                cursor.execute('''
                    INSERT OR IGNORE INTO resources (server_name, name, uri)
                    VALUES (?, ?, ?)
                ''', resource)
                
        except Exception as e:
            logger.error(f"Error inserting default data: {e}")
            raise
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with proper resource management"""
        conn = None
        try:
            with self._lock:
                if self._connections:
                    conn = self._connections.pop()
                else:
                    conn = sqlite3.connect(
                        self.db_path,
                        timeout=30.0,
                        check_same_thread=False
                    )
                    # Enable row factory for easier data access
                    conn.row_factory = sqlite3.Row
            
            yield conn
            
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a query and return results as list of dictionaries"""
        start_time = time.time()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                # Get column names
                columns = [description[0] for description in cursor.description] if cursor.description else []
                
                # Fetch results
                rows = cursor.fetchall()
                
                # Convert to list of dictionaries
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                execution_time = time.time() - start_time
                logger.debug(f"Query executed in {execution_time:.3f}s: {query[:100]}...")
                
                return results
                
        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """Execute an update query and return number of affected rows"""
        start_time = time.time()
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                conn.commit()
                affected_rows = cursor.rowcount
                
                execution_time = time.time() - start_time
                logger.debug(f"Update executed in {execution_time:.3f}s: {query[:100]}...")
                
                return affected_rows
                
        except Exception as e:
            logger.error(f"Database update error: {e}")
            raise
    
    def execute_transaction(self, queries: List[tuple]) -> bool:
        """Execute multiple queries in a transaction"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                for query, params in queries:
                    cursor.execute(query, params)
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Transaction error: {e}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        try:
            stats = {}
            
            # Table counts
            tables = ['servers', 'tools', 'resources', 'memory', 'chat_history', 'tool_executions']
            for table in tables:
                result = self.execute_query(f"SELECT COUNT(*) as count FROM {table}")
                stats[f"{table}_count"] = result[0]['count'] if result else 0
            
            # Database size
            result = self.execute_query("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
            stats['database_size'] = result[0]['size'] if result else 0
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {}

# Global database manager instance
db_manager = DatabaseManager()

# Decorator for database operations
def with_database(func):
    """Decorator for database operations with proper error handling"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database operation failed in {func.__name__}: {e}")
            raise
    return wrapper
