#!/usr/bin/env python3
"""
Custom SQLite MCP Server for MCP Hub
Provides database exploration and querying capabilities
"""

import asyncio
import json
import sqlite3
import sys
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    ListResourcesRequest,
    ListToolsRequest,
    ReadResourceRequest,
    Resource,
    TextContent,
    Tool,
)

# Initialize the MCP server
server = Server("sqlite-mcp-server")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available SQLite tools"""
    return [
        Tool(
            name="query_database",
            description="Execute a SQL query on the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in the database",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="describe_table",
            description="Get schema information for a specific table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to describe"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="get_table_data",
            description="Get sample data from a table",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of rows to return",
                        "default": 10
                    }
                },
                "required": ["table_name"]
            }
        )
    ]

@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available database resources"""
    return [
        Resource(
            uri="sqlite://mcp.db",
            name="mcp_database",
            description="Main MCP Hub SQLite database",
            mimeType="application/sqlite"
        )
    ]

@server.read_resource()
async def read_resource(uri: str) -> str:
    """Read database resource information"""
    if uri == "sqlite://mcp.db":
        try:
            conn = sqlite3.connect('mcp.db')
            cursor = conn.cursor()
            
            # Get database info
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            info = {
                "database": "mcp.db",
                "tables": [table[0] for table in tables],
                "description": "MCP Hub SQLite database containing servers, tools, and resources"
            }
            
            conn.close()
            return json.dumps(info, indent=2)
        except Exception as e:
            return f"Error reading database: {e}"
    else:
        return "Resource not found"

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> str:
    """Handle tool calls"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        if name == "query_database":
            query = arguments.get("query", "")
            cursor.execute(query)
            
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                return json.dumps({
                    "columns": columns,
                    "rows": results,
                    "row_count": len(results)
                }, indent=2)
            else:
                conn.commit()
                return f"Query executed successfully. Rows affected: {cursor.rowcount}"
        
        elif name == "list_tables":
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            return json.dumps([table[0] for table in tables], indent=2)
        
        elif name == "describe_table":
            table_name = arguments.get("table_name", "")
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            schema = {
                "table": table_name,
                "columns": [
                    {
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "primary_key": bool(col[5])
                    }
                    for col in columns
                ]
            }
            return json.dumps(schema, indent=2)
        
        elif name == "get_table_data":
            table_name = arguments.get("table_name", "")
            limit = arguments.get("limit", 10)
            
            cursor.execute(f"SELECT * FROM {table_name} LIMIT ?", (limit,))
            results = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            data = {
                "table": table_name,
                "columns": columns,
                "rows": results,
                "row_count": len(results)
            }
            return json.dumps(data, indent=2)
        
        else:
            return f"Unknown tool: {name}"
            
    except Exception as e:
        return f"Error executing tool {name}: {e}"
    finally:
        conn.close()

async def main():
    """Main server function"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="sqlite-mcp-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
