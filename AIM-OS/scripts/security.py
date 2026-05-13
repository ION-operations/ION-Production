#!/usr/bin/env python3
"""
AIM-OS Security Module — Shared Authentication, Rate Limiting & Request Logging

Used by both the SSE MCP server and the HTTP fallback server to protect
publicly exposed endpoints behind the Cloudflare tunnel.

Security layers:
1. Bearer Token Authentication — validates API keys
2. Rate Limiting — per-IP request throttle (sliding window)
3. Request Logging — logs every request with IP, path, status, timing
4. CORS Lockdown — restricts origins to known frontends + ChatGPT

Usage:
    from security import SecurityGate
    gate = SecurityGate()

    # Check a request:
    result = gate.check(ip="1.2.3.4", path="/sse", token="Bearer abc-123")
    if not result["allowed"]:
        return 403, result["reason"]
"""

import hashlib
import json
import os
import secrets
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from typing import Any, Dict, List, Optional

REPO_ROOT = str(Path(__file__).parent.parent)
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
KEYS_FILE = os.path.join(DATA_DIR, "api_keys.json")
LOG_FILE = os.path.join(DATA_DIR, "security_log.json")

# ── Defaults ────────────────────────────────────────────────────────
DEFAULT_RATE_LIMIT = 60          # requests per window
DEFAULT_RATE_WINDOW = 60         # seconds
MAX_LOG_ENTRIES = 500            # keep in memory
LOG_FLUSH_INTERVAL = 30          # seconds between disk flushes

# Paths that are always open (no auth needed)
PUBLIC_PATHS = frozenset({
    "/health",
    "/sse",         # SSE handshake is open — ChatGPT MCP needs this
    "/messages/",   # MCP message endpoint (SSE protocol)
})

# Paths that require auth
PROTECTED_PATHS_PREFIX = (
    "/mcp/",
    "/processes",
    "/connections",
    "/security/",
)


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash_key(key: str) -> str:
    """SHA-256 hash of an API key for storage (never store raw keys)."""
    return hashlib.sha256(key.encode()).hexdigest()


class RateLimiter:
    """Sliding window rate limiter per IP address."""

    def __init__(self, max_requests: int = DEFAULT_RATE_LIMIT, window_seconds: int = DEFAULT_RATE_WINDOW):
        self.max_requests = max_requests
        self.window = window_seconds
        self._buckets: Dict[str, deque] = {}
        self._lock = Lock()

    def check(self, ip: str) -> bool:
        """Returns True if the request is allowed, False if rate-limited."""
        now = time.time()
        with self._lock:
            if ip not in self._buckets:
                self._buckets[ip] = deque()
            bucket = self._buckets[ip]
            # Purge expired entries
            while bucket and bucket[0] < now - self.window:
                bucket.popleft()
            if len(bucket) >= self.max_requests:
                return False
            bucket.append(now)
            return True

    def get_stats(self) -> Dict[str, int]:
        """Return current request counts per IP."""
        now = time.time()
        with self._lock:
            stats = {}
            for ip, bucket in self._buckets.items():
                # Count only active entries
                count = sum(1 for t in bucket if t >= now - self.window)
                if count > 0:
                    stats[ip] = count
            return stats


class RequestLogger:
    """In-memory request log with periodic disk flush."""

    def __init__(self, max_entries: int = MAX_LOG_ENTRIES):
        self.max_entries = max_entries
        self._log: deque = deque(maxlen=max_entries)
        self._lock = Lock()
        self._last_flush = time.time()
        self._blocked_count = 0
        self._total_count = 0

    def log(self, entry: Dict[str, Any]) -> None:
        with self._lock:
            self._total_count += 1
            if entry.get("blocked"):
                self._blocked_count += 1
            self._log.append(entry)
            # Periodic disk flush
            if time.time() - self._last_flush > LOG_FLUSH_INTERVAL:
                self._flush_to_disk()

    def get_recent(self, limit: int = 50) -> List[Dict[str, Any]]:
        with self._lock:
            entries = list(self._log)
            return entries[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            blocked_ips = {}
            recent_ips = {}
            for entry in self._log:
                ip = entry.get("ip", "unknown")
                if entry.get("blocked"):
                    blocked_ips[ip] = blocked_ips.get(ip, 0) + 1
                recent_ips[ip] = recent_ips.get(ip, 0) + 1
            return {
                "total_requests": self._total_count,
                "blocked_requests": self._blocked_count,
                "blocked_ips": blocked_ips,
                "active_ips": recent_ips,
                "log_size": len(self._log),
            }

    def _flush_to_disk(self) -> None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            entries = list(self._log)[-100:]  # last 100 to disk
            with open(LOG_FILE, "w") as f:
                json.dump(entries, f, indent=2)
            self._last_flush = time.time()
        except Exception:
            pass


class APIKeyManager:
    """Manages API keys stored as SHA-256 hashes."""

    def __init__(self):
        self._keys: Dict[str, Dict[str, Any]] = {}  # hash -> metadata
        self._lock = Lock()
        self._load()

    def _load(self) -> None:
        """Load keys from disk."""
        try:
            if os.path.exists(KEYS_FILE):
                with open(KEYS_FILE) as f:
                    self._keys = json.load(f)
        except Exception:
            self._keys = {}

    def _save(self) -> None:
        """Save keys to disk."""
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(KEYS_FILE, "w") as f:
            json.dump(self._keys, f, indent=2)

    def generate_key(self, label: str = "default", scopes: Optional[List[str]] = None) -> str:
        """Generate a new API key, returns the raw key (only time it's visible)."""
        raw_key = f"aimos_{secrets.token_urlsafe(32)}"
        key_hash = _hash_key(raw_key)
        with self._lock:
            self._keys[key_hash] = {
                "label": label,
                "created": _utc_now(),
                "scopes": scopes or ["*"],
                "last_used": None,
                "use_count": 0,
            }
            self._save()
        return raw_key

    def validate(self, raw_key: str) -> Optional[Dict[str, Any]]:
        """Validate a raw API key. Returns metadata if valid, None if invalid."""
        if not raw_key:
            return None
        # Strip "Bearer " prefix if present
        if raw_key.startswith("Bearer "):
            raw_key = raw_key[7:]
        key_hash = _hash_key(raw_key)
        with self._lock:
            if key_hash in self._keys:
                self._keys[key_hash]["last_used"] = _utc_now()
                self._keys[key_hash]["use_count"] += 1
                # Save periodically (every 10 uses)
                if self._keys[key_hash]["use_count"] % 10 == 0:
                    self._save()
                return self._keys[key_hash]
        return None

    def list_keys(self) -> List[Dict[str, Any]]:
        """List all keys (hashes + metadata, never raw keys)."""
        with self._lock:
            return [
                {"hash_prefix": h[:12] + "...", **meta}
                for h, meta in self._keys.items()
            ]

    def revoke(self, hash_prefix: str) -> bool:
        """Revoke a key by its hash prefix."""
        with self._lock:
            for h in list(self._keys.keys()):
                if h.startswith(hash_prefix):
                    del self._keys[h]
                    self._save()
                    return True
        return False

    @property
    def has_keys(self) -> bool:
        return len(self._keys) > 0


class SecurityGate:
    """
    Unified security gate for all AIM-OS HTTP endpoints.

    Combines API key auth, rate limiting, and request logging.
    """

    def __init__(
        self,
        rate_limit: int = DEFAULT_RATE_LIMIT,
        rate_window: int = DEFAULT_RATE_WINDOW,
        enforce_auth: bool = True,
    ):
        self.keys = APIKeyManager()
        self.limiter = RateLimiter(rate_limit, rate_window)
        self.logger = RequestLogger()
        self.enforce_auth = enforce_auth
        self._start_time = time.time()

        # Trusted IPs that bypass auth (localhost)
        self.trusted_ips = frozenset({
            "127.0.0.1",
            "::1",
            "localhost",
            "0.0.0.0",
        })

        # Allowed CORS origins
        self.allowed_origins = [
            "http://localhost:5011",      # JOC dev
            "http://127.0.0.1:5011",
            "https://joc.helixion.net",   # JOC via tunnel
            "https://chatgpt.com",        # ChatGPT
            "https://chat.openai.com",    # ChatGPT legacy
        ]

    def check(
        self,
        ip: str,
        path: str,
        method: str = "GET",
        token: Optional[str] = None,
        user_agent: Optional[str] = None,
        origin: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Check if a request should be allowed.

        Returns:
            {"allowed": True/False, "reason": str, "key_label": str|None}
        """
        result = {
            "allowed": True,
            "reason": "ok",
            "key_label": None,
            "ip": ip,
            "path": path,
            "method": method,
            "timestamp": _utc_now(),
            "blocked": False,
        }

        # 1. Localhost bypass — always trust local requests
        if self._is_trusted(ip):
            result["reason"] = "trusted_ip"
            self.logger.log(result)
            return result

        # 2. Rate limit check
        if not self.limiter.check(ip):
            result["allowed"] = False
            result["reason"] = "rate_limited"
            result["blocked"] = True
            self.logger.log(result)
            return result

        # 3. Public path check — /health, /sse are open
        if self._is_public_path(path):
            result["reason"] = "public_path"
            self.logger.log(result)
            return result

        # 4. Auth check for protected paths
        if self.enforce_auth and self.keys.has_keys:
            if self._requires_auth(path):
                key_meta = self.keys.validate(token or "")
                if key_meta:
                    result["reason"] = "authenticated"
                    result["key_label"] = key_meta.get("label")
                else:
                    result["allowed"] = False
                    result["reason"] = "invalid_api_key"
                    result["blocked"] = True

        # Log the request
        if user_agent:
            result["user_agent"] = user_agent
        self.logger.log(result)
        return result

    def get_cors_headers(self, origin: Optional[str] = None) -> Dict[str, str]:
        """Return appropriate CORS headers."""
        allowed = origin if origin in self.allowed_origins else self.allowed_origins[0]
        return {
            "Access-Control-Allow-Origin": allowed,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Max-Age": "3600",
        }

    def get_security_report(self) -> Dict[str, Any]:
        """Full security report for JOC dashboard."""
        return {
            "timestamp": _utc_now(),
            "uptime_seconds": round(time.time() - self._start_time, 1),
            "auth_enforced": self.enforce_auth,
            "api_keys": self.keys.list_keys(),
            "rate_limit": {
                "max_requests": self.limiter.max_requests,
                "window_seconds": self.limiter.window,
                "active_ips": self.limiter.get_stats(),
            },
            "request_log": self.logger.get_stats(),
            "recent_requests": self.logger.get_recent(30),
            "trusted_ips": list(self.trusted_ips),
            "allowed_origins": self.allowed_origins,
        }

    def _is_trusted(self, ip: str) -> bool:
        return ip in self.trusted_ips

    def _is_public_path(self, path: str) -> bool:
        # Exact match
        if path in PUBLIC_PATHS:
            return True
        # Prefix match for SSE message paths
        for pub in PUBLIC_PATHS:
            if pub.endswith("/") and path.startswith(pub):
                return True
        return False

    def _requires_auth(self, path: str) -> bool:
        for prefix in PROTECTED_PATHS_PREFIX:
            if path.startswith(prefix):
                return True
        return False


# ── Module-level singleton ──────────────────────────────────────────
_gate: Optional[SecurityGate] = None


def get_security_gate() -> SecurityGate:
    """Get or create the global SecurityGate singleton."""
    global _gate
    if _gate is None:
        _gate = SecurityGate()
    return _gate


def generate_initial_key() -> str:
    """Generate the initial API key if none exist. Returns the raw key."""
    gate = get_security_gate()
    if not gate.keys.has_keys:
        key = gate.keys.generate_key(label="admin", scopes=["*"])
        print(f"\n{'='*60}")
        print(f"  🔑 INITIAL API KEY GENERATED")
        print(f"  Save this — it won't be shown again!")
        print(f"")
        print(f"  {key}")
        print(f"")
        print(f"  Use as: Authorization: Bearer {key}")
        print(f"{'='*60}\n")
        return key
    return ""
