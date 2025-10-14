# 🗄️ Multi-Database Support for MCP Hub

This guide explains how to set up and use multiple database connections in your MCP Hub, allowing the chat interface to interact with all configured databases.

## 🚀 **Quick Start**

### **1. Setup Multiple Databases**
```bash
# Run the database setup script
./setup-databases.sh
```

### **2. Start MCP Hub**
```bash
# Start the backend
cd mcp-hub-core
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### **3. Test Database Integration**
Open the chat interface and try these queries:
- "Show me all available databases"
- "What tables are in the mcp_hub database?"
- "Search for user data across all databases"
- "Check the health of all databases"

## 📊 **Supported Database Types**

| Database Type | Status | Features |
|---------------|--------|----------|
| **PostgreSQL** | ✅ Full Support | Connection pooling, async queries, schema introspection |
| **SQLite** | ✅ Full Support | File-based, lightweight, perfect for development |
| **MySQL** | 🔄 Partial Support | Basic connection support |
| **MongoDB** | 📋 Planned | Document database support |

## 🔧 **Configuration**

### **Database Configuration Format**
```json
{
  "name": "database_name",
  "type": "postgresql|sqlite|mysql",
  "host": "localhost",
  "port": 5432,
  "database": "database_name",
  "username": "username",
  "password": "password",
  "is_active": true,
  "max_connections": 10,
  "timeout": 30
}
```

### **Adding Databases via API**
```bash
# Add a new PostgreSQL database
curl -X POST "http://localhost:8000/api/databases/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "production_db",
    "type": "postgresql",
    "host": "prod-server.com",
    "port": 5432,
    "database": "production",
    "username": "prod_user",
    "password": "secure_password",
    "is_active": true
  }'
```

## 💬 **Chat Integration Examples**

### **Schema Queries**
```
User: "Show me the schema of all databases"
Response: [Shows table structures across all databases]

User: "What tables are in the mcp_hub database?"
Response: [Lists all tables in the specified database]

User: "Describe the users table structure"
Response: [Shows column details for the users table]
```

### **Data Queries**
```
User: "How many users are in the database?"
Response: [Executes SELECT COUNT(*) and returns results]

User: "Show me the last 10 log entries"
Response: [Queries logs table and returns recent entries]

User: "Find all active servers"
Response: [Searches for active server records]
```

### **Cross-Database Queries**
```
User: "Search for 'admin' across all databases"
Response: [Searches all tables in all databases for 'admin']

User: "Show me user data from all databases"
Response: [Aggregates user data from multiple sources]
```

### **Health and Status**
```
User: "Check database health"
Response: [Tests connections to all databases]

User: "What databases are available?"
Response: [Lists all configured databases with status]

User: "Show database performance"
Response: [Displays connection times and status]
```

## 🛠️ **API Endpoints**

### **Database Management**
- `GET /api/databases/` - List all databases
- `POST /api/databases/` - Add new database
- `GET /api/databases/{name}/schema` - Get database schema
- `GET /api/databases/{name}/tables` - Get database tables
- `GET /api/databases/{name}/health` - Check database health
- `DELETE /api/databases/{name}` - Remove database

### **Query Execution**
- `POST /api/databases/query` - Execute query on specific database
- `POST /api/databases/query/all` - Execute query on all databases
- `POST /api/databases/search` - Search across all databases

## 🔍 **Advanced Features**

### **1. Natural Language to SQL**
The system automatically converts natural language queries to SQL:
```
User: "Show me all users created this month"
→ SQL: SELECT * FROM users WHERE created_at >= date_trunc('month', CURRENT_DATE)
```

### **2. Cross-Database Search**
Search for data across multiple databases simultaneously:
```
User: "Find all records containing 'error'"
→ Searches all tables in all databases for 'error'
```

### **3. Schema Introspection**
Automatically discover and document database structures:
```
User: "What's the structure of the mcp_hub database?"
→ Returns complete schema with tables, columns, and relationships
```

### **4. Query Optimization**
The system can suggest query optimizations and explain execution plans.

## 📈 **Performance Features**

### **Connection Pooling**
- Automatic connection pooling for PostgreSQL
- Configurable pool sizes per database
- Connection health monitoring

### **Async Operations**
- Non-blocking database operations
- Concurrent query execution
- Real-time result streaming

### **Caching**
- Query result caching
- Schema metadata caching
- Connection status caching

## 🔒 **Security Features**

### **Access Control**
- Database-level permissions
- Query execution limits
- Connection timeouts

### **Data Protection**
- Password encryption
- Connection string security
- Audit logging

### **Query Validation**
- SQL injection prevention
- Query complexity limits
- Dangerous operation blocking

## 🚨 **Troubleshooting**

### **Common Issues**

#### **1. Database Connection Failed**
```bash
# Check database status
curl http://localhost:8000/api/databases/mcp_hub/health

# Check container status
docker ps --filter "name=postgres-mcp-hub"
```

#### **2. Query Execution Error**
```bash
# Check database logs
docker logs postgres-mcp-hub

# Test connection manually
docker exec postgres-mcp-hub psql -U postgres -d mcp_hub -c "SELECT 1;"
```

#### **3. Schema Not Found**
```bash
# Refresh database schema
curl -X GET http://localhost:8000/api/databases/schemas
```

### **Debug Mode**
Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## 📚 **Examples**

### **Example 1: E-commerce Multi-Database Setup**
```json
{
  "databases": [
    {
      "name": "users_db",
      "type": "postgresql",
      "host": "users-server.com",
      "database": "users"
    },
    {
      "name": "products_db", 
      "type": "postgresql",
      "host": "products-server.com",
      "database": "products"
    },
    {
      "name": "orders_db",
      "type": "mysql",
      "host": "orders-server.com", 
      "database": "orders"
    },
    {
      "name": "analytics_db",
      "type": "sqlite",
      "database": "./analytics.db"
    }
  ]
}
```

### **Example 2: Chat Queries**
```
User: "How many orders were placed today?"
→ Queries orders_db for today's orders

User: "What are the top-selling products?"
→ Joins products_db and orders_db for analytics

User: "Show me user activity across all systems"
→ Aggregates data from users_db and analytics_db
```

## 🚀 **Production Deployment**

### **Environment Variables**
```bash
# Database connections
DATABASE_URL=postgresql://user:pass@host:port/db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mcp_hub
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secure_password

# Redis cache
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
```

### **Docker Compose**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mcp_hub
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: secure_password
    ports:
      - "5432:5432"
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  mcp-hub:
    build: ./mcp-hub-core
    environment:
      DATABASE_URL: postgresql://postgres:secure_password@postgres:5432/mcp_hub
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - postgres
      - redis
```

## 📖 **Best Practices**

1. **Database Naming**: Use descriptive names for databases
2. **Connection Limits**: Set appropriate connection pool sizes
3. **Security**: Use strong passwords and encrypted connections
4. **Monitoring**: Monitor database health and performance
5. **Backup**: Regular database backups
6. **Testing**: Test queries before production use

## 🆘 **Support**

For issues and questions:
1. Check the logs: `docker logs mcp-hub-backend`
2. Test database connections manually
3. Verify environment variables
4. Check API documentation at `/api/docs`

---

**Happy querying! 🎉**
