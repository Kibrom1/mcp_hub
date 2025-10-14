# 🐳 MCP Hub Docker Setup Guide

This guide will help you set up the complete MCP Hub environment using Docker with PostgreSQL, Redis, and all services.

## 📋 Prerequisites

- **Docker** (version 20.10+)
- **Docker Compose** (version 2.0+)
- **Git** (for cloning the repository)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd mcp_hub
```

### 2. Run the Setup Script
```bash
./setup-docker.sh
```

This script will:
- Create the `.env` file from template
- Build and start all services
- Wait for services to be ready
- Display connection information

## 🔧 Manual Setup

If you prefer to set up manually:

### 1. Create Environment File
```bash
cp env.example .env
```

Edit `.env` with your actual values:
```bash
# Required API Keys
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Database (default values work for Docker)
DATABASE_URL=postgresql://postgres:mcp_hub_password@postgres:5432/mcp_hub
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_DB=mcp_hub
POSTGRES_USER=postgres
POSTGRES_PASSWORD=mcp_hub_password

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-super-secret-key-change-in-production
```

### 2. Start Services
```bash
# Build and start all services
docker-compose up --build -d

# Check status
docker-compose ps
```

### 3. Verify Services
```bash
# Check PostgreSQL
docker-compose exec postgres pg_isready -U postgres

# Check Redis
docker-compose exec redis redis-cli ping

# Check Backend
curl http://localhost:8000/health

# Check Frontend
curl http://localhost:3000
```

## 📊 Service Details

| Service | Port | Description |
|---------|------|-------------|
| **Frontend** | 3000 | React UI |
| **Backend** | 8000 | FastAPI API |
| **PostgreSQL** | 5432 | Database |
| **Redis** | 6379 | Cache & Sessions |

## 🔗 Connection Details

### PostgreSQL Connection
```bash
Host: localhost
Port: 5432
Database: mcp_hub
Username: postgres
Password: mcp_hub_password
```

### Redis Connection
```bash
Host: localhost
Port: 6379
Database: 0
```

### API Endpoints
```bash
# Health Check
GET http://localhost:8000/health

# API Documentation
GET http://localhost:8000/docs

# WebSocket
WS ws://localhost:8000/ws
```

## 🛠️ Management Commands

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f mcp-hub-core
docker-compose logs -f postgres
docker-compose logs -f redis
```

### Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Restart Services
```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart mcp-hub-core
```

### Update Services
```bash
# Pull latest images and rebuild
docker-compose pull
docker-compose up --build -d
```

## 🗄️ Database Management

### Connect to PostgreSQL
```bash
# Using Docker
docker-compose exec postgres psql -U postgres -d mcp_hub

# Using external client
psql -h localhost -p 5432 -U postgres -d mcp_hub
```

### Backup Database
```bash
# Create backup
docker-compose exec postgres pg_dump -U postgres mcp_hub > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres mcp_hub < backup.sql
```

### Reset Database
```bash
# Stop services
docker-compose down

# Remove volumes
docker-compose down -v

# Start services (will recreate database)
docker-compose up --build -d
```

## 🔍 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000
lsof -i :5432

# Kill the process
kill -9 <PID>
```

#### 2. Permission Denied
```bash
# Fix file permissions
sudo chown -R $USER:$USER .
chmod +x setup-docker.sh
```

#### 3. Database Connection Failed
```bash
# Check PostgreSQL logs
docker-compose logs postgres

# Check if PostgreSQL is ready
docker-compose exec postgres pg_isready -U postgres
```

#### 4. Services Not Starting
```bash
# Check all logs
docker-compose logs

# Check specific service
docker-compose logs mcp-hub-core
```

### Reset Everything
```bash
# Stop and remove everything
docker-compose down -v
docker system prune -a

# Start fresh
./setup-docker.sh
```

## 📈 Monitoring

### Health Checks
```bash
# Check service health
docker-compose ps

# Check resource usage
docker stats

# Check logs
docker-compose logs -f --tail=100
```

### Performance Monitoring
```bash
# Monitor database
docker-compose exec postgres psql -U postgres -d mcp_hub -c "SELECT * FROM system_status;"

# Monitor Redis
docker-compose exec redis redis-cli info memory
```

## 🔒 Security Notes

1. **Change Default Passwords**: Update PostgreSQL password in production
2. **API Keys**: Never commit API keys to version control
3. **Network Security**: Use proper firewall rules in production
4. **SSL/TLS**: Enable HTTPS in production
5. **Database Access**: Restrict database access to application only

## 🚀 Production Deployment

For production deployment:

1. **Use Production Images**: Use specific version tags
2. **Environment Variables**: Use secure secret management
3. **Database**: Use managed PostgreSQL service
4. **Monitoring**: Add proper monitoring and logging
5. **Backup**: Set up automated backups
6. **SSL**: Use reverse proxy with SSL termination

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Redis Documentation](https://redis.io/documentation)

## 🆘 Support

If you encounter issues:

1. Check the logs: `docker-compose logs -f`
2. Verify environment variables in `.env`
3. Ensure all ports are available
4. Check Docker and Docker Compose versions
5. Review the troubleshooting section above

---

**Happy coding! 🎉**
