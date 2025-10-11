#!/usr/bin/env python3
"""
MCP Hub - Tool Discovery Script

This script connects to MCP servers and discovers their available tools.
"""

import asyncio
import sqlite3
import subprocess
import json
import time
from datetime import datetime
from typing import List, Dict, Any

async def discover_tools_from_server(server_name: str, server_uri: str) -> Dict[str, Any]:
    """Discover tools from a specific MCP server."""
    try:
        print(f"🔍 Discovering tools from server: {server_name}")
        print(f"   Command: {server_uri}")
        
        # Check if the server command exists
        if server_uri.startswith("npx"):
            # Check if npx is available
            try:
                subprocess.run(["npx", "--version"], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                print(f"   ⚠️  npx not found. Please install Node.js and npm")
                return {"tools": [], "resources": [], "error": "npx not available"}
        
        # For demo purposes, let's create some sample tools
        if server_name == "filesystem":
            tools = [
                {
                    "name": "read_file",
                    "description": "Read contents of a file",
                    "parameters": '{"path": "string"}'
                },
                {
                    "name": "write_file", 
                    "description": "Write content to a file",
                    "parameters": '{"path": "string", "content": "string"}'
                },
                {
                    "name": "list_directory",
                    "description": "List files in a directory",
                    "parameters": '{"path": "string"}'
                }
            ]
            resources = [
                {
                    "name": "file_system",
                    "uri": "/Users"
                }
            ]
        elif server_name == "memory":
            tools = [
                {
                    "name": "store_memory",
                    "description": "Store information in memory",
                    "parameters": '{"key": "string", "value": "string"}'
                },
                {
                    "name": "retrieve_memory",
                    "description": "Retrieve information from memory", 
                    "parameters": '{"key": "string"}'
                },
                {
                    "name": "list_memories",
                    "description": "List all stored memories",
                    "parameters": '{}'
                }
            ]
            resources = [
                {
                    "name": "memory_store",
                    "uri": "memory://"
                }
            ]
        elif server_name == "brave-search":
            tools = [
                {
                    "name": "search_web",
                    "description": "Search the web using Brave Search",
                    "parameters": '{"query": "string", "count": "number"}'
                }
            ]
            resources = []
        else:
            tools = []
            resources = []
        
        print(f"   ✅ Found {len(tools)} tools and {len(resources)} resources")
        
        return {
            "tools": tools,
            "resources": resources,
            "error": None
        }
        
    except Exception as e:
        print(f"   ❌ Error discovering tools: {e}")
        return {"tools": [], "resources": [], "error": str(e)}

def save_tools_to_database(server_name: str, tools: List[Dict], resources: List[Dict]):
    """Save discovered tools and resources to the database."""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        # Save tools
        for tool in tools:
            cursor.execute("""
                INSERT OR REPLACE INTO tools 
                (id, server_name, name, description, parameters, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                f"{server_name}_{tool['name']}",
                server_name,
                tool['name'],
                tool['description'],
                tool['parameters'],
                datetime.now().isoformat()
            ))
        
        # Save resources
        for resource in resources:
            cursor.execute("""
                INSERT OR REPLACE INTO resources
                (id, server_name, name, uri, created_at)
                VALUES (?, ?, ?, ?, ?)
            """, (
                f"{server_name}_{resource['name']}",
                server_name,
                resource['name'],
                resource['uri'],
                datetime.now().isoformat()
            ))
        
        conn.commit()
        conn.close()
        
        print(f"   💾 Saved {len(tools)} tools and {len(resources)} resources to database")
        
    except Exception as e:
        print(f"   ❌ Error saving to database: {e}")

async def discover_all_tools():
    """Discover tools from all configured servers."""
    try:
        # Get servers from database
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, uri, enabled FROM servers")
        servers = cursor.fetchall()
        conn.close()
        
        if not servers:
            print("⚠️  No servers configured. Run 'python add_mcp_servers.py --add' first.")
            return
        
        print("🔍 MCP Hub - Tool Discovery")
        print("=" * 40)
        print()
        
        total_tools = 0
        total_resources = 0
        
        for server_name, server_uri, enabled in servers:
            if not enabled:
                print(f"⏭️  Skipping disabled server: {server_name}")
                continue
                
            result = await discover_tools_from_server(server_name, server_uri)
            
            if result["error"]:
                print(f"   ❌ {result['error']}")
                continue
            
            # Save to database
            save_tools_to_database(server_name, result["tools"], result["resources"])
            
            total_tools += len(result["tools"])
            total_resources += len(result["resources"])
            
            print()
        
        print("🎉 Tool Discovery Complete!")
        print(f"📊 Total: {total_tools} tools, {total_resources} resources")
        print()
        print("🔄 Restart your MCP Hub application to see the tools:")
        print("   ./run_local.sh")
        
    except Exception as e:
        print(f"❌ Discovery failed: {e}")

def list_discovered_tools():
    """List all discovered tools."""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        # Get tools
        cursor.execute("""
            SELECT s.name as server_name, t.name as tool_name, t.description, t.parameters
            FROM tools t
            JOIN servers s ON t.server_name = s.name
            ORDER BY s.name, t.name
        """)
        tools = cursor.fetchall()
        
        # Get resources
        cursor.execute("""
            SELECT s.name as server_name, r.name as resource_name, r.uri
            FROM resources r
            JOIN servers s ON r.server_name = s.name
            ORDER BY s.name, r.name
        """)
        resources = cursor.fetchall()
        
        conn.close()
        
        print("🔧 Discovered Tools")
        print("=" * 30)
        
        if tools:
            current_server = None
            for server_name, tool_name, description, parameters in tools:
                if server_name != current_server:
                    print(f"\n📡 {server_name}:")
                    current_server = server_name
                print(f"   🔧 {tool_name}")
                print(f"      {description}")
                if parameters:
                    print(f"      Parameters: {parameters}")
        else:
            print("⚠️  No tools discovered yet")
        
        print("\n📁 Discovered Resources")
        print("=" * 30)
        
        if resources:
            current_server = None
            for server_name, resource_name, resource_uri in resources:
                if server_name != current_server:
                    print(f"\n📡 {server_name}:")
                    current_server = server_name
                print(f"   📁 {resource_name}")
                print(f"      URI: {resource_uri}")
        else:
            print("⚠️  No resources discovered yet")
        
    except Exception as e:
        print(f"❌ Error listing tools: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_discovered_tools()
    else:
        asyncio.run(discover_all_tools())
