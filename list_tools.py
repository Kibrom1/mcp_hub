#!/usr/bin/env python3
"""
MCP Hub - List Available Tools

This script lists all available MCP tools from the database.
"""

import sqlite3
from datetime import datetime

def list_tools():
    """List all available MCP tools from the database."""
    try:
        # Connect to the database
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        print("🔧 MCP Hub - Available Tools")
        print("=" * 50)
        
        # List servers
        cursor.execute("SELECT name, uri, enabled, created_at FROM servers")
        servers = cursor.fetchall()
        
        if not servers:
            print("⚠️  No servers configured")
            return
        
        print(f"📊 Found {len(servers)} servers:")
        print()
        
        for server in servers:
            name, uri, enabled, created_at = server
            status = "✅ Enabled" if enabled else "❌ Disabled"
            print(f"🖥️  Server: {name}")
            print(f"   URI: {uri}")
            print(f"   Status: {status}")
            print(f"   Created: {created_at}")
            print()
            
            # List tools for this server
            cursor.execute("""
                SELECT name, description, parameters, created_at, last_used 
                FROM tools WHERE server_name = ?
            """, (name,))
            tools = cursor.fetchall()
            
            if tools:
                print(f"   🔧 Tools ({len(tools)}):")
                for tool in tools:
                    tool_name, description, parameters, created_at, last_used = tool
                    print(f"      • {tool_name}")
                    print(f"        Description: {description}")
                    if parameters:
                        print(f"        Parameters: {parameters}")
                    if last_used:
                        print(f"        Last Used: {last_used}")
                    print()
            else:
                print("   ⚠️  No tools available for this server")
                print()
            
            # List resources for this server
            cursor.execute("""
                SELECT name, uri, created_at, last_used 
                FROM resources WHERE server_name = ?
            """, (name,))
            resources = cursor.fetchall()
            
            if resources:
                print(f"   📁 Resources ({len(resources)}):")
                for resource in resources:
                    res_name, res_uri, created_at, last_used = resource
                    print(f"      • {res_name}")
                    print(f"        URI: {res_uri}")
                    if last_used:
                        print(f"        Last Used: {last_used}")
                    print()
            else:
                print("   ⚠️  No resources available for this server")
                print()
            
            print("-" * 50)
            print()
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def list_tools_summary():
    """List a summary of available tools."""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        # Count servers
        cursor.execute("SELECT COUNT(*) FROM servers")
        server_count = cursor.fetchone()[0]
        
        # Count tools
        cursor.execute("SELECT COUNT(*) FROM tools")
        tool_count = cursor.fetchone()[0]
        
        # Count resources
        cursor.execute("SELECT COUNT(*) FROM resources")
        resource_count = cursor.fetchone()[0]
        
        print("📊 MCP Hub - Tools Summary")
        print("=" * 30)
        print(f"🖥️  Servers: {server_count}")
        print(f"🔧 Tools: {tool_count}")
        print(f"📁 Resources: {resource_count}")
        print()
        
        # List tool names only
        cursor.execute("SELECT server_name, name FROM tools ORDER BY server_name, name")
        tools = cursor.fetchall()
        
        if tools:
            print("🔧 Available Tools:")
            current_server = None
            for server_name, tool_name in tools:
                if server_name != current_server:
                    print(f"   📡 {server_name}:")
                    current_server = server_name
                print(f"      • {tool_name}")
        else:
            print("⚠️  No tools found")
        
        conn.close()
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        list_tools_summary()
    else:
        list_tools()
