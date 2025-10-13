# MCP Hub Core - Deployment Guide

## Overview

This guide covers deploying MCP Hub Core in various environments, from development to production. The backend is designed to be containerized and scalable.

## Deployment Architecture

```mermaid
graph TB
    subgraph "Load Balancer"
        LB[Nginx/HAProxy]
    end
    
    subgraph "Application Layer"
        APP1[MCP Hub Core Instance 1]
        APP2[MCP Hub Core Instance 2]
        APP3[MCP Hub Core Instance N]
    end
    
    subgraph "Database Layer"
        DB[(SQLite/PostgreSQL)]
        REDIS[(Redis Cache)]
    end
    
    subgraph "External Services"
        OPENAI[OpenAI API]
        GOOGLE[Google Gemini]
        ANTHROPIC[Anthropic Claude]
    end
    
    subgraph "Monitoring"
        LOGS[Log Aggregation]
        METRICS[Metrics Collection]
        ALERTS[Alerting]
    end
    
    LB --> APP1
    LB --> APP2
    LB --> APP3
    
    APP1 --> DB
    APP2 --> DB
    APP3 --> DB
    
    APP1 --> REDIS
    APP2 --> REDIS
    APP3 --> REDIS
    
    APP1 --> OPENAI
    APP1 --> GOOGLE
    APP1 --> ANTHROPIC
    
    APP1 --> LOGS
    APP2 --> LOGS
    APP3 --> LOGS
```

## Prerequisites

### System Requirements
- Python 3.8+
- 2GB RAM minimum (4GB recommended)
- 10GB disk space
- Network access to LLM APIs

### Software Dependencies
- Docker (for containerized deployment)
- Docker Compose (for multi-service deployment)
- Git (for source code management)

## Development Deployment

### 1. Local Development Setup

```bash
# Clone repository
git clone https://github.com/Kibrom1/mcp_hub.git
cd mcp_hub/mcp-hub-core

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env.example .env
# Edit .env with your API keys

# Initialize database
python -c "from app.core.database import init_db; init_db()"

# Run development server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Environment Configuration

Create `.env` file:
```bash
# LLM Provider API Keys
OPENAI_API_KEY=your_openai_key_here
GOOGLE_API_KEY=your_google_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here

# Application Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
DATABASE_URL=sqlite:///mcp.db
LOG_LEVEL=INFO

# Security
SECRET_KEY=your_secret_key_here
JWT_SECRET=your_jwt_secret_here

# Optional: Redis for caching
REDIS_URL=redis://localhost:6379
```

## Docker Deployment

### 1. Single Container Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/status || exit 1

# Run application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**
```bash
# Build image
docker build -t mcp-hub-core .

# Run container
docker run -d \
  --name mcp-hub-core \
  -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e GOOGLE_API_KEY=your_key \
  -e ANTHROPIC_API_KEY=your_key \
  mcp-hub-core
```

### 2. Docker Compose Deployment

**docker-compose.yml:**
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
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - CORS_ORIGINS=http://localhost:3000,http://localhost:3001
      - DATABASE_URL=sqlite:///app/mcp.db
      - LOG_LEVEL=INFO
    volumes:
      - ./data:/app/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/status"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - mcp-hub-core
    restart: unless-stopped

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

**Deploy:**
```bash
# Create environment file
echo "OPENAI_API_KEY=your_key" > .env
echo "GOOGLE_API_KEY=your_key" >> .env
echo "ANTHROPIC_API_KEY=your_key" >> .env

# Deploy services
docker-compose up -d

# Check status
docker-compose ps
```

## Production Deployment

### 1. Kubernetes Deployment

**k8s/namespace.yaml:**
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: mcp-hub
```

**k8s/configmap.yaml:**
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-hub-config
  namespace: mcp-hub
data:
  CORS_ORIGINS: "https://yourdomain.com"
  DATABASE_URL: "postgresql://user:pass@postgres:5432/mcp_hub"
  LOG_LEVEL: "INFO"
```

**k8s/secret.yaml:**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mcp-hub-secrets
  namespace: mcp-hub
type: Opaque
data:
  openai-api-key: <base64-encoded-key>
  google-api-key: <base64-encoded-key>
  anthropic-api-key: <base64-encoded-key>
  secret-key: <base64-encoded-secret>
  jwt-secret: <base64-encoded-jwt-secret>
```

**k8s/deployment.yaml:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-hub-core
  namespace: mcp-hub
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-hub-core
  template:
    metadata:
      labels:
        app: mcp-hub-core
    spec:
      containers:
      - name: mcp-hub-core
        image: mcp-hub-core:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-hub-secrets
              key: openai-api-key
        - name: GOOGLE_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-hub-secrets
              key: google-api-key
        - name: ANTHROPIC_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-hub-secrets
              key: anthropic-api-key
        envFrom:
        - configMapRef:
            name: mcp-hub-config
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /api/status
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/status
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

**k8s/service.yaml:**
```yaml
apiVersion: v1
kind: Service
metadata:
  name: mcp-hub-core-service
  namespace: mcp-hub
spec:
  selector:
    app: mcp-hub-core
  ports:
  - port: 80
    targetPort: 8000
  type: ClusterIP
```

**k8s/ingress.yaml:**
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-hub-ingress
  namespace: mcp-hub
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - api.yourdomain.com
    secretName: mcp-hub-tls
  rules:
  - host: api.yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: mcp-hub-core-service
            port:
              number: 80
```

**Deploy to Kubernetes:**
```bash
# Apply configurations
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml

# Check deployment
kubectl get pods -n mcp-hub
kubectl get services -n mcp-hub
```

### 2. AWS ECS Deployment

**ecs-task-definition.json:**
```json
{
  "family": "mcp-hub-core",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "512",
  "memory": "1024",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "mcp-hub-core",
      "image": "your-account.dkr.ecr.region.amazonaws.com/mcp-hub-core:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "CORS_ORIGINS",
          "value": "https://yourdomain.com"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:mcp-hub/openai-api-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/mcp-hub-core",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 3. Google Cloud Run Deployment

**cloudbuild.yaml:**
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/mcp-hub-core', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/mcp-hub-core']
  - name: 'gcr.io/cloud-builders/gcloud'
    args: [
      'run', 'deploy', 'mcp-hub-core',
      '--image', 'gcr.io/$PROJECT_ID/mcp-hub-core',
      '--region', 'us-central1',
      '--platform', 'managed',
      '--allow-unauthenticated'
    ]
```

**Deploy:**
```bash
# Build and deploy
gcloud builds submit --config cloudbuild.yaml

# Set environment variables
gcloud run services update mcp-hub-core \
  --set-env-vars="OPENAI_API_KEY=your_key" \
  --set-env-vars="GOOGLE_API_KEY=your_key"
```

## Database Configuration

### 1. SQLite (Development)
```bash
# Default configuration
DATABASE_URL=sqlite:///mcp.db
```

### 2. PostgreSQL (Production)
```bash
# Environment variables
DATABASE_URL=postgresql://user:password@host:5432/mcp_hub

# Connection pool settings
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
```

**PostgreSQL Setup:**
```sql
-- Create database
CREATE DATABASE mcp_hub;

-- Create user
CREATE USER mcp_user WITH PASSWORD 'secure_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE mcp_hub TO mcp_user;
```

## Monitoring and Logging

### 1. Prometheus Metrics

**metrics.py:**
```python
from prometheus_client import Counter, Histogram, generate_latest

# Metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
LLM_REQUESTS = Counter('llm_requests_total', 'Total LLM requests', ['provider'])
TOOL_EXECUTIONS = Counter('tool_executions_total', 'Total tool executions', ['tool_name'])
```

### 2. ELK Stack Integration

**logstash.conf:**
```ruby
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "mcp-hub-core" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "mcp-hub-logs-%{+YYYY.MM.dd}"
  }
}
```

### 3. Health Checks

**health.py:**
```python
from fastapi import APIRouter
import asyncio

router = APIRouter()

@router.get("/health")
async def health_check():
    checks = {
        "database": await check_database(),
        "llm_providers": await check_llm_providers(),
        "redis": await check_redis()
    }
    
    status = "healthy" if all(checks.values()) else "unhealthy"
    
    return {
        "status": status,
        "checks": checks,
        "timestamp": datetime.now().isoformat()
    }
```

## Security Configuration

### 1. SSL/TLS Setup

**nginx.conf:**
```nginx
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    location / {
        proxy_pass http://mcp-hub-core:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Rate Limiting

**rate_limiting.py:**
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/chat/")
@limiter.limit("100/minute")
async def chat_endpoint(request: Request, ...):
    # Chat logic
    pass
```

### 3. Authentication

**auth.py:**
```python
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def verify_token(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

## Backup and Recovery

### 1. Database Backup

**backup.sh:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"
DB_NAME="mcp_hub"

# PostgreSQL backup
pg_dump $DB_NAME > $BACKUP_DIR/mcp_hub_$DATE.sql

# Compress backup
gzip $BACKUP_DIR/mcp_hub_$DATE.sql

# Upload to S3
aws s3 cp $BACKUP_DIR/mcp_hub_$DATE.sql.gz s3://your-backup-bucket/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "*.sql.gz" -mtime +30 -delete
```

### 2. Configuration Backup

**config_backup.sh:**
```bash
#!/bin/bash
# Backup configuration files
tar -czf /backups/config_$(date +%Y%m%d).tar.gz \
  /etc/nginx/nginx.conf \
  /etc/ssl/certs/ \
  /app/.env
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Issues
```bash
# Check database connectivity
python -c "from app.core.database import init_db; init_db()"

# Check database file permissions
ls -la mcp.db
chmod 664 mcp.db
```

#### 2. API Key Issues
```bash
# Verify environment variables
echo $OPENAI_API_KEY
echo $GOOGLE_API_KEY

# Test API connectivity
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

#### 3. Memory Issues
```bash
# Check memory usage
docker stats mcp-hub-core

# Increase memory limits
docker run -m 2g mcp-hub-core
```

#### 4. Port Conflicts
```bash
# Check port usage
lsof -i :8000
netstat -tulpn | grep :8000

# Use different port
uvicorn main:app --port 8001
```

### Log Analysis

```bash
# View application logs
docker logs mcp-hub-core -f

# Filter error logs
docker logs mcp-hub-core 2>&1 | grep ERROR

# Check system logs
journalctl -u mcp-hub-core -f
```

## Performance Optimization

### 1. Database Optimization
```python
# Connection pooling
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

### 2. Caching
```python
# Redis caching
import redis
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expiry=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, expiry, json.dumps(result))
            return result
        return wrapper
    return decorator
```

### 3. Load Balancing
```nginx
upstream mcp_hub_backend {
    server mcp-hub-core-1:8000;
    server mcp-hub-core-2:8000;
    server mcp-hub-core-3:8000;
}

server {
    location / {
        proxy_pass http://mcp_hub_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Scaling Considerations

### Horizontal Scaling
- Use load balancer to distribute traffic
- Implement session affinity if needed
- Use shared database for state consistency
- Implement proper health checks

### Vertical Scaling
- Increase CPU and memory resources
- Optimize database queries
- Implement caching strategies
- Use connection pooling

### Auto-scaling
```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: mcp-hub-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: mcp-hub-core
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

This comprehensive deployment guide covers all aspects of deploying MCP Hub Core from development to production environments with proper monitoring, security, and scaling considerations.
