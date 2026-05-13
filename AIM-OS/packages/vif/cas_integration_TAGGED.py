"""VIF Integration with CAS (Cognitive Analysis System)

Adds cognitive context to VIF witness envelopes, tracking how AI thought during
operations. Enhances confidence calibration based on cognitive state.

Based on CAS documentation: CAS adds cognitive context to witness envelopes
(how AI thought during operation), enhances confidence calibration.
"""

from __future__ import annotations

from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import logging

# CAS imports (optional - gracefully handle if CAS not available)
try:
    from packages.cas.activation import ActivationState
    CAS_AVAILABLE = True
except ImportError:
    try:
        from cas.activation import ActivationState
        CAS_AVAILABLE = True
    except ImportError:
        CAS_AVAILABLE = False
        ActivationState = None

# VIF imports
try:
    from packages.vif.witness import VIF, ConfidenceBand
except ImportError:
    from vif.witness import VIF, ConfidenceBand

logger = logging.getLogger(__name__)


@dataclass
class CognitiveContext:
    """Cognitive context data for VIF witness envelopes
    
    Captures how AI thought during operation, including activation state,
    task categorization, attention monitoring, and failure mode analysis.
    """
    # Activation state
    activation_state: Optional[Dict[str, Any]] = None  # ActivationState serialized
    principles_activation: Dict[str, float] = field(default_factory=dict)  # principle -> activation
    documents_activation: Dict[str, float] = field(default_factory=dict)  # doc -> activation
    concepts_activation: Dict[str, float] = field(default_factory=dict)  # concept -> activation
    
    # Task categorization
    task_category: Optional[str] = None  # How task was classified
    task_category_confidence: Optional[float] = None  # Confidence in categorization
    categorization_error: Optional[bool] = None  # Whether categorization was wrong
    
    # Attention monitoring
    cognitive_load: Optional[float] = None  # 0.0-1.0
    attention_breadth: Optional[str] = None  # "narrow" | "comprehensive"
    attention_narrowing: Optional[bool] = None  # Warning sign of degradation
    shortcuts_appearing: Optional[bool] = None  # Warning sign of degradation
    
    # Failure mode analysis
    failure_mode_detected: Optional[str] = None  # Type of failure mode if detected
    activation_gap: Optional[List[str]] = None  # Principles that should be hot but aren't
    procedure_gap: Optional[bool] = None  # Knowledge without how-to
    
    # Cognitive state metadata
    session_id: Optional[str] = None
    timestamp: Optional[datetime] = None
    context_size_tokens: Optional[int] = None
    working_attention_items: Optional[int] = None


# NL_TAG: VIF-CAS-001 | Extract cognitive context from CAS for VIF witness | extract_cognitive_context(cas_state) -> CognitiveContext | []
# NL_TAG_CONNECT: VIF-CAS-001 | Cognitive context extracted from CAS activation state | extract_cognitive_context → CognitiveContext | [VIF-CAS-001, CAS-ACTIVATION-001]
# NL_TAG_INTENT: VIF-INTENT-001 | Enables cognitive provenance tracking | activation state + task categorization | [ADR-VIF-CAS]
def extract_cognitive_context(
    activation_state: Optional[ActivationState] = None,
    task_category: Optional[str] = None,
    task_category_confidence: Optional[float] = None,
    cognitive_load: Optional[float] = None,
    attention_breadth: Optional[str] = None,
    failure_mode: Optional[str] = None,
    **kwargs
) -> CognitiveContext:
    """Extract cognitive context from CAS for VIF witness
    
    Args:
        activation_state: CAS ActivationState instance (optional)
        task_category: Task categorization result (optional)
        task_category_confidence: Confidence in task categorization (optional)
        cognitive_load: Current cognitive load 0.0-1.0 (optional)
        attention_breadth: Attention breadth "narrow" | "comprehensive" (optional)
        failure_mode: Detected failure mode type (optional)
        **kwargs: Additional cognitive state data
        
    Returns:
        CognitiveContext instance with extracted cognitive data
        
    Examples:
        >>> from cas.activation import ActivationState
        >>> state = ActivationState(...)
        >>> context = extract_cognitive_context(activation_state=state)
        >>> assert context.activation_state is not None
    """
    if not CAS_AVAILABLE:
        logger.warning("CAS unavailable, cognitive context extraction skipped")
        return CognitiveContext()
    
    try:
        # Extract activation state data
        principles_activation = {}
        documents_activation = {}
        concepts_activation = {}
        session_id = None
        timestamp = None
        context_size_tokens = None
        working_attention_items = None
        
        if activation_state:
            principles_activation = activation_state.principles_activation.copy()
            documents_activation = activation_state.documents_activation.copy()
            concepts_activation = activation_state.concepts_activation.copy()
            session_id = activation_state.session_id
            timestamp = activation_state.timestamp
            context_size_tokens = activation_state.context_size_tokens
            working_attention_items = activation_state.working_attention_items
            
            # Serialize activation state for storage
            activation_state_dict = {
                "timestamp": activation_state.timestamp.isoformat() if activation_state.timestamp else None,
                "session_id": activation_state.session_id,
                "principles_activation": principles_activation,
                "documents_activation": documents_activation,
                "concepts_activation": concepts_activation,
                "recent_operations": activation_state.recent_operations,
                "documents_read": [(path, ts.isoformat()) for path, ts in activation_state.documents_read],
                "working_attention_items": activation_state.working_attention_items,
                "context_size_tokens": activation_state.context_size_tokens,
                "load_level": activation_state.load_level,
            }
        else:
            activation_state_dict = None
        
        # Detect activation gaps (principles that should be hot but aren't)
        activation_gap = None
        if activation_state and kwargs.get("required_principles"):
            required = kwargs.get("required_principles", [])
            activation_gap = activation_state.get_cold_but_needed(required)
        
        # Detect attention narrowing (warning sign)
        attention_narrowing = None
        if cognitive_load is not None and attention_breadth:
            attention_narrowing = (cognitive_load > 0.8) and (attention_breadth == "narrow")
        
        # Detect shortcuts appearing (warning sign)
        shortcuts_appearing = kwargs.get("shortcuts_appearing", None)
        
        # Detect categorization error
        categorization_error = kwargs.get("categorization_error", None)
        
        # Detect procedure gap
        procedure_gap = kwargs.get("procedure_gap", None)
        
        return CognitiveContext(
            activation_state=activation_state_dict,
            principles_activation=principles_activation,
            documents_activation=documents_activation,
            concepts_activation=concepts_activation,
            task_category=task_category,
            task_category_confidence=task_category_confidence,
            categorization_error=categorization_error,
            cognitive_load=cognitive_load,
            attention_breadth=attention_breadth,
            attention_narrowing=attention_narrowing,
            shortcuts_appearing=shortcuts_appearing,
            failure_mode_detected=failure_mode,
            activation_gap=activation_gap,
            procedure_gap=procedure_gap,
            session_id=session_id,
            timestamp=timestamp or datetime.now(timezone.utc),
            context_size_tokens=context_size_tokens,
            working_attention_items=working_attention_items,
        )
        
    except Exception as e:
        logger.error(f"Failed to extract cognitive context: {e}")
        return CognitiveContext()


# NL_TAG: VIF-CAS-002 | Add cognitive context to VIF witness | add_cognitive_context_to_witness(vif, cognitive_context) -> VIF | []
# NL_TAG_CONNECT: VIF-CAS-002 | Cognitive context stored in VIF witness tool_parameters | add_cognitive_context_to_witness → VIF.tool_parameters | [VIF-CAS-002, VIF-WITNESS-001]
# NL_TAG_INTENT: VIF-INTENT-002 | Enables cognitive provenance in witness envelopes | [ADR-VIF-CAS]
def add_cognitive_context_to_witness(
    vif: VIF,
    cognitive_context: CognitiveContext,
) -> VIF:
    """Add cognitive context to VIF witness envelope
    
    Stores cognitive context in VIF witness `tool_parameters` field for
    complete provenance tracking of how AI thought during operation.
    
    Args:
        vif: VIF witness instance
        cognitive_context: CognitiveContext instance
        
    Returns:
        VIF witness with cognitive context added to tool_parameters
        
    Examples:
        >>> vif = VIF(...)
        >>> context = CognitiveContext(...)
        >>> vif_enhanced = add_cognitive_context_to_witness(vif, context)
        >>> assert "cognitive_context" in vif_enhanced.tool_parameters
    """
    try:
        # Serialize cognitive context for storage
        cognitive_context_dict = {
            "activation_state": cognitive_context.activation_state,
            "principles_activation": cognitive_context.principles_activation,
            "documents_activation": cognitive_context.documents_activation,
            "concepts_activation": cognitive_context.concepts_activation,
            "task_category": cognitive_context.task_category,
            "task_category_confidence": cognitive_context.task_category_confidence,
            "categorization_error": cognitive_context.categorization_error,
            "cognitive_load": cognitive_context.cognitive_load,
            "attention_breadth": cognitive_context.attention_breadth,
            "attention_narrowing": cognitive_context.attention_narrowing,
            "shortcuts_appearing": cognitive_context.shortcuts_appearing,
            "failure_mode_detected": cognitive_context.failure_mode_detected,
            "activation_gap": cognitive_context.activation_gap,
            "procedure_gap": cognitive_context.procedure_gap,
            "session_id": cognitive_context.session_id,
            "timestamp": cognitive_context.timestamp.isoformat() if cognitive_context.timestamp else None,
            "context_size_tokens": cognitive_context.context_size_tokens,
            "working_attention_items": cognitive_context.working_attention_items,
        }
        
        # Add cognitive context to tool_parameters
        if vif.tool_parameters is None:
            vif.tool_parameters = {}
        
        vif.tool_parameters["cognitive_context"] = cognitive_context_dict
        
        logger.info(f"Added cognitive context to VIF witness {vif.id}")
        return vif
        
    except Exception as e:
        logger.error(f"Failed to add cognitive context to VIF witness {vif.id}: {e}")
        return vif


# NL_TAG: VIF-CAS-003 | Enhance confidence calibration using cognitive state | enhance_confidence_with_cognitive_state(vif, cognitive_context) -> float | []
# NL_TAG_CONNECT: VIF-CAS-003 | Confidence adjusted based on cognitive state | enhance_confidence_with_cognitive_state → VIF.confidence_score | [VIF-CAS-003, VIF-CALIBRATION-001]
# NL_TAG_INTENT: VIF-INTENT-003 | Improves confidence calibration accuracy | cognitive load + attention + failure modes | [ADR-VIF-CAS]
def enhance_confidence_with_cognitive_state(
    vif: VIF,
    cognitive_context: CognitiveContext,
) -> float:
    """Enhance confidence calibration using cognitive state
    
    Adjusts confidence score based on cognitive load, attention patterns,
    and failure mode detection to improve calibration accuracy.
    
    Args:
        vif: VIF witness instance
        cognitive_context: CognitiveContext instance
        
    Returns:
        Adjusted confidence score (0.0-1.0)
        
    Examples:
        >>> vif = VIF(confidence_score=0.85, ...)
        >>> context = CognitiveContext(cognitive_load=0.9, attention_narrowing=True)
        >>> adjusted = enhance_confidence_with_cognitive_state(vif, context)
        >>> assert adjusted < vif.confidence_score  # Reduced due to high load
    """
    try:
        base_confidence = vif.confidence_score
        adjustment = 0.0
        
        # Reduce confidence if cognitive load is high
        if cognitive_context.cognitive_load is not None:
            if cognitive_context.cognitive_load > 0.8:
                adjustment -= 0.05  # High load reduces confidence
            elif cognitive_context.cognitive_load < 0.3:
                adjustment += 0.02  # Low load slightly increases confidence
        
        # Reduce confidence if attention is narrowing (degradation sign)
        if cognitive_context.attention_narrowing:
            adjustment -= 0.03
        
        # Reduce confidence if shortcuts are appearing (degradation sign)
        if cognitive_context.shortcuts_appearing:
            adjustment -= 0.02
        
        # Reduce confidence if categorization error detected
        if cognitive_context.categorization_error:
            adjustment -= 0.05
        
        # Reduce confidence if activation gap detected (principles not hot)
        if cognitive_context.activation_gap and len(cognitive_context.activation_gap) > 0:
            adjustment -= 0.02 * min(len(cognitive_context.activation_gap), 3)  # Max -0.06
        
        # Reduce confidence if failure mode detected
        if cognitive_context.failure_mode_detected:
            adjustment -= 0.10  # Significant reduction for failure modes
        
        # Apply adjustment (clamp to [0.0, 1.0])
        adjusted_confidence = max(0.0, min(1.0, base_confidence + adjustment))
        
        logger.info(f"Adjusted confidence from {base_confidence:.3f} to {adjusted_confidence:.3f} based on cognitive state")
        return adjusted_confidence
        
    except Exception as e:
        logger.error(f"Failed to enhance confidence with cognitive state: {e}")
        return vif.confidence_score


# NL_TAG: VIF-CAS-004 | Create VIF witness with cognitive context | create_witness_with_cognitive_context(vif, cognitive_context) -> VIF | []
# NL_TAG_CONNECT: VIF-CAS-004 | Complete witness with cognitive provenance | create_witness_with_cognitive_context → VIF | [VIF-CAS-004, VIF-WITNESS-001]
# NL_TAG_INTENT: VIF-INTENT-004 | Enables complete cognitive provenance tracking | witness + cognitive context + enhanced confidence | [ADR-VIF-CAS]
def create_witness_with_cognitive_context(
    vif: VIF,
    cognitive_context: CognitiveContext,
    enhance_confidence: bool = True,
) -> VIF:
    """Create VIF witness with cognitive context
    
    Combines VIF witness creation with cognitive context extraction and
    confidence enhancement for complete cognitive provenance tracking.
    
    Args:
        vif: VIF witness instance
        cognitive_context: CognitiveContext instance
        enhance_confidence: Whether to enhance confidence based on cognitive state
        
    Returns:
        VIF witness with cognitive context and optionally enhanced confidence
        
    Examples:
        >>> vif = VIF(...)
        >>> context = CognitiveContext(...)
        >>> vif_enhanced = create_witness_with_cognitive_context(vif, context)
        >>> assert "cognitive_context" in vif_enhanced.tool_parameters
    """
    try:
        # Add cognitive context to witness
        vif = add_cognitive_context_to_witness(vif, cognitive_context)
        
        # Optionally enhance confidence based on cognitive state
        if enhance_confidence:
            adjusted_confidence = enhance_confidence_with_cognitive_state(vif, cognitive_context)
            vif.confidence_score = adjusted_confidence
            
            # Update confidence band if needed
            if adjusted_confidence >= 0.90:
                vif.confidence_band = ConfidenceBand.A
            elif adjusted_confidence >= 0.70:
                vif.confidence_band = ConfidenceBand.B
            else:
                vif.confidence_band = ConfidenceBand.C
        
        logger.info(f"Created VIF witness {vif.id} with cognitive context")
        return vif
        
    except Exception as e:
        logger.error(f"Failed to create witness with cognitive context: {e}")
        return vif


# NL_TAG: VIF-CAS-005 | Check if CAS is available | is_cas_available() -> bool | []
# NL_TAG_CONNECT: VIF-CAS-005 | Health check for CAS availability | is_cas_available → bool | [VIF-CAS-005, CAS-HEALTH-001]
# NL_TAG_INTENT: VIF-INTENT-005 | Enables graceful degradation | health check before operations | [ADR-VIF-CAS]
def is_cas_available() -> bool:
    """Check if CAS is available
    
    Returns:
        True if CAS is available, False otherwise
        
    Examples:
        >>> if is_cas_available():
        ...     context = extract_cognitive_context(...)
    """
    return CAS_AVAILABLE

