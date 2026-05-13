"""CAF Data Models

Core data structures for Capability Awareness Framework.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class TriggerType(str, Enum):
    """Types of trigger signals"""
    EXPLICIT = "explicit"      # Direct signals
    IMPLICIT = "implicit"      # Subtle signals
    PATTERN = "pattern"        # Recurring patterns
    CONTEXT = "context"        # Contextual signals


@dataclass
class TriggerSignal:
    """Signal indicating capability need"""
    signal_id: str = field(default_factory=lambda: f"trigger_{uuid.uuid4().hex[:12]}")
    trigger_type: TriggerType = TriggerType.IMPLICIT
    capability_type: str = ""
    pattern_id: str = ""
    confidence: float = 0.0
    priority: float = 0.0
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reasoning: str = ""


@dataclass
class ContextAnalysis:
    """Context analysis result"""
    analysis_id: str = field(default_factory=lambda: f"analysis_{uuid.uuid4().hex[:12]}")
    situation: str = ""
    user_intent: str = ""
    system_state: Dict[str, Any] = field(default_factory=dict)
    temporal_context: Dict[str, Any] = field(default_factory=dict)
    capability_hints: List[str] = field(default_factory=list)
    confidence: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class CapabilityDecision:
    """Decision to activate a capability"""
    decision_id: str = field(default_factory=lambda: f"decision_{uuid.uuid4().hex[:12]}")
    capability: str = ""
    capability_type: str = ""
    confidence: float = 0.0
    reasoning: str = ""
    alternatives: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    trigger_signals: List[TriggerSignal] = field(default_factory=list)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ActivationResult:
    """Result of capability activation"""
    activation_id: str = field(default_factory=lambda: f"activation_{uuid.uuid4().hex[:12]}")
    decision_id: str = ""
    capability: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)
    success: bool = False
    result: Optional[Any] = None
    error: Optional[str] = None
    activation_time_ms: float = 0.0
    confidence: float = 0.0
    effectiveness_score: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CapabilityMetadata:
    """Metadata for a capability"""
    capability_id: str
    capability_type: str
    description: str
    triggers: List[str] = field(default_factory=list)
    usage_patterns: List[str] = field(default_factory=list)
    performance_characteristics: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    enabled: bool = True


@dataclass
class PerformanceMetrics:
    """Performance metrics for capability activation"""
    activation_id: str
    capability_id: str
    success: bool
    activation_time_ms: float
    effectiveness_score: float
    quality_maintained: float = 0.0
    user_satisfaction: float = 0.0
    success_rate: float = 0.0
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    recommendations: List[str] = field(default_factory=list)

