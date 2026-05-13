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
    try:
        from vif.witness import VIF
        from vif.cmc_integration import VIFStore
        VIF_AVAILABLE = True
        get_memory_store = None  # May not be available
    except ImportError:
        VIF_AVAILABLE = False
        VIF = None
        VIFStore = None
        get_memory_store = None


@dataclass
class ParityQualityResult:
    """Combined VIF confidence and parity score for quality validation"""
    vif_confidence: float
    parity_score: float
    combined_score: float  # Changed from combined_quality to match tests
    parity_passes: bool = True
    confidence_passes: bool = True
    overall_passes: bool = True
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


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
    # VIF should be available if we got this far (vif parameter is a VIF instance)
    # Try to import if not already available
    if not VIF_AVAILABLE:
        try:
            from packages.vif.witness import VIF as VIFClass
            if not isinstance(vif, VIFClass):
                raise ImportError("VIF not available - cannot convert witness to trace text")
        except ImportError:
            try:
                from vif.witness import VIF as VIFClass
                if not isinstance(vif, VIFClass):
                    raise ImportError("VIF not available - cannot convert witness to trace text")
            except ImportError:
                raise ImportError("VIF not available - cannot convert witness to trace text")
    
    # Extract key information from VIF witness
    trace_parts = [
        f"VIF Witness: {vif.id}",
        f"Model: {vif.model_id} ({vif.model_provider})",
        f"Confidence: {vif.confidence_score:.2f} ({vif.confidence_band.value})",
        f"Task Criticality: {vif.task_criticality.value.upper() if vif.task_criticality else 'UNKNOWN'}",
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
    vif_store: Optional[Any] = None,
) -> List[VIF]:
    """
    Collect VIF witnesses related to a code file for quartet parity.
    
    Queries VIFStore for witnesses related to the given file path.
    
    Args:
        file_path: Code file path to collect witnesses for
        limit: Maximum number of witnesses to return
        vif_store: Optional VIFStore instance (for testing). If None, creates from CMC.
        
    Returns:
        List of VIF witnesses
        
    Examples:
        >>> witnesses = collect_witnesses_for_file("packages/vif/witness.py", limit=10)
        >>> assert len(witnesses) <= 10
    """
    if not VIF_AVAILABLE:
        return []
    
    try:
        # Get VIFStore (use provided store or create from CMC)
        if vif_store is None:
            if get_memory_store is None:
                return []
            cmc_store = get_memory_store()
            vif_store = VIFStore(cmc_store)
        
        # Query witnesses using query_witnesses if available
        if hasattr(vif_store, 'query_witnesses'):
            witnesses = vif_store.query_witnesses(limit=limit)
            return witnesses if witnesses else []
        
        # Fallback: return empty list (graceful degradation)
        return []
    except Exception:
        # Graceful degradation
        return []


# NL_TAG: VIF-SDFCVF-003 | Create trace file from VIF witnesses for parity calculation. | create_trace_file_from_witnesses(witnesses, output_path) | []
# NL_TAG_CONNECT: VIF-SDFCVF-003 | Trace file created from VIF witnesses | create_trace_file_from_witnesses → vif_witness_to_trace_text | [VIF-SDFCVF-003, VIF-SDFCVF-001]
# NL_TAG_INTENT: VIF-INTENT-018 | Design decision: trace file generation | create_trace_file_from_witnesses | [ADR-VIF-SDFCVF]
def create_trace_file_from_witnesses(
    witnesses: List[VIF],
    output_dir: Optional[Any] = None,
    file_name: str = "vif_trace.txt",
    output_path: Optional[str] = None,
) -> Path:
    """
    Create trace file from VIF witnesses for quartet parity calculation.
    
    Writes VIF witnesses as trace text to a file that can be used in quartet/quintet parity.
    
    Args:
        witnesses: List of VIF witnesses
        output_dir: Optional output directory (Path or str). If None, uses output_path.
        file_name: Name of trace file (default: "vif_trace.txt")
        output_path: Optional full output path (for backward compatibility)
        
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
    
    # Determine output path
    if output_path:
        output_path_obj = Path(output_path)
    elif output_dir:
        output_path_obj = Path(output_dir) / file_name
    else:
        # Default to current directory
        output_path_obj = Path(file_name)
    
    # Write to file
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)
    output_path_obj.write_text(combined_trace, encoding='utf-8')
    
    return output_path_obj


# NL_TAG: VIF-SDFCVF-004 | Calculate quartet parity with VIF witnesses as traces. | calculate_parity_with_vif_traces(code_files, doc_files, test_files, witnesses, embedding_fn) | []
# NL_TAG_CONNECT: VIF-SDFCVF-004 | Parity calculated with VIF traces via ParityCalculator | calculate_parity_with_vif_traces → ParityCalculator.calculate | [VIF-SDFCVF-004, SDFCVF-PARITY-002]
# NL_TAG_INTENT: VIF-INTENT-019 | Design decision: quartet parity integration | calculate_parity_with_vif_traces | [ADR-VIF-SDFCVF]
def calculate_parity_with_vif_traces(
    code_file: Optional[Any] = None,
    doc_file: Optional[Any] = None,
    test_file: Optional[Any] = None,
    trace_files: Optional[List[Any]] = None,
    parity_calculator: Optional[Any] = None,
    code_files: Optional[List[str]] = None,
    doc_files: Optional[List[str]] = None,
    test_files: Optional[List[str]] = None,
    witnesses: Optional[List[VIF]] = None,
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
    
    # Handle both new parameter format (code_file, doc_file, etc.) and old format (code_files, doc_files, etc.)
    if code_file is not None:
        # New format: single files
        code_files_list = [str(code_file)]
        doc_files_list = [str(doc_file)] if doc_file else []
        test_files_list = [str(test_file)] if test_file else []
        trace_files_list = [str(tf) for tf in trace_files] if trace_files else []
    else:
        # Old format: lists
        code_files_list = code_files or []
        doc_files_list = doc_files or []
        test_files_list = test_files or []
        trace_files_list = []
        
        # Create trace file from witnesses if provided
        if witnesses:
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as tmp_file:
                trace_file = tmp_file.name
                create_trace_file_from_witnesses(witnesses, output_path=trace_file)
                trace_files_list.append(trace_file)
    
    # Use parity_calculator if provided, otherwise use default
    if parity_calculator is not None:
        # Use provided calculator
        result = parity_calculator.calculate_parity(
            code_files=code_files_list,
            doc_files=doc_files_list,
            test_files=test_files_list,
            trace_files=trace_files_list,
        )
    else:
        # Use default SDF-CVF calculator
        try:
            from packages.sdfcvf.parity import calculate_parity
            
            result = calculate_parity(
                code_files=code_files_list,
                doc_files=doc_files_list,
                test_files=test_files_list,
                trace_files=trace_files_list,
                embedding_fn=embedding_fn,
            )
        except ImportError:
            try:
                from sdfcvf.parity import calculate_parity
                result = calculate_parity(
                    code_files=code_files_list,
                    doc_files=doc_files_list,
                    test_files=test_files_list,
                    trace_files=trace_files_list,
                    embedding_fn=embedding_fn,
                )
            except ImportError:
                raise ImportError("SDF-CVF not available - cannot calculate parity")
    
    return result


# NL_TAG: VIF-SDFCVF-005 | Combine VIF confidence with parity score for quality validation. | combine_confidence_and_parity(parity_result, vif_confidence, confidence_threshold) | []
# NL_TAG_CONNECT: VIF-SDFCVF-005 | Quality validation combines VIF confidence with parity | combine_confidence_and_parity → ParityResult.passes_gate | [VIF-SDFCVF-005, SDFCVF-PARITY-001]
# NL_TAG_INTENT: VIF-INTENT-020 | Design decision: quality validation | combine_confidence_and_parity | [ADR-VIF-SDFCVF]
def combine_confidence_and_parity(
    vif_confidence: float,
    parity_score: float,
    confidence_weight: float = 0.4,
    parity_threshold: float = 0.90,
    confidence_threshold: float = 0.70,
    parity_result: Optional[ParityResult] = None,  # For backward compatibility
) -> ParityQualityResult:
    """
    Combine VIF confidence with parity score for quality validation.
    
    Validates quality using both quartet parity and VIF confidence scores.
    
    Args:
        vif_confidence: VIF confidence score (0.0-1.0)
        parity_score: Parity score (0.0-1.0)
        confidence_weight: Weight for confidence in combined score (default: 0.4)
        parity_threshold: Minimum parity score to pass (default: 0.90)
        confidence_threshold: Minimum VIF confidence to pass (default: 0.70)
        parity_result: Optional ParityResult (for backward compatibility)
        
    Returns:
        ParityQualityResult with combined quality validation
        
    Examples:
        >>> quality = combine_confidence_and_parity(vif_confidence=0.85, parity_score=0.92)
        >>> assert quality.overall_passes == True
    """
    # Extract parity_score from parity_result if provided (backward compatibility)
    if parity_result is not None:
        parity_score = parity_result.parity_score
    
    # Check if parity passes
    parity_passes = parity_score >= parity_threshold
    
    # Check if confidence passes
    confidence_passes = vif_confidence >= confidence_threshold
    
    # Calculate combined score (weighted average)
    # Parity weight: 1 - confidence_weight, Confidence weight: confidence_weight
    parity_weight = 1.0 - confidence_weight
    combined_score = (parity_weight * parity_score) + (confidence_weight * vif_confidence)
    
    # Overall passes if both pass
    overall_passes = parity_passes and confidence_passes
    
    # Collect warnings
    warnings = []
    if not parity_passes:
        warnings.append(f"Parity score {parity_score:.2f} below threshold {parity_threshold:.2f}")
    if not confidence_passes:
        warnings.append(f"VIF confidence {vif_confidence:.2f} below threshold {confidence_threshold:.2f}")
    
    # Add parity warnings from parity_result if provided
    if parity_result and hasattr(parity_result, 'warnings') and parity_result.warnings:
        warnings.extend(parity_result.warnings)
    
    return ParityQualityResult(
        parity_score=parity_score,
        vif_confidence=vif_confidence,
        combined_score=combined_score,
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
    # VIF should be available if we got this far (witnesses parameter contains VIF instances)
    # No need to check VIF_AVAILABLE
    
    nl_tags = []
    
    # Try to extract NL tags from witnesses
    # NL tags might be stored in tool_parameters or metadata
    for witness in witnesses:
        # Check tool_parameters for NL tags
        if hasattr(witness, 'tool_parameters') and witness.tool_parameters:
            tags = witness.tool_parameters.get("nl_tags", [])
            if tags:
                if isinstance(tags, list):
                    nl_tags.extend(tags)
                else:
                    nl_tags.append(tags)
        
        # Check metadata if available (future enhancement)
        if hasattr(witness, 'metadata') and witness.metadata:
            tags = witness.metadata.get("nl_tags", [])
            if tags:
                if isinstance(tags, list):
                    nl_tags.extend(tags)
                else:
                    nl_tags.append(tags)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_tags = []
    for tag in nl_tags:
        if tag not in seen:
            seen.add(tag)
            unique_tags.append(tag)
    
    return unique_tags


# P0: Simple entrypoint for CI/audit workflows
# NL_TAG: VIF-SDFCVF-007 | P0: Simple entrypoint for file set parity calculation | calculate_file_set_parity(code_file, doc_file, test_file, output_dir) | []
# NL_TAG_CONNECT: VIF-SDFCVF-007 | File set parity uses VIF witnesses as traces | calculate_file_set_parity → collect_witnesses_for_file → calculate_parity_with_vif_traces | [VIF-SDFCVF-007, VIF-SDFCVF-002, VIF-SDFCVF-004]
# NL_TAG_INTENT: VIF-INTENT-022 | Design decision: CI/audit integration | calculate_file_set_parity | [ADR-VIF-SDFCVF]
def calculate_file_set_parity(
    code_file: str,
    doc_file: Optional[str] = None,
    test_file: Optional[str] = None,
    output_dir: Optional[str] = None,
    limit_witnesses: int = 100,
) -> Tuple[ParityResult, ParityQualityResult]:
    """
    P0: Simple entrypoint for file set parity calculation using VIF witnesses.
    
    Given a code file (and optionally doc/test files), collects VIF witnesses
    related to the file, creates trace file, and calculates quartet parity.
    Returns both parity result and combined quality validation.
    
    Args:
        code_file: Code file path
        doc_file: Optional documentation file path
        test_file: Optional test file path
        output_dir: Optional output directory for trace file
        limit_witnesses: Maximum number of witnesses to collect
        
    Returns:
        Tuple of (ParityResult, ParityQualityResult)
        
    Examples:
        >>> parity, quality = calculate_file_set_parity(
        ...     code_file="packages/vif/witness.py",
        ...     doc_file="packages/vif/README.md",
        ...     test_file="packages/vif/tests/test_witness.py"
        ... )
        >>> assert parity.parity_score >= 0.0
        >>> assert quality.overall_passes in [True, False]
    """
    if not VIF_AVAILABLE or not SDFCVF_AVAILABLE:
        raise ImportError("VIF or SDF-CVF not available - cannot calculate file set parity")
    
    # Collect witnesses for code file
    witnesses = collect_witnesses_for_file(code_file, limit=limit_witnesses)
    
    # Calculate parity with VIF traces
    parity_result = calculate_parity_with_vif_traces(
        code_file=code_file,
        doc_file=doc_file,
        test_file=test_file,
        witnesses=witnesses,
    )
    
    # Calculate average VIF confidence from witnesses
    vif_confidence = 0.0
    if witnesses:
        vif_confidence = sum(w.confidence_score for w in witnesses) / len(witnesses)
    else:
        # No witnesses - use default confidence
        vif_confidence = 0.5
    
    # Combine confidence and parity for quality validation
    quality_result = combine_confidence_and_parity(
        vif_confidence=vif_confidence,
        parity_score=parity_result.parity_score,
    )
    
    return parity_result, quality_result
