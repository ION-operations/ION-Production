"""
AIM-OS Adaptive System Package -- v4.0 (Closed-Loop)

11 self-healing systems with autonomous daemon, learning engine, and git hooks:
1-8. Original sensors (research, doc, context, test, decay, security, arch)
9. Performance Regression Sensor
10. Dependency Health Sensor
11. Agent Effectiveness Sensor
12. Context Coherence Sensor

v4 additions: ProposalExecutor, AdaptiveDaemon, AdaptiveLearner, Git Hooks
"""

from .adaptive_core import (
    AdaptiveSystem,
    AdaptiveSensor,
    AdaptiveTracker,
    AdaptiveAnalyzer,
    AdaptiveGenerator,
    AdaptiveGatekeeper,
    Signal,
    TrackerEntry,
    Assessment,
    AdaptiveResponse,
    Severity,
    ApprovalLevel,
)
from .research_depth import create_research_depth_adaptor
from .doc_depth import create_doc_depth_adaptor
from .context_depth import create_context_depth_adaptor
from .test_coverage import create_test_coverage_adaptor
from .knowledge_decay import create_knowledge_decay_detector
from .security_posture import create_security_posture_adaptor
from .arch_drift import create_arch_drift_detector

# v4 modules
from .adaptive_executor import ProposalExecutor, Proposal
from .adaptive_daemon import AdaptiveDaemon, DaemonConfig
from .adaptive_learner import AdaptiveLearner

__all__ = [
    "AdaptiveSystem",
    "AdaptiveSensor",
    "AdaptiveTracker",
    "AdaptiveAnalyzer",
    "AdaptiveGenerator",
    "AdaptiveGatekeeper",
    "Signal",
    "TrackerEntry",
    "Assessment",
    "AdaptiveResponse",
    "Severity",
    "ApprovalLevel",
    "create_research_depth_adaptor",
    "create_doc_depth_adaptor",
    "create_context_depth_adaptor",
    "create_test_coverage_adaptor",
    "create_knowledge_decay_detector",
    "create_security_posture_adaptor",
    "create_arch_drift_detector",
    # v4
    "ProposalExecutor",
    "Proposal",
    "AdaptiveDaemon",
    "DaemonConfig",
    "AdaptiveLearner",
]

__version__ = "4.0.0"
