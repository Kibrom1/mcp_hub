#!/bin/bash

# MCP Hub - Main Application Runner
# Simple, working MCP tool integration platform

echo "🚀 Starting MCP Hub - MCP Tool Integration Platform"
echo "=================================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Load environment variables from .env file if it exists
if [ -f ".env" ]; then
    echo "📄 Loading environment variables from .env file..."
    export $(cat .env | grep -v '^#' | xargs)
fi

# Set API keys from environment variables
echo "🔑 Setting up API keys..."
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set. Please set it in your environment or .env file"
fi
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY not set. Please set it in your environment or .env file"
fi

# Check if database exists
if [ ! -f "mcp.db" ]; then
    echo "⚠️  Database not found. Please run discovery first:"
    echo "   python discover_tools.py"
    echo ""
fi

# Check if tools are available
echo "🔍 Checking available tools..."
python -c "
import sqlite3
try:
    conn = sqlite3.connect('mcp.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM tools')
    tool_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM servers WHERE enabled = 1')
    server_count = cursor.fetchone()[0]
    conn.close()
    print(f'📊 Found {tool_count} tools across {server_count} enabled servers')
    if tool_count == 0:
        print('⚠️  No tools available. Run: python discover_tools.py')
except Exception as e:
    print(f'❌ Database error: {e}')
"

echo ""
echo "🌐 Starting Streamlit application..."
echo "📍 URL: http://localhost:8501"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Run the main application
streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
