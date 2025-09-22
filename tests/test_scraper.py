"""
Unit tests for scraper service
"""

import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock

from app.services.scraper import ScrapingEngine, scrape_url, analyze_page_structure


@pytest.fixture
def sample_html():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Article</title>
        <meta name="author" content="John Doe">
        <meta property="article:published_time" content="2025-09-22T10:00:00Z">
    </head>
    <body>
        <header>
            <nav>Navigation</nav>
        </header>
        <main>
            <article>
                <h1 class="article-title">Sample News Article</h1>
                <div class="article-meta">
                    <span class="author">John Doe</span>
                    <time class="publish-date" datetime="2025-09-22T10:00:00Z">September 22, 2025</time>
                </div>
                <div class="article-content">
                    <p>This is the first paragraph of the article.</p>
                    <p>This is the second paragraph with an <img src="/image.jpg" alt="Test image"> inline image.</p>
                    <p>This is the third paragraph.</p>
                </div>
            </article>
        </main>
        <footer>Footer content</footer>
    </body>
    </html>
    """


@pytest.fixture
def sample_selectors():
    return {
        "title": "h1.article-title",
        "author": ".author",
        "date": "time.publish-date",
        "content": ".article-content p, .article-content img"
    }


class TestScrapingEngine:
    
    @pytest.mark.asyncio
    async def test_fetch_with_requests(self, sample_html):
        """Test fetching page content with requests fallback"""
        
        with patch('requests.get') as mock_get:
            # Mock response
            mock_response = MagicMock()
            mock_response.text = sample_html
            mock_response.content = sample_html.encode()
            mock_response.status_code = 200
            mock_response.raise_for_status.return_value = None
            mock_get.return_value = mock_response
            
            # Test with requests fallback
            async with ScrapingEngine(use_playwright=False) as scraper:
                result = await scraper.fetch_page_content("https://example.com/article")
                
                assert result["status_code"] == 200
                assert "Sample News Article" in result["html"]
                assert result["title"] == "Test Article"
                assert "author" in result["meta_tags"]
    
    def test_parse_content_with_selectors(self, sample_html, sample_selectors):
        """Test parsing HTML with CSS selectors"""
        
        scraper = ScrapingEngine(use_playwright=False)
        result = scraper.parse_content_with_selectors(
            sample_html, 
            sample_selectors,
            "https://example.com"
        )
        
        assert result["title"] == "Sample News Article"
        assert result["author"] == "John Doe"
        assert result["date"] == "September 22, 2025"
        assert "first paragraph" in result["content"]
        assert "image.jpg" in result["content"]
    
    def test_extract_structured_content(self, sample_html):
        """Test heuristic content extraction"""
        
        scraper = ScrapingEngine(use_playwright=False)
        result = scraper.extract_structured_content(sample_html, "https://example.com")
        
        assert result["title"] == "Sample News Article"
        assert result["author"] == "John Doe"
        assert "This is the first paragraph" in result["content"]
    
    def test_extract_element_content(self):
        """Test individual element content extraction"""
        
        from bs4 import BeautifulSoup
        
        scraper = ScrapingEngine(use_playwright=False)
        
        # Test image extraction
        html = '<img src="/test.jpg" alt="Test image">'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('img')
        
        result = scraper._extract_element_content(element, "https://example.com")
        assert 'src="https://example.com/test.jpg"' in result
        
        # Test text extraction
        html = '<p>Some text content</p>'
        soup = BeautifulSoup(html, 'html.parser')
        element = soup.find('p')
        
        result = scraper._extract_element_content(element, "https://example.com")
        assert result == "Some text content"


@pytest.mark.asyncio
async def test_scrape_url():
    """Test the convenience function for scraping URLs"""
    
    with patch('app.services.scraper.ScrapingEngine') as mock_engine:
        # Mock the scraper engine
        mock_scraper = AsyncMock()
        mock_scraper.fetch_page_content.return_value = {
            "html": "<html><body><h1>Test</h1></body></html>",
            "url": "https://example.com",
            "status_code": 200
        }
        mock_scraper.parse_content_with_selectors.return_value = {
            "title": "Test Article"
        }
        
        mock_engine.return_value.__aenter__.return_value = mock_scraper
        
        result = await scrape_url("https://example.com", {"title": "h1"})
        
        assert result["url"] == "https://example.com"
        assert result["extracted_data"]["title"] == "Test Article"


@pytest.mark.asyncio
async def test_analyze_page_structure():
    """Test page structure analysis"""
    
    with patch('app.services.scraper.ScrapingEngine') as mock_engine:
        mock_scraper = AsyncMock()
        mock_scraper.fetch_page_content.return_value = {
            "html": """
            <html>
                <body>
                    <h1 class="main-title">Article Title</h1>
                    <div class="author-info">Author Name</div>
                    <time class="publish-date">2025-09-22</time>
                    <div class="article-content">Content here</div>
                </body>
            </html>
            """,
            "url": "https://example.com"
        }
        
        mock_engine.return_value.__aenter__.return_value = mock_scraper
        
        result = await analyze_page_structure("https://example.com")
        
        assert "potential_selectors" in result
        assert "title" in result["potential_selectors"]
        assert "author" in result["potential_selectors"]


class TestSelectorFinding:
    
    def test_find_title_selectors(self):
        """Test title selector finding"""
        
        from app.services.scraper import _find_title_selectors
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <body>
                <h1 class="article-title main-title">Article Title</h1>
                <h1>Another Title</h1>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        selectors = _find_title_selectors(soup)
        
        assert any("article-title" in sel for sel in selectors)
        assert "h1" in selectors
    
    def test_find_author_selectors(self):
        """Test author selector finding"""
        
        from app.services.scraper import _find_author_selectors
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <body>
                <div class="author-name">John Doe</div>
                <span class="byline">Reporter</span>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        selectors = _find_author_selectors(soup)
        
        assert any("author-name" in sel for sel in selectors)
        assert any("byline" in sel for sel in selectors)
    
    def test_find_content_selectors(self):
        """Test content selector finding"""
        
        from app.services.scraper import _find_content_selectors
        from bs4 import BeautifulSoup
        
        html = """
        <html>
            <body>
                <article class="main-article">
                    <div class="article-content">Content here</div>
                </article>
                <div class="post-body">More content</div>
            </body>
        </html>
        """
        
        soup = BeautifulSoup(html, 'html.parser')
        selectors = _find_content_selectors(soup)
        
        assert any("article-content" in sel for sel in selectors)
        assert any("post-body" in sel for sel in selectors)
        assert "article" in selectors


if __name__ == "__main__":
    pytest.main([__file__])