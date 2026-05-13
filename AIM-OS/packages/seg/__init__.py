"""SEG: Shared Evidence Graph (Production-Ready)

Bitemporal knowledge graph with contradiction detection and provenance tracking.

Components:
- Entity, Relation, Evidence nodes (bitemporal)
- SEGraph (NetworkX-based graph with time-travel)
- Contradiction detection
- Provenance tracing
- CMC integration
"""

from .models import (
    Entity,
    Relation,
    Evidence,
    Contradiction,
    TimeSlice,
    NodeType,
    RelationType,
)
from .seg_graph import SEGraph
from .witness import write_witness  # Legacy function for compatibility
from .tcs_integration import (
    timeline_entry_to_evidence,
    ingest_timeline_entry,
)

# Import integration modules (may fail if dependencies not available)
try:
    from .cmc_integration import (
        store_evidence_in_cmc,
        retrieve_evidence_from_cmc,
        link_evidence_to_cmc,
    )
    CMC_INTEGRATION_AVAILABLE = True
except ImportError:
    CMC_INTEGRATION_AVAILABLE = False

try:
    from .vif_integration import (
        create_vif_witness,
        attach_witness_to_entity,
        attach_witness_to_relation,
        attach_witness_to_evidence,
        get_witness_provenance,
    )
    VIF_INTEGRATION_AVAILABLE = True
except ImportError:
    VIF_INTEGRATION_AVAILABLE = False

try:
    from .hhni_integration import (
        synthesize_evidence,
        get_synthesis_context,
        index_evidence_for_hhni,
    )
    HHNI_INTEGRATION_AVAILABLE = True
except ImportError:
    HHNI_INTEGRATION_AVAILABLE = False

try:
    from .apoe_integration import (
        store_execution_trace,
        get_plan_effectiveness,
        link_trace_to_evidence,
    )
    APOE_INTEGRATION_AVAILABLE = True
except ImportError:
    APOE_INTEGRATION_AVAILABLE = False

try:
    from .sdfcvf_integration import (
        validate_consistency,
        link_trace_to_evidence as link_sdfcvf_trace,
        get_consistency_report,
    )
    SDFCVF_INTEGRATION_AVAILABLE = True
except ImportError:
    SDFCVF_INTEGRATION_AVAILABLE = False

try:
    from .cas_integration import (
        store_failure_pattern,
        get_failure_patterns,
        link_pattern_to_evidence,
    )
    CAS_INTEGRATION_AVAILABLE = True
except ImportError:
    CAS_INTEGRATION_AVAILABLE = False

__all__ = [
    # Core models
    "Entity",
    "Relation",
    "Evidence",
    "Contradiction",
    "TimeSlice",
    # Enums
    "NodeType",
    "RelationType",
    # Graph
    "SEGraph",
    # TCS Integration
    "timeline_entry_to_evidence",
    "ingest_timeline_entry",
    # Legacy
    "write_witness",
]

# Add integration exports if available
if CMC_INTEGRATION_AVAILABLE:
    __all__.extend([
        "store_evidence_in_cmc",
        "retrieve_evidence_from_cmc",
        "link_evidence_to_cmc",
    ])

if VIF_INTEGRATION_AVAILABLE:
    __all__.extend([
        "create_vif_witness",
        "attach_witness_to_entity",
        "attach_witness_to_relation",
        "attach_witness_to_evidence",
        "get_witness_provenance",
    ])

if HHNI_INTEGRATION_AVAILABLE:
    __all__.extend([
        "synthesize_evidence",
        "get_synthesis_context",
        "index_evidence_for_hhni",
    ])

if APOE_INTEGRATION_AVAILABLE:
    __all__.extend([
        "store_execution_trace",
        "get_plan_effectiveness",
        "link_trace_to_evidence",
    ])

if SDFCVF_INTEGRATION_AVAILABLE:
    __all__.extend([
        "validate_consistency",
        "link_sdfcvf_trace",
        "get_consistency_report",
    ])

if CAS_INTEGRATION_AVAILABLE:
    __all__.extend([
        "store_failure_pattern",
        "get_failure_patterns",
        "link_pattern_to_evidence",
    ])
