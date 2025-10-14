"""
Database management API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import logging

from app.core.multi_database_manager import (
    multi_db_manager, 
    DatabaseConfig, 
    DatabaseType,
    QueryResult
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="", tags=["databases"])

class DatabaseConfigRequest(BaseModel):
    name: str
    type: str
    host: str
    port: int
    database: str
    username: str
    password: str
    connection_string: Optional[str] = None
    is_active: bool = True
    max_connections: int = 10
    timeout: int = 30

class QueryRequest(BaseModel):
    database_name: Optional[str] = None
    query: str
    params: Optional[Dict[str, Any]] = None

class SearchRequest(BaseModel):
    search_term: str
    table_pattern: str = "%"

@router.get("/", response_model=List[Dict[str, Any]])
async def list_databases():
    """Get list of all configured databases"""
    try:
        return multi_db_manager.get_database_list()
    except Exception as e:
        logger.error(f"Failed to list databases: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=Dict[str, Any])
async def add_database(config: DatabaseConfigRequest):
    """Add a new database connection"""
    try:
        # Convert string type to enum
        db_type = DatabaseType(config.type.lower())
        
        db_config = DatabaseConfig(
            name=config.name,
            type=db_type,
            host=config.host,
            port=config.port,
            database=config.database,
            username=config.username,
            password=config.password,
            connection_string=config.connection_string,
            is_active=config.is_active,
            max_connections=config.max_connections,
            timeout=config.timeout
        )
        
        success = await multi_db_manager.add_database(db_config)
        
        if success:
            return {"message": f"Database {config.name} added successfully", "success": True}
        else:
            raise HTTPException(status_code=400, detail=f"Failed to add database {config.name}")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid database type: {e}")
    except Exception as e:
        logger.error(f"Failed to add database: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{database_name}/schema", response_model=Dict[str, Any])
async def get_database_schema(database_name: str):
    """Get schema information for a specific database"""
    try:
        schema = await multi_db_manager.get_database_schema(database_name)
        return schema
    except Exception as e:
        logger.error(f"Failed to get schema for {database_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/schemas", response_model=Dict[str, Dict[str, Any]])
async def get_all_schemas():
    """Get schema information for all databases"""
    try:
        schemas = await multi_db_manager.get_all_schemas()
        return schemas
    except Exception as e:
        logger.error(f"Failed to get all schemas: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query", response_model=QueryResult)
async def execute_query(request: QueryRequest):
    """Execute query on a specific database"""
    try:
        if request.database_name:
            result = await multi_db_manager.execute_query(
                request.database_name, 
                request.query, 
                request.params
            )
        else:
            # Execute on all databases
            results = await multi_db_manager.execute_query_all_databases(
                request.query, 
                request.params
            )
            # Return first successful result or first result
            result = next(iter(results.values())) if results else None
            if not result:
                raise HTTPException(status_code=400, detail="No databases configured")
        
        return result
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/query/all", response_model=Dict[str, QueryResult])
async def execute_query_all_databases(request: QueryRequest):
    """Execute query on all databases"""
    try:
        results = await multi_db_manager.execute_query_all_databases(
            request.query, 
            request.params
        )
        return results
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/search", response_model=Dict[str, List[Dict[str, Any]]])
async def search_across_databases(request: SearchRequest):
    """Search for data across all databases"""
    try:
        results = await multi_db_manager.search_across_databases(
            request.search_term,
            request.table_pattern
        )
        return results
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{database_name}/tables", response_model=List[Dict[str, Any]])
async def get_database_tables(database_name: str):
    """Get list of tables in a specific database"""
    try:
        schema = await multi_db_manager.get_database_schema(database_name)
        if not schema.get('success', False):
            raise HTTPException(status_code=400, detail=schema.get('error', 'Unknown error'))
        
        # Extract table information
        tables = []
        if schema.get('type') == 'postgresql':
            # Group by table_name
            table_groups = {}
            for column in schema.get('tables', []):
                table_name = column.get('table_name')
                if table_name not in table_groups:
                    table_groups[table_name] = {
                        'table_name': table_name,
                        'columns': []
                    }
                table_groups[table_name]['columns'].append(column)
            
            tables = list(table_groups.values())
            
        elif schema.get('type') == 'sqlite':
            tables = schema.get('tables', [])
        
        return tables
        
    except Exception as e:
        logger.error(f"Failed to get tables for {database_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{database_name}/health", response_model=Dict[str, Any])
async def check_database_health(database_name: str):
    """Check database connection health"""
    try:
        # Simple health check query
        result = await multi_db_manager.execute_query(database_name, "SELECT 1 as health_check")
        
        return {
            "database_name": database_name,
            "status": "healthy" if result.success else "unhealthy",
            "response_time": result.execution_time,
            "error": result.error
        }
        
    except Exception as e:
        logger.error(f"Health check failed for {database_name}: {e}")
        return {
            "database_name": database_name,
            "status": "unhealthy",
            "response_time": 0,
            "error": str(e)
        }

@router.delete("/{database_name}")
async def remove_database(database_name: str):
    """Remove a database connection"""
    try:
        if database_name in multi_db_manager.configs:
            del multi_db_manager.configs[database_name]
            if database_name in multi_db_manager.connection_pools:
                await multi_db_manager.connection_pools[database_name].close()
                del multi_db_manager.connection_pools[database_name]
            
            return {"message": f"Database {database_name} removed successfully", "success": True}
        else:
            raise HTTPException(status_code=404, detail=f"Database {database_name} not found")
            
    except Exception as e:
        logger.error(f"Failed to remove database {database_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
