---
id: vif_T2_architecture
level: L2
system: VIF
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# VIF – T2 Architecture (≈2000 words)

## System Overview

VIF (Verifiable Intelligence Framework) makes every AI operation fully traceable and trustworthy through complete provenance envelopes, uncertainty quantification, and deterministic replay. The core innovation: instead of black-box AI where you can't verify how conclusions were reached, VIF captures EVERYTHING—model version, exact prompts, context used, tools invoked, confidence levels, and enables bit-identical reproduction of outputs.

VIF transforms black-box AI into transparent, auditable, verifiable intelligence through:
1. **Complete Provenance:** Every operation has a witness envelope with full traceability
2. **Uncertainty Quantification:** κ-gating prevents hallucinations, ECE tracks calibration
3. **Deterministic Replay:** Bit-identical reproduction enables debugging and auditing

## Components

### 1. Witness Generator
**Purpose:** Create complete provenance envelopes for AI operations

**Responsibilities:**
- Capture model identity (ID, weights hash, provider)
- Capture context (CMC snapshot, retrieved atoms)
- Capture prompts (exact text, template, hash)
- Capture tools (invoked tools, parameters, results)
- Calculate uncertainty (confidence, entropy, ECE)
- Generate replay seed for deterministic reproduction
- Store witness in CMC as atom

**Key Operations:**
- `create_witness()` - Generate complete witness envelope
- `capture_context()` - Create CMC snapshot of input context
- `hash_prompt()` - Compute SHA-256 of exact prompt
- `calculate_confidence()` - Extract confidence from model output
- `assign_confidence_band()` - Classify as A/B/C based on confidence
- `generate_replay_seed()` - Create deterministic seed for reproduction

### 2. κ-Gating Module
**Purpose:** Enforce behavioral abstention when confidence is insufficient

**Responsibilities:**
- Determine κ threshold based on task criticality
- Evaluate confidence against threshold
- Decide: PASS (proceed) or ABSTAIN (escalate)
- Provide escalation paths (HITL, retry, alternative)
- Log abstention events for analysis

**Key Operations:**
- `kappa_gate()` - Evaluate confidence against threshold
- `determine_kappa()` - Get threshold for task criticality
- `should_abstain()` - Check if confidence < threshold
- `escalate()` - Route to human-in-the-loop or alternative path
- `get_abstention_reason()` - Explain why abstained

### 3. Confidence Calibrator
**Purpose:** Track and measure calibration quality (ECE)

**Responsibilities:**
- Record predictions with confidence scores
- Track outcomes (correctness verification)
- Calculate Expected Calibration Error (ECE)
- Monitor calibration degradation over time
- Alert when ECE exceeds thresholds
- Update calibration models

**Key Operations:**
- `record_prediction()` - Store prediction with confidence
- `verify_prediction()` - Mark prediction as correct/incorrect
- `calculate_ece()` - Compute Expected Calibration Error
- `calibration_status()` - Assess calibration quality
- `update_calibration_model()` - Improve calibration over time
- `alert_degradation()` - Notify when ECE > 0.10

### 4. Provenance Store
**Purpose:** Persist and query witness envelopes

**Responsibilities:**
- Store witnesses as CMC atoms (immutable)
- Link witnesses to operations (parent-child chains)
- Query witnesses by model, confidence, time range
- Export witnesses for auditing
- Maintain witness index for fast lookup

**Key Operations:**
- `store_witness()` - Save witness to CMC
- `get_witness()` - Retrieve witness by ID
- `query_witnesses()` - Search by filters (model, confidence, time)
- `get_witness_chain()` - Trace operation lineage
- `export_witnesses()` - Generate audit report

### 5. Replay Engine
**Purpose:** Enable deterministic reproduction of outputs

**Responsibilities:**
- Store replay seed with witness
- Reconstruct exact context from snapshot
- Reconstruct exact prompt from hash
- Execute model with same seed and parameters
- Verify bit-identical output reproduction
- Enable debugging and regression testing

**Key Operations:**
- `store_replay_context()` - Save seed, context, prompt
- `replay_operation()` - Reproduce exact output
- `verify_replay()` - Check bit-identical reproduction
- `debug_replay()` - Step-by-step replay for debugging

### 6. API/Integration Layer
**Purpose:** Provide VIF services to other systems

**Responsibilities:**
- Wrap model operations with VIF
- Provide hooks for APOE orchestration
- Integrate with CMC for storage
- Integrate with SEG for provenance graph
- Emit metrics to monitoring systems

**Key Operations:**
- `wrap_model()` - Wrap model execution with VIF
- `provide_gate_hooks()` - κ-gating hooks for APOE
- `store_in_cmc()` - CMC integration
- `link_to_seg()` - SEG provenance graph integration
- `emit_metrics()` - Send metrics to monitoring

## Data Models

### Witness Envelope Schema

```python
@dataclass
class VIF:
    """Verifiable Intelligence Framework witness envelope"""
    
    # === IDENTITY ===
    id: str                          # "vif_{uuid}"
    version: str                     # "1.0"
    
    # === WHAT MODEL ===
    model_id: str                    # "gpt-4-turbo-2025-01-15"
    model_provider: str              # "openai", "anthropic", "local"
    weights_hash: Optional[str]      # SHA-256 of weights file
    
    # === WHAT DATA ===
    context_snapshot_id: str         # CMC snapshot reference
    prompt_template: str             # Template used
    prompt_hash: str                 # SHA-256 of exact prompt
    prompt_tokens: int               # Token count
    retrieved_atom_ids: List[str]    # From HHNI retrieval
    
    # === WHAT TOOLS ===
    tool_ids: List[str]              # ["hhni.retrieve", "cmc.store"]
    tool_parameters: Dict[str, Any]  # Exact params for each tool
    tool_results_hash: str           # Hash of tool outputs
    
    # === UNCERTAINTY ===
    confidence_score: float          # 0.0-1.0 (model's reported confidence)
    confidence_band: str             # "A" (0.95-1.0) | "B" (0.80-0.94) | "C" (<0.80)
    ece_score: Optional[float]       # Expected Calibration Error
    entropy: float                   # Output distribution entropy
    top_k_probs: List[Tuple[str, float]]  # Top-K token probabilities
    
    # === REPLAY ===
    replay_seed: Optional[int]       # For deterministic reproduction
    temperature: float               # Generation parameter
    top_p: Optional[float]           # Nucleus sampling parameter
    other_params: Dict[str, Any]     # Other generation params
    
    # === META ===
    writer: str                      # "system" | "user" | "agent_planner"
    created_at: datetime             # When witness created
    execution_time_ms: float         # How long operation took
    parent_vif_id: Optional[str]     # Chain of witnesses
    
    # === VALIDATION ===
    signature: Optional[str]         # Cryptographic signature (future)
```

### κ-Gate Result Schema

```python
@dataclass
class KappaGateResult:
    """Result of κ-gate check"""
    status: str                      # "PASS" | "ABSTAIN"
    confidence: float                # Reported confidence
    threshold: float                 # κ threshold
    task_criticality: str            # Task type
    reason: Optional[str]            # Why abstained (if applicable)
    escalation: Optional[str]        # Escalation path (HITL, retry, etc.)
```

### Calibration Tracker Schema

```python
@dataclass
class CalibrationTracker:
    """Track confidence vs accuracy over time"""
    predictions: List[Prediction]    # All predictions
    
    @dataclass
    class Prediction:
        id: str
        confidence: float
        output: Any
        ground_truth: Optional[Any] = None
        correct: Optional[bool] = None
        timestamp: datetime
```

## Key Flows

### Witness Creation Flow

```
AI Operation Request
    ↓
┌──────────────────┐
│ Capture Context  │ Create CMC snapshot
└──────────────────┘
    ↓
┌──────────────────┐
│ Capture Prompt   │ Hash exact prompt text
└──────────────────┘
    ↓
┌──────────────────┐
│ Generate Seed    │ Create deterministic seed
└──────────────────┘
    ↓
┌──────────────────┐
│ Execute Model    │ Run with seed, track tools
└──────────────────┘
    ↓
┌──────────────────┐
│ Calculate        │ Extract confidence, entropy
│ Uncertainty      │
└──────────────────┘
    ↓
┌──────────────────┐
│ Assign Band      │ Classify A/B/C
└──────────────────┘
    ↓
┌──────────────────┐
│ Create Witness   │ Generate complete envelope
└──────────────────┘
    ↓
┌──────────────────┐
│ Store in CMC     │ Save as atom
└──────────────────┘
    ↓
┌──────────────────┐
│ Link to SEG      │ Add to provenance graph
└──────────────────┘
    ↓
Witness Complete
```

### κ-Gating Flow

```
Output + Confidence
    ↓
┌──────────────────┐
│ Determine κ      │ Based on task criticality
└──────────────────┘
    ↓
┌──────────────────┐
│ Check Threshold  │ confidence >= κ?
└──────────────────┘
    ↓
    ├─ YES → PASS → Create Witness → Store
    │
    └─ NO → ABSTAIN → Escalate to HITL → Log
```

### Calibration Loop

```
Prediction Recorded
    ↓
┌──────────────────┐
│ Track Outcome    │ Verify correctness
└──────────────────┘
    ↓
┌──────────────────┐
│ Calculate ECE    │ Expected Calibration Error
└──────────────────┘
    ↓
┌──────────────────┐
│ Assess Quality   │ Well-calibrated? (ECE ≤ 0.05)
└──────────────────┘
    ↓
┌──────────────────┐
│ Alert if Poor    │ ECE > 0.10 → Alert
└──────────────────┘
    ↓
┌──────────────────┐
│ Update Model     │ Improve calibration
└──────────────────┘
```

## Integrations

**CMC (Context Memory Core):**
- VIF witnesses stored as atoms in CMC (immutable)
- VIF uses CMC snapshots for context capture
- Every atom includes VIF witness envelope
- Witness queries use CMC retrieval

**APOE (AI-Powered Orchestration Engine):**
- VIF provides κ-gating hooks for APOE execution
- Every step emits VIF witness
- Gates prevent low-confidence operations from proceeding
- APOE uses VIF confidence for routing decisions

**HHNI (Hierarchical Hypergraph Neural Index):**
- Retrieval context influences confidence scores
- VIF tracks which atoms were retrieved
- HHNI retrieval operations witnessed
- Confidence modulated by retrieval quality

**SEG (Shared Evidence Graph):**
- Witnesses become provenance nodes in SEG
- VIF enables contradiction detection via confidence tracking
- Synthesis operations use VIF witnesses for evidence weighting
- Provenance chains tracked in graph

**SDF-CVF (Atomic Evolution Framework):**
- VIF witnesses required for quartet parity (Code/Docs/Tests/Traces)
- Quality gates use VIF confidence to enforce standards
- Trace emissions include VIF witnesses
- Quality tracking relies on VIF provenance

## κ-Gating Thresholds

**Task-Specific Thresholds:**
- **Critical (κ = 0.95):** Medical, legal, safety-critical decisions
- **Important (κ = 0.85):** Code generation, data analysis
- **Routine (κ = 0.70):** Summarization, formatting
- **Low Stakes (κ = 0.60):** Suggestions, recommendations

**Behavioral Abstention:**
- If confidence < κ: ABSTAIN (escalate to HITL, don't guess)
- If confidence >= κ: PROCEED (use output)
- Prevents hallucinations by forcing honesty about uncertainty

## ECE Calibration Formula

**Expected Calibration Error:**
```
ECE = (1/N) × Σ |confidence_i - accuracy_i|

Where:
- N = number of predictions
- confidence_i = AI's reported confidence (0-1)
- accuracy_i = actual correctness (1 if correct, 0 if wrong)

Target: ECE ≤ 0.05 (well-calibrated)
Warning: ECE > 0.10 (poorly calibrated)
```

**Calibration Status:**
- **Well-Calibrated:** ECE ≤ 0.05 ✅
- **Acceptable:** 0.05 < ECE ≤ 0.10 ⚠️
- **Poorly Calibrated:** ECE > 0.10 ❌

## Confidence Bands

**Band A (High Confidence):** 0.95-1.00
- Proceed with confidence
- No escalation needed
- Use output directly

**Band B (Medium Confidence):** 0.80-0.94
- Proceed with caution
- Consider review
- Monitor outcomes

**Band C (Low Confidence):** <0.80
- Review carefully
- Consider abstention
- Escalate if critical

## Non‑Functional Requirements

### Performance Targets

**SLOs:**
- Witness creation: < 10ms overhead
- κ-gate evaluation: < 1ms latency
- ECE calculation: < 50ms for 1000 predictions
- Replay execution: Deterministic (bit-identical)

**Current Performance:**
- Witness creation: ~5ms overhead ✅
- κ-gate: < 1ms ✅
- ECE: Computed efficiently ✅

### Storage & Scalability

- **Witness Size:** ~2KB per witness (compressed)
- **Storage:** CMC atoms (immutable, content-addressed)
- **Query Performance:** Indexed by model, confidence, time

### Determinism & Reproducibility

- **Deterministic:** Same seed + context + prompt → same output
- **Reproducible:** Bit-identical replay enabled
- **Auditable:** Complete provenance trail

## Diagrams

**Component Diagram:**
```
┌────────────────────────────────────────┐
│         AI Operation Request           │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│       Witness Generator                │
├────────────────────────────────────────┤
│  • Capture Context (CMC snapshot)    │
│  • Capture Prompt (hash)              │
│  • Generate Seed                      │
│  • Calculate Uncertainty              │
│  • Create Witness Envelope            │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│           κ-Gating Module              │
├────────────────────────────────────────┤
│  • Determine Threshold                │
│  • Evaluate Confidence                │
│  • Decide: PASS/ABSTAIN               │
│  • Escalate if needed                 │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│      Confidence Calibrator            │
├────────────────────────────────────────┤
│  • Record Predictions                 │
│  • Track Outcomes                     │
│  • Calculate ECE                      │
│  • Monitor Degradation                │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│        Provenance Store                │
├────────────────────────────────────────┤
│  • Store in CMC                       │
│  • Link to SEG                        │
│  • Query Witnesses                    │
│  • Export for Audit                   │
└──────────────┬─────────────────────────┘
               │
┌──────────────▼─────────────────────────┐
│          Replay Engine                │
├────────────────────────────────────────┤
│  • Store Replay Context               │
│  • Reproduce Outputs                  │
│  • Verify Bit-Identical               │
│  • Enable Debugging                   │
└────────────────────────────────────────┘
```

**Sequence Diagram (Witness Creation):**
```
Operation → Witness Generator → κ-Gate → Calibrator → Store → SEG
```

## References

- System map: `systems/vif/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/vif/L0_executive.md` through `L4_complete.md`
- Implementation: `packages/vif/` (153 tests passing ✅)
