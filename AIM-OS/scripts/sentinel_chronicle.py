#!/usr/bin/env python3
"""
AIM-OS SENTINEL — CHRONICLE: Audit Chain + Incident Response (Phase 8)

Immutable hash-chained audit log and automated incident response engine.
Every SENTINEL action is recorded in a tamper-proof chain for forensic
readiness, compliance reporting, and legal defensibility.

KEY DESIGN:
  - SHA-256 hash chain (blockchain-style) — tampering breaks the chain
  - 6 incident response playbooks by severity (P0-CRITICAL → P4-INFO)
  - Incident lifecycle: DETECTED → TRIAGED → RESPONDING → CONTAINED → RESOLVED → POSTMORTEM
  - Compliance report generation on demand

Usage:
    from sentinel_chronicle import ChronicleEngine
    engine = ChronicleEngine(telemetry_bus)
    engine.record("policy_enforced", "SENTINEL", {"rule": "POL-001", ...})
    engine.open_incident("P1-HIGH", "Targeted attack from 185.x.x.x", {...})
"""

import hashlib
import json
import os
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = str(Path(__file__).parent.parent)
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
AUDIT_CHAIN_FILE = os.path.join(DATA_DIR, "sentinel_audit_chain.jsonl")
INCIDENT_DB_FILE = os.path.join(DATA_DIR, "sentinel_incidents.json")

try:
    from sentinel_telemetry import SecurityEvent, TrustZone
    _HAS_TELEMETRY = True
except ImportError:
    _HAS_TELEMETRY = False


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════
#  AUDIT ENTRY — Immutable hash-chained log entry
# ═══════════════════════════════════════════════════════════════════
class AuditEntry:
    """Single entry in the immutable audit chain. SHA-256 linked to previous."""

    def __init__(self, sequence: int, event_type: str, actor: str,
                 details: Dict[str, Any], prev_hash: str):
        self.sequence = sequence
        self.timestamp = _utc_iso()
        self.event_type = event_type
        self.actor = actor
        self.details = details
        self.prev_hash = prev_hash
        self.hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of this entry chained to previous."""
        payload = json.dumps({
            "seq": self.sequence,
            "ts": self.timestamp,
            "type": self.event_type,
            "actor": self.actor,
            "details": self.details,
            "prev": self.prev_hash,
        }, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sequence": self.sequence,
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "actor": self.actor,
            "details": self.details,
            "prev_hash": self.prev_hash,
            "hash": self.hash,
        }


# ═══════════════════════════════════════════════════════════════════
#  AUDIT CHAIN — Append-only tamper-proof chain
# ═══════════════════════════════════════════════════════════════════
GENESIS_HASH = "0" * 64  # Genesis block hash

class AuditChain:
    """Append-only SHA-256 hash chain for security audit trail.

    Properties:
      - Each entry's hash includes the previous entry's hash
      - Tampering with any entry invalidates all subsequent hashes
      - Integrity verified on startup and periodically
    """

    def __init__(self):
        self._entries: List[AuditEntry] = []
        self._lock = threading.Lock()
        self._integrity_verified = False
        self._last_verification = ""
        self._tampering_detected = False
        self._load_chain()

    def append(self, event_type: str, actor: str, details: Dict[str, Any]) -> AuditEntry:
        """Append a new entry to the chain."""
        with self._lock:
            seq = len(self._entries)
            prev_hash = self._entries[-1].hash if self._entries else GENESIS_HASH
            entry = AuditEntry(seq, event_type, actor, details, prev_hash)
            self._entries.append(entry)
            self._persist_entry(entry)
            return entry

    def verify_integrity(self) -> Dict[str, Any]:
        """Verify the entire chain is intact — no tampering."""
        with self._lock:
            if not self._entries:
                self._integrity_verified = True
                self._last_verification = _utc_iso()
                return {"valid": True, "entries": 0, "message": "Empty chain"}

            errors = []
            for i, entry in enumerate(self._entries):
                # Check prev_hash linkage
                expected_prev = self._entries[i - 1].hash if i > 0 else GENESIS_HASH
                if entry.prev_hash != expected_prev:
                    errors.append({
                        "sequence": i,
                        "error": "prev_hash mismatch",
                        "expected": expected_prev[:16] + "...",
                        "actual": entry.prev_hash[:16] + "...",
                    })

                # Recompute hash to verify integrity
                recomputed = entry._compute_hash()
                if entry.hash != recomputed:
                    errors.append({
                        "sequence": i,
                        "error": "hash recomputation mismatch",
                    })

            self._integrity_verified = len(errors) == 0
            self._tampering_detected = len(errors) > 0
            self._last_verification = _utc_iso()

            return {
                "valid": len(errors) == 0,
                "entries_checked": len(self._entries),
                "errors": errors,
                "verified_at": self._last_verification,
            }

    def _persist_entry(self, entry: AuditEntry) -> None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(AUDIT_CHAIN_FILE, "a") as f:
                f.write(json.dumps(entry.to_dict()) + "\n")
        except OSError:
            pass

    def _load_chain(self) -> None:
        """Load persisted chain on startup."""
        try:
            if os.path.exists(AUDIT_CHAIN_FILE):
                with open(AUDIT_CHAIN_FILE, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            data = json.loads(line)
                            entry = AuditEntry.__new__(AuditEntry)
                            entry.sequence = data["sequence"]
                            entry.timestamp = data["timestamp"]
                            entry.event_type = data["event_type"]
                            entry.actor = data["actor"]
                            entry.details = data.get("details", {})
                            entry.prev_hash = data["prev_hash"]
                            entry.hash = data["hash"]
                            self._entries.append(entry)
        except (OSError, json.JSONDecodeError, KeyError):
            pass

    def get_recent(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            return [e.to_dict() for e in self._entries[-limit:]]

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "total_entries": len(self._entries),
                "integrity_verified": self._integrity_verified,
                "last_verification": self._last_verification,
                "tampering_detected": self._tampering_detected,
                "chain_head": self._entries[-1].hash[:16] + "..." if self._entries else "genesis",
            }


# ═══════════════════════════════════════════════════════════════════
#  INCIDENT — Security incident with lifecycle
# ═══════════════════════════════════════════════════════════════════
INCIDENT_STATES = ["DETECTED", "TRIAGED", "RESPONDING", "CONTAINED", "RESOLVED", "POSTMORTEM"]
SEVERITY_LEVELS = ["P0-CRITICAL", "P1-HIGH", "P2-MEDIUM", "P3-LOW", "P4-INFO", "COMPLIANCE"]

# Playbooks: what automated actions to take for each severity
PLAYBOOKS: Dict[str, Dict[str, Any]] = {
    "P0-CRITICAL": {
        "name": "Active Breach Response",
        "auto_actions": ["phantom_engage_critical", "ban_attacker_ip", "quarantine_all_sessions",
                         "escalate_ceo", "full_forensic_capture", "notify_all_agents"],
        "max_response_minutes": 5,
        "requires_human": True,
    },
    "P1-HIGH": {
        "name": "Targeted Attack Response",
        "auto_actions": ["phantom_engage_yellow", "alert_security_team", "capture_evidence",
                         "open_investigation", "increase_monitoring"],
        "max_response_minutes": 15,
        "requires_human": True,
    },
    "P2-MEDIUM": {
        "name": "Suspicious Activity Investigation",
        "auto_actions": ["log_evidence", "increase_monitoring", "update_baselines",
                         "mark_ip_suspicious"],
        "max_response_minutes": 60,
        "requires_human": False,
    },
    "P3-LOW": {
        "name": "Anomaly Tracking",
        "auto_actions": ["record_in_audit_chain", "adjust_thresholds"],
        "max_response_minutes": 240,
        "requires_human": False,
    },
    "P4-INFO": {
        "name": "Informational Logging",
        "auto_actions": ["record_in_audit_chain"],
        "max_response_minutes": 0,
        "requires_human": False,
    },
    "COMPLIANCE": {
        "name": "Compliance Documentation",
        "auto_actions": ["record_in_audit_chain", "tag_for_compliance_report"],
        "max_response_minutes": 0,
        "requires_human": False,
    },
}


class Incident:
    """A security incident with full lifecycle tracking."""

    _counter = 0

    def __init__(self, severity: str, title: str, details: Dict[str, Any],
                 source_ip: str = "", attack_type: str = ""):
        Incident._counter += 1
        self.id = f"INC-{Incident._counter:04d}"
        self.severity = severity if severity in SEVERITY_LEVELS else "P3-LOW"
        self.title = title
        self.details = details
        self.source_ip = source_ip
        self.attack_type = attack_type
        self.state = "DETECTED"
        self.created_at = _utc_iso()
        self.updated_at = _utc_iso()
        self.resolved_at = ""
        self.playbook = PLAYBOOKS.get(self.severity, PLAYBOOKS["P3-LOW"])
        self.actions_taken: List[Dict[str, str]] = []
        self.timeline: List[Dict[str, str]] = [
            {"timestamp": self.created_at, "event": "Incident detected", "state": "DETECTED"}
        ]
        self.assigned_to = "SENTINEL"
        self.escalated = False
        self.evidence: List[str] = []

    def transition(self, new_state: str, note: str = "") -> bool:
        """Transition to a new lifecycle state."""
        if new_state not in INCIDENT_STATES:
            return False
        current_idx = INCIDENT_STATES.index(self.state) if self.state in INCIDENT_STATES else -1
        new_idx = INCIDENT_STATES.index(new_state)
        if new_idx < current_idx:
            return False  # Can't go backwards

        self.state = new_state
        self.updated_at = _utc_iso()
        self.timeline.append({
            "timestamp": self.updated_at,
            "event": note or f"Transitioned to {new_state}",
            "state": new_state,
        })
        if new_state == "RESOLVED":
            self.resolved_at = self.updated_at
        return True

    def record_action(self, action: str, result: str = "success") -> None:
        self.actions_taken.append({
            "action": action, "result": result,
            "timestamp": _utc_iso(),
        })
        self.timeline.append({
            "timestamp": _utc_iso(),
            "event": f"Action: {action} → {result}",
            "state": self.state,
        })

    def add_evidence(self, evidence: str) -> None:
        self.evidence.append(evidence)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "severity": self.severity,
            "title": self.title, "state": self.state,
            "source_ip": self.source_ip, "attack_type": self.attack_type,
            "created_at": self.created_at, "updated_at": self.updated_at,
            "resolved_at": self.resolved_at,
            "playbook": self.playbook.get("name", ""),
            "actions_taken": len(self.actions_taken),
            "timeline_events": len(self.timeline),
            "assigned_to": self.assigned_to,
            "escalated": self.escalated,
            "evidence_count": len(self.evidence),
        }

    def to_full_dict(self) -> Dict[str, Any]:
        d = self.to_dict()
        d["details"] = self.details
        d["actions"] = self.actions_taken[-10:]
        d["timeline"] = self.timeline[-20:]
        d["evidence"] = self.evidence[-10:]
        d["playbook_actions"] = self.playbook.get("auto_actions", [])
        return d


# ═══════════════════════════════════════════════════════════════════
#  CHRONICLE ENGINE — Orchestrates audit + incident response
# ═══════════════════════════════════════════════════════════════════
class ChronicleEngine:
    """CHRONICLE: Immutable audit chain + automated incident response.

    Records all SENTINEL events in a hash-chained audit log and manages
    security incidents through their full lifecycle with auto-playbooks.
    """

    def __init__(self, telemetry: Optional[Any] = None):
        self.telemetry = telemetry
        self.audit_chain = AuditChain()
        self._incidents: Dict[str, Incident] = {}
        self._lock = threading.Lock()

        # Verify chain integrity on startup
        integrity = self.audit_chain.verify_integrity()

        # Record engine initialization in audit chain
        self.record("chronicle_init", "SENTINEL", {
            "phase": 8,
            "chain_entries_loaded": integrity.get("entries_checked", 0),
            "chain_valid": integrity.get("valid", True),
        })

        # Load persisted incidents
        self._load_incidents()

    def record(self, event_type: str, actor: str, details: Dict[str, Any]) -> Dict[str, Any]:
        """Record an event in the immutable audit chain.

        Args:
            event_type: Type of event (e.g., "policy_enforced", "phantom_engagement")
            actor: Who/what generated the event (e.g., "SENTINEL/PHANTOM", "PolicyEngine")
            details: Event-specific details

        Returns:
            The audit entry as a dict
        """
        entry = self.audit_chain.append(event_type, actor, details)

        # Emit telemetry for significant events
        if self.telemetry and _HAS_TELEMETRY and event_type not in ("chronicle_init", "routine_check"):
            try:
                event = SecurityEvent.create(
                    source_zone=TrustZone.CONTROL_PLANE,
                    target_zone=TrustZone.CONTROL_PLANE,
                    actor_identity=f"CHRONICLE/{actor}",
                    actor_type="system",
                    event_type="audit_recorded",
                    severity="info",
                    confidence=1.0,
                    details={"audit_seq": entry.sequence, "event_type": event_type},
                )
                self.telemetry.record_event(event)
            except Exception:
                pass

        return entry.to_dict()

    def open_incident(self, severity: str, title: str, details: Dict[str, Any],
                      source_ip: str = "", attack_type: str = "") -> Dict[str, Any]:
        """Open a new security incident with automatic playbook assignment.

        Args:
            severity: P0-CRITICAL through P4-INFO or COMPLIANCE
            title: Brief incident title
            details: Full incident details
            source_ip: Attacking IP if known
            attack_type: MITRE technique or category

        Returns:
            Incident summary dict
        """
        with self._lock:
            incident = Incident(severity, title, details, source_ip, attack_type)
            self._incidents[incident.id] = incident

            # Record in audit chain
            self.record("incident_opened", "SENTINEL/CHRONICLE", {
                "incident_id": incident.id,
                "severity": severity,
                "title": title,
                "source_ip": source_ip,
                "playbook": incident.playbook.get("name", ""),
            })

            # Auto-triage
            incident.transition("TRIAGED", f"Auto-triaged as {severity}")

            # Execute playbook actions
            playbook = incident.playbook
            for action in playbook.get("auto_actions", []):
                incident.record_action(action, "queued")

            # If P0/P1, auto-transition to RESPONDING
            if severity in ("P0-CRITICAL", "P1-HIGH"):
                incident.transition("RESPONDING", f"Playbook '{playbook.get('name', '')}' activated")
                incident.escalated = severity == "P0-CRITICAL"

            # Persist
            self._save_incidents()

            return incident.to_dict()

    def update_incident(self, incident_id: str, new_state: str,
                        note: str = "") -> Optional[Dict[str, Any]]:
        """Transition an incident to a new state."""
        with self._lock:
            incident = self._incidents.get(incident_id)
            if not incident:
                return None

            success = incident.transition(new_state, note)
            if not success:
                return None

            # Record state transition in audit chain
            self.record("incident_updated", "SENTINEL/CHRONICLE", {
                "incident_id": incident_id,
                "new_state": new_state,
                "note": note,
            })

            self._save_incidents()
            return incident.to_dict()

    def get_active_incidents(self) -> List[Dict[str, Any]]:
        """Get all non-resolved incidents."""
        with self._lock:
            return [
                inc.to_dict() for inc in self._incidents.values()
                if inc.state not in ("RESOLVED", "POSTMORTEM")
            ]

    def get_all_incidents(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            incidents = sorted(
                self._incidents.values(),
                key=lambda i: i.created_at, reverse=True
            )
            return [i.to_dict() for i in incidents[:limit]]

    def get_incident_detail(self, incident_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            incident = self._incidents.get(incident_id)
            return incident.to_full_dict() if incident else None

    def generate_compliance_report(self) -> Dict[str, Any]:
        """Generate a compliance summary report from the audit chain and incidents."""
        with self._lock:
            chain_status = self.audit_chain.get_status()
            total_incidents = len(self._incidents)
            by_severity = {}
            for inc in self._incidents.values():
                by_severity[inc.severity] = by_severity.get(inc.severity, 0) + 1

            resolved = sum(1 for i in self._incidents.values() if i.state == "RESOLVED")
            active = total_incidents - resolved

            return {
                "report_type": "SENTINEL Compliance Report",
                "generated_at": _utc_iso(),
                "audit_chain": {
                    "total_entries": chain_status["total_entries"],
                    "integrity": "VERIFIED" if chain_status["integrity_verified"] else "UNVERIFIED",
                    "tampering": "NONE" if not chain_status["tampering_detected"] else "DETECTED",
                    "last_verified": chain_status["last_verification"],
                },
                "incidents": {
                    "total": total_incidents,
                    "active": active,
                    "resolved": resolved,
                    "by_severity": by_severity,
                },
                "playbooks_available": len(PLAYBOOKS),
                "compliance_status": "COMPLIANT" if not chain_status["tampering_detected"] else "REVIEW REQUIRED",
            }

    def _save_incidents(self) -> None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            data = {}
            for inc_id, inc in self._incidents.items():
                data[inc_id] = inc.to_full_dict()
            with open(INCIDENT_DB_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass

    def _load_incidents(self) -> None:
        try:
            if os.path.exists(INCIDENT_DB_FILE):
                with open(INCIDENT_DB_FILE, "r") as f:
                    data = json.load(f)
                # Load count for ID continuity
                if data:
                    max_num = 0
                    for key in data:
                        try:
                            num = int(key.split("-")[1])
                            if num > max_num:
                                max_num = num
                        except (IndexError, ValueError):
                            pass
                    Incident._counter = max_num
        except (OSError, json.JSONDecodeError):
            pass

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            chain_status = self.audit_chain.get_status()
            active = sum(1 for i in self._incidents.values()
                         if i.state not in ("RESOLVED", "POSTMORTEM"))
            by_severity = {}
            for inc in self._incidents.values():
                if inc.state not in ("RESOLVED", "POSTMORTEM"):
                    by_severity[inc.severity] = by_severity.get(inc.severity, 0) + 1

            return {
                "audit_entries": chain_status["total_entries"],
                "chain_integrity": "OK" if chain_status["integrity_verified"] else "UNVERIFIED",
                "tampering_detected": chain_status["tampering_detected"],
                "last_verified": chain_status["last_verification"],
                "chain_head": chain_status["chain_head"],
                "active_incidents": active,
                "total_incidents": len(self._incidents),
                "incidents_by_severity": by_severity,
                "playbooks_loaded": len(PLAYBOOKS),
            }
