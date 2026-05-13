"""VIF Integration with HHNI (Hierarchical Hypergraph Neural Index)

Tracks RS-Lift metrics from HHNI retrieval operations and stores them in VIF witnesses.
Provides RS-Lift analysis and statistics for retrieval quality assessment.
"""

from __future__ import annotations

from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone

# HHNI imports (optional - gracefully handle if HHNI not available)
try:
    from packages.hhni.retrieval import RetrievalResult
    HHNI_AVAILABLE = True
except ImportError:
    try:
        from hhni.retrieval import RetrievalResult
        HHNI_AVAILABLE = True
    except ImportError:
        HHNI_AVAILABLE = False
        RetrievalResult = None

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
class RSLiftMetrics:
    """RS-Lift metrics for a single retrieval operation"""
    retrieval_id: str
    query: str
    rs_lift: float
    dvns_relevance: float
    baseline_relevance: float
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    witness_id: Optional[str] = None
    precision_at_k: Optional[float] = None
    efficiency: Optional[float] = None


@dataclass
class RSLiftStatistics:
    """Statistics for RS-Lift metrics over time"""
    total_retrievals: int
    average_rs_lift: float
    median_rs_lift: float
    min_rs_lift: float
    max_rs_lift: float
    positive_lift_count: int
    negative_lift_count: int
    zero_lift_count: int
    average_precision_at_k: Optional[float] = None
    average_efficiency: Optional[float] = None


# NL_TAG: VIF-HHNI-001 | Extract RS-Lift metrics from HHNI RetrievalResult. | extract_rs_lift_metrics(retrieval_result, query, retrieval_id) | []
# NL_TAG_CONNECT: VIF-HHNI-001 | RS-Lift extracted from HHNI RetrievalResult | extract_rs_lift_metrics → RetrievalResult.rs_lift | [VIF-HHNI-001, HHNI-RETRIEVE-001]
# NL_TAG_INTENT: VIF-INTENT-012 | Design decision: RS-Lift tracking | extract_rs_lift_metrics | [ADR-VIF-HHNI]
def extract_rs_lift_metrics(
    retrieval_result: RetrievalResult,
    query: str,
    retrieval_id: Optional[str] = None,
) -> RSLiftMetrics:
    """
    Extract RS-Lift metrics from HHNI RetrievalResult.
    
    Args:
        retrieval_result: HHNI RetrievalResult instance
        query: Query string used for retrieval
        retrieval_id: Optional retrieval ID (if not provided, generates one)
        
    Returns:
        RSLiftMetrics with extracted metrics
        
    Examples:
        >>> from hhni.retrieval import RetrievalResult
        >>> result = RetrievalResult(selected_items=[], total_tokens=100, ...)
        >>> metrics = extract_rs_lift_metrics(result, "test query")
        >>> assert metrics.rs_lift is not None
    """
    if not HHNI_AVAILABLE:
        raise ImportError("HHNI not available - cannot extract RS-Lift metrics")
    
    if retrieval_id is None:
        retrieval_id = f"retrieval_{datetime.now(timezone.utc).timestamp()}"
    
    # Extract RS-Lift from RetrievalResult
    rs_lift = retrieval_result.rs_lift if retrieval_result.rs_lift is not None else 0.0
    
    # Extract relevance scores
    dvns_relevance = retrieval_result.relevance_score
    baseline_relevance = dvns_relevance / (1.0 + rs_lift) if rs_lift != -1.0 else dvns_relevance
    
    # Extract precision and efficiency if available
    precision_at_k = None
    if hasattr(retrieval_result, 'precision_at_k'):
        precision_at_k = retrieval_result.precision_at_k
    
    efficiency = retrieval_result.efficiency if hasattr(retrieval_result, 'efficiency') else None
    
    return RSLiftMetrics(
        retrieval_id=retrieval_id,
        query=query,
        rs_lift=rs_lift,
        dvns_relevance=dvns_relevance,
        baseline_relevance=baseline_relevance,
        precision_at_k=precision_at_k,
        efficiency=efficiency,
    )


# NL_TAG: VIF-HHNI-002 | Store RS-Lift metrics in VIF witness metadata. | store_rs_lift_in_witness(vif, rs_lift_metrics) | []
# NL_TAG_CONNECT: VIF-HHNI-002 | RS-Lift stored in VIF witness tool_parameters | store_rs_lift_in_witness → VIF.tool_parameters | [VIF-HHNI-002, VIF-WITNESS-001]
# NL_TAG_INTENT: VIF-INTENT-013 | Design decision: RS-Lift provenance | store_rs_lift_in_witness | [ADR-VIF-HHNI]
def store_rs_lift_in_witness(
    vif: VIF,
    rs_lift_metrics: RSLiftMetrics,
) -> VIF:
    """
    Store RS-Lift metrics in VIF witness metadata.
    
    Stores RS-Lift metrics in VIF witness tool_parameters for provenance tracking.
    
    Args:
        vif: VIF witness instance
        rs_lift_metrics: RS-Lift metrics to store
        
    Returns:
        Updated VIF witness with RS-Lift metrics
        
    Examples:
        >>> vif = VIF(model_id="gpt-4", ...)
        >>> metrics = RSLiftMetrics(retrieval_id="ret_123", query="test", rs_lift=0.15, ...)
        >>> updated_vif = store_rs_lift_in_witness(vif, metrics)
        >>> assert "rs_lift_metrics" in updated_vif.tool_parameters
    """
    # VIF should be available if we got this far (vif parameter is a VIF instance)
    # The import check is mainly for documentation/clarity
    
    # Store RS-Lift metrics in tool_parameters
    if vif.tool_parameters is None:
        vif.tool_parameters = {}
    
    vif.tool_parameters["rs_lift_metrics"] = {
        "retrieval_id": rs_lift_metrics.retrieval_id,
        "query": rs_lift_metrics.query,
        "rs_lift": rs_lift_metrics.rs_lift,
        "dvns_relevance": rs_lift_metrics.dvns_relevance,
        "baseline_relevance": rs_lift_metrics.baseline_relevance,
        "precision_at_k": rs_lift_metrics.precision_at_k,
        "efficiency": rs_lift_metrics.efficiency,
        "timestamp": rs_lift_metrics.timestamp.isoformat(),
    }
    
    # Link witness ID to metrics
    rs_lift_metrics.witness_id = vif.id
    
    return vif


# NL_TAG: VIF-HHNI-003 | Calculate RS-Lift statistics from VIF witnesses. | calculate_rs_lift_statistics(witness_ids, limit) | []
# NL_TAG_CONNECT: VIF-HHNI-003 | RS-Lift stats calculated from VIFStore | calculate_rs_lift_statistics → VIFStore.get_witness | [VIF-HHNI-003, CMC-STORE-001]
# NL_TAG_INTENT: VIF-INTENT-014 | Design decision: RS-Lift analytics | calculate_rs_lift_statistics | [ADR-VIF-HHNI]
def calculate_rs_lift_statistics(
    vif_store: Optional[Any] = None,
    witness_ids: Optional[List[str]] = None,
    limit: int = 1000,
) -> RSLiftStatistics:
    """
    Calculate RS-Lift statistics from VIF witnesses.
    
    Queries VIF witnesses for RS-Lift metrics and calculates statistics.
    
    Args:
        vif_store: Optional VIFStore instance (for testing). If None, creates from CMC.
        witness_ids: Optional list of witness IDs to analyze (if None, queries recent witnesses)
        limit: Maximum number of witnesses to analyze
        
    Returns:
        RSLiftStatistics with calculated statistics
        
    Examples:
        >>> stats = calculate_rs_lift_statistics(limit=100)
        >>> assert stats.average_rs_lift >= 0.0
    """
    if not VIF_AVAILABLE:
        return RSLiftStatistics(
            total_retrievals=0,
            average_rs_lift=0.0,
            median_rs_lift=0.0,
            min_rs_lift=0.0,
            max_rs_lift=0.0,
            positive_lift_count=0,
            negative_lift_count=0,
            zero_lift_count=0,
        )
    
    try:
        # Get VIFStore (use provided store or create from CMC)
        if vif_store is None:
            if get_memory_store is None:
                return RSLiftStatistics(
                    total_retrievals=0,
                    average_rs_lift=0.0,
                    median_rs_lift=0.0,
                    min_rs_lift=0.0,
                    max_rs_lift=0.0,
                    positive_lift_count=0,
                    negative_lift_count=0,
                    zero_lift_count=0,
                )
            cmc_store = get_memory_store()
            vif_store = VIFStore(cmc_store)
        
        # Collect RS-Lift metrics from witnesses
        rs_lift_values = []
        precision_values = []
        efficiency_values = []
        
        if witness_ids:
            # Query specific witnesses
            for witness_id in witness_ids[:limit]:
                witness = vif_store.get_witness(witness_id)
                if witness and witness.tool_parameters:
                    metrics = witness.tool_parameters.get("rs_lift_metrics")
                    if metrics:
                        rs_lift_values.append(metrics.get("rs_lift", 0.0))
                        if metrics.get("precision_at_k") is not None:
                            precision_values.append(metrics["precision_at_k"])
                        if metrics.get("efficiency") is not None:
                            efficiency_values.append(metrics["efficiency"])
        else:
            # Query recent witnesses using query_witnesses if available
            if hasattr(vif_store, 'query_witnesses'):
                witnesses = vif_store.query_witnesses(limit=limit)
                for witness in witnesses:
                    if witness and witness.tool_parameters:
                        metrics = witness.tool_parameters.get("rs_lift_metrics")
                        if metrics:
                            rs_lift_values.append(metrics.get("rs_lift", 0.0))
                            if metrics.get("precision_at_k") is not None:
                                precision_values.append(metrics["precision_at_k"])
                            if metrics.get("efficiency") is not None:
                                efficiency_values.append(metrics["efficiency"])
        
        if not rs_lift_values:
            return RSLiftStatistics(
                total_retrievals=0,
                average_rs_lift=0.0,
                median_rs_lift=0.0,
                min_rs_lift=0.0,
                max_rs_lift=0.0,
                positive_lift_count=0,
                negative_lift_count=0,
                zero_lift_count=0,
            )
        
        # Calculate statistics
        sorted_lifts = sorted(rs_lift_values)
        n = len(rs_lift_values)
        
        average_rs_lift = sum(rs_lift_values) / n
        median_rs_lift = sorted_lifts[n // 2] if n > 0 else 0.0
        min_rs_lift = sorted_lifts[0] if sorted_lifts else 0.0
        max_rs_lift = sorted_lifts[-1] if sorted_lifts else 0.0
        
        positive_lift_count = sum(1 for lift in rs_lift_values if lift > 0.0)
        negative_lift_count = sum(1 for lift in rs_lift_values if lift < 0.0)
        zero_lift_count = sum(1 for lift in rs_lift_values if lift == 0.0)
        
        average_precision = sum(precision_values) / len(precision_values) if precision_values else None
        average_efficiency = sum(efficiency_values) / len(efficiency_values) if efficiency_values else None
        
        return RSLiftStatistics(
            total_retrievals=n,
            average_rs_lift=average_rs_lift,
            median_rs_lift=median_rs_lift,
            min_rs_lift=min_rs_lift,
            max_rs_lift=max_rs_lift,
            positive_lift_count=positive_lift_count,
            negative_lift_count=negative_lift_count,
            zero_lift_count=zero_lift_count,
            average_precision_at_k=average_precision,
            average_efficiency=average_efficiency,
        )
    except Exception as e:
        # Graceful degradation
        return RSLiftStatistics(
            total_retrievals=0,
            average_rs_lift=0.0,
            median_rs_lift=0.0,
            min_rs_lift=0.0,
            max_rs_lift=0.0,
            positive_lift_count=0,
            negative_lift_count=0,
            zero_lift_count=0,
        )


# NL_TAG: VIF-HHNI-004 | Create VIF witness for HHNI retrieval operation. | create_retrieval_witness(retrieval_result, query, confidence, context_snapshot_id) | []
# NL_TAG_CONNECT: VIF-HHNI-004 | Retrieval witness created with RS-Lift metrics | create_retrieval_witness → extract_rs_lift_metrics → store_rs_lift_in_witness | [VIF-HHNI-004, VIF-HHNI-001, VIF-HHNI-002]
# NL_TAG_INTENT: VIF-INTENT-015 | Design decision: retrieval provenance | create_retrieval_witness | [ADR-VIF-HHNI]
def create_retrieval_witness(
    retrieval_result: RetrievalResult,
    context_snapshot_id: str,
    query: str = "",
    confidence: float = 0.95,
    model_id: str = "hhni-retriever",
    model_provider: str = "aim-os",
    **kwargs,
) -> VIF:
    """
    Create VIF witness for HHNI retrieval operation.
    
    Creates a VIF witness for a retrieval operation, including RS-Lift metrics.
    
    Args:
        retrieval_result: HHNI RetrievalResult instance
        query: Query string used for retrieval
        confidence: Confidence score for retrieval (0.0-1.0)
        context_snapshot_id: CMC snapshot ID for context
        model_id: Model identifier (default: "hhni-retriever")
        model_provider: Model provider (default: "aim-os")
        **kwargs: Additional VIF witness parameters
        
    Returns:
        VIF witness with RS-Lift metrics stored
        
    Examples:
        >>> from hhni.retrieval import RetrievalResult
        >>> result = RetrievalResult(selected_items=[], total_tokens=100, ...)
        >>> vif = create_retrieval_witness(result, "test query", 0.85, "snap_123")
        >>> assert vif.tool_parameters.get("rs_lift_metrics") is not None
    """
    # Import VIF (try multiple paths for test compatibility)
    try:
        from packages.vif.witness import VIF, ConfidenceBand, TaskCriticality
        from packages.vif.confidence_bands import determine_band
    except ImportError:
        try:
            from vif.witness import VIF, ConfidenceBand, TaskCriticality
            from vif.confidence_bands import determine_band
        except ImportError:
            if not HHNI_AVAILABLE:
                raise ImportError("VIF or HHNI not available - cannot create retrieval witness")
            raise ImportError("VIF not available - cannot create retrieval witness")
    
    if not HHNI_AVAILABLE:
        raise ImportError("HHNI not available - cannot create retrieval witness")
    
    # Extract RS-Lift metrics
    rs_lift_metrics = extract_rs_lift_metrics(retrieval_result, query)
    
    # Create VIF witness
    vif = VIF(
        model_id=model_id,
        model_provider=model_provider,
        context_snapshot_id=context_snapshot_id,
        prompt_hash="",  # Retrieval doesn't have a prompt hash
        prompt_tokens=0,
        confidence_score=confidence,
        confidence_band=determine_band(confidence),
        output_hash="",  # Retrieval doesn't have an output hash
        output_tokens=retrieval_result.total_tokens,
        total_tokens=retrieval_result.total_tokens,
        task_criticality=TaskCriticality.ROUTINE,  # Retrieval is typically routine
        tool_ids=["hhni.retrieve"],
        tool_parameters={},
        **kwargs,
    )
    
    # Store RS-Lift metrics in witness
    vif = store_rs_lift_in_witness(vif, rs_lift_metrics)
    
    return vif

