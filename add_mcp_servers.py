#!/usr/bin/env python3
"""
MCP Hub - Add MCP Servers and Tools

This script helps you add MCP servers to your MCP Hub.
"""

import sqlite3
import subprocess
import asyncio
import json
from datetime import datetime

def add_sample_servers():
    """Add sample MCP servers to the database."""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        
        # Sample MCP servers
        servers = [
            {
                "name": "filesystem",
                "uri": "npx @modelcontextprotocol/server-filesystem /Users",
                "enabled": True
            },
            {
                "name": "memory",
                "uri": "npx @modelcontextprotocol/server-memory",
                "enabled": True
            },
            {
                "name": "brave-search",
                "uri": "npx @modelcontextprotocol/server-brave-search",
                "enabled": False  # Requires API key
            }
        ]
        
        print("🔧 Adding sample MCP servers...")
        
        for server in servers:
            cursor.execute("""
                INSERT OR REPLACE INTO servers (name, uri, enabled, created_at)
                VALUES (?, ?, ?, ?)
            """, (
                server["name"],
                server["uri"],
                server["enabled"],
                datetime.now().isoformat()
            ))
            print(f"✅ Added server: {server['name']}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 Sample servers added successfully!")
        print("\n📝 Next steps:")
        print("1. Install MCP servers: npm install -g @modelcontextprotocol/server-filesystem")
        print("2. Install MCP servers: npm install -g @modelcontextprotocol/server-memory")
        print("3. Restart your MCP Hub application")
        print("4. The tools will be discovered automatically")
        
    except sqlite3.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def list_available_mcp_servers():
    """List available MCP servers that can be installed."""
    print("📦 Available MCP Servers")
    print("=" * 40)
    print()
    
    servers = [
        {
            "name": "filesystem",
            "package": "@modelcontextprotocol/server-filesystem",
            "description": "File system operations",
            "command": "npx @modelcontextprotocol/server-filesystem /path/to/directory"
        },
        {
            "name": "memory",
            "package": "@modelcontextprotocol/server-memory",
            "description": "Persistent memory storage",
            "command": "npx @modelcontextprotocol/server-memory"
        },
        {
            "name": "brave-search",
            "package": "@modelcontextprotocol/server-brave-search",
            "description": "Web search using Brave Search API",
            "command": "npx @modelcontextprotocol/server-brave-search"
        },
        {
            "name": "sqlite",
            "package": "@modelcontextprotocol/server-sqlite",
            "description": "SQLite database operations",
            "command": "npx @modelcontextprotocol/server-sqlite /path/to/database.db"
        },
        {
            "name": "fetch",
            "package": "@modelcontextprotocol/server-fetch",
            "description": "HTTP fetch operations",
            "command": "npx @modelcontextprotocol/server-fetch"
        }
    ]
    
    for server in servers:
        print(f"🔧 {server['name']}")
        print(f"   Package: {server['package']}")
        print(f"   Description: {server['description']}")
        print(f"   Command: {server['command']}")
        print()

def install_mcp_servers():
    """Install MCP servers using npm."""
    print("📦 Installing MCP servers...")
    print()
    
    servers_to_install = [
        "@modelcontextprotocol/server-filesystem",
        "@modelcontextprotocol/server-memory"
    ]
    
    for package in servers_to_install:
        try:
            print(f"Installing {package}...")
            result = subprocess.run(
                ["npm", "install", "-g", package],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print(f"✅ {package} installed successfully")
            else:
                print(f"❌ Failed to install {package}: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Timeout installing {package}")
        except Exception as e:
            print(f"❌ Error installing {package}: {e}")
    
    print("\n🎉 Installation complete!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            list_available_mcp_servers()
        elif sys.argv[1] == "--install":
            install_mcp_servers()
        elif sys.argv[1] == "--add":
            add_sample_servers()
        else:
            print("Usage: python add_mcp_servers.py [--list|--install|--add]")
    else:
        print("🔧 MCP Hub - Server Management")
        print("=" * 40)
        print()
        print("Available commands:")
        print("  --list    List available MCP servers")
        print("  --install Install MCP servers")
        print("  --add     Add sample servers to database")
        print()
        print("Example:")
        print("  python add_mcp_servers.py --list")
        print("  python add_mcp_servers.py --install")
        print("  python add_mcp_servers.py --add")
