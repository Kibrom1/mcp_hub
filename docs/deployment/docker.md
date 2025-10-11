# 🐳 Docker Deployment

Deploy MCP Hub using Docker containers for easy deployment and scaling.

## 🚀 **Quick Start**

### **Using Docker Compose**

```bash
# Clone the repository
git clone https://github.com/your-org/mcp-hub.git
cd mcp-hub

# Set environment variables
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-key"

# Start the application
docker-compose up -d
```

**Access at: http://localhost:8501**

## 📁 **Docker Configuration**

### **Dockerfile**

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 mcpuser && chown -R mcpuser:mcpuser /app
USER mcpuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Start application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### **docker-compose.yml**

```yaml
version: '3.8'

services:
  mcp-hub:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Add database service
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mcp_hub
      POSTGRES_USER: mcp_user
      POSTGRES_PASSWORD: mcp_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

## 🔧 **Configuration**

### **Environment Variables**

```bash
# Required: API Keys
OPENAI_API_KEY=your-openai-key
GOOGLE_API_KEY=your-google-key

# Optional: Application settings
MCP_HUB_PORT=8501
MCP_HUB_HOST=0.0.0.0
MCP_HUB_DEBUG=false

# Optional: Database settings
DATABASE_URL=postgresql://mcp_user:mcp_password@postgres:5432/mcp_hub
```

### **Volume Mounts**

```yaml
volumes:
  - ./data:/app/data          # Persistent data storage
  - ./logs:/app/logs          # Application logs
  - ./config:/app/config      # Configuration files
```

## 🚀 **Production Deployment**

### **Production Docker Compose**

```yaml
version: '3.8'

services:
  mcp-hub:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - MCP_HUB_DEBUG=false
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - mcp-hub
    restart: unless-stopped

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mcp_hub
      POSTGRES_USER: mcp_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres_data:
```

### **Nginx Configuration**

```nginx
events {
    worker_connections 1024;
}

http {
    upstream mcp_hub {
        server mcp-hub:8501;
    }

    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://mcp_hub;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
```

## 🔧 **Development Setup**

### **Development Docker Compose**

```yaml
version: '3.8'

services:
  mcp-hub-dev:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - MCP_HUB_DEBUG=true
    volumes:
      - .:/app
      - /app/venv
    command: ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.runOnSave=true"]
    restart: unless-stopped
```

## 📊 **Monitoring**

### **Health Checks**

```bash
# Check container health
docker-compose ps

# Check application health
curl http://localhost:8501/_stcore/health

# View logs
docker-compose logs -f mcp-hub
```

### **Logging**

```yaml
# Add logging configuration
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

## 🔒 **Security**

### **Security Best Practices**

```dockerfile
# Use non-root user
USER mcpuser

# Remove unnecessary packages
RUN apt-get autoremove -y && apt-get clean

# Set secure permissions
RUN chmod 755 /app && chmod 644 /app/*.py
```

### **Environment Security**

```bash
# Use secrets management
docker-compose --env-file .env.production up -d
```

## 🚀 **Scaling**

### **Horizontal Scaling**

```yaml
services:
  mcp-hub:
    # ... configuration ...
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
```

## 🆘 **Troubleshooting**

### **Common Issues**

#### **Container won't start**
```bash
# Check logs
docker-compose logs mcp-hub

# Check environment variables
docker-compose config
```

#### **Port conflicts**
```bash
# Change port in docker-compose.yml
ports:
  - "8502:8501"  # Use port 8502 instead
```

#### **Permission issues**
```bash
# Fix volume permissions
sudo chown -R 1000:1000 ./data
```

---

**For Kubernetes deployment, see [Kubernetes Guide](kubernetes.md)**
