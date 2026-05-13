"""
Template miner - extract log templates using Drain3 algorithm.
"""

from typing import List, Dict
import uuid

from ..types import LogRecord, Window


class LogTemplateMiner:
    """
    Template miner using Drain3 algorithm.
    
    Extracts log templates (patterns) from log records,
    enabling efficient log analysis and anomaly detection.
    """
    
    def __init__(self, cache_size: int = 5000):
        self.cache_size = cache_size
        self.miner = None  # Will be Drain3TemplateMiner instance
        self.template_cache: Dict[str, int] = {}
    
    def mine(self, records: List[LogRecord]) -> Dict[str, int]:
        """
        Mine templates from log records.
        
        Args:
            records: List of log records
            
        Returns:
            Dictionary mapping template -> count
        """
        templates = {}
        
        for record in records:
            # Extract template from log message
            template = self._extract_template(record.raw)
            
            # Count occurrences
            templates[template] = templates.get(template, 0) + 1
        
        # Update cache
        self.template_cache.update(templates)
        
        # Evict LRU if cache too large
        if len(self.template_cache) > self.cache_size:
            self._evict_lru()
        
        return templates
    
    def _extract_template(self, log_message: str) -> str:
        """
        Extract template from log message.
        
        In production, would use Drain3 algorithm:
        - Parse log message
        - Identify variable parts
        - Generate template pattern
        
        For now, simple placeholder.
        """
        # Placeholder: return first 50 chars as template
        # In production, would use Drain3 library
        return log_message[:50] + "..."
    
    async def novelty_score(self, window: Window) -> float:
        """
        Compute novelty score for window.
        
        Compares templates in window vs historical templates.
        Higher score = more novel (less similar to historical).
        
        Args:
            window: Window to analyze
            
        Returns:
            Novelty score (0-1), higher = more novel
        """
        if not window.templates:
            return 0.0
        
        # Compare window templates vs historical cache
        novel_count = 0
        total_count = sum(window.templates.values())
        
        for template, count in window.templates.items():
            if template not in self.template_cache:
                # Novel template
                novel_count += count
        
        if total_count == 0:
            return 0.0
        
        # Novelty score: ratio of novel records
        novelty = novel_count / total_count
        
        # Normalize to 0-1 range
        return min(novelty, 1.0)
    
    def _evict_lru(self):
        """Evict least recently used templates from cache."""
        # Simple implementation: remove oldest 10%
        to_remove = len(self.template_cache) // 10
        keys_to_remove = list(self.template_cache.keys())[:to_remove]
        for key in keys_to_remove:
            del self.template_cache[key]

