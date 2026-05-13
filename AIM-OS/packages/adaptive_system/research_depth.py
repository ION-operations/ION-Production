"""
Research Depth Adaptor — Auto-deepens investigation when shallow isn't enough.

Detects when VIF confidence is too low on retrieved evidence and
escalates research depth through progressive T-levels (T0→T4).

T0: Memory lookup (CMC/HHNI) — free
T1: Single-agent quick scan — 1 Gemini call
T2: Multi-file analysis — 3-5 Gemini calls
T3: Research Swarm (3 agents) — 10+ Gemini calls
T4: Full Deep Research Protocol — 20+ Gemini calls

NL_TAG: ADAPTIVE-RESEARCH-001 | Auto-deepen research when confidence is low | ResearchDepthAdaptor | [ADAPTIVE-CORE-001]
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

logger = logging.getLogger("adaptive_system.research")


# ─────────────────────────────────────────────────────────────
# T-Levels
# ─────────────────────────────────────────────────────────────

RESEARCH_DEPTHS = {
    "T0": {"name": "Memory Lookup", "method": "CMC/HHNI retrieval", "cost": "free", "agents": 0},
    "T1": {"name": "Quick Scan", "method": "Single-agent file scan", "cost": "1 call", "agents": 1},
    "T2": {"name": "Multi-File Analysis", "method": "Cross-reference analysis", "cost": "3-5 calls", "agents": 1},
    "T3": {"name": "Research Swarm", "method": "3-agent parallel research", "cost": "10+ calls", "agents": 3},
    "T4": {"name": "Deep Research Protocol", "method": "Full 7-phase methodology", "cost": "20+ calls", "agents": 3},
}

DEPTH_ORDER = ["T0", "T1", "T2", "T3", "T4"]


# ─────────────────────────────────────────────────────────────
# Sensor
# ─────────────────────────────────────────────────────────────

class ResearchDepthSensor(AdaptiveSensor):
    """
    Detects when research confidence is too low for the task at hand.
    
    Context expected:
        topic: str — what we're researching
        current_depth: str — current T-level (T0-T4)
        confidence: float — VIF confidence on current results (0-1)
        evidence_count: int — number of evidence pieces found
        task_complexity: float — how complex the task is (0-1)
    """
    
    CONFIDENCE_THRESHOLD = 0.60  # Below this = shallow
    MIN_EVIDENCE_THRESHOLD = 2   # Less than this = insufficient
    
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        topic = context.get("topic", "")
        if not topic:
            return None
        
        confidence = context.get("confidence", 1.0)
        evidence_count = context.get("evidence_count", 10)
        current_depth = context.get("current_depth", "T0")
        task_complexity = context.get("task_complexity", 0.5)
        
        # Already at max depth
        if current_depth == "T4":
            return None
        
        needs_deepening = False
        reasons = []
        
        if confidence < self.CONFIDENCE_THRESHOLD:
            needs_deepening = True
            reasons.append(f"confidence {confidence:.2f} < {self.CONFIDENCE_THRESHOLD}")
        
        if evidence_count < self.MIN_EVIDENCE_THRESHOLD:
            needs_deepening = True
            reasons.append(f"evidence count {evidence_count} < {self.MIN_EVIDENCE_THRESHOLD}")
        
        # High complexity + low depth = needs deepening
        if task_complexity >= 0.7 and current_depth in ("T0", "T1"):
            needs_deepening = True
            reasons.append(f"high complexity ({task_complexity:.2f}) at shallow depth ({current_depth})")
        
        if not needs_deepening:
            return None
        
        # Calculate next depth
        current_idx = DEPTH_ORDER.index(current_depth)
        # Jump by 1 normally, by 2 if confidence is very low
        jump = 2 if confidence < 0.30 else 1
        next_idx = min(current_idx + jump, len(DEPTH_ORDER) - 1)
        next_depth = DEPTH_ORDER[next_idx]
        
        severity = "critical" if confidence < 0.30 else "high" if confidence < 0.45 else "medium"
        
        return Signal(
            signal_type="low_research_confidence",
            source="vif_confidence",
            severity=severity,
            description=f"Research on '{topic}' needs deepening: {', '.join(reasons)}",
            data={
                "topic": topic,
                "current_depth": current_depth,
                "next_depth": next_depth,
                "confidence": confidence,
                "evidence_count": evidence_count,
                "task_complexity": task_complexity,
            },
        )
    
    def get_domain_key(self, signal: Signal) -> str:
        return signal.data.get("topic", "unknown").lower().strip()


# ─────────────────────────────────────────────────────────────
# Analyzer
# ─────────────────────────────────────────────────────────────

class ResearchDepthAnalyzer(AdaptiveAnalyzer):
    """Assesses whether to deepen research and at what level."""
    
    def assess(self, signal: Signal, occurrences: int, exceeds_threshold: bool) -> Assessment:
        next_depth = signal.data.get("next_depth", "T1")
        confidence = signal.data.get("confidence", 0.5)
        
        # Determine approval level by depth cost
        if next_depth in ("T0", "T1", "T2"):
            approval = ApprovalLevel.AUTO
        elif next_depth == "T3":
            approval = ApprovalLevel.LEAD
        else:  # T4
            approval = ApprovalLevel.EXECUTIVE
        
        # Severity mapping
        severity_map = {"low": Severity.LOW, "medium": Severity.MEDIUM, "high": Severity.HIGH, "critical": Severity.CRITICAL}
        severity = severity_map.get(signal.severity, Severity.MEDIUM)
        
        return Assessment(
            should_adapt=True,  # Research can deepen immediately (no threshold needed)
            severity=severity,
            domain_key=signal.data.get("topic", "unknown"),
            occurrences=occurrences,
            description=f"Deepen research from {signal.data.get('current_depth')} → {next_depth}",
            recommended_action=f"spawn_research_{next_depth}",
            approval_level=approval,
            confidence=confidence,
            metadata={"depth_info": RESEARCH_DEPTHS.get(next_depth, {})},
        )


# ─────────────────────────────────────────────────────────────
# Generator
# ─────────────────────────────────────────────────────────────

class ResearchDepthGenerator(AdaptiveGenerator):
    """Generates research depth escalation commands."""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path.cwd()
    
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        """Generate a research depth command."""
        next_depth = assessment.recommended_action.replace("spawn_research_", "")
        depth_info = RESEARCH_DEPTHS.get(next_depth, {})
        topic = assessment.domain_key
        
        # Build spawn command based on depth
        if next_depth in ("T0", "T1"):
            command = f"python scripts/ai_engine/genome_assembler.py spawn agent-research-strategist --task 'Research: {topic}'"
        elif next_depth == "T2":
            command = f"python scripts/ai_engine/genome_assembler.py spawn agent-research-strategist --task 'Deep analysis: {topic}'"
        elif next_depth == "T3":
            command = (
                f"python scripts/ai_engine/genome_assembler.py spawn-division intelligence "
                f"--task 'Research Swarm: {topic}'"
            )
        else:  # T4
            command = (
                f"python scripts/ai_engine/genome_assembler.py spawn-division intelligence "
                f"--task 'Full Deep Research Protocol: {topic}'"
            )
        
        return AdaptiveResponse(
            response_type=f"research_depth_{next_depth}",
            content={
                "command": command,
                "depth": next_depth,
                "depth_info": depth_info,
                "topic": topic,
                "agents_needed": depth_info.get("agents", 1),
            },
            description=f"Deepen research on '{topic}' to {next_depth}: {depth_info.get('name', '')}",
        )
    
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """Log the command for execution (actual spawning handled by caller)."""
        logger.info(f"Research depth command ready: {response.content.get('command', '')}")
        response.executed = True
        return response


# ─────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────

def create_research_depth_adaptor(
    storage_dir: Optional[Path] = None,
    project_root: Optional[Path] = None,
) -> AdaptiveSystem:
    """Create a fully wired Research Depth Adaptor."""
    storage = storage_dir or (Path.cwd() / ".agent" / "adaptive")
    
    return AdaptiveSystem(
        name="Research Depth",
        sensor=ResearchDepthSensor(),
        tracker=AdaptiveTracker(
            storage_path=storage / "research_depth.json",
            threshold=1,  # Research deepens immediately (no recurring threshold)
            window_days=7,
        ),
        analyzer=ResearchDepthAnalyzer(),
        generator=ResearchDepthGenerator(project_root),
        gatekeeper=AdaptiveGatekeeper(proposals_dir=storage / "proposals"),
    )
