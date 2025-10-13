# MCP Hub UI

React Frontend for MCP Hub - Multi-LLM Tool Integration Platform

## 🎨 **Overview**

MCP Hub UI is a modern React frontend that provides:
- **Interactive Dashboard** - System overview and statistics
- **Real-time Chat** - AI conversation interface
- **Tool Management** - Execute and manage MCP tools
- **Resource Explorer** - Database and file exploration
- **Settings Panel** - Configuration and preferences

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
git clone https://github.com/your-org/mcp-hub-ui.git
cd mcp-hub-ui
```

### **2. Install Dependencies**
```bash
npm install
```

### **3. Environment Setup**
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your API URL
nano .env
```

### **4. Start Development Server**
```bash
npm start
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000

# Feature Flags
REACT_APP_ENABLE_WEBSOCKET=true
REACT_APP_ENABLE_ANALYTICS=false
```

## 🚀 **Running the Application**

### **Development**
```bash
# Start development server
npm start

# Open http://localhost:3000
```

### **Production Build**
```bash
# Build for production
npm run build

# Serve static files
npx serve -s build
```

### **Docker**
```bash
# Build Docker image
docker build -t mcp-hub-ui .

# Run container
docker run -p 3000:3000 mcp-hub-ui
```

## 🎯 **Features**

### **📊 Dashboard**
- System overview and statistics
- Tool and resource counts
- Recent activity feed
- Quick actions

### **💬 Chat Interface**
- Real-time AI conversations
- Tool execution integration
- Message history
- Typing indicators

### **🔧 Tool Management**
- Browse available tools
- Execute tools with parameters
- View execution results
- Tool status monitoring

### **🗄️ Resource Explorer**
- Database table exploration
- File system navigation
- Resource metadata
- Quick actions

### **⚙️ Settings**
- API key management
- Provider configuration
- Theme customization
- User preferences

## 🛠️ **Development**

### **Project Structure**
```
mcp-hub-ui/
├── public/             # Static files
├── src/
│   ├── components/    # Reusable components
│   ├── pages/         # Page components
│   ├── services/      # API services
│   ├── hooks/         # Custom hooks
│   ├── utils/         # Utility functions
│   └── App.js         # Main app component
├── package.json       # Dependencies
└── README.md         # This file
```

### **Key Technologies**
- **React 18** - UI framework
- **Material-UI** - Component library
- **React Query** - Data fetching
- **React Router** - Navigation
- **Socket.IO** - Real-time communication
- **Axios** - HTTP client

### **Adding New Features**
1. Create component in `src/components/`
2. Add route in `App.js`
3. Update navigation in `Layout.js`
4. Add API service if needed

### **Testing**
```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# Run linting
npm run lint
```

## 🎨 **UI Components**

### **Layout Components**
- `Layout` - Main application layout
- `Sidebar` - Navigation sidebar
- `Header` - Top navigation bar

### **Feature Components**
- `Dashboard` - System overview
- `Chat` - AI conversation interface
- `Tools` - Tool management
- `Resources` - Resource explorer
- `Settings` - Configuration panel

### **Shared Components**
- `ToolCard` - Tool display card
- `ResourceCard` - Resource display card
- `ChatMessage` - Chat message component
- `StatusIndicator` - Status display

## 🔌 **API Integration**

### **Services**
```javascript
// API service example
import { api } from './services/api';

// Get tools
const tools = await api.tools.getTools();

// Execute tool
const result = await api.tools.executeTool('query_database', {
  query: 'SELECT * FROM users'
});

// Send chat message
const response = await api.chat.sendMessage('Hello!');
```

### **WebSocket Integration**
```javascript
// WebSocket service
import { socket } from './services/websocket';

// Connect to WebSocket
socket.connect();

// Listen for messages
socket.on('chat_response', (data) => {
  console.log('AI Response:', data);
});

// Send message
socket.emit('chat', { content: 'Hello!' });
```

## 🎨 **Theming**

### **Custom Theme**
```javascript
// Custom Material-UI theme
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#dc004e' },
  },
  typography: {
    fontFamily: '"Roboto", "Helvetica", "Arial"',
  },
});
```

### **Dark Mode**
- Toggle between light/dark themes
- Persistent theme preference
- System theme detection

## 📱 **Responsive Design**

### **Breakpoints**
- **Mobile**: < 600px
- **Tablet**: 600px - 960px
- **Desktop**: > 960px

### **Mobile Features**
- Touch-friendly interface
- Swipe navigation
- Mobile-optimized chat
- Responsive tables

## 🔒 **Security**

### **API Security**
- HTTPS in production
- CORS configuration
- API key management
- Request validation

### **Client Security**
- Environment variable protection
- Secure WebSocket connections
- Input sanitization
- XSS protection

## 🚀 **Deployment**

### **Static Hosting**
```bash
# Build for production
npm run build

# Deploy to Netlify/Vercel
npm run deploy
```

### **Docker Deployment**
```dockerfile
# Multi-stage build
FROM node:18-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
```

### **Environment Configuration**
```bash
# Production environment
REACT_APP_API_URL=https://api.mcp-hub.com
REACT_APP_WS_URL=wss://api.mcp-hub.com
```

## 📊 **Performance**

### **Optimization**
- Code splitting
- Lazy loading
- Image optimization
- Bundle analysis

### **Monitoring**
- Performance metrics
- Error tracking
- User analytics
- API monitoring

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
- **Documentation**: Component docs
- **Community**: Discord/Forum links

---

**MCP Hub UI - Beautiful Interface for Multi-LLM Tool Integration** 🎨
