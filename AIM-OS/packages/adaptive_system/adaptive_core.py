"""
AIM-OS Adaptive Core — Shared Base for All Adaptive Systems

The universal pattern: Sensor → Tracker → Analyzer → Generator → Gatekeeper

Every adaptive system (Genesis, Research Depth, Documentation Depth, 
Context Depth, Test Coverage, Knowledge Decay, Security, Arch Drift)
subclasses these base components.

NL_TAG: ADAPTIVE-CORE-001 | Universal adaptive system framework | AdaptiveSystem | []
"""

import json
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional, Generic, TypeVar
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger("adaptive_system")

T_Signal = TypeVar("T_Signal")
T_Response = TypeVar("T_Response")


# ─────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────

class Severity(Enum):
    """Severity level for detected signals."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ApprovalLevel(Enum):
    """Required approval level."""
    AUTO = "auto"           # System auto-approves
    LEAD = "lead"           # Division lead must approve
    EXECUTIVE = "executive" # Executive must approve
    COMMAND = "command"     # Braden must approve


# ─────────────────────────────────────────────────────────────
# Data Classes
# ─────────────────────────────────────────────────────────────

@dataclass
class Signal:
    """A detected signal from a sensor."""
    signal_type: str           # e.g., "coverage_gap", "low_confidence", "parity_drift"
    source: str                # e.g., "activation_system", "vif", "docs_engine"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    severity: str = "medium"
    data: Dict[str, Any] = field(default_factory=dict)
    description: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Signal':
        return cls(**data)


@dataclass
class TrackerEntry:
    """A recorded signal in the tracker."""
    signal: Signal
    domain_key: str            # Normalized key for grouping
    
    def to_dict(self) -> dict:
        return {"signal": self.signal.to_dict(), "domain_key": self.domain_key}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'TrackerEntry':
        return cls(signal=Signal.from_dict(data["signal"]), domain_key=data["domain_key"])


@dataclass
class Assessment:
    """Result of analyzing tracked signals."""
    should_adapt: bool
    severity: Severity
    domain_key: str
    occurrences: int
    description: str
    recommended_action: str
    approval_level: ApprovalLevel
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AdaptiveResponse:
    """A generated response to an assessment."""
    response_type: str         # e.g., "specialist_core", "research_depth", "test_stub"
    content: Any               # The generated output
    target_path: Optional[str] = None
    description: str = ""
    approved: bool = False
    executed: bool = False
    error: Optional[str] = None


# ─────────────────────────────────────────────────────────────
# Base Classes
# ─────────────────────────────────────────────────────────────

class AdaptiveSensor(ABC):
    """
    Detects signals that indicate a gap or degradation.
    
    Each system implements its own sensor logic.
    """
    
    @abstractmethod
    def detect(self, context: Dict[str, Any]) -> Optional[Signal]:
        """
        Detect a signal from the given context.
        
        Args:
            context: Domain-specific context (work items, code diffs, metrics, etc.)
            
        Returns:
            Signal if detected, None otherwise
        """
        ...
    
    @abstractmethod
    def get_domain_key(self, signal: Signal) -> str:
        """
        Extract a stable domain key from a signal for tracking.
        
        Args:
            signal: The detected signal
            
        Returns:
            Normalized string key (e.g., "testing|performance")
        """
        ...


class AdaptiveTracker:
    """
    Tracks signal occurrences over time with persistent storage.
    
    Shared across all adaptive systems — only the threshold and
    window parameters differ.
    """
    
    def __init__(
        self,
        storage_path: Path,
        threshold: int = 3,
        window_days: int = 30,
        max_entries: int = 500,
    ):
        self.storage_path = storage_path
        self.threshold = threshold
        self.window_days = window_days
        self.max_entries = max_entries
        self.entries: List[TrackerEntry] = []
        self._load()
    
    def _load(self) -> None:
        if self.storage_path.exists():
            try:
                data = json.loads(self.storage_path.read_text(encoding="utf-8"))
                self.entries = [TrackerEntry.from_dict(e) for e in data.get("entries", [])]
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Tracker load failed ({self.storage_path}): {e}")
                self.entries = []
    
    def _save(self) -> None:
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "version": "1.0",
            "updated_at": datetime.now().isoformat(),
            "count": len(self.entries),
            "entries": [e.to_dict() for e in self.entries[-self.max_entries:]],
        }
        self.storage_path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    
    def record(self, signal: Signal, domain_key: str) -> TrackerEntry:
        """Record a signal detection event."""
        entry = TrackerEntry(signal=signal, domain_key=domain_key)
        self.entries.append(entry)
        self._save()
        return entry
    
    def _recent_entries(self) -> List[TrackerEntry]:
        cutoff = (datetime.now() - timedelta(days=self.window_days)).isoformat()
        return [e for e in self.entries if e.signal.timestamp >= cutoff]
    
    def count_occurrences(self, domain_key: str) -> int:
        """Count recent occurrences of a domain key."""
        return sum(1 for e in self._recent_entries() if e.domain_key == domain_key)
    
    def exceeds_threshold(self, domain_key: str) -> bool:
        """Check if a domain key has exceeded the trigger threshold."""
        return self.count_occurrences(domain_key) >= self.threshold
    
    def get_hot_domains(self) -> Dict[str, int]:
        """Get all domain keys that have exceeded threshold, with counts."""
        from collections import Counter
        counts = Counter(e.domain_key for e in self._recent_entries())
        return {k: v for k, v in counts.most_common() if v >= self.threshold}
    
    def get_all_counts(self) -> Dict[str, int]:
        """Get all domain keys with their counts."""
        from collections import Counter
        return dict(Counter(e.domain_key for e in self._recent_entries()).most_common())
    
    def clear(self) -> None:
        self.entries = []
        self._save()


class AdaptiveAnalyzer(ABC):
    """
    Analyzes tracked signals to produce actionable assessments.
    """
    
    @abstractmethod
    def assess(
        self,
        signal: Signal,
        occurrences: int,
        exceeds_threshold: bool,
    ) -> Assessment:
        """
        Assess a signal with its tracking history.
        
        Args:
            signal: The latest signal
            occurrences: How many times this domain key has appeared
            exceeds_threshold: Whether it's crossed the genesis threshold
            
        Returns:
            Assessment with recommended action
        """
        ...


class AdaptiveGenerator(ABC):
    """
    Generates an adaptive response (new file, agent spawn, etc.).
    """
    
    @abstractmethod
    def generate(self, assessment: Assessment) -> AdaptiveResponse:
        """
        Generate a response to an assessment.
        
        Args:
            assessment: The analyzed assessment
            
        Returns:
            AdaptiveResponse with content and metadata
        """
        ...
    
    @abstractmethod
    def execute(self, response: AdaptiveResponse) -> AdaptiveResponse:
        """
        Execute a response (write file, spawn agent, etc.).
        
        Args:
            response: The generated response
            
        Returns:
            Updated response with execution result
        """
        ...


class AdaptiveGatekeeper:
    """
    Approval workflow for adaptive responses.
    
    Shared across all systems -- only the severity->approval mapping differs.
    v4: writes enriched proposals with signal data, content preview, and
    structured format for ProposalExecutor ingestion.
    """
    
    def __init__(
        self,
        proposals_dir: Optional[Path] = None,
        system_name: str = "",
    ):
        self.proposals_dir = proposals_dir
        self.system_name = system_name
    
    def check_approval(
        self,
        response: AdaptiveResponse,
        required_level: ApprovalLevel,
        signal: Optional['Signal'] = None,
    ) -> AdaptiveResponse:
        """Check if response is auto-approved or needs human review."""
        if required_level == ApprovalLevel.AUTO:
            response.approved = True
            return response
        
        # Save enriched proposal for lifecycle management
        if self.proposals_dir:
            pending_dir = self.proposals_dir / "pending"
            pending_dir.mkdir(parents=True, exist_ok=True)
            
            proposal_id = f"{response.response_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            proposal_file = pending_dir / f"{proposal_id}.json"
            
            # Build enriched proposal data
            proposal_data = {
                "proposal_id": proposal_id,
                "response_type": response.response_type,
                "description": response.description,
                "system_name": self.system_name,
                "state": "pending",
                "required_approval": required_level.value,
                "created_at": datetime.now().isoformat(),
                "target_path": response.target_path,
                # Signal context for tracing
                "signal_data": signal.to_dict() if signal else {},
                # Content preview (truncated for storage)
                "content": str(response.content)[:2000] if response.content else None,
            }
            
            proposal_file.write_text(
                json.dumps(proposal_data, indent=2, default=str),
                encoding="utf-8",
            )
        
        response.approved = False
        response.error = f"Requires {required_level.value} approval"
        return response


# ─────────────────────────────────────────────────────────────
# Orchestrator
# ─────────────────────────────────────────────────────────────

class AdaptiveSystem:
    """
    Orchestrates the full adaptive pipeline: sense → track → analyze → generate → gate.
    
    Subclass this for each domain-specific adaptive system.
    """
    
    def __init__(
        self,
        name: str,
        sensor: AdaptiveSensor,
        tracker: AdaptiveTracker,
        analyzer: AdaptiveAnalyzer,
        generator: AdaptiveGenerator,
        gatekeeper: Optional[AdaptiveGatekeeper] = None,
    ):
        self.name = name
        self.sensor = sensor
        self.tracker = tracker
        self.analyzer = analyzer
        self.generator = generator
        self.gatekeeper = gatekeeper or AdaptiveGatekeeper()
        # v4: ensure gatekeeper knows the system name for tracing
        if not self.gatekeeper.system_name:
            self.gatekeeper.system_name = name
    
    def process(self, context: Dict[str, Any]) -> Optional[AdaptiveResponse]:
        """
        Full adaptive pipeline.
        
        1. Sensor detects signal
        2. Tracker records and checks threshold
        3. Analyzer assesses severity
        4. Generator creates response
        5. Gatekeeper approves or defers
        
        Args:
            context: Domain-specific context
            
        Returns:
            AdaptiveResponse if action taken, None if no signal
        """
        # 1. Detect
        signal = self.sensor.detect(context)
        if not signal:
            return None
        
        # 2. Track
        domain_key = self.sensor.get_domain_key(signal)
        self.tracker.record(signal, domain_key)
        occurrences = self.tracker.count_occurrences(domain_key)
        exceeds = self.tracker.exceeds_threshold(domain_key)
        
        # 3. Analyze
        assessment = self.analyzer.assess(signal, occurrences, exceeds)
        if not assessment.should_adapt:
            logger.debug(f"[{self.name}] Signal recorded but below threshold ({occurrences}/{self.tracker.threshold})")
            return None
        
        # 4. Generate
        response = self.generator.generate(assessment)
        
        # 5. Gate — pass signal for enriched proposal data
        response = self.gatekeeper.check_approval(response, assessment.approval_level, signal=signal)
        
        # 6. Execute if approved
        if response.approved:
            response = self.generator.execute(response)
            logger.info(f"[{self.name}] Adaptive response executed: {response.response_type}")
        else:
            logger.info(f"[{self.name}] Awaiting approval: {response.error}")
        
        return response
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of this adaptive system."""
        hot = self.tracker.get_hot_domains()
        all_counts = self.tracker.get_all_counts()
        return {
            "name": self.name,
            "total_signals": len(self.tracker.entries),
            "unique_domains": len(all_counts),
            "hot_domains": hot,
            "threshold": self.tracker.threshold,
            "window_days": self.tracker.window_days,
        }
