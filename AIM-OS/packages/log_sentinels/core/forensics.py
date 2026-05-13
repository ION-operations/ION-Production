"""
Forensics adapter - deep local LLM for log analysis.
"""

from typing import Dict, Any
import json

from ..types import Window, ForensicsReport


class ForensicsAdapter:
    """
    Forensics adapter for deep local log analysis.
    
    Uses local LLM (e.g., Ollama/Llama3) for deep analysis.
    Can access raw logs (never leaves machine).
    """
    
    def __init__(self, model: str = "llama3:8b-instruct-q4"):
        """
        Initialize Forensics adapter.
        
        Args:
            model: Local model identifier (Ollama format)
        """
        self.model = model
        self.ollama = None  # Will be initialized when Ollama client is available
    
    async def analyze(
        self,
        window: Window,
        context: Dict[str, Any]
    ) -> ForensicsReport:
        """
        Analyze log window using Forensics LLM.
        
        Args:
            window: Window to analyze
            context: Local context (diffs, tests, PRs, etc.)
            
        Returns:
            ForensicsReport with root cause, fix suggestion, evidence
        """
        # Build prompt (can include raw logs - local only)
        prompt = self._build_prompt(window, context)
        
        # Call local LLM (stub for now - will use Ollama in production)
        response = await self._call_llm(prompt)
        
        # Parse report
        report = self._parse_report(response, window.id)
        
        return report
    
    def _build_prompt(self, window: Window, context: Dict[str, Any]) -> str:
        """Build prompt for Forensics LLM."""
        samples_text = "\n".join(window.sample[:20])  # More samples for deep analysis
        
        return f"""Deep analysis of log window:

{samples_text}

Window stats:
- Size: {window.size} records
- Time range: {window.to_time - window.from_time} seconds
- Templates: {len(window.templates)} unique patterns

Context:
{json.dumps(context, indent=2)}

Provide:
1. Root cause analysis
2. Fix suggestion (patch or steps)
3. Evidence references

Return as JSON:
{{
  "summary": "detailed summary",
  "confidence": 0.0-1.0,
  "severity": "low|medium|high",
  "tags": ["tag1", "tag2"],
  "suggested_tools": ["tool1", "tool2"],
  "root_cause": "root cause analysis",
  "fix_suggestion": {{
    "patch": "optional code patch",
    "steps": ["step1", "step2"]
  }},
  "evidence": ["evidence1", "evidence2"]
}}
"""
    
    async def _call_llm(self, prompt: str) -> str:
        """
        Call local LLM API (stub - will use Ollama in production).
        
        In production, this would:
        - Call Ollama API
        - Handle timeouts (8s max)
        - Handle errors
        - Return JSON response
        """
        # Stub implementation
        # In production: return await self.ollama.generate(model=self.model, prompt=prompt, max_tokens=2048, timeout_ms=8000)
        return json.dumps({
            "summary": "Forensics analysis placeholder",
            "confidence": 0.8,
            "severity": "medium",
            "tags": [],
            "suggested_tools": [],
            "root_cause": "Root cause placeholder",
            "fix_suggestion": {
                "steps": ["Step 1", "Step 2"]
            },
            "evidence": []
        })
    
    def _parse_report(self, response: str, window_id: str) -> ForensicsReport:
        """Parse LLM response into ForensicsReport."""
        try:
            data = json.loads(response)
            return ForensicsReport(
                window_id=window_id,
                summary=data.get("summary", ""),
                confidence=data.get("confidence", 0.5),
                severity=data.get("severity", "low"),
                tags=data.get("tags", []),
                suggested_tools=data.get("suggested_tools", []),
                root_cause=data.get("root_cause"),
                fix_suggestion=data.get("fix_suggestion"),
                evidence=data.get("evidence", [])
            )
        except (json.JSONDecodeError, KeyError) as e:
            # Return default report on parse error
            return ForensicsReport(
                window_id=window_id,
                summary="Parse error",
                confidence=0.0,
                severity="low",
                tags=[],
                suggested_tools=[],
                root_cause=None,
                fix_suggestion=None,
                evidence=[]
            )

