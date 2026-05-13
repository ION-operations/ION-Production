"""
Security Posture Adaptor — Detects new attack surfaces and spawns security audits.

Monitors for new attack surfaces introduced by code changes:
- New API endpoints without auth/rate-limiting
- New dependencies (npm/pip) not yet audited
- New environment variables containing secrets
- Configuration changes that weaken security
- New file I/O or network operations

NL_TAG: ADAPTIVE-SECURITY-001 | Auto-detect attack surfaces | SecurityPostureAdaptor | [ADAPTIVE-CORE-001]
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

logger = logging.getLogger("adaptive_system.security")


# ─────────────────────────────────────────────────────────────
# Security Actions
# ─────────────────────────────────────────────────────────────

SECURITY_ACTIONS = {
    "dep_audit":     {"name": "Dependency Audit",  "action": "npm audit / pip safety check", "cost": "low"},
    "endpoint_scan": {"name": "Endpoint Review",   "action": "Auth + rate-limit check on new routes", "cost": "medium"},
    "secret_scan":   {"name": "Secret Scan",       "action": "Scan for leaked secrets/keys", "cost": "low"},
    "config_review": {"name": "Config Review",     "action": "Review security-related config changes", "cost": "low"},
    "full_audit":    {"name": "Full Security Audit","action": "Spawn AGENT-SECURITY for comprehensive audit", "cost": "high"},
}

# Patterns that indicate security-relevant changes
HIGH_RISK_PATTERNS = [
    "auth", "token", "secret", "password", "api_key", "credential",
    "encrypt", "decrypt", "certificate", "ssl", "tls", "oauth",
    "permission", "role", "admin", "root", "sudo",
]


# ─────────────────────────────────────────────────────────────
# Sensor
# ─────────────────────────────────────────────────────────────

class SecurityPostureSensor(AdaptiveSensor):
    """
    Detects new attack surfaces from code changes.
    
    Context expected:
        change_type: str — "new_dependency", "new_endpoint", "new_env_var",
                           "config_change", "new_file_io", "permission_change"
        module_name: str — affected module
        details: str — description of the change
        new_dependencies: list — new deps added (for dep audit)
        new_endpoints: list — new API routes added
        new_env_vars: list — new env variables
        files_changed: list — changed file paths
        contains_auth_code: bool — whether change touches auth logic
        risk_keywords_found: list — security keywords found in changes
    """
    
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        change_type = context.get("change_type", "")
        if not change_type:
            return None
        
        module = context.get("module_name", "unknown")
        details = context.get("details", "")
        
        _RANK = {0: "low", 1: "medium", 2: "high", 3: "critical"}
        sev_rank = 0
        risks = []
        
        # New dependencies — need audit
        new_deps = context.get("new_dependencies", [])
        if change_type == "new_dependency" and new_deps:
            risks.append(f"{len(new_deps)} new dependencies: {', '.join(new_deps[:5])}")
            sev_rank = max(sev_rank, 2)
            action = "dep_audit"
        
        # New endpoints — need auth check
        elif change_type == "new_endpoint":
            endpoints = context.get("new_endpoints", [])
            risks.append(f"{len(endpoints)} new endpoint(s)")
            sev_rank = max(sev_rank, 2)
            action = "endpoint_scan"
        
        # New env vars — potential secrets
        elif change_type == "new_env_var":
            env_vars = context.get("new_env_vars", [])
            secret_vars = [v for v in env_vars if any(p in v.lower() for p in HIGH_RISK_PATTERNS)]
            if secret_vars:
                risks.append(f"potential secret env vars: {', '.join(secret_vars)}")
                sev_rank = max(sev_rank, 3)
            else:
                risks.append(f"{len(env_vars)} new env var(s)")
                sev_rank = max(sev_rank, 1)
            action = "secret_scan"
        
        # Config changes — review
        elif change_type == "config_change":
            risks.append(f"config changed: {details}")
            auth_touched = context.get("contains_auth_code", False)
            sev_rank = max(sev_rank, 2 if auth_touched else 1)
            action = "config_review"
        
        # Permission changes — always high risk
        elif change_type == "permission_change":
            risks.append(f"permission change: {details}")
            sev_rank = max(sev_rank, 3)
            action = "full_audit"
        
        else:
            # Generic security-relevant change
            keywords = context.get("risk_keywords_found", [])
            if keywords:
                risks.append(f"security keywords: {', '.join(keywords[:5])}")
                sev_rank = max(sev_rank, 2)
                action = "full_audit"
            else:
                return None
        
        if not risks:
            return None
        
        return Signal(
            signal_type="security_surface",
            source="git_diff_analysis",
            severity=_RANK[sev_rank],
            description=f"Security surface in '{module}': {'; '.join(risks)}",
            data={
                "change_type": change_type,
                "module_name": module,
                "risks": risks,
                "details": details,
                "recommended_action": action,
                "new_dependencies": new_deps,
                "new_endpoints": context.get("new_endpoints", []),
                "new_env_vars": context.get("new_env_vars", []),
            },
        )
    
    def get_domain_key(self, signal: Signal) -> str:
        return f"{signal.data.get('change_type', 'unknown')}|{signal.data.get('module_name', 'unknown')}"


# ─────────────────────────────────────────────────────────────
# Analyzer
# ─────────────────────────────────────────────────────────────

class SecurityPostureAnalyzer(AdaptiveAnalyzer):
    """Assesses security posture changes — ALL findings need human review."""
    
    def assess(self, signal: Signal, occurrences: int, exceeds_threshold: bool) -> Assessment:
        action = signal.data.get("recommended_action", "config_review")
        
        # Security always needs human review
        approval_map = {
            "dep_audit": ApprovalLevel.AUTO,      # Automated scan = safe
            "secret_scan": ApprovalLevel.AUTO,     # Automated scan = safe
            "endpoint_scan": ApprovalLevel.LEAD,
            "config_review": ApprovalLevel.LEAD,
            "full_audit": ApprovalLevel.EXECUTIVE,
        }
        approval = approval_map.get(action, ApprovalLevel.LEAD)
        
        severity_map = {"low": Severity.LOW, "medium": Severity.MEDIUM, "high": Severity.HIGH, "critical": Severity.CRITICAL}
        severity = severity_map.get(signal.severity, Severity.MEDIUM)
        
        # Security acts immediately — never ignore
        should_adapt = True
        
        return Assessment(
            should_adapt=should_adapt,
            severity=severity,
            domain_key=signal.data.get("module_name", "unknown"),
            occurrences=occurrences,
            description=f"Security {SECURITY_ACTIONS[action]['name']} for {signal.data.get('module_name')}",
            recommended_action=action,
            approval_level=approval,
            confidence=0.8,
            metadata={"risks": signal.data.get("risks", [])},
        )


# ─────────────────────────────────────────────────────────────
# Generator
# ─────────────────────────────────────────────────────────────

class SecurityPostureGenerator(AdaptiveGenerator):
    """Generates security audit commands or reports."""
    
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        action = assessment.recommended_action
        module = assessment.domain_key
        
        if action == "dep_audit":
            return AdaptiveResponse(
                response_type="security_dep_audit",
                content={
                    "commands": [
                        "npm audit --json",
                        "pip-audit --format=json",
                    ],
                    "module": module,
                },
                description=f"Dependency audit for {module}",
            )
        
        elif action == "secret_scan":
            return AdaptiveResponse(
                response_type="security_secret_scan",
                content={
                    "commands": [
                        "git diff HEAD~1 -- '*.env*' '*.config*' '*.json'",
                        "grep -rn 'API_KEY\\|SECRET\\|PASSWORD\\|TOKEN' --include='*.py' --include='*.ts'",
                    ],
                    "module": module,
                },
                description=f"Secret scan for {module}",
            )
        
        elif action == "endpoint_scan":
            command = (
                f"python scripts/ai_engine/genome_assembler.py spawn agent-security "
                f"--task 'Endpoint auth review for {module}: check auth, rate limiting, input validation'"
            )
            return AdaptiveResponse(
                response_type="security_endpoint_scan",
                content={"command": command, "module": module},
                description=f"Endpoint scan for {module}",
            )
        
        elif action == "config_review":
            return AdaptiveResponse(
                response_type="security_config_review",
                content={
                    "action": "review",
                    "module": module,
                    "message": f"Config change in {module} needs security review",
                    "risks": assessment.metadata.get("risks", []),
                },
                description=f"Config security review for {module}",
            )
        
        else:  # full_audit
            command = (
                f"python scripts/ai_engine/genome_assembler.py spawn agent-security "
                f"--task 'Full security audit for {module}'"
            )
            return AdaptiveResponse(
                response_type="security_full_audit",
                content={"command": command, "module": module},
                description=f"Full security audit for {module}",
            )
    
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        logger.info(f"Security action ready: {response.response_type} for {response.content.get('module', '')}")
        response.executed = True
        return response


# ─────────────────────────────────────────────────────────────
# Factory
# ─────────────────────────────────────────────────────────────

def create_security_posture_adaptor(
    storage_dir: Optional[Path] = None,
) -> AdaptiveSystem:
    """Create a fully wired Security Posture Adaptor."""
    storage = storage_dir or (Path.cwd() / ".agent" / "adaptive")
    
    return AdaptiveSystem(
        name="Security Posture",
        sensor=SecurityPostureSensor(),
        tracker=AdaptiveTracker(
            storage_path=storage / "security_posture.json",
            threshold=1,  # Security acts immediately
            window_days=30,
        ),
        analyzer=SecurityPostureAnalyzer(),
        generator=SecurityPostureGenerator(),
        gatekeeper=AdaptiveGatekeeper(proposals_dir=storage / "proposals"),
    )
