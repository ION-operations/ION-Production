#!/usr/bin/env python3
"""
AIM-OS SENTINEL — Host & Integrity Baselines (Phase 4)

Four scanner classes that emit SecurityEvents through TelemetryBus:
  - SecretsScanner    — regex hunt for leaked API keys, tokens, passwords
  - GenomeWatcher     — SHA-256 baseline of genome files + critical scripts
  - OutboundMonitor   — netstat snapshot, whitelist known, flag unknowns
  - AgentIdentityBinder — enrich IP/UA → agent genome identity

Usage:
    from sentinel_host_baselines import HostBaselineScanner
    scanner = HostBaselineScanner(telemetry_bus)
    report = scanner.run_all_scans()
"""

import hashlib
import json
import os
import re
import subprocess
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPO_ROOT = str(Path(__file__).parent.parent)
SCRIPTS_DIR = os.path.join(REPO_ROOT, "scripts")
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
GENOMES_DIR = os.path.join(REPO_ROOT, ".agent", "genomes")
BASELINES_FILE = os.path.join(DATA_DIR, "sentinel_host_baselines.json")

# Import telemetry (soft dependency — works without it)
try:
    from sentinel_telemetry import (
        get_telemetry_bus, TelemetryBus, SecurityEvent, SecurityFinding,
        TrustZone, Severity,
    )
    _HAS_TELEMETRY = True
except ImportError:
    _HAS_TELEMETRY = False


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_file(filepath: str) -> str:
    """Compute SHA-256 hash of a file."""
    h = hashlib.sha256()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    except (OSError, IOError):
        return "FILE_UNREADABLE"


# ── Secrets Scanner ─────────────────────────────────────────────────
class SecretsScanner:
    """Scans files for exposed secrets using regex patterns.

    Detects API keys, tokens, passwords, and other credentials
    that should never appear in plaintext in logs or code.
    """

    # Compiled patterns for speed — ordered by severity
    PATTERNS: List[Tuple[str, str, re.Pattern]] = [
        ("api_key_aimos", "critical", re.compile(r'aimos_[A-Za-z0-9_\-]{20,}', re.I)),
        ("openai_key", "critical", re.compile(r'sk-[A-Za-z0-9]{32,}', re.I)),
        ("anthropic_key", "critical", re.compile(r'sk-ant-[A-Za-z0-9\-]{32,}', re.I)),
        ("google_api_key", "critical", re.compile(r'AIza[A-Za-z0-9_\-]{35}', re.I)),
        ("github_token", "critical", re.compile(r'gh[ps]_[A-Za-z0-9]{36,}', re.I)),
        ("ngrok_token", "high", re.compile(r'ngrok[_\-]?[A-Za-z0-9]{20,}', re.I)),
        ("bearer_token", "high", re.compile(r'Bearer\s+[A-Za-z0-9_\-\.]{20,}', re.I)),
        ("password_assign", "high", re.compile(r'password\s*[:=]\s*["\'][^"\']{4,}["\']', re.I)),
        ("env_secret", "medium", re.compile(r'(?:SECRET|TOKEN|KEY|PASS)\s*=\s*["\']?[A-Za-z0-9_\-]{8,}', re.I)),
        ("private_key", "critical", re.compile(r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----', re.I)),
        ("aws_key", "critical", re.compile(r'AKIA[A-Z0-9]{16}', re.NOFLAG)),
    ]

    # Exclusion patterns (known safe contexts)
    SAFE_CONTEXTS = [
        re.compile(r'#.*regex|pattern|example|test|mock|placeholder', re.I),
        re.compile(r'\.compile\(', re.I),  # Our own regex definitions
        re.compile(r'PATTERNS\s*[:=]', re.I),  # Pattern definition lists
    ]

    def __init__(self):
        self._findings: List[Dict[str, Any]] = []
        self._last_scan: str = ""
        self._lock = threading.Lock()

    def _is_safe_context(self, line: str) -> bool:
        """Check if a match is in a safe context (regex definition, comment, etc.)."""
        return any(p.search(line) for p in self.SAFE_CONTEXTS)

    def scan_file(self, filepath: str) -> List[Dict[str, Any]]:
        """Scan a single file for secrets. Returns list of findings."""
        findings = []
        try:
            with open(filepath, "r", errors="replace") as f:
                for line_no, line in enumerate(f, 1):
                    # Skip safe contexts
                    if self._is_safe_context(line):
                        continue
                    for pattern_name, severity, pattern in self.PATTERNS:
                        match = pattern.search(line)
                        if match:
                            # Mask the actual secret in the finding
                            secret_preview = match.group(0)
                            masked = secret_preview[:6] + "***" + secret_preview[-3:]
                            findings.append({
                                "file": filepath,
                                "line": line_no,
                                "pattern": pattern_name,
                                "severity": severity,
                                "masked_value": masked,
                                "timestamp": _utc_iso(),
                            })
        except (OSError, UnicodeDecodeError):
            pass
        return findings

    def scan_directories(self, telemetry: Optional[Any] = None) -> Dict[str, Any]:
        """Scan configured directories for secrets."""
        scan_targets = []

        # Scan data/mcp/*.json* files
        if os.path.isdir(DATA_DIR):
            for f in os.listdir(DATA_DIR):
                if f.endswith((".json", ".jsonl", ".log")):
                    scan_targets.append(os.path.join(DATA_DIR, f))

        # Scan scripts/*.py
        if os.path.isdir(SCRIPTS_DIR):
            for f in os.listdir(SCRIPTS_DIR):
                if f.endswith(".py"):
                    scan_targets.append(os.path.join(SCRIPTS_DIR, f))

        # Scan .env files at repo root
        for env_name in (".env", ".env.local", ".env.production"):
            env_path = os.path.join(REPO_ROOT, env_name)
            if os.path.exists(env_path):
                scan_targets.append(env_path)

        all_findings = []
        for target in scan_targets:
            all_findings.extend(self.scan_file(target))

        with self._lock:
            self._findings = all_findings
            self._last_scan = _utc_iso()

        # Emit SecurityFindings through telemetry
        if telemetry and _HAS_TELEMETRY and all_findings:
            # Group by severity
            critical = [f for f in all_findings if f["severity"] == "critical"]
            if critical:
                finding = SecurityFinding.create(
                    summary=f"Secrets exposure scan: {len(critical)} critical secrets found in {len(set(f['file'] for f in critical))} files",
                    hypothesis="API keys or tokens may be exposed in plaintext",
                    evidence=[f"{f['file']}:{f['line']} ({f['pattern']})" for f in critical[:10]],
                    confidence=0.9,
                    recommended_actions=["Rotate exposed keys immediately", "Add files to .gitignore"],
                )
                telemetry.record_finding(finding)

            # Also emit a SecurityEvent for the scan itself
            event = SecurityEvent.create(
                source_zone=TrustZone.EVIDENCE,
                target_zone=TrustZone.SECRETS,
                actor_identity="SENTINEL/SecretsScanner",
                actor_type="system",
                event_type="secrets_scan",
                severity="critical" if critical else "info",
                confidence=0.95,
                details={
                    "total_findings": len(all_findings),
                    "critical": len(critical),
                    "files_scanned": len(scan_targets),
                    "patterns_active": len(self.PATTERNS),
                },
            )
            telemetry.record_event(event)

        return {
            "findings": all_findings,
            "total": len(all_findings),
            "files_scanned": len(scan_targets),
            "critical": sum(1 for f in all_findings if f["severity"] == "critical"),
            "high": sum(1 for f in all_findings if f["severity"] == "high"),
            "medium": sum(1 for f in all_findings if f["severity"] == "medium"),
            "last_scan": self._last_scan,
        }

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "total_findings": len(self._findings),
                "critical": sum(1 for f in self._findings if f["severity"] == "critical"),
                "high": sum(1 for f in self._findings if f["severity"] == "high"),
                "last_scan": self._last_scan,
            }


# ── Genome Watcher ──────────────────────────────────────────────────
class GenomeWatcher:
    """SHA-256 baseline monitor for genome files and critical scripts.

    Establishes a hash baseline on first run, then detects any
    modifications on subsequent scans. Changes are emitted as
    SecurityEvents through the TelemetryBus.
    """

    # Critical files to monitor beyond genomes
    CRITICAL_SCRIPTS = [
        "scripts/security.py",
        "scripts/sentinel.py",
        "scripts/sentinel_telemetry.py",
        "scripts/sentinel_host_baselines.py",
        "scripts/mcp_http_fallback_server.py",
        "scripts/mcp_sse_server.py",
    ]

    def __init__(self):
        self._baselines: Dict[str, str] = {}  # filepath -> sha256
        self._changes: List[Dict[str, Any]] = []
        self._last_scan: str = ""
        self._lock = threading.Lock()
        self._load_baselines()

    def _load_baselines(self) -> None:
        """Load saved baselines from disk."""
        try:
            if os.path.exists(BASELINES_FILE):
                with open(BASELINES_FILE) as f:
                    data = json.load(f)
                    self._baselines = data.get("genome_hashes", {})
        except (json.JSONDecodeError, OSError):
            self._baselines = {}

    def _save_baselines(self) -> None:
        """Save baselines to disk."""
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(BASELINES_FILE, "w") as f:
                json.dump({
                    "genome_hashes": self._baselines,
                    "updated": _utc_iso(),
                    "total_files": len(self._baselines),
                }, f, indent=2)
        except OSError:
            pass

    def _get_watched_files(self) -> List[str]:
        """Get all files to watch."""
        files = []

        # Genome files
        if os.path.isdir(GENOMES_DIR):
            for f in os.listdir(GENOMES_DIR):
                if f.endswith(".genome.md"):
                    files.append(os.path.join(GENOMES_DIR, f))

        # Critical scripts
        for rel_path in self.CRITICAL_SCRIPTS:
            full_path = os.path.join(REPO_ROOT, rel_path)
            if os.path.exists(full_path):
                files.append(full_path)

        return files

    def scan(self, telemetry: Optional[Any] = None) -> Dict[str, Any]:
        """Scan all watched files, compare to baseline, emit events for changes."""
        files = self._get_watched_files()
        changes = []
        new_baselines = {}

        for filepath in files:
            current_hash = _sha256_file(filepath)
            rel_path = os.path.relpath(filepath, REPO_ROOT)
            new_baselines[filepath] = current_hash

            if filepath in self._baselines:
                if self._baselines[filepath] != current_hash:
                    change = {
                        "file": rel_path,
                        "status": "MODIFIED",
                        "old_hash": self._baselines[filepath][:16] + "...",
                        "new_hash": current_hash[:16] + "...",
                        "timestamp": _utc_iso(),
                    }
                    changes.append(change)

                    # Emit SecurityEvent for file change
                    if telemetry and _HAS_TELEMETRY:
                        severity = "high" if "security" in rel_path.lower() or "sentinel" in rel_path.lower() else "medium"
                        is_genome = ".genome.md" in rel_path
                        event = SecurityEvent.create(
                            source_zone=TrustZone.EVIDENCE,
                            target_zone=TrustZone.CONTROL_PLANE if is_genome else TrustZone.RUNTIME,
                            actor_identity="SENTINEL/GenomeWatcher",
                            actor_type="system",
                            event_type="genome_modified" if is_genome else "critical_file_modified",
                            severity=severity,
                            confidence=1.0,
                            details={
                                "file": rel_path,
                                "old_hash": self._baselines[filepath][:16],
                                "new_hash": current_hash[:16],
                            },
                        )
                        telemetry.record_event(event)
            else:
                changes.append({
                    "file": rel_path,
                    "status": "BASELINED",
                    "hash": current_hash[:16] + "...",
                    "timestamp": _utc_iso(),
                })

        with self._lock:
            self._baselines = new_baselines
            self._changes = changes
            self._last_scan = _utc_iso()

        self._save_baselines()

        return {
            "files_watched": len(files),
            "files_modified": sum(1 for c in changes if c["status"] == "MODIFIED"),
            "files_baselined": sum(1 for c in changes if c["status"] == "BASELINED"),
            "changes": changes,
            "last_scan": self._last_scan,
        }

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "files_watched": len(self._baselines),
                "modified": sum(1 for c in self._changes if c["status"] == "MODIFIED"),
                "last_scan": self._last_scan,
            }


# ── Outbound Connection Monitor ─────────────────────────────────────
class OutboundMonitor:
    """Monitors network connections and flags unknown destinations.

    Uses netstat to enumerate ESTABLISHED connections, compares against
    a whitelist of expected services, and flags unknowns.
    """

    # Known/expected local ports and destinations
    WHITELIST_PORTS = {5001, 5000, 5011, 5002, 8000}  # Our services
    WHITELIST_HOSTS = {"127.0.0.1", "::1", "0.0.0.0", "localhost"}
    # Cloudflare IPs are trusted (tunnel)
    CLOUDFLARE_PREFIXES = ("104.16.", "104.17.", "104.18.", "104.19.", "104.20.",
                           "172.64.", "172.65.", "172.66.", "172.67.",
                           "198.41.", "2606:4700:")

    def __init__(self):
        self._connections: List[Dict[str, Any]] = []
        self._unknowns: List[Dict[str, Any]] = []
        self._last_scan: str = ""
        self._lock = threading.Lock()

    def _is_whitelisted(self, remote_addr: str, remote_port: int, local_port: int) -> bool:
        """Check if a connection is expected."""
        if remote_addr in self.WHITELIST_HOSTS:
            return True
        if local_port in self.WHITELIST_PORTS:
            return True
        # Cloudflare tunnel connections
        if any(remote_addr.startswith(prefix) for prefix in self.CLOUDFLARE_PREFIXES):
            return True
        # DNS and common system ports
        if remote_port in {53, 443, 80}:
            return True
        return False

    def scan(self, telemetry: Optional[Any] = None) -> Dict[str, Any]:
        """Snapshot current network connections."""
        connections = []
        unknowns = []

        try:
            # Windows netstat
            result = subprocess.run(
                ["netstat", "-nao"],
                capture_output=True, text=True, timeout=10
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if len(parts) >= 4 and parts[0] in ("TCP", "UDP"):
                    state = parts[3] if len(parts) > 3 else "UNKNOWN"
                    if state not in ("ESTABLISHED", "CLOSE_WAIT"):
                        continue

                    local = parts[1]
                    remote = parts[2]

                    # Parse addresses
                    try:
                        local_addr, local_port_s = local.rsplit(":", 1)
                        remote_addr, remote_port_s = remote.rsplit(":", 1)
                        local_port = int(local_port_s)
                        remote_port = int(remote_port_s)
                    except (ValueError, IndexError):
                        continue

                    pid = parts[4] if len(parts) > 4 else "?"
                    conn = {
                        "protocol": parts[0],
                        "local": local,
                        "remote": remote,
                        "remote_addr": remote_addr,
                        "remote_port": remote_port,
                        "local_port": local_port,
                        "state": state,
                        "pid": pid,
                    }
                    connections.append(conn)

                    if not self._is_whitelisted(remote_addr, remote_port, local_port):
                        conn["whitelisted"] = False
                        unknowns.append(conn)

        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            pass

        with self._lock:
            self._connections = connections
            self._unknowns = unknowns
            self._last_scan = _utc_iso()

        # Emit SecurityEvent for unknown connections
        if telemetry and _HAS_TELEMETRY and unknowns:
            event = SecurityEvent.create(
                source_zone=TrustZone.RUNTIME,
                target_zone=TrustZone.EXTERNAL,
                actor_identity="SENTINEL/OutboundMonitor",
                actor_type="system",
                event_type="unknown_outbound_connections",
                severity="medium",
                confidence=0.7,
                details={
                    "unknown_count": len(unknowns),
                    "total_established": len(connections),
                    "samples": [
                        {"remote": u["remote"], "pid": u.get("pid", "?")}
                        for u in unknowns[:5]
                    ],
                },
            )
            telemetry.record_event(event)

        return {
            "total_connections": len(connections),
            "unknown_connections": len(unknowns),
            "unknowns": unknowns[:10],  # Cap for API response
            "last_scan": self._last_scan,
        }

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            return {
                "total_connections": len(self._connections),
                "unknown_connections": len(self._unknowns),
                "last_scan": self._last_scan,
            }


# ── Agent Identity Binder ───────────────────────────────────────────
class AgentIdentityBinder:
    """Maps IPs and User-Agents to known AIM-OS agent identities.

    When SENTINEL sees a request from 127.0.0.1 with a recognizable
    User-Agent, it can enrich the event to say "antigravity/Opus"
    instead of just an IP address.
    """

    # Known agent signatures (UA substrings → identity)
    AGENT_SIGNATURES = {
        "antigravity": "Opus/Antigravity",
        "cursor": "Opus/Antigravity",
        "codex-cli": "Codex/CLI",
        "gemini-cli": "Gemini/CLI",
        "chatgpt": "Sev/ChatGPT",
        "openai": "Sev/ChatGPT",
        "python-requests": "System/Script",
        "node-fetch": "JOC/Frontend",
        "mozilla": "Human/Browser",
        "chrome": "Human/Browser",
    }

    # Known caller IPs
    KNOWN_IPS = {
        "127.0.0.1": "localhost",
        "::1": "localhost",
    }

    def __init__(self):
        self._bindings: Dict[str, str] = {}  # session/ip → identity
        self._lock = threading.Lock()

    def identify(self, ip: str, user_agent: str = "", caller_agent: str = "") -> str:
        """Resolve IP + UA to a human-readable agent identity."""
        # If caller_agent is explicitly set, use it
        if caller_agent:
            return caller_agent

        # Check UA signatures
        ua_lower = user_agent.lower()
        for sig, identity in self.AGENT_SIGNATURES.items():
            if sig in ua_lower:
                return identity

        # Check known IPs
        if ip in self.KNOWN_IPS:
            return f"LOCAL/{self.KNOWN_IPS[ip]}"

        return ip  # Fallback to raw IP

    def enrich_event(self, event_dict: Dict[str, Any], user_agent: str = "") -> Dict[str, Any]:
        """Enrich a SecurityEvent dict with resolved identity."""
        raw_actor = event_dict.get("actor_identity", "")
        resolved = self.identify(raw_actor, user_agent)
        if resolved != raw_actor:
            event_dict["actor_identity"] = resolved
            event_dict.setdefault("details", {})["raw_actor"] = raw_actor
        return event_dict

    def get_status(self) -> Dict[str, Any]:
        return {
            "known_signatures": len(self.AGENT_SIGNATURES),
            "known_ips": len(self.KNOWN_IPS),
        }


# ── Facade Scanner ──────────────────────────────────────────────────
class HostBaselineScanner:
    """Facade wrapping all Phase 4 host baseline scanners.

    Provides a single entry point for running all scans and
    retrieving combined status.
    """

    def __init__(self, telemetry: Optional[Any] = None):
        self.telemetry = telemetry
        self.secrets = SecretsScanner()
        self.genomes = GenomeWatcher()
        self.outbound = OutboundMonitor()
        self.identity = AgentIdentityBinder()
        self._last_full_scan: str = ""
        self._scan_interval = 300  # 5 minutes
        self._last_scan_time = 0.0

    def run_all_scans(self) -> Dict[str, Any]:
        """Run all baseline scans."""
        results = {
            "secrets": self.secrets.scan_directories(self.telemetry),
            "genomes": self.genomes.scan(self.telemetry),
            "outbound": self.outbound.scan(self.telemetry),
            "timestamp": _utc_iso(),
        }
        self._last_full_scan = results["timestamp"]
        self._last_scan_time = time.time()
        return results

    def maybe_periodic_scan(self) -> Optional[Dict[str, Any]]:
        """Run scans if enough time has passed since last one."""
        if time.time() - self._last_scan_time >= self._scan_interval:
            return self.run_all_scans()
        return None

    def get_status(self) -> Dict[str, Any]:
        """Combined status for all scanners."""
        return {
            "secrets": self.secrets.get_status(),
            "genomes": self.genomes.get_status(),
            "outbound": self.outbound.get_status(),
            "identity": self.identity.get_status(),
            "last_full_scan": self._last_full_scan,
        }
