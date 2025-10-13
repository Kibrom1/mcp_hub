# MCP Hub Core

Backend API for MCP Hub - Multi-LLM Tool Integration Platform

## 🚀 **Overview**

MCP Hub Core is the backend API that provides:
- **LLM Integration** - OpenAI, Google Gemini, Anthropic Claude
- **MCP Tool Execution** - Database, filesystem, memory operations
- **Real-time Communication** - WebSocket support
- **Secure API** - Encrypted API key management

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐
│   mcp-hub-ui    │◄──►│   mcp-hub-core  │
│   (React)       │    │   (FastAPI)     │
└─────────────────┘    └─────────────────┘
```

## 📦 **Installation**

### **1. Clone Repository**
```bash
git clone https://github.com/your-org/mcp-hub-core.git
cd mcp-hub-core
```

### **2. Create Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API keys
nano .env
```

### **5. Initialize Database**
```bash
python -c "from app.core.database import init_db; init_db()"
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# API Keys
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Database
DATABASE_URL=sqlite:///mcp.db

# Security
SECRET_KEY=your_secret_key_here

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## 🚀 **Running the API**

### **Development**
```bash
# Start the API server
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### **Production**
```bash
# Using gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## 📚 **API Documentation**

Once running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## 🔌 **API Endpoints**

### **Health & Status**
- `GET /` - Root endpoint
- `GET /api/health` - Health check
- `GET /api/status` - System status

### **Tools**
- `GET /api/tools` - List all tools
- `GET /api/tools/{tool_name}` - Get tool details
- `POST /api/tools/{tool_name}/execute` - Execute tool
- `GET /api/tools/servers` - List servers
- `POST /api/tools/servers/{server_name}/toggle` - Toggle server

### **Chat**
- `POST /api/chat/` - Send chat message
- `GET /api/chat/history` - Get chat history
- `DELETE /api/chat/history` - Clear chat history

### **Resources**
- `GET /api/resources/` - List resources
- `GET /api/resources/{resource_name}` - Get resource details

### **WebSocket**
- `WS /ws` - WebSocket connection for real-time communication

## 🛠️ **Development**

### **Project Structure**
```
mcp-hub-core/
├── app/
│   ├── api/           # API routes
│   ├── core/          # Core configuration
│   ├── models/        # Data models
│   └── services/      # Business logic
├── main.py            # FastAPI app
├── requirements.txt   # Dependencies
└── README.md         # This file
```

### **Adding New Endpoints**
1. Create route in `app/api/`
2. Add to main.py router
3. Update documentation

### **Testing**
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

## 🔒 **Security**

### **API Key Management**
- Encrypted storage with master password
- Environment variable support
- Docker secrets integration
- Cloud secret management

### **Authentication**
- JWT token support
- API key authentication
- CORS configuration

## 🐳 **Docker Deployment**

### **Build Image**
```bash
docker build -t mcp-hub-core .
```

### **Run Container**
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e GOOGLE_API_KEY=your_key \
  mcp-hub-core
```

### **Docker Compose**
```yaml
version: '3.8'
services:
  mcp-hub-core:
    build: .
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./data:/app/data
```

## 📊 **Monitoring**

### **Health Checks**
- `/api/health` - Basic health check
- `/api/status` - Detailed system status

### **Logging**
- Structured logging with timestamps
- Request/response logging
- Error tracking

## 🤝 **Contributing**

1. Fork the repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

## 📄 **License**

MIT License - see LICENSE file for details

## 🆘 **Support**

- **Issues**: GitHub Issues
- **Documentation**: API docs at `/api/docs`
- **Community**: Discord/Forum links

---

**MCP Hub Core - Powering the Multi-LLM Tool Integration Platform** 🚀
