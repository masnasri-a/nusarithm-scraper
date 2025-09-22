"""
Web scraping service using Playwright and BeautifulSoup
"""

import asyncio
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime

try:
    from playwright.async_api import async_playwright, Browser, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not installed. Install with: pip install playwright")

try:
    from bs4 import BeautifulSoup, Tag
    import requests
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    print("Warning: BeautifulSoup4 not installed. Install with: pip install beautifulsoup4 requests")


class ScrapingEngine:
    """Main scraping engine with Playwright and BeautifulSoup support"""
    
    def __init__(self, use_playwright: bool = True, prefer_playwright_for_gov: bool = True):
        self.use_playwright = use_playwright and PLAYWRIGHT_AVAILABLE
        self.prefer_playwright_for_gov = prefer_playwright_for_gov
        self.browser: Optional[Browser] = None
        
        # Government domains that often need Playwright
        self.gov_domains = [
            'go.id', 'gov.id', 'kemenkeu.go.id', 'ekon.go.id', 
            'kemenperin.go.id', 'kemendag.go.id', 'bps.go.id'
        ]
        
    async def __aenter__(self):
        """Async context manager entry"""
        if self.use_playwright:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def fetch_page_content(self, url: str) -> Dict[str, Any]:
        """Fetch page content and return HTML + metadata"""
        
        if BS4_AVAILABLE:
            print("Falling back to requests...")
            return await self._fetch_with_requests(url)
        else:
            raise
       
    
    async def _fetch_with_playwright(self, url: str) -> Dict[str, Any]:
        """Fetch page using Playwright (handles JavaScript)"""
        if not self.browser:
            raise RuntimeError("Browser not initialized. Use async context manager.")
        
        page = await self.browser.new_page()
        try:
            # Set a longer timeout and better user agent
            await page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            # Navigate to page with longer timeout
            response = await page.goto(
                url, 
                wait_until='networkidle',
                timeout=60000  # 60 seconds timeout
            )
            
            # Wait for content to load
            await page.wait_for_timeout(3000)
            
            # Get page content and metadata
            html_content = await page.content()
            title = await page.title()
            
            # Get meta tags
            meta_tags = await page.evaluate("""
                () => {
                    const metas = {};
                    document.querySelectorAll('meta').forEach(meta => {
                        if (meta.name) metas[meta.name] = meta.content;
                        if (meta.property) metas[meta.property] = meta.content;
                    });
                    return metas;
                }
            """)
            
            return {
                "html": html_content,
                "title": title,
                "url": url,
                "status_code": response.status if response else 200,
                "meta_tags": meta_tags,
                "timestamp": datetime.now()
            }
            
        finally:
            await page.close()
    
    async def _fetch_with_playwright_fallback(self, url: str) -> Dict[str, Any]:
        """Fetch using Playwright when requests fails"""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available for fallback")
        
        # Initialize Playwright if not already done
        if not self.browser:
            playwright = await async_playwright().start()
            browser = await playwright.chromium.launch(headless=True)
            
            try:
                page = await browser.new_page()
                
                # Set headers
                await page.set_extra_http_headers({
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                })
                
                # Navigate with long timeout
                response = await page.goto(
                    url, 
                    wait_until='networkidle',
                    timeout=60000
                )
                
                await page.wait_for_timeout(3000)
                
                html_content = await page.content()
                title = await page.title()
                
                meta_tags = await page.evaluate("""
                    () => {
                        const metas = {};
                        document.querySelectorAll('meta').forEach(meta => {
                            if (meta.name) metas[meta.name] = meta.content;
                            if (meta.property) metas[meta.property] = meta.content;
                        });
                        return metas;
                    }
                """)
                
                return {
                    "html": html_content,
                    "title": title,
                    "url": url,
                    "status_code": response.status if response else 200,
                    "meta_tags": meta_tags,
                    "timestamp": datetime.now()
                }
                
            finally:
                await page.close()
                await browser.close()
                await playwright.stop()
        else:
            # Use existing browser
            return await self._fetch_with_playwright(url)
    
    async def _fetch_with_requests(self, url: str) -> Dict[str, Any]:
        """Fetch page using requests (fallback for static content)"""
        if not BS4_AVAILABLE:
            raise RuntimeError("BeautifulSoup4 not available for requests fallback")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        session = requests.Session()
        session.headers.update(headers)
        
        try:
            # Try with longer timeout and retries
            response = session.get(
                url, 
                timeout=30,  # Increased timeout
                verify=False,
                allow_redirects=True
            )
            response.raise_for_status()
            
        except requests.exceptions.ConnectTimeout:
            print(f"Connection timeout for {url}, trying with Playwright...")
            # Fall back to Playwright if available
            if PLAYWRIGHT_AVAILABLE:
                return await self._fetch_with_playwright_fallback(url)
            else:
                raise Exception(f"Connection timeout to {url} and Playwright not available")
                
        except requests.exceptions.SSLError:
            print(f"SSL error for {url}, retrying with different settings...")
            # Retry with SSL verification disabled if SSL error occurs
            response = session.get(
                url, 
                timeout=30, 
                verify=False,
                allow_redirects=True
            )
            response.raise_for_status()
            
        except requests.exceptions.RequestException as e:
            print(f"Request error for {url}: {e}")
            # Try Playwright as fallback
            if PLAYWRIGHT_AVAILABLE:
                return await self._fetch_with_playwright_fallback(url)
            else:
                raise
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract meta tags
        meta_tags = {}
        for meta in soup.find_all('meta'):
            if meta.get('name'):
                meta_tags[meta.get('name')] = meta.get('content', '')
            if meta.get('property'):
                meta_tags[meta.get('property')] = meta.get('content', '')
        
        return {
            "html": response.text,
            "title": soup.title.string if soup.title else "",
            "url": url,
            "status_code": response.status_code,
            "meta_tags": meta_tags,
            "timestamp": datetime.now()
        }
    
    def parse_content_with_selectors(
        self, 
        html: str, 
        selectors: Dict[str, str],
        base_url: str = ""
    ) -> Dict[str, Any]:
        """Parse HTML content using CSS selectors"""
        soup = BeautifulSoup(html, 'html.parser')
        result = {}
        
        for field, selector in selectors.items():
            try:
                result[field] = self._extract_field(soup, selector, base_url)
            except Exception as e:
                print(f"Error extracting field '{field}' with selector '{selector}': {e}")
                result[field] = None
        
        return result
    
    def _extract_field(self, soup: BeautifulSoup, selector: str, base_url: str) -> Optional[str]:
        """Extract a single field using CSS selector"""
        elements = soup.select(selector)
        
        if not elements:
            return None
        
        # Handle different extraction strategies
        if len(elements) == 1:
            return self._extract_element_content(elements[0], base_url)
        else:
            # Multiple elements - combine them
            contents = []
            for element in elements:
                content = self._extract_element_content(element, base_url)
                if content:
                    contents.append(content)
            return "\n".join(contents) if contents else None
    
    def _extract_element_content(self, element: Tag, base_url: str) -> str:
        """Extract content from a single element"""
        # Handle images
        if element.name == 'img':
            src = element.get('src', '')
            if src:
                # Convert relative URLs to absolute
                if base_url and not src.startswith('http'):
                    src = urljoin(base_url, src)
                alt = element.get('alt', '')
                return f'<img src="{src}" alt="{alt}">'
            return ""
        
        # Handle links
        elif element.name == 'a':
            href = element.get('href', '')
            if href and base_url and not href.startswith('http'):
                href = urljoin(base_url, href)
                element['href'] = href
            return str(element)
        
        # Handle text content with inline elements
        else:
            # Preserve some HTML structure for rich content
            if element.find(['p', 'br', 'img', 'a']):
                # Convert relative image URLs
                for img in element.find_all('img'):
                    src = img.get('src', '')
                    if src and base_url and not src.startswith('http'):
                        img['src'] = urljoin(base_url, src)
                
                # Convert relative link URLs
                for link in element.find_all('a'):
                    href = link.get('href', '')
                    if href and base_url and not href.startswith('http'):
                        link['href'] = urljoin(base_url, href)
                
                return str(element)
            else:
                return element.get_text(strip=True)
    
    def extract_structured_content(self, html: str, base_url: str = "") -> Dict[str, Any]:
        """Extract structured content using heuristics"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Common patterns for news articles
        result = {
            "title": self._extract_title(soup),
            "author": self._extract_author(soup),
            "date": self._extract_date(soup),
            "content": self._extract_main_content(soup, base_url)
        }
        
        return result
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title using common patterns"""
        selectors = [
            'h1[class*="title"]',
            'h1[class*="headline"]', 
            '.article-title',
            '.post-title',
            'h1',
            '[property="og:title"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.get('content'):  # meta tag
                    return element.get('content')
                return element.get_text(strip=True)
        
        return None
    
    def _extract_author(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article author using common patterns"""
        selectors = [
            '.author',
            '.byline',
            '[class*="author"]',
            '[rel="author"]',
            '[property="article:author"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                if element.get('content'):  # meta tag
                    return element.get('content')
                return element.get_text(strip=True)
        
        return None
    
    def _extract_date(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article date using common patterns"""
        selectors = [
            'time',
            '.date',
            '.publish-date',
            '[class*="date"]',
            '[property="article:published_time"]',
            '[name="date"]'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Try datetime attribute first
                if element.get('datetime'):
                    return element.get('datetime')
                if element.get('content'):  # meta tag
                    return element.get('content')
                text = element.get_text(strip=True)
                if text and len(text) > 4:  # Basic validation
                    return text
        
        return None
    
    def _extract_main_content(self, soup: BeautifulSoup, base_url: str) -> Optional[str]:
        """Extract main content using common patterns"""
        # Remove unwanted elements
        for element in soup(['script', 'style', 'nav', 'footer', 'aside', 'header']):
            element.decompose()
        
        selectors = [
            '.article-content',
            '.post-content', 
            '.content',
            'article',
            '[class*="content"]',
            '.entry-content'
        ]
        
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                # Process images and links
                for img in element.find_all('img'):
                    src = img.get('src', '')
                    if src and base_url and not src.startswith('http'):
                        img['src'] = urljoin(base_url, src)
                
                for link in element.find_all('a'):
                    href = link.get('href', '')
                    if href and base_url and not href.startswith('http'):
                        link['href'] = urljoin(base_url, href)
                
                return str(element)
        
        return None


# Convenience functions
async def scrape_url(url: str, selectors: Optional[Dict[str, str]] = None, force_playwright: bool = False) -> Dict[str, Any]:
    """Scrape a URL with optional selectors"""
    
    # Force Playwright for government sites or when requested
    domain = urlparse(url).netloc.lower()
    use_playwright = force_playwright or any(gov in domain for gov in [
        'go.id', 'gov.id', 'ekon.go.id', 'kemenperin.go.id'
    ])
    
    async with ScrapingEngine(use_playwright=use_playwright) as scraper:
        try:
            page_data = await scraper.fetch_page_content(url)
            
            if selectors:
                # Use provided selectors
                extracted_data = scraper.parse_content_with_selectors(
                    page_data["html"], 
                    selectors,
                    page_data["url"]
                )
            else:
                # Use heuristic extraction
                extracted_data = scraper.extract_structured_content(
                    page_data["html"],
                    page_data["url"] 
                )
            
            return {
                "url": url,
                "page_data": page_data,
                "extracted_data": extracted_data,
                "scraping_method": "playwright" if use_playwright else "requests"
            }
            
        except Exception as e:
            print(f"Scraping failed for {url}: {e}")
            # Try alternative method
            if use_playwright:
                print("Retrying with requests...")
                async with ScrapingEngine(use_playwright=False) as fallback_scraper:
                    page_data = await fallback_scraper.fetch_page_content(url)
                    extracted_data = fallback_scraper.extract_structured_content(
                        page_data["html"],
                        page_data["url"] 
                    )
                    return {
                        "url": url,
                        "page_data": page_data,
                        "extracted_data": extracted_data,
                        "scraping_method": "requests_fallback"
                    }
            else:
                raise


async def analyze_page_structure(url: str) -> Dict[str, Any]:
    """Analyze page structure for template generation"""
    async with ScrapingEngine() as scraper:
        page_data = await scraper.fetch_page_content(url)
        soup = BeautifulSoup(page_data["html"], 'html.parser')
        
        # Find potential selectors for common fields
        potential_selectors = {
            "title": _find_title_selectors(soup),
            "author": _find_author_selectors(soup), 
            "date": _find_date_selectors(soup),
            "content": _find_content_selectors(soup)
        }
        
        return {
            "url": url,
            "page_data": page_data,
            "potential_selectors": potential_selectors
        }


def _find_title_selectors(soup: BeautifulSoup) -> List[str]:
    """Find potential title selectors"""
    selectors = []
    
    # Find h1 tags with meaningful classes
    for h1 in soup.find_all('h1'):
        if h1.get('class'):
            classes = ' '.join(h1.get('class'))
            if any(keyword in classes.lower() for keyword in ['title', 'headline', 'head']):
                selectors.append(f"h1.{classes.replace(' ', '.')}")
    
    # Add generic selectors
    selectors.extend(['h1', '.title', '.headline'])
    
    return selectors


def _find_author_selectors(soup: BeautifulSoup) -> List[str]:
    """Find potential author selectors"""
    selectors = []
    
    # Find elements with author-related classes
    for element in soup.find_all(attrs={"class": True}):
        classes = ' '.join(element.get('class', []))
        if any(keyword in classes.lower() for keyword in ['author', 'byline', 'writer']):
            tag_classes = classes.replace(' ', '.')
            selectors.append(f"{element.name}.{tag_classes}")
    
    return selectors


def _find_date_selectors(soup: BeautifulSoup) -> List[str]:
    """Find potential date selectors"""
    selectors = []
    
    # Find time elements
    for time_elem in soup.find_all('time'):
        if time_elem.get('class'):
            classes = '.'.join(time_elem.get('class'))
            selectors.append(f"time.{classes}")
        else:
            selectors.append('time')
    
    # Find elements with date-related classes
    for element in soup.find_all(attrs={"class": True}):
        classes = ' '.join(element.get('class', []))
        if any(keyword in classes.lower() for keyword in ['date', 'time', 'publish']):
            tag_classes = classes.replace(' ', '.')
            selectors.append(f"{element.name}.{tag_classes}")
    
    return selectors


def _find_content_selectors(soup: BeautifulSoup) -> List[str]:
    """Find potential content selectors"""
    selectors = []
    
    # Find content containers
    for element in soup.find_all(['article', 'div', 'section']):
        if element.get('class'):
            classes = ' '.join(element.get('class', []))
            if any(keyword in classes.lower() for keyword in ['content', 'article', 'post', 'body']):
                tag_classes = classes.replace(' ', '.')
                selectors.append(f"{element.name}.{tag_classes}")
    
    # Add generic selectors
    selectors.extend(['article', '.content', '.article-body'])
    
    return selectors