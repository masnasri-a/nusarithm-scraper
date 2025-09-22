#!/bin/bash

echo "🔍 Checking frontend health..."

# Check if port 3000 is available
if lsof -i :3000 > /dev/null 2>&1; then
    echo "✅ Frontend server is running on port 3000"
else
    echo "❌ Frontend server is not running on port 3000"
fi

# Check if port 8000 is available (backend)
if lsof -i :8000 > /dev/null 2>&1; then
    echo "✅ Backend server is running on port 8000"
else
    echo "❌ Backend server is not running on port 8000"
fi

# Test frontend connection
echo "🌐 Testing frontend connection..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not accessible"
fi

# Test backend connection  
echo "🔌 Testing backend connection..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend API is accessible"
else
    echo "❌ Backend API is not accessible"
fi

echo "🎯 Test complete!"