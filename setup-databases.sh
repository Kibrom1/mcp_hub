#!/bin/bash

# Multi-Database Setup Script for MCP Hub
# This script sets up multiple database connections

set -e

echo "🗄️ Setting up Multi-Database Support for MCP Hub..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi

print_status "Docker is running"

# Start PostgreSQL container if not running
if ! docker ps --filter "name=postgres-mcp-hub" --format "{{.Names}}" | grep -q "postgres-mcp-hub"; then
    print_info "Starting PostgreSQL container..."
    docker run -d --name postgres-mcp-hub \
        -e POSTGRES_DB=mcp_hub \
        -e POSTGRES_USER=postgres \
        -e POSTGRES_PASSWORD=mcp_hub_password \
        -p 5432:5432 \
        postgres:15
    print_status "PostgreSQL container started"
else
    print_status "PostgreSQL container already running"
fi

# Start Redis container if not running
if ! docker ps --filter "name=redis-mcp-hub" --format "{{.Names}}" | grep -q "redis-mcp-hub"; then
    print_info "Starting Redis container..."
    docker run -d --name redis-mcp-hub \
        -p 6379:6379 \
        redis:7-alpine
    print_status "Redis container started"
else
    print_status "Redis container already running"
fi

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 5

# Test PostgreSQL connection
print_info "Testing PostgreSQL connection..."
if docker exec postgres-mcp-hub pg_isready -U postgres >/dev/null 2>&1; then
    print_status "PostgreSQL is ready"
else
    print_error "PostgreSQL is not ready"
    exit 1
fi

# Test Redis connection
print_info "Testing Redis connection..."
if docker exec redis-mcp-hub redis-cli ping >/dev/null 2>&1; then
    print_status "Redis is ready"
else
    print_error "Redis is not ready"
    exit 1
fi

# Create additional databases
print_info "Creating additional databases..."

# Create a test database
docker exec postgres-mcp-hub psql -U postgres -c "CREATE DATABASE test_db;" 2>/dev/null || true
print_status "Test database created"

# Create a user database
docker exec postgres-mcp-hub psql -U postgres -c "CREATE DATABASE user_data;" 2>/dev/null || true
print_status "User data database created"

# Create a logs database
docker exec postgres-mcp-hub psql -U postgres -c "CREATE DATABASE logs_db;" 2>/dev/null || true
print_status "Logs database created"

# Display connection information
echo ""
print_status "Multi-Database Setup Complete!"
echo ""
echo "📊 Database Connection Details:"
echo ""
echo "🔹 PostgreSQL Main Database:"
echo "  • Host: localhost"
echo "  • Port: 5432"
echo "  • Database: mcp_hub"
echo "  • Username: postgres"
echo "  • Password: mcp_hub_password"
echo ""
echo "🔹 PostgreSQL Test Database:"
echo "  • Host: localhost"
echo "  • Port: 5432"
echo "  • Database: test_db"
echo "  • Username: postgres"
echo "  • Password: mcp_hub_password"
echo ""
echo "🔹 PostgreSQL User Data Database:"
echo "  • Host: localhost"
echo "  • Port: 5432"
echo "  • Database: user_data"
echo "  • Username: postgres"
echo "  • Password: mcp_hub_password"
echo ""
echo "🔹 PostgreSQL Logs Database:"
echo "  • Host: localhost"
echo "  • Port: 5432"
echo "  • Database: logs_db"
echo "  • Username: postgres"
echo "  • Password: mcp_hub_password"
echo ""
echo "🔹 Redis Cache:"
echo "  • Host: localhost"
echo "  • Port: 6379"
echo "  • Database: 0"
echo ""
echo "🔹 SQLite Database:"
echo "  • File: mcp.db"
echo "  • Path: ./mcp.db"
echo ""
echo "📝 Next Steps:"
echo "  1. Start your MCP Hub backend"
echo "  2. Use the chat interface to interact with databases"
echo "  3. Try queries like:"
echo "     - 'Show me the schema of all databases'"
echo "     - 'What tables are in the mcp_hub database?'"
echo "     - 'Search for user data across all databases'"
echo "     - 'Check the health of all databases'"
echo ""
print_warning "Make sure to set your API keys in the .env file!"

# Show container status
echo "📋 Container Status:"
docker ps --filter "name=postgres-mcp-hub" --filter "name=redis-mcp-hub"
