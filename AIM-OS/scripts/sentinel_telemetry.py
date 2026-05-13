#!/usr/bin/env python3
"""
AIM-OS SENTINEL — Control-Plane Telemetry (Phase 3)

Normalized event schemas, provenance records, and tamper-evident audit.

Core Data Objects (from Sev's doctrine):
  - SecurityEvent   — a normalized fact about something that happened
  - SecurityFinding  — a reasoned conclusion from events
  - ResponseAction   — an executed security action with provenance
  - EvidencePackage  — preserved materials for investigation
  - PostureMetric    — a measured security state indicator

Trust Zones:
  A=Untrusted External, B=Guarded Ingress, C=Application Runtime,
  D=Control Plane, E=Evidence & Memory, F=Human Command, G=Secrets

Usage:
    from sentinel_telemetry import TelemetryBus, SecurityEvent, TrustZone
    bus = TelemetryBus()
    evt = SecurityEvent.create(
        source_zone=TrustZone.EXTERNAL,
        target_zone=TrustZone.CONTROL_PLANE,
        actor_identity="203.0.113.5",
        event_type="mcp_tool_call",
        severity="medium",
    )
    bus.record_event(evt)
"""

import hashlib
import json
import os
import threading
import time
import uuid
from collections import deque
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = str(Path(__file__).parent.parent)
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
AUDIT_LEDGER_FILE = os.path.join(DATA_DIR, "sentinel_audit_ledger.jsonl")
POSTURE_FILE = os.path.join(DATA_DIR, "sentinel_posture.json")


# ── Trust Zones ─────────────────────────────────────────────────────
class TrustZone(str, Enum):
    """7 trust zones from SENTINEL doctrine."""
    EXTERNAL = "A_EXTERNAL"         # Internet, scanners, hostile
    INGRESS = "B_INGRESS"           # WAF, honeypots, tunnels, proxy
    RUNTIME = "C_RUNTIME"           # HTTP services, relay, router
    CONTROL_PLANE = "D_CONTROL"     # MCP server, tool registry, routing
    EVIDENCE = "E_EVIDENCE"         # Logs, audit, CMC, forensic artifacts
    HUMAN_COMMAND = "F_HUMAN"       # CEO, JOC approvals, overrides
    SECRETS = "G_SECRETS"           # API keys, signing material, credentials


# ── Autonomy Levels ─────────────────────────────────────────────────
class AutonomyLevel(str, Enum):
    """3-tier autonomy from SENTINEL doctrine."""
    AUTO = "auto"           # Reversible, low blast, high-confidence
    GUARDED = "guarded"     # Medium blast, policy gate, rollback exists
    ESCALATED = "escalated" # Human approval required


# ── Severity Levels ─────────────────────────────────────────────────
class Severity(str, Enum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ── Core Data Object: SecurityEvent ─────────────────────────────────
@dataclass
class SecurityEvent:
    """A normalized fact about something that happened."""
    event_id: str
    timestamp: str
    source_zone: str
    target_zone: str
    actor_identity: str
    actor_type: str           # "ip", "agent", "tool", "system", "human"
    event_type: str           # "request", "mcp_tool_call", "file_change", "honeypot", "anomaly", etc.
    severity: str
    confidence: float         # 0.0 - 1.0
    raw_refs: List[str] = field(default_factory=list)
    session_id: str = ""
    correlation_keys: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    mitre_technique: str = ""

    @classmethod
    def create(cls, *, source_zone: TrustZone, target_zone: TrustZone,
               actor_identity: str, event_type: str, severity: str = "info",
               actor_type: str = "system", confidence: float = 0.9,
               session_id: str = "", correlation_keys: Optional[List[str]] = None,
               details: Optional[Dict[str, Any]] = None,
               mitre_technique: str = "", raw_refs: Optional[List[str]] = None) -> "SecurityEvent":
        return cls(
            event_id=f"EVT-{uuid.uuid4().hex[:12]}",
            timestamp=datetime.now(timezone.utc).isoformat(),
            source_zone=source_zone.value if isinstance(source_zone, TrustZone) else source_zone,
            target_zone=target_zone.value if isinstance(target_zone, TrustZone) else target_zone,
            actor_identity=actor_identity,
            actor_type=actor_type,
            event_type=event_type,
            severity=severity,
            confidence=confidence,
            raw_refs=raw_refs or [],
            session_id=session_id,
            correlation_keys=correlation_keys or [],
            details=details or {},
            mitre_technique=mitre_technique,
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Core Data Object: SecurityFinding ───────────────────────────────
@dataclass
class SecurityFinding:
    """A reasoned conclusion drawn from one or more events."""
    finding_id: str
    related_event_ids: List[str]
    summary: str
    hypothesis: str
    evidence: List[str]
    mitre_mapping: str = ""
    affected_assets: List[str] = field(default_factory=list)
    confidence: float = 0.0
    recommended_actions: List[str] = field(default_factory=list)
    timestamp: str = ""

    @classmethod
    def create(cls, *, summary: str, hypothesis: str,
               related_event_ids: Optional[List[str]] = None,
               evidence: Optional[List[str]] = None,
               mitre_mapping: str = "", confidence: float = 0.7,
               recommended_actions: Optional[List[str]] = None) -> "SecurityFinding":
        return cls(
            finding_id=f"FND-{uuid.uuid4().hex[:12]}",
            related_event_ids=related_event_ids or [],
            summary=summary,
            hypothesis=hypothesis,
            evidence=evidence or [],
            mitre_mapping=mitre_mapping,
            confidence=confidence,
            recommended_actions=recommended_actions or [],
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Core Data Object: ResponseAction ────────────────────────────────
@dataclass
class ResponseAction:
    """An attempted or executed security action with full provenance."""
    action_id: str
    trigger_finding_id: str
    action_type: str          # "block_ip", "rate_limit", "ban", "quarantine", "rotate_key", etc.
    autonomy_level: str       # Auto, Guarded, Escalated
    actor: str                # Who/what performed it
    policy_version: str
    result: str               # "success", "failed", "pending_approval"
    rollback_available: bool
    evidence_refs: List[str] = field(default_factory=list)
    timestamp: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def create(cls, *, trigger_finding_id: str = "", action_type: str,
               autonomy_level: AutonomyLevel = AutonomyLevel.AUTO,
               actor: str = "SENTINEL", result: str = "success",
               rollback_available: bool = True,
               evidence_refs: Optional[List[str]] = None,
               details: Optional[Dict[str, Any]] = None) -> "ResponseAction":
        return cls(
            action_id=f"ACT-{uuid.uuid4().hex[:12]}",
            trigger_finding_id=trigger_finding_id,
            action_type=action_type,
            autonomy_level=autonomy_level.value if isinstance(autonomy_level, AutonomyLevel) else autonomy_level,
            actor=actor,
            policy_version="SENTINEL-v2.0",
            result=result,
            rollback_available=rollback_available,
            evidence_refs=evidence_refs or [],
            timestamp=datetime.now(timezone.utc).isoformat(),
            details=details or {},
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Core Data Object: EvidencePackage ───────────────────────────────
@dataclass
class EvidencePackage:
    """Preserved set of materials for investigation or review."""
    evidence_id: str
    artifact_refs: List[str]
    collection_method: str
    chain_of_custody: List[str]
    sensitivity: str          # "public", "internal", "restricted", "secret"
    retention_policy: str     # "30d", "90d", "1y", "permanent"
    timestamp: str = ""

    @classmethod
    def create(cls, *, artifact_refs: Optional[List[str]] = None,
               collection_method: str = "automated",
               sensitivity: str = "internal",
               retention_policy: str = "90d") -> "EvidencePackage":
        return cls(
            evidence_id=f"EVD-{uuid.uuid4().hex[:12]}",
            artifact_refs=artifact_refs or [],
            collection_method=collection_method,
            chain_of_custody=[f"SENTINEL @ {datetime.now(timezone.utc).isoformat()}"],
            sensitivity=sensitivity,
            retention_policy=retention_policy,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Core Data Object: PostureMetric ─────────────────────────────────
@dataclass
class PostureMetric:
    """A measured security state indicator."""
    metric_id: str
    category: str             # "detection", "response", "hardening", "evolution"
    name: str
    value: float
    baseline: float
    trend: str                # "improving", "stable", "degrading"
    owner: str                # Agent or system responsible
    timestamp: str = ""

    @classmethod
    def create(cls, *, category: str, name: str, value: float,
               baseline: float = 0.0, trend: str = "stable",
               owner: str = "SENTINEL") -> "PostureMetric":
        return cls(
            metric_id=f"MTR-{uuid.uuid4().hex[:12]}",
            category=category,
            name=name,
            value=value,
            baseline=baseline,
            trend=trend,
            owner=owner,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── Tamper-Evident Audit Ledger ─────────────────────────────────────
class AuditLedger:
    """Append-only, hash-chained audit log.

    Each entry includes a SHA-256 hash of the previous entry,
    creating a tamper-evident chain. If any entry is modified,
    the chain breaks and verification fails.
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._chain_hash = "GENESIS"
        self._entry_count = 0
        self._recent: deque = deque(maxlen=200)
        os.makedirs(DATA_DIR, exist_ok=True)
        self._restore_chain_hash()

    def _restore_chain_hash(self) -> None:
        """Restore the last chain hash from the ledger file."""
        try:
            if os.path.exists(AUDIT_LEDGER_FILE):
                last_line = ""
                with open(AUDIT_LEDGER_FILE, "r") as f:
                    for line in f:
                        last_line = line.strip()
                        self._entry_count += 1
                if last_line:
                    entry = json.loads(last_line)
                    self._chain_hash = entry.get("_hash", "GENESIS")
        except Exception:
            pass

    def _compute_hash(self, data: str, prev_hash: str) -> str:
        """SHA-256 hash linking this entry to the previous one."""
        return hashlib.sha256(f"{prev_hash}|{data}".encode()).hexdigest()[:24]

    def append(self, record_type: str, record: Dict[str, Any]) -> str:
        """Append a record to the tamper-evident ledger.

        Returns the entry hash.
        """
        with self._lock:
            entry = {
                "_seq": self._entry_count,
                "_type": record_type,
                "_ts": datetime.now(timezone.utc).isoformat(),
                "_prev": self._chain_hash,
                **record,
            }
            # Compute hash over the serialized entry (without hash field)
            data_str = json.dumps(entry, sort_keys=True, default=str)
            entry_hash = self._compute_hash(data_str, self._chain_hash)
            entry["_hash"] = entry_hash

            # Write to ledger file
            try:
                with open(AUDIT_LEDGER_FILE, "a") as f:
                    f.write(json.dumps(entry, default=str) + "\n")
            except Exception:
                pass

            self._chain_hash = entry_hash
            self._entry_count += 1
            self._recent.append(entry)
            return entry_hash

    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent audit entries."""
        with self._lock:
            return list(self._recent)[-limit:]

    def verify_chain(self, max_entries: int = 1000) -> Dict[str, Any]:
        """Verify the hash chain integrity of the ledger."""
        result = {"valid": True, "entries_checked": 0, "breaks": []}
        try:
            if not os.path.exists(AUDIT_LEDGER_FILE):
                return {**result, "entries_checked": 0}

            prev_hash = "GENESIS"
            with open(AUDIT_LEDGER_FILE, "r") as f:
                for i, line in enumerate(f):
                    if i >= max_entries:
                        break
                    entry = json.loads(line.strip())
                    stored_hash = entry.pop("_hash", "")

                    # Verify previous hash link
                    if entry.get("_prev") != prev_hash:
                        result["valid"] = False
                        result["breaks"].append({
                            "seq": entry.get("_seq"),
                            "type": "prev_hash_mismatch",
                        })

                    # Verify entry hash
                    data_str = json.dumps(entry, sort_keys=True, default=str)
                    computed = self._compute_hash(data_str, entry.get("_prev", ""))
                    if computed != stored_hash:
                        result["valid"] = False
                        result["breaks"].append({
                            "seq": entry.get("_seq"),
                            "type": "hash_mismatch",
                        })

                    prev_hash = stored_hash
                    result["entries_checked"] += 1

        except Exception as e:
            result["valid"] = False
            result["breaks"].append({"error": str(e)})

        return result

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_entries": self._entry_count,
            "chain_hash": self._chain_hash[:12] + "...",
            "ledger_file": AUDIT_LEDGER_FILE,
        }


# ── Telemetry Bus ───────────────────────────────────────────────────
class TelemetryBus:
    """Central bus for SENTINEL telemetry.

    All security events, findings, actions, and evidence flow through here.
    The bus handles:
      - Event normalization and recording
      - Audit ledger writes (tamper-evident)
      - Correlation key indexing
      - Posture metric aggregation
      - CMC atom creation (when available)
    """

    def __init__(self):
        self.ledger = AuditLedger()
        self._events: deque = deque(maxlen=500)
        self._findings: deque = deque(maxlen=100)
        self._actions: deque = deque(maxlen=200)
        self._lock = threading.Lock()
        self._stats = {
            "events_total": 0,
            "events_by_type": {},
            "events_by_zone": {},
            "findings_total": 0,
            "actions_total": 0,
            "actions_by_autonomy": {"auto": 0, "guarded": 0, "escalated": 0},
        }

    def record_event(self, event: SecurityEvent) -> str:
        """Record a security event. Returns the audit ledger hash."""
        with self._lock:
            self._events.append(event)
            self._stats["events_total"] += 1
            et = event.event_type
            self._stats["events_by_type"][et] = self._stats["events_by_type"].get(et, 0) + 1
            sz = event.source_zone
            self._stats["events_by_zone"][sz] = self._stats["events_by_zone"].get(sz, 0) + 1

        return self.ledger.append("event", event.to_dict())

    def record_finding(self, finding: SecurityFinding) -> str:
        """Record a security finding."""
        with self._lock:
            self._findings.append(finding)
            self._stats["findings_total"] += 1
        return self.ledger.append("finding", finding.to_dict())

    def record_action(self, action: ResponseAction) -> str:
        """Record a response action with provenance."""
        with self._lock:
            self._actions.append(action)
            self._stats["actions_total"] += 1
            al = action.autonomy_level
            if al in self._stats["actions_by_autonomy"]:
                self._stats["actions_by_autonomy"][al] += 1
        return self.ledger.append("action", action.to_dict())

    def record_evidence(self, evidence: EvidencePackage) -> str:
        """Record an evidence package."""
        return self.ledger.append("evidence", evidence.to_dict())

    def get_recent_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            return [e.to_dict() for e in list(self._events)[-limit:]]

    def get_recent_findings(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            return [f.to_dict() for f in list(self._findings)[-limit:]]

    def get_recent_actions(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self._lock:
            return [a.to_dict() for a in list(self._actions)[-limit:]]

    def get_telemetry_status(self) -> Dict[str, Any]:
        """Full telemetry status for JOC."""
        with self._lock:
            stats = dict(self._stats)
        chain_verify = self.ledger.verify_chain(max_entries=100)
        return {
            **stats,
            "audit_ledger": self.ledger.get_stats(),
            "chain_integrity": chain_verify,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    # ── MCP Tool Call Audit (enhanced) ──────────────────────────────

    def audit_mcp_call(self, *, tool_name: str, arguments: Dict[str, Any],
                       caller_ip: str = "127.0.0.1", caller_agent: str = "",
                       session_id: str = "", duration_ms: float = 0,
                       result_status: str = "success",
                       correlation_id: str = "") -> SecurityEvent:
        """Create a full-provenance MCP tool call audit event."""

        # Determine trust zones
        if caller_ip in ("127.0.0.1", "::1", "localhost"):
            source_zone = TrustZone.RUNTIME
        elif caller_agent:
            source_zone = TrustZone.CONTROL_PLANE
        else:
            source_zone = TrustZone.EXTERNAL

        # Determine severity based on tool sensitivity
        sensitive_tools = {
            "run_command", "send_command_input", "write_to_file",
            "replace_file_content", "multi_replace_file_content",
        }
        severity = "high" if tool_name in sensitive_tools else "info"
        if source_zone == TrustZone.EXTERNAL and tool_name in sensitive_tools:
            severity = "critical"

        event = SecurityEvent.create(
            source_zone=source_zone,
            target_zone=TrustZone.CONTROL_PLANE,
            actor_identity=caller_agent or caller_ip,
            actor_type="agent" if caller_agent else "ip",
            event_type="mcp_tool_call",
            severity=severity,
            confidence=0.95,
            session_id=session_id,
            correlation_keys=[correlation_id] if correlation_id else [],
            details={
                "tool": tool_name,
                "args_size": len(json.dumps(arguments, default=str)),
                "caller_ip": caller_ip,
                "caller_agent": caller_agent,
                "duration_ms": duration_ms,
                "result": result_status,
            },
            mitre_technique="T1059" if tool_name == "run_command" else "",
        )

        self.record_event(event)
        return event

    # ── Request Audit ───────────────────────────────────────────────

    def audit_request(self, *, ip: str, path: str, method: str,
                      status_code: int = 200, blocked: bool = False,
                      attack_category: str = "", session_id: str = "",
                      user_agent: str = "") -> SecurityEvent:
        """Create a request audit event with trust zone annotation."""

        if ip in ("127.0.0.1", "::1", "localhost") or ip.startswith(("192.168.", "10.")):
            source_zone = TrustZone.RUNTIME
        else:
            source_zone = TrustZone.EXTERNAL

        # Determine target zone based on path
        if path.startswith("/mcp/"):
            target_zone = TrustZone.CONTROL_PLANE
        elif path.startswith("/security/") or path.startswith("/sentinel/"):
            target_zone = TrustZone.EVIDENCE
        else:
            target_zone = TrustZone.RUNTIME

        severity = "info"
        event_type = "http_request"
        if blocked:
            severity = "medium"
            event_type = "request_blocked"
        if attack_category:
            severity = "high" if attack_category in ("xss", "path_traversal") else "critical"
            event_type = f"attack_{attack_category}"

        event = SecurityEvent.create(
            source_zone=source_zone,
            target_zone=target_zone,
            actor_identity=ip,
            actor_type="ip",
            event_type=event_type,
            severity=severity,
            confidence=0.85 if attack_category else 0.95,
            session_id=session_id,
            details={
                "method": method,
                "path": path,
                "status_code": status_code,
                "user_agent": user_agent[:120] if user_agent else "",
                "blocked": blocked,
                "attack_category": attack_category,
            },
        )

        self.record_event(event)
        return event

    # ── Response Action with Provenance ─────────────────────────────

    def record_auto_response(self, *, action_type: str, trigger_event_id: str = "",
                             actor: str = "SENTINEL", details: Optional[Dict[str, Any]] = None,
                             rollback_available: bool = True) -> ResponseAction:
        """Record an auto-autonomy response action with full provenance."""
        action = ResponseAction.create(
            trigger_finding_id=trigger_event_id,
            action_type=action_type,
            autonomy_level=AutonomyLevel.AUTO,
            actor=actor,
            result="success",
            rollback_available=rollback_available,
            evidence_refs=[trigger_event_id],
            details=details,
        )
        self.record_action(action)
        return action


# ── Module-level singleton ──────────────────────────────────────────
_telemetry_bus: Optional[TelemetryBus] = None


def get_telemetry_bus() -> TelemetryBus:
    """Get or create the global TelemetryBus singleton."""
    global _telemetry_bus
    if _telemetry_bus is None:
        _telemetry_bus = TelemetryBus()
    return _telemetry_bus
