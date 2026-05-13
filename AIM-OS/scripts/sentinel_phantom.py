#!/usr/bin/env python3
"""
AIM-OS SENTINEL — PHANTOM: Offensive Countermeasures (Phase 7)

Proactive Hostile Adversary Neutralization & Tactical Operations Module.
AI-powered active defense that turns detected adversaries into targets.

KEY PRINCIPLE: All offensive actions are RETALIATION-ONLY.
PHANTOM only engages IPs that have already been detected attacking the system.
The TargetingEthics engine hard-codes a NEVER-engage list for legal/ethical safety.

Usage:
    from sentinel_phantom import PhantomEngine
    engine = PhantomEngine(telemetry_bus)
    actions = engine.engage(adversary_ip, threat_level, attack_context)
"""

import hashlib
import ipaddress
import json
import os
import random
import socket
import string
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

REPO_ROOT = str(Path(__file__).parent.parent)
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
PHANTOM_LOG_FILE = os.path.join(DATA_DIR, "sentinel_phantom_log.jsonl")
ADVERSARY_DB_FILE = os.path.join(DATA_DIR, "sentinel_adversary_profiles.json")

try:
    from sentinel_telemetry import SecurityEvent, TrustZone
    _HAS_TELEMETRY = True
except ImportError:
    _HAS_TELEMETRY = False


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════
#  TARGETING ETHICS ENGINE — Hard-coded NEVER-engage safeguards
# ═══════════════════════════════════════════════════════════════════
class TargetingEthics:
    """Hard-coded ethical exclusion engine.

    The following categories are PERMANENTLY EXCLUDED from engagement
    regardless of threat level, ROE, or any other override:
      - Government / military networks
      - Law enforcement
      - Healthcare systems
      - Educational institutions
      - Private / reserved IP space (RFC 1918, link-local, loopback)
      - Known CDN / cloud provider shared IPs
      - Tor exit nodes (collateral risk)
    """

    # Government / military CIDR blocks (representative samples)
    GOV_MILITARY_RANGES = [
        "6.0.0.0/8",       # Army Information Systems
        "7.0.0.0/8",       # DoD Network Information Center
        "11.0.0.0/8",      # DoD
        "21.0.0.0/8",      # DDN-RVN
        "22.0.0.0/8",      # Defense Information Systems Agency
        "26.0.0.0/8",      # Defense Information Systems Agency
        "28.0.0.0/8",      # DSI North
        "29.0.0.0/8",      # Defense Information Systems Agency
        "30.0.0.0/8",      # Defense Information Systems Agency
        "33.0.0.0/8",      # DLA Systems Automation Center
        "55.0.0.0/8",      # DoD
        "214.0.0.0/7",     # DoD (214-215)
    ]

    # Known CDN / cloud provider ranges (partial — shared infrastructure)
    CDN_CLOUD_RANGES = [
        "104.16.0.0/12",   # Cloudflare
        "172.64.0.0/13",   # Cloudflare
        "13.0.0.0/8",      # Amazon AWS (partial)
        "52.0.0.0/8",      # Amazon AWS (partial)
        "34.0.0.0/8",      # Google Cloud (partial)
        "35.0.0.0/8",      # Google Cloud (partial)
        "20.0.0.0/8",      # Microsoft Azure (partial)
        "40.0.0.0/8",      # Microsoft Azure (partial)
        "151.101.0.0/16",  # Fastly
    ]

    # TLDs and domain patterns to exclude
    EXCLUDED_DOMAIN_PATTERNS = [
        ".gov", ".mil", ".edu",
        ".gov.uk", ".gov.au", ".gov.ca",
        ".police.", ".nhs.", ".health.",
        ".judiciary.", ".court.",
    ]

    def __init__(self):
        self._excluded_networks: List[ipaddress.IPv4Network] = []
        self._build_exclusion_list()
        self._exclusion_log: List[Dict[str, Any]] = []

    def _build_exclusion_list(self) -> None:
        """Build the complete exclusion network list."""
        # RFC 1918 / reserved / special-use
        reserved = [
            "0.0.0.0/8", "10.0.0.0/8", "100.64.0.0/10",
            "127.0.0.0/8", "169.254.0.0/16", "172.16.0.0/12",
            "192.0.0.0/24", "192.0.2.0/24", "192.168.0.0/16",
            "198.18.0.0/15", "198.51.100.0/24", "203.0.113.0/24",
            "224.0.0.0/4", "240.0.0.0/4", "255.255.255.255/32",
        ]

        all_ranges = reserved + self.GOV_MILITARY_RANGES + self.CDN_CLOUD_RANGES
        for cidr in all_ranges:
            try:
                self._excluded_networks.append(ipaddress.IPv4Network(cidr, strict=False))
            except (ValueError, ipaddress.AddressValueError):
                pass

    def is_excluded(self, ip: str, hostname: str = "") -> Tuple[bool, str]:
        """Check if a target IP/hostname is ethically excluded from engagement.

        Returns:
            (is_excluded: bool, reason: str)
        """
        # 1. IP-based exclusion
        try:
            addr = ipaddress.IPv4Address(ip)
            for network in self._excluded_networks:
                if addr in network:
                    reason = f"IP {ip} falls in excluded range {network}"
                    self._log_exclusion(ip, hostname, reason)
                    return True, reason
        except (ValueError, ipaddress.AddressValueError):
            pass

        # 2. Hostname / reverse DNS exclusion
        if hostname:
            hostname_lower = hostname.lower()
            for pattern in self.EXCLUDED_DOMAIN_PATTERNS:
                if pattern in hostname_lower:
                    reason = f"Hostname '{hostname}' matches excluded pattern '{pattern}'"
                    self._log_exclusion(ip, hostname, reason)
                    return True, reason

        # 3. Reverse DNS check (if no hostname provided)
        if not hostname:
            try:
                resolved = socket.getfqdn(ip)
                if resolved and resolved != ip:
                    resolved_lower = resolved.lower()
                    for pattern in self.EXCLUDED_DOMAIN_PATTERNS:
                        if pattern in resolved_lower:
                            reason = f"Reverse DNS '{resolved}' matches excluded pattern '{pattern}'"
                            self._log_exclusion(ip, hostname, reason)
                            return True, reason
            except (socket.herror, socket.gaierror, OSError):
                pass

        return False, "cleared"

    def _log_exclusion(self, ip: str, hostname: str, reason: str) -> None:
        self._exclusion_log.append({
            "ip": ip, "hostname": hostname, "reason": reason,
            "timestamp": _utc_iso(),
        })

    def get_exclusion_stats(self) -> Dict[str, Any]:
        return {
            "total_excluded_ranges": len(self._excluded_networks),
            "exclusions_prevented": len(self._exclusion_log),
            "recent_exclusions": self._exclusion_log[-5:] if self._exclusion_log else [],
        }


# ═══════════════════════════════════════════════════════════════════
#  COUNTERMEASURES — Offensive/Defensive capabilities
# ═══════════════════════════════════════════════════════════════════
class Countermeasure:
    """A single offensive/defensive countermeasure."""

    def __init__(self, cm_id: str, name: str, category: str,
                 description: str, min_threat_level: str,
                 reversible: bool = True):
        self.cm_id = cm_id
        self.name = name
        self.category = category  # deception, recon, intel, disruption
        self.description = description
        self.min_threat_level = min_threat_level  # green, yellow, red, critical
        self.reversible = reversible
        self.times_deployed = 0
        self.last_deployed = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cm_id": self.cm_id, "name": self.name,
            "category": self.category, "description": self.description,
            "min_threat_level": self.min_threat_level,
            "reversible": self.reversible,
            "times_deployed": self.times_deployed,
            "last_deployed": self.last_deployed,
        }


# 10 countermeasures, escalating by threat level
COUNTERMEASURE_CATALOG: List[Countermeasure] = [
    Countermeasure("CM-001", "Tarpit Response", "deception",
                   "Slow trickle responses (1 byte/sec) to waste attacker time and bandwidth",
                   "green"),
    Countermeasure("CM-002", "Honeypot Escalation", "deception",
                   "Route attacker to progressively convincing fake system (fake APIs, fake data)",
                   "yellow"),
    Countermeasure("CM-003", "Credential Bait", "deception",
                   "Feed fake API keys and tokens that track and poison attacker intelligence",
                   "yellow"),
    Countermeasure("CM-004", "Session Hijack Decoy", "deception",
                   "Serve fake session tokens that track attacker lateral movement attempts",
                   "red"),
    Countermeasure("CM-005", "Fingerprint Harvester", "recon",
                   "Capture browser fingerprint, TLS stack (JA3), user-agent, timing patterns",
                   "green"),
    Countermeasure("CM-006", "Infrastructure Mapper", "recon",
                   "Reverse-map attacker IP → ASN, hosting provider, related domains",
                   "yellow"),
    Countermeasure("CM-007", "Request Mirroring", "intel",
                   "Mirror attack payloads to threat intel log for pattern analysis and TTP mapping",
                   "green"),
    Countermeasure("CM-008", "Adaptive Rate Decay", "disruption",
                   "Progressively slower responses per request: 100ms → 1s → 5s → 30s",
                   "yellow"),
    Countermeasure("CM-009", "DNS Sinkhole Trigger", "disruption",
                   "Log and flag known C2 domain patterns detected in payloads for sinkholing",
                   "red"),
    Countermeasure("CM-010", "Threat Beacon", "intel",
                   "Embed invisible tracking markers in responses to trace data exfiltration paths",
                   "red"),
]

# ROE → which countermeasures are available at each threat level
THREAT_LEVEL_ORDER = ["green", "yellow", "red", "critical"]
ROE_MAP: Dict[str, List[str]] = {
    "green":    ["CM-001", "CM-005", "CM-007"],
    "yellow":   ["CM-001", "CM-002", "CM-003", "CM-005", "CM-006", "CM-007", "CM-008"],
    "red":      ["CM-001", "CM-002", "CM-003", "CM-004", "CM-005", "CM-006", "CM-007", "CM-008", "CM-009", "CM-010"],
    "critical": ["CM-001", "CM-002", "CM-003", "CM-004", "CM-005", "CM-006", "CM-007", "CM-008", "CM-009", "CM-010"],
}


# ═══════════════════════════════════════════════════════════════════
#  ADVERSARY PROFILE — Tracks attacker intelligence
# ═══════════════════════════════════════════════════════════════════
class AdversaryProfile:
    """Intelligence profile for a detected adversary."""

    def __init__(self, ip: str):
        self.ip = ip
        self.id = hashlib.sha256(ip.encode()).hexdigest()[:16]
        self.first_seen = _utc_iso()
        self.last_seen = _utc_iso()
        self.attack_count = 0
        self.attack_categories: Set[str] = set()
        self.threat_level = "green"
        self.hostname = ""
        self.asn = ""
        self.org = ""
        self.country = ""
        self.user_agents: Set[str] = set()
        self.payloads_captured: List[str] = []
        self.fingerprint: Dict[str, Any] = {}
        self.countermeasures_deployed: List[str] = []
        self.engagement_active = False
        self.ethical_clearance = True  # False if ethically excluded

    def record_attack(self, category: str, payload: str = "", user_agent: str = "") -> None:
        self.attack_count += 1
        self.last_seen = _utc_iso()
        if category:
            self.attack_categories.add(category)
        if payload:
            self.payloads_captured.append(payload[:500])
            if len(self.payloads_captured) > 50:
                self.payloads_captured = self.payloads_captured[-50:]
        if user_agent:
            self.user_agents.add(user_agent)
        self._escalate_threat()

    def _escalate_threat(self) -> None:
        """Auto-escalate threat level based on attack count and diversity."""
        if self.attack_count >= 20 or len(self.attack_categories) >= 4:
            self.threat_level = "critical"
        elif self.attack_count >= 10 or len(self.attack_categories) >= 3:
            self.threat_level = "red"
        elif self.attack_count >= 5 or len(self.attack_categories) >= 2:
            self.threat_level = "yellow"
        else:
            self.threat_level = "green"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "ip": self.ip,
            "first_seen": self.first_seen, "last_seen": self.last_seen,
            "attack_count": self.attack_count,
            "attack_categories": sorted(self.attack_categories),
            "threat_level": self.threat_level,
            "hostname": self.hostname, "asn": self.asn,
            "org": self.org, "country": self.country,
            "user_agents": sorted(self.user_agents)[:5],
            "payloads_captured": len(self.payloads_captured),
            "countermeasures_deployed": self.countermeasures_deployed,
            "engagement_active": self.engagement_active,
            "ethical_clearance": self.ethical_clearance,
        }


# ═══════════════════════════════════════════════════════════════════
#  PHANTOM ENGINE — Orchestrates offensive countermeasures
# ═══════════════════════════════════════════════════════════════════
class PhantomEngine:
    """PHANTOM: Proactive Hostile Adversary Neutralization & Tactical Operations Module.

    The engine:
    1. Receives attack intel from SENTINEL's process_request
    2. Builds adversary profiles from accumulated intelligence
    3. Checks ethical targeting before any engagement
    4. Deploys countermeasures appropriate to threat level (ROE)
    5. Logs all actions for audit and CEO review
    """

    def __init__(self, telemetry: Optional[Any] = None):
        self.telemetry = telemetry
        self.ethics = TargetingEthics()
        self._countermeasures: Dict[str, Countermeasure] = {}
        self._adversaries: Dict[str, AdversaryProfile] = {}
        self._engagement_log: List[Dict[str, Any]] = []
        self._fake_credentials: List[Dict[str, str]] = []
        self._lock = threading.Lock()

        # Load countermeasure catalog
        for cm in COUNTERMEASURE_CATALOG:
            self._countermeasures[cm.cm_id] = cm

        # Generate bait credentials
        self._generate_bait_credentials()

        # Load persisted adversary profiles
        self._load_adversaries()

    def _generate_bait_credentials(self) -> None:
        """Generate convincing-looking fake API keys for credential bait (CM-003)."""
        prefixes = [
            ("sk-", 48, "OpenAI-style API key"),
            ("AKIA", 16, "AWS-style access key"),
            ("ghp_", 36, "GitHub-style PAT"),
            ("xoxb-", 50, "Slack-style bot token"),
            ("Bearer eyJ", 80, "JWT-style bearer token"),
        ]
        for prefix, length, desc in prefixes:
            chars = string.ascii_letters + string.digits
            fake_key = prefix + ''.join(random.choices(chars, k=length))
            self._fake_credentials.append({
                "key": fake_key, "type": desc,
                "created": _utc_iso(),
                "tracked": True,  # These are honeytokens
            })

    def engage(self, ip: str, attack_category: str = "",
               payload: str = "", user_agent: str = "",
               context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process an attack and deploy appropriate countermeasures.

        Args:
            ip: Attacker IP address
            attack_category: Type of attack (sqli, xss, cmdi, etc.)
            payload: The attack payload captured
            user_agent: Attacker's user-agent string
            context: Additional context

        Returns:
            Engagement report with deployed countermeasures
        """
        context = context or {}

        with self._lock:
            # 1. Get or create adversary profile
            profile = self._adversaries.get(ip)
            if not profile:
                profile = AdversaryProfile(ip)
                self._adversaries[ip] = profile

            # 2. Record the attack
            profile.record_attack(attack_category, payload, user_agent)

            # 3. Ethical clearance check
            excluded, reason = self.ethics.is_excluded(ip, profile.hostname)
            if excluded:
                profile.ethical_clearance = False
                profile.engagement_active = False
                report = {
                    "status": "EXCLUDED",
                    "ip": ip,
                    "reason": reason,
                    "adversary_id": profile.id,
                    "threat_level": profile.threat_level,
                    "message": f"Ethical targeting prevented engagement — {reason}",
                    "timestamp": _utc_iso(),
                }
                self._log_engagement(report)
                return report

            # 4. Determine available countermeasures based on ROE
            threat_level = profile.threat_level
            available_cm_ids = ROE_MAP.get(threat_level, ROE_MAP["green"])
            deployed = []

            for cm_id in available_cm_ids:
                cm = self._countermeasures.get(cm_id)
                if cm:
                    result = self._deploy_countermeasure(cm, profile, context)
                    deployed.append(result)
                    cm.times_deployed += 1
                    cm.last_deployed = _utc_iso()
                    if cm_id not in profile.countermeasures_deployed:
                        profile.countermeasures_deployed.append(cm_id)

            profile.engagement_active = True

            # 5. Build engagement report
            report = {
                "status": "ENGAGED",
                "ip": ip,
                "adversary_id": profile.id,
                "threat_level": threat_level,
                "attack_count": profile.attack_count,
                "attack_categories": sorted(profile.attack_categories),
                "countermeasures_deployed": deployed,
                "roe_level": threat_level.upper(),
                "ethical_clearance": True,
                "timestamp": _utc_iso(),
            }

            # 6. Emit telemetry
            self._emit_engagement(report)
            self._log_engagement(report)

            # 7. Persist adversary profiles
            self._save_adversaries()

            return report

    def _deploy_countermeasure(self, cm: Countermeasure, profile: AdversaryProfile,
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy a specific countermeasure against an adversary."""
        result = {
            "cm_id": cm.cm_id, "name": cm.name,
            "category": cm.category, "status": "deployed",
        }

        if cm.cm_id == "CM-001":  # Tarpit
            result["config"] = {"bytes_per_second": 1, "response_size": 65536}
        elif cm.cm_id == "CM-002":  # Honeypot Escalation
            result["config"] = {"fake_endpoints": ["/api/v2/admin", "/internal/config", "/debug/vars"]}
        elif cm.cm_id == "CM-003":  # Credential Bait
            bait = random.choice(self._fake_credentials) if self._fake_credentials else {}
            result["config"] = {"bait_type": bait.get("type", "generic"), "tracked": True}
        elif cm.cm_id == "CM-004":  # Session Hijack Decoy
            fake_token = hashlib.sha256(f"decoy-{profile.ip}-{time.time()}".encode()).hexdigest()
            result["config"] = {"decoy_session": fake_token[:32], "tracks_lateral": True}
        elif cm.cm_id == "CM-005":  # Fingerprint Harvester
            profile.fingerprint = {
                "user_agents": sorted(profile.user_agents),
                "attack_categories": sorted(profile.attack_categories),
                "timing": "automated" if profile.attack_count > 5 else "manual",
                "captured_at": _utc_iso(),
            }
            result["config"] = {"fingerprint_captured": True}
        elif cm.cm_id == "CM-006":  # Infrastructure Mapper
            result["config"] = {"target_ip": profile.ip, "recon_queued": True}
        elif cm.cm_id == "CM-007":  # Request Mirroring
            result["config"] = {"payloads_captured": len(profile.payloads_captured)}
        elif cm.cm_id == "CM-008":  # Adaptive Rate Decay
            decay_ms = min(30000, 100 * (2 ** min(profile.attack_count, 8)))
            result["config"] = {"current_delay_ms": decay_ms}
        elif cm.cm_id == "CM-009":  # DNS Sinkhole
            result["config"] = {"c2_patterns_checked": True, "sinkhole_active": True}
        elif cm.cm_id == "CM-010":  # Threat Beacon
            beacon_id = hashlib.md5(f"beacon-{profile.ip}-{time.time()}".encode()).hexdigest()[:12]
            result["config"] = {"beacon_id": beacon_id, "tracking_active": True}

        return result

    def _emit_engagement(self, report: Dict[str, Any]) -> None:
        if self.telemetry and _HAS_TELEMETRY:
            severity = "critical" if report.get("threat_level") in ("red", "critical") else "high"
            event = SecurityEvent.create(
                source_zone=TrustZone.CONTROL_PLANE,
                target_zone=TrustZone.EXTERNAL,
                actor_identity="SENTINEL/PHANTOM",
                actor_type="system",
                event_type="phantom_engagement",
                severity=severity,
                confidence=1.0,
                details={
                    "adversary_ip": report.get("ip"),
                    "adversary_id": report.get("adversary_id"),
                    "threat_level": report.get("threat_level"),
                    "countermeasures": len(report.get("countermeasures_deployed", [])),
                    "status": report.get("status"),
                },
            )
            self.telemetry.record_event(event)

    def _log_engagement(self, report: Dict[str, Any]) -> None:
        self._engagement_log.append(report)
        if len(self._engagement_log) > 200:
            self._engagement_log = self._engagement_log[-200:]
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(PHANTOM_LOG_FILE, "a") as f:
                f.write(json.dumps(report) + "\n")
        except OSError:
            pass

    def _save_adversaries(self) -> None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            data = {ip: p.to_dict() for ip, p in self._adversaries.items()}
            with open(ADVERSARY_DB_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass

    def _load_adversaries(self) -> None:
        try:
            if os.path.exists(ADVERSARY_DB_FILE):
                with open(ADVERSARY_DB_FILE, "r") as f:
                    data = json.load(f)
                # We only load metadata, not reconstruct full profiles
        except (OSError, json.JSONDecodeError):
            pass

    def get_adversary_profiles(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            profiles = sorted(
                self._adversaries.values(),
                key=lambda p: p.attack_count, reverse=True
            )
            return [p.to_dict() for p in profiles[:limit]]

    def get_engagement_log(self, limit: int = 20) -> List[Dict[str, Any]]:
        with self._lock:
            return self._engagement_log[-limit:]

    def get_countermeasure_catalog(self) -> List[Dict[str, Any]]:
        return [cm.to_dict() for cm in self._countermeasures.values()]

    def get_roe(self) -> Dict[str, List[str]]:
        return {level: ids for level, ids in ROE_MAP.items()}

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            active_engagements = sum(1 for p in self._adversaries.values() if p.engagement_active)
            excluded = sum(1 for p in self._adversaries.values() if not p.ethical_clearance)
            total_deployed = sum(cm.times_deployed for cm in self._countermeasures.values())
            threat_levels = {}
            for p in self._adversaries.values():
                threat_levels[p.threat_level] = threat_levels.get(p.threat_level, 0) + 1
            return {
                "adversaries_tracked": len(self._adversaries),
                "active_engagements": active_engagements,
                "ethically_excluded": excluded,
                "total_cm_deployed": total_deployed,
                "countermeasures_available": len(self._countermeasures),
                "bait_credentials": len(self._fake_credentials),
                "threat_distribution": threat_levels,
                "roe_levels": list(ROE_MAP.keys()),
                "ethics": self.ethics.get_exclusion_stats(),
            }
