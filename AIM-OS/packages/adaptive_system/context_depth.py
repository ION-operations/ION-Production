"""
Context Depth Adaptor — Auto-compresses or enriches context when quality drops.

Detects cognitive drift (rising errors, large context, falling confidence)
and responds by:
- Compressing context (summarize and trim)
- Enriching retrieval (expand HHNI search scope)
- Switching context strategy (raw → summary → atoms)

NL_TAG: ADAPTIVE-CONTEXT-001 | Auto-manage context quality | ContextDepthAdaptor | [ADAPTIVE-CORE-001]
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from .adaptive_core import (
    AdaptiveSensor, AdaptiveTracker, AdaptiveAnalyzer,
    AdaptiveGenerator, AdaptiveGatekeeper, AdaptiveSystem,
    Signal, Assessment, AdaptiveResponse,
    Severity, ApprovalLevel,
)

logger = logging.getLogger("adaptive_system.context")


# ─────────────────────────────────────────────────────────────
# Strategies
# ─────────────────────────────────────────────────────────────

CONTEXT_STRATEGIES = {
    "raw_snapshot":       {"name": "Raw Snapshot", "quality": "high", "token_cost": "very high"},
    "truth_atoms":        {"name": "Truth Atoms", "quality": "high", "token_cost": "medium"},
    "compressed_history": {"name": "Compressed History", "quality": "medium", "token_cost": "low"},
    "big_picture":        {"name": "Big Picture (Atlas)", "quality": "medium", "token_cost": "medium"},
    "minimal":            {"name": "Minimal Essential", "quality": "low", "token_cost": "very low"},
}

# Compression actions in order of aggressiveness
COMPRESSION_LEVELS = [
    {"action": "summarize_old", "description": "Summarize older context entries", "saves": "20-30%"},
    {"action": "switch_strategy", "description": "Switch to more compressed strategy", "saves": "30-50%"},
    {"action": "prune_low_relevance", "description": "Remove low-relevance entries", "saves": "40-60%"},
    {"action": "emergency_compress", "description": "Keep only essential context", "saves": "60-80%"},
]


# ─────────────────────────────────────────────────────────────
# Sensor
# ─────────────────────────────────────────────────────────────

class ContextDepthSensor(AdaptiveSensor):
    """
    Detects context quality degradation.
    
    Context expected:
        context_size_tokens: int — current context window usage
        max_context_tokens: int — max context window (default 100k)
        error_rate: float — recent error/hallucination rate (0-1)
        confidence: float — VIF confidence on recent outputs (0-1)
        working_memory_items: int — active items in working memory
        current_strategy: str — current context strategy name
        retrieval_quality: float — HHNI retrieval relevance (0-1)
    """
    
    CONTEXT_FILL_THRESHOLD = 0.70   # Trigger at 70% context fill
    ERROR_RATE_THRESHOLD = 0.15     # 15%+ error rate = problem
    CONFIDENCE_THRESHOLD = 0.50     # VIF confidence below 0.50 = degrading
    MEMORY_OVERLOAD = 20            # More than 20 working memory items
    
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        context_size = context.get("context_size_tokens", 0)
        max_context = context.get("max_context_tokens", 100000)
        error_rate = context.get("error_rate", 0.0)
        confidence = context.get("confidence", 1.0)
        memory_items = context.get("working_memory_items", 0)
        retrieval_quality = context.get("retrieval_quality", 1.0)
        current_strategy = context.get("current_strategy", "raw_snapshot")
        
        fill_ratio = context_size / max_context if max_context > 0 else 0
        
        problems = []
        # Use numeric rank for proper severity comparison
        _RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
        _NAME = {0: "low", 1: "medium", 2: "high", 3: "critical"}
        sev_rank = 0  # start at "low"
        
        # Context window filling up
        if fill_ratio >= 0.90:
            problems.append(f"context {fill_ratio:.0%} full — emergency")
            sev_rank = max(sev_rank, 3)
        elif fill_ratio >= self.CONTEXT_FILL_THRESHOLD:
            problems.append(f"context {fill_ratio:.0%} full")
            sev_rank = max(sev_rank, 2)
        
        # Error rate rising
        if error_rate >= 0.30:
            problems.append(f"error rate {error_rate:.0%} — critical")
            sev_rank = max(sev_rank, 3)
        elif error_rate >= self.ERROR_RATE_THRESHOLD:
            problems.append(f"error rate {error_rate:.0%}")
            sev_rank = max(sev_rank, 2)
        
        # Confidence dropping
        if confidence < 0.30:
            problems.append(f"confidence {confidence:.2f} — very low")
            sev_rank = max(sev_rank, 3)
        elif confidence < self.CONFIDENCE_THRESHOLD:
            problems.append(f"confidence {confidence:.2f} — low")
            sev_rank = max(sev_rank, 1)
        
        # Memory overload
        if memory_items > self.MEMORY_OVERLOAD:
            problems.append(f"{memory_items} items in working memory")
            sev_rank = max(sev_rank, 1)
        
        # Low retrieval quality
        if retrieval_quality < 0.40:
            problems.append(f"retrieval quality {retrieval_quality:.2f} — needs enrichment")
            sev_rank = max(sev_rank, 1)
        
        severity = _NAME[sev_rank]
        
        if not problems:
            return None
        
        # Determine recommended action
        if severity == "critical":
            action = "emergency_compress"
        elif fill_ratio >= self.CONTEXT_FILL_THRESHOLD:
            action = "summarize_old"
        elif retrieval_quality < 0.40:
            action = "enrich_retrieval"
        elif error_rate >= self.ERROR_RATE_THRESHOLD:
            action = "switch_strategy"
        else:
            action = "summarize_old"
        
        return Signal(
            signal_type="context_degradation",
            source="cas_drift_detection",
            severity=severity,
            description=f"Context quality degrading: {'; '.join(problems)}",
            data={
                "fill_ratio": fill_ratio,
                "error_rate": error_rate,
                "confidence": confidence,
                "memory_items": memory_items,
                "retrieval_quality": retrieval_quality,
                "current_strategy": current_strategy,
                "recommended_action": action,
                "problems": problems,
            },
        )
    
    def get_domain_key(self, signal: Signal) -> str:
        return signal.data.get("recommended_action", "context_general")


# ─────────────────────────────────────────────────────────────
# Analyzer
# ─────────────────────────────────────────────────────────────

class ContextDepthAnalyzer(AdaptiveAnalyzer):
    """Assesses context quality and determines response."""
    
    def assess(self, signal: Signal, occurrences: int, exceeds_threshold: bool) -> Assessment:
        action = signal.data.get("recommended_action", "summarize_old")
        
        # Context management is always auto-approved (operational, not creative)
        approval = ApprovalLevel.AUTO
        
        severity_map = {"low": Severity.LOW, "medium": Severity.MEDIUM, "high": Severity.HIGH, "critical": Severity.CRITICAL}
        severity = severity_map.get(signal.severity, Severity.MEDIUM)
        
        # Context always needs immediate response — no threshold required
        should_adapt = True
        
        return Assessment(
            should_adapt=should_adapt,
            severity=severity,
            domain_key=action,
            occurrences=occurrences,
            description=f"Context action needed: {action}",
            recommended_action=action,
            approval_level=approval,
            confidence=signal.data.get("confidence", 0.5),
            metadata={
                "fill_ratio": signal.data.get("fill_ratio", 0),
                "problems": signal.data.get("problems", []),
            },
        )


# ─────────────────────────────────────────────────────────────
# Generator
# ─────────────────────────────────────────────────────────────

class ContextDepthGenerator(AdaptiveGenerator):
    """Generates context management responses."""
    
    # Strategy compression order
    STRATEGY_ORDER = ["raw_snapshot", "truth_atoms", "big_picture", "compressed_history", "minimal"]
    
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        action = assessment.recommended_action
        
        if action == "summarize_old":
            return AdaptiveResponse(
                response_type="context_compress",
                content={
                    "action": "summarize_old",
                    "description": "Summarize context entries older than 10 turns",
                    "method": "recursive_summarization",
                    "expected_savings": "20-30%",
                },
                description="Compress old context entries via summarization",
            )
        
        elif action == "switch_strategy":
            current = assessment.metadata.get("current_strategy", "raw_snapshot")
            current_idx = self.STRATEGY_ORDER.index(current) if current in self.STRATEGY_ORDER else 0
            next_idx = min(current_idx + 1, len(self.STRATEGY_ORDER) - 1)
            next_strategy = self.STRATEGY_ORDER[next_idx]
            
            return AdaptiveResponse(
                response_type="context_strategy_switch",
                content={
                    "action": "switch_strategy",
                    "from_strategy": current,
                    "to_strategy": next_strategy,
                    "strategy_info": CONTEXT_STRATEGIES.get(next_strategy, {}),
                },
                description=f"Switch context strategy: {current} → {next_strategy}",
            )
        
        elif action == "enrich_retrieval":
            return AdaptiveResponse(
                response_type="context_enrich",
                content={
                    "action": "enrich_retrieval",
                    "description": "Expand HHNI search scope and re-index critical atoms",
                    "method": "increase_k_neighbors",
                },
                description="Enrich HHNI retrieval by expanding search scope",
            )
        
        elif action == "emergency_compress":
            return AdaptiveResponse(
                response_type="context_emergency",
                content={
                    "action": "emergency_compress",
                    "description": "Keep only essential context — discard all non-critical entries",
                    "method": "keep_essential_only",
                    "expected_savings": "60-80%",
                },
                description="Emergency context compression — keep essentials only",
            )
        
        else:
            return AdaptiveResponse(
                response_type="context_general",
                content={"action": action},
                description=f"Context action: {action}",
            )
    
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """Log the context action for execution by the calling agent."""
        action = response.content.get("action", "unknown")
        logger.info(f"Context depth action ready: {action}")
        response.executed = True
        return response


# ─────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────

def create_context_depth_adaptor(
    storage_dir: Optional[Path] = None,
) -> AdaptiveSystem:
    """Create a fully wired Context Depth Adaptor."""
    storage = storage_dir or (Path.cwd() / ".agent" / "adaptive")
    
    return AdaptiveSystem(
        name="Context Depth",
        sensor=ContextDepthSensor(),
        tracker=AdaptiveTracker(
            storage_path=storage / "context_depth.json",
            threshold=1,  # Context responds immediately
            window_days=1,  # Short window — context is ephemeral
        ),
        analyzer=ContextDepthAnalyzer(),
        generator=ContextDepthGenerator(),
        gatekeeper=AdaptiveGatekeeper(proposals_dir=storage / "proposals"),
    )
