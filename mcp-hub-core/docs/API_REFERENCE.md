# MCP Hub Core - API Reference

## Base URL
```
http://localhost:8000
```

## Authentication

The API uses JWT token-based authentication. Include the token in the Authorization header:

```bash
Authorization: Bearer <your_jwt_token>
```

## Endpoints Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/status` | GET | System status and health |
| `/api/chat/` | POST | Send chat message |
| `/api/chat/history` | GET | Get chat history |
| `/api/chat/history` | DELETE | Clear chat history |
| `/api/tools/` | GET | List all tools |
| `/api/tools/{tool_name}` | GET | Get tool details |
| `/api/tools/{tool_name}/execute` | POST | Execute tool |
| `/api/tools/servers` | GET | List servers |
| `/api/tools/servers/{server_name}/toggle` | POST | Toggle server |
| `/api/resources/` | GET | List resources |
| `/api/resources/{resource_name}` | GET | Get resource |
| `/api/resources/` | POST | Create resource |
| `/api/resources/{resource_name}` | PUT | Update resource |
| `/api/resources/{resource_name}` | DELETE | Delete resource |
| `/api/resources/servers/` | GET | List servers |
| `/api/resources/servers/` | POST | Create server |
| `/api/resources/servers/{server_name}` | DELETE | Delete server |
| `/api/auth/login` | POST | User login |
| `/api/auth/logout` | POST | User logout |
| `/api/auth/profile` | GET | Get user profile |

## System Status

### GET /api/status

Get system status and health information.

**Response:**
```json
{
  "tools": 10,
  "servers": 3,
  "resources": 5,
  "llm_providers": 3,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Chat API

### POST /api/chat/

Send a message to the AI assistant.

**Request Body:**
```json
{
  "message": "List all database tables",
  "provider": "openai",
  "max_tokens": 2000,
  "temperature": 0.3
}
```

**Parameters:**
- `message` (string, required): The user's message
- `provider` (string, optional): LLM provider ("openai", "google", "anthropic")
- `max_tokens` (integer, optional): Maximum tokens in response (default: 2000)
- `temperature` (float, optional): Response creativity (0.0-1.0, default: 0.3)

**Response:**
```json
{
  "response": "Found 3 tables in the database:\n• servers\n• resources\n• tools",
  "provider": "nlp-tools",
  "model": "natural-language-processor",
  "tokens_used": 0,
  "response_time": 0.15,
  "timestamp": "2024-01-15T10:30:00Z",
  "tool_executed": {
    "tool": "list_tables",
    "parameters": {},
    "result": {
      "tables": ["servers", "resources", "tools"],
      "count": 3
    },
    "success": true,
    "execution_time": 0.15
  }
}
```

### GET /api/chat/history

Get chat conversation history.

**Response:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "List all database tables",
      "timestamp": "2024-01-15T10:30:00Z"
    },
    {
      "role": "assistant",
      "content": "Found 3 tables in the database:\n• servers\n• resources\n• tools",
      "timestamp": "2024-01-15T10:30:05Z",
      "provider": "nlp-tools"
    }
  ]
}
```

### DELETE /api/chat/history

Clear chat conversation history.

**Response:**
```json
{
  "message": "Chat history cleared"
}
```

## Tools API

### GET /api/tools/

List all available tools.

**Response:**
```json
{
  "tools": [
    {
      "name": "list_tables",
      "server": "sqlite",
      "description": "List all tables in the SQLite database",
      "parameters": []
    },
    {
      "name": "query_database",
      "server": "sqlite",
      "description": "Execute a SQL query on the SQLite database",
      "parameters": [
        {
          "name": "query",
          "type": "string",
          "description": "SQL query to execute"
        }
      ]
    }
  ]
}
```

### GET /api/tools/{tool_name}

Get details for a specific tool.

**Example:** `GET /api/tools/query_database`

**Response:**
```json
{
  "name": "query_database",
  "server": "sqlite",
  "description": "Execute a SQL query on the SQLite database",
  "parameters": [
    {
      "name": "query",
      "type": "string",
      "description": "SQL query to execute"
    }
  ]
}
```

### POST /api/tools/{tool_name}/execute

Execute a specific tool.

**Example:** `POST /api/tools/query_database/execute`

**Request Body:**
```json
{
  "query": "SELECT COUNT(*) FROM tools"
}
```

**Response:**
```json
{
  "server": "sqlite",
  "tool": "query_database",
  "result": {
    "columns": ["COUNT(*)"],
    "rows": [[10]],
    "row_count": 1
  },
  "success": true
}
```

### GET /api/tools/servers

List all MCP servers.

**Response:**
```json
{
  "servers": [
    {
      "name": "sqlite",
      "uri": "sqlite:///mcp.db",
      "enabled": true,
      "description": "Local SQLite Database"
    },
    {
      "name": "filesystem",
      "uri": "file:///",
      "enabled": true,
      "description": "Local Filesystem Access"
    }
  ]
}
```

### POST /api/tools/servers/{server_name}/toggle

Toggle server enabled/disabled status.

**Request Body:**
```json
{
  "enabled": false
}
```

**Response:**
```json
{
  "message": "Server toggled successfully",
  "server": "sqlite",
  "enabled": false
}
```

## Resources API

### GET /api/resources/

List all resources.

**Response:**
```json
{
  "resources": [
    {
      "name": "mcp_database",
      "uri": "sqlite:///mcp.db",
      "server": "sqlite",
      "enabled": true
    },
    {
      "name": "local_files",
      "uri": "file:///",
      "server": "filesystem",
      "enabled": true
    }
  ]
}
```

### GET /api/resources/{resource_name}

Get details for a specific resource.

**Example:** `GET /api/resources/mcp_database`

**Response:**
```json
{
  "name": "mcp_database",
  "uri": "sqlite:///mcp.db",
  "server": "sqlite",
  "enabled": true
}
```

### POST /api/resources/

Create a new resource.

**Request Body:**
```json
{
  "name": "external_api",
  "uri": "https://api.example.com",
  "server_name": "external-server",
  "description": "External API resource"
}
```

**Response:**
```json
{
  "message": "Resource created successfully",
  "resource": {
    "name": "external_api",
    "uri": "https://api.example.com",
    "server_name": "external-server",
    "description": "External API resource"
  }
}
```

### PUT /api/resources/{resource_name}

Update an existing resource.

**Example:** `PUT /api/resources/external_api`

**Request Body:**
```json
{
  "uri": "https://api.example.com/v2",
  "server_name": "external-server",
  "description": "Updated external API resource"
}
```

**Response:**
```json
{
  "message": "Resource updated successfully"
}
```

### DELETE /api/resources/{resource_name}

Delete a resource.

**Example:** `DELETE /api/resources/external_api`

**Response:**
```json
{
  "message": "Resource deleted successfully"
}
```

### GET /api/resources/servers/

List all resource servers.

**Response:**
```json
{
  "servers": [
    {
      "name": "sqlite",
      "uri": "sqlite:///mcp.db",
      "enabled": true,
      "description": "Local SQLite Database"
    },
    {
      "name": "external-server",
      "uri": "https://api.example.com",
      "enabled": true,
      "description": "External API Server"
    }
  ]
}
```

### POST /api/resources/servers/

Create a new server.

**Request Body:**
```json
{
  "name": "external-server",
  "uri": "https://api.example.com",
  "description": "External API Server"
}
```

**Response:**
```json
{
  "message": "Server created successfully",
  "server": {
    "name": "external-server",
    "uri": "https://api.example.com",
    "description": "External API Server"
  }
}
```

### DELETE /api/resources/servers/{server_name}

Delete a server.

**Example:** `DELETE /api/resources/servers/external-server`

**Response:**
```json
{
  "message": "Server deleted successfully"
}
```

## Authentication API

### POST /api/auth/login

Authenticate user and get JWT token.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### POST /api/auth/logout

Logout user and invalidate token.

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

### GET /api/auth/profile

Get current user profile.

**Headers:**
```
Authorization: Bearer <your_jwt_token>
```

**Response:**
```json
{
  "username": "user@example.com",
  "email": "user@example.com",
  "role": "user",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "detail": "Error message",
  "status_code": 400,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Common Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Bad Request - Invalid parameters |
| 401 | Unauthorized - Missing or invalid authentication |
| 403 | Forbidden - Insufficient permissions |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Invalid data format |
| 500 | Internal Server Error - Server issues |

### Error Examples

**Validation Error (422):**
```json
{
  "detail": [
    {
      "loc": ["body", "message"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Not Found (404):**
```json
{
  "detail": "Resource not found"
}
```

**Unauthorized (401):**
```json
{
  "detail": "Not authenticated"
}
```

## WebSocket Support

### WebSocket Endpoint: `/ws`

Real-time communication for chat and tool execution.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

**Message Types:**

#### Chat Message
```json
{
  "type": "chat",
  "content": "Hello, how can I help you?"
}
```

#### Tool Execution
```json
{
  "type": "tool_execute",
  "tool_name": "list_tables",
  "arguments": {}
}
```

**Response Types:**

#### Chat Response
```json
{
  "type": "chat_response",
  "content": "Found 3 tables in the database",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Tool Result
```json
{
  "type": "tool_result",
  "result": {
    "tables": ["servers", "resources", "tools"],
    "count": 3
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Rate Limiting

API endpoints are rate-limited to prevent abuse:

- **Chat API**: 100 requests per minute per IP
- **Tool Execution**: 50 requests per minute per IP
- **Resource Management**: 20 requests per minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642248600
```

## SDK Examples

### Python
```python
import requests

# Chat API
response = requests.post('http://localhost:8000/api/chat/', json={
    'message': 'List database tables',
    'provider': 'openai'
})
print(response.json())

# Tool Execution
response = requests.post('http://localhost:8000/api/tools/query_database/execute', json={
    'query': 'SELECT COUNT(*) FROM tools'
})
print(response.json())
```

### JavaScript
```javascript
// Chat API
const response = await fetch('http://localhost:8000/api/chat/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    message: 'List database tables',
    provider: 'openai'
  })
});
const data = await response.json();
console.log(data);
```

### cURL
```bash
# Chat API
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "List database tables", "provider": "openai"}'

# Tool Execution
curl -X POST http://localhost:8000/api/tools/query_database/execute \
  -H "Content-Type: application/json" \
  -d '{"query": "SELECT COUNT(*) FROM tools"}'
```

## Testing

### Health Check
```bash
curl http://localhost:8000/api/status
```

### Interactive API Documentation
Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.

### OpenAPI Schema
The complete OpenAPI schema is available at `http://localhost:8000/openapi.json`.
