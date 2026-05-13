"""VIF Integration with SDF-CVF (Quartet/Quintet Parity)

Provides VIF witnesses as "Traces" component for quartet/quintet parity validation.
Enables quality validation combining VIF confidence with parity scores.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path

# SDF-CVF imports (optional - gracefully handle if SDF-CVF not available)
try:
    from packages.sdfcvf.parity import ParityResult, ParityCalculator
    from packages.sdfcvf.quartet import Quartet
    SDFCVF_AVAILABLE = True
except ImportError:
    try:
        from sdfcvf.parity import ParityResult, ParityCalculator
        from sdfcvf.quartet import Quartet
        SDFCVF_AVAILABLE = True
    except ImportError:
        SDFCVF_AVAILABLE = False
        ParityResult = None
        ParityCalculator = None
        Quartet = None

# VIF imports
try:
    from packages.vif.witness import VIF
    from packages.vif.cmc_integration import VIFStore
    from packages.cmc import get_memory_store
    VIF_AVAILABLE = True
except ImportError:
    VIF_AVAILABLE = False
    VIF = None
    VIFStore = None
    get_memory_store = None


@dataclass
class ParityQualityResult:
    """Combined VIF confidence and parity score for quality validation"""
    parity_score: float
    vif_confidence: float
    combined_quality: float
    parity_passes: bool
    confidence_passes: bool
    overall_passes: bool
    warnings: List[str]


# NL_TAG: VIF-SDFCVF-001 | Convert VIF witness to trace text for parity calculation. | vif_witness_to_trace_text(vif) | []
# NL_TAG_CONNECT: VIF-SDFCVF-001 | VIF witness converted to trace text for SDF-CVF | vif_witness_to_trace_text → Quartet.trace_files | [VIF-SDFCVF-001, SDFCVF-QUARTET-001]
# NL_TAG_INTENT: VIF-INTENT-016 | Design decision: quartet parity traces | vif_witness_to_trace_text | [ADR-VIF-SDFCVF]
def vif_witness_to_trace_text(vif: VIF) -> str:
    """
    Convert VIF witness to trace text for quartet/quintet parity calculation.
    
    Formats VIF witness as text that can be embedded for similarity calculation.
    
    Args:
        vif: VIF witness instance
        
    Returns:
        Trace text string for parity calculation
        
    Examples:
        >>> vif = VIF(model_id="gpt-4", ...)
        >>> trace_text = vif_witness_to_trace_text(vif)
        >>> assert "gpt-4" in trace_text
    """
    if not VIF_AVAILABLE:
        raise ImportError("VIF not available - cannot convert witness to trace text")
    
    # Extract key information from VIF witness
    trace_parts = [
        f"VIF Witness: {vif.id}",
        f"Model: {vif.model_id} ({vif.model_provider})",
        f"Confidence: {vif.confidence_score:.2f} ({vif.confidence_band.value})",
        f"Task Criticality: {vif.task_criticality.value if vif.task_criticality else 'unknown'}",
        f"Context Snapshot: {vif.context_snapshot_id}",
        f"Prompt Hash: {vif.prompt_hash[:16]}...",
        f"Output Hash: {vif.output_hash[:16] if vif.output_hash else 'N/A'}...",
        f"Tokens: {vif.prompt_tokens} + {vif.output_tokens} = {vif.total_tokens}",
    ]
    
    # Add tool information
    if vif.tool_ids:
        trace_parts.append(f"Tools: {', '.join(vif.tool_ids)}")
    
    # Add κ-gate information
    if vif.kappa_gate_passed is not None:
        trace_parts.append(f"κ-Gate: {'PASSED' if vif.kappa_gate_passed else 'FAILED'}")
        if vif.kappa_threshold:
            trace_parts.append(f"κ-Threshold: {vif.kappa_threshold:.2f}")
    
    # Add ECE if available
    if vif.ece_score is not None:
        trace_parts.append(f"ECE: {vif.ece_score:.4f}")
    
    # Add lineage information
    if vif.parent_vif_id:
        trace_parts.append(f"Parent Witness: {vif.parent_vif_id}")
    if vif.child_vif_ids:
        trace_parts.append(f"Child Witnesses: {len(vif.child_vif_ids)}")
    
    # Add timestamp
    if hasattr(vif, 'timestamp') and vif.timestamp:
        trace_parts.append(f"Timestamp: {vif.timestamp}")
    
    return "\n".join(trace_parts)


# NL_TAG: VIF-SDFCVF-002 | Collect VIF witnesses for code file as traces. | collect_witnesses_for_file(file_path, limit) | []
# NL_TAG_CONNECT: VIF-SDFCVF-002 | Witnesses collected via VIFStore | collect_witnesses_for_file → VIFStore.query_witnesses | [VIF-SDFCVF-002, CMC-STORE-001]
# NL_TAG_INTENT: VIF-INTENT-017 | Design decision: trace collection | collect_witnesses_for_file | [ADR-VIF-SDFCVF]
def collect_witnesses_for_file(
    file_path: str,
    limit: int = 100,
) -> List[VIF]:
    """
    Collect VIF witnesses related to a code file for quartet parity.
    
    Queries VIFStore for witnesses related to the given file path.
    
    Args:
        file_path: Code file path to collect witnesses for
        limit: Maximum number of witnesses to return
        
    Returns:
        List of VIF witnesses
        
    Examples:
        >>> witnesses = collect_witnesses_for_file("packages/vif/witness.py", limit=10)
        >>> assert len(witnesses) <= 10
    """
    if not VIF_AVAILABLE:
        return []
    
    try:
        # Get VIFStore
        cmc_store = get_memory_store()
        vif_store = VIFStore(cmc_store)
        
        # Query witnesses (would need VIFStore.query_witnesses method)
        # For now, return empty list (graceful degradation)
        # TODO: Implement VIFStore.query_witnesses when available
        return []
    except Exception:
        # Graceful degradation
        return []


# NL_TAG: VIF-SDFCVF-003 | Create trace file from VIF witnesses for parity calculation. | create_trace_file_from_witnesses(witnesses, output_path) | []
# NL_TAG_CONNECT: VIF-SDFCVF-003 | Trace file created from VIF witnesses | create_trace_file_from_witnesses → vif_witness_to_trace_text | [VIF-SDFCVF-003, VIF-SDFCVF-001]
# NL_TAG_INTENT: VIF-INTENT-018 | Design decision: trace file generation | create_trace_file_from_witnesses | [ADR-VIF-SDFCVF]
def create_trace_file_from_witnesses(
    witnesses: List[VIF],
    output_path: str,
) -> str:
    """
    Create trace file from VIF witnesses for quartet parity calculation.
    
    Writes VIF witnesses as trace text to a file that can be used in quartet/quintet parity.
    
    Args:
        witnesses: List of VIF witnesses
        output_path: Path to write trace file to
        
    Returns:
        Path to created trace file
        
    Examples:
        >>> witnesses = [vif1, vif2, vif3]
        >>> trace_file = create_trace_file_from_witnesses(witnesses, "audit/traces.md")
        >>> assert Path(trace_file).exists()
    """
    if not VIF_AVAILABLE:
        raise ImportError("VIF not available - cannot create trace file")
    
    # Convert all witnesses to trace text
    trace_texts = []
    for i, witness in enumerate(witnesses, 1):
        trace_texts.append(f"## Witness {i}: {witness.id}")
        trace_texts.append(vif_witness_to_trace_text(witness))
        trace_texts.append("")  # Blank line between witnesses
    
    # Combine all trace texts
    combined_trace = "\n".join(trace_texts)
    
    # Write to file
    output_path_obj = Path(output_path)
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    output_path_obj.write_text(combined_trace, encoding='utf-8')
    
    return str(output_path_obj)


# NL_TAG: VIF-SDFCVF-004 | Calculate quartet parity with VIF witnesses as traces. | calculate_parity_with_vif_traces(code_files, doc_files, test_files, witnesses, embedding_fn) | []
# NL_TAG_CONNECT: VIF-SDFCVF-004 | Parity calculated with VIF traces via ParityCalculator | calculate_parity_with_vif_traces → ParityCalculator.calculate | [VIF-SDFCVF-004, SDFCVF-PARITY-002]
# NL_TAG_INTENT: VIF-INTENT-019 | Design decision: quartet parity integration | calculate_parity_with_vif_traces | [ADR-VIF-SDFCVF]
def calculate_parity_with_vif_traces(
    code_files: List[str],
    doc_files: List[str],
    test_files: List[str],
    witnesses: List[VIF],
    embedding_fn: Optional[callable] = None,
) -> ParityResult:
    """
    Calculate quartet parity with VIF witnesses as traces.
    
    Creates trace file from VIF witnesses and calculates quartet parity.
    
    Args:
        code_files: List of code file paths
        doc_files: List of documentation file paths
        test_files: List of test file paths
        witnesses: List of VIF witnesses to use as traces
        embedding_fn: Optional custom embedding function
        
    Returns:
        ParityResult with parity score and similarities
        
    Examples:
        >>> witnesses = [vif1, vif2]
        >>> result = calculate_parity_with_vif_traces(
        ...     code_files=["src/feature.py"],
        ...     doc_files=["docs/feature.md"],
        ...     test_files=["tests/test_feature.py"],
        ...     witnesses=witnesses
        ... )
        >>> assert result.parity_score >= 0.0
    """
    if not VIF_AVAILABLE or not SDFCVF_AVAILABLE:
        raise ImportError("VIF or SDF-CVF not available - cannot calculate parity")
    
    # Create temporary trace file
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
        trace_file = tmp_file.name
        create_trace_file_from_witnesses(witnesses, trace_file)
    
    try:
        # Calculate parity using SDF-CVF
        from packages.sdfcvf.parity import calculate_parity
        
        result = calculate_parity(
            code_files=code_files,
            doc_files=doc_files,
            test_files=test_files,
            trace_files=[trace_file],
            embedding_fn=embedding_fn,
        )
        
        return result
    finally:
        # Clean up temporary file
        try:
            Path(trace_file).unlink()
        except Exception:
            pass


# NL_TAG: VIF-SDFCVF-005 | Combine VIF confidence with parity score for quality validation. | combine_confidence_and_parity(parity_result, vif_confidence, confidence_threshold) | []
# NL_TAG_CONNECT: VIF-SDFCVF-005 | Quality validation combines VIF confidence with parity | combine_confidence_and_parity → ParityResult.passes_gate | [VIF-SDFCVF-005, SDFCVF-PARITY-001]
# NL_TAG_INTENT: VIF-INTENT-020 | Design decision: quality validation | combine_confidence_and_parity | [ADR-VIF-SDFCVF]
def combine_confidence_and_parity(
    parity_result: ParityResult,
    vif_confidence: float,
    confidence_threshold: float = 0.70,
    parity_threshold: float = 0.90,
) -> ParityQualityResult:
    """
    Combine VIF confidence with parity score for quality validation.
    
    Validates quality using both quartet parity and VIF confidence scores.
    
    Args:
        parity_result: Parity calculation result
        vif_confidence: VIF confidence score (0.0-1.0)
        confidence_threshold: Minimum VIF confidence to pass (default: 0.70)
        parity_threshold: Minimum parity score to pass (default: 0.90)
        
    Returns:
        ParityQualityResult with combined quality validation
        
    Examples:
        >>> result = ParityResult(parity_score=0.92, ...)
        >>> quality = combine_confidence_and_parity(result, vif_confidence=0.85)
        >>> assert quality.overall_passes == True
    """
    if not SDFCVF_AVAILABLE:
        raise ImportError("SDF-CVF not available - cannot combine confidence and parity")
    
    # Check if parity passes
    parity_passes = parity_result.passes_gate(parity_threshold)
    
    # Check if confidence passes
    confidence_passes = vif_confidence >= confidence_threshold
    
    # Calculate combined quality (weighted average)
    # Parity weight: 0.60, Confidence weight: 0.40
    combined_quality = (0.60 * parity_result.parity_score) + (0.40 * vif_confidence)
    
    # Overall passes if both pass
    overall_passes = parity_passes and confidence_passes
    
    # Collect warnings
    warnings = []
    if not parity_passes:
        warnings.append(f"Parity score {parity_result.parity_score:.2f} below threshold {parity_threshold:.2f}")
    if not confidence_passes:
        warnings.append(f"VIF confidence {vif_confidence:.2f} below threshold {confidence_threshold:.2f}")
    
    # Add parity warnings
    if parity_result.warnings:
        warnings.extend(parity_result.warnings)
    
    return ParityQualityResult(
        parity_score=parity_result.parity_score,
        vif_confidence=vif_confidence,
        combined_quality=combined_quality,
        parity_passes=parity_passes,
        confidence_passes=confidence_passes,
        overall_passes=overall_passes,
        warnings=warnings,
    )


# NL_TAG: VIF-SDFCVF-006 | Get NL tags from VIF witnesses for quintet parity. | get_nl_tags_from_witnesses(witnesses) | []
# NL_TAG_CONNECT: VIF-SDFCVF-006 | NL tags extracted from VIF witnesses | get_nl_tags_from_witnesses → NLTagParser | [VIF-SDFCVF-006, NL-TAGS-001]
# NL_TAG_INTENT: VIF-INTENT-021 | Design decision: quintet parity NL tags | get_nl_tags_from_witnesses | [ADR-VIF-SDFCVF]
def get_nl_tags_from_witnesses(
    witnesses: List[VIF],
) -> List[Any]:
    """
    Get NL tags from VIF witnesses for quintet parity.
    
    Extracts NL tags from VIF witnesses (if stored in tool_parameters or metadata).
    
    Args:
        witnesses: List of VIF witnesses
        
    Returns:
        List of NL tags (or empty list if not available)
        
    Examples:
        >>> witnesses = [vif1, vif2]
        >>> nl_tags = get_nl_tags_from_witnesses(witnesses)
        >>> assert isinstance(nl_tags, list)
    """
    if not VIF_AVAILABLE:
        return []
    
    nl_tags = []
    
    # Try to extract NL tags from witnesses
    # NL tags might be stored in tool_parameters or metadata
    for witness in witnesses:
        # Check tool_parameters for NL tags
        if witness.tool_parameters:
            tags = witness.tool_parameters.get("nl_tags", [])
            if tags:
                nl_tags.extend(tags)
        
        # Check metadata if available (future enhancement)
        if hasattr(witness, 'metadata') and witness.metadata:
            tags = witness.metadata.get("nl_tags", [])
            if tags:
                nl_tags.extend(tags)
    
    return nl_tags

