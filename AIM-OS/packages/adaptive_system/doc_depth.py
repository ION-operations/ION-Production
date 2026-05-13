"""
Documentation Depth Adaptor — Auto-generates docs when code outpaces them.

Detects parity drift between code and documentation, then either:
- Creates T0 stubs for undocumented modules
- Updates parity appendices for changed code
- Spawns AGENT-DOCS for deeper T-level generation

NL_TAG: ADAPTIVE-DOCS-001 | Auto-generate docs when code outpaces them | DocDepthAdaptor | [ADAPTIVE-CORE-001]
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

logger = logging.getLogger("adaptive_system.docs")


# ─────────────────────────────────────────────────────────────
# Doc Depth Levels
# ─────────────────────────────────────────────────────────────

DOC_DEPTHS = {
    "stub":   {"name": "T0 Stub", "action": "Create executive summary", "cost": "minimal"},
    "enrich": {"name": "Parity Enrich", "action": "Append code structure appendix", "cost": "low"},
    "t1":     {"name": "T1 Overview", "action": "Full overview generation", "cost": "medium"},
    "t2":     {"name": "T2 Architecture", "action": "Architecture documentation", "cost": "high"},
    "full":   {"name": "Full T0-T4", "action": "Complete documentation suite", "cost": "very high"},
}


# ─────────────────────────────────────────────────────────────
# Sensor
# ─────────────────────────────────────────────────────────────

class DocDepthSensor(AdaptiveSensor):
    """
    Detects documentation parity drift.
    
    Context expected:
        module_name: str — package or module name
        code_changed_files: int — number of changed .py/.ts files since last doc
        new_symbols: int — new classes/functions not in docs
        removed_symbols: int — removed classes/functions still in docs
        doc_exists: bool — whether any docs exist for this module
        parity_score: float — current doc-code parity (0-1)
        last_doc_update: str — ISO timestamp of last doc change
        last_code_update: str — ISO timestamp of last code change
    """
    
    PARITY_THRESHOLD = 0.70    # Below this = docs need update
    STALENESS_DAYS = 14        # Code changed more than N days without doc update
    
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        module_name = context.get("module_name", "")
        if not module_name:
            return None
        
        doc_exists = context.get("doc_exists", True)
        parity_score = context.get("parity_score", 1.0)
        new_symbols = context.get("new_symbols", 0)
        code_changed_files = context.get("code_changed_files", 0)
        
        needs_action = False
        reasons = []
        
        if not doc_exists:
            needs_action = True
            reasons.append("no documentation exists")
            severity = "critical"
            depth = "stub"
        elif parity_score < self.PARITY_THRESHOLD:
            needs_action = True
            reasons.append(f"parity {parity_score:.0%} < {self.PARITY_THRESHOLD:.0%}")
            severity = "high" if parity_score < 0.40 else "medium"
            depth = "enrich" if parity_score > 0.40 else "t1"
        elif new_symbols >= 3:
            needs_action = True
            reasons.append(f"{new_symbols} new symbols undocumented")
            severity = "medium"
            depth = "enrich"
        elif code_changed_files >= 5:
            needs_action = True
            reasons.append(f"{code_changed_files} files changed without doc update")
            severity = "medium"
            depth = "t1"
        else:
            return None
        
        if not needs_action:
            return None
        
        return Signal(
            signal_type="doc_parity_drift",
            source="docs_engine",
            severity=severity,
            description=f"Documentation for '{module_name}' needs update: {', '.join(reasons)}",
            data={
                "module_name": module_name,
                "parity_score": parity_score,
                "new_symbols": new_symbols,
                "code_changed_files": code_changed_files,
                "doc_exists": doc_exists,
                "recommended_depth": depth,
            },
        )
    
    def get_domain_key(self, signal: Signal) -> str:
        return signal.data.get("module_name", "unknown").lower().strip()


# ─────────────────────────────────────────────────────────────
# Analyzer
# ─────────────────────────────────────────────────────────────

class DocDepthAnalyzer(AdaptiveAnalyzer):
    """Assesses documentation depth needed."""
    
    def assess(self, signal: Signal, occurrences: int, exceeds_threshold: bool) -> Assessment:
        depth = signal.data.get("recommended_depth", "stub")
        
        # Approval by depth cost
        if depth in ("stub", "enrich"):
            approval = ApprovalLevel.AUTO
        elif depth in ("t1", "t2"):
            approval = ApprovalLevel.LEAD
        else:
            approval = ApprovalLevel.EXECUTIVE
        
        severity_map = {"low": Severity.LOW, "medium": Severity.MEDIUM, "high": Severity.HIGH, "critical": Severity.CRITICAL}
        severity = severity_map.get(signal.severity, Severity.MEDIUM)
        
        # Docs should respond quickly — lower threshold
        should_adapt = exceeds_threshold or (severity in (Severity.HIGH, Severity.CRITICAL))
        
        return Assessment(
            should_adapt=should_adapt,
            severity=severity,
            domain_key=signal.data.get("module_name", "unknown"),
            occurrences=occurrences,
            description=f"Generate {DOC_DEPTHS[depth]['name']} for {signal.data.get('module_name')}",
            recommended_action=f"generate_docs_{depth}",
            approval_level=approval,
            confidence=1.0 - signal.data.get("parity_score", 0.5),
            metadata={"depth_info": DOC_DEPTHS[depth]},
        )


# ─────────────────────────────────────────────────────────────
# Generator
# ─────────────────────────────────────────────────────────────

class DocDepthGenerator(AdaptiveGenerator):
    """Generates documentation or spawns AGENT-DOCS."""
    
    def __init__(self, docs_root: Optional[Path] = None):
        self.docs_root = docs_root or (Path.cwd() / "docs")
    
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        depth = assessment.recommended_action.replace("generate_docs_", "")
        module = assessment.domain_key
        depth_info = DOC_DEPTHS.get(depth, {})
        
        if depth == "stub":
            # Auto-generate T0 stub content
            content = self._generate_t0_stub(module)
            target = str(self.docs_root / module / "T0_executive.md")
            return AdaptiveResponse(
                response_type="doc_t0_stub",
                content=content,
                target_path=target,
                description=f"T0 executive summary for {module}",
            )
        elif depth == "enrich":
            command = f"python scripts/ai_engine/docs_engine.py enrich --module {module}"
            return AdaptiveResponse(
                response_type="doc_enrich",
                content={"command": command, "module": module},
                description=f"Parity enrich for {module}",
            )
        else:
            command = (
                f"python scripts/ai_engine/genome_assembler.py spawn agent-docs "
                f"--task 'Generate {depth_info.get('name', depth)} documentation for {module}'"
            )
            return AdaptiveResponse(
                response_type=f"doc_{depth}",
                content={"command": command, "module": module, "depth": depth},
                description=f"{depth_info.get('name', depth)} for {module}",
            )
    
    def _generate_t0_stub(self, module: str) -> str:
        """Generate a minimal T0 executive summary."""
        return f"""---
title: "{module.replace('_', ' ').title()}"
level: T0
status: auto-generated
---

# {module.replace('_', ' ').title()}

> Auto-generated by Documentation Depth Adaptor. Awaiting human enrichment.

## Overview

This module provides functionality for {module.replace('_', ' ')}.

## Status

- **Coverage:** Stub only — needs manual review
- **Generated by:** adaptive_system.doc_depth
"""
    
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """Execute: write stub file or log command for spawning."""
        if response.response_type == "doc_t0_stub" and response.target_path:
            target = Path(response.target_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(response.content, encoding="utf-8")
            logger.info(f"T0 stub written: {target}")
        else:
            logger.info(f"Doc command ready: {response.content}")
        
        response.executed = True
        return response


# ─────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────

def create_doc_depth_adaptor(
    storage_dir: Optional[Path] = None,
    docs_root: Optional[Path] = None,
) -> AdaptiveSystem:
    """Create a fully wired Documentation Depth Adaptor."""
    storage = storage_dir or (Path.cwd() / ".agent" / "adaptive")
    
    return AdaptiveSystem(
        name="Documentation Depth",
        sensor=DocDepthSensor(),
        tracker=AdaptiveTracker(
            storage_path=storage / "doc_depth.json",
            threshold=2,  # 2nd detection of same module drift triggers action
            window_days=30,
        ),
        analyzer=DocDepthAnalyzer(),
        generator=DocDepthGenerator(docs_root),
        gatekeeper=AdaptiveGatekeeper(proposals_dir=storage / "proposals"),
    )
