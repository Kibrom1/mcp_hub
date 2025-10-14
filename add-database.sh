#!/bin/bash

# Add Database Script for MCP Hub
# This script helps you add new databases to your MCP Hub

set -e

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

# Check if MCP Hub is running
if ! curl -s http://localhost:8000/ >/dev/null 2>&1; then
    print_error "MCP Hub is not running. Please start it first with: uvicorn main:app --host 0.0.0.0 --port 8000 --reload"
    exit 1
fi

print_status "MCP Hub is running"

# Function to add PostgreSQL database
add_postgresql() {
    local name=$1
    local host=${2:-localhost}
    local port=${3:-5432}
    local database=$4
    local username=${5:-postgres}
    local password=${6:-mcp_hub_password}
    
    print_info "Adding PostgreSQL database: $name"
    
    curl -X POST "http://localhost:8000/api/databases/" \
      -H "Content-Type: application/json" \
      -d "{
        \"name\": \"$name\",
        \"type\": \"postgresql\",
        \"host\": \"$host\",
        \"port\": $port,
        \"database\": \"$database\",
        \"username\": \"$username\",
        \"password\": \"$password\",
        \"is_active\": true,
        \"max_connections\": 10,
        \"timeout\": 30
      }"
    
    echo ""
}

# Function to add SQLite database
add_sqlite() {
    local name=$1
    local database_path=$2
    
    print_info "Adding SQLite database: $name"
    
    curl -X POST "http://localhost:8000/api/databases/" \
      -H "Content-Type: application/json" \
      -d "{
        \"name\": \"$name\",
        \"type\": \"sqlite\",
        \"host\": \"localhost\",
        \"port\": 0,
        \"database\": \"$database_path\",
        \"username\": \"\",
        \"password\": \"\",
        \"is_active\": true
      }"
    
    echo ""
}

# Function to add MySQL database
add_mysql() {
    local name=$1
    local host=${2:-localhost}
    local port=${3:-3306}
    local database=$4
    local username=${5:-root}
    local password=${6:-password}
    
    print_info "Adding MySQL database: $name"
    
    curl -X POST "http://localhost:8000/api/databases/" \
      -H "Content-Type: application/json" \
      -d "{
        \"name\": \"$name\",
        \"type\": \"mysql\",
        \"host\": \"$host\",
        \"port\": $port,
        \"database\": \"$database\",
        \"username\": \"$username\",
        \"password\": \"$password\",
        \"is_active\": true,
        \"max_connections\": 10,
        \"timeout\": 30
      }"
    
    echo ""
}

# Interactive menu
echo "🗄️  MCP Hub Database Addition Tool"
echo "=================================="
echo ""
echo "Choose database type to add:"
echo "1) PostgreSQL"
echo "2) SQLite"
echo "3) MySQL"
echo "4) Add sample databases"
echo "5) List existing databases"
echo "6) Exit"
echo ""

read -p "Enter your choice (1-6): " choice

case $choice in
    1)
        echo ""
        print_info "Adding PostgreSQL Database"
        echo "=============================="
        read -p "Database name: " db_name
        read -p "Host (default: localhost): " db_host
        read -p "Port (default: 5432): " db_port
        read -p "Database name: " db_database
        read -p "Username (default: postgres): " db_username
        read -p "Password (default: mcp_hub_password): " db_password
        
        add_postgresql "${db_name}" "${db_host:-localhost}" "${db_port:-5432}" "${db_database}" "${db_username:-postgres}" "${db_password:-mcp_hub_password}"
        ;;
    2)
        echo ""
        print_info "Adding SQLite Database"
        echo "========================"
        read -p "Database name: " db_name
        read -p "Database file path (e.g., ./analytics.db): " db_path
        
        add_sqlite "${db_name}" "${db_path}"
        ;;
    3)
        echo ""
        print_info "Adding MySQL Database"
        echo "======================="
        read -p "Database name: " db_name
        read -p "Host (default: localhost): " db_host
        read -p "Port (default: 3306): " db_port
        read -p "Database name: " db_database
        read -p "Username (default: root): " db_username
        read -p "Password (default: password): " db_password
        
        add_mysql "${db_name}" "${db_host:-localhost}" "${db_port:-3306}" "${db_database}" "${db_username:-root}" "${db_password:-password}"
        ;;
    4)
        echo ""
        print_info "Adding Sample Databases"
        echo "========================="
        
        # Add sample PostgreSQL databases
        add_postgresql "test_db" "localhost" "5432" "test_db" "postgres" "mcp_hub_password"
        add_postgresql "analytics_db" "localhost" "5432" "analytics" "postgres" "mcp_hub_password"
        add_postgresql "logs_db" "localhost" "5432" "logs" "postgres" "mcp_hub_password"
        
        # Add sample SQLite databases
        add_sqlite "cache_db" "./cache.db"
        add_sqlite "temp_db" "./temp.db"
        
        print_status "Sample databases added successfully!"
        ;;
    5)
        echo ""
        print_info "Listing Existing Databases"
        echo "============================"
        curl -s "http://localhost:8000/api/databases/" | python -m json.tool
        ;;
    6)
        print_info "Goodbye!"
        exit 0
        ;;
    *)
        print_error "Invalid choice. Please run the script again."
        exit 1
        ;;
esac

echo ""
print_status "Database addition completed!"
echo ""
print_info "You can now use the chat interface to interact with your databases:"
echo "  - 'Show me all databases'"
echo "  - 'What tables are in the [database_name] database?'"
echo "  - 'Search for data across all databases'"
echo "  - 'Check database health'"
