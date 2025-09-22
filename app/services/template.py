"""
Template management service for scraping templates
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from urllib.parse import urlparse
import asyncio

try:
    from ..db import template_store, extract_domain
    from .scraper import ScrapingEngine, analyze_page_structure
    from .llm_agent import LLMAgent, generate_template_with_llm
except ImportError:
    from app.db import template_store, extract_domain
    from app.services.scraper import ScrapingEngine, analyze_page_structure
    from app.services.llm_agent import LLMAgent, generate_template_with_llm


class TemplateManager:
    """Manages scraping templates - creation, storage, and usage"""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "glm-4.5-flash"
    ):
        self.llm_agent = LLMAgent(api_key=api_key, model=model)
    
    async def create_template(
        self,
        url: str,
        expected_schema: Dict[str, str],
        force_retrain: bool = False
    ) -> Dict[str, Any]:
        """Create a new scraping template for a domain"""
        
        domain = extract_domain(url)
        
        # Check if template already exists
        if not force_retrain:
            existing_template = await template_store.get_template_by_domain(domain)
            if existing_template:
                return {
                    "success": True,
                    "template_id": existing_template["id"],
                    "domain": domain,
                    "template": existing_template,
                    "message": "Template already exists for this domain",
                    "created_new": False
                }
        
        try:
            # Scrape the training page
            async with ScrapingEngine() as scraper:
                page_data = await scraper.fetch_page_content(url)
                
                # Analyze page structure for potential selectors
                potential_selectors = await analyze_page_structure(url)
                
                # Generate template using LLM
                llm_result = await generate_template_with_llm(
                    page_data["html"],
                    url,
                    expected_schema,
                    api_key=self.llm_agent.api_key,
                    model=self.llm_agent.model
                )
                
                # Extract selectors and confidence
                template_data = llm_result["template"]
                selectors = template_data["selectors"]
                confidence = template_data.get("confidence_score", 0.0)
                
                # Test the generated template
                test_result = scraper.parse_content_with_selectors(
                    page_data["html"],
                    selectors,
                    url
                )
                
                # Calculate success score
                success_score = self._calculate_success_score(test_result, expected_schema)
                
                # Save template to database
                template_id = await template_store.save_template(
                    domain=domain,
                    template=selectors,
                    confidence_score=confidence
                )
                
                return {
                    "success": True,
                    "template_id": template_id,
                    "domain": domain,
                    "template": {
                        "id": template_id,
                        "domain": domain,
                        "selectors": selectors,
                        "confidence_score": confidence,
                        "success_score": success_score,
                        "created_at": datetime.now()
                    },
                    "test_result": test_result,
                    "validation": llm_result["validation"],
                    "message": "Template created successfully",
                    "created_new": True
                }
        
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "domain": domain,
                "error": str(e),
                "message": f"Failed to create template: {str(e)}"
            }
    
    async def get_template(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get template for a specific domain"""
        return await template_store.get_template_by_domain(domain)
    
    async def scrape_with_template(
        self,
        url: str,
        template_id: Optional[str] = None,
        output_format: str = "html"
    ) -> Dict[str, Any]:
        """Scrape a URL using existing template"""
        
        domain = extract_domain(url)
        
        try:
            # Get template
            if template_id:
                # TODO: Implement get_template_by_id
                template = await template_store.get_template_by_domain(domain)
            else:
                template = await template_store.get_template_by_domain(domain)
            
            if not template:
                return {
                    "success": False,
                    "error": f"No template found for domain: {domain}",
                    "message": "Template not found. Please train a template first."
                }
            
            # Scrape the page
            async with ScrapingEngine() as scraper:
                page_data = await scraper.fetch_page_content(url)
                
                # Extract data using template
                extracted_data = scraper.parse_content_with_selectors(
                    page_data["html"],
                    template["selectors"],
                    url
                )
                
                # Format output based on requested format
                formatted_data = self._format_output(extracted_data, output_format)
                
                # Update template usage statistics
                success = self._is_extraction_successful(extracted_data)
                await template_store.update_template_usage(template["id"], success)
                
                return {
                    "success": True,
                    "url": url,
                    "domain": domain,
                    "template_used": template["id"],
                    "scraped_at": datetime.now(),
                    "data": formatted_data,
                    "raw_data": extracted_data,
                    "template_info": {
                        "confidence_score": template.get("confidence_score"),
                        "usage_count": template.get("usage_count", 0) + 1
                    }
                }
        
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "domain": domain,
                "error": str(e),
                "message": f"Failed to scrape: {str(e)}"
            }
    
    async def test_template(
        self,
        url: str,
        selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """Test selectors against a URL"""
        
        try:
            async with ScrapingEngine() as scraper:
                page_data = await scraper.fetch_page_content(url)
                
                # Test selectors
                extracted_data = scraper.parse_content_with_selectors(
                    page_data["html"],
                    selectors,
                    url
                )
                
                # Validate selectors
                validation_results = await self.llm_agent.validate_selectors(
                    page_data["html"],
                    selectors
                )
                
                return {
                    "success": True,
                    "url": url,
                    "extracted_data": extracted_data,
                    "validation_results": validation_results,
                    "selector_performance": self._analyze_selector_performance(
                        extracted_data, 
                        validation_results
                    )
                }
        
        except Exception as e:
            return {
                "success": False,
                "url": url,
                "error": str(e)
            }
    
    async def improve_template(
        self,
        domain: str,
        test_urls: List[str]
    ) -> Dict[str, Any]:
        """Improve template by testing against multiple URLs"""
        
        template = await template_store.get_template_by_domain(domain)
        if not template:
            return {
                "success": False,
                "error": f"No template found for domain: {domain}"
            }
        
        improvement_results = []
        
        for url in test_urls:
            try:
                test_result = await self.test_template(url, template["selectors"])
                improvement_results.append({
                    "url": url,
                    "result": test_result
                })
            except Exception as e:
                improvement_results.append({
                    "url": url,
                    "error": str(e)
                })
        
        # Analyze results and suggest improvements
        improvement_suggestions = self._analyze_improvement_opportunities(improvement_results)
        
        return {
            "success": True,
            "domain": domain,
            "template_id": template["id"],
            "test_results": improvement_results,
            "improvement_suggestions": improvement_suggestions
        }
    
    def _calculate_success_score(
        self, 
        extracted_data: Dict[str, Any], 
        expected_schema: Dict[str, str]
    ) -> float:
        """Calculate success score for extracted data"""
        
        if not extracted_data:
            return 0.0
        
        successful_extractions = 0
        total_fields = len(expected_schema)
        
        for field in expected_schema.keys():
            if field in extracted_data and extracted_data[field]:
                value = extracted_data[field]
                if isinstance(value, str) and len(value.strip()) > 0:
                    successful_extractions += 1
        
        return successful_extractions / total_fields if total_fields > 0 else 0.0
    
    def _is_extraction_successful(self, extracted_data: Dict[str, Any]) -> bool:
        """Determine if extraction was successful"""
        if not extracted_data:
            return False
        
        # Consider successful if at least 50% of fields have data
        non_empty_fields = sum(
            1 for value in extracted_data.values() 
            if value and isinstance(value, str) and len(value.strip()) > 0
        )
        
        return (non_empty_fields / len(extracted_data)) >= 0.5 if extracted_data else False
    
    def _format_output(self, data: Dict[str, Any], output_format: str) -> Dict[str, Any]:
        """Format extracted data according to output format"""
        
        if output_format == "plaintext":
            return self._to_plaintext(data)
        elif output_format == "markdown":
            return self._to_markdown(data)
        else:  # default html
            return data
    
    def _to_plaintext(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert HTML content to plain text"""
        try:
            from bs4 import BeautifulSoup
            
            result = {}
            for key, value in data.items():
                if isinstance(value, str):
                    # Remove HTML tags
                    soup = BeautifulSoup(value, 'html.parser')
                    result[key] = soup.get_text()
                else:
                    result[key] = value
            return result
            
        except ImportError:
            return data
    
    def _to_markdown(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert HTML content to Markdown"""
        try:
            from bs4 import BeautifulSoup
            
            result = {}
            for key, value in data.items():
                if isinstance(value, str):
                    # Basic HTML to Markdown conversion
                    soup = BeautifulSoup(value, 'html.parser')
                    
                    # Convert images
                    for img in soup.find_all('img'):
                        src = img.get('src', '')
                        alt = img.get('alt', '')
                        img.replace_with(f'![{alt}]({src})')
                    
                    # Convert links
                    for link in soup.find_all('a'):
                        href = link.get('href', '')
                        text = link.get_text()
                        link.replace_with(f'[{text}]({href})')
                    
                    # Convert paragraphs
                    for p in soup.find_all('p'):
                        p.replace_with(p.get_text() + '\n\n')
                    
                    result[key] = soup.get_text()
                else:
                    result[key] = value
            return result
            
        except ImportError:
            return data
    
    def _analyze_selector_performance(
        self, 
        extracted_data: Dict[str, Any],
        validation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze performance of selectors"""
        
        performance = {}
        
        for field, data in extracted_data.items():
            validation = validation_results.get(field, {})
            
            performance[field] = {
                "has_data": bool(data and str(data).strip()),
                "found_elements": validation.get("found_elements", 0),
                "is_valid": validation.get("valid", False),
                "data_length": len(str(data)) if data else 0,
                "quality_score": self._calculate_field_quality(data, validation)
            }
        
        return performance
    
    def _calculate_field_quality(self, data: Any, validation: Dict[str, Any]) -> float:
        """Calculate quality score for a field"""
        score = 0.0
        
        # Has data
        if data and str(data).strip():
            score += 0.4
        
        # Found elements
        if validation.get("found_elements", 0) > 0:
            score += 0.3
        
        # Valid selector
        if validation.get("valid", False):
            score += 0.2
        
        # Data quality
        if data:
            data_str = str(data)
            if len(data_str) > 10:  # Reasonable length
                score += 0.1
        
        return score
    
    def _analyze_improvement_opportunities(
        self, 
        test_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze test results for improvement opportunities"""
        
        field_performance = {}
        overall_issues = []
        
        # Aggregate performance across all tests
        for result in test_results:
            if result.get("result", {}).get("success"):
                performance = result["result"].get("selector_performance", {})
                
                for field, metrics in performance.items():
                    if field not in field_performance:
                        field_performance[field] = []
                    field_performance[field].append(metrics)
        
        # Identify problematic fields
        suggestions = {}
        for field, performances in field_performance.items():
            avg_quality = sum(p.get("quality_score", 0) for p in performances) / len(performances)
            success_rate = sum(1 for p in performances if p.get("has_data", False)) / len(performances)
            
            if avg_quality < 0.5 or success_rate < 0.7:
                suggestions[field] = {
                    "issue": "Low quality or success rate",
                    "avg_quality": avg_quality,
                    "success_rate": success_rate,
                    "recommendation": "Consider updating CSS selector for better reliability"
                }
        
        return {
            "field_suggestions": suggestions,
            "overall_performance": {
                "total_tests": len(test_results),
                "successful_tests": sum(1 for r in test_results if r.get("result", {}).get("success")),
                "avg_field_quality": sum(
                    sum(p.get("quality_score", 0) for p in performances) / len(performances)
                    for performances in field_performance.values()
                ) / len(field_performance) if field_performance else 0
            }
        }


# Convenience functions
async def train_template(
    url: str,
    expected_schema: Dict[str, str],
    force_retrain: bool = False
) -> Dict[str, Any]:
    """Train a new template for a URL"""
    manager = TemplateManager()
    return await manager.create_template(url, expected_schema, force_retrain)


async def scrape_url_with_template(
    url: str,
    output_format: str = "html"
) -> Dict[str, Any]:
    """Scrape URL using existing template"""
    manager = TemplateManager()
    return await manager.scrape_with_template(url, output_format=output_format)