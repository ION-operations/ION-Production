"""
API Key Manager

Manages multiple API keys per provider with rotation, usage tracking, and quota management.
Supports up to 22 keys per provider for massive combined capacity.
"""

import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from collections import defaultdict


class APIKeyManager:
    """
    Manages multiple API keys per provider with rotation and quota tracking.
    
    Features:
    - Supports up to 22 keys per provider
    - Automatic key rotation on quota/rate limit errors
    - Usage tracking per key (requests, tokens, errors)
    - Quota exhaustion detection
    - Rate limit tracking
    """
    
    def __init__(self):
        """Initialize the key manager and load API keys from environment."""
        self.keys: Dict[str, List[str]] = {}  # provider -> [key1, key2, ...]
        self.current_index: Dict[str, int] = defaultdict(int)  # provider -> current key index
        self.usage: Dict[str, Dict[str, Any]] = {}  # key -> {requests, tokens, errors, last_used, ...}
        self.quota_limits: Dict[str, Dict[str, int]] = {}  # key -> {requests_per_minute, tokens_per_day, etc.}
        # Event tracking for timeline logging (Chronos P0 requirement)
        self._last_rotation_event: Optional[Dict[str, Any]] = None
        self._last_quota_event: Optional[Dict[str, Any]] = None
        self._load_api_keys()
    
    def _load_api_keys(self):
        """Load API keys from environment variables (supports multiple keys per provider)."""
        # Initialize provider key lists
        providers = ["gemini", "cerebras", "anthropic", "openai", "deepinfra", "replicate"]
        for provider in providers:
            self.keys[provider] = []
        
        # Load Gemini keys
        single_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if single_key:
            self.keys["gemini"].append(single_key)
        
        # Load multiple Gemini keys (up to 22)
        for i in range(1, 23):
            key = os.getenv(f"GEMINI_API_KEY_{i}")
            if key and key not in self.keys["gemini"]:
                self.keys["gemini"].append(key)
        
        # Load Cerebras keys
        single_key = os.getenv("CEREBRAS_API_KEY")
        if single_key:
            self.keys["cerebras"].append(single_key)
        
        # Load multiple Cerebras keys (up to 22)
        for i in range(1, 23):
            key = os.getenv(f"CEREBRAS_API_KEY_{i}")
            if key and key not in self.keys["cerebras"]:
                self.keys["cerebras"].append(key)
        
        # Phase 2: Load other provider keys (when implemented)
        # Anthropic keys
        single_key = os.getenv("ANTHROPIC_API_KEY")
        if single_key:
            self.keys["anthropic"].append(single_key)
        for i in range(1, 23):
            key = os.getenv(f"ANTHROPIC_API_KEY_{i}")
            if key and key not in self.keys["anthropic"]:
                self.keys["anthropic"].append(key)
        
        # OpenAI keys
        single_key = os.getenv("OPENAI_API_KEY")
        if single_key:
            self.keys["openai"].append(single_key)
        for i in range(1, 23):
            key = os.getenv(f"OPENAI_API_KEY_{i}")
            if key and key not in self.keys["openai"]:
                self.keys["openai"].append(key)
        
        # DeepInfra keys
        single_key = os.getenv("DEEPINFRA_API_KEY")
        if single_key:
            self.keys["deepinfra"].append(single_key)
        for i in range(1, 23):
            key = os.getenv(f"DEEPINFRA_API_KEY_{i}")
            if key and key not in self.keys["deepinfra"]:
                self.keys["deepinfra"].append(key)
        
        # Replicate keys
        single_key = os.getenv("REPLICATE_API_KEY")
        if single_key:
            self.keys["replicate"].append(single_key)
        for i in range(1, 23):
            key = os.getenv(f"REPLICATE_API_KEY_{i}")
            if key and key not in self.keys["replicate"]:
                self.keys["replicate"].append(key)
        
        # Initialize usage tracking for all loaded keys
        for provider, keys in self.keys.items():
            for key in keys:
                self.usage[key] = {
                    "requests": 0,
                    "tokens": 0,
                    "errors": 0,
                    "last_used": None,
                    "quota_exhausted": False,
                    "rate_limited": False,
                    "provider": provider
                }
    
    def get_key(self, provider: str, rotate_on_error: bool = True) -> Optional[str]:
        """
        Get current API key for provider, with rotation support.
        
        Args:
            provider: Provider name (e.g., 'gemini', 'cerebras')
            rotate_on_error: If True, automatically rotate if current key is exhausted
        
        Returns:
            API key string, or None if no keys available
        """
        if provider not in self.keys or not self.keys[provider]:
            return None
        
        # Try current key
        current_index = self.current_index[provider]
        current_key = self.keys[provider][current_index]
        
        # Check if current key is exhausted
        if self.usage[current_key].get("quota_exhausted") and rotate_on_error:
            # Rotate to next key
            return self.rotate_key(provider, reason="quota_exhausted")
        
        return current_key
    
    def rotate_key(self, provider: str, reason: str = "quota_exhausted") -> Optional[str]:
        """
        Rotate to next available API key for provider.
        
        Args:
            provider: Provider name
            reason: Why rotation occurred (e.g., "quota_exhausted", "rate_limited")
        
        Returns:
            Next available key, or None if all keys exhausted
        """
        if provider not in self.keys or not self.keys[provider]:
            return None
        
        # Store old index for event tracking (Chronos P0 requirement)
        old_index = self.current_index[provider]
        old_key = self.keys[provider][old_index]
        
        # Mark current key as exhausted
        self.usage[old_key]["quota_exhausted"] = True
        
        # Find next available key
        total_keys = len(self.keys[provider])
        for _ in range(total_keys):
            self.current_index[provider] = (self.current_index[provider] + 1) % total_keys
            next_key = self.keys[provider][self.current_index[provider]]
            
            # If key is not exhausted, use it
            if not self.usage[next_key].get("quota_exhausted"):
                # Store rotation event for timeline logging (Chronos P0 requirement)
                self._last_rotation_event = {
                    "provider": provider,
                    "old_key_index": old_index,
                    "new_key_index": self.current_index[provider],
                    "reason": reason,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }
                return next_key
        
        # All keys exhausted
        return None
    
    def record_usage(self, key: str, tokens: int = 0, error: bool = False):
        """
        Record API usage for a key.
        
        Args:
            key: API key string
            tokens: Number of tokens used (input + output)
            error: Whether the request resulted in an error
        """
        if key not in self.usage:
            return
        
        self.usage[key]["requests"] += 1
        self.usage[key]["tokens"] += tokens
        if error:
            self.usage[key]["errors"] += 1
        self.usage[key]["last_used"] = datetime.now(timezone.utc)
    
    def mark_quota_exhausted(self, key: str):
        """
        Mark a key as quota exhausted.
        
        Stores quota exhaustion event for timeline logging (Chronos P0 requirement).
        """
        if key in self.usage:
            self.usage[key]["quota_exhausted"] = True
            
            # Store quota exhaustion event for timeline logging (Chronos P0 requirement)
            provider = self.usage[key].get("provider")
            if provider:
                # Find key index
                key_index = None
                for idx, k in enumerate(self.keys.get(provider, [])):
                    if k == key:
                        key_index = idx
                        break
                
                if key_index is not None:
                    self._last_quota_event = {
                        "provider": provider,
                        "key_index": key_index,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
    
    def mark_rate_limited(self, key: str, limited: bool = True):
        """Mark a key as rate limited."""
        if key in self.usage:
            self.usage[key]["rate_limited"] = limited
    
    def get_current_key_index(self, provider: str) -> Optional[int]:
        """
        Get current key index for provider (Sage P1 requirement).
        
        Args:
            provider: Provider name
        
        Returns:
            Current key index (0-21), or None if provider not found
        """
        if provider not in self.current_index:
            return None
        return self.current_index[provider]
    
    def get_usage_stats(self, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage statistics for a provider or all providers.
        
        Args:
            provider: Provider name (None for all providers)
        
        Returns:
            Usage statistics dictionary
        """
        if provider:
            keys = [k for k, v in self.usage.items() if v.get("provider") == provider]
        else:
            keys = list(self.usage.keys())
        
        stats = {
            "total_keys": len(keys),
            "exhausted_keys": sum(1 for k in keys if self.usage[k].get("quota_exhausted")),
            "rate_limited_keys": sum(1 for k in keys if self.usage[k].get("rate_limited")),
            "total_requests": sum(self.usage[k]["requests"] for k in keys),
            "total_tokens": sum(self.usage[k]["tokens"] for k in keys),
            "total_errors": sum(self.usage[k]["errors"] for k in keys),
        }
        
        return stats

