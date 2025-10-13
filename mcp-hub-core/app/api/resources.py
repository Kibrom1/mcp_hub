"""
Resources API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import sqlite3

router = APIRouter()

# Pydantic models
class ResourceCreate(BaseModel):
    name: str
    uri: str
    server_name: str
    description: Optional[str] = None

class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    uri: Optional[str] = None
    server_name: Optional[str] = None
    description: Optional[str] = None

class ServerCreate(BaseModel):
    name: str
    uri: str
    enabled: bool = True
    description: Optional[str] = None

@router.get("/")
async def get_resources():
    """Get all available resources"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.name, r.uri, s.name as server_name, s.enabled
            FROM resources r
            JOIN servers s ON r.server_name = s.name
            ORDER BY s.name, r.name
        """)
        resources = cursor.fetchall()
        conn.close()
        
        resources_list = []
        for resource in resources:
            resources_list.append({
                "name": resource[0],
                "uri": resource[1],
                "server": resource[2],
                "enabled": bool(resource[3])
            })
        
        return {"resources": resources_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resources: {e}")

@router.get("/{resource_name}")
async def get_resource(resource_name: str):
    """Get specific resource details"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.name, r.uri, s.name as server_name, s.enabled
            FROM resources r
            JOIN servers s ON r.server_name = s.name
            WHERE r.name = ?
        """, (resource_name,))
        resource = cursor.fetchone()
        conn.close()
        
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        
        return {
            "name": resource[0],
            "uri": resource[1],
            "server": resource[2],
            "enabled": bool(resource[3])
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get resource: {e}")

@router.post("/", status_code=201)
async def create_resource(resource: ResourceCreate):
    """Create a new resource"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        # Check if server exists
        cursor.execute("SELECT id FROM servers WHERE name = ?", (resource.server_name,))
        server = cursor.fetchone()
        
        if not server:
            conn.close()
            raise HTTPException(status_code=400, detail=f"Server '{resource.server_name}' not found")
        
        # Check if resource already exists
        cursor.execute("SELECT id FROM resources WHERE name = ? AND server_name = ?", 
                      (resource.name, resource.server_name))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            raise HTTPException(status_code=400, detail="Resource already exists")
        
        # Create resource
        cursor.execute("""
            INSERT INTO resources (name, uri, server_name)
            VALUES (?, ?, ?)
        """, (resource.name, resource.uri, resource.server_name))
        
        conn.commit()
        conn.close()
        
        return {"message": "Resource created successfully", "resource": resource.dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create resource: {e}")

@router.put("/{resource_name}")
async def update_resource(resource_name: str, resource: ResourceUpdate):
    """Update a resource"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        # Check if resource exists
        cursor.execute("SELECT id FROM resources WHERE name = ?", (resource_name,))
        existing = cursor.fetchone()
        
        if not existing:
            conn.close()
            raise HTTPException(status_code=404, detail="Resource not found")
        
        # Build update query dynamically
        update_fields = []
        values = []
        
        if resource.name is not None:
            update_fields.append("name = ?")
            values.append(resource.name)
        if resource.uri is not None:
            update_fields.append("uri = ?")
            values.append(resource.uri)
        if resource.server_name is not None:
            # Check if new server exists
            cursor.execute("SELECT id FROM servers WHERE name = ?", (resource.server_name,))
            server = cursor.fetchone()
            if not server:
                conn.close()
                raise HTTPException(status_code=400, detail=f"Server '{resource.server_name}' not found")
            update_fields.append("server_name = ?")
            values.append(resource.server_name)
        
        if not update_fields:
            conn.close()
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(resource_name)
        query = f"UPDATE resources SET {', '.join(update_fields)} WHERE name = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        
        return {"message": "Resource updated successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update resource: {e}")

@router.delete("/{resource_name}")
async def delete_resource(resource_name: str):
    """Delete a resource"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        # Check if resource exists
        cursor.execute("SELECT id FROM resources WHERE name = ?", (resource_name,))
        existing = cursor.fetchone()
        
        if not existing:
            conn.close()
            raise HTTPException(status_code=404, detail="Resource not found")
        
        # Delete resource
        cursor.execute("DELETE FROM resources WHERE name = ?", (resource_name,))
        conn.commit()
        conn.close()
        
        return {"message": "Resource deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete resource: {e}")

@router.get("/servers/")
async def get_servers():
    """Get all servers"""
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

@router.post("/servers/", status_code=201)
async def create_server(server: ServerCreate):
    """Create a new server"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        # Check if server already exists
        cursor.execute("SELECT id FROM servers WHERE name = ?", (server.name,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            raise HTTPException(status_code=400, detail="Server already exists")
        
        # Create server
        cursor.execute("""
            INSERT INTO servers (name, uri, enabled)
            VALUES (?, ?, ?)
        """, (server.name, server.uri, server.enabled))
        
        conn.commit()
        conn.close()
        
        return {"message": "Server created successfully", "server": server.dict()}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create server: {e}")

@router.delete("/servers/{server_name}")
async def delete_server(server_name: str):
    """Delete a server and its resources"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        # Check if server exists
        cursor.execute("SELECT id FROM servers WHERE name = ?", (server_name,))
        existing = cursor.fetchone()
        
        if not existing:
            conn.close()
            raise HTTPException(status_code=404, detail="Server not found")
        
        # Delete associated resources first
        cursor.execute("DELETE FROM resources WHERE server_name = ?", (server_name,))
        
        # Delete server
        cursor.execute("DELETE FROM servers WHERE name = ?", (server_name,))
        conn.commit()
        conn.close()
        
        return {"message": "Server and associated resources deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete server: {e}")
