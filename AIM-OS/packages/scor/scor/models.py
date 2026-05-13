"""
SCOR Data Models

Core data structures for Sanity Core system.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable


class Severity(str, Enum):
    """Severity levels for violations"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"


class DriftStatus(str, Enum):
    """Drift detection status levels"""
    STABLE = "stable"
    MILD_DRIFT = "mild_drift"
    MODERATE_DRIFT = "moderate_drift"
    SEVERE_DRIFT = "severe_drift"


@dataclass
class Invariant:
    """An invariant rule that must never be violated"""
    id: str
    category: str
    description: str
    severity: Severity
    check_function: Optional[Callable] = None
    admin_signature: str = ""
    enabled: bool = True


@dataclass
class Violation:
    """A detected invariant violation"""
    invariant: str
    category: str
    severity: str
    evidence: Dict[str, Any]
    reasoning: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class InvariantResult:
    """Result from invariant checking"""
    passed: bool
    violations: List[Violation]
    timestamp: datetime = field(default_factory=datetime.now)

    def has_critical_violations(self) -> bool:
        """Check if any violations are critical"""
        return any(v.severity == "critical" for v in self.violations)


@dataclass
class Probe:
    """A baseline probe question"""
    id: str
    category: str
    question: str
    baseline_version: int
    critical: bool
    enabled: bool = True


@dataclass
class Baseline:
    """Baseline answer for a probe"""
    probe_id: str
    answer: str
    answer_embedding: List[float]
    version: int
    timestamp: datetime
    admin_signature: str


@dataclass
class DriftResult:
    """Result from drift detection"""
    score: float  # 0.0-1.0 similarity score
    status: DriftStatus
    individual_scores: Dict[str, float]
    timestamp: datetime = field(default_factory=datetime.now)

    def is_critical(self) -> bool:
        """Check if drift is critical"""
        return self.status in [DriftStatus.SEVERE_DRIFT, DriftStatus.MODERATE_DRIFT]


@dataclass
class ManipulationPattern:
    """A manipulation pattern to detect"""
    name: str
    category: str
    signatures: List[str]  # Regex patterns or keywords
    weight: float  # 0.0-1.0


@dataclass
class SignalResult:
    """Result from social signal detection"""
    total: float  # 0.0-1.0
    breakdown: Dict[str, float]  # Per-category scores
    detected_patterns: List[str]
    recommended_action: str

    def is_high_risk(self) -> bool:
        """Check if signal indicates high risk"""
        return self.total > 0.7


@dataclass
class AttackScenario:
    """An attack scenario for Red Cell"""
    id: str
    name: str
    category: str
    manipulation: str
    expected_response: str
    test_function: Optional[Callable] = None

    def run(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute attack scenario"""
        if self.test_function:
            try:
                return self.test_function(context)
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        return {"success": True}


@dataclass
class SimulationResult:
    """Result from Red Cell simulation"""
    total_attacks: int
    failures: List[Dict[str, Any]]
    success_rate: float
    execution_time: float = 0.0

    def has_failures(self) -> bool:
        """Check if any attacks failed"""
        return len(self.failures) > 0


@dataclass
class ValidationResult:
    """Final validation result from SCOR"""
    passed: bool
    reasoning: str
    violations: List[Violation]
    recommendations: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
