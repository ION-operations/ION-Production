"""
Architectural Drift Detector — Detects code pattern violations and flags divergence.

Monitors for violations of established architectural patterns:
- Direct database access bypassing the service layer
- MCP tools not registered through the registry
- Missing error handling on async operations
- Circular or cross-layer imports
- Naming convention violations
- Bypassed abstraction layers

NL_TAG: ADAPTIVE-ARCH-001 | Detect architectural pattern violations | ArchDriftDetector | [ADAPTIVE-CORE-001]
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

logger = logging.getLogger("adaptive_system.arch_drift")


# ─────────────────────────────────────────────────────────────
# Drift Types and Rules
# ─────────────────────────────────────────────────────────────

DRIFT_ACTIONS = {
    "warning":   {"name": "Warning", "action": "Log warning in audit log", "cost": "free"},
    "flag":      {"name": "Flag Violation", "action": "Create violation report", "cost": "free"},
    "refactor":  {"name": "Refactoring Request","action": "Propose refactoring via CODEX", "cost": "medium"},
    "redesign":  {"name": "Redesign Needed",   "action": "Escalate to AGENT-ARCH-MAPPER", "cost": "high"},
}

ARCH_RULES = {
    "layer_bypass": {
        "name": "Layer Bypass",
        "description": "Direct access to data layer bypassing service abstractions",
        "severity": "high",
    },
    "unregistered_tool": {
        "name": "Unregistered MCP Tool",
        "description": "MCP tool implemented but not registered in tool registry",
        "severity": "medium",
    },
    "missing_error_handling": {
        "name": "Missing Error Handling",
        "description": "Async operation without try/catch or error propagation",
        "severity": "medium",
    },
    "circular_import": {
        "name": "Circular Import",
        "description": "Import cycle between modules",
        "severity": "high",
    },
    "naming_violation": {
        "name": "Naming Convention Violation",
        "description": "File, class, or function naming breaks established convention",
        "severity": "low",
    },
    "god_module": {
        "name": "God Module",
        "description": "Module exceeds complexity threshold (too many classes/functions)",
        "severity": "medium",
    },
    "missing_docstring": {
        "name": "Missing Docstring",
        "description": "Public class or function lacks docstring",
        "severity": "low",
    },
}


# ─────────────────────────────────────────────────────────────
# Sensor
# ─────────────────────────────────────────────────────────────

class ArchDriftSensor(AdaptiveSensor):
    """
    Detects architectural drift from established patterns.
    
    Context expected:
        rule_id: str — which arch rule was violated (key in ARCH_RULES)
        module_name: str — affected module
        file_path: str — affected file
        description: str — violation details
        violation_count: int — how many violations in this file/module
        module_complexity: int — total classes + functions in module
        max_complexity: int — threshold (default 50)
    """
    
    COMPLEXITY_THRESHOLD = 50
    
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        rule_id = context.get("rule_id", "")
        module = context.get("module_name", "")
        
        if not rule_id and not module:
            return None
        
        # Check for god module (complexity threshold)
        complexity = context.get("module_complexity", 0)
        max_complexity = context.get("max_complexity", self.COMPLEXITY_THRESHOLD)
        
        if not rule_id and complexity > max_complexity:
            rule_id = "god_module"
        
        if not rule_id:
            return None
        
        rule = ARCH_RULES.get(rule_id)
        if not rule:
            return None
        
        file_path = context.get("file_path", "")
        description = context.get("description", rule["description"])
        violation_count = context.get("violation_count", 1)
        
        # Severity from rule definition
        severity = rule["severity"]
        
        # Escalate for repeated violations
        if violation_count >= 5:
            _RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
            current = _RANK.get(severity, 1)
            severity = {0: "low", 1: "medium", 2: "high", 3: "critical"}[min(current + 1, 3)]
        
        # Determine action
        if severity == "low":
            action = "warning"
        elif severity == "medium":
            action = "flag"
        elif severity == "high":
            action = "refactor"
        else:
            action = "redesign"
        
        return Signal(
            signal_type="arch_drift",
            source="ast_pattern_analysis",
            severity=severity,
            description=f"Architecture violation [{rule['name']}] in '{module}': {description}",
            data={
                "rule_id": rule_id,
                "rule_name": rule["name"],
                "module_name": module,
                "file_path": file_path,
                "violation_count": violation_count,
                "complexity": complexity,
                "recommended_action": action,
            },
        )
    
    def get_domain_key(self, signal: Signal) -> str:
        return f"{signal.data.get('rule_id', 'unknown')}|{signal.data.get('module_name', 'unknown')}"


# ─────────────────────────────────────────────────────────────
# Analyzer
# ─────────────────────────────────────────────────────────────

class ArchDriftAnalyzer(AdaptiveAnalyzer):
    """Assesses architectural drift severity and response."""
    
    def assess(self, signal: Signal, occurrences: int, exceeds_threshold: bool) -> Assessment:
        action = signal.data.get("recommended_action", "warning")
        
        approval_map = {
            "warning": ApprovalLevel.AUTO,
            "flag": ApprovalLevel.AUTO,
            "refactor": ApprovalLevel.LEAD,
            "redesign": ApprovalLevel.EXECUTIVE,
        }
        approval = approval_map.get(action, ApprovalLevel.AUTO)
        
        severity_map = {"low": Severity.LOW, "medium": Severity.MEDIUM, "high": Severity.HIGH, "critical": Severity.CRITICAL}
        severity = severity_map.get(signal.severity, Severity.MEDIUM)
        
        # Drift accumulates — respond after threshold OR high severity
        should_adapt = exceeds_threshold or severity in (Severity.HIGH, Severity.CRITICAL)
        
        return Assessment(
            should_adapt=should_adapt,
            severity=severity,
            domain_key=f"{signal.data.get('rule_id')}|{signal.data.get('module_name')}",
            occurrences=occurrences,
            description=f"{DRIFT_ACTIONS[action]['name']}: {signal.data.get('rule_name')} in {signal.data.get('module_name')}",
            recommended_action=action,
            approval_level=approval,
            confidence=min(1.0, occurrences / 5),
            metadata={
                "rule_id": signal.data.get("rule_id"),
                "violation_count": signal.data.get("violation_count", 0),
            },
        )


# ─────────────────────────────────────────────────────────────
# Generator
# ─────────────────────────────────────────────────────────────

class ArchDriftGenerator(AdaptiveGenerator):
    """Generates drift responses: warnings, flags, refactoring requests."""
    
    def __init__(self, audit_log_dir: Optional[Path] = None):
        self.audit_log_dir = audit_log_dir
    
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        action = assessment.recommended_action
        rule_id = assessment.metadata.get("rule_id", "unknown")
        parts = assessment.domain_key.split("|")
        module = parts[1] if len(parts) > 1 else "unknown"
        
        if action == "warning":
            return AdaptiveResponse(
                response_type="drift_warning",
                content={
                    "level": "warning",
                    "rule": rule_id,
                    "module": module,
                    "message": assessment.description,
                },
                description=f"Architecture warning: {rule_id} in {module}",
            )
        
        elif action == "flag":
            report = self._build_violation_report(assessment)
            return AdaptiveResponse(
                response_type="drift_flag",
                content=report,
                target_path=str(self.audit_log_dir / f"drift_{rule_id}_{module}.md") if self.audit_log_dir else None,
                description=f"Violation report: {rule_id} in {module}",
            )
        
        elif action == "refactor":
            command = (
                f"python scripts/ai_engine/genome_assembler.py spawn codex "
                f"--task 'Refactor {module} to fix {rule_id}: {assessment.description}'"
            )
            return AdaptiveResponse(
                response_type="drift_refactor",
                content={"command": command, "rule": rule_id, "module": module},
                description=f"Refactoring request: {rule_id} in {module}",
            )
        
        else:  # redesign
            command = (
                f"python scripts/ai_engine/genome_assembler.py spawn agent-arch-mapper "
                f"--task 'Redesign needed for {module}: {assessment.description}'"
            )
            return AdaptiveResponse(
                response_type="drift_redesign",
                content={"command": command, "rule": rule_id, "module": module},
                description=f"Redesign request: {rule_id} in {module}",
            )
    
    def _build_violation_report(self, assessment: Assessment) -> dict:
        return {
            "type": "violation_report",
            "rule": assessment.metadata.get("rule_id"),
            "module": assessment.domain_key,
            "description": assessment.description,
            "occurrences": assessment.occurrences,
            "severity": assessment.severity.value,
            "recommendation": "Review and fix before merging",
        }
    
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """Write report or log command."""
        if response.target_path and response.response_type == "drift_flag":
            target = Path(response.target_path)
            target.parent.mkdir(parents=True, exist_ok=True)
            import json
            target.write_text(json.dumps(response.content, indent=2), encoding="utf-8")
            logger.info(f"Drift report written: {target}")
        else:
            logger.info(f"Drift action ready: {response.response_type}")
        
        response.executed = True
        return response


# ─────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────

def create_arch_drift_detector(
    storage_dir: Optional[Path] = None,
    audit_log_dir: Optional[Path] = None,
) -> AdaptiveSystem:
    """Create a fully wired Architectural Drift Detector."""
    storage = storage_dir or (Path.cwd() / ".agent" / "adaptive")
    
    return AdaptiveSystem(
        name="Architectural Drift",
        sensor=ArchDriftSensor(),
        tracker=AdaptiveTracker(
            storage_path=storage / "arch_drift.json",
            threshold=3,  # Drift accumulates — respond after 3 detections
            window_days=30,
        ),
        analyzer=ArchDriftAnalyzer(),
        generator=ArchDriftGenerator(audit_log_dir=audit_log_dir or (storage / "drift_reports")),
        gatekeeper=AdaptiveGatekeeper(proposals_dir=storage / "proposals"),
    )
