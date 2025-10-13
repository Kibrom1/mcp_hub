#!/usr/bin/env python3
"""
MCP Hub Core - Backend API
FastAPI backend for MCP Hub
"""

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import os
import json
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
import asyncio

# Import MCP Hub modules
from app.api import tools, chat, resources, auth
from app.core.config import settings
from app.core.database import init_db
from app.services.llm_manager import LLMManager
from app.services.mcp_executor import MCPExecutor

# Create FastAPI app
app = FastAPI(
    title="MCP Hub Core API",
    description="Backend API for MCP Hub - Multi-LLM Tool Integration Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(resources.router, prefix="/api/resources", tags=["resources"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

# Global variables
llm_manager = None
mcp_executor = None
active_connections: List[WebSocket] = []

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    global llm_manager, mcp_executor
    
    # Initialize database
    init_db()
    
    # Initialize LLM manager
    try:
        llm_manager = LLMManager()
        print("✅ LLM Manager initialized")
    except Exception as e:
        print(f"⚠️ LLM Manager initialization failed: {e}")
    
    # Initialize MCP executor
    try:
        mcp_executor = MCPExecutor()
        print("✅ MCP Executor initialized")
    except Exception as e:
        print(f"⚠️ MCP Executor initialization failed: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MCP Hub Core API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "llm_manager": llm_manager is not None,
            "mcp_executor": mcp_executor is not None,
            "database": True
        }
    }

@app.get("/api/status")
async def get_status():
    """Get system status"""
    try:
        # Get tools count
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tools")
        tools_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM servers WHERE enabled = 1")
        servers_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM resources")
        resources_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "tools": tools_count,
            "servers": servers_count,
            "resources": resources_count,
            "llm_providers": len(llm_manager.list_available_providers()) if llm_manager else 0,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get status: {e}")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time communication"""
    await websocket.accept()
    active_connections.append(websocket)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "chat":
                # Process chat message
                response = await process_chat_message(message.get("content", ""))
                await websocket.send_text(json.dumps({
                    "type": "chat_response",
                    "content": response,
                    "timestamp": datetime.now().isoformat()
                }))
            
            elif message.get("type") == "tool_execute":
                # Execute tool
                result = await execute_tool(
                    message.get("tool_name"),
                    message.get("arguments", {})
                )
                await websocket.send_text(json.dumps({
                    "type": "tool_result",
                    "result": result,
                    "timestamp": datetime.now().isoformat()
                }))
            
    except WebSocketDisconnect:
        active_connections.remove(websocket)

async def process_chat_message(content: str) -> str:
    """Process chat message with LLM"""
    if not llm_manager:
        return "LLM manager not available"
    
    try:
        # Get available tools and resources
        tools_info = get_tools_info()
        resources_info = get_resources_info()
        
        system_prompt = f"""You are a helpful AI assistant with access to MCP tools and resources.

Available Tools: {tools_info}
Available Resources: {resources_info}

When a user asks something that can be answered using these tools, you should:
1. Analyze the user's request
2. Determine which tool(s) would be most helpful
3. Execute the appropriate tool(s)
4. Use the results to provide a comprehensive answer

You can execute tools by responding with:
TOOL_EXECUTE: {{"tool": "tool_name", "server": "server_name", "arguments": {{"param": "value"}}}}
"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content}
        ]
        
        response = await llm_manager.generate_response_async(
            messages,
            provider="openai",  # Default provider
            max_tokens=2000,
            temperature=0.3
        )
        
        return response.content
        
    except Exception as e:
        return f"Error processing message: {e}"

async def execute_tool(tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute MCP tool"""
    if not mcp_executor:
        return {"error": "MCP executor not available"}
    
    try:
        result = await mcp_executor.execute_tool(tool_name, arguments)
        return result
    except Exception as e:
        return {"error": f"Tool execution failed: {e}"}

def get_tools_info() -> str:
    """Get formatted tools information"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, description, parameters FROM tools")
        tools = cursor.fetchall()
        conn.close()
        
        tools_info = []
        for tool in tools:
            tools_info.append(f"- {tool[0]}: {tool[1]}")
        
        return "\n".join(tools_info)
    except Exception as e:
        return f"Error loading tools: {e}"

def get_resources_info() -> str:
    """Get formatted resources information"""
    try:
        conn = sqlite3.connect('mcp.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name, uri FROM resources")
        resources = cursor.fetchall()
        conn.close()
        
        resources_info = []
        for resource in resources:
            resources_info.append(f"- {resource[0]}: {resource[1]}")
        
        return "\n".join(resources_info)
    except Exception as e:
        return f"Error loading resources: {e}"

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
