"""
Knowledge Decay Detector — Detects stale knowledge and flags for refresh.

Cross-references Knowledge Items (KIs) and CMC memories against source
code changes. When referenced files change significantly after a KI was
created, the KI is flagged as potentially stale.

Decay Score = (days_since_ki_update) × (referenced_file_changes) / normalization

NL_TAG: ADAPTIVE-DECAY-001 | Detect stale knowledge items | KnowledgeDecayDetector | [ADAPTIVE-CORE-001]
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime

from .adaptive_core import (
    AdaptiveSensor, AdaptiveTracker, AdaptiveAnalyzer,
    AdaptiveGenerator, AdaptiveGatekeeper, AdaptiveSystem,
    Signal, Assessment, AdaptiveResponse,
    Severity, ApprovalLevel,
)

logger = logging.getLogger("adaptive_system.knowledge_decay")


# ─────────────────────────────────────────────────────────────
# Decay Levels
# ─────────────────────────────────────────────────────────────

DECAY_ACTIONS = {
    "flag":    {"name": "Flag Stale", "action": "Add STALE warning to KI", "cost": "free"},
    "review":  {"name": "Manual Review", "action": "Queue for human review", "cost": "free"},
    "refresh": {"name": "Agent Refresh", "action": "Spawn AGENT-KNOWLEDGE-AUDITOR", "cost": "medium"},
    "rebuild": {"name": "Full Rebuild", "action": "Spawn Research Swarm to rebuild KI", "cost": "high"},
}


# ─────────────────────────────────────────────────────────────
# Sensor
# ─────────────────────────────────────────────────────────────

class KnowledgeDecaySensor(AdaptiveSensor):
    """
    Detects knowledge items that have become stale.
    
    Context expected:
        ki_id: str — KI identifier
        ki_title: str — KI title for display
        days_since_update: int — days since KI was last updated
        referenced_files: int — total files referenced by KI
        changed_files: int — referenced files that changed since KI update
        referenced_functions: int — total functions/classes referenced
        changed_functions: int — referenced functions/classes that changed
        ki_type: str — "architecture", "implementation", "process", "reference"
    """
    
    # Decay score thresholds
    STALE_THRESHOLD = 15.0       # Flag as stale
    REVIEW_THRESHOLD = 30.0      # Queue for review
    REFRESH_THRESHOLD = 60.0     # Needs agent refresh
    REBUILD_THRESHOLD = 120.0    # Needs full rebuild
    
    # Type-based decay multipliers (some knowledge rots faster)
    TYPE_MULTIPLIER = {
        "implementation": 2.0,   # Implementation details rot fastest
        "architecture": 1.0,     # Architecture is more stable
        "process": 0.5,          # Processes rarely change
        "reference": 1.5,        # References need updating
    }
    
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        ki_id = context.get("ki_id", "")
        if not ki_id:
            return None
        
        days = context.get("days_since_update", 0)
        referenced = context.get("referenced_files", 0)
        changed = context.get("changed_files", 0)
        changed_funcs = context.get("changed_functions", 0)
        ki_type = context.get("ki_type", "reference")
        ki_title = context.get("ki_title", ki_id)
        
        # No referenced files = can't decay
        if referenced == 0:
            return None
        
        # Calculate decay score
        change_ratio = changed / referenced if referenced > 0 else 0
        func_weight = min(1.0, changed_funcs / 5) if changed_funcs > 0 else 0
        type_mult = self.TYPE_MULTIPLIER.get(ki_type, 1.0)
        
        decay_score = (days * (change_ratio + func_weight * 0.5)) * type_mult
        
        # Determine action and severity
        if decay_score >= self.REBUILD_THRESHOLD:
            action = "rebuild"
            severity = "critical"
        elif decay_score >= self.REFRESH_THRESHOLD:
            action = "refresh"
            severity = "high"
        elif decay_score >= self.REVIEW_THRESHOLD:
            action = "review"
            severity = "medium"
        elif decay_score >= self.STALE_THRESHOLD:
            action = "flag"
            severity = "low"
        else:
            return None
        
        return Signal(
            signal_type="knowledge_decay",
            source="ki_decay_scanner",
            severity=severity,
            description=(
                f"KI '{ki_title}' has decay score {decay_score:.1f}: "
                f"{changed}/{referenced} referenced files changed in {days} days"
            ),
            data={
                "ki_id": ki_id,
                "ki_title": ki_title,
                "decay_score": decay_score,
                "days_since_update": days,
                "change_ratio": change_ratio,
                "changed_files": changed,
                "referenced_files": referenced,
                "changed_functions": changed_funcs,
                "ki_type": ki_type,
                "recommended_action": action,
            },
        )
    
    def get_domain_key(self, signal: Signal) -> str:
        return signal.data.get("ki_id", "unknown")


# ─────────────────────────────────────────────────────────────
# Analyzer
# ─────────────────────────────────────────────────────────────

class KnowledgeDecayAnalyzer(AdaptiveAnalyzer):
    """Assesses knowledge decay and determines refresh strategy."""
    
    def assess(self, signal: Signal, occurrences: int, exceeds_threshold: bool) -> Assessment:
        action = signal.data.get("recommended_action", "flag")
        decay_score = signal.data.get("decay_score", 0)
        
        # Flagging is always auto; refresh/rebuild need approval
        approval_map = {
            "flag": ApprovalLevel.AUTO,
            "review": ApprovalLevel.AUTO,
            "refresh": ApprovalLevel.LEAD,
            "rebuild": ApprovalLevel.EXECUTIVE,
        }
        approval = approval_map.get(action, ApprovalLevel.AUTO)
        
        severity_map = {"low": Severity.LOW, "medium": Severity.MEDIUM, "high": Severity.HIGH, "critical": Severity.CRITICAL}
        severity = severity_map.get(signal.severity, Severity.MEDIUM)
        
        # Decay acts immediately — no need for recurring threshold
        should_adapt = True
        
        return Assessment(
            should_adapt=should_adapt,
            severity=severity,
            domain_key=signal.data.get("ki_id", "unknown"),
            occurrences=occurrences,
            description=f"{DECAY_ACTIONS[action]['name']} for KI '{signal.data.get('ki_title')}'",
            recommended_action=action,
            approval_level=approval,
            confidence=min(1.0, decay_score / 100),
            metadata={
                "decay_score": decay_score,
                "action_info": DECAY_ACTIONS[action],
            },
        )


# ─────────────────────────────────────────────────────────────
# Generator
# ─────────────────────────────────────────────────────────────

class KnowledgeDecayGenerator(AdaptiveGenerator):
    """Generates decay responses: flags, reviews, or agent spawns."""
    
    def __init__(self, ki_root: Optional[Path] = None):
        self.ki_root = ki_root
    
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        action = assessment.recommended_action
        ki_id = assessment.domain_key
        decay = assessment.metadata.get("decay_score", 0)
        
        if action == "flag":
            return AdaptiveResponse(
                response_type="decay_flag",
                content={
                    "action": "flag",
                    "ki_id": ki_id,
                    "banner": f"⚠️ STALE (decay score: {decay:.0f}) — referenced files have changed since this KI was written.",
                },
                description=f"Flag KI '{ki_id}' as stale (score: {decay:.0f})",
            )
        
        elif action == "review":
            return AdaptiveResponse(
                response_type="decay_review",
                content={
                    "action": "review",
                    "ki_id": ki_id,
                    "message": f"KI '{ki_id}' needs manual review (decay: {decay:.0f}). Referenced code has changed.",
                },
                description=f"Queue KI '{ki_id}' for manual review",
            )
        
        elif action == "refresh":
            command = (
                f"python scripts/ai_engine/genome_assembler.py spawn agent-knowledge-auditor "
                f"--task 'Refresh KI: {ki_id} — verify all claims against current code'"
            )
            return AdaptiveResponse(
                response_type="decay_refresh",
                content={"command": command, "ki_id": ki_id, "decay_score": decay},
                description=f"Spawn AGENT-KNOWLEDGE-AUDITOR to refresh '{ki_id}'",
            )
        
        else:  # rebuild
            command = (
                f"python scripts/ai_engine/genome_assembler.py spawn-division intelligence "
                f"--task 'Full rebuild of KI: {ki_id} — codebase has diverged significantly'"
            )
            return AdaptiveResponse(
                response_type="decay_rebuild",
                content={"command": command, "ki_id": ki_id, "decay_score": decay},
                description=f"Spawn Research Swarm to rebuild '{ki_id}'",
            )
    
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """Log the decay action."""
        logger.info(f"Knowledge decay action ready: {response.response_type} for {response.content.get('ki_id', '')}")
        response.executed = True
        return response


# ─────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────

def create_knowledge_decay_detector(
    storage_dir: Optional[Path] = None,
    ki_root: Optional[Path] = None,
) -> AdaptiveSystem:
    """Create a fully wired Knowledge Decay Detector."""
    storage = storage_dir or (Path.cwd() / ".agent" / "adaptive")
    
    return AdaptiveSystem(
        name="Knowledge Decay",
        sensor=KnowledgeDecaySensor(),
        tracker=AdaptiveTracker(
            storage_path=storage / "knowledge_decay.json",
            threshold=1,  # Report immediately
            window_days=90,  # Long window — decay is slow
        ),
        analyzer=KnowledgeDecayAnalyzer(),
        generator=KnowledgeDecayGenerator(ki_root),
        gatekeeper=AdaptiveGatekeeper(proposals_dir=storage / "proposals"),
    )
