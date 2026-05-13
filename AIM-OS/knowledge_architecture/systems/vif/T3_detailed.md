---
id: "vif_T3_detailed"
system: "vif"
component: null
level: "T3"
type: "detailed"
title: "VIF Detailed Implementation Guide"
description: "10,000-word detailed implementation guide"
audience: "developers, implementers"
confidence_threshold: 0.60
token_cost: 10000
word_count: 10000
created: "2025-11-02T00:00:00Z"
updated: "2025-11-02T16:00:00Z"
author: "aether"
status: "complete"
tags: ["vif", "core", "t0-t6", "transitional"]
dependencies: ["vif_T2_architecture"]
related_docs: ["vif_T4_complete", "system.map.lucid.json5", "usage.envelope.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.


# VIF – L3 Detailed Implementation Guide

## Purpose

This document provides comprehensive implementation guidance for integrating and using VIF (Verifiable Intelligence Framework) in production systems. It covers all APIs, configuration options, integration patterns, performance optimization, troubleshooting, and best practices.

## Audience

- **Developers** integrating VIF into AI applications
- **System Architects** designing trustworthy AI systems
- **DevOps Engineers** deploying and monitoring VIF
- **QA Engineers** testing VIF functionality

## Prerequisites

- Understanding of AI/ML model operations
- Familiarity with Python 3.10+
- Basic knowledge of provenance and audit trails
- Understanding of CMC and SEG (for integration)

---

## 📋 Implementation Tag Map

This document provides detailed implementation guidance. All referenced code is tagged for semantic search and quintet parity validation.

**Tag Categories Referenced:**
- **Core Implementation:** VIF-WITNESS-* (witness operations), VIF-CONF-* (confidence tracking), VIF-CAL-* (calibration), VIF-GATE-* (κ-gating), VIF-REPLAY-* (deterministic replay)
- **Integration Points:** VIF-CMC-* (storage integration), VIF-HHNI-* (retrieval integration + RS-Lift), VIF-APOE-* (execution integration), VIF-SEG-* (provenance chains + evidence weighting), VIF-SDFCVF-* (quartet parity + trace conversion), VIF-TCS-* (timeline integration), VIF-CAS-* (cognitive context)
- **Data Models:** VIF-MODEL-* (schemas and enums)
- **Design Decisions:** VIF-DESIGN-* (architectural rationale), VIF-INTENT-* (intent preservation)
- **Validation:** VIF-SPEC-* (schema validation and constraints)

**Quick Tag Navigation:**
- Use tag IDs to locate exact code: `VIF-WITNESS-001` → `packages/vif/witness.py:123-156`
- CONNECT tags show cross-system integration points
- INTENT tags explain design rationale
- SPEC tags document validation rules

**Complete tag index:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) (408 total VIF tags)

---

## Setup & Interfaces

### Public API Methods

```python
from packages.vif import VIF, create_witness, kappa_gate, CalibrationTracker, replay_from_vif

# Create witness for AI operation
vif = create_witness(
    model_id="gpt-4-turbo-2025-01-15",
    prompt="What is 2+2?",
    output="4",
    context_snapshot_id="snapshot_123",
    confidence=0.95,
    task_criticality="routine"
)

# κ-gate check
gate_result = kappa_gate(
    output="4",
    confidence=0.95,
    task_criticality="critical"  # κ = 0.95
)

if gate_result.status == "ABSTAIN":
    # Escalate to human-in-the-loop
    escalate_to_hitl(gate_result.reason)

# Calibration tracking
tracker = CalibrationTracker()
pred_id = tracker.record_prediction(confidence=0.90, output="4")
tracker.verify_prediction(pred_id, ground_truth="4")
ece = tracker.calculate_ece()  # Returns ECE score

# Deterministic replay
original_output, vif = generate_with_replay(
    prompt="What is 2+2?",
    context=[],
    model_id="gpt-4-turbo"
)
replayed_output = replay_from_vif(vif)  # Bit-identical!
```

### Type Definitions

```python
from dataclasses import dataclass
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

@dataclass
class VIF:
    """Verifiable Intelligence Framework witness envelope"""
    id: str
    model_id: str
    context_snapshot_id: str
    prompt_hash: str
    confidence_score: float
    confidence_band: str  # "A" | "B" | "C"
    ece_score: Optional[float]
    replay_seed: Optional[int]
    created_at: datetime
    # ... (full schema in T2)

@dataclass
class KappaGateResult:
    """Result of κ-gate check"""
    status: str  # "PASS" | "ABSTAIN"
    confidence: float
    threshold: float
    task_criticality: str
    reason: Optional[str]
    escalation: Optional[str]

@dataclass
class CalibrationTracker:
    """Track confidence vs accuracy"""
    predictions: List[Prediction]
```

## Witness Creation Implementation

### Complete Witness Generation

```python
def create_witness(
    model_id: str,
    prompt: str,
    output: str,
    context_snapshot_id: str,
    confidence: float,
    task_criticality: str = "routine",
    tools_used: List[str] = [],
    replay_seed: Optional[int] = None
) -> VIF:
    """Generate complete VIF witness envelope"""
    
    # Hash prompt and output
    prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()
    output_hash = hashlib.sha256(output.encode()).hexdigest()
    
    # Count tokens (estimate)
    prompt_tokens = estimate_tokens(prompt)
    output_tokens = estimate_tokens(output)
    
    # Determine confidence band
    band = determine_confidence_band(confidence)
    # Band A: 0.95-1.00
    # Band B: 0.80-0.94
    # Band C: <0.80
    
    # Get κ threshold for task
    kappa = get_kappa_threshold(task_criticality)
    # Critical: 0.95
    # Important: 0.85
    # Routine: 0.70
    # Low Stakes: 0.60
    
    # Check κ-gate
    kappa_passed = confidence >= kappa
    
    # Generate replay seed if not provided
    if replay_seed is None:
        replay_seed = random.randint(0, 2**32 - 1)
    
    # Calculate entropy (if available)
    entropy = calculate_entropy(output)
    
    # Create witness
    vif = VIF(
        id=f"vif_{uuid.uuid4().hex}",
        model_id=model_id,
        context_snapshot_id=context_snapshot_id,
        prompt_hash=prompt_hash,
        prompt_tokens=prompt_tokens,
        confidence_score=confidence,
        confidence_band=band,
        ece_score=None,  # Computed later
        replay_seed=replay_seed,
        output_hash=output_hash,
        output_tokens=output_tokens,
        task_criticality=task_criticality,
        kappa_threshold=kappa,
        kappa_gate_passed=kappa_passed,
        tool_ids=tools_used,
        created_at=datetime.utcnow()
    )
    
    # Store in CMC
    store_in_cmc(vif)
    
    # Link to SEG
    link_to_seg(vif)
    
    return vif
```

### Confidence Band Assignment

```python
def determine_confidence_band(confidence: float) -> str:
    """Assign confidence band A/B/C"""
    if confidence >= 0.95:
        return "A"  # High confidence
    elif confidence >= 0.80:
        return "B"  # Medium confidence
    else:
        return "C"  # Low confidence
```

## κ-Gating Implementation

### κ-Threshold Determination

```python
class KappaThresholds:
    """Per-task confidence thresholds"""
    CRITICAL = 0.95      # Medical, legal, safety-critical
    IMPORTANT = 0.85     # Code generation, data analysis
    ROUTINE = 0.70       # Summarization, formatting
    LOW_STAKES = 0.60    # Suggestions, recommendations

def get_kappa_threshold(task_criticality: str) -> float:
    """Get κ threshold for task"""
    thresholds = {
        "critical": KappaThresholds.CRITICAL,
        "important": KappaThresholds.IMPORTANT,
        "routine": KappaThresholds.ROUTINE,
        "low_stakes": KappaThresholds.LOW_STAKES
    }
    return thresholds.get(task_criticality, KappaThresholds.ROUTINE)
```

### κ-Gate Evaluation

```python
def kappa_gate(
    output: Any,
    confidence: float,
    task_criticality: str,
    enable_abstention: bool = True
) -> KappaGateResult:
    """Enforce behavioral abstention"""
    
    kappa = get_kappa_threshold(task_criticality)
    
    if confidence < kappa:
        if enable_abstention:
            return KappaGateResult(
                status="ABSTAIN",
                confidence=confidence,
                threshold=kappa,
                task_criticality=task_criticality,
                reason=f"Confidence {confidence:.2f} below threshold {kappa:.2f}",
                escalation="hitl"  # Human-in-the-loop
            )
        else:
            # Log warning but proceed (abstention disabled)
            log.warning(f"κ-gate would abstain but abstention disabled: conf={confidence}, κ={kappa}")
    
    return KappaGateResult(
        status="PASS",
        confidence=confidence,
        threshold=kappa,
        task_criticality=task_criticality
    )
```

### Escalation Handling

```python
def escalate_to_hitl(gate_result: KappaGateResult) -> str:
    """Escalate to human-in-the-loop"""
    message = f"""
    Confidence too low for {gate_result.task_criticality} task.
    
    Confidence: {gate_result.confidence:.0%}
    Required: {gate_result.threshold:.0%}
    
    Reason: {gate_result.reason}
    
    Escalating to human review...
    """
    return message
```

## Calibration Tracking Implementation

### ECE Calculation

```python
def calculate_ece(predictions: List[Prediction]) -> float:
    """Calculate Expected Calibration Error"""
    verified = [p for p in predictions if p.correct is not None]
    
    if not verified:
        return None  # Not enough data
    
    total_error = 0.0
    for pred in verified:
        accuracy = 1.0 if pred.correct else 0.0
        error = abs(pred.confidence - accuracy)
        total_error += error
    
    ece = total_error / len(verified)
    return ece
```

### Calibration Tracker Usage

```python
tracker = CalibrationTracker()

# Record prediction
pred_id = tracker.record_prediction(
    confidence=0.90,
    output="4"
)

# Verify later (when ground truth known)
tracker.verify_prediction(pred_id, ground_truth="4")

# Calculate ECE
ece = tracker.calculate_ece()
status = tracker.calibration_status()
# Returns: "WELL_CALIBRATED" (ECE ≤ 0.05)
#          "ACCEPTABLE" (0.05 < ECE ≤ 0.10)
#          "POORLY_CALIBRATED" (ECE > 0.10)
```

## Deterministic Replay Implementation

### Replay Storage

```python
def generate_with_replay(
    prompt: str,
    context: List[Atom],
    model_id: str,
    task_criticality: str = "routine"
) -> Tuple[str, VIF]:
    """Generate output with replay capability"""
    
    # Set deterministic seed
    replay_seed = random.randint(0, 2**32 - 1)
    set_seed(replay_seed)
    
    # Create context snapshot
    snapshot = create_snapshot(context, notes="Replay-capable generation")
    
    # Generate with fixed params
    output = model.generate(
        prompt=prompt,
        temperature=0.0,  # Deterministic
        seed=replay_seed,
        max_tokens=1000
    )
    
    # Get confidence
    confidence = model.get_confidence()
    
    # κ-gate check
    gate_result = kappa_gate(output, confidence, task_criticality)
    if gate_result.status == "ABSTAIN":
        raise ConfidenceTooLow(gate_result.reason)
    
    # Create VIF witness
    vif = create_witness(
        model_id=model_id,
        prompt=prompt,
        output=output,
        context_snapshot_id=snapshot.id,
        confidence=confidence,
        task_criticality=task_criticality,
        replay_seed=replay_seed
    )
    
    return output, vif
```

### Replay Execution

```python
def replay_from_vif(vif: VIF) -> str:
    """Reproduce exact output from VIF witness"""
    
    # Load exact context
    snapshot = load_snapshot(vif.context_snapshot_id)
    context = snapshot.get_atoms()
    
    # Reconstruct prompt (store full prompt or template + vars)
    prompt = reconstruct_prompt(vif)
    
    # Verify prompt hash
    actual_hash = hashlib.sha256(prompt.encode()).hexdigest()
    if actual_hash != vif.prompt_hash:
        raise ReplayError("Prompt hash mismatch!")
    
    # Set same seed
    set_seed(vif.replay_seed)
    
    # Generate with exact same params
    output = model.generate(
        prompt=prompt,
        temperature=vif.temperature,
        top_p=vif.top_p,
        seed=vif.replay_seed,
        max_tokens=vif.max_tokens,
        **vif.other_params
    )
    
    return output  # Should be bit-identical!
```

## Error Handling

### Invalid Inputs

```python
class VIFError(Exception):
    """Base VIF error"""
    pass

class ConfidenceTooLow(VIFError):
    """Confidence below κ threshold"""
    pass

class ReplayError(VIFError):
    """Replay failed"""
    pass

def create_witness_safe(
    model_id: str,
    prompt: str,
    output: str,
    confidence: float,
    **kwargs
) -> VIF:
    """Create witness with validation"""
    if not model_id:
        raise VIFError("model_id required")
    if not prompt:
        raise VIFError("prompt required")
    if not (0.0 <= confidence <= 1.0):
        raise VIFError(f"confidence must be 0.0-1.0, got {confidence}")
    
    return create_witness(model_id, prompt, output, confidence, **kwargs)
```

## Examples

### Example: Witness Creation

```python
# AI operation
output = model.generate("What is 2+2?")
confidence = model.get_confidence()  # 0.95

# Create witness
vif = create_witness(
    model_id="gpt-4-turbo-2025-01-15",
    prompt="What is 2+2?",
    output="4",
    context_snapshot_id="snapshot_123",
    confidence=confidence,
    task_criticality="routine"
)

# Store and link
store_in_cmc(vif)
link_to_seg(vif)
```

### Example: κ-Gating

```python
# Critical task (medical diagnosis)
diagnosis = model.generate(prompt, task="medical_diagnosis")
confidence = model.get_confidence()  # 0.85

gate_result = kappa_gate(diagnosis, confidence, "critical")

if gate_result.status == "ABSTAIN":
    # Don't use uncertain diagnosis!
    return escalate_to_hitl(gate_result)
else:
    return diagnosis
```

### Example: Calibration Tracking

```python
tracker = CalibrationTracker()

# Record predictions
for prediction in predictions:
    pred_id = tracker.record_prediction(
        confidence=prediction.confidence,
        output=prediction.output
    )

# Verify later
for pred_id, ground_truth in zip(pred_ids, ground_truths):
    tracker.verify_prediction(pred_id, ground_truth)

# Check calibration
ece = tracker.calculate_ece()
status = tracker.calibration_status()

if status == "POORLY_CALIBRATED":
    alert(f"Poor calibration detected: ECE={ece:.3f}")
```

### Example: Deterministic Replay

```python
# Generate original
original_output, vif = generate_with_replay(
    prompt="What is 2+2?",
    context=[],
    model_id="gpt-4-turbo"
)

# Replay (should be identical)
replayed_output = replay_from_vif(vif)

assert original_output == replayed_output  # ✅ PASSING!
```

## Tests

### Unit Test Example

```python
def test_kappa_gate():
    """Test κ-gating behavior"""
    # High confidence, low threshold
    result = kappa_gate("output", confidence=0.95, task_criticality="routine")
    assert result.status == "PASS"
    
    # Low confidence, high threshold
    result = kappa_gate("output", confidence=0.85, task_criticality="critical")
    assert result.status == "ABSTAIN"
    assert result.escalation == "hitl"
```

### Integration Test Example

```python
def test_complete_pipeline():
    """End-to-end witness creation"""
    # Generate output
    output, vif = generate_with_replay(
        prompt="What is 2+2?",
        context=[],
        model_id="test_model"
    )
    
    # Validate witness
    assert vif.confidence_score > 0.0
    assert vif.confidence_band in ["A", "B", "C"]
    assert vif.replay_seed is not None
    
    # Verify replay
    replayed = replay_from_vif(vif)
    assert replayed == output  # Bit-identical!
```

## Performance Optimization

### Caching Strategy

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_kappa_threshold_cached(task_criticality: str) -> float:
    """Cache κ threshold lookups"""
    return get_kappa_threshold(task_criticality)
```

### Batch Processing

```python
def create_witnesses_batch(operations: List[Operation]) -> List[VIF]:
    """Create witnesses for multiple operations efficiently"""
    witnesses = []
    for op in operations:
        witness = create_witness(
            model_id=op.model_id,
            prompt=op.prompt,
            output=op.output,
            context_snapshot_id=op.snapshot_id,
            confidence=op.confidence,
            task_criticality=op.criticality
        )
        witnesses.append(witness)
    
    # Batch store in CMC
    batch_store_in_cmc(witnesses)
    
    return witnesses
```

## Complete API Reference

This section provides comprehensive documentation for all VIF public APIs.

### VIF Class

**Purpose:** Complete provenance envelope for AI operations.

**Constructor:**

```python
@dataclass
class VIF(BaseModel):
    """Verifiable Intelligence Framework witness envelope"""
    
    # Identity fields
    id: str = Field(default_factory=lambda: f"vif_{uuid.uuid4().hex}")
    version: str = Field(default="1.0.0")
    
    # Model identification
    model_id: str  # e.g., "gpt-4-turbo-2025-01-15"
    model_provider: str  # "openai", "anthropic", "local"
    weights_hash: Optional[str] = None  # SHA-256 hash of weights
    
    # Context and prompts
    context_snapshot_id: str  # CMC snapshot ID
    context_atom_ids: List[str] = Field(default_factory=list)
    prompt_template: Optional[str] = None
    prompt_hash: str  # SHA-256 hash of exact prompt
    prompt_tokens: int
    retrieved_atom_ids: List[str] = Field(default_factory=list)
    
    # Tools
    tool_ids: List[str] = Field(default_factory=list)
    tool_parameters: Dict[str, Any] = Field(default_factory=dict)
    tool_results_hash: Optional[str] = None
    
    # Uncertainty
    confidence_score: float  # 0.0-1.0
    confidence_band: ConfidenceBand  # A, B, or C
    ece_score: Optional[float] = None
    entropy: float = 0.0
    top_k_probs: List[Tuple[str, float]] = Field(default_factory=list)
    
    # Replay
    replay_seed: Optional[int] = None
    temperature: float = 0.7
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    max_tokens: Optional[int] = None
    other_params: Dict[str, Any] = Field(default_factory=dict)
    
    # Output
    output_hash: str  # SHA-256 hash of output
    output_tokens: int
    total_tokens: int
    
    # Metadata
    writer: str = "system"
    task_criticality: TaskCriticality = TaskCriticality.ROUTINE
    kappa_threshold: float = 0.70
    kappa_gate_passed: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    execution_time_ms: float = 0.0
    parent_vif_id: Optional[str] = None
```

**create_witness() Function:**

```python
def create_witness(
    model_id: str,
    prompt: str,
    output: str,
    context_snapshot_id: str,
    confidence: float,
    task_criticality: TaskCriticality = TaskCriticality.ROUTINE,
    tools_used: List[str] = [],
    replay_seed: Optional[int] = None,
    **kwargs
) -> VIF:
    """
    Create complete VIF witness envelope for an AI operation.
    
    Args:
        model_id: Model identifier (e.g., "gpt-4-turbo-2025-01-15")
        prompt: Exact prompt text sent to model
        output: Model output text
        context_snapshot_id: CMC snapshot ID capturing context
        confidence: Confidence score (0.0-1.0)
        task_criticality: Task criticality level
        tools_used: List of tool IDs used
        replay_seed: Random seed for deterministic replay
        **kwargs: Additional witness fields
    
    Returns:
        VIF: Complete witness envelope
    
    Example:
        vif = create_witness(
            model_id="gpt-4-turbo",
            prompt="What is 2+2?",
            output="4",
            context_snapshot_id="snap_123",
            confidence=0.95,
            task_criticality=TaskCriticality.ROUTINE
        )
        print(f"Created witness: {vif.id}")
    """
```

### KappaGate Class

**Purpose:** Behavioral abstention system enforcing confidence thresholds.

**check() Method:**

```python
def check(
    self,
    confidence: float,
    task_criticality: TaskCriticality = TaskCriticality.ROUTINE,
    *,
    custom_threshold: Optional[float] = None
) -> KappaGateResult:
    """
    Check if confidence meets κ threshold for task.
    
    Args:
        confidence: Model's confidence score (0.0-1.0)
        task_criticality: Criticality level (CRITICAL, IMPORTANT, ROUTINE, LOW_STAKES)
        custom_threshold: Override default threshold
    
    Returns:
        KappaGateResult: Pass/fail status and escalation info
    
    Thresholds:
        - CRITICAL: 0.95 (medical, legal, safety)
        - IMPORTANT: 0.85 (financial, strategic)
        - ROUTINE: 0.70 (standard operations)
        - LOW_STAKES: 0.60 (experimental)
    
    Example:
        gate = KappaGate()
        result = gate.check(
            confidence=0.85,
            task_criticality=TaskCriticality.CRITICAL
        )
        
        if not result.passed:
            escalate_to_hitl(result)
    """
```

**gate_operation() Method:**

```python
def gate_operation(
    self,
    operation: Callable[[], Any],
    confidence: float,
    task_criticality: TaskCriticality = TaskCriticality.ROUTINE,
    *,
    on_fail: Optional[Callable[[KappaGateResult], Any]] = None
) -> Tuple[Any, KappaGateResult]:
    """
    Gate an operation through κ-check.
    
    Args:
        operation: Function to execute if gate passes
        confidence: Model's confidence in operation
        task_criticality: Criticality level
        on_fail: Function to call if gate fails
    
    Returns:
        Tuple[operation_result, gate_result]
    
    Example:
        def risky_operation():
            return model.generate("medical diagnosis")
        
        def safe_fallback(result):
            return "Operation refused - low confidence"
        
        output, result = gate.gate_operation(
            risky_operation,
            confidence=0.60,
            task_criticality=TaskCriticality.CRITICAL,
            on_fail=safe_fallback
        )
    """
```

### ECETracker Class

**Purpose:** Track Expected Calibration Error for confidence calibration.

**add_prediction() Method:**

```python
def add_prediction(
    self,
    confidence: float,
    correct: bool,
    *,
    validate: bool = True
) -> None:
    """
    Add a prediction to calibration tracker.
    
    Args:
        confidence: Model's confidence score (0.0-1.0)
        correct: Whether prediction was actually correct
        validate: If True, raise error for invalid confidence
    
    Example:
        tracker = ECETracker(num_bins=10)
        tracker.add_prediction(confidence=0.85, correct=True)
        tracker.add_prediction(confidence=0.90, correct=True)
        tracker.add_prediction(confidence=0.80, correct=False)
        
        ece = tracker.calculate_ece()
        print(f"ECE: {ece:.4f}")
    """
```

**calculate_ece() Method:**

```python
def calculate_ece(self) -> float:
    """
    Calculate Expected Calibration Error.
    
    ECE = Σ (n_b / n_total) * |conf_b - acc_b|
    
    Where:
    - n_b: number of predictions in bin b
    - n_total: total number of predictions
    - conf_b: average confidence in bin b
    - acc_b: accuracy in bin b
    
    Returns:
        ECE score (0.0 = perfect, lower is better)
    
    Interpretation:
        - ECE < 0.05: Excellent calibration
        - ECE < 0.10: Good calibration
        - ECE > 0.10: Poor calibration (recalibration needed)
    """
```

### ReplayEngine Class

**Purpose:** Enable deterministic reproduction of AI operations.

**replay() Method:**

```python
def replay(
    self,
    vif: VIF,
    operation: Callable[[Dict[str, Any]], Any],
    *,
    verify_hash: bool = True
) -> ReplayResult:
    """
    Replay an operation from its VIF witness.
    
    Args:
        vif: VIF witness containing full provenance
        operation: Function that executes the operation
        verify_hash: If True, verify output hash matches
    
    Returns:
        ReplayResult: Success status and verification
    
    Process:
        1. Load context from CMC snapshot
        2. Reconstruct prompt from witness
        3. Set same seed and parameters
        4. Execute operation
        5. Verify output hash matches
    
    Example:
        engine = ReplayEngine()
        
        # Original operation captured in VIF
        original_vif = create_witness(...)
        
        # Replay operation
        result = engine.replay(original_vif, operation_fn)
        
        assert result.matches_original  # Bit-identical!
    """
```

## Detailed Implementation Guide

### Step 1: Installation

```bash
# Install VIF package
cd packages/vif
pip install -e .

# Install dependencies
pip install pydantic numpy

# Verify installation
python -c "from vif import VIF, KappaGate; print('VIF installed successfully')"
```

### Step 2: Create Witness

```python
from vif import VIF, create_witness, ConfidenceBand, TaskCriticality
import hashlib

# Create witness for AI operation
vif = create_witness(
    model_id="gpt-4-turbo-2025-01-15",
    model_provider="openai",
    prompt="What is 2+2?",
    output="4",
    context_snapshot_id="snap_123",
    confidence=0.95,
    task_criticality=TaskCriticality.ROUTINE
)

print(f"Created witness: {vif.id}")
print(f"Confidence band: {vif.confidence_band}")
print(f"κ-gate passed: {vif.kappa_gate_passed}")
```

### Step 3: κ-Gate Check

```python
from vif import KappaGate, TaskCriticality

# Create gate
gate = KappaGate()

# Check confidence for critical task
result = gate.check(
    confidence=0.85,
    task_criticality=TaskCriticality.CRITICAL
)

if not result.passed:
    print(f"Operation refused: {result.escalation_reason}")
    escalate_to_hitl(result)
else:
    print("Operation approved")
```

### Step 4: Calibration Tracking

```python
from vif import ECETracker

# Create tracker
tracker = ECETracker(num_bins=10)

# Record predictions
tracker.add_prediction(confidence=0.85, correct=True)
tracker.add_prediction(confidence=0.90, correct=True)
tracker.add_prediction(confidence=0.80, correct=False)

# Calculate ECE
ece = tracker.calculate_ece()
print(f"ECE: {ece:.4f}")

# Check calibration status
summary = tracker.get_calibration_summary()
print(f"Calibration status: {summary}")
```

### Step 5: Deterministic Replay

```python
from vif import ReplayEngine

# Create replay engine
engine = ReplayEngine()

# Replay operation from witness
result = engine.replay(
    vif=original_vif,
    operation=lambda params: model.generate(**params),
    verify_hash=True
)

if result.matches_original:
    print("Replay successful - bit-identical output!")
else:
    print(f"Replay mismatch: {result.error}")
```

## Integration Guides

### CMC Integration

**Store Witness in CMC:**

```python
from vif import VIF, VIFStore
from cmc_service import MemoryStore

# Connect to CMC
store = MemoryStore(Path("./data/cmc"))

# Create VIF store
vif_store = VIFStore(store)

# Create witness
vif = create_witness(
    model_id="gpt-4-turbo",
    prompt="What is 2+2?",
    output="4",
    context_snapshot_id="snap_123",
    confidence=0.95
)

# Store in CMC
atom_id = vif_store.store_witness(vif)
print(f"Stored witness as atom: {atom_id}")
```

**Query Witnesses:**

```python
# Query witnesses by model
witnesses = vif_store.query_witnesses(
    model_id="gpt-4-turbo",
    confidence_min=0.90,
    time_range=(start_time, end_time)
)

# Query witnesses by task criticality
critical_witnesses = vif_store.query_witnesses(
    task_criticality=TaskCriticality.CRITICAL
)

# Get witness chain
chain = vif_store.get_witness_chain(parent_vif_id="vif_parent123")
```

### SEG Integration

**Link Witness to SEG:**

```python
from seg import SEGClient

# Create SEG client
seg_client = SEGClient()

# Link witness to SEG
seg_client.link_witness(
    witness_id=vif.id,
    operation_id="op_123",
    evidence_nodes=["ev_1", "ev_2"]
)

# Query provenance graph
provenance = seg_client.get_provenance(witness_id=vif.id)
```

### APOE Integration

**Provide κ-Gate Hooks:**

```python
from apoe import APOEOrchestrator
from vif import KappaGate

# Create orchestrator
orchestrator = APOEOrchestrator()

# Create gate
gate = KappaGate()

# Register gate hooks
def check_confidence(operation, confidence, criticality):
    """Check confidence before operation."""
    result = gate.check(confidence, criticality)
    if not result.passed:
        return None, result  # Refuse operation
    return operation(), result

orchestrator.register_gate_hook("vif", check_confidence)

# Use in orchestration
plan = orchestrator.create_plan(
    goal="Implement feature",
    gate_hook="vif"
)
```

### HHNI Integration (Phase 4)

**Track RS-Lift Metrics:**

```python
from vif.hhni_integration import (
    extract_rs_lift_metrics,
    store_rs_lift_in_witness,
    create_retrieval_witness,
    calculate_rs_lift_statistics,
)
from hhni.retrieval import RetrievalResult

# Extract RS-Lift from HHNI retrieval
retrieval_result = RetrievalResult(
    selected_items=[],
    rs_lift=0.5,
    relevance_score=0.8,
    total_tokens=100
)

# Extract metrics
metrics = extract_rs_lift_metrics(
    retrieval_result=retrieval_result,
    query="test query",
    retrieval_id="retrieval_123"
)

# Create witness with RS-Lift
vif = create_retrieval_witness(
    retrieval_result=retrieval_result,
    context_snapshot_id="snap_123",
    confidence=0.95,
    query="test query"
)

# Calculate statistics
stats = calculate_rs_lift_statistics(vif_store)
print(f"Average RS-Lift: {stats.avg_rs_lift}")
```

### SDF-CVF Integration (Phase 4)

**Convert Witnesses to Traces for Quartet Parity:**

```python
from vif.sdfcvf_integration import (
    vif_witness_to_trace_text,
    collect_witnesses_for_file,
    create_trace_file_from_witnesses,
    calculate_parity_with_vif_traces,
    combine_confidence_and_parity,
)

# Convert witness to trace text
vif = create_witness(...)
trace_text = vif_witness_to_trace_text(vif)

# Collect witnesses for a file
witnesses = collect_witnesses_for_file(
    file_path="packages/vif/witness.py",
    vif_store=vif_store,
    limit=100
)

# Create trace file
trace_file = create_trace_file_from_witnesses(
    witnesses=witnesses,
    output_dir=Path("./traces"),
    file_name="witness_trace.txt"
)

# Calculate parity with VIF traces
parity_result = calculate_parity_with_vif_traces(
    code_file=Path("code.py"),
    doc_file=Path("doc.md"),
    test_file=Path("test.py"),
    trace_files=[trace_file],
    parity_calculator=parity_calculator
)

# Combine VIF confidence with parity score
quality = combine_confidence_and_parity(
    vif_confidence=0.95,
    parity_score=0.85,
    confidence_weight=0.4
)
```

### TCS Integration (Phase 4)

**Create Timeline Entries for Witnesses:**

```python
from vif.tcs_integration import (
    create_witness_timeline_entry,
    create_kappa_gate_timeline_entry,
    query_witness_timeline,
    query_snapshot_timeline,
    query_confidence_timeline,
)

# Create timeline entry for witness
vif = create_witness(...)
entry_id = create_witness_timeline_entry(
    vif=vif,
    add_timeline_entry_fn=mcp_client.add_timeline_entry
)

# Create timeline entry for κ-gate event
gate_result = kappa_gate.check(confidence=0.90, task_criticality=TaskCriticality.CRITICAL)
entry_id = create_kappa_gate_timeline_entry(
    kappa_gate=kappa_gate,
    task_criticality=TaskCriticality.CRITICAL,
    add_timeline_entry_fn=mcp_client.add_timeline_entry,
    witness_id=vif.id
)

# Query timeline for witness
entries = query_witness_timeline(
    witness_id="vif_123",
    get_timeline_entries_fn=mcp_client.get_timeline_entries,
    limit=100
)

# Query timeline for snapshot
entries = query_snapshot_timeline(
    snapshot_id="snap_123",
    get_timeline_entries_fn=mcp_client.get_timeline_entries
)

# Query timeline for confidence range
entries = query_confidence_timeline(
    min_confidence=0.80,
    max_confidence=0.95,
    get_timeline_entries_fn=mcp_client.get_timeline_entries
)
```

### CAS Integration (Phase 4)

**Add Cognitive Context to Witnesses:**

```python
from vif.cas_integration import (
    extract_cognitive_context,
    add_cognitive_context_to_witness,
    enhance_confidence_with_cognitive_state,
    create_witness_with_cognitive_context,
)
from cas.activation import ActivationState

# Extract cognitive context from CAS
activation_state = ActivationState(...)
cognitive_context = extract_cognitive_context(
    activation_state=activation_state,
    task_category="coding",
    task_category_confidence=0.9,
    cognitive_load=0.7,
    attention_breadth="comprehensive"
)

# Add cognitive context to existing witness
vif = create_witness(...)
vif_with_context = add_cognitive_context_to_witness(vif, cognitive_context)

# Enhance confidence based on cognitive state
enhanced_confidence = enhance_confidence_with_cognitive_state(
    vif_confidence=0.95,
    cognitive_context=cognitive_context
)

# Create witness with cognitive context (one-step)
vif = create_witness_with_cognitive_context(
    model_id="gpt-4-turbo",
    model_provider="openai",
    context_snapshot_id="snap_123",
    prompt_hash="hash1",
    output_hash="hash2",
    output_tokens=5,
    total_tokens=15,
    cognitive_context=cognitive_context,
    initial_confidence=0.95
)
```

### SEG Integration (Enhanced - Phase 4)

**Verify Provenance Chains and Weight Evidence:**

```python
from vif.seg_integration import (
    verify_witness_link,
    verify_provenance_chain,
    calculate_evidence_weighting,
    verify_all_witness_links,
)

# Verify single witness link
verification = verify_witness_link("witness_123")
print(f"Witness exists: {verification.exists}")
print(f"Confidence: {verification.confidence}")

# Verify full provenance chain
chain_verification = verify_provenance_chain(
    graph=seg_graph,
    entity_id="entity_123",
    max_depth=5
)
print(f"Chain valid: {chain_verification.is_valid}")
print(f"Verified links: {chain_verification.verified_count}")

# Calculate evidence weighting
weighting = calculate_evidence_weighting(
    evidence=evidence,
    witness_id="witness_123"
)
print(f"Weighted confidence: {weighting.weighted_confidence}")

# Verify all witness links in graph
stats = verify_all_witness_links(seg_graph)
print(f"Total links: {stats['total_links']}")
print(f"Verified: {stats['verified_count']}")
```

## Configuration

### Environment Variables

```bash
# VIF configuration
export VIF_DEFAULT_KAPPA_CRITICAL=0.95
export VIF_DEFAULT_KAPPA_IMPORTANT=0.85
export VIF_DEFAULT_KAPPA_ROUTINE=0.70
export VIF_DEFAULT_KAPPA_LOW_STAKES=0.60

# Calibration
export VIF_ECE_BINS=10
export VIF_ECE_THRESHOLD=0.10

# Replay
export VIF_REPLAY_ENABLED=true
export VIF_REPLAY_VERIFY_HASH=true
```

### Production Configuration

```python
# Production κ-gate configuration
gate = KappaGate(
    thresholds={
        TaskCriticality.CRITICAL: 0.95,
        TaskCriticality.IMPORTANT: 0.85,
        TaskCriticality.ROUTINE: 0.70,
        TaskCriticality.LOW_STAKES: 0.60
    },
    escalation_margin=0.10  # Escalate if within 10% of threshold
)

# Production calibration tracker
tracker = ECETracker(
    num_bins=10  # More bins for finer calibration
)

# Production replay engine
engine = ReplayEngine(
    context_loader=load_context_from_cmc,
    verify_hash=True
)
```

## Testing

### Unit Tests

```python
import pytest
from vif import VIF, KappaGate, TaskCriticality, ECETracker

def test_kappa_gate_pass():
    """Test κ-gate passing."""
    gate = KappaGate()
    result = gate.check(
        confidence=0.95,
        task_criticality=TaskCriticality.ROUTINE
    )
    assert result.passed is True

def test_kappa_gate_abstain():
    """Test κ-gate abstention."""
    gate = KappaGate()
    result = gate.check(
        confidence=0.60,
        task_criticality=TaskCriticality.CRITICAL
    )
    assert result.passed is False
    assert result.should_escalate is True

def test_ece_calculation():
    """Test ECE calculation."""
    tracker = ECETracker(num_bins=10)
    tracker.add_prediction(confidence=0.85, correct=True)
    tracker.add_prediction(confidence=0.90, correct=True)
    tracker.add_prediction(confidence=0.80, correct=False)
    
    ece = tracker.calculate_ece()
    assert 0.0 <= ece <= 1.0
```

### Integration Tests

```python
def test_complete_workflow():
    """Test complete VIF workflow."""
    # Extract confidence
    extraction = extract_confidence("I am 95% confident...")
    
    # Check κ-gate
    gate = KappaGate()
    gate_result = gate.check(
        confidence=extraction.confidence_score,
        task_criticality=TaskCriticality.ROUTINE
    )
    assert gate_result.passed is True
    
    # Create witness
    vif = create_witness(
        model_id="gpt-4-turbo",
        prompt="test",
        output="test output",
        context_snapshot_id="snap_123",
        confidence=extraction.confidence_score
    )
    
    # Store witness
    store = VIFStore(mock_cmc)
    atom_id = store.store_witness(vif)
    assert atom_id is not None
    
    # Replay
    engine = ReplayEngine()
    result = engine.replay(vif, operation_fn)
    assert result.matches_original
```

## Troubleshooting

### Issue: High ECE (Poor Calibration)

**Symptoms:** ECE > 0.10, indicating poor calibration.

**Solutions:**

```python
# Recalibrate confidence scores
def recalibrate_confidence(raw_confidence: float, ece: float) -> float:
    """Recalibrate confidence based on ECE."""
    # Apply calibration curve
    if ece > 0.10:
        # Reduce confidence (overconfident)
        return raw_confidence * 0.9
    return raw_confidence

# Use recalibrated confidence
calibrated = recalibrate_confidence(raw_confidence, ece)
```

### Issue: Replay Mismatch

**Symptoms:** Replay output hash doesn't match original.

**Solutions:**

```python
# Verify replay parameters match
def verify_replay_params(vif: VIF, params: Dict[str, Any]) -> bool:
    """Verify replay parameters match witness."""
    assert params["seed"] == vif.replay_seed
    assert params["temperature"] == vif.temperature
    assert params["top_p"] == vif.top_p
    return True

# Ensure deterministic model
model.set_temperature(0.0)  # Fully deterministic
model.set_seed(vif.replay_seed)
```

### Issue: κ-Gate False Positives

**Symptoms:** Gate passes but output is incorrect.

**Solutions:**

```python
# Adjust thresholds
gate.set_threshold(TaskCriticality.CRITICAL, 0.98)  # Higher threshold

# Use tighter escalation margin
gate = KappaGate(escalation_margin=0.05)  # Escalate closer to threshold
```

## Best Practices

### 1. Always Create Witnesses

```python
# Wrap all AI operations with VIF
def ai_operation_with_vif(prompt: str, context: List[Atom]):
    """Execute AI operation with VIF witness."""
    # Create context snapshot
    snapshot = create_snapshot(context)
    
    # Execute operation
    output = model.generate(prompt)
    confidence = extract_confidence(output)
    
    # Create witness
    vif = create_witness(
        model_id=model.id,
        prompt=prompt,
        output=output,
        context_snapshot_id=snapshot.id,
        confidence=confidence
    )
    
    # Store witness
    store.store_witness(vif)
    
    return output, vif
```

### 2. Monitor Calibration

```python
# Track calibration continuously
tracker = ECETracker()

# After each prediction
tracker.add_prediction(confidence=confidence, correct=is_correct)

# Check ECE periodically
if tracker.calculate_ece() > 0.10:
    alert("Poor calibration detected - recalibration needed")
```

### 3. Use κ-Gating for Critical Operations

```python
# Always gate critical operations
gate = KappaGate()

def critical_operation():
    """Critical operation with κ-gating."""
    output = model.generate("critical prompt")
    confidence = extract_confidence(output)
    
    result = gate.check(
        confidence=confidence,
        task_criticality=TaskCriticality.CRITICAL
    )
    
    if not result.passed:
        return escalate_to_hitl(result)
    
    return output
```

### 4. Enable Replay for Auditing

```python
# Always enable replay for critical operations
vif = create_witness(
    ...,
    replay_seed=random.randint(0, 2**32 - 1),
    temperature=0.0  # Deterministic
)

# Store witness for replay
store.store_witness(vif)

# Later: replay for audit
engine = ReplayEngine()
replay_result = engine.replay(vif, operation_fn)
assert replay_result.matches_original
```

## Advanced Topics

### Cross-Model Confidence Calibration

```python
from vif import CrossModelConfidenceCalibrator

# Create calibrator
calibrator = CrossModelConfidenceCalibrator()

# Calibrate across models
calibrated_confidence = calibrator.calibrate(
    model_id="gpt-4-turbo",
    raw_confidence=0.85,
    reference_model="gpt-3.5-turbo"
)

print(f"Calibrated confidence: {calibrated_confidence}")
```

### Witness Chains

```python
# Track operation lineage
parent_vif = create_witness(...)

# Child operation
child_vif = create_witness(
    ...,
    parent_vif_id=parent_vif.id
)

# Query chain
chain = store.get_witness_chain(parent_vif.id)
print(f"Chain length: {len(chain)}")
```

### Batch Witness Creation

```python
def create_witnesses_batch(operations: List[Operation]) -> List[VIF]:
    """Create witnesses for multiple operations."""
    witnesses = []
    for op in operations:
        vif = create_witness(
            model_id=op.model_id,
            prompt=op.prompt,
            output=op.output,
            context_snapshot_id=op.snapshot_id,
            confidence=op.confidence
        )
        witnesses.append(vif)
    
    # Batch store
    store.batch_store_witnesses(witnesses)
    
    return witnesses
```

## Data Models and Schemas

This section documents the complete data models used by VIF.

### ConfidenceBand Enum

**Purpose:** User-facing confidence indicator bands.

```python
class ConfidenceBand(str, Enum):
    """Confidence bands for user trust indicators"""
    A = "A"  # High confidence (≥0.95) - 🟢 Green
    B = "B"  # Medium confidence (0.80-0.94) - 🟡 Yellow
    C = "C"  # Low confidence (<0.80) - 🔴 Red
```

### TaskCriticality Enum

**Purpose:** Task criticality levels determining κ thresholds.

```python
class TaskCriticality(str, Enum):
    """Task criticality levels for κ-gate thresholds"""
    CRITICAL = "critical"      # Medical, legal, safety-critical → κ=0.95
    IMPORTANT = "important"    # Financial, strategic → κ=0.85
    ROUTINE = "routine"        # Standard operations → κ=0.70
    LOW_STAKES = "low_stakes"  # Experimental, low-impact → κ=0.60
```

### KappaGateResult Model

**Purpose:** Result of κ-gate evaluation.

```python
@dataclass
class KappaGateResult:
    """Result of κ-gate check"""
    passed: bool  # Whether gate passed
    confidence: float  # Reported confidence
    threshold: float  # κ threshold used
    task_criticality: TaskCriticality  # Task criticality
    gap: float  # How far above/below threshold
    should_escalate: bool = False  # Should escalate to human
    escalation_reason: Optional[str] = None  # Why escalating
    
    @property
    def margin(self) -> float:
        """Safety margin above threshold (positive if passed)"""
        return self.confidence - self.threshold
```

### CalibrationBin Model

**Purpose:** Bin for calibration tracking.

```python
@dataclass
class CalibrationBin:
    """A bin for calibration tracking"""
    confidence_range: Tuple[float, float]  # (min, max) confidence
    predictions: List[float] = field(default_factory=list)  # Predicted confidences
    outcomes: List[bool] = field(default_factory=list)  # Actual outcomes
    
    @property
    def count(self) -> int:
        """Number of predictions in this bin"""
        return len(self.predictions)
    
    @property
    def avg_confidence(self) -> float:
        """Average predicted confidence"""
        return sum(self.predictions) / len(self.predictions) if self.predictions else 0.0
    
    @property
    def accuracy(self) -> float:
        """Actual accuracy (fraction correct)"""
        return sum(self.outcomes) / len(self.outcomes) if self.outcomes else 0.0
    
    @property
    def calibration_gap(self) -> float:
        """Gap between confidence and accuracy"""
        return abs(self.avg_confidence - self.accuracy)
```

### ReplayResult Model

**Purpose:** Result of replay operation.

```python
@dataclass
class ReplayResult:
    """Result of replay operation"""
    success: bool  # Whether replay succeeded
    output: Optional[Any] = None  # Replayed output
    output_hash: Optional[str] = None  # Hash of replayed output
    matches_original: bool = False  # Whether hash matches original
    original_hash: Optional[str] = None  # Original output hash
    error: Optional[str] = None  # Error message if failed
    execution_time_ms: float = 0.0  # Execution time
```

## Advanced Implementation Details

### Confidence Extraction Algorithm

**Extract Confidence from LLM Output:**

```python
def extract_confidence(text: str) -> ConfidenceExtraction:
    """
    Extract confidence score from LLM output text.
    
    Methods (in order):
    1. Explicit confidence statements ("I am 95% confident")
    2. Hedging language analysis (reduces confidence)
    3. Uncertainty/confidence marker analysis
    4. Default (0.70 for neutral text)
    
    Args:
        text: LLM output text
    
    Returns:
        ConfidenceExtraction: Confidence score and metadata
    
    Example:
        extraction = extract_confidence("I am 95% confident that...")
        assert extraction.confidence_score == 0.95
        assert extraction.extraction_method == "explicit"
    """
    text_lower = text.lower()
    
    # Method 1: Explicit confidence
    explicit_result = _extract_explicit_confidence(text_lower)
    if explicit_result:
        return explicit_result
    
    # Method 2: Hedging analysis
    hedging_result = _analyze_hedging(text_lower)
    if hedging_result:
        return hedging_result
    
    # Method 3: Uncertainty/confidence markers
    marker_result = _analyze_markers(text_lower)
    if marker_result:
        return marker_result
    
    # Method 4: Default
    return ConfidenceExtraction(
        confidence_score=0.70,
        extraction_method="default"
    )
```

**Explicit Confidence Pattern Matching:**

```python
EXPLICIT_PATTERNS = [
    # "I am X% confident"
    r"(?:i am|i'm|confidence|confident)\s+(?:about\s+)?(\d+)%",
    r"(\d+)%\s+(?:confidence|confident|sure|certain)",
    
    # "X out of 10"
    r"(\d+)\s+(?:out of|/)\s+10",
    
    # "very confident" → map to score
    r"(very|extremely|highly)\s+(?:confident|certain|sure)",
    r"(somewhat|moderately|fairly)\s+(?:confident|certain|sure)",
    r"(not very|slightly|barely)\s+(?:confident|certain|sure)",
]

def _extract_explicit_confidence(text: str) -> Optional[ConfidenceExtraction]:
    """Extract explicit confidence statement."""
    for pattern in EXPLICIT_PATTERNS:
        match = re.search(pattern, text)
        if match:
            if "%" in pattern:
                # Percentage confidence
                percent = int(match.group(1))
                confidence = percent / 100.0
                return ConfidenceExtraction(
                    confidence_score=confidence,
                    extraction_method="explicit_percentage",
                    explicit_statement=match.group(0)
                )
            elif "out of" in pattern or "/" in pattern:
                # Out of 10 scale
                score = int(match.group(1))
                confidence = score / 10.0
                return ConfidenceExtraction(
                    confidence_score=confidence,
                    extraction_method="explicit_scale",
                    explicit_statement=match.group(0)
                )
            elif "very" in pattern or "extremely" in pattern:
                # High confidence markers
                return ConfidenceExtraction(
                    confidence_score=0.90,
                    extraction_method="explicit_high",
                    explicit_statement=match.group(0)
                )
            elif "somewhat" in pattern or "moderately" in pattern:
                # Medium confidence markers
                return ConfidenceExtraction(
                    confidence_score=0.70,
                    extraction_method="explicit_medium",
                    explicit_statement=match.group(0)
                )
            elif "not very" in pattern or "slightly" in pattern:
                # Low confidence markers
                return ConfidenceExtraction(
                    confidence_score=0.50,
                    extraction_method="explicit_low",
                    explicit_statement=match.group(0)
                )
    return None
```

**Hedging Language Analysis:**

```python
HEDGING_PHRASES = [
    "might", "maybe", "perhaps", "possibly", "probably",
    "could be", "may be", "seems like", "appears to",
    "i think", "i believe", "i guess", "i suppose",
    "likely", "unlikely", "uncertain", "unclear",
]

def _analyze_hedging(text: str) -> Optional[ConfidenceExtraction]:
    """Analyze hedging language to estimate confidence."""
    hedging_count = sum(1 for phrase in HEDGING_PHRASES if phrase in text)
    
    if hedging_count == 0:
        return None
    
    # More hedging = lower confidence
    # Base confidence: 0.70
    # Reduce by 0.10 per hedging phrase (minimum 0.30)
    confidence_reduction = min(hedging_count * 0.10, 0.40)
    confidence = max(0.70 - confidence_reduction, 0.30)
    
    detected_phrases = [phrase for phrase in HEDGING_PHRASES if phrase in text]
    
    return ConfidenceExtraction(
        confidence_score=confidence,
        extraction_method="hedging",
        hedging_detected=True,
        uncertainty_markers=detected_phrases
    )
```

### ECE Calculation Algorithm

**Detailed ECE Calculation:**

```python
def calculate_ece_detailed(tracker: ECETracker) -> Dict[str, float]:
    """
    Calculate comprehensive calibration metrics.
    
    Returns:
        Dictionary with ECE, MCE, RMSCE, and bin details
    """
    total_predictions = sum(bin.count for bin in tracker.bins)
    
    if total_predictions == 0:
        return {
            "ece": 0.0,
            "mce": 0.0,
            "rmsce": 0.0,
            "total_predictions": 0,
            "non_empty_bins": 0
        }
    
    # Calculate ECE
    ece = 0.0
    gaps = []
    
    for bin in tracker.bins:
        if bin.count > 0:
            weight = bin.count / total_predictions
            gap = bin.calibration_gap
            ece += weight * gap
            gaps.append(gap)
    
    # Calculate MCE (Maximum Calibration Error)
    mce = max(gaps) if gaps else 0.0
    
    # Calculate RMSCE (Root Mean Squared Calibration Error)
    rmsce_squared = 0.0
    for bin in tracker.bins:
        if bin.count > 0:
            weight = bin.count / total_predictions
            gap = bin.avg_confidence - bin.accuracy
            rmsce_squared += weight * (gap ** 2)
    rmsce = math.sqrt(rmsce_squared)
    
    return {
        "ece": ece,
        "mce": mce,
        "rmsce": rmsce,
        "total_predictions": total_predictions,
        "non_empty_bins": sum(1 for bin in tracker.bins if bin.count > 0)
    }
```

### Replay Verification Algorithm

**Verify Replay Success:**

```python
def verify_replay(
    original_vif: VIF,
    replayed_output: str,
    tolerance: float = 0.0
) -> ReplayVerification:
    """
    Verify replay output matches original.
    
    Args:
        original_vif: Original VIF witness
        replayed_output: Output from replay operation
        tolerance: Tolerance for hash comparison (0.0 = exact match)
    
    Returns:
        ReplayVerification: Verification result
    
    Verification Steps:
        1. Compare output hash
        2. Compare token count
        3. Compare structure (if applicable)
        4. Check execution time (should be similar)
    """
    # Hash replayed output
    replayed_hash = hashlib.sha256(replayed_output.encode()).hexdigest()
    
    # Compare hashes
    hash_match = (replayed_hash == original_vif.output_hash)
    
    # Compare token counts
    replayed_tokens = estimate_tokens(replayed_output)
    token_match = (replayed_tokens == original_vif.output_tokens)
    
    # Overall match
    matches = hash_match and token_match
    
    return ReplayVerification(
        matches=matches,
        hash_match=hash_match,
        token_match=token_match,
        original_hash=original_vif.output_hash,
        replayed_hash=replayed_hash,
        original_tokens=original_vif.output_tokens,
        replayed_tokens=replayed_tokens
    )
```

## Deployment Guide

### Local Development Setup

**Step 1: Install Dependencies**

```bash
# Install Python 3.10+
python --version  # Should be 3.10+

# Install VIF package
cd packages/vif
pip install -e .

# Install dependencies
pip install pydantic numpy pytest

# Verify installation
python -c "from vif import VIF, KappaGate, ECETracker; print('VIF installed successfully')"
```

**Step 2: Configure CMC Integration**

```python
from vif import VIFStore
from cmc_service import MemoryStore

# Connect to CMC
store = MemoryStore(Path("./data/cmc"))

# Create VIF store
vif_store = VIFStore(store)

# Test witness storage
vif = create_witness(...)
atom_id = vif_store.store_witness(vif)
print(f"Stored witness: {atom_id}")
```

**Step 3: Test κ-Gating**

```python
from vif import KappaGate, TaskCriticality

# Create gate
gate = KappaGate()

# Test routine task
result = gate.check(
    confidence=0.75,
    task_criticality=TaskCriticality.ROUTINE
)
assert result.passed is True

# Test critical task (should fail)
result = gate.check(
    confidence=0.75,
    task_criticality=TaskCriticality.CRITICAL
)
assert result.passed is False
```

### Production Deployment

**Step 1: Environment Configuration**

```bash
# Production environment variables
export VIF_DEFAULT_KAPPA_CRITICAL=0.95
export VIF_DEFAULT_KAPPA_IMPORTANT=0.85
export VIF_DEFAULT_KAPPA_ROUTINE=0.70
export VIF_DEFAULT_KAPPA_LOW_STAKES=0.60
export VIF_ECE_BINS=10
export VIF_ECE_THRESHOLD=0.10
export VIF_REPLAY_ENABLED=true
export VIF_REPLAY_VERIFY_HASH=true
```

**Step 2: Docker Deployment**

**Dockerfile:**

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY packages/vif/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy VIF package
COPY packages/vif/ ./vif/

# Set environment
ENV VIF_REPLAY_ENABLED=true
ENV VIF_REPLAY_VERIFY_HASH=true

# Run VIF service
CMD ["python", "-m", "vif.service"]
```

## Performance Tuning

### Witness Creation Optimization

**Batch Witness Creation:**

```python
def batch_create_witnesses(operations: List[Operation]) -> List[VIF]:
    """Create witnesses for multiple operations efficiently."""
    # Parallel witness creation
    from concurrent.futures import ThreadPoolExecutor
    
    witnesses = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(create_witness, **op.to_dict())
            for op in operations
        ]
        
        for future in futures:
            witness = future.result()
            witnesses.append(witness)
    
    # Batch store in CMC
    vif_store.batch_store_witnesses(witnesses)
    
    return witnesses
```

### Calibration Tracker Optimization

**Efficient ECE Calculation:**

```python
class OptimizedECETracker(ECETracker):
    """Optimized ECE tracker with caching."""
    
    def __init__(self, num_bins: int = 10):
        super().__init__(num_bins)
        self._cached_ece: Optional[float] = None
        self._cache_dirty: bool = False
    
    def add_prediction(self, confidence: float, correct: bool, **kwargs):
        """Add prediction and invalidate cache."""
        super().add_prediction(confidence, correct, **kwargs)
        self._cache_dirty = True
    
    def calculate_ece(self) -> float:
        """Calculate ECE with caching."""
        if self._cached_ece is None or self._cache_dirty:
            self._cached_ece = super().calculate_ece()
            self._cache_dirty = False
        return self._cached_ece
```

## Security Considerations

### Witness Integrity

**Cryptographic Verification:**

```python
def sign_witness(vif: VIF, private_key: bytes) -> str:
    """Sign witness with cryptographic signature."""
    # Create canonical representation
    canonical = json.dumps(vif.to_dict(), sort_keys=True)
    
    # Sign with private key
    signature = cryptography.sign(canonical.encode(), private_key)
    
    # Add signature to witness
    vif.signature = signature.hex()
    
    return signature.hex()

def verify_witness(vif: VIF, public_key: bytes) -> bool:
    """Verify witness signature."""
    if not vif.signature:
        return False
    
    # Create canonical representation
    canonical = json.dumps(vif.to_dict(), sort_keys=True)
    
    # Verify signature
    signature_bytes = bytes.fromhex(vif.signature)
    return cryptography.verify(canonical.encode(), signature_bytes, public_key)
```

### Access Control

**Restrict Witness Access:**

```python
class SecureVIFStore(VIFStore):
    """VIF store with access control."""
    
    def __init__(self, store: MemoryStore, allowed_users: List[str]):
        super().__init__(store)
        self.allowed_users = set(allowed_users)
    
    def store_witness(self, vif: VIF, user_id: str) -> str:
        """Store witness with user authentication."""
        if user_id not in self.allowed_users:
            raise PermissionError(f"User {user_id} not authorized")
        
        return super().store_witness(vif)
    
    def query_witnesses(self, user_id: str, **filters) -> List[VIF]:
        """Query witnesses with user authentication."""
        if user_id not in self.allowed_users:
            raise PermissionError(f"User {user_id} not authorized")
        
        return super().query_witnesses(**filters)
```

## Real-World Use Cases

### Use Case 1: Medical Diagnosis System

**Scenario:** AI system for medical diagnosis with VIF provenance.

```python
# Medical diagnosis with VIF
def diagnose_with_vif(symptoms: str, patient_history: List[Atom]):
    """Diagnose with complete VIF provenance."""
    # Create context snapshot
    snapshot = create_snapshot(patient_history)
    
    # Generate diagnosis
    diagnosis = model.generate(f"Diagnose: {symptoms}")
    confidence = extract_confidence(diagnosis)
    
    # κ-gate check (CRITICAL task)
    gate = KappaGate()
    gate_result = gate.check(
        confidence=confidence,
        task_criticality=TaskCriticality.CRITICAL
    )
    
    if not gate_result.passed:
        # Escalate to human doctor
        return escalate_to_human_doctor(gate_result)
    
    # Create witness
    vif = create_witness(
        model_id="medical-ai-v1",
        prompt=f"Diagnose: {symptoms}",
        output=diagnosis,
        context_snapshot_id=snapshot.id,
        confidence=confidence,
        task_criticality=TaskCriticality.CRITICAL,
        replay_seed=random.randint(0, 2**32 - 1),
        temperature=0.0  # Deterministic
    )
    
    # Store witness (legal requirement)
    store.store_witness(vif)
    
    # Link to patient record
    link_to_patient_record(vif, patient_id)
    
    return diagnosis, vif
```

### Use Case 2: Code Generation System

**Scenario:** AI code generation with VIF for auditability.

```python
# Code generation with VIF
def generate_code_with_vif(requirements: str, context: List[Atom]):
    """Generate code with VIF provenance."""
    # Create context snapshot
    snapshot = create_snapshot(context)
    
    # Generate code
    code = model.generate(f"Generate code: {requirements}")
    confidence = extract_confidence(code)
    
    # κ-gate check (IMPORTANT task)
    gate = KappaGate()
    gate_result = gate.check(
        confidence=confidence,
        task_criticality=TaskCriticality.IMPORTANT
    )
    
    if not gate_result.passed:
        # Request human review
        return request_code_review(gate_result)
    
    # Create witness
    vif = create_witness(
        model_id="code-gen-v1",
        prompt=f"Generate code: {requirements}",
        output=code,
        context_snapshot_id=snapshot.id,
        confidence=confidence,
        task_criticality=TaskCriticality.IMPORTANT
    )
    
    # Store witness
    store.store_witness(vif)
    
    # Link to code review
    link_to_code_review(vif, review_id)
    
    return code, vif
```

### Use Case 3: Legal Document Analysis

**Scenario:** Legal document analysis with deterministic replay.

```python
# Legal analysis with replay
def analyze_legal_document(document: str, case_law: List[Atom]):
    """Analyze legal document with replay capability."""
    # Create context snapshot
    snapshot = create_snapshot(case_law)
    
    # Generate analysis
    analysis = model.generate(f"Analyze: {document}")
    confidence = extract_confidence(analysis)
    
    # κ-gate check (CRITICAL task)
    gate = KappaGate()
    gate_result = gate.check(
        confidence=confidence,
        task_criticality=TaskCriticality.CRITICAL
    )
    
    if not gate_result.passed:
        # Escalate to human lawyer
        return escalate_to_lawyer(gate_result)
    
    # Create witness with replay
    replay_seed = random.randint(0, 2**32 - 1)
    vif = create_witness(
        model_id="legal-ai-v1",
        prompt=f"Analyze: {document}",
        output=analysis,
        context_snapshot_id=snapshot.id,
        confidence=confidence,
        task_criticality=TaskCriticality.CRITICAL,
        replay_seed=replay_seed,
        temperature=0.0  # Deterministic for legal compliance
    )
    
    # Store witness (legal requirement)
    store.store_witness(vif)
    
    # Enable replay for audit
    engine = ReplayEngine()
    replay_result = engine.replay(vif, operation_fn)
    
    if not replay_result.matches_original:
        alert("Replay verification failed - audit concern!")
    
    return analysis, vif
```

## Monitoring and Observability

### Metrics Collection

**Prometheus Metrics:**

```python
from prometheus_client import Counter, Histogram, Gauge

# Metrics
WITNESS_CREATED = Counter('vif_witnesses_created_total', 'Total witnesses created')
KAPPA_GATE_FAILED = Counter('vif_kappa_gate_failed_total', 'Total κ-gate failures')
ECE_SCORE = Gauge('vif_ece_score', 'Current ECE score')
REPLAY_SUCCESS_RATE = Gauge('vif_replay_success_rate', 'Replay success rate')

# Instrument witness creation
def instrumented_create_witness(**kwargs) -> VIF:
    """Create witness with metrics."""
    WITNESS_CREATED.inc()
    
    vif = create_witness(**kwargs)
    
    # Record κ-gate status
    if not vif.kappa_gate_passed:
        KAPPA_GATE_FAILED.inc()
    
    return vif
```

### Health Checks

**Health Check Endpoint:**

```python
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/health")
def health_check():
    """Health check endpoint."""
    # Check CMC connection
    try:
        store.list_atoms(limit=1)
        cmc_healthy = True
    except Exception:
        cmc_healthy = False
    
    # Check calibration tracker
    try:
        tracker = ECETracker()
        tracker.calculate_ece()
        calibration_healthy = True
    except Exception:
        calibration_healthy = False
    
    # Overall health
    healthy = cmc_healthy and calibration_healthy
    
    if healthy:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": "healthy",
                "cmc": "connected",
                "calibration": "operational"
            }
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "unhealthy",
                "cmc": "connected" if cmc_healthy else "disconnected",
                "calibration": "operational" if calibration_healthy else "error"
            }
        )
```

## Common Patterns and Recipes

### Pattern 1: Confidence Wrapper

**Wrap Model Operations with VIF:**

```python
def vif_wrapped_model(model: Any, store: VIFStore):
    """Wrap model with VIF witness creation."""
    
    def wrapped_generate(prompt: str, context: List[Atom], **kwargs):
        """Generate with VIF witness."""
        # Create snapshot
        snapshot = create_snapshot(context)
        
        # Generate
        output = model.generate(prompt, **kwargs)
        confidence = extract_confidence(output)
        
        # κ-gate check
        gate = KappaGate()
        gate_result = gate.check(
            confidence=confidence,
            task_criticality=kwargs.get("task_criticality", TaskCriticality.ROUTINE)
        )
        
        if not gate_result.passed:
            raise ConfidenceTooLow(gate_result.escalation_reason)
        
        # Create witness
        vif = create_witness(
            model_id=model.id,
            prompt=prompt,
            output=output,
            context_snapshot_id=snapshot.id,
            confidence=confidence,
            task_criticality=kwargs.get("task_criticality", TaskCriticality.ROUTINE)
        )
        
        # Store witness
        store.store_witness(vif)
        
        return output, vif
    
    return wrapped_generate
```

### Pattern 2: Calibration Monitoring

**Monitor Calibration Continuously:**

```python
class CalibrationMonitor:
    """Monitor calibration and alert on degradation."""
    
    def __init__(self, alert_threshold: float = 0.10):
        self.tracker = ECETracker(num_bins=10)
        self.alert_threshold = alert_threshold
    
    def record_prediction(self, confidence: float, correct: bool):
        """Record prediction and check calibration."""
        self.tracker.add_prediction(confidence, correct)
        
        # Check ECE periodically
        ece = self.tracker.calculate_ece()
        
        if ece > self.alert_threshold:
            alert(f"Poor calibration detected: ECE={ece:.3f}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get calibration status."""
        summary = self.tracker.get_calibration_summary()
        
        return {
            "ece": summary["ece"],
            "status": "well_calibrated" if summary["ece"] < 0.05 else
                     "acceptable" if summary["ece"] < 0.10 else
                     "poorly_calibrated",
            "total_predictions": summary["total_predictions"]
        }
```

### Pattern 3: Replay Verification

**Verify Replay for Critical Operations:**

```python
def verify_critical_replay(vif: VIF, operation_fn: Callable) -> bool:
    """Verify replay for critical operations."""
    engine = ReplayEngine()
    
    # Replay operation
    result = engine.replay(vif, operation_fn, verify_hash=True)
    
    if not result.matches_original:
        # Critical failure - alert immediately
        alert("CRITICAL: Replay verification failed!", {
            "vif_id": vif.id,
            "original_hash": result.original_hash,
            "replayed_hash": result.output_hash,
            "error": result.error
        })
        return False
    
    return True
```

## Debugging and Diagnostics

### Debug Mode

**Enable Debug Logging:**

```python
import logging

# Configure debug logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Enable VIF debug logging
logger = logging.getLogger("vif")
logger.setLevel(logging.DEBUG)

# All operations will be logged
vif = create_witness(...)  # Logged with full details
```

### Diagnostic Tools

**Witness Inspector:**

```python
def inspect_witness(vif: VIF):
    """Inspect witness for debugging."""
    print(f"Witness ID: {vif.id}")
    print(f"Model: {vif.model_id}")
    print(f"Confidence: {vif.confidence_score:.3f}")
    print(f"Confidence Band: {vif.confidence_band}")
    print(f"κ-Gate Passed: {vif.kappa_gate_passed}")
    print(f"Task Criticality: {vif.task_criticality}")
    print(f"Replay Seed: {vif.replay_seed}")
    print(f"Created At: {vif.created_at}")

# Use inspector
inspect_witness(vif)
```

**Calibration Diagnostics:**

```python
def diagnose_calibration(tracker: ECETracker):
    """Diagnose calibration issues."""
    summary = tracker.get_calibration_summary()
    bin_details = tracker.get_bin_details()
    
    print(f"ECE: {summary['ece']:.4f}")
    print(f"MCE: {summary['mce']:.4f}")
    print(f"RMSCE: {summary['rmsce']:.4f}")
    print(f"Total Predictions: {summary['total_predictions']}")
    
    print("\nBin Details:")
    for bin_detail in bin_details:
        print(f"  Bin {bin_detail['bin']}: "
              f"Confidence={bin_detail['avg_confidence']:.3f}, "
              f"Accuracy={bin_detail['accuracy']:.3f}, "
              f"Gap={bin_detail['calibration_gap']:.3f}")

# Use diagnostics
diagnose_calibration(tracker)
```

## Complete Code Examples

### Example 1: Basic Witness Creation

```python
from vif import VIF, create_witness, ConfidenceBand, TaskCriticality
from datetime import datetime, timezone

# Simple AI operation
prompt = "What is the capital of France?"
output = "Paris"
confidence = 0.95

# Create witness
vif = create_witness(
    model_id="gpt-4-turbo",
    model_provider="openai",
    prompt=prompt,
    output=output,
    context_snapshot_id="snap_123",
    confidence=confidence,
    task_criticality=TaskCriticality.ROUTINE
)

print(f"Witness ID: {vif.id}")
print(f"Confidence Band: {vif.confidence_band}")  # A
print(f"κ-Gate Passed: {vif.kappa_gate_passed}")  # True
```

### Example 2: κ-Gate with Escalation

```python
from vif import KappaGate, TaskCriticality

# Critical operation requiring high confidence
gate = KappaGate()

# Low confidence for critical task
result = gate.check(
    confidence=0.80,
    task_criticality=TaskCriticality.CRITICAL
)

if not result.passed:
    print(f"Operation refused: {result.escalation_reason}")
    print(f"Confidence: {result.confidence:.2%}")
    print(f"Required: {result.threshold:.2%}")
    
    # Escalate to human
    escalate_to_hitl(result)
else:
    print("Operation approved")
```

### Example 3: Calibration Tracking

```python
from vif import ECETracker

# Create tracker
tracker = ECETracker(num_bins=10)

# Record predictions over time
predictions = [
    (0.95, True),   # High confidence, correct
    (0.90, True),   # High confidence, correct
    (0.85, False),  # High confidence, incorrect (overconfident)
    (0.70, True),   # Medium confidence, correct
    (0.60, False),  # Low confidence, incorrect
]

for confidence, correct in predictions:
    tracker.add_prediction(confidence, correct)

# Calculate ECE
ece = tracker.calculate_ece()
print(f"ECE: {ece:.4f}")

# Get calibration summary
summary = tracker.get_calibration_summary()
print(f"Calibration Status: {summary}")

# Check calibration quality
if ece > 0.10:
    print("Warning: Poor calibration detected - recalibration needed")
```

### Example 4: Deterministic Replay

```python
from vif import ReplayEngine
import random

# Original operation
original_output, vif = generate_with_replay(
    prompt="What is 2+2?",
    context=[],
    model_id="gpt-4-turbo",
    task_criticality=TaskCriticality.ROUTINE
)

print(f"Original output: {original_output}")
print(f"Replay seed: {vif.replay_seed}")

# Replay operation
engine = ReplayEngine()
replay_result = engine.replay(
    vif=vif,
    operation=lambda params: model.generate(**params),
    verify_hash=True
)

if replay_result.matches_original:
    print("✅ Replay successful - bit-identical output!")
else:
    print(f"❌ Replay mismatch: {replay_result.error}")
```

### Example 5: Complete Workflow

```python
from vif import (
    VIF, create_witness, KappaGate, ECETracker,
    ReplayEngine, extract_confidence, TaskCriticality
)
from cmc_service import MemoryStore

# Initialize components
store = MemoryStore(Path("./data/cmc"))
vif_store = VIFStore(store)
gate = KappaGate()
tracker = ECETracker()
engine = ReplayEngine()

# Step 1: Generate output
prompt = "Analyze this code for security vulnerabilities"
output = model.generate(prompt)
confidence = extract_confidence(output).confidence_score

# Step 2: κ-gate check
gate_result = gate.check(
    confidence=confidence,
    task_criticality=TaskCriticality.IMPORTANT
)

if not gate_result.passed:
    escalate_to_hitl(gate_result)
    return

# Step 3: Create witness
snapshot = create_snapshot(context)
vif = create_witness(
    model_id="security-ai-v1",
    prompt=prompt,
    output=output,
    context_snapshot_id=snapshot.id,
    confidence=confidence,
    task_criticality=TaskCriticality.IMPORTANT,
    replay_seed=random.randint(0, 2**32 - 1)
)

# Step 4: Store witness
atom_id = vif_store.store_witness(vif)

# Step 5: Record for calibration
tracker.add_prediction(confidence, correct=None)  # Verify later

# Step 6: Verify replay
replay_result = engine.replay(vif, operation_fn)
assert replay_result.matches_original

print(f"Complete workflow successful - witness {vif.id} stored")
```

## Storage Architecture

### CMC Storage Integration

**Witness Storage as Atoms:**

```python
class VIFStore:
    """Store VIF witnesses in CMC as atoms."""
    
    def __init__(self, cmc_store: MemoryStore):
        self.store = cmc_store
    
    def store_witness(self, vif: VIF) -> str:
        """Store witness as CMC atom."""
        # Convert VIF to atom
        atom = self.store.create_atom(
            AtomCreate(
                modality="vif_witness",
                content=AtomContent(inline=json.dumps(vif.to_dict())),
                tags={
                    "vif_id": vif.id,
                    "model_id": vif.model_id,
                    "confidence_band": vif.confidence_band.value,
                    "task_criticality": vif.task_criticality.value
                },
                metadata={
                    "vif": vif.to_dict(),
                    "created_at": vif.created_at.isoformat()
                }
            )
        )
        
        return atom.id
    
    def query_witnesses(
        self,
        model_id: Optional[str] = None,
        confidence_min: Optional[float] = None,
        task_criticality: Optional[TaskCriticality] = None,
        time_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[VIF]:
        """Query witnesses by filters."""
        # Build query filters
        filters = {}
        
        if model_id:
            filters["model_id"] = model_id
        
        if confidence_min:
            filters["confidence_min"] = confidence_min
        
        if task_criticality:
            filters["task_criticality"] = task_criticality.value
        
        # Query atoms
        atoms = self.store.query_atoms(
            modality="vif_witness",
            filters=filters,
            time_range=time_range
        )
        
        # Convert to VIF
        witnesses = []
        for atom in atoms:
            vif_dict = atom.metadata.get("vif")
            if vif_dict:
                witnesses.append(VIF(**vif_dict))
        
        return witnesses
```

### Witness Indexing

**Index Witnesses for Fast Lookup:**

```python
class WitnessIndex:
    """Index witnesses for fast lookup."""
    
    def __init__(self):
        self.by_model: Dict[str, List[str]] = {}  # model_id -> [vif_ids]
        self.by_confidence: Dict[ConfidenceBand, List[str]] = {}  # band -> [vif_ids]
        self.by_criticality: Dict[TaskCriticality, List[str]] = {}  # criticality -> [vif_ids]
        self.by_time: List[Tuple[datetime, str]] = []  # (timestamp, vif_id)
    
    def add_witness(self, vif: VIF):
        """Add witness to index."""
        # Index by model
        self.by_model.setdefault(vif.model_id, []).append(vif.id)
        
        # Index by confidence band
        self.by_confidence.setdefault(vif.confidence_band, []).append(vif.id)
        
        # Index by criticality
        self.by_criticality.setdefault(vif.task_criticality, []).append(vif.id)
        
        # Index by time
        self.by_time.append((vif.created_at, vif.id))
    
    def query_by_model(self, model_id: str) -> List[str]:
        """Query witnesses by model."""
        return self.by_model.get(model_id, [])
    
    def query_by_confidence_band(self, band: ConfidenceBand) -> List[str]:
        """Query witnesses by confidence band."""
        return self.by_confidence.get(band, [])
    
    def query_by_time_range(
        self,
        start: datetime,
        end: datetime
    ) -> List[str]:
        """Query witnesses by time range."""
        return [
            vif_id for timestamp, vif_id in self.by_time
            if start <= timestamp <= end
        ]
```

## Advanced Configuration

### Custom κ Thresholds

**Configure Custom Thresholds:**

```python
# Custom thresholds for specific use cases
custom_gate = KappaGate(
    thresholds={
        TaskCriticality.CRITICAL: 0.98,  # Very strict
        TaskCriticality.IMPORTANT: 0.90,  # Higher than default
        TaskCriticality.ROUTINE: 0.70,    # Standard
        TaskCriticality.LOW_STAKES: 0.50  # More lenient
    },
    escalation_margin=0.05  # Tighter escalation
)

# Use custom gate
result = custom_gate.check(
    confidence=0.85,
    task_criticality=TaskCriticality.CRITICAL
)
```

### Calibration Configuration

**Configure Calibration Tracker:**

```python
# High-resolution calibration tracker
tracker = ECETracker(
    num_bins=20  # More bins for finer calibration
)

# Custom calibration thresholds
CALIBRATION_THRESHOLDS = {
    "excellent": 0.05,  # ECE < 0.05
    "good": 0.10,      # ECE < 0.10
    "poor": 0.20       # ECE > 0.20
}

def get_calibration_status(tracker: ECETracker) -> str:
    """Get calibration status with custom thresholds."""
    ece = tracker.calculate_ece()
    
    if ece < CALIBRATION_THRESHOLDS["excellent"]:
        return "excellent"
    elif ece < CALIBRATION_THRESHOLDS["good"]:
        return "good"
    elif ece < CALIBRATION_THRESHOLDS["poor"]:
        return "acceptable"
    else:
        return "poor"
```

### Replay Configuration

**Configure Replay Engine:**

```python
# Custom replay engine with retry
class RetryReplayEngine(ReplayEngine):
    """Replay engine with retry logic."""
    
    def __init__(self, max_retries: int = 3, **kwargs):
        super().__init__(**kwargs)
        self.max_retries = max_retries
    
    def replay_with_retry(
        self,
        vif: VIF,
        operation: Callable,
        **kwargs
    ) -> ReplayResult:
        """Replay with retry on failure."""
        for attempt in range(self.max_retries):
            result = self.replay(vif, operation, **kwargs)
            
            if result.matches_original:
                return result
            
            # Retry with slight delay
            time.sleep(0.1 * (attempt + 1))
        
        return result  # Return last attempt
```

## Scalability Considerations

### Distributed Witness Storage

**Sharded Witness Storage:**

```python
class ShardedVIFStore:
    """Sharded witness storage for scalability."""
    
    def __init__(self, shards: List[VIFStore]):
        self.shards = shards
        self.shard_count = len(shards)
    
    def get_shard(self, vif_id: str) -> VIFStore:
        """Get shard for witness."""
        shard_index = hash(vif_id) % self.shard_count
        return self.shards[shard_index]
    
    def store_witness(self, vif: VIF) -> str:
        """Store witness on appropriate shard."""
        shard = self.get_shard(vif.id)
        return shard.store_witness(vif)
    
    def query_witnesses(self, **filters) -> List[VIF]:
        """Query witnesses from all shards."""
        all_witnesses = []
        
        for shard in self.shards:
            witnesses = shard.query_witnesses(**filters)
            all_witnesses.extend(witnesses)
        
        # Deduplicate and sort
        unique_witnesses = {w.id: w for w in all_witnesses}
        return sorted(
            unique_witnesses.values(),
            key=lambda w: w.created_at,
            reverse=True
        )
```

### Caching Strategy

**Multi-Level Witness Cache:**

```python
class CachedVIFStore(VIFStore):
    """VIF store with multi-level caching."""
    
    def __init__(self, store: MemoryStore):
        super().__init__(store)
        self.memory_cache: Dict[str, VIF] = {}  # L1: In-memory
        self.redis_cache = RedisCache(ttl=3600)  # L2: Redis
        self.cache_size = 10000
    
    def get_witness(self, vif_id: str) -> Optional[VIF]:
        """Get witness with caching."""
        # Try L1 cache
        if vif_id in self.memory_cache:
            return self.memory_cache[vif_id]
        
        # Try L2 cache
        cached = self.redis_cache.get(f"vif:{vif_id}")
        if cached:
            self.memory_cache[vif_id] = cached
            return cached
        
        # Load from CMC
        witness = super().get_witness(vif_id)
        
        if witness:
            # Populate caches
            self.redis_cache.set(f"vif:{vif_id}", witness)
            if len(self.memory_cache) < self.cache_size:
                self.memory_cache[vif_id] = witness
        
        return witness
```

---

## References

- **System Map:** `knowledge_architecture/systems/vif/system.map.lucid.json5`
- **L2 Architecture:** `knowledge_architecture/systems/vif/L2_architecture.md`
- **L4 Complete Reference:** `knowledge_architecture/systems/vif/L4_complete.md`
- **Implementation:** `packages/vif/`
- **Tests:** `packages/vif/tests/`

---

**Read L4 for complete reference:**
- **L4 Complete Reference:** `knowledge_architecture/systems/vif/L4_complete.md` - Exhaustive 15,000+ word reference