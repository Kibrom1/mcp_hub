#!/bin/bash

# MCP Hub Docker Setup Script
# This script sets up the complete MCP Hub environment with PostgreSQL

set -e

echo "🚀 Setting up MCP Hub with Docker..."

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

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Docker and Docker Compose are installed"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_info "Creating .env file from template..."
    cp env.example .env
    print_warning "Please edit .env file with your actual API keys and configuration"
    print_warning "Required: OPENAI_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY"
else
    print_status ".env file already exists"
fi

# Create logs directory
mkdir -p logs
print_status "Created logs directory"

# Stop any existing containers
print_info "Stopping any existing containers..."
docker-compose down 2>/dev/null || true

# Remove any existing containers
print_info "Removing any existing containers..."
docker-compose rm -f 2>/dev/null || true

# Build and start services
print_info "Building and starting services..."
docker-compose up --build -d

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 10

# Check if PostgreSQL is ready
print_info "Checking PostgreSQL connection..."
for i in {1..30}; do
    if docker-compose exec -T postgres pg_isready -U postgres -d mcp_hub >/dev/null 2>&1; then
        print_status "PostgreSQL is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "PostgreSQL failed to start"
        exit 1
    fi
    sleep 2
done

# Check if Redis is ready
print_info "Checking Redis connection..."
for i in {1..30}; do
    if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
        print_status "Redis is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Redis failed to start"
        exit 1
    fi
    sleep 2
done

# Check if backend is ready
print_info "Checking backend service..."
for i in {1..30}; do
    if curl -f http://localhost:8000/health >/dev/null 2>&1; then
        print_status "Backend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Backend failed to start"
        exit 1
    fi
    sleep 2
done

# Check if frontend is ready
print_info "Checking frontend service..."
for i in {1..30}; do
    if curl -f http://localhost:3000 >/dev/null 2>&1; then
        print_status "Frontend is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        print_error "Frontend failed to start"
        exit 1
    fi
    sleep 2
done

# Display connection information
echo ""
print_status "MCP Hub is now running!"
echo ""
echo "📊 Connection Details:"
echo "  • Frontend: http://localhost:3000"
echo "  • Backend API: http://localhost:8000"
echo "  • PostgreSQL: localhost:5432"
echo "  • Redis: localhost:6379"
echo ""
echo "🔑 Database Connection:"
echo "  • Host: localhost"
echo "  • Port: 5432"
echo "  • Database: mcp_hub"
echo "  • Username: postgres"
echo "  • Password: mcp_hub_password"
echo ""
echo "📝 Useful Commands:"
echo "  • View logs: docker-compose logs -f"
echo "  • Stop services: docker-compose down"
echo "  • Restart services: docker-compose restart"
echo "  • View status: docker-compose ps"
echo ""
print_warning "Don't forget to set your API keys in the .env file!"

# Show container status
echo "📋 Container Status:"
docker-compose ps
