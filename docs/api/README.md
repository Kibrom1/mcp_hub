# 🔧 API Documentation

Complete API reference for MCP Hub components.

## 📚 **API Overview**

MCP Hub provides several APIs for different functionalities:

- **LLM Providers API**: Multi-LLM provider management
- **MCP Client API**: MCP tool integration
- **Tool Discovery API**: Discovering and managing tools
- **Database API**: Data persistence and retrieval

## 🤖 **LLM Providers API**

### **LLMProvider Interface**

```python
class LLMProvider:
    def __init__(self, api_key: str, model: str)
    async def generate_response(self, messages: List[Dict], **kwargs) -> LLMResponse
    def is_available(self) -> bool
```

### **Available Providers**

#### **OpenAI Provider**
```python
from llm_providers import OpenAIProvider

provider = OpenAIProvider(
    api_key="your-openai-key",
    model="gpt-4o-mini"
)

response = await provider.generate_response(
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=1000,
    temperature=0.3
)
```

#### **Google Provider**
```python
from llm_providers import GoogleProvider

provider = GoogleProvider(
    api_key="your-google-key",
    model="gemini-2.0-flash"
)

response = await provider.generate_response(
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=1000,
    temperature=0.3
)
```

### **LLM Manager**

```python
from llm_providers import get_llm_manager

# Get manager instance
llm_manager = get_llm_manager()

# List available providers
providers = llm_manager.list_available_providers()

# Generate response
response = await llm_manager.generate_response(
    messages=[{"role": "user", "content": "Hello!"}],
    provider="openai",  # or "google"
    max_tokens=1000,
    temperature=0.3
)
```

## 🛠️ **MCP Client API**

### **Tool Execution**

```python
# Direct tool execution (simplified)
def execute_mcp_tool(server_name: str, tool_name: str, arguments: dict):
    """Execute an MCP tool directly"""
    # Implementation handles tool execution
    return {
        "server": server_name,
        "tool": tool_name,
        "arguments": arguments,
        "result": "Tool execution result",
        "success": True
    }
```

### **Available Tools**

#### **Filesystem Tools**
```python
# Read file
result = execute_mcp_tool("filesystem", "read_file", {
    "path": "/path/to/file.txt"
})

# Write file
result = execute_mcp_tool("filesystem", "write_file", {
    "path": "/path/to/file.txt",
    "content": "File content here"
})

# List directory
result = execute_mcp_tool("filesystem", "list_directory", {
    "path": "/path/to/directory"
})
```

#### **Memory Tools**
```python
# Store memory
result = execute_mcp_tool("memory", "store_memory", {
    "key": "project-notes",
    "value": "Important project information"
})

# Retrieve memory
result = execute_mcp_tool("memory", "retrieve_memory", {
    "key": "project-notes"
})

# List memories
result = execute_mcp_tool("memory", "list_memories", {})
```

## 🔍 **Tool Discovery API**

### **Discovering Tools**

```python
# Discover tools from servers
import asyncio
from discover_tools import discover_tools_from_server

async def discover_tools():
    result = await discover_tools_from_server(
        server_name="filesystem",
        server_uri="npx @modelcontextprotocol/server-filesystem /Users"
    )
    return result
```

### **Managing Servers**

```python
# Add MCP servers
from add_mcp_servers import add_sample_servers

# Add servers to database
add_sample_servers()

# List available servers
from list_tools import list_servers
servers = list_servers()
```

## 💾 **Database API**

### **Database Models**

```python
# Server model
class MCPServer:
    name: str
    uri: str
    enabled: bool
    created_at: datetime
    last_used: datetime

# Tool model
class MCPTool:
    server_name: str
    name: str
    description: str
    parameters: str  # JSON string
    enabled: bool

# Resource model
class MCPResource:
    server_name: str
    name: str
    uri: str
    enabled: bool
```

### **Database Operations**

```python
import sqlite3

# Connect to database
conn = sqlite3.connect('mcp.db')
cursor = conn.cursor()

# Query servers
cursor.execute("SELECT name, uri, enabled FROM servers")
servers = cursor.fetchall()

# Query tools
cursor.execute("SELECT server_name, name, description FROM tools")
tools = cursor.fetchall()

# Query resources
cursor.execute("SELECT server_name, name, uri FROM resources")
resources = cursor.fetchall()

conn.close()
```

## 🔄 **Response Models**

### **LLMResponse**

```python
@dataclass
class LLMResponse:
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    response_time: float = 0.0
```

### **Tool Execution Result**

```python
{
    "server": "filesystem",
    "tool": "read_file",
    "arguments": {"path": "/path/to/file.txt"},
    "result": "File contents here",
    "success": True,
    "error": None
}
```

## 🚨 **Error Handling**

### **Common Exceptions**

```python
# LLM Provider errors
class LLMProviderError(Exception):
    """Base exception for LLM provider errors"""
    pass

# MCP Tool errors
class MCPToolError(Exception):
    """Base exception for MCP tool errors"""
    pass

# Database errors
class DatabaseError(Exception):
    """Base exception for database errors"""
    pass
```

### **Error Response Format**

```python
{
    "error": "Error message",
    "server": "server_name",
    "tool": "tool_name",
    "success": False
}
```

## 📝 **Usage Examples**

### **Complete Example**

```python
import asyncio
from llm_providers import get_llm_manager

async def main():
    # Initialize LLM manager
    llm_manager = get_llm_manager()
    
    # Create messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to tools."},
        {"role": "user", "content": "List files in my home directory"}
    ]
    
    # Generate response
    response = await llm_manager.generate_response(
        messages,
        provider="openai",
        max_tokens=1000,
        temperature=0.3
    )
    
    print(f"Response: {response.content}")
    print(f"Model: {response.model}")
    print(f"Response time: {response.response_time:.2f}s")

# Run the example
asyncio.run(main())
```

## 🔧 **Configuration**

### **Environment Variables**

```bash
# LLM Provider API Keys
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"

# Optional: Model overrides
export OPENAI_MODEL="gpt-4o-mini"
export GOOGLE_MODEL="gemini-2.0-flash"
```

### **Configuration Files**

```yaml
# config.yaml
app:
  title: "MCP Hub"
  layout: "wide"

database:
  url: "sqlite:///mcp.db"
  echo: false

ai:
  model: "gpt-4o-mini"
  max_tokens: 1000
  temperature: 0.3

security:
  rate_limit: 100
  max_attempts: 3
```

---

**For more examples, see the [Examples Directory](../examples/)**
