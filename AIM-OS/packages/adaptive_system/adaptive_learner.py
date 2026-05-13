"""
Adaptive Learner -- Self-Calibrating Feedback Engine

Learns from proposal outcomes to improve the adaptive system over time.

Key capabilities:
    1. Outcome tracking -- record whether proposals were effective/noise/false-positive
    2. Threshold calibration -- raise/lower detection thresholds based on outcome rates
    3. Noise suppression -- mute chronically noisy domain keys
    4. Effectiveness reporting -- per-system performance metrics

Calibration rules:
    - If system has >30% FALSE_POSITIVE rate: raise threshold by 1
    - If system has >80% EFFECTIVE rate: lower threshold by 1 (catch earlier)
    - If a domain_key is rejected 5+ times: add to suppression list
    - Thresholds are bounded: min=2, max=10

Usage:
    from packages.adaptive_system.adaptive_learner import AdaptiveLearner
    learner = AdaptiveLearner(calibration_path)
    
    # Record outcome
    learner.record_outcome("test_coverage", "test_full_suite_...", "effective")
    
    # Recalibrate
    changes = learner.recalibrate()
    
    # Apply calibration to live systems
    learner.apply_to_systems(systems_dict)
"""

import json
import logging
from collections import Counter, defaultdict
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("adaptive_learner")


# ---------------------------------------------------------------
# Calibration State
# ---------------------------------------------------------------

class CalibrationState:
    """Persistent calibration data for the learning engine."""
    
    DEFAULT = {
        "version": "1.0",
        "updated_at": "",
        "systems": {},
        "global_suppressions": [],
        "outcome_history": [],
    }
    
    def __init__(self, path: Path):
        self.path = path
        self.data = self._load()
    
    def _load(self) -> dict:
        if self.path.exists():
            try:
                return json.loads(self.path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                pass
        return deepcopy(self.DEFAULT)
    
    def save(self):
        self.data["updated_at"] = datetime.now().isoformat()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(self.data, indent=2, default=str),
            encoding="utf-8",
        )
    
    def get_system(self, name: str) -> dict:
        systems = self.data.setdefault("systems", {})
        if name not in systems:
            systems[name] = {
                "threshold_adjustment": 0,
                "suppressed_domains": [],
                "outcome_counts": {"effective": 0, "noise": 0, "false_positive": 0, "rejected": 0},
                "total_proposals": 0,
                "effectiveness_rate": 0.0,
            }
        return systems[name]
    
    def add_outcome(self, system_name: str, proposal_id: str, outcome: str, domain_key: str = ""):
        """Add an outcome record."""
        history = self.data.setdefault("outcome_history", [])
        history.append({
            "system": system_name,
            "proposal_id": proposal_id,
            "outcome": outcome,
            "domain_key": domain_key,
            "timestamp": datetime.now().isoformat(),
        })
        # Keep last 500 outcomes
        if len(history) > 500:
            self.data["outcome_history"] = history[-500:]
        
        # Update per-system counts
        sys_data = self.get_system(system_name)
        counts = sys_data["outcome_counts"]
        if outcome in counts:
            counts[outcome] += 1
        sys_data["total_proposals"] += 1
        
        # Update effectiveness rate
        total = sum(counts.values())
        if total > 0:
            sys_data["effectiveness_rate"] = counts["effective"] / total


# ---------------------------------------------------------------
# Adaptive Learner
# ---------------------------------------------------------------

class AdaptiveLearner:
    """
    Self-calibrating learning engine for the adaptive nervous system.
    
    Tracks outcomes, adjusts thresholds, and suppresses noise.
    """
    
    # Bounds for threshold adjustments
    MIN_THRESHOLD = 2
    MAX_THRESHOLD = 10
    MAX_ADJUSTMENT_PER_CYCLE = 2  # Don't change more than +-2 at once
    
    # Calibration triggers
    FALSE_POSITIVE_CEILING = 0.30  # If >30% false positive -> raise threshold
    EFFECTIVENESS_FLOOR = 0.80     # If >80% effective -> lower threshold
    NOISE_REJECT_COUNT = 5         # If domain rejected 5+ times -> suppress
    MIN_SAMPLES = 5                # Need at least this many samples to calibrate
    
    def __init__(self, calibration_path: Optional[Path] = None):
        default_path = Path.cwd() / ".agent" / "adaptive" / "calibration.json"
        self.state = CalibrationState(calibration_path or default_path)
    
    def record_outcome(
        self,
        system_name: str,
        proposal_id: str,
        outcome: str,
        domain_key: str = "",
    ):
        """Record the outcome of a proposal execution.
        
        Args:
            system_name: Which adaptive system generated the proposal
            proposal_id: The proposal ID
            outcome: One of: effective, noise, false_positive, rejected
            domain_key: The signal domain key (for noise suppression)
        """
        valid_outcomes = {"effective", "noise", "false_positive", "rejected"}
        if outcome not in valid_outcomes:
            raise ValueError(f"Invalid outcome: {outcome}. Must be one of: {valid_outcomes}")
        
        self.state.add_outcome(system_name, proposal_id, outcome, domain_key)
        self.state.save()
        logger.info(f"[learner] Recorded {outcome} for {system_name}/{proposal_id}")
    
    def recalibrate(self) -> Dict[str, Any]:
        """Run recalibration across all systems.
        
        Returns:
            Dict of changes made: {system: {old_threshold, new_threshold, suppressions_added}}
        """
        changes = {}
        
        for sys_name, sys_data in self.state.data.get("systems", {}).items():
            total = sys_data.get("total_proposals", 0)
            if total < self.MIN_SAMPLES:
                continue
            
            counts = sys_data.get("outcome_counts", {})
            total_evaluated = sum(counts.values())
            if total_evaluated == 0:
                continue
            
            fp_rate = counts.get("false_positive", 0) / total_evaluated
            eff_rate = counts.get("effective", 0) / total_evaluated
            
            old_adj = sys_data.get("threshold_adjustment", 0)
            new_adj = old_adj
            reason = ""
            
            # Rule 1: Too many false positives -> raise threshold
            if fp_rate > self.FALSE_POSITIVE_CEILING:
                delta = min(2, int(fp_rate * 4))  # Scale with FP rate
                new_adj = min(old_adj + delta, self.MAX_THRESHOLD - 3)  # Leave room for base
                reason = f"FP rate {fp_rate:.0%} > {self.FALSE_POSITIVE_CEILING:.0%}"
            
            # Rule 2: Very effective -> lower threshold (catch earlier)
            elif eff_rate > self.EFFECTIVENESS_FLOOR:
                new_adj = max(old_adj - 1, -(self.MIN_THRESHOLD - 1))
                reason = f"Effectiveness {eff_rate:.0%} > {self.EFFECTIVENESS_FLOOR:.0%}"
            
            # Noise suppression: check domain-level rejection rates
            new_suppressions = self._check_noise_domains(sys_name)
            
            if new_adj != old_adj or new_suppressions:
                sys_data["threshold_adjustment"] = new_adj
                for domain in new_suppressions:
                    if domain not in sys_data.get("suppressed_domains", []):
                        sys_data.setdefault("suppressed_domains", []).append(domain)
                
                changes[sys_name] = {
                    "old_adjustment": old_adj,
                    "new_adjustment": new_adj,
                    "reason": reason,
                    "suppressions_added": new_suppressions,
                    "fp_rate": fp_rate,
                    "eff_rate": eff_rate,
                }
                
                logger.info(
                    f"[learner] Recalibrated {sys_name}: "
                    f"threshold adj {old_adj} -> {new_adj} ({reason})"
                )
        
        self.state.save()
        return changes
    
    def _check_noise_domains(self, system_name: str) -> List[str]:
        """Check if any domain keys should be suppressed for noise."""
        history = self.state.data.get("outcome_history", [])
        
        # Count rejections per domain for this system
        domain_rejections = Counter()
        for entry in history:
            if entry["system"] == system_name and entry["outcome"] in ("rejected", "false_positive"):
                dk = entry.get("domain_key", "")
                if dk:
                    domain_rejections[dk] += 1
        
        # Suppress domains exceeding threshold
        existing = set(
            self.state.get_system(system_name).get("suppressed_domains", [])
        )
        new_suppressions = []
        for domain, count in domain_rejections.items():
            if count >= self.NOISE_REJECT_COUNT and domain not in existing:
                new_suppressions.append(domain)
                logger.info(f"[learner] Suppressing noisy domain: {system_name}/{domain} ({count} rejections)")
        
        return new_suppressions
    
    def apply_to_systems(self, systems: Dict[str, Any]) -> Dict[str, int]:
        """Apply learned calibration to live adaptive systems.
        
        Args:
            systems: Dict mapping system_name -> AdaptiveSystem instance
            
        Returns:
            Dict of {system_name: adjusted_threshold}
        """
        applied = {}
        
        for name, system in systems.items():
            cal = self.state.get_system(name)
            adj = cal.get("threshold_adjustment", 0)
            
            if adj != 0 and hasattr(system, "tracker"):
                base = system.tracker.threshold
                new_threshold = max(self.MIN_THRESHOLD, min(self.MAX_THRESHOLD, base + adj))
                system.tracker.threshold = new_threshold
                applied[name] = new_threshold
                logger.info(f"[learner] Applied calibration to {name}: threshold {base} -> {new_threshold}")
        
        return applied
    
    def is_suppressed(self, system_name: str, domain_key: str) -> bool:
        """Check if a domain key is suppressed for a system."""
        sys_data = self.state.get_system(system_name)
        suppressed = sys_data.get("suppressed_domains", [])
        global_suppressed = self.state.data.get("global_suppressions", [])
        return domain_key in suppressed or domain_key in global_suppressed
    
    def get_report(self) -> Dict[str, Any]:
        """Generate a learning report."""
        report = {
            "calibration_file": str(self.state.path),
            "last_updated": self.state.data.get("updated_at", "never"),
            "total_outcomes": len(self.state.data.get("outcome_history", [])),
            "systems": {},
        }
        
        for name, sys_data in self.state.data.get("systems", {}).items():
            counts = sys_data.get("outcome_counts", {})
            total = sum(counts.values())
            report["systems"][name] = {
                "total_proposals": sys_data.get("total_proposals", 0),
                "effectiveness_rate": sys_data.get("effectiveness_rate", 0),
                "threshold_adjustment": sys_data.get("threshold_adjustment", 0),
                "suppressed_domains": len(sys_data.get("suppressed_domains", [])),
                "outcome_breakdown": counts,
            }
        
        return report
    
    def reset_system(self, system_name: str):
        """Reset calibration for a specific system."""
        if system_name in self.state.data.get("systems", {}):
            del self.state.data["systems"][system_name]
            self.state.save()
            logger.info(f"[learner] Reset calibration for {system_name}")
