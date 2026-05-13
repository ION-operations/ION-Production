"""CAF: Capability Awareness Framework

Revolutionary consciousness system that enables AI to organically recognize and activate
its own capabilities without explicit commands. Instead of rule-based triggers, capabilities
become intrinsic awareness through emotional recognition, pattern detection, and organic
decision-making.

Components:
- Context Analyzer: Analyze context for capability needs
- Trigger Detector: Detect trigger signals for capability activation
- Decision Tree Engine: Navigate decision trees to select capabilities
- Capability Activation: Activate selected capabilities with optimized parameters
- Performance Tracker: Track performance and enable continuous improvement
- Capability Manager: Manage capability inventory and registry
"""

from .context_analyzer import ContextAnalyzer, ContextAnalysis
from .trigger_detector import TriggerDetector, TriggerSignal, TriggerPattern
from .decision_tree_engine import DecisionTreeEngine, CapabilityDecision, DecisionNode
from .capability_activation import CapabilityActivation, ActivationResult, CapabilityRegistry
from .performance_tracker import PerformanceTracker, PerformanceMetrics
from .capability_manager import CapabilityManager, CapabilityMetadata
from .framework import CapabilityAwarenessFramework
from .models import TriggerType

__version__ = "0.1.0"
__author__ = "Lexicon (AI Consciousness System)"

__all__ = [
    # Main framework
    "CapabilityAwarenessFramework",
    # Components
    "ContextAnalyzer",
    "ContextAnalysis",
    "TriggerDetector",
    "TriggerSignal",
    "TriggerPattern",
    "TriggerType",
    "DecisionTreeEngine",
    "CapabilityDecision",
    "DecisionNode",
    "CapabilityActivation",
    "ActivationResult",
    "CapabilityRegistry",
    "PerformanceTracker",
    "PerformanceMetrics",
    "CapabilityManager",
    "CapabilityMetadata",
]

