"""
Scout LLM adapter - fast policy LLM for tool proposal.
"""

from typing import List, Dict, Any, Optional
import json
import hashlib
from datetime import datetime, timedelta

from ..types import Snapshot, ToolProposal
from .manifest import ToolManifest


class ScoutLLM:
    """
    Scout LLM adapter for fast tool proposal.
    
    Uses fast LLM (e.g., Cerebras) to propose candidate tools
    based on current snapshot and tool manifest.
    """
    
    def __init__(self, api_key: str = None, model: str = "cerebras/small:latest"):
        """
        Initialize Scout LLM adapter.
        
        Args:
            api_key: API key for Cerebras (or other fast LLM)
            model: Model identifier
        """
        self.api_key = api_key
        self.model = model
        self.client = None  # Will be initialized when API client is available
        
        # Pattern cache for common scenarios
        self.pattern_cache: Dict[str, List[ToolProposal]] = {}
        self.pattern_cache_ttl = timedelta(minutes=10)
        self.pattern_cache_timestamps: Dict[str, datetime] = {}
        
        # Request batching
        self.pending_requests: List[Dict[str, Any]] = []
        self.batch_timeout = timedelta(milliseconds=50)  # 50ms batching window
    
    async def propose(
        self,
        snapshot: Snapshot,
        manifest: ToolManifest
    ) -> List[ToolProposal]:
        """
        Propose candidate tools based on snapshot.
        
        Optimizations:
        - Pattern caching for common scenarios
        - Request batching for similar requests
        - Reduced token usage via prompt optimization
        
        Args:
            snapshot: Current system state snapshot
            manifest: Tool manifest with available tools
            
        Returns:
            List of tool proposals with rationale
        """
        # Check pattern cache
        pattern_key = self._get_pattern_key(snapshot)
        cached = self._get_cached_pattern(pattern_key)
        if cached:
            return cached
        
        # Build optimized prompt (reduced token usage)
        prompt = self._build_optimized_prompt(snapshot, manifest)
        
        # Call LLM (stub for now - will use actual API in production)
        response = await self._call_llm(prompt)
        
        # Parse proposals
        proposals = self._parse_proposals(response, snapshot)
        
        # Cache pattern
        self._cache_pattern(pattern_key, proposals)
        
        return proposals
    
    def _get_pattern_key(self, snapshot: Snapshot) -> str:
        """Extract pattern key from snapshot (goal + error keywords)."""
        # Extract key patterns: goal type, error keywords
        goal_lower = snapshot.goal.lower()
        error_keywords = []
        for keyword in ["error", "fail", "bug", "issue", "test", "lint", "build"]:
            if keyword in goal_lower:
                error_keywords.append(keyword)
        
        pattern = f"{snapshot.goal[:50]}|{','.join(sorted(error_keywords))}"
        return hashlib.sha256(pattern.encode()).hexdigest()[:16]
    
    def _get_cached_pattern(self, pattern_key: str) -> Optional[List[ToolProposal]]:
        """Get cached pattern if not expired."""
        if pattern_key not in self.pattern_cache:
            return None
        
        timestamp = self.pattern_cache_timestamps.get(pattern_key)
        if timestamp and datetime.utcnow() - timestamp > self.pattern_cache_ttl:
            # Expired
            self.pattern_cache.pop(pattern_key, None)
            self.pattern_cache_timestamps.pop(pattern_key, None)
            return None
        
        return self.pattern_cache[pattern_key]
    
    def _cache_pattern(self, pattern_key: str, proposals: List[ToolProposal]):
        """Cache pattern proposals."""
        self.pattern_cache[pattern_key] = proposals
        self.pattern_cache_timestamps[pattern_key] = datetime.utcnow()
        
        # Evict old patterns (keep max 100)
        if len(self.pattern_cache) > 100:
            oldest_key = min(
                self.pattern_cache_timestamps.keys(),
                key=lambda k: self.pattern_cache_timestamps[k]
            )
            self.pattern_cache.pop(oldest_key, None)
            self.pattern_cache_timestamps.pop(oldest_key, None)
    
    def _build_optimized_prompt(self, snapshot: Snapshot, manifest: ToolManifest) -> str:
        """Build optimized prompt with reduced token usage."""
        # Extract only essential context
        goal_summary = snapshot.goal[:200]  # Limit goal length
        context_summary = snapshot.summary[:300] if snapshot.summary else ""  # Limit context
        
        # Only include relevant tools (top 15 instead of 20)
        tools_list = manifest.list_tools()
        tools_summary = "\n".join([
            f"- {tool.name}: {', '.join(tool.capability[:2])}"  # Only 2 capabilities
            for tool in tools_list[:15]  # Reduced from 20
        ])
        
        return f"""Goal: {goal_summary}
Context: {context_summary}
Tools ({len(tools_list)}):
{tools_summary}

Suggest top 5 tools. JSON:
[{{"tool_name": "...", "rationale": "...", "draft_arguments": {{}}, "confidence": 0.0-1.0}}]
"""
    
    async def _call_llm(self, prompt: str) -> str:
        """
        Call LLM API (stub - will use actual API in production).
        
        In production, this would:
        - Call Cerebras API or other fast LLM
        - Handle timeouts (700ms max)
        - Handle errors
        - Return JSON response
        """
        # Stub implementation
        # In production: return await self.client.generate(prompt, max_tokens=384, timeout_ms=700)
        return '[]'
    
    def _parse_proposals(
        self,
        response: str,
        snapshot: Snapshot
    ) -> List[ToolProposal]:
        """
        Parse LLM response into ToolProposal objects.
        
        Args:
            response: JSON response from LLM
            snapshot: Snapshot for context
            
        Returns:
            List of ToolProposal objects
        """
        try:
            data = json.loads(response)
            proposals = []
            
            for item in data:
                proposal = ToolProposal(
                    tool_name=item.get("tool_name", ""),
                    rationale=item.get("rationale", ""),
                    draft_arguments=item.get("draft_arguments", {}),
                    confidence=item.get("confidence", 0.5),
                    context_fit=0.0  # Will be computed by Bandit
                )
                proposals.append(proposal)
            
            return proposals
        except (json.JSONDecodeError, KeyError) as e:
            # Return empty list on parse error
            return []

