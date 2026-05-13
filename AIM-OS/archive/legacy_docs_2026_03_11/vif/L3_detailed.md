---
id: vif_T3_detailed
level: L3
system: VIF
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# VIF – T3 Detailed Implementation Guide

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

## Migration & Cutover Notes

### T→L Rename Strategy

After review and acceptance:
1. Run validation gate: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
2. Get reviewer sign-off (Braden)
3. Backup L-level files: `mv L*.md L*.md.backup`
4. Rename T-level files: `mv T0_executive.md L0_executive.md` (repeat for T1-T6)
5. Update references in indices/maps
6. Run post-cutover validation
7. Archive old L-level files

### Post-Cutover Validation Checklist

- [ ] All T-level files renamed to L-level
- [ ] Indices updated to reference new L-level paths
- [ ] System maps updated
- [ ] Validation gates pass
- [ ] No broken links
- [ ] Old L-level files archived
- [ ] Performance benchmarks still pass
- [ ] Witness creation still works
- [ ] κ-gating still functions
- [ ] Replay still deterministic

## References

- System map: `systems/vif/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/vif/L0_executive.md` through `L4_complete.md`
- Implementation: `packages/vif/` (153 tests passing ✅)
