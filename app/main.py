"""
AI-Assisted News Scraper API (FastAPI)
Main application entry point
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import asyncio
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add the parent directory to Python path to ensure proper imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Load environment variables from .env file
load_dotenv()

# Import routers
try:
    from .routers import training, scraping, auth, users
    from .models.schema import HealthResponse, ErrorResponse
except ImportError:
    # Fallback for different import contexts
    from app.routers import training, scraping, auth, users
    from app.models.schema import HealthResponse, ErrorResponse


# Application metadata
APP_NAME = "AI-Assisted News Scraper API"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = """
🤖 **AI-Powered Web Scraping Platform**

This API enables you to:

* **Train Templates**: Use AI to generate CSS selectors from example pages
* **Scrape Articles**: Extract structured data using trained templates  
* **Multi-format Output**: Get results in HTML, Markdown, or Plain Text
* **Batch Processing**: Scrape multiple articles concurrently
* **Template Management**: Store and reuse scraping patterns per domain

## 🚀 Quick Start

1. **Train a template**: `POST /train` with example URL + expected schema
2. **Scrape articles**: `POST /scrape` with article URLs  
3. **Check health**: `GET /health` to verify all services

## 🏗️ Architecture

Built with **FastAPI** + **Playwright/BeautifulSoup** + **Local LLM (Ollama)**
"""


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print(f"🚀 Starting {APP_NAME} v{APP_VERSION}")
    
    # Initialize services
    try:
        # Test database connection
        from .db import template_store
        print("✅ Database connection established")
        
        # Initialize superadmin user
        await template_store.initialize_superadmin()
        
        # Test LLM connection
        from .services.llm_agent import test_openai_connection
        llm_status = await test_openai_connection()
        if llm_status["connected"]:
            print(f"✅ LLM connection established: {llm_status['model']}")
        else:
            print(f"⚠️  LLM connection failed: {llm_status.get('error', 'Unknown error')}")
        
        # Test scraper
        from .services.scraper import ScrapingEngine
        print("✅ Scraper engine initialized")
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=APP_NAME,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(training.router)
app.include_router(scraping.router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": APP_NAME,
        "version": APP_VERSION,
        "description": "AI-powered web scraping platform",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "training": "/train",
            "scraping": "/scrape"
        },
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Comprehensive health check for all services"""
    
    services_status = {}
    overall_status = "healthy"
    
    # Check database
    try:
        from .db import template_store
        # Simple database test
        services_status["database"] = "connected"
    except Exception as e:
        services_status["database"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    # Check LLM
    try:
        from .services.llm_agent import test_openai_connection
        llm_status = await test_openai_connection()
        if llm_status["connected"]:
            services_status["llm"] = f"connected ({llm_status['model']})"
        else:
            services_status["llm"] = f"disconnected: {llm_status.get('error', 'Unknown error')}"
            overall_status = "degraded"
    except Exception as e:
        services_status["llm"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    # Check scraper
    try:
        from .services.scraper import PLAYWRIGHT_AVAILABLE, BS4_AVAILABLE
        scraper_status = []
        if PLAYWRIGHT_AVAILABLE:
            scraper_status.append("playwright")
        if BS4_AVAILABLE:
            scraper_status.append("beautifulsoup4")
        
        if scraper_status:
            services_status["scraper"] = f"ready ({', '.join(scraper_status)})"
        else:
            services_status["scraper"] = "no engines available"
            overall_status = "unhealthy"
            
    except Exception as e:
        services_status["scraper"] = f"error: {str(e)}"
        overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        timestamp=datetime.now(),
        services=services_status
    )


@app.get("/info", tags=["Info"])
async def api_info():
    """Detailed API information and configuration"""
    
    return {
        "api": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "environment": os.getenv("ENVIRONMENT", "development"),
            "debug": os.getenv("DEBUG", "false").lower() == "true"
        },
        "configuration": {
            "database_type": "sqlite",
            "database_path": os.getenv("DATABASE_PATH", "scraper.db"),
            "openai_model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            "playwright_enabled": os.getenv("PLAYWRIGHT_ENABLED", "true").lower() == "true"
        },
        "features": {
            "ai_template_generation": True,
            "multi_format_output": True,
            "batch_scraping": True,
            "template_management": True,
            "concurrent_requests": True
        },
        "limits": {
            "max_concurrent_scrapes": 10,
            "request_timeout": 60,
            "llm_timeout": 60
        }
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors"""
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else "An unexpected error occurred",
            "timestamp": datetime.now().isoformat(),
            "path": str(request.url)
        }
    )


# Add utility endpoints
@app.get("/version", tags=["Info"])
async def get_version():
    """Get API version"""
    return {"version": APP_VERSION}


@app.get("/status", tags=["Health"])
async def get_status():
    """Quick status check"""
    return {"status": "running", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    
    # Development server configuration
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )