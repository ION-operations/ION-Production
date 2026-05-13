"""
Web Crawler - Polite async web crawling with robots.txt respect

Conservative, respectful crawling with rate limiting and politeness.
"""

import aiohttp
import asyncio
from urllib.parse import urlparse, urljoin, robotsurl
from urllib.robotparser import RobotFileParser
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from datetime import datetime
import time


@dataclass
class CrawlResult:
    """Result from crawling a URL"""
    url: str
    content: str
    status_code: int
    crawled_at: datetime
    content_type: Optional[str] = None
    error: Optional[str] = None


class WebCrawler:
    """Polite async web crawler"""
    
    def __init__(
        self,
        rate_limit: float = 1.0,  # Requests per second per domain
        timeout: int = 10,         # Request timeout in seconds
        max_retries: int = 3,      # Max retry attempts
        user_agent: str = "DEEPSEARCH/1.0 (Polite Crawler; +https://github.com/aim-os)"
    ):
        """
        Initialize web crawler
        
        Args:
            rate_limit: Max requests per second per domain (default: 1.0 = very polite)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
            user_agent: User agent string
        """
        self.rate_limit = rate_limit
        self.timeout = timeout
        self.max_retries = max_retries
        self.user_agent = user_agent
        
        # Rate limiting: Track last request time per domain
        self.domain_last_request: Dict[str, float] = {}
        
        # robots.txt cache
        self.robots_cache: Dict[str, RobotFileParser] = {}
    
    async def crawl(self, url: str) -> CrawlResult:
        """
        Crawl single URL with politeness
        
        Args:
            url: URL to crawl
            
        Returns:
            CrawlResult with content or error
        """
        domain = self._get_domain(url)
        
        # Check robots.txt
        if not await self._can_crawl(url):
            return CrawlResult(
                url=url,
                content="",
                status_code=403,
                crawled_at=datetime.now(),
                error="Disallowed by robots.txt"
            )
        
        # Rate limiting: Wait if needed
        await self._wait_for_rate_limit(domain)
        
        # Crawl with retries
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        timeout=aiohttp.ClientTimeout(total=self.timeout),
                        headers={'User-Agent': self.user_agent}
                    ) as response:
                        content = await response.text()
                        
                        # Update rate limit tracker
                        self.domain_last_request[domain] = time.time()
                        
                        return CrawlResult(
                            url=url,
                            content=content,
                            status_code=response.status,
                            crawled_at=datetime.now(),
                            content_type=response.content_type
                        )
            
            except asyncio.TimeoutError:
                if attempt == self.max_retries - 1:
                    return CrawlResult(
                        url=url,
                        content="",
                        status_code=0,
                        crawled_at=datetime.now(),
                        error="Timeout"
                    )
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            
            except Exception as e:
                if attempt == self.max_retries - 1:
                    return CrawlResult(
                        url=url,
                        content="",
                        status_code=0,
                        crawled_at=datetime.now(),
                        error=str(e)
                    )
                await asyncio.sleep(2 ** attempt)
        
        return CrawlResult(
            url=url,
            content="",
            status_code=0,
            crawled_at=datetime.now(),
            error="Max retries exceeded"
        )
    
    async def crawl_multiple(self, urls: List[str]) -> List[CrawlResult]:
        """
        Crawl multiple URLs concurrently (with rate limiting per domain)
        
        Args:
            urls: List of URLs to crawl
            
        Returns:
            List of CrawlResults
        """
        tasks = [self.crawl(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        final_results = []
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                final_results.append(CrawlResult(
                    url=url,
                    content="",
                    status_code=0,
                    crawled_at=datetime.now(),
                    error=str(result)
                ))
            else:
                final_results.append(result)
        
        return final_results
    
    async def _can_crawl(self, url: str) -> bool:
        """Check if URL can be crawled per robots.txt"""
        domain = self._get_domain(url)
        
        # Check cache
        if domain in self.robots_cache:
            rp = self.robots_cache[domain]
        else:
            # Fetch robots.txt
            rp = RobotFileParser()
            robots_url = f"{urlparse(url).scheme}://{domain}/robots.txt"
            rp.set_url(robots_url)
            
            try:
                # Fetch with timeout
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        robots_url,
                        timeout=aiohttp.ClientTimeout(total=5),
                        headers={'User-Agent': self.user_agent}
                    ) as response:
                        if response.status == 200:
                            robots_content = await response.text()
                            rp.parse(robots_content.splitlines())
                        else:
                            # No robots.txt or error → allow crawling
                            pass
            except Exception:
                # Error fetching robots.txt → allow crawling (conservative)
                pass
            
            self.robots_cache[domain] = rp
        
        # Check if user agent can fetch
        try:
            return rp.can_fetch(self.user_agent, url) or rp.can_fetch("*", url)
        except Exception:
            # If robots.txt parsing fails, allow (conservative)
            return True
    
    async def _wait_for_rate_limit(self, domain: str):
        """Wait if necessary to respect rate limit"""
        if domain not in self.domain_last_request:
            return
        
        # Calculate time since last request
        elapsed = time.time() - self.domain_last_request[domain]
        
        # Wait if needed (1 / rate_limit = minimum seconds between requests)
        min_interval = 1.0 / self.rate_limit
        if elapsed < min_interval:
            wait_time = min_interval - elapsed
            await asyncio.sleep(wait_time)
    
    def _get_domain(self, url: str) -> str:
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except Exception:
            return "unknown"

