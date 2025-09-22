"""
Training endpoint router for template generation
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Dict, Any
import asyncio, traceback

try:
    from ..models.schema import (
        TrainingRequest, 
        TrainingResponse, 
        TemplateMapping,
        TemplateInfo,
        TemplateListResponse,
        ErrorResponse
    )
    from ..services.template import TemplateManager
    from ..db import extract_domain, template_store
except ImportError:
    from app.models.schema import (
        TrainingRequest, 
        TrainingResponse, 
        TemplateMapping,
        TemplateInfo,
        TemplateListResponse,
        ErrorResponse
    )
    from app.services.template import TemplateManager
    from app.db import extract_domain, template_store


router = APIRouter(prefix="/train", tags=["training"])


@router.post("/", response_model=TrainingResponse)
async def train_template(
    request: TrainingRequest,
    background_tasks: BackgroundTasks
) -> TrainingResponse:
    """
    Train a new scraping template for a domain
    
    This endpoint analyzes a sample article URL and generates CSS selectors
    for extracting the specified fields using AI.
    """
    
    try:
        # Initialize template manager
        manager = TemplateManager()
        
        # Extract domain
        domain = request.domain or extract_domain(str(request.url))
        
        # Create template
        result = await manager.create_template(
            url=str(request.url),
            expected_schema=request.expected_schema,
            force_retrain=False
        )
        
        if result["success"]:
            # Prepare response
            template_data = result["template"]
            
            template_mapping = TemplateMapping(
                selectors=template_data["selectors"],
                confidence_score=template_data.get("confidence_score")
            )
            
            return TrainingResponse(
                domain=domain,
                template=template_mapping,
                success=True,
                message=result.get("message", "Template created successfully")
            )
        else:
            import traceback
            traceback.print_exc()
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to create template")
            )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.post("/retrain", response_model=TrainingResponse)
async def retrain_template(
    request: TrainingRequest
) -> TrainingResponse:
    """
    Force retrain an existing template
    
    This endpoint will retrain a template even if one already exists for the domain.
    """
    
    try:
        manager = TemplateManager()
        domain = request.domain or extract_domain(str(request.url))
        
        # Force retrain
        result = await manager.create_template(
            url=str(request.url),
            expected_schema=request.expected_schema,
            force_retrain=True
        )
        
        if result["success"]:
            template_data = result["template"]
            
            template_mapping = TemplateMapping(
                selectors=template_data["selectors"],
                confidence_score=template_data.get("confidence_score")
            )
            
            return TrainingResponse(
                domain=domain,
                template=template_mapping,
                success=True,
                message="Template retrained successfully"
            )
        else:
            raise HTTPException(
                status_code=400,
                detail=result.get("error", "Failed to retrain template")
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/templates", response_model=TemplateListResponse)
async def list_templates() -> TemplateListResponse:
    """
    List all stored scraping templates
    
    Returns a list of all templates with their metadata including:
    - Template ID and domain
    - CSS selectors
    - Usage statistics (usage count, success rate)
    - Timestamps (created_at, last_used)
    - Confidence scores
    """
    
    try:
        # Get all templates from database
        templates_data = await template_store.get_all_templates()
        
        # Convert to TemplateInfo objects
        template_infos = []
        for template_data in templates_data:
            # Create TemplateMapping object
            template_mapping = TemplateMapping(
                selectors=template_data["selectors"],
                confidence_score=template_data.get("confidence_score")
            )
            
            # Handle datetime parsing
            created_at = template_data["created_at"]
            if isinstance(created_at, str):
                from datetime import datetime
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            
            last_used = template_data.get("last_used")
            if last_used and isinstance(last_used, str):
                from datetime import datetime
                last_used = datetime.fromisoformat(last_used.replace("Z", "+00:00"))
            
            template_info = TemplateInfo(
                id=template_data["id"],
                domain=template_data["domain"],
                template=template_mapping,
                usage_count=template_data.get("usage_count", 0),
                success_rate=template_data.get("success_rate", 1.0),
                last_used=last_used
            )
            
            template_infos.append(template_info)
        
        return TemplateListResponse(
            templates=template_infos,
            total=len(template_infos)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving templates: {str(e)}"
        )


@router.get("/template/{domain}")
async def get_template(domain: str) -> Dict[str, Any]:
    """
    Get existing template for a domain
    """
    
    try:
        manager = TemplateManager()
        template = await manager.get_template(domain)
        
        if template:
            return {
                "domain": domain,
                "template": template,
                "exists": True
            }
        else:
            return {
                "domain": domain,
                "template": None,
                "exists": False,
                "message": "No template found for this domain"
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving template: {str(e)}"
        )


@router.delete("/template/{template_id}")
async def delete_template(template_id: str) -> Dict[str, Any]:
    """
    Delete a specific template by ID
    
    This permanently removes the template from the database.
    """
    
    try:
        success = await template_store.delete_template(template_id)
        
        if success:
            return {
                "success": True,
                "message": f"Template {template_id} deleted successfully",
                "template_id": template_id
            }
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Template {template_id} not found"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting template: {str(e)}"
        )


@router.post("/test")
async def test_template(
    data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Test CSS selectors against a URL
    
    Request body should contain:
    - url: string
    - selectors: dict of field->selector mappings
    """
    
    try:
        url = data.get("url")
        selectors = data.get("selectors")
        
        if not url or not selectors:
            raise HTTPException(
                status_code=400,
                detail="Both 'url' and 'selectors' are required"
            )
        
        manager = TemplateManager()
        result = await manager.test_template(url, selectors)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error testing template: {str(e)}"
        )


@router.post("/improve/{domain}")
async def improve_template(
    domain: str,
    test_urls: Dict[str, list]
) -> Dict[str, Any]:
    """
    Improve template by testing against multiple URLs
    
    Request body should contain:
    - urls: list of URLs to test against
    """
    
    try:
        urls = test_urls.get("urls", [])
        
        if not urls:
            raise HTTPException(
                status_code=400,
                detail="List of test URLs is required"
            )
        
        manager = TemplateManager()
        result = await manager.improve_template(domain, urls)
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error improving template: {str(e)}"
        )


@router.get("/health")
async def training_health() -> Dict[str, Any]:
    """
    Health check for training service
    """
    
    try:
        from ..services.llm_agent import test_openai_connection
        
        # Test LLM connection
        llm_status = await test_openai_connection()
        
        return {
            "service": "training",
            "status": "healthy" if llm_status["connected"] else "degraded",
            "llm_connection": llm_status,
            "timestamp": "2025-09-22T00:00:00Z"  # Will be dynamic in real implementation
        }
    
    except Exception as e:
        return {
            "service": "training", 
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2025-09-22T00:00:00Z"
        }