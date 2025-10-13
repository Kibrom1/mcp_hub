"""
MCP Executor for MCP Hub Core
Handles execution of MCP tools and resources
"""

import sqlite3
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

class MCPExecutor:
    """Executes MCP tools and manages resources"""
    
    def __init__(self):
        self.db_path = 'mcp.db'
        self.initialize_database()
    
    def initialize_database(self):
        """Initialize the MCP database if it doesn't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create tables if they don't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS servers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    uri TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_name TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT,
                    parameters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_name) REFERENCES servers (name)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS resources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    server_name TEXT NOT NULL,
                    name TEXT NOT NULL,
                    uri TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (server_name) REFERENCES servers (name)
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Database initialization failed: {e}")
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an MCP tool with given arguments"""
        try:
            # Get tool information
            tool_info = self.get_tool_info(tool_name)
            if not tool_info:
                return {
                    "error": f"Tool {tool_name} not found",
                    "success": False
                }
            
            server_name = tool_info['server_name']
            
            # Route to appropriate executor based on server
            if server_name == 'sqlite':
                return await self.execute_sqlite_tool(tool_name, arguments)
            elif server_name == 'filesystem':
                return await self.execute_filesystem_tool(tool_name, arguments)
            elif server_name == 'memory':
                return await self.execute_memory_tool(tool_name, arguments)
            else:
                return {
                    "error": f"Unknown server type: {server_name}",
                    "success": False
                }
                
        except Exception as e:
            return {
                "error": f"Tool execution failed: {e}",
                "success": False
            }
    
    def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific tool"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT name, server_name, description, parameters
                FROM tools
                WHERE name = ?
            ''', (tool_name,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'name': result[0],
                    'server_name': result[1],
                    'description': result[2],
                    'parameters': json.loads(result[3]) if result[3] else {}
                }
            return None
            
        except Exception as e:
            print(f"Error getting tool info: {e}")
            return None
    
    async def execute_sqlite_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute SQLite database tools"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            if tool_name == "query_database":
                query = arguments.get("query", "")
                cursor.execute(query)
                
                if query.strip().upper().startswith("SELECT"):
                    results = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    return {
                        "server": "sqlite",
                        "tool": tool_name,
                        "result": {
                            "columns": columns,
                            "rows": results,
                            "row_count": len(results)
                        },
                        "success": True
                    }
                else:
                    conn.commit()
                    return {
                        "server": "sqlite",
                        "tool": tool_name,
                        "result": f"Query executed successfully. Rows affected: {cursor.rowcount}",
                        "success": True
                    }
            
            elif tool_name == "list_tables":
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()
                table_names = [table[0] for table in tables]
                return {
                    "server": "sqlite",
                    "tool": tool_name,
                    "result": {
                        "tables": table_names,
                        "count": len(table_names)
                    },
                    "success": True
                }
            
            elif tool_name == "describe_table":
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
                return {
                    "server": "sqlite",
                    "tool": tool_name,
                    "result": schema,
                    "success": True
                }
            
            elif tool_name == "get_table_data":
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
                return {
                    "server": "sqlite",
                    "tool": tool_name,
                    "result": data,
                    "success": True
                }
            
            else:
                return {
                    "server": "sqlite",
                    "tool": tool_name,
                    "result": f"Unknown tool: {tool_name}",
                    "success": False
                }
                
        except Exception as e:
            return {
                "server": "sqlite",
                "tool": tool_name,
                "error": f"SQLite tool execution failed: {e}",
                "success": False
            }
        finally:
            conn.close()
    
    async def execute_filesystem_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute filesystem tools"""
        try:
            if tool_name == "read_file":
                path = arguments.get("path", "")
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return {
                    "server": "filesystem",
                    "tool": tool_name,
                    "result": content,
                    "success": True
                }
            
            elif tool_name == "write_file":
                path = arguments.get("path", "")
                content = arguments.get("content", "")
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                return {
                    "server": "filesystem",
                    "tool": tool_name,
                    "result": f"File written successfully: {path}",
                    "success": True
                }
            
            elif tool_name == "list_directory":
                path = arguments.get("path", "")
                items = os.listdir(path)
                return {
                    "server": "filesystem",
                    "tool": tool_name,
                    "result": items,
                    "success": True
                }
            
            else:
                return {
                    "server": "filesystem",
                    "tool": tool_name,
                    "result": f"Unknown tool: {tool_name}",
                    "success": False
                }
                
        except Exception as e:
            return {
                "server": "filesystem",
                "tool": tool_name,
                "error": f"Filesystem tool execution failed: {e}",
                "success": False
            }
    
    async def execute_memory_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute memory tools"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Create memory table if it doesn't exist
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memory (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            if tool_name == "store_memory":
                key = arguments.get("key", "")
                value = arguments.get("value", "")
                
                cursor.execute('''
                    INSERT OR REPLACE INTO memory (key, value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                ''', (key, value))
                conn.commit()
                
                return {
                    "server": "memory",
                    "tool": tool_name,
                    "result": f"Memory stored: {key}",
                    "success": True
                }
            
            elif tool_name == "retrieve_memory":
                key = arguments.get("key", "")
                cursor.execute("SELECT value FROM memory WHERE key = ?", (key,))
                result = cursor.fetchone()
                
                if result:
                    return {
                        "server": "memory",
                        "tool": tool_name,
                        "result": result[0],
                        "success": True
                    }
                else:
                    return {
                        "server": "memory",
                        "tool": tool_name,
                        "result": None,
                        "success": True
                    }
            
            elif tool_name == "list_memories":
                cursor.execute("SELECT key, value, created_at FROM memory ORDER BY created_at DESC")
                memories = cursor.fetchall()
                
                result = [
                    {
                        "key": mem[0],
                        "value": mem[1],
                        "created_at": mem[2]
                    }
                    for mem in memories
                ]
                
                return {
                    "server": "memory",
                    "tool": tool_name,
                    "result": result,
                    "success": True
                }
            
            else:
                return {
                    "server": "memory",
                    "tool": tool_name,
                    "result": f"Unknown tool: {tool_name}",
                    "success": False
                }
                
        except Exception as e:
            return {
                "server": "memory",
                "tool": tool_name,
                "error": f"Memory tool execution failed: {e}",
                "success": False
            }
        finally:
            conn.close()
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """Get list of all available tools"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT t.name, t.description, t.parameters, s.name as server_name, s.enabled
                FROM tools t
                JOIN servers s ON t.server_name = s.name
                ORDER BY s.name, t.name
            ''')
            
            tools = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "name": tool[0],
                    "description": tool[1],
                    "parameters": json.loads(tool[2]) if tool[2] else {},
                    "server": tool[3],
                    "enabled": bool(tool[4])
                }
                for tool in tools
            ]
            
        except Exception as e:
            print(f"Error getting available tools: {e}")
            return []
    
    def get_available_resources(self) -> List[Dict[str, Any]]:
        """Get list of all available resources"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT r.name, r.uri, s.name as server_name, s.enabled
                FROM resources r
                JOIN servers s ON r.server_name = s.name
                ORDER BY s.name, r.name
            ''')
            
            resources = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "name": resource[0],
                    "uri": resource[1],
                    "server": resource[2],
                    "enabled": bool(resource[3])
                }
                for resource in resources
            ]
            
        except Exception as e:
            print(f"Error getting available resources: {e}")
            return []
