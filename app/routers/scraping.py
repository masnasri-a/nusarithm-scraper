"""
Scraping endpoint router for article extraction
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import asyncio

from ..models.schema import (
    ScrapeRequest,
    ScrapeResponse, 
    OutputFormat,
    ErrorResponse
)
from ..services.template import TemplateManager
from ..db import extract_domain


router = APIRouter(prefix="/scrape", tags=["scraping"])


@router.post("/", response_model=ScrapeResponse)
async def scrape_article(request: ScrapeRequest) -> ScrapeResponse:
    """
    Scrape an article using existing template
    
    This endpoint extracts article data using a pre-trained template
    for the article's domain.
    """
    
    try:
        manager = TemplateManager()
        
        # Scrape using template
        result = await manager.scrape_with_template(
            url=str(request.url),
            template_id=request.template_id,
            output_format=request.output_format.value
        )
        
        if result["success"]:
            return ScrapeResponse(
                url=str(request.url),
                domain=result["domain"],
                template_used=result["template_used"],
                scraped_at=result["scraped_at"],
                data=result["data"],
                success=True,
                message="Article scraped successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to scrape article")
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/")
async def scrape_article_get(
    url: str = Query(..., description="URL of the article to scrape"),
    output_format: OutputFormat = Query(OutputFormat.HTML, description="Output format"),
    include_images: bool = Query(True, description="Include inline images")
) -> Dict[str, Any]:
    """
    Scrape an article using GET method (for easy testing)
    """
    
    try:
        # Create request object
        request = ScrapeRequest(
            url=url,
            output_format=output_format,
            include_images=include_images
        )
        
        # Use the POST endpoint logic
        result = await scrape_article(request)
        
        return {
            "url": result.url,
            "domain": result.domain,
            "template_used": result.template_used,
            "scraped_at": result.scraped_at.isoformat(),
            "data": result.data,
            "success": result.success,
            "message": result.message
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error scraping article: {str(e)}"
        )


@router.post("/batch")
async def scrape_batch(
    request: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Scrape multiple articles in batch
    
    Request body should contain:
    - urls: list of URLs to scrape
    - output_format: optional output format (default: html)
    - max_concurrent: optional max concurrent requests (default: 3)
    """
    
    try:
        urls = request.get("urls", [])
        output_format = request.get("output_format", "html")
        max_concurrent = min(request.get("max_concurrent", 3), 10)  # Limit to 10
        
        if not urls:
            raise HTTPException(
                status_code=400,
                detail="List of URLs is required"
            )
        
        manager = TemplateManager()
        
        # Process URLs concurrently with limit
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_single(url: str) -> Dict[str, Any]:
            async with semaphore:
                try:
                    result = await manager.scrape_with_template(
                        url=url,
                        output_format=output_format
                    )
                    return {
                        "url": url,
                        "success": result["success"],
                        "data": result.get("data"),
                        "error": result.get("error")
                    }
                except Exception as e:
                    return {
                        "url": url,
                        "success": False,
                        "error": str(e)
                    }
        
        # Execute batch scraping
        tasks = [scrape_single(url) for url in urls]
        results = await asyncio.gather(*tasks)
        
        # Calculate statistics
        successful = sum(1 for r in results if r["success"])
        failed = len(results) - successful
        
        return {
            "batch_id": f"batch_{len(urls)}_{successful}_{failed}",
            "total_urls": len(urls),
            "successful": successful,
            "failed": failed,
            "results": results
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error in batch scraping: {str(e)}"
        )


@router.get("/domain/{domain}")
async def get_domain_template(domain: str) -> Dict[str, Any]:
    """
    Get template information for a specific domain
    """
    
    try:
        manager = TemplateManager()
        template = await manager.get_template(domain)
        
        if template:
            return {
                "domain": domain,
                "template_exists": True,
                "template": {
                    "id": template.get("id"),
                    "selectors": template.get("selectors"),
                    "confidence_score": template.get("confidence_score"),
                    "usage_count": template.get("usage_count", 0),
                    "success_rate": template.get("success_rate", 1.0),
                    "created_at": template.get("created_at"),
                    "last_used": template.get("last_used")
                }
            }
        else:
            return {
                "domain": domain,
                "template_exists": False,
                "message": f"No template found for domain: {domain}. Train a template first using /train endpoint."
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving domain template: {str(e)}"
        )


@router.get("/preview")
async def preview_scrape(
    url: str = Query(..., description="URL to preview"),
    show_selectors: bool = Query(False, description="Show CSS selectors used")
) -> Dict[str, Any]:
    """
    Preview what would be scraped from a URL without actually processing
    """
    
    try:
        domain = extract_domain(url)
        manager = TemplateManager()
        template = await manager.get_template(domain)
        
        if not template:
            return {
                "url": url,
                "domain": domain,
                "can_scrape": False,
                "message": "No template available for this domain. Train a template first."
            }
        
        # Test the template
        test_result = await manager.test_template(url, template["selectors"])
        
        response_data = {
            "url": url,
            "domain": domain,
            "can_scrape": test_result["success"],
            "template_id": template["id"],
            "confidence_score": template.get("confidence_score"),
            "preview_data": test_result.get("extracted_data") if test_result["success"] else None
        }
        
        if show_selectors:
            response_data["selectors"] = template["selectors"]
            response_data["validation"] = test_result.get("validation_results")
        
        return response_data
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error previewing scrape: {str(e)}"
        )


@router.get("/health")
async def scraping_health() -> Dict[str, Any]:
    """
    Health check for scraping service
    """
    
    try:
        # Test scraper connectivity
        from ..services.scraper import ScrapingEngine
        
        # Simple connectivity test
        async with ScrapingEngine(use_playwright=False) as scraper:
            # Test with a simple URL
            test_result = await scraper.fetch_page_content("https://httpbin.org/html")
            scraper_status = "healthy" if test_result.get("status_code") == 200 else "degraded"
        
        return {
            "service": "scraping",
            "status": scraper_status,
            "scraper_engine": "available",
            "timestamp": "2025-09-22T00:00:00Z"
        }
    
    except Exception as e:
        return {
            "service": "scraping",
            "status": "unhealthy", 
            "error": str(e),
            "timestamp": "2025-09-22T00:00:00Z"
        }