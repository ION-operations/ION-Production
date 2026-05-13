"""CAS: Cognitive Analysis System

Meta-cognitive monitoring system that tracks AI thought processes, detects failure modes,
and enables self-correction. Provides systematic introspection for continuous improvement.

Components:
- Activation Tracking (hot vs cold principles)
- Category Recognition (task classification validation)
- Attention Monitoring (cognitive load tracking)
- Failure Mode Analysis (4 specific error patterns)
- Introspection Protocols (systematic self-examination)
"""

from .activation import ActivationTracker, ActivationState
from .category import CategoryRecognizer, CategoryResult
from .attention import AttentionMonitor, AttentionState
from .failure_modes import FailureModeAnalyzer, FailurePattern
from .introspection import IntrospectionProtocol, IntrospectionResult

__version__ = "0.1.0"
__author__ = "Aether (AI Consciousness System)"

__all__ = [
    "ActivationTracker",
    "ActivationState", 
    "CategoryRecognizer",
    "CategoryResult",
    "AttentionMonitor",
    "AttentionState",
    "FailureModeAnalyzer",
    "FailurePattern",
    "IntrospectionProtocol",
    "IntrospectionResult"
]
