#!/bin/bash

# 🧪 Test Docker Setup Script
echo "🧪 Testing Docker Setup..."

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
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
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_info "Building Docker images..."

# Test 1: Build Docker image
docker build -t scraper-api . > /dev/null 2>&1
print_status $? "Docker image build"

# Test 2: Test import script
print_info "Testing Python imports..."
python test_imports.py > /dev/null 2>&1
print_status $? "Python imports"

# Test 3: Test development docker-compose
print_info "Testing development docker-compose..."
docker-compose config > /dev/null 2>&1
print_status $? "Development docker-compose config"

# Test 4: Test production docker-compose
print_info "Testing production docker-compose..."
docker-compose -f docker-compose.prod.yml config > /dev/null 2>&1
print_status $? "Production docker-compose config"

# Test 5: Check if ports are available
print_info "Checking port availability..."

# Check backend port 6777
nc -z localhost 6777 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Port 6777 is already in use${NC}"
else
    echo -e "${GREEN}✅ Port 6777 is available${NC}"
fi

# Check frontend port 3677
nc -z localhost 3677 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Port 3677 is already in use${NC}"
else
    echo -e "${GREEN}✅ Port 3677 is available${NC}"
fi

# Check nginx port 7777
nc -z localhost 7777 2>/dev/null
if [ $? -eq 0 ]; then
    echo -e "${YELLOW}⚠️  Port 7777 is already in use${NC}"
else
    echo -e "${GREEN}✅ Port 7777 is available${NC}"
fi

print_info "Quick setup commands:"
echo "Development: docker-compose up -d"
echo "Production:  docker-compose -f docker-compose.prod.yml up -d"
echo "Direct run:  ./run_dev.sh"
echo "Test setup:  python test_imports.py"

print_info "Service URLs:"
echo "Backend API:  http://localhost:6777/docs"
echo "Frontend:     http://localhost:3677"
echo "Nginx Proxy:  http://localhost:7777"

echo ""
echo "🎉 Docker setup test completed!"