"""
Z.AI integration service for template generation using HTTP API
"""

import json
import asyncio
import ssl
from typing import Dict, List, Optional, Any
import os
import re
from urllib.parse import urlparse
import aiohttp
import certifi


class LLMAgent:
    """Z.AI agent for CSS selector generation using HTTP API"""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        model: str = "glm-4.5-flash",
        timeout: int = 60
    ):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")  # Z.AI uses same env var name
        self.model = model or os.getenv("OPENAI_MODEL", "glm-4.5-flash")
        self.timeout = timeout
        self.base_url = "https://api.z.ai/api/paas/v4"
        
        if not self.api_key:
            raise ValueError("Z.AI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # Setup headers for HTTP requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")  # Z.AI uses same env var name
        self.model = model or os.getenv("OPENAI_MODEL", "glm-4.5-flash")
        self.timeout = timeout
        self.base_url = "https://api.z.ai/api/paas/v4"
        
        if not self.api_key:
            raise ValueError("Z.AI API key is required. Set OPENAI_API_KEY environment variable.")
        
        # Setup headers for HTTP requests
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def generate_template(
        self, 
        html_content: str, 
        url: str,
        expected_schema: Dict[str, str],
        existing_selectors: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """Generate CSS selectors template using LLM"""
        
        # Prepare context for LLM
        context = self._prepare_context(html_content, url, expected_schema, existing_selectors)
        
        # Generate template using LLM
        llm_response = await self._call_llm(context)
        
        # Parse and validate response
        template = self._parse_llm_response(llm_response, expected_schema)
        
        return template
    
    def _prepare_context(
        self, 
        html_content: str, 
        url: str,
        expected_schema: Dict[str, str],
        existing_selectors: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Prepare context for LLM with HTML and requirements"""
        
        # Clean and truncate HTML for LLM
        cleaned_html = self._clean_html_for_llm(html_content)
        
        # Extract domain for context
        domain = urlparse(url).netloc
        
        # Build prompt
        prompt = f"""
You are an expert web scraper that generates CSS selectors for extracting specific data from web pages.

TASK: Analyze the following HTML content and generate CSS selectors to extract the required fields.

URL: {url}
DOMAIN: {domain}

REQUIRED FIELDS:
{json.dumps(expected_schema, indent=2)}

HTML CONTENT (truncated):
```html
{cleaned_html}
```

INSTRUCTIONS:
1. Analyze the HTML structure carefully
2. Generate specific CSS selectors for each required field
3. Prefer class-based selectors over tag-only selectors
4. For content fields, include both text and images using comma-separated selectors
5. Return ONLY a valid JSON object with field names as keys and CSS selectors as values
6. If a field cannot be found, use "NOT_FOUND" as the selector

EXAMPLE OUTPUT:
{{
    "title": "h1.article-title",
    "author": ".author-name, .byline",
    "date": "time.publish-date, .date-published", 
    "content": ".article-body p, .article-body img"
}}

PREVIOUS ATTEMPTS (if any):
{json.dumps(existing_selectors, indent=2) if existing_selectors else "None"}

JSON OUTPUT:"""
        print(prompt)

        return prompt
    
    def _clean_html_for_llm(self, html_content: str, max_length: int = 10000) -> str:
        """Clean and truncate HTML content for LLM processing"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Remove comments
            for comment in soup.find_all(string=lambda text: isinstance(text, str) and text.strip().startswith('<!--')):
                comment.extract()
            
            # Get clean HTML
            clean_html = str(soup)
            
            # Truncate if too long
            # if len(clean_html) > max_length:
            #     clean_html = clean_html[:max_length] + "\n... [TRUNCATED]"
            
            return clean_html
            
        except Exception as e:
            print(f"Error cleaning HTML: {e}")
            # Fallback: simple truncation
            if len(html_content) > max_length:
                return html_content[:max_length] + "\n... [TRUNCATED]"
            return html_content
    
    async def _call_llm(self, prompt: str) -> str:
        """Call Z.AI API using HTTP request"""
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system", 
                    "content": "You are an expert web scraper that generates precise CSS selectors for extracting data from web pages. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 10000
        }
        
        try:
            # For development: disable SSL verification due to certificate issues
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            print("Using disabled SSL verification for Z.AI API")
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout),
                connector=connector
            ) as session:
                print("Sending request to Z.AI API...")
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result["choices"][0]["message"]["content"]
                    else:
                        error_text = await response.text()
                        raise Exception(f"Z.AI API error {response.status}: {error_text}")
                        
        except asyncio.TimeoutError:
            raise Exception(f"Z.AI API timeout after {self.timeout} seconds")
        except aiohttp.ClientError as e:
            raise Exception(f"Z.AI API connection error: {str(e)}")
        except Exception as e:
            raise Exception(f"Error calling Z.AI API: {str(e)}")
    
    def _parse_llm_response(self, response: str, expected_schema: Dict[str, str]) -> Dict[str, Any]:
        """Parse LLM response and extract CSS selectors"""
        try:
            # Clean the response
            response = response.strip()
            
            # Handle Z.AI response format with markdown code blocks
            json_str = None
            
            # First, try to extract JSON from markdown code block
            markdown_match = re.search(r'```json\s*\n(.*?)\n```', response, re.DOTALL)
            if markdown_match:
                json_str = markdown_match.group(1).strip()
            else:
                # Fallback: try to find JSON without markdown
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
            
            if json_str:
                selectors = json.loads(json_str)
                
                # Validate selectors
                validated_selectors = {}
                confidence_scores = {}
                
                for field in expected_schema.keys():
                    if field in selectors and selectors[field] != "NOT_FOUND":
                        validated_selectors[field] = selectors[field]
                        confidence_scores[field] = self._calculate_confidence(selectors[field])
                    else:
                        # Provide fallback selectors instead of None
                        fallback_selectors = {
                            "title": "h1, .title, .headline, article h1, .post-title",
                            "content": ".content, .article-content, .post-content, article p, .entry-content",
                            "author": ".author, .byline, .writer, .post-author, [rel='author']",
                            "date": ".date, .published, .timestamp, time, .post-date"
                        }
                        validated_selectors[field] = fallback_selectors.get(field, "body")
                        confidence_scores[field] = 0.1  # Low confidence for fallback
                
                # Calculate overall confidence
                overall_confidence = sum(confidence_scores.values()) / len(confidence_scores) if confidence_scores else 0.0
                
                return {
                    "selectors": validated_selectors,
                    "confidence_score": overall_confidence,
                    "field_confidence": confidence_scores,
                    "raw_response": response
                }
            
            else:
                raise ValueError("No valid JSON found in response")
                
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            # Provide fallback selectors for all fields
            fallback_selectors = {
                "title": "h1, .title, .headline, article h1, .post-title",
                "content": ".content, .article-content, .post-content, article p, .entry-content",
                "author": ".author, .byline, .writer, .post-author, [rel='author']",
                "date": ".date, .published, .timestamp, time, .post-date"
            }
            return {
                "selectors": {field: fallback_selectors.get(field, "body") for field in expected_schema.keys()},
                "confidence_score": 0.0,
                "field_confidence": {field: 0.0 for field in expected_schema.keys()},
                "raw_response": response,
                "error": str(e)
            }
    
    def _calculate_confidence(self, selector: str) -> float:
        """Calculate confidence score for a CSS selector"""
        if not selector or selector == "NOT_FOUND":
            return 0.0
        
        score = 0.5  # Base score
        
        # Class-based selectors are more reliable
        if '.' in selector:
            score += 0.2
        
        # ID-based selectors are highly reliable
        if '#' in selector:
            score += 0.3
        
        # Semantic class names are better
        semantic_keywords = ['title', 'author', 'date', 'content', 'article', 'post', 'byline']
        for keyword in semantic_keywords:
            if keyword in selector.lower():
                score += 0.1
                break
        
        # Multiple selectors (comma-separated) show thoroughness
        if ',' in selector:
            score += 0.1
        
        return min(score, 1.0)
    
    async def validate_selectors(
        self, 
        html_content: str, 
        selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """Validate CSS selectors against HTML content"""
        try:
            from bs4 import BeautifulSoup
            
            soup = BeautifulSoup(html_content, 'html.parser')
            validation_results = {}
            
            for field, selector in selectors.items():
                if not selector:
                    validation_results[field] = {
                        "valid": False,
                        "found_elements": 0,
                        "sample_content": None
                    }
                    continue
                
                try:
                    elements = soup.select(selector)
                    sample_content = None
                    
                    if elements:
                        # Get sample content from first element
                        first_element = elements[0]
                        if first_element.name == 'img':
                            sample_content = f"<img src='{first_element.get('src', '')}' alt='{first_element.get('alt', '')}'>"
                        else:
                            sample_content = first_element.get_text(strip=True)[:100] + "..." if len(first_element.get_text(strip=True)) > 100 else first_element.get_text(strip=True)
                    
                    validation_results[field] = {
                        "valid": len(elements) > 0,
                        "found_elements": len(elements),
                        "sample_content": sample_content
                    }
                    
                except Exception as e:
                    validation_results[field] = {
                        "valid": False,
                        "found_elements": 0,
                        "sample_content": None,
                        "error": str(e)
                    }
            
            return validation_results
            
        except ImportError:
            return {"error": "BeautifulSoup4 not available for validation"}
        except Exception as e:
            return {"error": f"Validation error: {str(e)}"}
    
    async def improve_selectors(
        self,
        html_content: str,
        current_selectors: Dict[str, str],
        validation_results: Dict[str, Any],
        expected_schema: Dict[str, str]
    ) -> Dict[str, Any]:
        """Improve selectors based on validation results"""
        
        # Find fields that need improvement
        fields_to_improve = []
        for field, result in validation_results.items():
            if not result.get("valid", False) or result.get("found_elements", 0) == 0:
                fields_to_improve.append(field)
        
        if not fields_to_improve:
            return {
                "selectors": current_selectors,
                "confidence_score": 0.9,
                "improved": False
            }
        
        # Generate improved selectors for problematic fields
        improvement_prompt = f"""
The following CSS selectors failed to extract data from the HTML. Please provide improved selectors.

FAILED FIELDS: {', '.join(fields_to_improve)}

CURRENT SELECTORS:
{json.dumps(current_selectors, indent=2)}

VALIDATION RESULTS:
{json.dumps(validation_results, indent=2)}

HTML CONTENT (truncated):
```html
{self._clean_html_for_llm(html_content)}
```

Please provide ONLY a JSON object with improved selectors for the failed fields:
"""
        
        try:
            improved_response = await self._call_llm(improvement_prompt)
            improved_template = self._parse_llm_response(improved_response, expected_schema)
            
            # Merge improved selectors with current ones
            final_selectors = current_selectors.copy()
            for field in fields_to_improve:
                if field in improved_template["selectors"] and improved_template["selectors"][field]:
                    final_selectors[field] = improved_template["selectors"][field]
            
            return {
                "selectors": final_selectors,
                "confidence_score": improved_template["confidence_score"],
                "improved": True,
                "improved_fields": fields_to_improve
            }
            
        except Exception as e:
            print(f"Error improving selectors: {e}")
            return {
                "selectors": current_selectors,
                "confidence_score": 0.3,
                "improved": False,
                "error": str(e)
            }


# Convenience functions
async def generate_template_with_llm(
    html_content: str,
    url: str, 
    expected_schema: Dict[str, str],
    api_key: Optional[str] = None,
    model: str = "glm-4.5-flash"
) -> Dict[str, Any]:
    """Generate template using Z.AI with validation and improvement"""
    
    agent = LLMAgent(api_key=api_key, model=model)
    
    # Generate initial template
    template = await agent.generate_template(html_content, url, expected_schema)
    
    # Validate selectors
    validation_results = await agent.validate_selectors(html_content, template["selectors"])
    
    # Improve selectors if needed
    improved_template = await agent.improve_selectors(
        html_content, 
        template["selectors"],
        validation_results,
        expected_schema
    )
    
    return {
        "template": improved_template,
        "validation": validation_results,
        "original_response": template
    }


async def test_openai_connection(
    api_key: Optional[str] = None,
    model: str = "glm-4.5-flash"
) -> Dict[str, Any]:
    """Test connection to Z.AI service using HTTP API"""
    try:
        agent = LLMAgent(api_key=api_key, model=model)
        
        response = await agent._call_llm("Hello, please respond with 'OK' if you can read this.")
        return {
            "connected": True,
            "model": model,
            "service": "Z.AI",
            "method": "HTTP API",
            "response": response[:100] + "..." if len(response) > 100 else response
        }
    except Exception as e:
        return {
            "connected": False,
            "model": model,
            "service": "Z.AI", 
            "method": "HTTP API",
            "error": str(e)
        }


# Configuration
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "glm-4.5-flash")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))


async def test_openai_connection(
    api_key: Optional[str] = None,
    model: str = "glm-4.5-flash"
) -> Dict[str, Any]:
    """Test connection to Z.AI service using HTTP API"""
    try:
        agent = LLMAgent(api_key=api_key, model=model)
        
        response = await agent._call_llm("Hello, please respond with 'OK' if you can read this.")
        return {
            "connected": True,
            "model": model,
            "service": "Z.AI",
            "method": "HTTP API",
            "response": response[:100] + "..." if len(response) > 100 else response
        }
    except Exception as e:
        return {
            "connected": False,
            "model": model,
            "service": "Z.AI", 
            "method": "HTTP API",
            "error": str(e)
        }


# Configuration
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "glm-4.5-flash")
LLM_TIMEOUT = int(os.getenv("LLM_TIMEOUT", "60"))