"""
Multi-Database Manager for MCP Hub
Supports multiple database connections and routing
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional, Union
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum
import sqlite3
import json
from datetime import datetime

# Optional imports for database drivers
try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    logging.warning("asyncpg not available, PostgreSQL async support disabled")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    logging.warning("psycopg2 not available, PostgreSQL sync support disabled")

try:
    import aiomysql
    AIOMYSQL_AVAILABLE = True
except ImportError:
    AIOMYSQL_AVAILABLE = False
    logging.warning("aiomysql not available, MySQL async support disabled")

logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    MYSQL = "mysql"
    MONGODB = "mongodb"

@dataclass
class DatabaseConfig:
    """Database configuration"""
    name: str
    type: DatabaseType
    host: str
    port: int
    database: str
    username: str
    password: str
    connection_string: Optional[str] = None
    is_active: bool = True
    max_connections: int = 10
    timeout: int = 30

@dataclass
class QueryResult:
    """Query execution result"""
    database_name: str
    query: str
    data: List[Dict[str, Any]]
    columns: List[str]
    row_count: int
    execution_time: float
    success: bool
    error: Optional[str] = None

class MultiDatabaseManager:
    """Manages multiple database connections"""
    
    def __init__(self):
        self.connections: Dict[str, Any] = {}
        self.configs: Dict[str, DatabaseConfig] = {}
        self.connection_pools: Dict[str, Any] = {}
        self._lock = asyncio.Lock()
    
    async def add_database(self, config: DatabaseConfig) -> bool:
        """Add a new database connection"""
        try:
            async with self._lock:
                if config.name in self.configs:
                    logger.warning(f"Database {config.name} already exists")
                    return False
                
                self.configs[config.name] = config
                
                # Create connection based on type
                if config.type == DatabaseType.POSTGRESQL:
                    await self._setup_postgresql(config)
                elif config.type == DatabaseType.SQLITE:
                    await self._setup_sqlite(config)
                elif config.type == DatabaseType.MYSQL:
                    await self._setup_mysql(config)
                else:
                    logger.error(f"Unsupported database type: {config.type}")
                    return False
                
                logger.info(f"Database {config.name} added successfully")
                return True
                
        except Exception as e:
            logger.error(f"Failed to add database {config.name}: {e}")
            return False
    
    async def _setup_postgresql(self, config: DatabaseConfig):
        """Setup PostgreSQL connection pool"""
        if not ASYNCPG_AVAILABLE:
            raise ImportError("asyncpg is required for PostgreSQL support. Install with: pip install asyncpg")
        
        try:
            # Create connection string
            if not config.connection_string:
                config.connection_string = (
                    f"postgresql://{config.username}:{config.password}"
                    f"@{config.host}:{config.port}/{config.database}"
                )
            
            # Create connection pool
            pool = await asyncpg.create_pool(
                config.connection_string,
                min_size=1,
                max_size=config.max_connections,
                command_timeout=config.timeout
            )
            
            self.connection_pools[config.name] = pool
            logger.info(f"PostgreSQL pool created for {config.name}")
            
        except Exception as e:
            logger.error(f"Failed to setup PostgreSQL for {config.name}: {e}")
            raise
    
    async def _setup_sqlite(self, config: DatabaseConfig):
        """Setup SQLite connection"""
        try:
            # SQLite doesn't need connection pooling
            # Just store the database path
            self.connections[config.name] = {
                'type': 'sqlite',
                'path': config.database,
                'config': config
            }
            logger.info(f"SQLite connection setup for {config.name}")
            
        except Exception as e:
            logger.error(f"Failed to setup SQLite for {config.name}: {e}")
            raise
    
    async def _setup_mysql(self, config: DatabaseConfig):
        """Setup MySQL connection"""
        if not AIOMYSQL_AVAILABLE:
            raise ImportError("aiomysql is required for MySQL support. Install with: pip install aiomysql")
        
        try:
            # MySQL connection setup (placeholder)
            # You would implement MySQL connection here
            logger.info(f"MySQL connection setup for {config.name}")
            
        except Exception as e:
            logger.error(f"Failed to setup MySQL for {config.name}: {e}")
            raise
    
    @asynccontextmanager
    async def get_connection(self, database_name: str):
        """Get database connection"""
        if database_name not in self.configs:
            raise ValueError(f"Database {database_name} not found")
        
        config = self.configs[database_name]
        
        if config.type == DatabaseType.POSTGRESQL:
            async with self.connection_pools[database_name].acquire() as conn:
                yield conn
        elif config.type == DatabaseType.SQLITE:
            conn = sqlite3.connect(config.database)
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()
        else:
            raise ValueError(f"Unsupported database type: {config.type}")
    
    async def execute_query(
        self, 
        database_name: str, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> QueryResult:
        """Execute query on specific database"""
        start_time = datetime.now()
        
        try:
            async with self.get_connection(database_name) as conn:
                if self.configs[database_name].type == DatabaseType.POSTGRESQL:
                    # PostgreSQL async execution
                    if params:
                        rows = await conn.fetch(query, *params.values())
                    else:
                        rows = await conn.fetch(query)
                    
                    data = [dict(row) for row in rows]
                    columns = list(rows[0].keys()) if rows else []
                    
                elif self.configs[database_name].type == DatabaseType.SQLITE:
                    # SQLite execution
                    cursor = conn.execute(query, params or {})
                    rows = cursor.fetchall()
                    data = [dict(row) for row in rows]
                    columns = [description[0] for description in cursor.description] if cursor.description else []
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                return QueryResult(
                    database_name=database_name,
                    query=query,
                    data=data,
                    columns=columns,
                    row_count=len(data),
                    execution_time=execution_time,
                    success=True
                )
                
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            logger.error(f"Query execution failed on {database_name}: {e}")
            
            return QueryResult(
                database_name=database_name,
                query=query,
                data=[],
                columns=[],
                row_count=0,
                execution_time=execution_time,
                success=False,
                error=str(e)
            )
    
    async def execute_query_all_databases(
        self, 
        query: str, 
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, QueryResult]:
        """Execute query on all active databases"""
        results = {}
        
        for db_name, config in self.configs.items():
            if config.is_active:
                try:
                    result = await self.execute_query(db_name, query, params)
                    results[db_name] = result
                except Exception as e:
                    logger.error(f"Failed to execute query on {db_name}: {e}")
                    results[db_name] = QueryResult(
                        database_name=db_name,
                        query=query,
                        data=[],
                        columns=[],
                        row_count=0,
                        execution_time=0,
                        success=False,
                        error=str(e)
                    )
        
        return results
    
    async def get_database_schema(self, database_name: str) -> Dict[str, Any]:
        """Get database schema information"""
        try:
            if self.configs[database_name].type == DatabaseType.POSTGRESQL:
                schema_query = """
                SELECT 
                    table_name,
                    column_name,
                    data_type,
                    is_nullable,
                    column_default
                FROM information_schema.columns 
                WHERE table_schema = 'public'
                ORDER BY table_name, ordinal_position;
                """
                
                result = await self.execute_query(database_name, schema_query)
                return {
                    'database_name': database_name,
                    'type': 'postgresql',
                    'tables': result.data,
                    'success': result.success
                }
                
            elif self.configs[database_name].type == DatabaseType.SQLITE:
                # Get SQLite schema
                tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
                tables_result = await self.execute_query(database_name, tables_query)
                
                schema = {
                    'database_name': database_name,
                    'type': 'sqlite',
                    'tables': [],
                    'success': True
                }
                
                for table in tables_result.data:
                    table_name = table['name']
                    columns_query = f"PRAGMA table_info({table_name});"
                    columns_result = await self.execute_query(database_name, columns_query)
                    
                    schema['tables'].append({
                        'table_name': table_name,
                        'columns': columns_result.data
                    })
                
                return schema
                
        except Exception as e:
            logger.error(f"Failed to get schema for {database_name}: {e}")
            return {
                'database_name': database_name,
                'type': 'unknown',
                'tables': [],
                'success': False,
                'error': str(e)
            }
    
    async def get_all_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all databases"""
        schemas = {}
        
        for db_name in self.configs.keys():
            if self.configs[db_name].is_active:
                schema = await self.get_database_schema(db_name)
                schemas[db_name] = schema
        
        return schemas
    
    async def search_across_databases(
        self, 
        search_term: str, 
        table_pattern: str = "%"
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Search for data across all databases"""
        results = {}
        
        for db_name, config in self.configs.items():
            if not config.is_active:
                continue
                
            try:
                if config.type == DatabaseType.POSTGRESQL:
                    # PostgreSQL search
                    search_query = """
                    SELECT table_name, column_name, data_type
                    FROM information_schema.columns 
                    WHERE table_name ILIKE %s 
                    AND column_name ILIKE %s
                    ORDER BY table_name, column_name;
                    """
                    
                    result = await self.execute_query(
                        db_name, 
                        search_query, 
                        {'table_pattern': table_pattern, 'search_term': f'%{search_term}%'}
                    )
                    
                elif config.type == DatabaseType.SQLITE:
                    # SQLite search
                    search_query = """
                    SELECT name as table_name, sql
                    FROM sqlite_master 
                    WHERE type='table' 
                    AND name LIKE ?
                    AND sql LIKE ?
                    ORDER BY name;
                    """
                    
                    result = await self.execute_query(
                        db_name, 
                        search_query, 
                        {'table_pattern': table_pattern, 'search_term': f'%{search_term}%'}
                    )
                
                results[db_name] = result.data if result.success else []
                
            except Exception as e:
                logger.error(f"Search failed on {db_name}: {e}")
                results[db_name] = []
        
        return results
    
    async def close_all_connections(self):
        """Close all database connections"""
        for db_name, pool in self.connection_pools.items():
            try:
                await pool.close()
                logger.info(f"Closed connection pool for {db_name}")
            except Exception as e:
                logger.error(f"Failed to close pool for {db_name}: {e}")
        
        self.connection_pools.clear()
        self.connections.clear()
    
    def get_database_list(self) -> List[Dict[str, Any]]:
        """Get list of all configured databases"""
        return [
            {
                'name': name,
                'type': config.type.value,
                'host': config.host,
                'port': config.port,
                'database': config.database,
                'is_active': config.is_active
            }
            for name, config in self.configs.items()
        ]

# Global instance
multi_db_manager = MultiDatabaseManager()
