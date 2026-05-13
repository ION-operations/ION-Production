"""Verifiable Intelligence Framework (VIF)

Provides provenance, uncertainty quantification, and verifiability for AI operations.

Components:
- witness.py: VIF schema and provenance envelopes
- confidence_extraction.py: Extract confidence from LLM outputs
- calibration.py: ECE tracking and calibration analysis
- kappa_gate.py: Behavioral abstention (κ-gating) and HITL escalation
- replay.py: Deterministic replay of operations
- confidence_bands.py: User-facing confidence indicators
"""

from .witness import VIF, ConfidenceBand, TaskCriticality
from .confidence_extraction import (
    extract_confidence,
    extract_from_logprobs,
    combine_confidence_signals,
    ConfidenceExtraction,
)
from .calibration import (
    ECETracker,
    CalibrationBin,
    calculate_ece_from_predictions,
    apply_temperature_scaling,
)
from .kappa_gate import (
    KappaGate,
    KappaGateResult,
    HITLEscalator,
    create_confidence_based_gate,
    adaptive_kappa_threshold,
    DEFAULT_KAPPA_THRESHOLDS,
)
from .replay import (
    ReplayEngine,
    ReplayResult,
    ReplayCache,
    create_replay_witness,
)
from .confidence_bands import (
    determine_band,
    get_band_definition,
    format_confidence_for_user,
    format_band_badge,
    get_confidence_color,
    get_recommended_action,
    should_show_warning,
    get_all_band_info,
    BandRouter,
    BandDefinition,
    STANDARD_BANDS,
)
from .cmc_integration import (
    vif_to_atom_payload,
    atom_to_vif,
    VIFStore,
    create_witness_and_store,
)
from .seg_integration import (
    verify_witness_link,
    verify_provenance_chain,
    calculate_evidence_weighting,
    verify_all_witness_links,
    get_evidence_weighting_stats,
    WitnessLinkVerification,
    ProvenanceChainVerification,
    EvidenceWeightingResult,
)
from .hhni_integration import (
    extract_rs_lift_metrics,
    store_rs_lift_in_witness,
    calculate_rs_lift_statistics,
    create_retrieval_witness,
    RSLiftMetrics,
    RSLiftStatistics,
)
from .sdfcvf_integration import (
    vif_witness_to_trace_text,
    collect_witnesses_for_file,
    create_trace_file_from_witnesses,
    calculate_parity_with_vif_traces,
    combine_confidence_and_parity,
    get_nl_tags_from_witnesses,
    ParityQualityResult,
)
from .tcs_integration import (
    create_witness_timeline_entry,
    create_kappa_gate_timeline_entry,
    query_witness_timeline,
    query_snapshot_timeline,
    query_confidence_timeline,
    is_tcs_available,
)
from .cas_integration import (
    extract_cognitive_context,
    add_cognitive_context_to_witness,
    enhance_confidence_with_cognitive_state,
    create_witness_with_cognitive_context,
    is_cas_available,
    CognitiveContext,
)
from .audit_api import (
    get_witness_for_audit,
    query_witnesses_for_audit,
    get_provenance_chain_for_audit,
    get_run_witnesses_for_audit,
    AuditFormat,
    AuditReport,
    AuditQuery,
)

__all__ = [
    # Witness schema
    "VIF",
    "ConfidenceBand",
    "TaskCriticality",
    # Confidence extraction
    "extract_confidence",
    "extract_from_logprobs",
    "combine_confidence_signals",
    "ConfidenceExtraction",
    # Calibration
    "ECETracker",
    "CalibrationBin",
    "calculate_ece_from_predictions",
    "apply_temperature_scaling",
    # κ-gating
    "KappaGate",
    "KappaGateResult",
    "HITLEscalator",
    "create_confidence_based_gate",
    "adaptive_kappa_threshold",
    "DEFAULT_KAPPA_THRESHOLDS",
    # Replay
    "ReplayEngine",
    "ReplayResult",
    "ReplayCache",
    "create_replay_witness",
    # Confidence bands
    "determine_band",
    "get_band_definition",
    "format_confidence_for_user",
    "format_band_badge",
    "get_confidence_color",
    "get_recommended_action",
    "should_show_warning",
    "get_all_band_info",
    "BandRouter",
    "BandDefinition",
    "STANDARD_BANDS",
    # CMC integration
    "vif_to_atom_payload",
    "atom_to_vif",
    "VIFStore",
    "create_witness_and_store",
    # SEG integration
    "verify_witness_link",
    "verify_provenance_chain",
    "calculate_evidence_weighting",
    "verify_all_witness_links",
    "get_evidence_weighting_stats",
    "WitnessLinkVerification",
    "ProvenanceChainVerification",
    "EvidenceWeightingResult",
    # HHNI integration
    "extract_rs_lift_metrics",
    "store_rs_lift_in_witness",
    "calculate_rs_lift_statistics",
    "create_retrieval_witness",
    "RSLiftMetrics",
    "RSLiftStatistics",
    # SDF-CVF integration
    "vif_witness_to_trace_text",
    "collect_witnesses_for_file",
    "create_trace_file_from_witnesses",
    "calculate_parity_with_vif_traces",
    "combine_confidence_and_parity",
    "get_nl_tags_from_witnesses",
    "ParityQualityResult",
    # TCS integration
    "create_witness_timeline_entry",
    "create_kappa_gate_timeline_entry",
    "query_witness_timeline",
    "query_snapshot_timeline",
    "query_confidence_timeline",
    "is_tcs_available",
    # CAS integration
    "extract_cognitive_context",
    "add_cognitive_context_to_witness",
    "enhance_confidence_with_cognitive_state",
    "create_witness_with_cognitive_context",
    "is_cas_available",
    "CognitiveContext",
    # Audit API
    "get_witness_for_audit",
    "query_witnesses_for_audit",
    "get_provenance_chain_for_audit",
    "get_run_witnesses_for_audit",
    "AuditFormat",
    "AuditReport",
    "AuditQuery",
]

