"""
Tools API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
import sqlite3
import json

router = APIRouter()

@router.get("/")
async def get_tools():
    """Get all available tools grouped by server/resource"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.name, t.description, t.parameters, s.name as server_name, s.enabled, s.uri
            FROM tools t
            JOIN servers s ON t.server_name = s.name
            ORDER BY s.name, t.name
        """)
        tools = cursor.fetchall()
        conn.close()
        
        # Group tools by server/resource
        grouped_tools = {}
        for tool in tools:
            server_name = tool[3]
            if server_name not in grouped_tools:
                grouped_tools[server_name] = {
                    "server": server_name,
                    "uri": tool[5],
                    "enabled": bool(tool[4]),
                    "tools": []
                }
            
            grouped_tools[server_name]["tools"].append({
                "name": tool[0],
                "description": tool[1],
                "parameters": json.loads(tool[2]) if tool[2] else {},
                "enabled": bool(tool[4])
            })
        
        # Convert to list format
        servers_list = list(grouped_tools.values())
        
        return {
            "servers": servers_list,
            "total_tools": sum(len(server["tools"]) for server in servers_list),
            "total_servers": len(servers_list)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tools: {e}")

@router.get("/{tool_name}")
async def get_tool(tool_name: str):
    """Get specific tool details"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT t.name, t.description, t.parameters, s.name as server_name, s.enabled
            FROM tools t
            JOIN servers s ON t.server_name = s.name
            WHERE t.name = ?
        """, (tool_name,))
        tool = cursor.fetchone()
        conn.close()
        
        if not tool:
            raise HTTPException(status_code=404, detail="Tool not found")
        
        return {
            "name": tool[0],
            "description": tool[1],
            "parameters": json.loads(tool[2]) if tool[2] else {},
            "server": tool[3],
            "enabled": bool(tool[4])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get tool: {e}")

@router.post("/{tool_name}/execute")
async def execute_tool(tool_name: str, arguments: Dict[str, Any]):
    """Execute a tool with given arguments"""
    try:
        # Import here to avoid circular imports
        from app.services.mcp_executor import MCPExecutor
        
        executor = MCPExecutor()
        result = await executor.execute_tool(tool_name, arguments)
        
        return {
            "tool": tool_name,
            "arguments": arguments,
            "result": result,
            "success": True,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "tool": tool_name,
            "arguments": arguments,
            "error": str(e),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

@router.get("/servers")
async def get_servers():
    """Get all MCP servers"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, uri, enabled FROM servers ORDER BY name")
        servers = cursor.fetchall()
        conn.close()
        
        servers_list = []
        for server in servers:
            servers_list.append({
                "name": server[0],
                "uri": server[1],
                "enabled": bool(server[2])
            })
        
        return {"servers": servers_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get servers: {e}")

@router.post("/servers/{server_name}/toggle")
async def toggle_server(server_name: str, enabled: bool):
    """Enable/disable a server"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE servers SET enabled = ? WHERE name = ?",
            (enabled, server_name)
        )
        conn.commit()
        conn.close()
        
        return {
            "server": server_name,
            "enabled": enabled,
            "message": f"Server {'enabled' if enabled else 'disabled'} successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle server: {e}")
