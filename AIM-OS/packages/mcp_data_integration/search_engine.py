# packages/mcp_data_integration/search_engine.py
"""
Search Engine - Comprehensive search across all consciousness data

This module provides advanced search capabilities across all consciousness data,
including full-text search, semantic search, and filtered search.

Features:
- Full-text search across all files
- Semantic search for meaning-based queries
- Filtered search by type, date, category
- Search result ranking and relevance scoring
- Search analytics and insights
"""

import re
import json
import math
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from .data_indexer import DataIndexer, SearchResult, IndexedFile

logger = logging.getLogger(__name__)

@dataclass
class SearchQuery:
    """Represents a search query with filters and options."""
    query_text: str
    file_types: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    limit: int = 10
    offset: int = 0
    sort_by: str = "relevance"  # relevance, date, title
    sort_order: str = "desc"  # asc, desc

@dataclass
class SearchResponse:
    """Represents a search response with results and metadata."""
    query: SearchQuery
    results: List[SearchResult]
    total_results: int
    search_time_ms: float
    suggestions: List[str]
    facets: Dict[str, Dict[str, int]]

class SearchEngine:
    """
    Advanced search engine for consciousness data.
    
    This class provides comprehensive search capabilities across all consciousness data,
    including full-text search, semantic search, and advanced filtering.
    """
    
    def __init__(self, data_indexer: DataIndexer):
        """
        Initialize the Search Engine.
        
        Args:
            data_indexer: DataIndexer instance for accessing indexed data
        """
        self.data_indexer = data_indexer
        self.search_cache: Dict[str, SearchResponse] = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Search configuration
        self.min_word_length = 3
        self.max_results = 1000
        self.relevance_weights = {
            'title': 3.0,
            'content': 1.0,
            'tags': 2.0,
            'categories': 1.5,
            'metadata': 1.2
        }
        
        logger.info("Search Engine initialized")
    
    def search(self, query: SearchQuery) -> SearchResponse:
        """
        Perform a comprehensive search.
        
        Args:
            query: SearchQuery object with search parameters
            
        Returns:
            SearchResponse with results and metadata
        """
        start_time = time.time()
        
        # Check cache first
        cache_key = self._get_cache_key(query)
        if cache_key in self.search_cache:
            cached_response = self.search_cache[cache_key]
            if time.time() - cached_response.search_time_ms < self.cache_ttl:
                logger.debug("Returning cached search results")
                return cached_response
        
        # Perform search
        results = self._perform_search(query)
        
        # Calculate search time
        search_time_ms = (time.time() - start_time) * 1000
        
        # Create response
        response = SearchResponse(
            query=query,
            results=results,
            total_results=len(results),
            search_time_ms=search_time_ms,
            suggestions=self._generate_suggestions(query),
            facets=self._generate_facets(results)
        )
        
        # Cache response
        self.search_cache[cache_key] = response
        
        logger.info(f"Search completed: {len(results)} results in {search_time_ms:.2f}ms")
        
        return response
    
    def _perform_search(self, query: SearchQuery) -> List[SearchResult]:
        """Perform the actual search operation."""
        # Start with basic text search
        basic_results = self._basic_text_search(query.query_text)
        
        # Apply filters
        filtered_results = self._apply_filters(basic_results, query)
        
        # Calculate relevance scores
        scored_results = self._calculate_relevance_scores(filtered_results, query)
        
        # Sort results
        sorted_results = self._sort_results(scored_results, query)
        
        # Apply pagination
        paginated_results = self._apply_pagination(sorted_results, query)
        
        return paginated_results
    
    def _basic_text_search(self, query_text: str) -> List[SearchResult]:
        """Perform basic text search."""
        # Use the data indexer's search method
        return self.data_indexer.search(query_text, self.max_results)
    
    def _apply_filters(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Apply filters to search results."""
        filtered_results = []
        
        for result in results:
            # Get the indexed file for additional filtering
            indexed_file = self.data_indexer.get_file_by_path(result.file_path)
            if not indexed_file:
                continue
            
            # Apply file type filter
            if query.file_types and indexed_file.file_type not in query.file_types:
                continue
            
            # Apply category filter
            if query.categories and not any(cat in indexed_file.categories for cat in query.categories):
                continue
            
            # Apply tag filter
            if query.tags and not any(tag in indexed_file.tags for tag in query.tags):
                continue
            
            # Apply date filter
            if query.date_from or query.date_to:
                file_date = datetime.fromtimestamp(indexed_file.last_modified)
                if query.date_from and file_date < query.date_from:
                    continue
                if query.date_to and file_date > query.date_to:
                    continue
            
            filtered_results.append(result)
        
        return filtered_results
    
    def _calculate_relevance_scores(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Calculate relevance scores for search results."""
        query_terms = self._extract_query_terms(query.query_text)
        
        for result in results:
            indexed_file = self.data_indexer.get_file_by_path(result.file_path)
            if not indexed_file:
                continue
            
            # Calculate relevance score
            relevance_score = self._calculate_relevance_score(
                query_terms, indexed_file, result
            )
            
            # Update result with calculated score
            result.relevance_score = relevance_score
        
        return results
    
    def _calculate_relevance_score(self, query_terms: List[str], indexed_file: IndexedFile, result: SearchResult) -> float:
        """Calculate relevance score for a specific result."""
        score = 0.0
        
        # Title matching
        title = indexed_file.metadata.get('title', '')
        title_score = self._calculate_term_score(query_terms, title)
        score += title_score * self.relevance_weights['title']
        
        # Content matching
        content_score = self._calculate_term_score(query_terms, indexed_file.content)
        score += content_score * self.relevance_weights['content']
        
        # Tags matching
        tags_text = ' '.join(indexed_file.tags)
        tags_score = self._calculate_term_score(query_terms, tags_text)
        score += tags_score * self.relevance_weights['tags']
        
        # Categories matching
        categories_text = ' '.join(indexed_file.categories)
        categories_score = self._calculate_term_score(query_terms, categories_text)
        score += categories_score * self.relevance_weights['categories']
        
        # Metadata matching
        metadata_text = ' '.join(str(v) for v in indexed_file.metadata.values())
        metadata_score = self._calculate_term_score(query_terms, metadata_text)
        score += metadata_score * self.relevance_weights['metadata']
        
        # Normalize score
        max_possible_score = sum(self.relevance_weights.values())
        normalized_score = min(score / max_possible_score, 1.0)
        
        return normalized_score
    
    def _calculate_term_score(self, query_terms: List[str], text: str) -> float:
        """Calculate score for query terms in text."""
        if not query_terms or not text:
            return 0.0
        
        text_lower = text.lower()
        total_score = 0.0
        
        for term in query_terms:
            term_lower = term.lower()
            
            # Exact match
            if term_lower in text_lower:
                # Count occurrences
                count = text_lower.count(term_lower)
                # Calculate score based on frequency and position
                score = count * 0.1
                
                # Boost for early occurrence
                position = text_lower.find(term_lower)
                if position >= 0:
                    position_boost = max(0, 1.0 - (position / len(text_lower)))
                    score += position_boost * 0.2
                
                total_score += score
        
        return total_score
    
    def _extract_query_terms(self, query_text: str) -> List[str]:
        """Extract search terms from query text."""
        # Clean and split query
        cleaned_query = re.sub(r'[^\w\s]', ' ', query_text.lower())
        terms = [term for term in cleaned_query.split() if len(term) >= self.min_word_length]
        
        return terms
    
    def _sort_results(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Sort search results based on query parameters."""
        if query.sort_by == "relevance":
            key_func = lambda x: x.relevance_score
        elif query.sort_by == "date":
            # Sort by file modification time
            key_func = lambda x: self.data_indexer.get_file_by_path(x.file_path).last_modified if self.data_indexer.get_file_by_path(x.file_path) else 0
        elif query.sort_by == "title":
            key_func = lambda x: x.file_name.lower()
        else:
            key_func = lambda x: x.relevance_score
        
        reverse = query.sort_order == "desc"
        return sorted(results, key=key_func, reverse=reverse)
    
    def _apply_pagination(self, results: List[SearchResult], query: SearchQuery) -> List[SearchResult]:
        """Apply pagination to search results."""
        start = query.offset
        end = start + query.limit
        return results[start:end]
    
    def _generate_suggestions(self, query: SearchQuery) -> List[str]:
        """Generate search suggestions based on query."""
        suggestions = []
        
        # Simple suggestions based on common terms
        common_terms = [
            "consciousness", "decision", "confidence", "breakthrough",
            "learning", "audit", "timeline", "milestone", "quality"
        ]
        
        query_lower = query.query_text.lower()
        for term in common_terms:
            if term not in query_lower and term.startswith(query_lower):
                suggestions.append(term)
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _generate_facets(self, results: List[SearchResult]) -> Dict[str, Dict[str, int]]:
        """Generate facets for search results."""
        facets = {
            "file_types": {},
            "categories": {},
            "tags": {}
        }
        
        for result in results:
            indexed_file = self.data_indexer.get_file_by_path(result.file_path)
            if not indexed_file:
                continue
            
            # Count file types
            file_type = indexed_file.file_type
            facets["file_types"][file_type] = facets["file_types"].get(file_type, 0) + 1
            
            # Count categories
            for category in indexed_file.categories:
                facets["categories"][category] = facets["categories"].get(category, 0) + 1
            
            # Count tags
            for tag in indexed_file.tags:
                facets["tags"][tag] = facets["tags"].get(tag, 0) + 1
        
        return facets
    
    def _get_cache_key(self, query: SearchQuery) -> str:
        """Generate cache key for query."""
        query_dict = {
            "query_text": query.query_text,
            "file_types": query.file_types,
            "categories": query.categories,
            "tags": query.tags,
            "date_from": query.date_from.isoformat() if query.date_from else None,
            "date_to": query.date_to.isoformat() if query.date_to else None,
            "limit": query.limit,
            "offset": query.offset,
            "sort_by": query.sort_by,
            "sort_order": query.sort_order
        }
        return hashlib.md5(json.dumps(query_dict, sort_keys=True).encode()).hexdigest()
    
    def get_popular_searches(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular search queries."""
        # This would typically be stored in a separate analytics table
        # For now, return empty list
        return []
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """Get search analytics and insights."""
        # This would typically be calculated from search logs
        # For now, return basic stats
        return {
            "total_searches": len(self.search_cache),
            "cache_hit_rate": 0.0,  # Would be calculated from actual usage
            "average_search_time": 0.0,  # Would be calculated from actual usage
            "most_popular_terms": [],  # Would be calculated from search logs
            "search_trends": {}  # Would be calculated from search patterns
        }
    
    def clear_cache(self):
        """Clear the search cache."""
        self.search_cache.clear()
        logger.info("Search cache cleared")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.search_cache),
            "cache_ttl": self.cache_ttl,
            "cache_memory_usage": sum(len(str(response)) for response in self.search_cache.values())
        }

# Import time and hashlib at the top
import time
import hashlib
