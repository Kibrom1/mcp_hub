# 🚀 MCP Hub - Multi-LLM Tool Integration Platform

A modern, separated architecture for integrating multiple LLM providers with MCP (Model Context Protocol) tools and resources.

## 📁 **Project Structure**

This repository contains two separate projects:

### 🔧 **mcp-hub-core** (Backend API)
- **FastAPI** backend with multi-LLM support
- **MCP tool execution** for database, filesystem, and memory operations
- **WebSocket** support for real-time communication
- **Secure API key management** with encryption
- **SQLite database** integration

### 🎨 **mcp-hub-ui** (Frontend React)
- **React** frontend with Material-UI
- **Real-time chat** interface with AI
- **Tool management** and execution interface
- **Resource explorer** for database and files
- **Responsive design** for all devices

---

## 🚀 **Quick Start**

### **1. Backend Setup**
```bash
cd mcp-hub-core

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from app.core.database import init_db; init_db()"

# Start the API server
python main.py
```

### **2. Frontend Setup**
```bash
cd mcp-hub-ui

# Install dependencies
npm install

# Setup environment
cp env.example .env
# Edit .env with your API URL

# Start development server
npm start
```

### **3. Access the Application**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

---

## 🎯 **Features**

### **🤖 Multi-LLM Support**
- **OpenAI GPT** - GPT-4, GPT-3.5-turbo
- **Google Gemini** - Gemini Pro, Gemini Pro Vision
- **Anthropic Claude** - Claude-3 Sonnet, Haiku, Opus

### **🔧 MCP Tools**
- **Database Operations** - SQL queries, table management
- **File System** - Read, write, list files and directories
- **Memory Store** - Store and retrieve information
- **Real-time Execution** - Execute tools via chat interface

### **💬 Chat Interface**
- **Real-time AI conversations** with WebSocket
- **Tool integration** - AI can use tools automatically
- **Message history** and persistence
- **Typing indicators** and status updates

### **📊 Dashboard**
- **System overview** and statistics
- **Tool and resource counts**
- **Health monitoring** and status
- **Quick actions** and navigation

### **🔒 Security**
- **Encrypted API key storage** with master password
- **Environment variable** support
- **CORS configuration** for cross-origin requests
- **Input validation** and sanitization

---

## 🏗️ **Architecture**

```
┌─────────────────┐    ┌─────────────────┐
│   mcp-hub-ui    │◄──►│   mcp-hub-core  │
│   (React)       │    │   (FastAPI)     │
│   Port: 3000    │    │   Port: 8000    │
└─────────────────┘    └─────────────────┘
```

### **Communication**
- **REST API** for data operations
- **WebSocket** for real-time chat
- **Environment variables** for configuration
- **CORS** properly configured

---

## 📚 **Documentation**

### **Backend (mcp-hub-core)**
- **API Reference**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **README**: `mcp-hub-core/README.md`

### **Frontend (mcp-hub-ui)**
- **Component Docs**: Built-in React documentation
- **README**: `mcp-hub-ui/README.md`

### **Utility Modules**
- **CRUD Generator**: moved to the new `utility` repository at `../utility/spring-boot-crud-generator`

---

## 🔧 **Configuration**

### **API Keys**
Set your API keys in `mcp-hub-core/.env`:
```bash
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
```

### **Environment Variables**
- **Backend**: `mcp-hub-core/env.example`
- **Frontend**: `mcp-hub-ui/env.example`

---

## 🚀 **Deployment**

### **Development**
```bash
# Backend
cd mcp-hub-core && python main.py

# Frontend
cd mcp-hub-ui && npm start
```

### **Production**
```bash
# Backend
cd mcp-hub-core
pip install -r requirements.txt
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# Frontend
cd mcp-hub-ui
npm run build
npx serve -s build
```

### **Docker**
```bash
# Backend
docker build -t mcp-hub-core ./mcp-hub-core
docker run -p 8000:8000 mcp-hub-core

# Frontend
docker build -t mcp-hub-ui ./mcp-hub-ui
docker run -p 3000:3000 mcp-hub-ui
```

---

## 🎯 **Benefits of Separation**

- ✅ **Independent deployment** - Deploy frontend/backend separately
- ✅ **Technology flexibility** - Use different tech stacks
- ✅ **Team scalability** - Different teams can work on each
- ✅ **Performance optimization** - Optimize each service independently
- ✅ **Easier maintenance** - Focused debugging and updates

---

## 🆘 **Support**

- **Backend Issues**: Check `mcp-hub-core/README.md`
- **Frontend Issues**: Check `mcp-hub-ui/README.md`
- **API Documentation**: http://localhost:8000/api/docs
- **GitHub Issues**: Create issues in respective repositories

---

## 📄 **License**

MIT License - see LICENSE file for details

---

**🎉 MCP Hub - Modern Multi-LLM Tool Integration Platform**

**Ready for development, deployment, and scaling! 🚀**