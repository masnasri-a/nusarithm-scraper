"""
Pydantic schemas for AI-Assisted News Scraper API
"""

from pydantic import BaseModel, HttpUrl, Field
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum


class OutputFormat(str, Enum):
    """Supported output formats"""
    HTML = "html"
    MARKDOWN = "markdown"
    PLAINTEXT = "plaintext"


class TrainingRequest(BaseModel):
    """Request model for training a scraping template"""
    url: HttpUrl = Field(..., description="URL of the example article to analyze")
    expected_schema: Dict[str, str] = Field(
        ..., 
        description="Expected output schema with field names and types",
        example={
            "title": "string",
            "date": "string", 
            "author": "string",
            "content": "string"
        }
    )
    domain: Optional[str] = Field(None, description="Optional domain override")


class TemplateMapping(BaseModel):
    """Template mapping with CSS selectors for each field"""
    selectors: Dict[str, Optional[str]] = Field(
        ...,
        description="CSS selectors for each field",
        example={
            "title": "h1.article-title",
            "date": "span.pub-date", 
            "author": ".author-name",
            "content": "div.article-body p, div.article-body img"
        }
    )
    created_at: datetime = Field(default_factory=datetime.now)
    confidence_score: Optional[float] = Field(None, description="LLM confidence score")


class TrainingResponse(BaseModel):
    """Response model for training endpoint"""
    domain: str = Field(..., description="Domain for which template was created")
    template: TemplateMapping
    success: bool = Field(True, description="Whether training was successful")
    message: Optional[str] = Field(None, description="Additional information")


class ScrapeRequest(BaseModel):
    """Request model for scraping an article"""
    url: HttpUrl = Field(..., description="URL of the article to scrape")
    template_id: Optional[str] = Field(None, description="Specific template ID to use")
    output_format: OutputFormat = Field(
        OutputFormat.HTML, 
        description="Output format for content"
    )
    include_images: bool = Field(True, description="Whether to include inline images")


class ScrapeResponse(BaseModel):
    """Response model for scraping endpoint"""
    url: str = Field(..., description="Original URL that was scraped")
    domain: str = Field(..., description="Domain of the scraped article")
    template_used: str = Field(..., description="ID of template used for scraping")
    scraped_at: datetime = Field(default_factory=datetime.now)
    data: Dict[str, Any] = Field(
        ..., 
        description="Scraped data according to template",
        example={
            "title": "New Cultural Event in Jakarta...",
            "date": "2025-09-20T10:00:00Z",
            "author": "Reporter",
            "content": "<p>Jakarta held a cultural event...</p><p><img src='https://example.com/img1.jpg'></p>"
        }
    )
    success: bool = Field(True, description="Whether scraping was successful")
    message: Optional[str] = Field(None, description="Additional information or errors")


class TemplateInfo(BaseModel):
    """Information about a scraping template"""
    id: str = Field(..., description="Unique template identifier")
    domain: str = Field(..., description="Domain this template applies to")
    template: TemplateMapping
    usage_count: int = Field(0, description="Number of times this template has been used")
    success_rate: float = Field(1.0, description="Success rate of this template")
    last_used: Optional[datetime] = Field(None, description="Last time this template was used")


class TemplateListResponse(BaseModel):
    """Response model for listing templates"""
    templates: List[TemplateInfo]
    total: int = Field(..., description="Total number of templates")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field("healthy", description="API status")
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = Field(
        default_factory=lambda: {
            "database": "connected",
            "llm": "available",
            "scraper": "ready"
        }
    )


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = Field(None, description="Request ID for tracking")