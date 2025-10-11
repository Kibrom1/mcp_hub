#!/bin/bash

# MCP Hub - Demo Mode Runner
# Works without API keys for demonstration purposes

echo "🔧 Starting MCP Hub - Demo Mode"
echo "=================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup first."
    exit 1
fi

# Activate virtual environment
echo "📦 Activating virtual environment..."
source venv/bin/activate

# Demo mode info
echo "🔧 Running in DEMO MODE"
echo "💡 No API keys required for demo features"
echo ""

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
echo "🌐 Starting Streamlit application in DEMO MODE..."
echo "📍 URL: http://localhost:8501"
echo "🔧 Features: Tool exploration, database queries, file operations"
echo "💡 No AI chat available (requires API keys)"
echo "🛑 Press Ctrl+C to stop"
echo ""

# Run the demo application
streamlit run app_demo.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
