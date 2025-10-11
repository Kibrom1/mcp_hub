# 🚀 Quick Start Guide

Get up and running with MCP Hub in under 5 minutes!

## ⚡ **Prerequisites**

- Python 3.8 or higher
- Node.js and npm (for MCP servers)
- OpenAI API key (optional)
- Google API key (optional)

## 🏃‍♂️ **Quick Setup**

### 1. **Clone and Setup**
```bash
git clone https://github.com/your-org/mcp-hub.git
cd mcp-hub
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. **Configure API Keys**
```bash
# Optional: Set OpenAI API key
export OPENAI_API_KEY="your-openai-key"

# Optional: Set Google API key  
export GOOGLE_API_KEY="your-google-key"
```

### 3. **Discover Tools**
```bash
# Add MCP servers
python add_mcp_servers.py --add

# Discover available tools
python discover_tools.py
```

### 4. **Run Application**
```bash
./run.sh
```

**🎉 That's it! Access your MCP Hub at: http://localhost:8501**

## 🎯 **First Steps**

### **1. Explore the Interface**
- **Sidebar**: View available tools and resources
- **Chat**: Interact with AI assistants
- **File Operations**: Create and manage files

### **2. Try File Operations**
1. Go to **Sidebar** → **Resources** → **filesystem**
2. Click **"📝 Text File"** template
3. Click **"📝 Create File"**
4. See your file created!

### **3. Test AI Chat**
1. In the chat, ask: "List files in my home directory"
2. Watch the AI use MCP tools to respond
3. Try: "Create a Python script that prints hello"

## 🛠️ **Available Tools**

### **Filesystem Server**
- `read_file` - Read file contents
- `write_file` - Write content to files
- `list_directory` - List directory contents

### **Memory Server**
- `store_memory` - Store information
- `retrieve_memory` - Retrieve stored information
- `list_memories` - List all stored memories

## 🤖 **LLM Providers**

### **OpenAI** (if API key provided)
- Model: GPT-4o-mini
- Features: Tool execution, code generation

### **Google Gemini** (if API key provided)
- Model: gemini-2.0-flash
- Features: Fast responses, tool integration

## 🎯 **Example Queries**

Try these in the chat interface:

```
"List files in my Documents folder"
"Create a markdown file with project notes"
"Store a memory about our conversation"
"What tools do I have available?"
"Read the contents of my README file"
```

## 🆘 **Troubleshooting**

### **No Tools Available**
```bash
python discover_tools.py
```

### **API Key Issues**
- Check your API keys are set correctly
- Verify you have credits/quota available

### **Port Already in Use**
```bash
# Kill existing processes
pkill -f streamlit
./run.sh
```

## 🚀 **Next Steps**

- [User Manual](user-manual.md) - Complete user guide
- [Tool Integration](tool-integration.md) - Advanced tool usage
- [LLM Providers](llm-providers.md) - Configure AI models
- [File Operations](file-operations.md) - File management guide

---

**Welcome to MCP Hub! 🎉**
