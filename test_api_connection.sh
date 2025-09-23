#!/bin/bash

# 🧪 Test API Connection Script
echo "🧪 Testing direct API connection to https://scraper-api.nusarithm.id/"

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

API_BASE_URL="https://scraper-api.nusarithm.id"

print_info "Testing API endpoints..."

# Test 1: Health check
print_info "Testing health endpoint..."
curl -s -f "$API_BASE_URL/health" > /dev/null 2>&1
print_status $? "Health endpoint: $API_BASE_URL/health"

# Test 2: API info
print_info "Testing info endpoint..."
curl -s -f "$API_BASE_URL/info" > /dev/null 2>&1
print_status $? "Info endpoint: $API_BASE_URL/info"

# Test 3: API docs
print_info "Testing API docs..."
curl -s -f "$API_BASE_URL/docs" > /dev/null 2>&1
print_status $? "API docs: $API_BASE_URL/docs"

# Test 4: HTTPS certificate
print_info "Checking HTTPS certificate..."
curl -s -I "$API_BASE_URL/health" | grep -q "200 OK"
print_status $? "HTTPS connection working"

# Test 5: CORS headers
print_info "Checking CORS headers..."
CORS_RESPONSE=$(curl -s -H "Origin: https://scraper.nusarithm.id" -I "$API_BASE_URL/health" | grep -i "access-control-allow-origin")
if [ ! -z "$CORS_RESPONSE" ]; then
    print_status 0 "CORS headers present"
else
    print_status 1 "CORS headers missing"
fi

echo ""
echo "📊 API Configuration Summary:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Backend API:     $API_BASE_URL"
echo "📋 API Docs:        $API_BASE_URL/docs"
echo "🔍 Health Check:    $API_BASE_URL/health"
echo "ℹ️  API Info:        $API_BASE_URL/info"
echo ""
echo "🔧 Frontend Configuration:"
echo "   All API calls use getApiUrl() helper"
echo "   No reverse proxy needed"
echo "   Direct HTTPS connection to backend"
echo ""

# Display actual health response
print_info "Health check response:"
curl -s "$API_BASE_URL/health" | python3 -m json.tool 2>/dev/null || echo "Failed to get health response"

echo ""
echo "🎯 Next Steps:"
echo "1. Verify all frontend components use getApiUrl() helper"
echo "2. Test authentication flow: login/register"
echo "3. Test template creation and scraping"
echo "4. Monitor frontend console for any API errors"