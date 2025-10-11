# 🤖 MCP Hub - Model Context Protocol Integration Platform

A simple, working MCP tool integration platform with multi-LLM support.

## ✨ Features

- **🛠️ MCP Tool Integration**: Connect to and use MCP servers
- **🤖 Multi-LLM Support**: OpenAI GPT and Google Gemini
- **📁 File Operations**: Create, read, and manage files
- **💾 Memory Management**: Store and retrieve information
- **🎯 Tool-Aware AI**: LLM can execute tools during conversations

## 🚀 Quick Start

### 1. Setup
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
# Option 1: Create a .env file (recommended)
cp env.example .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your_openai_api_key_here
# GOOGLE_API_KEY=your_google_api_key_here

# Option 2: Set environment variables directly
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"
```

**Get your API keys:**
- **OpenAI**: https://platform.openai.com/api-keys
- **Google Gemini**: https://makersuite.google.com/app/apikey

### 3. Discover Tools
```bash
# Add MCP servers
python add_mcp_servers.py --add

# Discover available tools
python discover_tools.py
```

### 4. Run Application
```bash
./run.sh
```

Access at: http://localhost:8501

## 📁 Project Structure

```
mcp_hub/
├── app.py                    # Main Streamlit application
├── run.sh                    # Application runner
├── llm_providers.py          # Multi-LLM provider management
├── discover_tools.py         # MCP tool discovery
├── list_tools.py            # List available tools
├── add_mcp_servers.py       # MCP server management
├── requirements.txt         # Python dependencies
├── config/                   # Configuration files
├── deployment/              # Deployment configurations
└── tests/                   # Test suite
```

## 🛠️ Available Tools

### Filesystem Server
- `read_file` - Read file contents
- `write_file` - Write content to files
- `list_directory` - List directory contents

### Memory Server
- `store_memory` - Store information
- `retrieve_memory` - Retrieve stored information
- `list_memories` - List all stored memories

## 🤖 LLM Providers

- **OpenAI**: GPT-4o-mini
- **Google Gemini**: gemini-2.0-flash

## 📚 Documentation

- [OpenAI Setup](OPENAI_SETUP.md)
- [Google API Setup](GOOGLE_API_SETUP.md)
- [Tool Integration Guide](TOOL_INTEGRATION_GUIDE.md)
- [Production Ready](PRODUCTION_READY.md)

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test specific components
python -m pytest tests/test_core/
```

## 🚀 Deployment

```bash
# Docker deployment
cd deployment/docker
docker-compose up -d

# Kubernetes deployment
kubectl apply -f deployment/k8s/
```

## 📄 License

MIT License - see LICENSE file for details.
