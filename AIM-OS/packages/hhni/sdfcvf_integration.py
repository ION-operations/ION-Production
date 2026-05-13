"""HHNI ↔ SDF-CVF Integration - Quartet Parity Validation Hooks

Enables SDF-CVF quartet parity validation for HHNI retrieval operations.
Validates that retrieved code/docs/tests/traces are aligned (parity ≥ 0.90).

Integration Points:
- Quartet detection from retrieved file paths
- Parity validation using SDF-CVF
- Parity metadata in retrieval results
- Optional parity gating (can filter low-parity results)
"""

from __future__ import annotations

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# SDF-CVF imports (optional, fail-soft)
try:
    from packages.sdfcvf.quartet import Quartet, FileClassification, QuartetDetector
    from packages.sdfcvf.parity import ParityCalculator, ParityResult
    SDFCVF_AVAILABLE = True
except ImportError:
    SDFCVF_AVAILABLE = False
    Quartet = None
    FileClassification = None
    QuartetDetector = None
    ParityCalculator = None
    ParityResult = None

logger = logging.getLogger(__name__)


@dataclass
class QuartetParityInfo:
    """Quartet parity information for a retrieved item"""
    file_path: str
    quartet: Optional[Quartet] = None
    parity_result: Optional[ParityResult] = None
    parity_score: float = 0.0
    passes_gate: bool = False
    validation_error: Optional[str] = None


def validate_retrieval_parity(
    retrieved_file_paths: List[str],
    repo_root: Optional[str] = None,
    parity_threshold: float = 0.90,
    enable_gating: bool = False
) -> Dict[str, QuartetParityInfo]:
    """
    Validate quartet parity for retrieved file paths.
    
    For each retrieved file, attempts to:
    1. Detect its quartet (code/docs/tests/traces)
    2. Calculate parity score using SDF-CVF
    3. Check if parity passes threshold (≥ 0.90)
    
    Args:
        retrieved_file_paths: List of file paths from HHNI retrieval
        repo_root: Repository root path (defaults to current directory)
        parity_threshold: Minimum parity score to pass (default: 0.90)
        enable_gating: If True, filter out low-parity results (default: False)
    
    Returns:
        Dictionary mapping file paths to QuartetParityInfo
    """
    if not SDFCVF_AVAILABLE:
        logger.warning("SDF-CVF not available, skipping quartet parity validation")
        return {
            path: QuartetParityInfo(
                file_path=path,
                validation_error="SDF-CVF not available"
            )
            for path in retrieved_file_paths
        }
    
    parity_info: Dict[str, QuartetParityInfo] = {}
    detector = QuartetDetector(repo_root=repo_root)
    calculator = ParityCalculator(repo_root=repo_root)
    
    for file_path in retrieved_file_paths:
        try:
            # Classify the file and create a minimal quartet
            # For HHNI retrieval, we validate the retrieved file itself
            # If related files exist, we can validate the full quartet
            file_classification = detector.classify_file(file_path)
            
            # Create quartet with just this file (will be incomplete, but that's okay)
            quartet = Quartet()
            if file_classification == FileClassification.CODE:
                quartet.code_files.append(file_path)
            elif file_classification == FileClassification.DOCS:
                quartet.doc_files.append(file_path)
            elif file_classification == FileClassification.TESTS:
                quartet.test_files.append(file_path)
            elif file_classification == FileClassification.TRACES:
                quartet.trace_files.append(file_path)
            else:
                # Unknown file type - skip validation
                parity_info[file_path] = QuartetParityInfo(
                    file_path=file_path,
                    validation_error="Unknown file classification"
                )
                continue
            
            # Try to find related quartet files (code/docs/tests/traces)
            # This is a best-effort attempt - if we can't find them, we validate what we have
            try:
                related_quartet = detector.detect_related_quartet(file_path)
                if related_quartet and related_quartet.is_complete():
                    # Use the complete related quartet
                    quartet = related_quartet
            except (NotImplementedError, Exception):
                # detect_related_quartet not implemented or failed - use single-file quartet
                pass
            
            if not quartet.is_complete():
                # Incomplete quartet - log warning but don't fail
                # This is expected for single-file retrievals
                parity_info[file_path] = QuartetParityInfo(
                    file_path=file_path,
                    quartet=quartet,
                    parity_score=0.50,  # Incomplete = low parity
                    passes_gate=False,
                    validation_error="Incomplete quartet (missing elements - expected for single-file retrieval)"
                )
                continue
            
            # Calculate parity
            parity_result = calculator.calculate(quartet)
            
            # Check if passes gate
            passes = parity_result.passes_gate(threshold=parity_threshold)
            
            parity_info[file_path] = QuartetParityInfo(
                file_path=file_path,
                quartet=quartet,
                parity_result=parity_result,
                parity_score=parity_result.parity_score,
                passes_gate=passes
            )
            
            if not passes:
                logger.warning(
                    f"Low parity for {file_path}: {parity_result.parity_score:.2f} < {parity_threshold}"
                )
        
        except Exception as e:
            logger.error(f"Error validating parity for {file_path}: {e}")
            parity_info[file_path] = QuartetParityInfo(
                file_path=file_path,
                validation_error=str(e)
            )
    
    return parity_info


def filter_by_parity(
    retrieved_file_paths: List[str],
    parity_info: Dict[str, QuartetParityInfo],
    parity_threshold: float = 0.90
) -> List[str]:
    """
    Filter retrieved file paths by parity threshold.
    
    Args:
        retrieved_file_paths: Original list of file paths
        parity_info: Parity information from validate_retrieval_parity()
        parity_threshold: Minimum parity score to keep
    
    Returns:
        Filtered list of file paths that pass parity threshold
    """
    filtered = []
    for path in retrieved_file_paths:
        info = parity_info.get(path)
        if info and info.passes_gate:
            filtered.append(path)
        elif info and info.parity_score >= parity_threshold:
            filtered.append(path)
        else:
            logger.debug(f"Filtered out {path} (parity: {info.parity_score if info else 'unknown'})")
    
    return filtered


def add_parity_metadata_to_result(
    retrieval_result: "RetrievalResult",
    parity_info: Dict[str, QuartetParityInfo]
) -> None:
    """
    Add quartet parity metadata to RetrievalResult audit trail.
    
    Args:
        retrieval_result: HHNI RetrievalResult to update
        parity_info: Parity information from validate_retrieval_parity()
    """
    if not hasattr(retrieval_result, 'audit_trail'):
        return
    
    # Calculate aggregate parity statistics
    parity_scores = [
        info.parity_score
        for info in parity_info.values()
        if info.parity_result is not None
    ]
    
    if parity_scores:
        avg_parity = sum(parity_scores) / len(parity_scores)
        min_parity = min(parity_scores)
        max_parity = max(parity_scores)
        passing_count = sum(1 for info in parity_info.values() if info.passes_gate)
        
        retrieval_result.audit_trail["sdfcvf_parity_validation"] = "enabled"
        retrieval_result.audit_trail["sdfcvf_avg_parity"] = f"{avg_parity:.3f}"
        retrieval_result.audit_trail["sdfcvf_min_parity"] = f"{min_parity:.3f}"
        retrieval_result.audit_trail["sdfcvf_max_parity"] = f"{max_parity:.3f}"
        retrieval_result.audit_trail["sdfcvf_passing_count"] = str(passing_count)
        retrieval_result.audit_trail["sdfcvf_total_validated"] = str(len(parity_scores))
    else:
        retrieval_result.audit_trail["sdfcvf_parity_validation"] = "no_quartets_found"


def validate_retrieval_result_parity(
    retrieval_result: "RetrievalResult",
    repo_root: Optional[str] = None,
    parity_threshold: float = 0.90,
    enable_gating: bool = False
) -> Dict[str, QuartetParityInfo]:
    """
    Validate quartet parity for all files in a RetrievalResult.
    
    Extracts file paths from retrieval result and validates quartet parity.
    
    Args:
        retrieval_result: HHNI RetrievalResult
        repo_root: Repository root path
        parity_threshold: Minimum parity score (default: 0.90)
        enable_gating: If True, filter low-parity results (default: False)
    
    Returns:
        Dictionary mapping file paths to QuartetParityInfo
    """
    # Extract file paths from retrieval result
    file_paths = []
    for item in retrieval_result.selected_items:
        if hasattr(item, 'node') and hasattr(item.node, 'path'):
            file_paths.append(item.node.path)
        elif hasattr(item, 'path'):
            file_paths.append(item.path)
    
    if not file_paths:
        logger.debug("No file paths found in retrieval result")
        return {}
    
    # Validate parity
    parity_info = validate_retrieval_parity(
        retrieved_file_paths=file_paths,
        repo_root=repo_root,
        parity_threshold=parity_threshold,
        enable_gating=enable_gating
    )
    
    # Add metadata to result
    add_parity_metadata_to_result(retrieval_result, parity_info)
    
    return parity_info

