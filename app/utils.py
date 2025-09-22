"""
Utility functions for the scraper API
"""

import re
import hashlib
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse, urljoin
from datetime import datetime
import json


def extract_domain(url: str) -> str:
    """Extract clean domain from URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove www. prefix
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return domain
    except Exception:
        return ""


def generate_template_id(domain: str, selectors: Dict[str, str]) -> str:
    """Generate unique template ID"""
    # Create hash from domain + selectors
    content = f"{domain}_{json.dumps(selectors, sort_keys=True)}"
    return hashlib.md5(content.encode()).hexdigest()[:12]


def validate_url(url: str) -> bool:
    """Validate if URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def clean_text(text: str) -> str:
    """Clean extracted text content"""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def validate_css_selector(selector: str) -> bool:
    """Basic validation for CSS selectors"""
    if not selector or not isinstance(selector, str):
        return False
    
    # Basic patterns that indicate valid CSS selectors
    valid_patterns = [
        r'^[a-zA-Z][a-zA-Z0-9_-]*$',  # element
        r'^\.[a-zA-Z][a-zA-Z0-9_-]*$',  # class
        r'^#[a-zA-Z][a-zA-Z0-9_-]*$',  # id
        r'^[a-zA-Z][a-zA-Z0-9_-]*\.[a-zA-Z][a-zA-Z0-9_-]*$',  # element.class
    ]
    
    # Allow comma-separated selectors
    selectors = [s.strip() for s in selector.split(',')]
    
    for sel in selectors:
        if not sel:
            continue
            
        # Check for obviously invalid characters
        if any(char in sel for char in ['<', '>', '"', "'"]):
            return False
    
    return True


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove/replace invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    if len(filename) > 100:
        filename = filename[:100]
    
    return filename


def format_timestamp(dt: datetime) -> str:
    """Format datetime for API responses"""
    return dt.isoformat() + "Z"


def calculate_similarity(text1: str, text2: str) -> float:
    """Calculate basic text similarity"""
    if not text1 or not text2:
        return 0.0
    
    # Convert to lowercase and split into words
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    # Calculate Jaccard similarity
    intersection = len(words1.intersection(words2))
    union = len(words1.union(words2))
    
    return intersection / union if union > 0 else 0.0


def extract_main_content_heuristics(html: str) -> List[str]:
    """Extract potential content areas using heuristics"""
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
            element.decompose()
        
        # Find potential content containers
        content_selectors = [
            'article',
            '.article-content', 
            '.post-content',
            '.content',
            '.entry-content',
            '[role="main"]',
            'main',
            '.article-body',
            '.post-body'
        ]
        
        found_selectors = []
        
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                # Check if element has substantial text content
                for element in elements:
                    text = element.get_text(strip=True)
                    if len(text) > 100:  # Minimum content length
                        found_selectors.append(selector)
                        break
        
        return found_selectors
        
    except ImportError:
        return []
    except Exception:
        return []


def detect_language(text: str) -> str:
    """Basic language detection (placeholder implementation)"""
    if not text:
        return "unknown"
    
    # Very basic detection based on common words
    # In production, use a proper language detection library
    
    # Count characters
    char_counts = {}
    for char in text.lower():
        if char.isalpha():
            char_counts[char] = char_counts.get(char, 0) + 1
    
    # Simple heuristics
    if any(char in text.lower() for char in ['ñ', 'ü', 'á', 'é', 'í', 'ó']):
        return "es"  # Spanish
    elif any(char in text.lower() for char in ['ç', 'ã', 'õ']):
        return "pt"  # Portuguese
    elif 'the ' in text.lower() or 'and ' in text.lower():
        return "en"  # English
    else:
        return "id"  # Default to Indonesian for this project


def generate_request_id() -> str:
    """Generate unique request ID for tracking"""
    import uuid
    return str(uuid.uuid4())[:8]


def validate_schema(schema: Dict[str, str]) -> List[str]:
    """Validate expected schema structure"""
    errors = []
    
    if not schema:
        errors.append("Schema cannot be empty")
        return errors
    
    # Check for required field types
    valid_types = ["string", "text", "html", "markdown", "date", "datetime", "url"]
    
    for field, field_type in schema.items():
        if not field:
            errors.append("Field name cannot be empty")
        
        if not field_type or field_type not in valid_types:
            errors.append(f"Invalid type '{field_type}' for field '{field}'. Valid types: {valid_types}")
        
        # Check field name format
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', field):
            errors.append(f"Invalid field name '{field}'. Must start with letter and contain only letters, numbers, and underscores")
    
    return errors


def merge_selectors(selectors1: Dict[str, str], selectors2: Dict[str, str]) -> Dict[str, str]:
    """Merge two selector dictionaries intelligently"""
    merged = selectors1.copy()
    
    for field, selector in selectors2.items():
        if field in merged:
            # Combine selectors if both exist
            existing = merged[field]
            if existing and selector and existing != selector:
                merged[field] = f"{existing}, {selector}"
        else:
            merged[field] = selector
    
    return merged


def estimate_content_quality(content: str) -> float:
    """Estimate quality score for extracted content"""
    if not content:
        return 0.0
    
    score = 0.0
    
    # Length factor
    if len(content) > 50:
        score += 0.3
    if len(content) > 200:
        score += 0.2
    if len(content) > 500:
        score += 0.2
    
    # Sentence structure
    sentences = content.split('.')
    if len(sentences) > 2:
        score += 0.1
    
    # Word count
    words = content.split()
    if len(words) > 10:
        score += 0.1
    if len(words) > 50:
        score += 0.1
    
    return min(score, 1.0)


def convert_relative_urls(html: str, base_url: str) -> str:
    """Convert relative URLs to absolute URLs in HTML content"""
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Convert image sources
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and not src.startswith(('http://', 'https://', 'data:')):
                img['src'] = urljoin(base_url, src)
        
        # Convert link hrefs
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and not href.startswith(('http://', 'https://', 'mailto:', '#')):
                link['href'] = urljoin(base_url, href)
        
        return str(soup)
        
    except ImportError:
        return html
    except Exception:
        return html


def extract_meta_tags(html: str) -> Dict[str, str]:
    """Extract meta tags from HTML"""
    try:
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        meta_tags = {}
        
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            
            if name and content:
                meta_tags[name] = content
        
        return meta_tags
        
    except ImportError:
        return {}
    except Exception:
        return {}


# Configuration helpers
def get_env_bool(key: str, default: bool = False) -> bool:
    """Get boolean from environment variable"""
    import os
    value = os.getenv(key, str(default)).lower()
    return value in ('true', '1', 'yes', 'on')


def get_env_int(key: str, default: int = 0) -> int:
    """Get integer from environment variable"""
    import os
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def get_env_list(key: str, default: List[str] = None, separator: str = ',') -> List[str]:
    """Get list from environment variable"""
    import os
    if default is None:
        default = []
    
    value = os.getenv(key, '')
    if not value:
        return default
    
    return [item.strip() for item in value.split(separator) if item.strip()]