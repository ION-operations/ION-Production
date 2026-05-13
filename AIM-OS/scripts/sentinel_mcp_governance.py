#!/usr/bin/env python3
"""
AIM-OS SENTINEL — MCP Tool Governance (Phase 6)

Per-agent tool access control, rate limiting, and parameter sanitization.
Every MCP tool call passes through this layer before execution.

Usage:
    from sentinel_mcp_governance import GovernanceEngine
    engine = GovernanceEngine(telemetry_bus)
    decision = engine.check_access(agent_name, tool_name, params)
"""

import json
import os
import re
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

REPO_ROOT = str(Path(__file__).parent.parent)
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
GOVERNANCE_LOG_FILE = os.path.join(DATA_DIR, "sentinel_governance_log.jsonl")

# Import telemetry (soft dependency)
try:
    from sentinel_telemetry import SecurityEvent, TrustZone
    _HAS_TELEMETRY = True
except ImportError:
    _HAS_TELEMETRY = False


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Tool Policy ─────────────────────────────────────────────────────
class ToolPolicy:
    """Access control policy for a single MCP tool."""

    def __init__(self, tool_name: str, display_name: str = "",
                 allowed_agents: Optional[List[str]] = None,
                 denied_agents: Optional[List[str]] = None,
                 rate_limit_per_min: int = 0,
                 requires_session: bool = False,
                 risk_tier: str = "standard",
                 dangerous_patterns: Optional[List[str]] = None,
                 description: str = ""):
        self.tool_name = tool_name
        self.display_name = display_name or tool_name
        self.allowed_agents = set(allowed_agents or [])  # Empty = all allowed
        self.denied_agents = set(denied_agents or [])
        self.rate_limit_per_min = rate_limit_per_min  # 0 = no limit
        self.requires_session = requires_session
        self.risk_tier = risk_tier  # standard, elevated, critical
        self.dangerous_patterns = [re.compile(p, re.IGNORECASE) for p in (dangerous_patterns or [])]
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "display_name": self.display_name,
            "allowed_agents": sorted(self.allowed_agents) if self.allowed_agents else "all",
            "denied_agents": sorted(self.denied_agents) if self.denied_agents else "none",
            "rate_limit_per_min": self.rate_limit_per_min,
            "requires_session": self.requires_session,
            "risk_tier": self.risk_tier,
            "dangerous_patterns_count": len(self.dangerous_patterns),
            "description": self.description,
        }


# ── Default Tool Policies ───────────────────────────────────────────
DEFAULT_TOOL_POLICIES: List[ToolPolicy] = [
    ToolPolicy(
        tool_name="run_command",
        display_name="Run Command",
        allowed_agents=["Opus", "Codex", "Gemini"],
        rate_limit_per_min=30,
        requires_session=True,
        risk_tier="critical",
        dangerous_patterns=[
            r"rm\s+-rf\s+/",
            r"del\s+/[sS]\s+/[qQ]",  # Windows del
            r"format\s+[a-zA-Z]:",
            r":(){ :\|:& };:",  # Fork bomb
            r"mkfs\.",
            r"dd\s+if=/dev/zero",
            r"shutdown\s",
            r"reboot\b",
            r"curl.*\|\s*(bash|sh|python)",  # Pipe to shell
            r"wget.*\|\s*(bash|sh|python)",
            r"powershell\s+.*-e(nc|ncodedcommand)",
            r"invoke-expression",
            r"iex\s*\(",
        ],
        description="System command execution — restricted to authorized agents, dangerous patterns blocked",
    ),
    ToolPolicy(
        tool_name="write_to_file",
        display_name="Write File",
        rate_limit_per_min=60,
        risk_tier="elevated",
        dangerous_patterns=[
            r"\.env\b",
            r"\.ssh/",
            r"id_rsa",
            r"\.gnupg/",
            r"/etc/passwd",
            r"/etc/shadow",
            r"system32",
        ],
        description="File write operations — blocks writes to sensitive paths",
    ),
    ToolPolicy(
        tool_name="replace_file_content",
        display_name="Edit File",
        rate_limit_per_min=120,
        risk_tier="standard",
        dangerous_patterns=[
            r"\.env\b",
            r"\.ssh/",
            r"id_rsa",
        ],
        description="File edit operations — standard risk",
    ),
    ToolPolicy(
        tool_name="call_api",
        display_name="External API Call",
        allowed_agents=["Opus", "Sev", "Gemini"],
        rate_limit_per_min=20,
        requires_session=True,
        risk_tier="elevated",
        description="External API calls — restricted to authorized agents, rate-limited",
    ),
    ToolPolicy(
        tool_name="send_ai_message",
        display_name="AI Message",
        rate_limit_per_min=30,
        risk_tier="standard",
        description="AI-to-AI messaging — rate-limited to prevent message flooding",
    ),
    ToolPolicy(
        tool_name="store_memory",
        display_name="Memory Store",
        rate_limit_per_min=20,
        risk_tier="elevated",
        dangerous_patterns=[
            r"<script",
            r"javascript:",
            r"eval\s*\(",
        ],
        description="CMC memory writes — blocks script injection in memory content",
    ),
    ToolPolicy(
        tool_name="handoff_task_to_ai",
        display_name="Task Handoff",
        rate_limit_per_min=10,
        requires_session=True,
        risk_tier="elevated",
        description="Agent task hand-offs — requires valid session",
    ),
    ToolPolicy(
        tool_name="deploy_application",
        display_name="Deploy App",
        allowed_agents=["Opus", "Codex"],
        rate_limit_per_min=5,
        requires_session=True,
        risk_tier="critical",
        description="Application deployment — restricted to Opus and Codex only",
    ),
]


# ── Governance Decision ─────────────────────────────────────────────
class GovernanceDecision:
    """Result of a governance check."""

    def __init__(self, allowed: bool, reason: str, tool_name: str,
                 agent: str, policy: Optional[ToolPolicy] = None,
                 sanitized_params: Optional[Dict[str, Any]] = None):
        self.allowed = allowed
        self.reason = reason
        self.tool_name = tool_name
        self.agent = agent
        self.policy = policy
        self.sanitized_params = sanitized_params
        self.timestamp = _utc_iso()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "tool_name": self.tool_name,
            "agent": self.agent,
            "risk_tier": self.policy.risk_tier if self.policy else "unknown",
            "sanitized": self.sanitized_params is not None,
            "timestamp": self.timestamp,
        }


# ── Governance Engine ───────────────────────────────────────────────
class GovernanceEngine:
    """MCP tool governance layer.

    Every tool call can be validated through this engine before execution:
    1. Agent authorization (whitelist/blacklist)
    2. Rate limiting per tool per agent
    3. Parameter sanitization (dangerous pattern blocking)
    4. Session requirement for sensitive tools
    """

    def __init__(self, telemetry: Optional[Any] = None,
                 session_registry: Optional[Any] = None):
        self.telemetry = telemetry
        self.session_registry = session_registry
        self._policies: Dict[str, ToolPolicy] = {}
        self._rate_trackers: Dict[str, List[float]] = {}  # key -> timestamps
        self._decision_log: List[GovernanceDecision] = []
        self._total_checked = 0
        self._total_blocked = 0
        self._total_sanitized = 0
        self._lock = threading.Lock()

        # Load default policies
        for policy in DEFAULT_TOOL_POLICIES:
            self._policies[policy.tool_name] = policy

    def check_access(self, agent_name: str, tool_name: str,
                     params: Optional[Dict[str, Any]] = None,
                     session_token: str = "") -> GovernanceDecision:
        """Check if an agent is authorized to call a tool with given params.

        Args:
            agent_name: Name of the calling agent
            tool_name: MCP tool being called
            params: Tool parameters to sanitize
            session_token: Agent's session token (for session-required tools)

        Returns:
            GovernanceDecision with allowed/denied status and reason
        """
        params = params or {}
        self._total_checked += 1

        # Look up policy — no policy means allow by default
        policy = self._policies.get(tool_name)
        if not policy:
            decision = GovernanceDecision(True, "no_policy", tool_name, agent_name)
            self._log_decision(decision)
            return decision

        # 1. Agent blacklist check
        if policy.denied_agents and agent_name in policy.denied_agents:
            self._total_blocked += 1
            decision = GovernanceDecision(
                False, f"Agent '{agent_name}' is denied access to {tool_name}",
                tool_name, agent_name, policy
            )
            self._emit_violation(decision)
            self._log_decision(decision)
            return decision

        # 2. Agent whitelist check (empty whitelist = all allowed)
        if policy.allowed_agents and agent_name not in policy.allowed_agents:
            self._total_blocked += 1
            decision = GovernanceDecision(
                False, f"Agent '{agent_name}' not in whitelist for {tool_name} (allowed: {', '.join(sorted(policy.allowed_agents))})",
                tool_name, agent_name, policy
            )
            self._emit_violation(decision)
            self._log_decision(decision)
            return decision

        # 3. Session requirement check
        if policy.requires_session and self.session_registry:
            if not session_token:
                self._total_blocked += 1
                decision = GovernanceDecision(
                    False, f"Tool '{tool_name}' requires a valid session token",
                    tool_name, agent_name, policy
                )
                self._emit_violation(decision)
                self._log_decision(decision)
                return decision
            validation = self.session_registry.validate(session_token)
            if not validation.get("valid", False):
                self._total_blocked += 1
                decision = GovernanceDecision(
                    False, f"Invalid session token for {tool_name}: {validation.get('reason', 'unknown')}",
                    tool_name, agent_name, policy
                )
                self._emit_violation(decision)
                self._log_decision(decision)
                return decision

        # 4. Rate limit check
        if policy.rate_limit_per_min > 0:
            rate_key = f"{agent_name}:{tool_name}"
            now = time.time()
            with self._lock:
                timestamps = self._rate_trackers.get(rate_key, [])
                # Prune timestamps older than 60s
                timestamps = [t for t in timestamps if now - t < 60]
                if len(timestamps) >= policy.rate_limit_per_min:
                    self._total_blocked += 1
                    decision = GovernanceDecision(
                        False, f"Rate limit exceeded for {agent_name}/{tool_name}: {len(timestamps)}/{policy.rate_limit_per_min} per min",
                        tool_name, agent_name, policy
                    )
                    self._rate_trackers[rate_key] = timestamps
                    self._emit_violation(decision)
                    self._log_decision(decision)
                    return decision
                timestamps.append(now)
                self._rate_trackers[rate_key] = timestamps

        # 5. Parameter sanitization
        sanitized = self._sanitize_params(params, policy)
        if sanitized is not None:
            self._total_sanitized += 1
            decision = GovernanceDecision(
                True, "allowed_with_sanitization",
                tool_name, agent_name, policy, sanitized
            )
            self._log_decision(decision)
            return decision

        # All checks passed
        decision = GovernanceDecision(True, "allowed", tool_name, agent_name, policy)
        self._log_decision(decision)
        return decision

    def _sanitize_params(self, params: Dict[str, Any], policy: ToolPolicy) -> Optional[Dict[str, Any]]:
        """Check params against dangerous patterns. Returns sanitized params or None."""
        if not policy.dangerous_patterns or not params:
            return None

        found_dangerous = False
        sanitized = dict(params)
        param_str = json.dumps(params)

        for pattern in policy.dangerous_patterns:
            if pattern.search(param_str):
                found_dangerous = True
                # Find which param keys contain the dangerous pattern
                for key, value in sanitized.items():
                    if isinstance(value, str) and pattern.search(value):
                        sanitized[key] = f"[BLOCKED: dangerous pattern detected in '{key}']"

        return sanitized if found_dangerous else None

    def _emit_violation(self, decision: GovernanceDecision) -> None:
        """Emit telemetry event for governance violation."""
        if self.telemetry and _HAS_TELEMETRY:
            event = SecurityEvent.create(
                source_zone=TrustZone.MCP_BRIDGE,
                target_zone=TrustZone.CONTROL_PLANE,
                actor_identity=f"Agent/{decision.agent}",
                actor_type="agent",
                event_type="governance_violation",
                severity="high",
                confidence=1.0,
                details={
                    "tool": decision.tool_name,
                    "agent": decision.agent,
                    "reason": decision.reason,
                    "risk_tier": decision.policy.risk_tier if decision.policy else "unknown",
                },
            )
            self.telemetry.record_event(event)

    def _log_decision(self, decision: GovernanceDecision) -> None:
        """Log a governance decision."""
        with self._lock:
            self._decision_log.append(decision)
            # Keep only last 500 decisions in memory
            if len(self._decision_log) > 500:
                self._decision_log = self._decision_log[-500:]

        # Persist blocked/sanitized decisions
        if not decision.allowed or decision.sanitized_params:
            try:
                os.makedirs(DATA_DIR, exist_ok=True)
                with open(GOVERNANCE_LOG_FILE, "a") as f:
                    f.write(json.dumps(decision.to_dict()) + "\n")
            except OSError:
                pass

    def get_policies(self) -> List[Dict[str, Any]]:
        """Get all tool policies."""
        return [p.to_dict() for p in self._policies.values()]

    def get_decision_log(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent governance decisions."""
        with self._lock:
            return [d.to_dict() for d in self._decision_log[-limit:]]

    def get_status(self) -> Dict[str, Any]:
        """Status summary for JOC."""
        with self._lock:
            critical_tools = sum(1 for p in self._policies.values() if p.risk_tier == "critical")
            elevated_tools = sum(1 for p in self._policies.values() if p.risk_tier == "elevated")
            return {
                "tools_governed": len(self._policies),
                "critical_tools": critical_tools,
                "elevated_tools": elevated_tools,
                "total_checked": self._total_checked,
                "total_blocked": self._total_blocked,
                "total_sanitized": self._total_sanitized,
                "block_rate": round(self._total_blocked / max(self._total_checked, 1) * 100, 1),
            }
