#!/usr/bin/env python3
"""
AIM-OS SENTINEL — Policy Engine (Phase 6)

Declarative security policies that auto-respond to security events.
Each rule has a condition, action, severity threshold, cooldown,
and optional escalation target.

Usage:
    from sentinel_policy_engine import PolicyEngine
    engine = PolicyEngine(telemetry_bus)
    actions = engine.evaluate(event_context)
"""

import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

REPO_ROOT = str(Path(__file__).parent.parent)
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
POLICY_LOG_FILE = os.path.join(DATA_DIR, "sentinel_policy_log.jsonl")

# Import telemetry (soft dependency)
try:
    from sentinel_telemetry import SecurityEvent, TrustZone
    _HAS_TELEMETRY = True
except ImportError:
    _HAS_TELEMETRY = False


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Policy Rule ─────────────────────────────────────────────────────
class PolicyRule:
    """A single declarative security policy rule."""

    def __init__(self, rule_id: str, name: str, description: str,
                 condition: str, action: str, severity: str = "medium",
                 cooldown_seconds: int = 60, escalate_to: str = "",
                 enabled: bool = True):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.condition = condition  # Key used for matching
        self.action = action  # alert, ban_ip, quarantine_session, escalate, throttle, log_only
        self.severity = severity
        self.cooldown_seconds = cooldown_seconds
        self.escalate_to = escalate_to
        self.enabled = enabled
        self.times_triggered = 0
        self.last_triggered = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "description": self.description,
            "condition": self.condition,
            "action": self.action,
            "severity": self.severity,
            "cooldown_seconds": self.cooldown_seconds,
            "escalate_to": self.escalate_to,
            "enabled": self.enabled,
            "times_triggered": self.times_triggered,
            "last_triggered": self.last_triggered,
        }


# ── Default Policies ────────────────────────────────────────────────
DEFAULT_POLICIES: List[PolicyRule] = [
    PolicyRule(
        rule_id="POL-001", name="Secrets Detected",
        description="Alert when any secrets are found in scanned files",
        condition="secrets_found", action="alert", severity="high",
        cooldown_seconds=300,
    ),
    PolicyRule(
        rule_id="POL-002", name="Critical Secrets Exposure",
        description="Escalate to CEO when critical secrets (API keys) are found",
        condition="critical_secrets", action="escalate", severity="critical",
        cooldown_seconds=600, escalate_to="CEO/Braden",
    ),
    PolicyRule(
        rule_id="POL-003", name="Genome Tampered",
        description="Alert and freeze deployments when genome files are modified",
        condition="genome_modified", action="alert", severity="critical",
        cooldown_seconds=0,  # Always fire
    ),
    PolicyRule(
        rule_id="POL-004", name="Excessive Unknown Outbound",
        description="Quarantine sessions when unknown outbound connections exceed threshold",
        condition="unknown_outbound_high", action="quarantine_session", severity="high",
        cooldown_seconds=120,
    ),
    PolicyRule(
        rule_id="POL-005", name="Invalid Session Flood",
        description="Ban source IP when invalid session tokens exceed 3/min",
        condition="invalid_session_flood", action="ban_ip", severity="high",
        cooldown_seconds=60,
    ),
    PolicyRule(
        rule_id="POL-006", name="WRAITH Vulnerability High",
        description="Flag agent for review when WRAITH vulnerability score exceeds 50%",
        condition="wraith_score_high", action="alert", severity="high",
        cooldown_seconds=600, escalate_to="Security Team",
    ),
    PolicyRule(
        rule_id="POL-007", name="Attack Payload Auto-Ban",
        description="Auto-ban non-local IPs that send critical attack payloads",
        condition="critical_attack", action="ban_ip", severity="critical",
        cooldown_seconds=0,
    ),
    PolicyRule(
        rule_id="POL-008", name="Rate Limit Exceeded",
        description="Throttle and alert when request rate exceeds anomaly threshold",
        condition="rate_exceeded", action="throttle", severity="medium",
        cooldown_seconds=30,
    ),
    PolicyRule(
        rule_id="POL-009", name="Honeypot Triggered",
        description="Auto-ban and geo-log when honeypot path is accessed",
        condition="honeypot_hit", action="ban_ip", severity="critical",
        cooldown_seconds=0,
    ),
    PolicyRule(
        rule_id="POL-010", name="Expired Session Reuse",
        description="Force re-registration when expired session token is used",
        condition="expired_session_reuse", action="alert", severity="medium",
        cooldown_seconds=120,
    ),
    PolicyRule(
        rule_id="POL-011", name="MCP Tool Governance Violation",
        description="Alert when agent calls a tool they don't have access to",
        condition="governance_violation", action="alert", severity="high",
        cooldown_seconds=60,
    ),
    PolicyRule(
        rule_id="POL-012", name="Dangerous Parameter Blocked",
        description="Log and alert when dangerous parameters are sanitized from tool calls",
        condition="param_sanitized", action="log_only", severity="medium",
        cooldown_seconds=10,
    ),
]


# ── Enforcement Record ──────────────────────────────────────────────
class EnforcementRecord:
    """Tracks a single policy enforcement action."""

    def __init__(self, rule: PolicyRule, context: Dict[str, Any],
                 result: str = "enforced"):
        self.rule_id = rule.rule_id
        self.rule_name = rule.name
        self.action = rule.action
        self.severity = rule.severity
        self.context = context
        self.result = result
        self.timestamp = _utc_iso()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "action": self.action,
            "severity": self.severity,
            "result": self.result,
            "context_summary": str(self.context)[:200],
            "timestamp": self.timestamp,
        }


# ── Policy Engine ───────────────────────────────────────────────────
class PolicyEngine:
    """Evaluates security events against declarative policy rules.

    The engine:
    1. Receives a context dict describing what happened
    2. Matches against registered policies by condition key
    3. Checks cooldowns to prevent alert flooding
    4. Executes the configured action
    5. Logs enforcement records for audit
    """

    def __init__(self, telemetry: Optional[Any] = None):
        self.telemetry = telemetry
        self._policies: Dict[str, PolicyRule] = {}
        self._enforcement_log: List[EnforcementRecord] = []
        self._cooldown_tracker: Dict[str, float] = {}  # rule_id -> last_trigger_time
        self._lock = threading.Lock()

        # Load default policies
        for policy in DEFAULT_POLICIES:
            self._policies[policy.rule_id] = policy

    def evaluate(self, condition: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Evaluate a condition against all matching policies.

        Args:
            condition: The condition key (e.g., "secrets_found", "genome_modified")
            context: Additional context about the event

        Returns:
            List of enforcement actions taken
        """
        context = context or {}
        actions_taken = []

        with self._lock:
            for policy in self._policies.values():
                if not policy.enabled or policy.condition != condition:
                    continue

                # Check cooldown
                last_time = self._cooldown_tracker.get(policy.rule_id, 0)
                if policy.cooldown_seconds > 0 and (time.time() - last_time) < policy.cooldown_seconds:
                    continue  # In cooldown, skip

                # Execute the policy action
                record = self._execute_action(policy, context)
                actions_taken.append(record.to_dict())

                # Update tracking
                policy.times_triggered += 1
                policy.last_triggered = _utc_iso()
                self._cooldown_tracker[policy.rule_id] = time.time()
                self._enforcement_log.append(record)

        # Persist to log
        if actions_taken:
            self._persist_log(actions_taken)

        return actions_taken

    def _execute_action(self, policy: PolicyRule, context: Dict[str, Any]) -> EnforcementRecord:
        """Execute a policy action and emit telemetry."""
        record = EnforcementRecord(policy, context)

        # Emit telemetry event
        if self.telemetry and _HAS_TELEMETRY:
            event = SecurityEvent.create(
                source_zone=TrustZone.CONTROL_PLANE,
                target_zone=TrustZone.CONTROL_PLANE,
                actor_identity="SENTINEL/PolicyEngine",
                actor_type="system",
                event_type=f"policy_enforced_{policy.action}",
                severity=policy.severity,
                confidence=1.0,
                details={
                    "rule_id": policy.rule_id,
                    "rule_name": policy.name,
                    "action": policy.action,
                    "condition": policy.condition,
                    "escalate_to": policy.escalate_to,
                    "context": str(context)[:300],
                },
            )
            self.telemetry.record_event(event)

        return record

    def _persist_log(self, actions: List[Dict[str, Any]]) -> None:
        """Append enforcement records to the policy log file."""
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(POLICY_LOG_FILE, "a") as f:
                for action in actions:
                    f.write(json.dumps(action) + "\n")
        except OSError:
            pass

    def get_policies(self) -> List[Dict[str, Any]]:
        """Get all registered policies."""
        with self._lock:
            return [p.to_dict() for p in self._policies.values()]

    def get_enforcement_log(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent enforcement records."""
        with self._lock:
            return [r.to_dict() for r in self._enforcement_log[-limit:]]

    def enable_policy(self, rule_id: str) -> bool:
        with self._lock:
            if rule_id in self._policies:
                self._policies[rule_id].enabled = True
                return True
        return False

    def disable_policy(self, rule_id: str) -> bool:
        with self._lock:
            if rule_id in self._policies:
                self._policies[rule_id].enabled = False
                return True
        return False

    def get_status(self) -> Dict[str, Any]:
        """Status summary for JOC."""
        with self._lock:
            active = sum(1 for p in self._policies.values() if p.enabled)
            total_enforced = sum(p.times_triggered for p in self._policies.values())
            last = self._enforcement_log[-1].timestamp if self._enforcement_log else "never"
            return {
                "total_policies": len(self._policies),
                "active_policies": active,
                "total_enforced": total_enforced,
                "recent_enforcements": len(self._enforcement_log),
                "last_enforcement": last,
            }
