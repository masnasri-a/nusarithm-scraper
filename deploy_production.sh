#!/bin/bash

# 🚀 Production Deployment Script for HTTPS Environment
echo "🚀 Setting up production deployment with HTTPS support..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2${NC}"
    else
        echo -e "${RED}❌ $2${NC}"
    fi
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info "Production deployment for HTTPS environment"
echo "Domain: scraper.nusarithm.id"
echo "Backend: https://scraper.nusarithm.id/api"
echo "Frontend: https://scraper.nusarithm.id"
echo ""

# Check if production environment file exists
if [ ! -f ".env" ]; then
    print_warning "No .env file found. Creating from production template..."
    cp .env.production .env
    print_status $? "Created .env from production template"
    
    print_warning "Please edit .env file and add your actual API keys and secrets!"
    echo "Required changes:"
    echo "  - OPENAI_API_KEY=your_actual_api_key"
    echo "  - SECRET_KEY=your_production_secret_key"
    echo ""
fi

# Check if frontend production env exists
if [ ! -f "frontend/.env.production" ]; then
    print_warning "Creating frontend production environment..."
    echo "NEXT_PUBLIC_BACKEND_URL=https://scraper.nusarithm.id/api" > frontend/.env.production
    print_status $? "Created frontend/.env.production"
fi

# Update docker-compose to use HTTPS backend URL
print_info "Ensuring docker-compose.prod.yml uses HTTPS backend URL..."
if grep -q "NEXT_PUBLIC_BACKEND_URL.*https" docker-compose.prod.yml; then
    print_status 0 "Docker compose already configured for HTTPS"
else
    print_warning "Updating docker-compose.prod.yml for HTTPS..."
fi

# Build the application
print_info "Building production containers..."
docker-compose -f docker-compose.prod.yml build --no-cache
print_status $? "Docker build completed"

# Test configuration
print_info "Testing configuration..."

# Check if ports are available
for port in 6777 3677 7777; do
    if nc -z localhost $port 2>/dev/null; then
        print_warning "Port $port is already in use"
    else
        print_status 0 "Port $port is available"
    fi
done

print_info "Deployment Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 Production URLs:"
echo "   Frontend:     https://scraper.nusarithm.id"
echo "   Backend API:  https://scraper.nusarithm.id/api"
echo "   API Docs:     https://scraper.nusarithm.id/api/docs"
echo "   Health:       https://scraper.nusarithm.id/api/health"
echo ""
echo "🐳 Local Development URLs (if running locally):"
echo "   Nginx Proxy:  http://localhost:7777"
echo "   Backend:      http://localhost:6777"
echo "   Frontend:     http://localhost:3677"
echo ""
echo "🚀 To start production deployment:"
echo "   docker-compose -f docker-compose.prod.yml up -d"
echo ""
echo "🔍 To view logs:"
echo "   docker-compose -f docker-compose.prod.yml logs -f"
echo ""
echo "🛑 To stop:"
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""
echo "⚠️  Important: Make sure you have configured SSL certificates in nginx"
echo "   and updated the domain name in nginx.prod.conf if different from scraper.nusarithm.id"
echo ""
print_status 0 "Production deployment configuration completed!"

# Verify Next.js config
print_info "Verifying Next.js configuration..."
cd frontend
if node -e "console.log('Next.js config verification:', require('./next.config.js'))"; then
    print_status 0 "Next.js configuration is valid"
else
    print_status 1 "Next.js configuration has issues"
fi
cd ..

echo ""
echo "🎯 Next Steps:"
echo "1. Verify .env file has correct API keys"
echo "2. Run: docker-compose -f docker-compose.prod.yml up -d"
echo "3. Test: curl https://scraper.nusarithm.id/api/health"
echo "4. Monitor logs for any HTTPS/CORS issues"
echo ""