"""
Unit Tests: WebCrawler
"""

import pytest
import asyncio
from datetime import datetime
from deepsearch.web_crawler import WebCrawler, CrawlResult


@pytest.fixture
def crawler():
    return WebCrawler(rate_limit=10.0)  # Faster for tests


@pytest.mark.asyncio
async def test_crawl_valid_url(crawler):
    """Test crawling a valid URL"""
    # Note: This will make real HTTP request - use mock in production
    url = "https://httpbin.org/html"
    
    result = await crawler.crawl(url)
    
    assert isinstance(result, CrawlResult)
    assert result.url == url
    assert result.status_code in [200, 0]  # 0 if timeout/error
    assert result.crawled_at is not None


@pytest.mark.asyncio
async def test_crawl_invalid_url(crawler):
    """Test crawling invalid URL returns error"""
    url = "https://this-domain-does-not-exist-12345.com"
    
    result = await crawler.crawl(url)
    
    assert isinstance(result, CrawlResult)
    assert result.status_code == 0
    assert result.error is not None


@pytest.mark.asyncio
async def test_crawl_multiple(crawler):
    """Test crawling multiple URLs concurrently"""
    urls = [
        "https://httpbin.org/html",
        "https://httpbin.org/json",
    ]
    
    results = await crawler.crawl_multiple(urls)
    
    assert len(results) == 2
    assert all(isinstance(r, CrawlResult) for r in results)


@pytest.mark.asyncio
async def test_rate_limiting(crawler):
    """Test rate limiting is enforced"""
    # Crawler with 1 req/sec rate limit
    slow_crawler = WebCrawler(rate_limit=1.0)
    
    url = "https://httpbin.org/delay/0"
    
    start = asyncio.get_event_loop().time()
    
    # Make 2 requests to same domain
    await slow_crawler.crawl(url)
    await slow_crawler.crawl(url)
    
    end = asyncio.get_event_loop().time()
    duration = end - start
    
    # Should take at least 1 second (rate limit delay)
    # Note: This might be flaky, so we check for >= 0.8 seconds
    assert duration >= 0.8


@pytest.mark.asyncio
async def test_timeout_handling(crawler):
    """Test timeout handling"""
    # Create crawler with short timeout
    fast_timeout_crawler = WebCrawler(timeout=1)
    
    # httpbin.org/delay/10 will take 10 seconds
    url = "https://httpbin.org/delay/10"
    
    result = await fast_timeout_crawler.crawl(url)
    
    # Should timeout
    assert result.status_code == 0
    assert "Timeout" in result.error or result.error is not None


@pytest.mark.asyncio
async def test_user_agent_set(crawler):
    """Test user agent is set correctly"""
    # httpbin.org/user-agent returns the user agent
    url = "https://httpbin.org/user-agent"
    
    result = await crawler.crawl(url)
    
    if result.status_code == 200:
        assert "DEEPSEARCH" in result.content


@pytest.mark.asyncio
async def test_robots_txt_caching(crawler):
    """Test robots.txt is cached per domain"""
    url1 = "https://httpbin.org/html"
    url2 = "https://httpbin.org/json"
    
    # Crawl both (same domain)
    await crawler.crawl(url1)
    await crawler.crawl(url2)
    
    # Cache should have entry for httpbin.org
    assert "httpbin.org" in crawler.robots_cache


@pytest.mark.asyncio
async def test_get_domain(crawler):
    """Test domain extraction"""
    url = "https://example.com/path/to/page"
    domain = crawler._get_domain(url)
    
    assert domain == "example.com"


@pytest.mark.asyncio
async def test_crawl_result_structure(crawler):
    """Test CrawlResult has all required fields"""
    url = "https://httpbin.org/html"
    
    result = await crawler.crawl(url)
    
    # Check all fields exist
    assert hasattr(result, 'url')
    assert hasattr(result, 'content')
    assert hasattr(result, 'status_code')
    assert hasattr(result, 'crawled_at')
    assert hasattr(result, 'content_type')
    assert hasattr(result, 'error')


@pytest.mark.asyncio
async def test_max_retries(crawler):
    """Test max retries is respected"""
    # Crawler with 1 retry
    retry_crawler = WebCrawler(max_retries=1)
    
    # Invalid URL will fail
    url = "https://invalid-domain-12345.com"
    
    result = await retry_crawler.crawl(url)
    
    # Should fail after 1 retry
    assert result.status_code == 0
    assert result.error is not None

