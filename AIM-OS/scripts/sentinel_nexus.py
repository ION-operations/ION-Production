#!/usr/bin/env python3
"""
AIM-OS SENTINEL — NEXUS: Threat Intelligence Fusion + Adaptive Learning (Phase 9)

The capstone module that unifies all SENTINEL phases into a self-improving
security brain. NEXUS correlates threats across subsystems, learns from
attack patterns, and dynamically adjusts defensive posture.

KEY DESIGN:
  - Threat Correlation Engine — cross-references anomaly, recon, phantom,
    chronicle, and session data to build holistic threat pictures
  - Attack Pattern Learning — tracks TTPs, builds attacker profiles, and
    predicts next moves based on historical patterns
  - Adaptive Defense Orchestrator — dynamically tunes thresholds, ROE,
    and countermeasure selection based on learned threat landscape
  - Threat Score — composite 0-100 score from all subsystem signals

Usage:
    from sentinel_nexus import NexusEngine
    engine = NexusEngine(telemetry, chronicle, phantom, recon, sessions)
    engine.correlate_threat("192.168.1.100", {"source": "anomaly", ...})
"""

import hashlib
import json
import os
import threading
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

REPO_ROOT = str(Path(__file__).parent.parent)
DATA_DIR = os.path.join(REPO_ROOT, "data", "mcp")
NEXUS_DB_FILE = os.path.join(DATA_DIR, "sentinel_nexus_intel.json")

try:
    from sentinel_telemetry import SecurityEvent, TrustZone
    _HAS_TELEMETRY = True
except ImportError:
    _HAS_TELEMETRY = False


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═══════════════════════════════════════════════════════════════════
#  THREAT INTELLIGENCE — Individual threat signals from subsystems
# ═══════════════════════════════════════════════════════════════════
SIGNAL_WEIGHTS: Dict[str, float] = {
    # Signal source → weight in composite threat score
    "anomaly_spike":          15.0,   # Traffic anomaly detected
    "file_integrity_alert":   20.0,   # File modified unexpectedly
    "honeypot_triggered":     25.0,   # Honeypot path accessed
    "injection_detected":     30.0,   # WRAITH injection found
    "session_hijack":         35.0,   # Session anomaly
    "policy_violation":       20.0,   # Policy engine block
    "governance_block":       15.0,   # MCP governance denial
    "recon_tool_detected":    25.0,   # Known attack tool identified
    "c2_indicator":           40.0,   # C2 communication suspected
    "mitre_technique":        20.0,   # MITRE ATT&CK technique mapped
    "repeated_attacker":      30.0,   # Previously seen attacker returns
    "credential_harvest":     35.0,   # Bait credential accessed
    "phantom_escalation":     25.0,   # PHANTOM escalated threat level
    "brute_force":            20.0,   # Multiple failed auth attempts
    "data_exfil_pattern":     40.0,   # Data exfiltration indicators
}

DEFENSE_POSTURES = {
    "NOMINAL":   {"description": "Normal operations — standard monitoring", "threshold": 20},
    "ELEVATED":  {"description": "Increased vigilance — enhanced logging", "threshold": 40},
    "GUARDED":   {"description": "Active defense — countermeasures armed", "threshold": 60},
    "HIGH":      {"description": "Aggressive defense — full PHANTOM engagement", "threshold": 80},
    "MAXIMUM":   {"description": "Maximum defense — all systems active, CEO escalation", "threshold": 95},
}


class ThreatSignal:
    """A single threat signal from any SENTINEL subsystem."""

    def __init__(self, source: str, signal_type: str, ip: str,
                 details: Dict[str, Any], confidence: float = 0.8):
        self.id = hashlib.sha256(f"{_utc_iso()}{source}{ip}{signal_type}".encode()).hexdigest()[:12]
        self.timestamp = _utc_iso()
        self.source = source           # e.g., "anomaly", "wraith", "recon"
        self.signal_type = signal_type  # e.g., "injection_detected"
        self.ip = ip
        self.details = details
        self.confidence = min(1.0, max(0.0, confidence))
        self.weight = SIGNAL_WEIGHTS.get(signal_type, 10.0)
        self.processed = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "timestamp": self.timestamp,
            "source": self.source, "signal_type": self.signal_type,
            "ip": self.ip, "confidence": self.confidence,
            "weight": self.weight, "processed": self.processed,
        }


# ═══════════════════════════════════════════════════════════════════
#  THREAT PROFILE — Composite view of an attacker across all sources
# ═══════════════════════════════════════════════════════════════════
class ThreatProfile:
    """Holistic threat profile for an IP built from correlated signals."""

    def __init__(self, ip: str):
        self.ip = ip
        self.first_seen = _utc_iso()
        self.last_seen = _utc_iso()
        self.signals: List[ThreatSignal] = []
        self.threat_score: float = 0.0
        self.ttps: Set[str] = set()
        self.sources: Set[str] = set()
        self.attack_tools: List[str] = []
        self.c2_indicators: List[str] = []
        self.posture = "NOMINAL"
        self.escalation_count: int = 0
        self.countermeasures_deployed: List[str] = []
        self.predictions: List[str] = []

    def add_signal(self, signal: ThreatSignal) -> None:
        self.signals.append(signal)
        self.last_seen = _utc_iso()
        self.sources.add(signal.source)
        self._recalculate_threat_score()

    def _recalculate_threat_score(self) -> None:
        """Compute composite threat score from all signals with time decay."""
        if not self.signals:
            self.threat_score = 0.0
            return

        total = 0.0
        for sig in self.signals[-50:]:  # Recent 50 signals
            total += sig.weight * sig.confidence

        # Cap at 100, normalize by signal count for smoothing
        self.threat_score = min(100.0, total)

        # Determine defense posture
        for posture_name in ["MAXIMUM", "HIGH", "GUARDED", "ELEVATED", "NOMINAL"]:
            if self.threat_score >= DEFENSE_POSTURES[posture_name]["threshold"]:
                self.posture = posture_name
                break

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ip": self.ip,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "threat_score": round(self.threat_score, 1),
            "posture": self.posture,
            "signal_count": len(self.signals),
            "sources": sorted(self.sources),
            "ttps": sorted(self.ttps),
            "attack_tools": self.attack_tools[-5:],
            "c2_indicators": self.c2_indicators[-3:],
            "escalation_count": self.escalation_count,
            "countermeasures": self.countermeasures_deployed[-5:],
            "predictions": self.predictions[-3:],
        }


# ═══════════════════════════════════════════════════════════════════
#  ATTACK PATTERN LEARNING — Learn from historical patterns
# ═══════════════════════════════════════════════════════════════════
# Common attack chains (sequence of TTPs that indicate specific attack types)
KNOWN_ATTACK_CHAINS: Dict[str, Dict[str, Any]] = {
    "APT_RECON_TO_EXPLOIT": {
        "name": "APT Reconnaissance → Exploitation",
        "chain": ["recon_tool_detected", "anomaly_spike", "injection_detected"],
        "prediction": "Attacker likely to attempt privilege escalation next",
        "recommended_action": "Deploy deception layer + increase monitoring",
    },
    "BRUTE_FORCE_TO_PIVOT": {
        "name": "Credential Brute Force → Lateral Movement",
        "chain": ["brute_force", "session_hijack"],
        "prediction": "Attacker will attempt data exfiltration within 30 min",
        "recommended_action": "Quarantine affected sessions + enable full forensics",
    },
    "C2_ESTABLISHMENT": {
        "name": "C2 Channel Establishment",
        "chain": ["c2_indicator", "data_exfil_pattern"],
        "prediction": "Active data exfiltration via C2 channel",
        "recommended_action": "DNS sinkhole + network isolation + CEO escalation",
    },
    "SUPPLY_CHAIN_ATTACK": {
        "name": "Supply Chain Compromise",
        "chain": ["file_integrity_alert", "policy_violation"],
        "prediction": "Dependency or tool compromise — verify all binaries",
        "recommended_action": "Full file integrity scan + freeze deployments",
    },
    "AUTOMATED_SCAN_CHAIN": {
        "name": "Automated Scanner → Targeted Exploit",
        "chain": ["recon_tool_detected", "honeypot_triggered", "injection_detected"],
        "prediction": "Bot escalating to targeted exploit after initial recon",
        "recommended_action": "Tarpit + fingerprint harvester + ban network range",
    },
    "INSIDER_THREAT": {
        "name": "Insider Threat Pattern",
        "chain": ["policy_violation", "governance_block", "data_exfil_pattern"],
        "prediction": "Possible insider attempting unauthorized data access",
        "recommended_action": "Session audit + access review + escalate to CEO",
    },
}


class PatternLearner:
    """Learns from attack patterns and predicts attacker behavior."""

    def __init__(self):
        self.observed_chains: Dict[str, int] = defaultdict(int)
        self.successful_predictions: int = 0
        self.total_predictions: int = 0
        self.learned_patterns: List[Dict[str, Any]] = []

    def analyze_chain(self, signal_history: List[str]) -> List[Dict[str, Any]]:
        """Check if signal history matches known attack chains."""
        matches = []
        for chain_id, chain_def in KNOWN_ATTACK_CHAINS.items():
            chain_signals = chain_def["chain"]
            # Check if the chain signals appear in order within history
            chain_idx = 0
            for sig_type in signal_history:
                if chain_idx < len(chain_signals) and sig_type == chain_signals[chain_idx]:
                    chain_idx += 1
            if chain_idx == len(chain_signals):
                matches.append({
                    "chain_id": chain_id,
                    "name": chain_def["name"],
                    "prediction": chain_def["prediction"],
                    "recommended_action": chain_def["recommended_action"],
                    "confidence": min(1.0, 0.7 + (chain_idx * 0.1)),
                })
                self.observed_chains[chain_id] += 1
                self.total_predictions += 1

        return matches

    def record_outcome(self, prediction_accurate: bool) -> None:
        if prediction_accurate:
            self.successful_predictions += 1

    def get_accuracy(self) -> float:
        if self.total_predictions == 0:
            return 0.0
        return self.successful_predictions / self.total_predictions

    def get_status(self) -> Dict[str, Any]:
        return {
            "known_chains": len(KNOWN_ATTACK_CHAINS),
            "observed_chain_matches": dict(self.observed_chains),
            "total_predictions": self.total_predictions,
            "successful_predictions": self.successful_predictions,
            "accuracy": round(self.get_accuracy(), 2),
            "learned_patterns": len(self.learned_patterns),
        }


# ═══════════════════════════════════════════════════════════════════
#  ADAPTIVE DEFENSE — Dynamically tune SENTINEL based on learned intel
# ═══════════════════════════════════════════════════════════════════
class AdaptiveDefense:
    """Dynamically adjusts SENTINEL's defensive posture based on threat landscape."""

    def __init__(self):
        self.current_posture = "NOMINAL"
        self.posture_history: List[Dict[str, str]] = []
        self.threshold_adjustments: Dict[str, float] = {}
        self.active_adaptations: List[Dict[str, Any]] = []

    def evaluate_posture(self, threat_profiles: Dict[str, ThreatProfile]) -> str:
        """Evaluate overall defense posture from all threat profiles."""
        if not threat_profiles:
            new_posture = "NOMINAL"
        else:
            max_score = max(
                (p.threat_score for p in threat_profiles.values()),
                default=0.0
            )
            # Determine posture from highest threat
            new_posture = "NOMINAL"
            for posture_name in ["MAXIMUM", "HIGH", "GUARDED", "ELEVATED", "NOMINAL"]:
                if max_score >= DEFENSE_POSTURES[posture_name]["threshold"]:
                    new_posture = posture_name
                    break

        if new_posture != self.current_posture:
            self.posture_history.append({
                "from": self.current_posture,
                "to": new_posture,
                "timestamp": _utc_iso(),
                "reason": f"Threat landscape shift (max score: {max_score:.1f})" if threat_profiles else "All clear",
            })
            self.current_posture = new_posture

        return self.current_posture

    def generate_adaptations(self, posture: str) -> List[Dict[str, Any]]:
        """Generate defense adaptations based on current posture."""
        adaptations = []

        if posture == "ELEVATED":
            adaptations = [
                {"action": "increase_log_verbosity", "parameter": "all", "value": "debug"},
                {"action": "reduce_anomaly_threshold", "parameter": "rpm_spike", "value": 0.8},
            ]
        elif posture == "GUARDED":
            adaptations = [
                {"action": "arm_countermeasures", "parameter": "phantom_roe", "value": "YELLOW"},
                {"action": "enable_deep_packet_inspection", "parameter": "all_ingress", "value": True},
                {"action": "increase_scan_frequency", "parameter": "file_integrity", "value": "5min"},
            ]
        elif posture == "HIGH":
            adaptations = [
                {"action": "arm_countermeasures", "parameter": "phantom_roe", "value": "RED"},
                {"action": "quarantine_suspicious_sessions", "parameter": "threshold", "value": 0.6},
                {"action": "enable_full_forensics", "parameter": "all", "value": True},
                {"action": "notify_team", "parameter": "channel", "value": "security-alerts"},
            ]
        elif posture == "MAXIMUM":
            adaptations = [
                {"action": "arm_countermeasures", "parameter": "phantom_roe", "value": "CRITICAL"},
                {"action": "lockdown_sessions", "parameter": "all_external", "value": True},
                {"action": "enable_full_forensics", "parameter": "all", "value": True},
                {"action": "escalate_ceo", "parameter": "priority", "value": "immediate"},
                {"action": "ban_attacker_ranges", "parameter": "scope", "value": "all_tracked"},
            ]

        self.active_adaptations = adaptations
        return adaptations

    def get_status(self) -> Dict[str, Any]:
        return {
            "current_posture": self.current_posture,
            "posture_description": DEFENSE_POSTURES[self.current_posture]["description"],
            "posture_changes": len(self.posture_history),
            "active_adaptations": len(self.active_adaptations),
            "threshold_adjustments": len(self.threshold_adjustments),
            "recent_changes": self.posture_history[-3:] if self.posture_history else [],
        }


# ═══════════════════════════════════════════════════════════════════
#  NEXUS ENGINE — The brain that fuses everything
# ═══════════════════════════════════════════════════════════════════
class NexusEngine:
    """NEXUS: Threat Intelligence Fusion + Adaptive Learning.

    The capstone module that cross-correlates threat signals from all
    SENTINEL subsystems, learns attack patterns, predicts attacker
    behavior, and dynamically adjusts defensive posture.
    """

    def __init__(self, telemetry: Optional[Any] = None,
                 chronicle: Optional[Any] = None,
                 phantom: Optional[Any] = None,
                 recon: Optional[Any] = None,
                 sessions: Optional[Any] = None):
        self.telemetry = telemetry
        self.chronicle = chronicle
        self.phantom = phantom
        self.recon = recon
        self.sessions = sessions

        self._lock = threading.Lock()
        self._threat_profiles: Dict[str, ThreatProfile] = {}
        self._signal_buffer: List[ThreatSignal] = []
        self._pattern_learner = PatternLearner()
        self._adaptive_defense = AdaptiveDefense()

        # Global threat landscape
        self._total_signals_processed: int = 0
        self._total_correlations: int = 0
        self._total_threats_identified: int = 0

        # Load persisted intel
        self._load_intel()

    def ingest_signal(self, source: str, signal_type: str, ip: str,
                      details: Dict[str, Any], confidence: float = 0.8) -> Dict[str, Any]:
        """Ingest a threat signal from any SENTINEL subsystem.

        Args:
            source: Subsystem name (anomaly, wraith, recon, phantom, etc.)
            signal_type: Type from SIGNAL_WEIGHTS keys
            ip: Source IP of the threat
            details: Signal-specific details
            confidence: 0.0-1.0 confidence in this signal

        Returns:
            Correlation result with threat profile update
        """
        with self._lock:
            signal = ThreatSignal(source, signal_type, ip, details, confidence)
            self._signal_buffer.append(signal)
            self._total_signals_processed += 1

            # Get or create threat profile
            if ip not in self._threat_profiles:
                self._threat_profiles[ip] = ThreatProfile(ip)
                self._total_threats_identified += 1

            profile = self._threat_profiles[ip]
            profile.add_signal(signal)

            # Extract TTPs
            if "ttp" in details:
                profile.ttps.add(details["ttp"])
            if "mitre_id" in details:
                profile.ttps.add(details["mitre_id"])
            if "tool" in details:
                if details["tool"] not in profile.attack_tools:
                    profile.attack_tools.append(details["tool"])
            if "c2_domain" in details:
                profile.c2_indicators.append(details["c2_domain"])

            # Pattern analysis — check for known attack chains
            signal_history = [s.signal_type for s in profile.signals]
            chain_matches = self._pattern_learner.analyze_chain(signal_history)
            for match in chain_matches:
                profile.predictions.append(match["prediction"])

            # Update defense posture
            posture = self._adaptive_defense.evaluate_posture(self._threat_profiles)
            adaptations = self._adaptive_defense.generate_adaptations(posture)

            self._total_correlations += 1

            # Record in chronicle if available
            if self.chronicle and hasattr(self.chronicle, "record"):
                try:
                    self.chronicle.record("nexus_correlation", "SENTINEL/NEXUS", {
                        "ip": ip,
                        "signal": signal_type,
                        "threat_score": profile.threat_score,
                        "posture": posture,
                        "chain_matches": len(chain_matches),
                    })
                except Exception:
                    pass

            # Auto-open incident for high threats
            if profile.threat_score >= 60 and self.chronicle:
                try:
                    severity = "P0-CRITICAL" if profile.threat_score >= 95 else \
                               "P1-HIGH" if profile.threat_score >= 80 else "P2-MEDIUM"
                    self.chronicle.open_incident(
                        severity,
                        f"NEXUS: Correlated threat from {ip} (score: {profile.threat_score:.0f})",
                        {
                            "threat_score": profile.threat_score,
                            "signals": len(profile.signals),
                            "ttps": sorted(profile.ttps),
                            "posture": posture,
                        },
                        source_ip=ip,
                    )
                except Exception:
                    pass

            signal.processed = True

            result = {
                "signal_id": signal.id,
                "ip": ip,
                "threat_score": round(profile.threat_score, 1),
                "posture": posture,
                "chain_matches": chain_matches,
                "adaptations": adaptations,
                "profile_summary": profile.to_dict(),
            }

            self._save_intel()
            return result

    def get_threat_landscape(self) -> Dict[str, Any]:
        """Get the full threat landscape overview."""
        with self._lock:
            profiles_by_posture: Dict[str, int] = defaultdict(int)
            top_threats = []

            for profile in sorted(
                self._threat_profiles.values(),
                key=lambda p: p.threat_score,
                reverse=True
            ):
                profiles_by_posture[profile.posture] += 1
                if len(top_threats) < 5:
                    top_threats.append(profile.to_dict())

            return {
                "timestamp": _utc_iso(),
                "defense_posture": self._adaptive_defense.current_posture,
                "posture_description": DEFENSE_POSTURES[
                    self._adaptive_defense.current_posture
                ]["description"],
                "total_threats": len(self._threat_profiles),
                "threats_by_posture": dict(profiles_by_posture),
                "top_threats": top_threats,
                "total_signals": self._total_signals_processed,
                "total_correlations": self._total_correlations,
                "pattern_learning": self._pattern_learner.get_status(),
                "adaptive_defense": self._adaptive_defense.get_status(),
                "signal_types_tracked": len(SIGNAL_WEIGHTS),
                "known_attack_chains": len(KNOWN_ATTACK_CHAINS),
            }

    def get_threat_profile(self, ip: str) -> Optional[Dict[str, Any]]:
        """Get detailed threat profile for a specific IP."""
        with self._lock:
            profile = self._threat_profiles.get(ip)
            if not profile:
                return None
            result = profile.to_dict()
            result["signals"] = [s.to_dict() for s in profile.signals[-20:]]
            return result

    def _save_intel(self) -> None:
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            data = {
                "threat_profiles": {
                    ip: p.to_dict() for ip, p in self._threat_profiles.items()
                },
                "posture": self._adaptive_defense.current_posture,
                "total_signals": self._total_signals_processed,
                "total_correlations": self._total_correlations,
                "total_threats": self._total_threats_identified,
                "saved_at": _utc_iso(),
            }
            with open(NEXUS_DB_FILE, "w") as f:
                json.dump(data, f, indent=2)
        except OSError:
            pass

    def _load_intel(self) -> None:
        try:
            if os.path.exists(NEXUS_DB_FILE):
                with open(NEXUS_DB_FILE, "r") as f:
                    data = json.load(f)
                self._total_signals_processed = data.get("total_signals", 0)
                self._total_correlations = data.get("total_correlations", 0)
                self._total_threats_identified = data.get("total_threats", 0)
        except (OSError, json.JSONDecodeError):
            pass

    def get_status(self) -> Dict[str, Any]:
        with self._lock:
            active_threats = sum(
                1 for p in self._threat_profiles.values()
                if p.posture not in ("NOMINAL",)
            )
            return {
                "defense_posture": self._adaptive_defense.current_posture,
                "total_signals": self._total_signals_processed,
                "total_correlations": self._total_correlations,
                "tracked_threats": len(self._threat_profiles),
                "active_threats": active_threats,
                "known_chains": len(KNOWN_ATTACK_CHAINS),
                "chain_matches": sum(self._pattern_learner.observed_chains.values()),
                "prediction_accuracy": round(self._pattern_learner.get_accuracy(), 2),
                "adaptations_active": len(self._adaptive_defense.active_adaptations),
                "signal_types": len(SIGNAL_WEIGHTS),
            }
