"""
Scout adapter - fast cloud LLM for log analysis.
"""

from typing import Dict, Any
import json

from ..types import Window, ScoutReport


class ScoutAdapter:
    """
    Scout adapter for fast cloud log analysis.
    
    Uses fast LLM (e.g., Cerebras) to analyze log windows.
    Only sees redacted logs (PII removed).
    """
    
    def __init__(self, api_key: str = None, model: str = "cerebras/small:latest"):
        """
        Initialize Scout adapter.
        
        Args:
            api_key: API key for Cerebras (or other fast LLM)
            model: Model identifier
        """
        self.api_key = api_key
        self.model = model
        self.client = None  # Will be initialized when API client is available
    
    async def analyze(self, window: Window) -> ScoutReport:
        """
        Analyze log window using Scout LLM.
        
        Args:
            window: Window to analyze
            
        Returns:
            ScoutReport with summary, confidence, severity, tags, suggested tools
        """
        # Build prompt (only uses redacted samples)
        prompt = self._build_prompt(window)
        
        # Call LLM (stub for now - will use actual API in production)
        response = await self._call_llm(prompt)
        
        # Parse report
        report = self._parse_report(response, window.id)
        
        return report
    
    def _build_prompt(self, window: Window) -> str:
        """Build prompt for Scout LLM."""
        samples_text = "\n".join(window.sample[:5])  # Use first 5 samples
        
        return f"""Analyze these log entries from a {window.source} source:

{samples_text}

Window stats:
- Size: {window.size} records
- Time range: {window.to_time - window.from_time} seconds
- Templates: {len(window.templates)} unique patterns

Provide:
1. Brief summary (1-2 sentences)
2. Confidence level (0-1)
3. Severity (low/medium/high)
4. Tags (components/APIs mentioned)
5. Suggested MCP tools that could help

Return as JSON:
{{
  "summary": "brief summary",
  "confidence": 0.0-1.0,
  "severity": "low|medium|high",
  "tags": ["tag1", "tag2"],
  "suggested_tools": ["tool1", "tool2"]
}}
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
        return json.dumps({
            "summary": "Log analysis placeholder",
            "confidence": 0.7,
            "severity": "medium",
            "tags": [],
            "suggested_tools": []
        })
    
    def _parse_report(self, response: str, window_id: str) -> ScoutReport:
        """Parse LLM response into ScoutReport."""
        try:
            data = json.loads(response)
            return ScoutReport(
                window_id=window_id,
                summary=data.get("summary", ""),
                confidence=data.get("confidence", 0.5),
                severity=data.get("severity", "low"),
                tags=data.get("tags", []),
                suggested_tools=data.get("suggested_tools", [])
            )
        except (json.JSONDecodeError, KeyError) as e:
            # Return default report on parse error
            return ScoutReport(
                window_id=window_id,
                summary="Parse error",
                confidence=0.0,
                severity="low",
                tags=[],
                suggested_tools=[]
            )

