"""
DEEPSEARCH Package - Sovereign Local Intelligence Engine

9-layer architecture for comprehensive search with trust and quality scoring.

Now with REAL algorithms:
- Trust scoring (domain + content + recency)
- Shannon entropy (information density)
- Web crawler (async, polite, robots.txt respect)
- Master index (SQLite persistence)
"""

import time
import os
from typing import List, Dict, Optional
from datetime import datetime

from .trust_scorer import TrustScorer
from .entropy_calculator import EntropyCalculator
from .web_crawler import WebCrawler, CrawlResult
from .master_index import MasterIndex

__all__ = [
    'search_deepsearch',
    'TrustScorer',
    'EntropyCalculator',
    'WebCrawler',
    'MasterIndex',
]


def search_deepsearch(
    query: str,
    search_type: str = "mixed",
    depth: int = 3,
    max_results: int = 20,
    filters: dict = None,
    analysis: dict = None,
    synthesis: dict = None,
    workspace_path: str = None
) -> dict:
    """
    Execute DEEPSEARCH with real algorithms
    
    Args:
        query: Search query
        search_type: Type of search (web, filesystem, code, mixed)
        depth: Crawling depth (1-10)
        max_results: Maximum results to return
        filters: Optional filters (domains, dates, trust threshold)
        analysis: Optional analysis options
        synthesis: Optional synthesis options
        workspace_path: Path to workspace for filesystem search
        
    Returns:
        Dictionary with results and metadata
    """
    start_time = time.time()
    
    # Initialize components with REAL algorithms
    trust_scorer = TrustScorer()
    entropy_calc = EntropyCalculator()
    crawler = WebCrawler(rate_limit=1.0)  # 1 req/sec (polite)
    index = MasterIndex()
    
    filters = filters or {}
    analysis = analysis or {}
    synthesis = synthesis or {}
    
    results = []
    
    # Filesystem search (functional now with real scoring)
    if search_type in ['filesystem', 'mixed']:
        if workspace_path and os.path.exists(workspace_path):
            for root, dirs, files in os.walk(workspace_path):
                # Skip common directories
                dirs[:] = [d for d in dirs if d not in [
                    'node_modules', '.git', '__pycache__', 'dist', 
                    'build', 'coverage', 'venv', '.venv', '.icip'
                ]]
                
                for filename in files:
                    if filename.endswith(('.md', '.txt', '.py', '.ts', '.js')):
                        filepath = os.path.join(root, filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            if query.lower() in content.lower():
                                # Calculate REAL scores using algorithms
                                trust = trust_scorer.calculate_trust(
                                    f"file://{filepath}",
                                    content,
                                    None
                                )
                                
                                entropy_score = entropy_calc.calculate_entropy(
                                    content,
                                    normalize=True
                                )
                                
                                quality_score = trust * entropy_score
                                
                                results.append({
                                    'url': f"file://{filepath}",
                                    'title': filename,
                                    'content': content[:500],  # Snippet
                                    'trustScore': trust,
                                    'entropy': entropy_score,
                                    'qualityScore': quality_score,
                                    'type': 'file',
                                })
                                
                                # Store in master index
                                index.add_source(
                                    f"file://{filepath}",
                                    content,
                                    trust,
                                    entropy_score,
                                    {'filename': filename}
                                )
                                
                                if len(results) >= max_results:
                                    break
                        except Exception as e:
                            continue
                
                if len(results) >= max_results:
                    break
    
    # Web search (TODO: Implement in next iteration)
    # Will use crawler.crawl_multiple() for actual web crawling
    if search_type in ['web', 'mixed']:
        # Placeholder for web search
        # Will integrate with Google Custom Search, Bing, etc.
        pass
    
    # Apply filters
    trust_threshold = filters.get('trust_threshold', 0.0)
    results = [r for r in results if r.get('trustScore', 0) >= trust_threshold]
    
    # Sort by quality score (trust * entropy)
    results.sort(key=lambda r: r.get('qualityScore', 0), reverse=True)
    
    # Limit results
    results = results[:max_results]
    
    search_time = time.time() - start_time
    
    # Close index
    index.close()
    
    return {
        "results": results,
        "metadata": {
            "query": query,
            "search_type": search_type,
            "total_results": len(results),
            "search_time": search_time,
            "algorithms_used": ["trust_scoring", "shannon_entropy", "quality_ranking"],
            "avg_trust": sum(r.get('trustScore', 0) for r in results) / max(len(results), 1),
            "avg_entropy": sum(r.get('entropy', 0) for r in results) / max(len(results), 1),
        }
    }
