#!/bin/bash

# Installation script for AI-Assisted News Scraper API
# This script handles common installation issues on macOS

echo "🚀 Installing AI-Assisted News Scraper API dependencies..."

# Check if we're on macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📱 Detected macOS system"
    
    # Check if Xcode command line tools are installed
    if ! xcode-select -p &> /dev/null; then
        echo "⚙️  Installing Xcode command line tools..."
        xcode-select --install
        echo "Please install Xcode command line tools and re-run this script"
        exit 1
    fi
    
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "🍺 Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    fi
fi

# Upgrade pip and install build tools
echo "📦 Upgrading pip and installing build tools..."
python3 -m pip install --upgrade pip setuptools wheel

# For Apple Silicon Macs, set some environment variables
if [[ "$(uname -m)" == "arm64" ]]; then
    echo "🔧 Configuring for Apple Silicon..."
    export ARCHFLAGS="-arch arm64"
    export _PYTHON_HOST_PLATFORM="macosx-11.0-arm64"
fi

# Install dependencies with no binary packages first (to avoid pre-compiled issues)
echo "🔨 Installing core dependencies..."
python3 -m pip install --no-binary=:all: pydantic-core greenlet || {
    echo "⚠️  Failed to compile from source, trying with pre-compiled wheels..."
    python3 -m pip install pydantic-core greenlet
}

# Install the rest of the requirements
echo "📚 Installing remaining dependencies..."
python3 -m pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python3 -m playwright install chromium

echo "✅ Installation completed!"
echo ""
echo "🚀 You can now run the API with:"
echo "   uvicorn app.main:app --reload"
echo ""
echo "📖 Or check the documentation at:"
echo "   http://localhost:8000/docs"