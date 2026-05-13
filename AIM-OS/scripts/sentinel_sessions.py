#!/usr/bin/env python3
"""
AIM-OS SENTINEL — Agent Session Registry (Phase 5)

Cryptographic identity binding for agent sessions.
Every agent gets an HMAC-SHA256 signed session token tied to its
genome hash, enabling full provenance on all telemetry events.

Usage:
    from sentinel_sessions import SessionRegistry
    registry = SessionRegistry()
    token = registry.register("Opus", genome_hash="abc123...")
    info = registry.validate(token)
"""

import hashlib
import hmac
import json
import os
import secrets
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

REPO_ROOT = str(Path(__file__).parent.parent)
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
SESSIONS_FILE = os.path.join(DATA_DIR, "sentinel_sessions.json")
SESSION_SECRET_FILE = os.path.join(DATA_DIR, "sentinel_session_secret.key")

# Import telemetry (soft dependency)
try:
    from sentinel_telemetry import (
        SecurityEvent, TrustZone,
    )
    _HAS_TELEMETRY = True
except ImportError:
    _HAS_TELEMETRY = False


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Agent Session ───────────────────────────────────────────────────
class AgentSession:
    """Represents a single authenticated agent session."""

    def __init__(self, agent_name: str, session_id: str, token: str,
                 genome_hash: str = "", capabilities: Optional[List[str]] = None):
        self.agent_name = agent_name
        self.session_id = session_id
        self.token = token
        self.genome_hash = genome_hash
        self.capabilities = capabilities or []
        self.created_at = _utc_iso()
        self.last_seen = self.created_at
        self.request_count = 0
        self.is_active = True
        self.ttl_hours = 24

    def touch(self) -> None:
        """Update last-seen timestamp and increment request count."""
        self.last_seen = _utc_iso()
        self.request_count += 1

    def is_expired(self) -> bool:
        """Check if session has expired."""
        try:
            created = datetime.fromisoformat(self.created_at)
            age_hours = (datetime.now(timezone.utc) - created).total_seconds() / 3600
            return age_hours > self.ttl_hours
        except (ValueError, TypeError):
            return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "agent_name": self.agent_name,
            "session_id": self.session_id,
            "genome_hash": self.genome_hash[:16] + "..." if len(self.genome_hash) > 16 else self.genome_hash,
            "capabilities": self.capabilities,
            "created_at": self.created_at,
            "last_seen": self.last_seen,
            "request_count": self.request_count,
            "is_active": self.is_active,
            "expired": self.is_expired(),
        }


# ── Session Registry ────────────────────────────────────────────────
class SessionRegistry:
    """Issues, validates, and revokes HMAC-signed agent session tokens.

    Security properties:
    - Tokens are HMAC-SHA256 signed with a persistent server secret
    - Each token encodes: agent_name + session_id + genome_hash + timestamp
    - Tokens expire after 24 hours
    - Invalid/expired tokens trigger SecurityEvents
    """

    def __init__(self, telemetry: Optional[Any] = None):
        self.telemetry = telemetry
        self._sessions: Dict[str, AgentSession] = {}  # token -> session
        self._by_agent: Dict[str, str] = {}  # agent_name -> token (latest)
        self._lock = threading.Lock()
        self._secret = self._load_or_create_secret()
        self._revoked_tokens: set = set()
        self._load_sessions()

    def _load_or_create_secret(self) -> bytes:
        """Load or generate the HMAC signing secret."""
        try:
            if os.path.exists(SESSION_SECRET_FILE):
                with open(SESSION_SECRET_FILE, "rb") as f:
                    secret = f.read()
                    if len(secret) >= 32:
                        return secret
        except OSError:
            pass

        # Generate new 256-bit secret
        secret = secrets.token_bytes(32)
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(SESSION_SECRET_FILE, "wb") as f:
                f.write(secret)
        except OSError:
            pass
        return secret

    def _compute_hmac(self, agent_name: str, session_id: str,
                      genome_hash: str, timestamp: str) -> str:
        """Compute HMAC-SHA256 over session data."""
        message = f"{agent_name}:{session_id}:{genome_hash}:{timestamp}"
        return hmac.new(self._secret, message.encode(), hashlib.sha256).hexdigest()

    def _load_sessions(self) -> None:
        """Load persisted sessions from disk."""
        try:
            if os.path.exists(SESSIONS_FILE):
                with open(SESSIONS_FILE) as f:
                    data = json.load(f)
                    for entry in data.get("sessions", []):
                        session = AgentSession(
                            agent_name=entry["agent_name"],
                            session_id=entry["session_id"],
                            token=entry.get("token", ""),
                            genome_hash=entry.get("genome_hash", ""),
                        )
                        session.created_at = entry.get("created_at", session.created_at)
                        session.last_seen = entry.get("last_seen", session.last_seen)
                        session.request_count = entry.get("request_count", 0)
                        session.is_active = entry.get("is_active", True)
                        if not session.is_expired() and session.is_active:
                            self._sessions[session.token] = session
                            self._by_agent[session.agent_name] = session.token
        except (json.JSONDecodeError, OSError, KeyError):
            pass

    def _save_sessions(self) -> None:
        """Persist active sessions to disk."""
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            sessions_list = [s.to_dict() for s in self._sessions.values() if s.is_active]
            with open(SESSIONS_FILE, "w") as f:
                json.dump({
                    "sessions": sessions_list,
                    "total": len(sessions_list),
                    "updated": _utc_iso(),
                }, f, indent=2)
        except OSError:
            pass

    def register(self, agent_name: str, genome_hash: str = "",
                 capabilities: Optional[List[str]] = None) -> Dict[str, Any]:
        """Register an agent and issue a session token.

        Returns dict with session_id, token, and expiry info.
        """
        session_id = secrets.token_hex(16)
        timestamp = _utc_iso()
        token_sig = self._compute_hmac(agent_name, session_id, genome_hash, timestamp)
        # Token format: session_id.signature (verifiable)
        token = f"sentinel_{session_id}.{token_sig[:32]}"

        session = AgentSession(
            agent_name=agent_name,
            session_id=session_id,
            token=token,
            genome_hash=genome_hash,
            capabilities=capabilities,
        )

        with self._lock:
            # Revoke previous session for this agent
            if agent_name in self._by_agent:
                old_token = self._by_agent[agent_name]
                if old_token in self._sessions:
                    self._sessions[old_token].is_active = False
                    self._revoked_tokens.add(old_token)

            self._sessions[token] = session
            self._by_agent[agent_name] = token

        self._save_sessions()

        # Emit registration event
        if self.telemetry and _HAS_TELEMETRY:
            event = SecurityEvent.create(
                source_zone=TrustZone.CONTROL_PLANE,
                target_zone=TrustZone.CONTROL_PLANE,
                actor_identity=agent_name,
                actor_type="agent",
                event_type="session_registered",
                severity="info",
                confidence=1.0,
                session_id=session_id,
                details={
                    "genome_hash": genome_hash[:16] if genome_hash else "none",
                    "capabilities": capabilities or [],
                },
            )
            self.telemetry.record_event(event)

        return {
            "session_id": session_id,
            "token": token,
            "agent_name": agent_name,
            "created_at": timestamp,
            "expires_in_hours": 24,
            "status": "active",
        }

    def validate(self, token: str) -> Dict[str, Any]:
        """Validate a session token. Returns session info or error."""
        with self._lock:
            if token in self._revoked_tokens:
                self._emit_invalid_token_event(token, "revoked")
                return {"valid": False, "reason": "token_revoked"}

            session = self._sessions.get(token)
            if not session:
                self._emit_invalid_token_event(token, "unknown")
                return {"valid": False, "reason": "token_unknown"}

            if not session.is_active:
                self._emit_invalid_token_event(token, "inactive")
                return {"valid": False, "reason": "session_inactive"}

            if session.is_expired():
                session.is_active = False
                self._emit_invalid_token_event(token, "expired")
                return {"valid": False, "reason": "session_expired", "agent": session.agent_name}

            session.touch()

        return {
            "valid": True,
            "agent_name": session.agent_name,
            "session_id": session.session_id,
            "genome_hash": session.genome_hash[:16] + "..." if len(session.genome_hash) > 16 else session.genome_hash,
            "request_count": session.request_count,
            "created_at": session.created_at,
        }

    def revoke(self, agent_name: str) -> Dict[str, Any]:
        """Revoke an agent's current session."""
        with self._lock:
            token = self._by_agent.get(agent_name)
            if token and token in self._sessions:
                self._sessions[token].is_active = False
                self._revoked_tokens.add(token)
                del self._by_agent[agent_name]
                self._save_sessions()
                return {"revoked": True, "agent": agent_name}
        return {"revoked": False, "reason": "no_active_session"}

    def resolve_identity(self, token: str) -> Optional[str]:
        """Quick lookup: token → agent_name (or None)."""
        with self._lock:
            session = self._sessions.get(token)
            if session and session.is_active and not session.is_expired():
                session.touch()
                return session.agent_name
        return None

    def _emit_invalid_token_event(self, token: str, reason: str) -> None:
        """Emit a high-severity event for invalid token usage."""
        if self.telemetry and _HAS_TELEMETRY:
            event = SecurityEvent.create(
                source_zone=TrustZone.INGRESS,
                target_zone=TrustZone.CONTROL_PLANE,
                actor_identity=f"UNKNOWN(token={token[:20]}...)",
                actor_type="unknown",
                event_type="invalid_session_token",
                severity="high",
                confidence=0.95,
                details={"reason": reason, "token_prefix": token[:20]},
            )
            self.telemetry.record_event(event)

    def get_status(self) -> Dict[str, Any]:
        """Status summary for JOC."""
        with self._lock:
            active = [s for s in self._sessions.values() if s.is_active and not s.is_expired()]
            return {
                "active_sessions": len(active),
                "total_registered": len(self._sessions),
                "revoked": len(self._revoked_tokens),
                "agents": [s.agent_name for s in active],
                "last_registration": active[-1].created_at if active else "never",
            }

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all session details for API."""
        with self._lock:
            return [s.to_dict() for s in self._sessions.values()]
