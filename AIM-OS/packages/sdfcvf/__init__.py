"""SDF-CVF: Atomic Evolution Framework

Ensures code, documentation, tests, and traces evolve together atomically.

Key Concepts:
- Quartet: (code, docs, tests, traces) that must stay aligned
- Parity: Measure of quartet alignment (0.0-1.0)
- Gate: Block commits/deploys if parity too low
"""

from .quartet import Quartet, QuartetDetector, FileClassification, extract_module_name
from .parity import ParityCalculator, ParityResult, calculate_parity, weighted_parity
from .gates import (
    ParityGate,
    GateConfig,
    GateType,
    GateResult,
    create_pre_commit_gate,
    create_deployment_gate,
    create_pr_gate,
)
from .blast_radius import DependencyAnalyzer, BlastRadiusResult, analyze_blast_radius
from .dora import (
    DORAMetricsCollector,
    DORAMetrics,
    ParityDORACorrelator,
    CorrelationAnalysis,
    initialize_dora_db,
    report_dora_metrics,
)
# Integration modules (optional dependencies)
# Note: These may fail due to circular dependencies in other packages
# They are imported lazily when needed, not at module level
try:
    from .cmc_integration import CMCIntegration, ParityAtom
    from .vif_integration import VIFIntegration
    from .seg_integration import SEGIntegration
    from .apoe_integration import APOEIntegration
    from .hhni_integration import HHNIIntegration
    from .cas_integration import CASIntegration
    from .tcs_integration import TCSIntegration
    INTEGRATIONS_AVAILABLE = True
except (ImportError, SyntaxError, AttributeError, ModuleNotFoundError):
    # Integrations are optional - may fail due to circular deps or syntax errors in other packages
    INTEGRATIONS_AVAILABLE = False
    CMCIntegration = None
    ParityAtom = None
    VIFIntegration = None
    SEGIntegration = None
    APOEIntegration = None
    HHNIIntegration = None
    CASIntegration = None
    TCSIntegration = None

__all__ = [
    # Quartet detection
    "Quartet",
    "QuartetDetector",
    "FileClassification",
    "extract_module_name",
    # Parity calculation
    "ParityCalculator",
    "ParityResult",
    "calculate_parity",
    "weighted_parity",
    # Gates
    "ParityGate",
    "GateConfig",
    "GateType",
    "GateResult",
    "create_pre_commit_gate",
    "create_deployment_gate",
    "create_pr_gate",
    # Blast radius
    "DependencyAnalyzer",
    "BlastRadiusResult",
    "analyze_blast_radius",
    # DORA metrics
    "DORAMetricsCollector",
    "DORAMetrics",
    "ParityDORACorrelator",
    "CorrelationAnalysis",
    "initialize_dora_db",
    "report_dora_metrics",
    # Integrations (optional)
    "CMCIntegration",
    "ParityAtom",
    "VIFIntegration",
    "SEGIntegration",
    "APOEIntegration",
    "HHNIIntegration",
    "CASIntegration",
    "TCSIntegration",
    "INTEGRATIONS_AVAILABLE",
]

