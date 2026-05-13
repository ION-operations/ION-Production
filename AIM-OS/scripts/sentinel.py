#!/usr/bin/env python3
"""
AIM-OS SENTINEL — Security Engine for Networked Threat Intelligence,
                   NL-Logging & Defense

Phase 1: Honeypots, NL Log Feed, Anomaly Detection, GeoIP
Phase 2: Request Signature Analysis, MCP Tool Auditing, IP Profiling,
         File Integrity Baseline
Phase 3: Control-Plane Telemetry, Normalized Events, Provenance, Audit Ledger

Integrates with SecurityGate (scripts/security.py) to provide:
  - Honeypot trap endpoints (instant IP ban on access)
  - Natural language log narration (raw events → human-readable feed)
  - Traffic anomaly baseline with 2σ deviation alerts
  - GeoIP lookup for request origin mapping
  - Threat level assessment (GREEN/YELLOW/RED/CRITICAL)

Usage:
    from sentinel import SentinelEngine
    sentinel = SentinelEngine()
    sentinel.process_request(request_info)
    feed = sentinel.get_nl_feed(limit=20)
    status = sentinel.get_status()
"""

import hashlib
import json
import math
import os
import re
import time
import threading
import urllib.request
from collections import deque, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPO_ROOT = str(Path(__file__).parent.parent)
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
SENTINEL_LOG = os.path.join(DATA_DIR, "sentinel_feed.json")
BANNED_IPS_FILE = os.path.join(DATA_DIR, "sentinel_banned_ips.json")
GEOIP_CACHE_FILE = os.path.join(DATA_DIR, "sentinel_geoip_cache.json")
AUDIT_LOG_FILE = os.path.join(DATA_DIR, "sentinel_audit.json")
FILE_INTEGRITY_FILE = os.path.join(DATA_DIR, "sentinel_file_integrity.json")

# Phase 3: TelemetryBus integration
try:
    from sentinel_telemetry import (
        get_telemetry_bus, TelemetryBus, SecurityEvent, SecurityFinding,
        ResponseAction, TrustZone, AutonomyLevel,
    )
    _HAS_TELEMETRY = True
except ImportError:
    _HAS_TELEMETRY = False

# Phase 4: Host & Integrity Baselines
try:
    from sentinel_host_baselines import HostBaselineScanner
    _HAS_BASELINES = True
except ImportError:
    _HAS_BASELINES = False

# Phase 5: WRAITH + Agent Sessions
try:
    from sentinel_sessions import SessionRegistry
    from sentinel_wraith import WraithEngine
    _HAS_PHASE5 = True
except ImportError:
    _HAS_PHASE5 = False

# Phase 6: Policy Engine + MCP Governance
try:
    from sentinel_policy_engine import PolicyEngine
    from sentinel_mcp_governance import GovernanceEngine
    _HAS_PHASE6 = True
except ImportError:
    _HAS_PHASE6 = False

# Phase 7: PHANTOM Offensive Countermeasures
try:
    from sentinel_phantom import PhantomEngine
    from sentinel_recon import ReconEngine
    _HAS_PHASE7 = True
except ImportError:
    _HAS_PHASE7 = False

# Phase 8: CHRONICLE Audit Chain + Incident Response
try:
    from sentinel_chronicle import ChronicleEngine
    _HAS_PHASE8 = True
except ImportError:
    _HAS_PHASE8 = False

# Phase 9: NEXUS Threat Intelligence Fusion + Adaptive Learning
try:
    from sentinel_nexus import NexusEngine
    _HAS_PHASE9 = True
except ImportError:
    _HAS_PHASE9 = False

# ── Honeypot Traps ──────────────────────────────────────────────────
# Any request to these paths = instant IP ban + alert
HONEYPOT_PATHS = frozenset({
    "/admin",
    "/admin/",
    "/wp-login.php",
    "/wp-admin",
    "/wp-admin/",
    "/.env",
    "/.git",
    "/.git/config",
    "/phpmyadmin",
    "/phpmyadmin/",
    "/config.php",
    "/xmlrpc.php",
    "/shell",
    "/shell.php",
    "/cmd",
    "/eval",
    "/debug",
    "/backup",
    "/database",
    "/passwd",
    "/etc/passwd",
    "/.aws/credentials",
    "/.ssh/id_rsa",
    "/api/v1/admin",
    "/actuator",
    "/actuator/env",
    "/server-status",
    "/.well-known/../",
})

# ── Threat Levels ───────────────────────────────────────────────────
THREAT_GREEN = "GREEN"       # Normal operation
THREAT_YELLOW = "YELLOW"     # Elevated — anomalous traffic or honeypot probes
THREAT_RED = "RED"           # Active attack — rate limits hit, multiple blocks
THREAT_CRITICAL = "CRITICAL" # Sustained attack — multiple IPs, repeated bans

# ── NL Log Emojis ───────────────────────────────────────────────────
NL_ICONS = {
    "normal": "🟢",
    "info": "🔵",
    "warning": "🟡",
    "alert": "🔴",
    "honeypot": "🍯",
    "ban": "⛔",
    "red_team": "🟣",
    "system": "⚙️",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%H:%M:%S")


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ── Phase 2: Request Signature Analysis ─────────────────────────────
class RequestSignatureAnalyzer:
    """Detects attack payloads in request paths, bodies, and headers.

    Categories: SQLi, XSS, Command Injection, Path Traversal, LFI, Shellshock.
    Uses compiled regex patterns for performance.
    """

    SIGNATURES: Dict[str, List[re.Pattern]] = {
        "sqli": [
            re.compile(r"(?i)(?:union\s+(?:all\s+)?select|select\s+.+from)"),
            re.compile(r"(?i)(?:or|and)\s+['\"]?\d+['\"]?\s*[=<>]"),
            re.compile(r"(?i)(?:insert|update|delete|drop|alter|create)\s+(?:into|table|database)"),
            re.compile(r"(?i)(?:--|#|/\*).*(?:$|\*/)"),  # SQL comments
            re.compile(r"(?i)(?:exec|execute|xp_|sp_)\w+"),
            re.compile(r"(?i)(?:sleep|benchmark|waitfor\s+delay)\s*\("),
            re.compile(r"(?i)(?:load_file|into\s+(?:outfile|dumpfile))\s*\("),
            re.compile(r"(?i)(?:information_schema|sys\.\w+|mysql\.\w+)"),
        ],
        "xss": [
            re.compile(r"(?i)<\s*script[^>]*>"),
            re.compile(r"(?i)(?:on(?:error|load|click|mouseover|focus|blur|submit))\s*="),
            re.compile(r"(?i)javascript\s*:"),
            re.compile(r"(?i)<\s*(?:img|iframe|object|embed|svg|video|audio)[^>]+(?:src|data|href)\s*="),
            re.compile(r"(?i)(?:eval|alert|confirm|prompt|document\.)\s*\("),
            re.compile(r"(?i)<\s*(?:style|link)[^>]*>.*(?:expression|import|url)\s*\("),
        ],
        "command_injection": [
            re.compile(r"(?:[;|`]|\$\()\s*(?:cat|ls|id|whoami|uname|pwd|wget|curl|nc|bash|sh|python|perl|ruby|php)"),
            re.compile(r"(?i)(?:\||&&)\s*(?:cat|ls|id|whoami|uname|pwd)"),
            re.compile(r"(?i)(?:/bin/(?:sh|bash|zsh)|cmd\.exe|powershell)"),
            re.compile(r"\$\{.*\}"),  # Shell variable expansion
        ],
        "path_traversal": [
            re.compile(r"(?:\.\.[\\/]){2,}"),
            re.compile(r"(?i)(?:etc/(?:passwd|shadow|hosts)|proc/self|windows/system32)"),
            re.compile(r"(?i)(?:\.(?:env|git|svn|hg|aws|ssh|docker))"),
            re.compile(r"%(?:2e|2f|5c|c0%af|c1%1c)", re.IGNORECASE),  # Encoded traversal
        ],
        "lfi": [
            re.compile(r"(?i)(?:php://|file://|dict://|gopher://|ftp://|ldap://|data:)"),
            re.compile(r"(?i)(?:expect://|input://|filter/|zip://|phar://)"),
            re.compile(r"(?i)(?:include|require)(?:_once)?\s*\("),
        ],
        "shellshock": [
            re.compile(r"\(\)\s*\{\s*[^}]*;\s*}\s*;"),  # Shellshock CVE-2014-6271
        ],
    }

    SEVERITY = {
        "sqli": "critical",
        "xss": "high",
        "command_injection": "critical",
        "path_traversal": "high",
        "lfi": "critical",
        "shellshock": "critical",
    }

    @classmethod
    def scan(cls, text: str) -> List[Dict[str, str]]:
        """Scan text for attack signatures. Returns list of matches."""
        findings: List[Dict[str, str]] = []
        for category, patterns in cls.SIGNATURES.items():
            for pattern in patterns:
                match = pattern.search(text)
                if match:
                    findings.append({
                        "category": category,
                        "severity": cls.SEVERITY.get(category, "medium"),
                        "matched": match.group()[:80],
                        "pattern": pattern.pattern[:60],
                    })
                    break  # One match per category is enough
        return findings


# ── Phase 2: Per-IP Behavior Profiler ───────────────────────────────
class IPProfiler:
    """Tracks per-IP behavior patterns for behavioral anomaly detection."""

    def __init__(self):
        self._profiles: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def record(self, ip: str, path: str, method: str, was_blocked: bool = False) -> None:
        with self._lock:
            if ip not in self._profiles:
                self._profiles[ip] = {
                    "first_seen": _utc_iso(),
                    "last_seen": _utc_iso(),
                    "request_count": 0,
                    "blocked_count": 0,
                    "paths": defaultdict(int),
                    "methods": defaultdict(int),
                    "suspicious_count": 0,
                }
            p = self._profiles[ip]
            p["last_seen"] = _utc_iso()
            p["request_count"] += 1
            p["methods"][method] += 1
            # Track top paths (limit stored paths to prevent memory bloat)
            if len(p["paths"]) < 100:
                p["paths"][path] += 1
            if was_blocked:
                p["blocked_count"] += 1

    def flag_suspicious(self, ip: str) -> None:
        with self._lock:
            if ip in self._profiles:
                self._profiles[ip]["suspicious_count"] += 1

    def get_profile(self, ip: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            if ip not in self._profiles:
                return None
            p = self._profiles[ip].copy()
            p["paths"] = dict(p["paths"])
            p["methods"] = dict(p["methods"])
            return p

    def get_summary(self) -> Dict[str, Any]:
        """Summary stats for JOC."""
        with self._lock:
            total_ips = len(self._profiles)
            suspicious = sum(1 for p in self._profiles.values() if p["suspicious_count"] > 0)
            top_talkers = sorted(
                self._profiles.items(),
                key=lambda x: x[1]["request_count"],
                reverse=True
            )[:5]
            return {
                "total_ips_tracked": total_ips,
                "suspicious_ips": suspicious,
                "top_talkers": [
                    {"ip": ip, "requests": p["request_count"], "blocked": p["blocked_count"]}
                    for ip, p in top_talkers
                ],
            }


# ── Phase 2: MCP Tool Call Auditor ──────────────────────────────────
class MCPAuditor:
    """Audits MCP tool executions for security-relevant patterns."""

    def __init__(self):
        self._log: deque = deque(maxlen=500)
        self._tool_counts: Dict[str, int] = defaultdict(int)
        self._lock = threading.Lock()
        self._suspicious_tools = {
            "run_command", "send_command_input", "write_to_file",
            "replace_file_content", "multi_replace_file_content",
        }

    def audit(self, tool_name: str, arguments: Dict[str, Any], caller_ip: str = "local") -> Optional[Dict[str, Any]]:
        """Audit a tool call. Returns alert dict if suspicious."""
        entry = {
            "timestamp": _utc_iso(),
            "tool": tool_name,
            "caller_ip": caller_ip,
            "args_size": len(json.dumps(arguments, default=str)),
        }

        alert = None

        # Check for sensitive tool usage from external IPs
        if caller_ip not in ("127.0.0.1", "::1", "localhost", "local") and tool_name in self._suspicious_tools:
            entry["alert"] = "sensitive_tool_external"
            alert = {
                "type": "sensitive_tool_external",
                "tool": tool_name,
                "ip": caller_ip,
                "severity": "critical",
            }

        # Check for prompt injection in arguments
        args_str = json.dumps(arguments, default=str)
        sig_findings = RequestSignatureAnalyzer.scan(args_str)
        if sig_findings:
            entry["attack_signatures"] = sig_findings
            alert = {
                "type": "attack_payload_in_tool_args",
                "tool": tool_name,
                "ip": caller_ip,
                "findings": sig_findings,
                "severity": sig_findings[0]["severity"],
            }

        with self._lock:
            self._log.append(entry)
            self._tool_counts[tool_name] += 1

        return alert

    def get_recent(self, limit: int = 30) -> List[Dict[str, Any]]:
        with self._lock:
            return list(self._log)[-limit:]

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            total = sum(self._tool_counts.values())
            top = sorted(self._tool_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            alerts = sum(1 for e in self._log if "alert" in e)
            return {
                "total_calls": total,
                "unique_tools": len(self._tool_counts),
                "top_tools": [{"tool": t, "count": c} for t, c in top],
                "alerts": alerts,
            }


# ── Phase 2: File Integrity Baseline ────────────────────────────────
class FileIntegrityMonitor:
    """SHA-256 baseline of critical files, detects modifications."""

    WATCHED_PATTERNS = [
        "scripts/security.py",
        "scripts/sentinel.py",
        "scripts/mcp_http_fallback_server.py",
        "scripts/mcp_sse_server.py",
        "scripts/mcp_bridge.py",
        ".agent/genomes/*.genome.md",
        ".env",
        "package.json",
    ]

    def __init__(self):
        self._baseline: Dict[str, str] = {}  # path -> sha256
        self._changes: List[Dict[str, str]] = []
        self._lock = threading.Lock()
        self._last_scan = 0.0
        self._load_baseline()

    def _hash_file(self, filepath: str) -> Optional[str]:
        try:
            h = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(8192), b""):
                    h.update(chunk)
            return h.hexdigest()
        except Exception:
            return None

    def _resolve_paths(self) -> List[str]:
        """Resolve glob patterns to actual file paths."""
        import glob
        resolved = []
        for pattern in self.WATCHED_PATTERNS:
            full = os.path.join(REPO_ROOT, pattern)
            matches = glob.glob(full)
            resolved.extend(matches)
        return resolved

    def scan(self) -> List[Dict[str, str]]:
        """Scan watched files and compare to baseline."""
        changes = []
        paths = self._resolve_paths()

        with self._lock:
            for path in paths:
                current_hash = self._hash_file(path)
                if current_hash is None:
                    continue
                rel = os.path.relpath(path, REPO_ROOT)
                if rel in self._baseline:
                    if self._baseline[rel] != current_hash:
                        changes.append({
                            "file": rel,
                            "status": "MODIFIED",
                            "old_hash": self._baseline[rel][:12],
                            "new_hash": current_hash[:12],
                            "detected": _utc_iso(),
                        })
                        self._baseline[rel] = current_hash
                else:
                    self._baseline[rel] = current_hash
                    changes.append({
                        "file": rel,
                        "status": "BASELINED",
                        "hash": current_hash[:12],
                        "detected": _utc_iso(),
                    })

            self._changes.extend(changes)
            self._last_scan = time.time()

        if changes:
            self._save_baseline()
        return changes

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "files_monitored": len(self._baseline),
                "last_scan": self._last_scan,
                "recent_changes": self._changes[-10:] if self._changes else [],
            }

    def _load_baseline(self) -> None:
        try:
            if os.path.exists(FILE_INTEGRITY_FILE):
                with open(FILE_INTEGRITY_FILE) as f:
                    self._baseline = json.load(f)
        except Exception:
            self._baseline = {}

    def _save_baseline(self) -> None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(FILE_INTEGRITY_FILE, "w") as f:
                json.dump(self._baseline, f, indent=2)
        except Exception:
            pass


class GeoIPLookup:
    """GeoIP using free ip-api.com (no key needed, 45 req/min)."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()
        self._load_cache()

    def _load_cache(self) -> None:
        try:
            if os.path.exists(GEOIP_CACHE_FILE):
                with open(GEOIP_CACHE_FILE) as f:
                    self._cache = json.load(f)
        except Exception:
            self._cache = {}

    def _save_cache(self) -> None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(GEOIP_CACHE_FILE, "w") as f:
                json.dump(self._cache, f)
        except Exception:
            pass

    def lookup(self, ip: str) -> Dict[str, Any]:
        """Lookup GeoIP info for an IP. Returns cached or live results."""
        # Skip private/local IPs
        if ip in ("127.0.0.1", "::1", "localhost", "0.0.0.0") or ip.startswith("192.168.") or ip.startswith("10."):
            return {"country": "Local", "city": "localhost", "isp": "Local Network", "is_local": True}

        with self._lock:
            if ip in self._cache:
                return self._cache[ip]

        # Live lookup (non-blocking thread would be better, but this is fine for now)
        try:
            req = urllib.request.Request(
                f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,regionName,city,isp,org,query",
                headers={"User-Agent": "AIM-OS-SENTINEL/1.0"}
            )
            with urllib.request.urlopen(req, timeout=3) as resp:
                data = json.loads(resp.read().decode())
                if data.get("status") == "success":
                    result = {
                        "country": data.get("country", "Unknown"),
                        "country_code": data.get("countryCode", "??"),
                        "city": data.get("city", "Unknown"),
                        "region": data.get("regionName", ""),
                        "isp": data.get("isp", "Unknown"),
                        "org": data.get("org", ""),
                        "is_local": False,
                    }
                    with self._lock:
                        self._cache[ip] = result
                        if len(self._cache) % 10 == 0:
                            self._save_cache()
                    return result
        except Exception:
            pass

        return {"country": "Unknown", "city": "Unknown", "isp": "Unknown", "is_local": False}


class AnomalyDetector:
    """Tracks request rate baseline and flags statistical anomalies."""

    def __init__(self, window_minutes: int = 10):
        self.window = window_minutes * 60
        self._timestamps: deque = deque()
        self._minute_counts: deque = deque(maxlen=60)  # last 60 minutes
        self._last_minute_ts: float = 0
        self._last_minute_count: int = 0
        self._lock = threading.Lock()

    def record(self) -> None:
        """Record a request timestamp."""
        now = time.time()
        with self._lock:
            self._timestamps.append(now)
            # Purge old entries
            cutoff = now - self.window
            while self._timestamps and self._timestamps[0] < cutoff:
                self._timestamps.popleft()
            # Track per-minute counts
            current_minute = int(now / 60)
            if current_minute != int(self._last_minute_ts / 60):
                if self._last_minute_ts > 0:
                    self._minute_counts.append(self._last_minute_count)
                self._last_minute_count = 0
                self._last_minute_ts = now
            self._last_minute_count += 1

    def is_anomalous(self) -> tuple:
        """Check if current rate is anomalous. Returns (is_anomaly, current_rate, baseline, threshold)."""
        with self._lock:
            if len(self._minute_counts) < 3:
                # Not enough data for baseline
                return (False, len(self._timestamps), 0, 0)

            counts = list(self._minute_counts)
            mean = sum(counts) / len(counts)
            variance = sum((x - mean) ** 2 for x in counts) / len(counts)
            std = math.sqrt(variance) if variance > 0 else 1
            threshold = mean + (2 * std)  # 2σ deviation

            current_rate = self._last_minute_count
            is_anomaly = current_rate > threshold and current_rate > 5  # min 5 to avoid noise

            return (is_anomaly, current_rate, round(mean, 1), round(threshold, 1))

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            counts = list(self._minute_counts)
            if not counts:
                return {"baseline_rpm": 0, "current_rpm": 0, "std_dev": 0, "data_minutes": 0}
            mean = sum(counts) / len(counts)
            variance = sum((x - mean) ** 2 for x in counts) / len(counts)
            return {
                "baseline_rpm": round(mean, 1),
                "current_rpm": self._last_minute_count,
                "std_dev": round(math.sqrt(variance), 1),
                "data_minutes": len(counts),
                "window_total": len(self._timestamps),
            }


class SentinelEngine:
    """
    SENTINEL — main security intelligence engine.

    Processes every request, maintains NL feed, detects anomalies,
    manages honeypots, and assesses threat level.
    """

    def __init__(self):
        self._nl_feed: deque = deque(maxlen=200)
        self._banned_ips: Set[str] = set()
        self._honeypot_hits: Dict[str, int] = {}  # ip -> count
        self._lock = threading.Lock()
        self.geoip = GeoIPLookup()
        self.anomaly = AnomalyDetector()
        self.signatures = RequestSignatureAnalyzer()
        self.ip_profiler = IPProfiler()
        self.mcp_auditor = MCPAuditor()
        self.file_integrity = FileIntegrityMonitor()
        self._threat_level = THREAT_GREEN
        self._start_time = time.time()
        self._total_processed = 0
        self._total_blocked = 0
        self._total_honeypot_hits = 0
        self._total_attacks_detected = 0

        # NEVER ban these IPs — prevents localhost lockout
        self._safeguard_ips = frozenset({"127.0.0.1", "::1", "localhost", "0.0.0.0"})

        self._load_banned_ips()

        # Phase 3: TelemetryBus
        self.telemetry = get_telemetry_bus() if _HAS_TELEMETRY else None

        # Phase 4: Host Baselines
        self.host_baselines = HostBaselineScanner(self.telemetry) if _HAS_BASELINES else None

        # Phase 5: WRAITH + Agent Sessions
        self.sessions = SessionRegistry(self.telemetry) if _HAS_PHASE5 else None
        self.wraith = WraithEngine(self.telemetry) if _HAS_PHASE5 else None

        # Phase 6: Policy Engine + MCP Governance
        self.policy_engine = PolicyEngine(self.telemetry) if _HAS_PHASE6 else None
        self.governance = GovernanceEngine(self.telemetry, self.sessions) if _HAS_PHASE6 else None

        # Phase 7: PHANTOM Offensive Countermeasures
        self.phantom = PhantomEngine(self.telemetry) if _HAS_PHASE7 else None
        self.recon = ReconEngine(self.telemetry) if _HAS_PHASE7 else None

        # Phase 8: CHRONICLE Audit Chain + Incident Response
        self.chronicle = ChronicleEngine(self.telemetry) if _HAS_PHASE8 else None

        # Phase 9: NEXUS Threat Intelligence Fusion
        self.nexus = NexusEngine(
            telemetry=self.telemetry,
            chronicle=self.chronicle,
            phantom=self.phantom,
            recon=self.recon,
            sessions=self.sessions,
        ) if _HAS_PHASE9 else None

        self._emit("system", "SENTINEL engine initialized — Phase 9 NEXUS threat intelligence active")

        # Initial file integrity baseline scan
        try:
            changes = self.file_integrity.scan()
            baselined = sum(1 for c in changes if c["status"] == "BASELINED")
            if baselined:
                self._emit("system", f"File integrity: {baselined} files baselined")
        except Exception:
            pass

        # Initial host baseline scan
        if self.host_baselines:
            try:
                scan = self.host_baselines.run_all_scans()
                genome_status = scan.get("genomes", {})
                secrets_status = scan.get("secrets", {})
                self._emit("system", f"Host baselines: {genome_status.get('files_watched', 0)} files watched, {secrets_status.get('total', 0)} secrets findings")
            except Exception:
                pass

    # ── Core Processing ─────────────────────────────────────────────

    def process_request(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming request through SENTINEL.

        Args:
            info: {"ip": str, "path": str, "method": str, "blocked": bool,
                   "reason": str, "user_agent": str, "timestamp": str}

        Returns:
            {"action": "allow"|"ban"|"alert", "nl_message": str}
        """
        ip = info.get("ip", "unknown")
        path = info.get("path", "/")
        method = info.get("method", "GET")
        blocked = info.get("blocked", False)
        reason = info.get("reason", "")
        user_agent = info.get("user_agent", "")

        self._total_processed += 1
        self.anomaly.record()

        # 1. Check if IP is banned
        if ip in self._banned_ips:
            self._total_blocked += 1
            if self.telemetry:
                self.telemetry.audit_request(ip=ip, path=path, method=method, blocked=True, user_agent=user_agent)
            return {"action": "ban", "nl_message": f"Banned IP {ip} attempted access — dropped"}

        # 2. Honeypot check
        if self._is_honeypot(path):
            self._trigger_honeypot(ip, path, user_agent)
            return {"action": "ban", "nl_message": f"Honeypot triggered — {ip} banned"}

        # 3. Already blocked by SecurityGate
        if blocked:
            self._total_blocked += 1
            geo = self.geoip.lookup(ip)
            location = f"{geo['city']}, {geo['country']}" if not geo.get("is_local") else "localhost"
            self._emit("alert", f"Blocked {ip} ({location}) → {path} — {reason}")
            self._update_threat_level()
            return {"action": "alert", "nl_message": f"Blocked: {ip} from {location}"}

        # 4. Request signature analysis — detect attack payloads
        scan_text = f"{path} {user_agent} {info.get('query_string', '')} {info.get('body', '')}"
        attack_findings = self.signatures.scan(scan_text)
        if attack_findings:
            self._total_attacks_detected += 1
            self.ip_profiler.flag_suspicious(ip)
            top = attack_findings[0]
            geo = self.geoip.lookup(ip)
            location = f"{geo['city']}, {geo['country']}" if not geo.get('is_local') else "local"
            self._emit("alert", f"ATTACK PAYLOAD — {top['category'].upper()} ({top['severity']}) from {ip} ({location}) → {path}")
            if top["severity"] == "critical":
                # SAFEGUARD: Never ban localhost
                if ip in self._safeguard_ips:
                    self._emit("warn", f"Critical attack from localhost ({ip}) — NOT banning")
                else:
                    self._banned_ips.add(ip)
                    self._total_blocked += 1
                    self._emit("ban", f"IP {ip} auto-banned — critical attack payload detected ({top['category']})")
                    self._save_banned_ips()
                    self._update_threat_level()
                    # Phase 3: Record provenance for auto-ban
                    if self.telemetry:
                        evt = self.telemetry.audit_request(
                            ip=ip, path=path, method=method, blocked=True,
                            attack_category=top["category"], user_agent=user_agent,
                        )
                        self.telemetry.record_auto_response(
                            action_type="ban_ip",
                            trigger_event_id=evt.event_id,
                            details={"ip": ip, "reason": top["category"], "severity": top["severity"]},
                        )
                    return {"action": "ban", "nl_message": f"Attack detected: {top['category']}", "findings": attack_findings}

        # 5. IP profiling
        self.ip_profiler.record(ip, path, method, was_blocked=blocked)

        # 6. Normal traffic — NL narration for external IPs
        if not self._is_local(ip):
            geo = self.geoip.lookup(ip)
            location = f"{geo['city']}, {geo['country']}" if not geo.get("is_local") else "local"
            self._emit("info", f"External request from {ip} ({location}) → {method} {path}")
        else:
            # Quiet logging for local traffic (don't spam the feed)
            if path not in ("/health", "/sentinel/feed", "/sentinel/status", "/security/report", "/connections"):
                self._emit("normal", f"{method} {path} (local, routine)")

        # 7. Anomaly check
        is_anomaly, current, baseline, threshold = self.anomaly.is_anomalous()
        if is_anomaly:
            self._emit("warning", f"Traffic anomaly detected — {current} req/min (baseline: {baseline}, threshold: {threshold})")
            self._threat_level = THREAT_YELLOW

        self._update_threat_level()
        return {"action": "allow", "nl_message": "ok"}

    # ── Honeypot System ─────────────────────────────────────────────

    def _is_honeypot(self, path: str) -> bool:
        """Check if path matches a honeypot trap."""
        path_lower = path.lower().rstrip("/")
        if path_lower + "/" in HONEYPOT_PATHS or path_lower in HONEYPOT_PATHS:
            return True
        # Also catch common traversal attempts
        if ".." in path or "etc/passwd" in path or ".env" in path:
            return True
        return False

    def _trigger_honeypot(self, ip: str, path: str, user_agent: str) -> None:
        """Handle honeypot trigger — ban IP, log, alert."""
        # SAFEGUARD: Never ban localhost
        if ip in self._safeguard_ips:
            self._emit("warn", f"Honeypot triggered by localhost ({ip}) on {path} — NOT banning")
            return

        self._total_honeypot_hits += 1
        self._total_blocked += 1

        with self._lock:
            self._honeypot_hits[ip] = self._honeypot_hits.get(ip, 0) + 1
            self._banned_ips.add(ip)

        geo = self.geoip.lookup(ip)
        location = f"{geo['city']}, {geo['country']}" if not geo.get("is_local") else "local"
        isp = geo.get("isp", "Unknown")

        self._emit("honeypot", f"TRAP TRIGGERED — {ip} ({location}, {isp}) hit {path}")
        self._emit("ban", f"IP {ip} permanently banned — honeypot access detected")

        if user_agent:
            ua_short = user_agent[:80] + "..." if len(user_agent) > 80 else user_agent
            self._emit("info", f"  Attacker UA: {ua_short}")

        self._save_banned_ips()
        self._update_threat_level()

    def is_banned(self, ip: str) -> bool:
        """Check if IP is banned."""
        return ip in self._banned_ips

    # ── NL Feed ─────────────────────────────────────────────────────

    def _emit(self, level: str, message: str) -> None:
        """Add an NL entry to the feed."""
        icon = NL_ICONS.get(level, "⚪")
        entry = {
            "time": _utc_now(),
            "timestamp": _utc_iso(),
            "level": level,
            "icon": icon,
            "message": message,
            "text": f"{icon} {_utc_now()}  {message}",
        }
        with self._lock:
            self._nl_feed.append(entry)

    def get_nl_feed(self, limit: int = 30) -> List[Dict[str, Any]]:
        """Get recent NL feed entries."""
        with self._lock:
            entries = list(self._nl_feed)
        return entries[-limit:]

    # ── Threat Level ────────────────────────────────────────────────

    def _update_threat_level(self) -> None:
        """Recalculate threat level based on recent activity."""
        recent_blocks = self._total_blocked
        honeypot_hits = self._total_honeypot_hits
        banned_count = len(self._banned_ips)

        if honeypot_hits > 5 or banned_count > 10 or recent_blocks > 50:
            self._threat_level = THREAT_CRITICAL
        elif honeypot_hits > 2 or banned_count > 3 or recent_blocks > 20:
            self._threat_level = THREAT_RED
        elif honeypot_hits > 0 or recent_blocks > 5:
            self._threat_level = THREAT_YELLOW
        else:
            self._threat_level = THREAT_GREEN

    # ── Status Report ───────────────────────────────────────────────

    def get_status(self) -> Dict[str, Any]:
        """Full SENTINEL status for JOC."""
        uptime = time.time() - self._start_time
        anomaly_stats = self.anomaly.get_stats()

        return {
            "threat_level": self._threat_level,
            "uptime_seconds": round(uptime, 1),
            "total_processed": self._total_processed,
            "total_blocked": self._total_blocked,
            "total_honeypot_hits": self._total_honeypot_hits,
            "total_attacks_detected": self._total_attacks_detected,
            "banned_ips": list(self._banned_ips),
            "banned_count": len(self._banned_ips),
            "honeypot_hits_by_ip": dict(self._honeypot_hits),
            "anomaly": anomaly_stats,
            "ip_profiles": self.ip_profiler.get_summary(),
            "mcp_audit": self.mcp_auditor.get_stats(),
            "file_integrity": self.file_integrity.get_status(),
            "threat_colors": {
                THREAT_GREEN: "#22cc44",
                THREAT_YELLOW: "#cc8800",
                THREAT_RED: "#cc3333",
                THREAT_CRITICAL: "#ff0044",
            },
            "honeypot_paths_count": len(HONEYPOT_PATHS),
            "telemetry": self.telemetry.get_telemetry_status() if self.telemetry else {"status": "unavailable"},
            "host_baselines": self.host_baselines.get_status() if self.host_baselines else {"status": "unavailable"},
            "sessions": self.sessions.get_status() if self.sessions else {"status": "unavailable"},
            "wraith": self.wraith.get_status() if self.wraith else {"status": "unavailable"},
            "policies": self.policy_engine.get_status() if self.policy_engine else {"status": "unavailable"},
            "governance": self.governance.get_status() if self.governance else {"status": "unavailable"},
            "phantom": self.phantom.get_status() if self.phantom else {"status": "unavailable"},
            "recon": self.recon.get_status() if self.recon else {"status": "unavailable"},
            "chronicle": self.chronicle.get_status() if self.chronicle else {"status": "unavailable"},
            "nexus": self.nexus.get_status() if self.nexus else {"status": "unavailable"},
            "timestamp": _utc_iso(),
        }

    # ── Persistence ─────────────────────────────────────────────────

    def _load_banned_ips(self) -> None:
        try:
            if os.path.exists(BANNED_IPS_FILE):
                with open(BANNED_IPS_FILE) as f:
                    data = json.load(f)
                    self._banned_ips = set(data.get("banned", []))
                    self._honeypot_hits = data.get("honeypot_hits", {})
        except Exception:
            pass

    def _save_banned_ips(self) -> None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(BANNED_IPS_FILE, "w") as f:
                json.dump({
                    "banned": list(self._banned_ips),
                    "honeypot_hits": self._honeypot_hits,
                    "updated": _utc_iso(),
                }, f, indent=2)
        except Exception:
            pass

    # ── MCP Tool Auditing ────────────────────────────────────────────

    def audit_tool_call(self, tool_name: str, arguments: Dict[str, Any], caller_ip: str = "local") -> Optional[Dict[str, Any]]:
        """Audit an MCP tool call through SENTINEL."""
        alert = self.mcp_auditor.audit(tool_name, arguments, caller_ip)
        if alert:
            sev = alert.get("severity", "medium")
            self._emit(
                "alert" if sev == "critical" else "warning",
                f"MCP AUDIT — {alert['type']} — tool={tool_name} from {caller_ip}"
            )
            self._total_attacks_detected += 1
        return alert

    # ── File Integrity Scan ─────────────────────────────────────────

    def scan_file_integrity(self) -> List[Dict[str, str]]:
        """Run a file integrity scan and log results."""
        changes = self.file_integrity.scan()
        for c in changes:
            if c["status"] == "MODIFIED":
                self._emit("alert", f"FILE MODIFIED — {c['file']} ({c['old_hash']} → {c['new_hash']})")
            elif c["status"] == "BASELINED":
                self._emit("system", f"File baselined: {c['file']}")
        return changes

    # ── Helpers ──────────────────────────────────────────────────────

    @staticmethod
    def _is_local(ip: str) -> bool:
        return ip in ("127.0.0.1", "::1", "localhost", "0.0.0.0") or ip.startswith("192.168.") or ip.startswith("10.")


# ── Module-level singleton ──────────────────────────────────────────
_sentinel: Optional[SentinelEngine] = None


def get_sentinel() -> SentinelEngine:
    """Get or create the global SentinelEngine singleton."""
    global _sentinel
    if _sentinel is None:
        _sentinel = SentinelEngine()
    return _sentinel
