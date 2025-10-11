#!/bin/bash

# Production Deployment Script for MCP Hub
set -e

echo "🚀 Starting MCP Hub Production Deployment..."

# Check if required environment variables are set
check_env_vars() {
    echo "🔍 Checking environment variables..."
    
    required_vars=(
        "OPENAI_API_KEY"
        "SECRET_KEY"
        "JWT_SECRET"
        "ADMIN_PASSWORD"
        "USER_PASSWORD"
    )
    
    missing_vars=()
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        echo "❌ Missing required environment variables:"
        printf '%s\n' "${missing_vars[@]}"
        echo ""
        echo "Please set these variables before deploying:"
        echo "export OPENAI_API_KEY='your-key'"
        echo "export SECRET_KEY='your-secret-key'"
        echo "export JWT_SECRET='your-jwt-secret'"
        echo "export ADMIN_PASSWORD='secure-admin-password'"
        echo "export USER_PASSWORD='secure-user-password'"
        exit 1
    fi
    
    echo "✅ All required environment variables are set"
}

# Generate secure secrets if not provided
generate_secrets() {
    echo "🔐 Generating secure secrets..."
    
    if [ -z "$SECRET_KEY" ]; then
        export SECRET_KEY=$(openssl rand -hex 32)
        echo "Generated SECRET_KEY"
    fi
    
    if [ -z "$JWT_SECRET" ]; then
        export JWT_SECRET=$(openssl rand -hex 32)
        echo "Generated JWT_SECRET"
    fi
}

# Create necessary directories
create_directories() {
    echo "📁 Creating necessary directories..."
    mkdir -p logs data ssl
    chmod 755 logs data ssl
}

# Generate SSL certificates (self-signed for development)
generate_ssl() {
    echo "🔒 Generating SSL certificates..."
    
    if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem \
            -days 365 -nodes -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        chmod 600 ssl/key.pem
        chmod 644 ssl/cert.pem
        echo "✅ SSL certificates generated"
    else
        echo "✅ SSL certificates already exist"
    fi
}

# Build and start services
deploy_services() {
    echo "🐳 Building and starting services..."
    
    # Stop existing services
    docker-compose down --remove-orphans
    
    # Build and start services
    docker-compose up -d --build
    
    echo "⏳ Waiting for services to be ready..."
    sleep 30
    
    # Check if services are running
    if docker-compose ps | grep -q "Up"; then
        echo "✅ Services are running"
    else
        echo "❌ Some services failed to start"
        docker-compose logs
        exit 1
    fi
}

# Run health checks
health_check() {
    echo "🏥 Running health checks..."
    
    # Wait for application to be ready
    max_attempts=30
    attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
            echo "✅ Application is healthy"
            return 0
        fi
        
        echo "Attempt $attempt/$max_attempts: Waiting for application..."
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo "❌ Health check failed"
    docker-compose logs mcp-hub
    exit 1
}

# Display deployment information
show_info() {
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📊 Service Information:"
    echo "  - Application: http://localhost:8501"
    echo "  - Database: PostgreSQL on port 5432"
    echo "  - Redis: Redis on port 6379"
    echo "  - Nginx: Reverse proxy on ports 80/443"
    echo ""
    echo "🔐 Security Information:"
    echo "  - HTTPS enabled with SSL certificates"
    echo "  - Rate limiting configured"
    echo "  - Security headers enabled"
    echo "  - Input sanitization active"
    echo ""
    echo "📝 Useful Commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Stop services: docker-compose down"
    echo "  - Restart services: docker-compose restart"
    echo "  - Update services: docker-compose up -d --build"
    echo ""
    echo "⚠️  Security Notes:"
    echo "  - Change default passwords immediately"
    echo "  - Use proper SSL certificates in production"
    echo "  - Configure firewall rules"
    echo "  - Monitor logs for suspicious activity"
}

# Main deployment process
main() {
    echo "🚀 MCP Hub Production Deployment"
    echo "================================="
    
    check_env_vars
    generate_secrets
    create_directories
    generate_ssl
    deploy_services
    health_check
    show_info
}

# Run main function
main "$@"
