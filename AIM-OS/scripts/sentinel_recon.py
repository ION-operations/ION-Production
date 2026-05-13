#!/usr/bin/env python3
"""
AIM-OS SENTINEL — Reconnaissance Engine (Phase 7)

Attacker reconnaissance and threat attribution via local OSINT.
No external API calls — all analysis is performed locally from observed traffic.

Usage:
    from sentinel_recon import ReconEngine
    engine = ReconEngine(telemetry_bus)
    intel = engine.analyze(ip, user_agent, payload)
"""

import hashlib
import json
import os
import re
import socket
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPO_ROOT = str(Path(__file__).parent.parent)
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
RECON_DB_FILE = os.path.join(DATA_DIR, "sentinel_recon_intel.json")

try:
    from sentinel_telemetry import SecurityEvent, TrustZone
    _HAS_TELEMETRY = True
except ImportError:
    _HAS_TELEMETRY = False


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════
#  MITRE ATT&CK TECHNIQUE MAPPING
# ═══════════════════════════════════════════════════════════════════
# Maps attack payload patterns to MITRE ATT&CK technique IDs
MITRE_ATTACK_MAP: Dict[str, Dict[str, str]] = {
    "sqli": {
        "technique_id": "T1190",
        "technique_name": "Exploit Public-Facing Application",
        "tactic": "Initial Access",
        "sub_technique": "SQL Injection",
    },
    "xss": {
        "technique_id": "T1059.007",
        "technique_name": "JavaScript Execution",
        "tactic": "Execution",
        "sub_technique": "Cross-Site Scripting",
    },
    "cmdi": {
        "technique_id": "T1059",
        "technique_name": "Command and Scripting Interpreter",
        "tactic": "Execution",
        "sub_technique": "OS Command Injection",
    },
    "path_traversal": {
        "technique_id": "T1083",
        "technique_name": "File and Directory Discovery",
        "tactic": "Discovery",
        "sub_technique": "Path Traversal / LFI",
    },
    "lfi": {
        "technique_id": "T1005",
        "technique_name": "Data from Local System",
        "tactic": "Collection",
        "sub_technique": "Local File Inclusion",
    },
    "shellshock": {
        "technique_id": "T1190",
        "technique_name": "Exploit Public-Facing Application",
        "tactic": "Initial Access",
        "sub_technique": "Shellshock (CVE-2014-6271)",
    },
    "credential_stuffing": {
        "technique_id": "T1110.004",
        "technique_name": "Credential Stuffing",
        "tactic": "Credential Access",
        "sub_technique": "Brute Force: Credential Stuffing",
    },
    "c2_beacon": {
        "technique_id": "T1071",
        "technique_name": "Application Layer Protocol",
        "tactic": "Command and Control",
        "sub_technique": "C2 Callback / Beacon",
    },
    "exfiltration": {
        "technique_id": "T1041",
        "technique_name": "Exfiltration Over C2 Channel",
        "tactic": "Exfiltration",
        "sub_technique": "Data Exfiltration",
    },
    "reconnaissance": {
        "technique_id": "T1595",
        "technique_name": "Active Scanning",
        "tactic": "Reconnaissance",
        "sub_technique": "Vulnerability Scanning",
    },
}


# ═══════════════════════════════════════════════════════════════════
#  USER-AGENT FINGERPRINTING
# ═══════════════════════════════════════════════════════════════════
# Known attack tool user-agent signatures
KNOWN_ATTACK_TOOLS: Dict[str, Dict[str, str]] = {
    r"sqlmap": {"tool": "sqlmap", "category": "SQL Injection Scanner", "threat": "high"},
    r"nikto": {"tool": "Nikto", "category": "Web Vulnerability Scanner", "threat": "high"},
    r"nmap": {"tool": "Nmap", "category": "Port/Service Scanner", "threat": "medium"},
    r"dirbuster|gobuster|dirb": {"tool": "Directory Brute-Forcer", "category": "Path Discovery", "threat": "medium"},
    r"hydra": {"tool": "THC Hydra", "category": "Brute Force Tool", "threat": "critical"},
    r"burp\s*suite|burpcollaborator": {"tool": "Burp Suite", "category": "Web App Security Testing", "threat": "high"},
    r"metasploit|meterpreter": {"tool": "Metasploit", "category": "Exploitation Framework", "threat": "critical"},
    r"cobalt\s*strike|beacon": {"tool": "Cobalt Strike", "category": "C2 Framework", "threat": "critical"},
    r"w3af": {"tool": "w3af", "category": "Web App Scanner", "threat": "high"},
    r"masscan": {"tool": "Masscan", "category": "Mass Port Scanner", "threat": "high"},
    r"zgrab": {"tool": "ZGrab", "category": "Service Scanner", "threat": "medium"},
    r"censys|shodan": {"tool": "Internet Scanner", "category": "OSINT Scanner", "threat": "medium"},
    r"python-requests|python-urllib|aiohttp": {"tool": "Python Script", "category": "Scripted Attack", "threat": "medium"},
    r"curl/|wget/": {"tool": "cURL/wget", "category": "Command-Line Tool", "threat": "low"},
    r"scrapy|beautifulsoup": {"tool": "Web Scraper", "category": "Data Extraction", "threat": "low"},
}

# C2 domain patterns
C2_DOMAIN_PATTERNS = [
    r"\b[a-z0-9]{8,}\.(xyz|top|club|buzz|icu|tk|ml|ga|cf|gq)\b",  # Suspicious TLDs
    r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{4,5}\b",  # IP:high-port
    r"\b[a-f0-9]{32}\.[a-z]+\b",  # Hash-like subdomains
    r"(pastebin|hastebin|ghostbin|dpaste)\.(com|org)",  # Paste sites as C2
]


# ═══════════════════════════════════════════════════════════════════
#  IP INTELLIGENCE
# ═══════════════════════════════════════════════════════════════════
class IPIntelligence:
    """Local IP intelligence via reverse DNS and analysis."""

    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}

    def lookup(self, ip: str) -> Dict[str, Any]:
        """Perform local IP intelligence lookup."""
        if ip in self._cache:
            return self._cache[ip]

        intel: Dict[str, Any] = {
            "ip": ip,
            "hostname": "",
            "is_private": False,
            "is_loopback": False,
            "reverse_dns": "",
            "domain_indicators": [],
            "lookup_time": _utc_iso(),
        }

        # Check if private/loopback
        try:
            import ipaddress
            addr = ipaddress.IPv4Address(ip)
            intel["is_private"] = addr.is_private
            intel["is_loopback"] = addr.is_loopback
        except (ValueError, ImportError):
            pass

        # Reverse DNS
        try:
            hostname = socket.getfqdn(ip)
            if hostname and hostname != ip:
                intel["hostname"] = hostname
                intel["reverse_dns"] = hostname
                # Extract domain indicators
                parts = hostname.lower().split(".")
                if len(parts) >= 2:
                    tld = ".".join(parts[-2:])
                    intel["domain_indicators"].append(tld)
                    # Check for hosting indicators
                    hosting_keywords = ["amazonaws", "googleusercontent", "azure", "cloudflare",
                                         "digitalocean", "linode", "vultr", "ovh", "hetzner"]
                    for kw in hosting_keywords:
                        if kw in hostname.lower():
                            intel["hosting_provider"] = kw
        except (socket.herror, socket.gaierror, OSError):
            pass

        self._cache[ip] = intel
        return intel


# ═══════════════════════════════════════════════════════════════════
#  TTP PROFILER
# ═══════════════════════════════════════════════════════════════════
class TTPProfiler:
    """Classify attacker tactics, techniques, and procedures."""

    def __init__(self):
        self._tool_patterns = [(re.compile(p, re.IGNORECASE), info)
                               for p, info in KNOWN_ATTACK_TOOLS.items()]
        self._c2_patterns = [re.compile(p, re.IGNORECASE) for p in C2_DOMAIN_PATTERNS]

    def identify_tool(self, user_agent: str) -> Optional[Dict[str, str]]:
        """Identify attack tool from User-Agent string."""
        for pattern, info in self._tool_patterns:
            if pattern.search(user_agent):
                return dict(info)
        return None

    def map_technique(self, attack_category: str) -> Optional[Dict[str, str]]:
        """Map attack category to MITRE ATT&CK technique."""
        return MITRE_ATTACK_MAP.get(attack_category.lower())

    def detect_c2(self, payload: str) -> List[str]:
        """Detect C2 domain patterns in payloads."""
        c2_hits = []
        for pattern in self._c2_patterns:
            matches = pattern.findall(payload)
            if matches:
                c2_hits.extend(matches)
        return c2_hits

    def classify_cadence(self, timestamps: List[float]) -> Dict[str, Any]:
        """Classify attack cadence — automated vs human."""
        if len(timestamps) < 3:
            return {"cadence": "insufficient_data", "confidence": 0}

        intervals = [timestamps[i+1] - timestamps[i] for i in range(len(timestamps)-1)]
        avg_interval = sum(intervals) / len(intervals)
        variance = sum((i - avg_interval) ** 2 for i in intervals) / len(intervals)

        # Automated attacks have very consistent timing
        if variance < 0.1 and avg_interval < 1.0:
            return {"cadence": "automated_rapid", "confidence": 0.95,
                    "avg_interval_ms": round(avg_interval * 1000),
                    "tool_likely": "scanner/bot"}
        elif variance < 0.5:
            return {"cadence": "automated_steady", "confidence": 0.85,
                    "avg_interval_ms": round(avg_interval * 1000),
                    "tool_likely": "scripted_attack"}
        elif variance < 2.0:
            return {"cadence": "semi_automated", "confidence": 0.6,
                    "avg_interval_ms": round(avg_interval * 1000),
                    "tool_likely": "interactive_tool"}
        else:
            return {"cadence": "manual", "confidence": 0.7,
                    "avg_interval_ms": round(avg_interval * 1000),
                    "tool_likely": "human_operator"}


# ═══════════════════════════════════════════════════════════════════
#  RECON ENGINE
# ═══════════════════════════════════════════════════════════════════
class ReconEngine:
    """Orchestrates reconnaissance and threat attribution.

    All intelligence is gathered through local analysis of observed traffic.
    No external API calls are made.
    """

    def __init__(self, telemetry: Optional[Any] = None):
        self.telemetry = telemetry
        self.ip_intel = IPIntelligence()
        self.ttp_profiler = TTPProfiler()
        self._intel_reports: Dict[str, Dict[str, Any]] = {}
        self._attack_timestamps: Dict[str, List[float]] = {}
        self._lock = threading.Lock()

    def analyze(self, ip: str, user_agent: str = "",
                attack_category: str = "", payload: str = "") -> Dict[str, Any]:
        """Run full reconnaissance on an attacker.

        Args:
            ip: Attacker IP address
            user_agent: Attacker's User-Agent string
            attack_category: Type of attack detected
            payload: Captured attack payload

        Returns:
            Intelligence report with attribution data
        """
        with self._lock:
            # Track timestamps for cadence analysis
            if ip not in self._attack_timestamps:
                self._attack_timestamps[ip] = []
            self._attack_timestamps[ip].append(time.time())
            # Keep only last 100 timestamps
            self._attack_timestamps[ip] = self._attack_timestamps[ip][-100:]

        # 1. IP Intelligence
        ip_data = self.ip_intel.lookup(ip)

        # 2. Tool identification
        tool_info = self.ttp_profiler.identify_tool(user_agent) if user_agent else None

        # 3. MITRE ATT&CK mapping
        technique = self.ttp_profiler.map_technique(attack_category) if attack_category else None

        # 4. C2 detection
        c2_indicators = self.ttp_profiler.detect_c2(payload) if payload else []

        # 5. Cadence analysis
        timestamps = self._attack_timestamps.get(ip, [])
        cadence = self.ttp_profiler.classify_cadence(timestamps)

        # Build intel report
        report = {
            "ip": ip,
            "report_id": hashlib.sha256(f"recon-{ip}-{time.time()}".encode()).hexdigest()[:16],
            "ip_intelligence": ip_data,
            "attack_tool": tool_info,
            "mitre_technique": technique,
            "c2_indicators": c2_indicators[:5],
            "cadence_analysis": cadence,
            "total_attacks_from_ip": len(timestamps),
            "timestamp": _utc_iso(),
        }

        # Store report
        with self._lock:
            self._intel_reports[ip] = report

        # Emit telemetry
        if self.telemetry and _HAS_TELEMETRY and tool_info:
            event = SecurityEvent.create(
                source_zone=TrustZone.EXTERNAL,
                target_zone=TrustZone.CONTROL_PLANE,
                actor_identity=f"Attacker/{ip}",
                actor_type="external",
                event_type="recon_tool_identified",
                severity=tool_info.get("threat", "medium"),
                confidence=0.9,
                details={
                    "ip": ip, "tool": tool_info.get("tool"),
                    "category": tool_info.get("category"),
                    "technique": technique.get("technique_id") if technique else None,
                },
            )
            self.telemetry.record_event(event)

        return report

    def get_intel_reports(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            reports = sorted(
                self._intel_reports.values(),
                key=lambda r: r.get("total_attacks_from_ip", 0), reverse=True
            )
            return reports[:limit]

    def get_mitre_map(self) -> Dict[str, Dict[str, str]]:
        """Return the full MITRE ATT&CK mapping."""
        return dict(MITRE_ATTACK_MAP)

    def get_known_tools(self) -> List[Dict[str, str]]:
        """Return the known attack tool signatures."""
        tools = []
        for pattern_str, info in KNOWN_ATTACK_TOOLS.items():
            entry = dict(info)
            entry["pattern"] = pattern_str
            tools.append(entry)
        return tools

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            tools_detected = sum(1 for r in self._intel_reports.values() if r.get("attack_tool"))
            c2_detected = sum(1 for r in self._intel_reports.values() if r.get("c2_indicators"))
            return {
                "ips_analyzed": len(self._intel_reports),
                "attack_tools_detected": tools_detected,
                "c2_indicators_found": c2_detected,
                "mitre_techniques_mapped": len(MITRE_ATTACK_MAP),
                "known_tool_signatures": len(KNOWN_ATTACK_TOOLS),
                "c2_pattern_rules": len(C2_DOMAIN_PATTERNS),
            }
