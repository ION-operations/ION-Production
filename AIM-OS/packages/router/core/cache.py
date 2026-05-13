"""
Router caching system - performance optimization for context and tool proposals.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json

from ..types import Snapshot, ToolProposal


class RouterCache:
    """
    Caching system for Router to reduce latency.
    
    Caches:
    - Context snapshots -> Tool proposals
    - Tool proposals -> Ranked tools
    - Embeddings for context fit computation
    """
    
    def __init__(self, ttl_seconds: int = 300, max_size: int = 1000):
        """
        Initialize Router cache.
        
        Args:
            ttl_seconds: Time-to-live for cache entries (default: 5 minutes)
            max_size: Maximum number of cache entries (default: 1000)
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        
        # Cache storage
        self.context_cache: Dict[str, Dict[str, Any]] = {}
        self.tool_cache: Dict[str, List[ToolProposal]] = {}
        self.embedding_cache: Dict[str, List[float]] = {}
        
        # Access tracking for LRU eviction
        self.access_times: Dict[str, datetime] = {}
    
    def _hash_snapshot(self, snapshot: Snapshot) -> str:
        """
        Create hash key for snapshot.
        
        Uses goal, summary, and key context elements.
        """
        key_parts = [
            snapshot.goal,
            snapshot.summary,
            str(len(snapshot.cmc_decisions)),
            str(len(snapshot.hhni_context)),
        ]
        key_string = "|".join(key_parts)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _hash_tool_list(self, tool_names: List[str]) -> str:
        """Create hash key for tool list."""
        sorted_tools = sorted(tool_names)
        key_string = "|".join(sorted_tools)
        return hashlib.sha256(key_string.encode()).hexdigest()[:16]
    
    def _is_expired(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired."""
        if "timestamp" not in cache_entry:
            return True
        
        age = datetime.utcnow() - cache_entry["timestamp"]
        return age.total_seconds() > self.ttl_seconds
    
    def _evict_lru(self):
        """Evict least recently used entry if cache is full."""
        if len(self.context_cache) < self.max_size:
            return
        
        # Find oldest entry
        oldest_key = min(
            self.access_times.keys(),
            key=lambda k: self.access_times.get(k, datetime.min)
        )
        
        # Remove from all caches
        self.context_cache.pop(oldest_key, None)
        self.tool_cache.pop(oldest_key, None)
        self.embedding_cache.pop(oldest_key, None)
        self.access_times.pop(oldest_key, None)
    
    async def get_cached_proposals(
        self,
        snapshot: Snapshot
    ) -> Optional[List[ToolProposal]]:
        """
        Get cached tool proposals for snapshot.
        
        Args:
            snapshot: System state snapshot
            
        Returns:
            Cached proposals if available and not expired, None otherwise
        """
        cache_key = self._hash_snapshot(snapshot)
        
        if cache_key not in self.context_cache:
            return None
        
        entry = self.context_cache[cache_key]
        
        if self._is_expired(entry):
            # Remove expired entry
            self.context_cache.pop(cache_key, None)
            self.tool_cache.pop(cache_key, None)
            return None
        
        # Update access time
        self.access_times[cache_key] = datetime.utcnow()
        
        # Return cached proposals
        return self.tool_cache.get(cache_key)
    
    async def cache_proposals(
        self,
        snapshot: Snapshot,
        proposals: List[ToolProposal]
    ):
        """
        Cache tool proposals for snapshot.
        
        Args:
            snapshot: System state snapshot
            proposals: Tool proposals to cache
        """
        cache_key = self._hash_snapshot(snapshot)
        
        # Evict if needed
        self._evict_lru()
        
        # Store in cache
        self.context_cache[cache_key] = {
            "timestamp": datetime.utcnow(),
            "snapshot_hash": cache_key
        }
        self.tool_cache[cache_key] = proposals
        self.access_times[cache_key] = datetime.utcnow()
    
    async def get_cached_embedding(
        self,
        text: str
    ) -> Optional[List[float]]:
        """
        Get cached embedding for text.
        
        Args:
            text: Text to get embedding for
            
        Returns:
            Cached embedding if available, None otherwise
        """
        cache_key = hashlib.sha256(text.encode()).hexdigest()[:16]
        
        if cache_key not in self.embedding_cache:
            return None
        
        return self.embedding_cache[cache_key]
    
    async def cache_embedding(
        self,
        text: str,
        embedding: List[float]
    ):
        """
        Cache embedding for text.
        
        Args:
            text: Text that was embedded
            embedding: Embedding vector
        """
        cache_key = hashlib.sha256(text.encode()).hexdigest()[:16]
        
        # Evict if needed (separate limit for embeddings)
        if len(self.embedding_cache) >= self.max_size:
            # Simple eviction: remove oldest
            oldest_key = min(
                self.embedding_cache.keys(),
                key=lambda k: self.access_times.get(k, datetime.min)
            )
            self.embedding_cache.pop(oldest_key, None)
            self.access_times.pop(oldest_key, None)
        
        self.embedding_cache[cache_key] = embedding
        self.access_times[cache_key] = datetime.utcnow()
    
    def clear(self):
        """Clear all caches."""
        self.context_cache.clear()
        self.tool_cache.clear()
        self.embedding_cache.clear()
        self.access_times.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "context_cache_size": len(self.context_cache),
            "tool_cache_size": len(self.tool_cache),
            "embedding_cache_size": len(self.embedding_cache),
            "max_size": self.max_size,
            "ttl_seconds": self.ttl_seconds
        }

