---
id: "vif_T2_architecture"
system: "vif"
component: null
level: "T2"
type: "architecture"
title: "VIF Architecture"
description: "2,000-word architecture document for Verifiable Intelligence Framework"
audience: "developers, architects, implementation planning"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-10-30T00:00:00Z"
updated: "2025-11-02T15:50:00Z"
author: "aether"
status: "complete"
tags: ["vif", "core", "verification", "confidence", "t0-t6", "transitional"]
dependencies: ["vif_T1_overview"]
related_docs: ["vif_T3_detailed", "system.map.lucid.json5", "usage.envelope.md"]
version: "v2.2.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# VIF – T2 Architecture (≈2000 words)

## 🔄 **SDF-CVF QUARTET PARITY ENFORCEMENT**

### **Quartet Elements:**

**Code:** VIF implementation files (`packages/vif/`), witness generator, κ-gating module, confidence calibrator  
**Docs:** T0-T6 documentation (L0_executive.md, L1_overview.md, L2_architecture.md, L3_detailed.md, L4_complete.md), usage.envelope.md  
**Tests:** VIF test suite (`packages/vif/tests/`), integration tests, confidence calibration tests  
**Traces:** VIF witnesses (stored with atoms), SEG provenance (witness chains), timeline entries, decision logs

**Parity Requirement:** P ≥ 0.90 for all changes  
**Cross-Tagging:** All quartet elements must be tagged with change ID (vif-change-YYYYMMDD-HHMMSS) and semantically aligned

### **Quartet Parity Formula:**

```
P = (C_code×docs + C_code×tests + C_code×traces +
     C_docs×tests + C_docs×traces + C_tests×traces) / 6

Where:
- C_code×docs = semantic similarity between code and docs
- C_code×tests = semantic similarity between code and tests
- C_code×traces = semantic similarity between code and traces
- C_docs×tests = semantic similarity between docs and tests
- C_docs×traces = semantic similarity between docs and traces
- C_tests×traces = semantic similarity between tests and traces

Target: P ≥ 0.90 for all changes
```

### **Cross-Tagging Protocol:**

**Change ID Format:** `vif-change-YYYYMMDD-HHMMSS` (e.g., `vif-change-20251102-155030`)

**Tagging Requirements:**
- **Code:** Change ID in comments/metadata within modified code sections
- **Docs:** Change ID in frontmatter `tags` array and/or inline comments
- **Tests:** Change ID in test function docstrings/comments
- **Traces:** Change ID in VIF witness metadata, SEG provenance links, timeline entry metadata, decision log filename/content

**Workflow:**
1. Generate Change ID at start of VIF modification
2. Modify code (VIF implementation) → Tag with Change ID
3. Update docs (T-level docs) → Tag with Change ID
4. Update/add tests (VIF test suite) → Tag with Change ID
5. Create traces (VIF witnesses, SEG, timeline, decision log) → Tag with Change ID
6. Validate quartet parity (P ≥ 0.90) before merge

### **Gate Enforcement:**

**Pre-commit Gate:** Check quartet completeness and parity before commit  
**CI Gate:** Validate quartet parity in pipeline  
**Deployment Gate:** Verify quartet parity before deployment  
**Quarantine:** Changes with P < 0.90 are quarantined until parity achieved

---

## 🎯 **LUCID DEVELOPMENT PROTOCOL INTEGRATION**

### **Stage 0: Intent Capture**

**Intent Statement:**
We are updating VIF documentation to current standards (T0-T6, Perfect Metadata, SDF-CVF quartet parity, System Maps, Usage Envelopes, LDP Stage 0-1) so that VIF documentation serves as a complete template for other AIM-OS systems and ensures perfect alignment across Code, Docs, Tests, and Traces.

**Value Targets:**
- **Must Get Better:** Documentation structure, standards compliance, quartet parity clarity, onboarding experience
- **Must Not Get Worse:** Existing functionality, backward compatibility, documentation accuracy, performance

**Scope Class:** Extension - Adding T0-T6 documentation structure, quartet parity requirements, LDP integration, and system mapping to existing VIF documentation

**Why This Matters:**
This update preserves the "ghost of intent" - why VIF exists (make AI operations verifiable and trustworthy through provenance and confidence tracking) - while elevating documentation to full AIM-OS standards compliance. The intent follows the work forever, ensuring VIF never drifts from its core purpose.

---

### **Stage 1: System Index & Ontology**

**System Classification:**
- **Layer:** 2 (Verification Layer - depends on CMC and HHNI)
- **Security Level:** Critical (verification integrity must be protected)
- **Performance Sensitivity:** High (verification latency affects all systems)
- **Ownership:** Core (AIM-OS core system)
- **Side Effects:** 
  - Provides verification for all AIM-OS systems
  - Enables confidence tracking and κ-gating
  - Supports deterministic replay
  - Affects trust and reliability for all systems

**System Relationships:**
- **Depends On:** CMC (witness storage), HHNI (retrieval context), LLM providers (model execution)
- **Feeds Data To:** All AIM-OS systems (APOE, SEG, SDF-CVF, CAS, TCS, etc.)
- **Integrates With:** CMC (witness storage), HHNI (retrieval witnessing + RS-Lift), APOE (execution gates), SEG (provenance chains + evidence weighting), SDF-CVF (quartet parity witnesses + trace conversion), TCS (timeline tracking), CAS (cognitive context + confidence enhancement)

**System Context:**
VIF operates at the verification layer, providing provenance and confidence tracking for all AIM-OS systems. It transforms black-box AI into transparent, auditable, verifiable intelligence through complete witness envelopes, κ-gating, and deterministic replay.

---

## 📋 NL Tag Coverage

This system has comprehensive NL tag coverage enabling semantic search, cross-system tracing, and quintet parity validation:

**Tag Metrics:**
- **Total tags:** 408 NL tags across 10 VIF files
- **Primary tags (NL_TAG):** 172 tags
- **Integration tags (NL_TAG_CONNECT):** 13 tags
- **Design decisions (NL_TAG_INTENT):** 45 tags
- **Validations (NL_TAG_SPEC):** 7 tags
- **Coverage:** 95% public API, 78% internal functions
- **Quintet parity:** P = 0.92 (excellent - after manual enhancement)

**Key Tag Categories:**
- **VIF-WITNESS:** Witness creation, management, serialization (38 tags)
  - Core witness envelope operations
  - Provenance tracking and lineage
  - CMC integration for storage
  
- **VIF-MODEL:** Data models, enums, schemas (38 tags)
  - Witness dataclass definitions
  - Confidence band enums
  - Task criticality classifications
  
- **VIF-CONF:** Confidence tracking, scoring, bands (29 tags)
  - Confidence extraction from LLM outputs
  - Band assignment (A/B/C)
  - Calibration scoring
  
- **VIF-CAL:** Calibration, ECE tracking, adaptation (22 tags)
  - Expected Calibration Error calculation
  - Calibration tracking over time
  - Adaptive threshold adjustment
  
- **VIF-DESIGN:** Architecture decisions and rationale (20 tags)
  - Core design principles
  - Trade-off documentation
  - ADR references
  
- **VIF-REPLAY:** Deterministic replay operations (17 tags)
  - Witness-based replay
  - Context restoration
  - Output verification
  
- **VIF-GATE:** κ-gate operations, behavioral abstention (10 tags)
  - Threshold evaluation
  - Abstention decisions
  - HITL escalation

**Integration Points (CONNECT tags):**
- **VIF↔CMC:** Witness storage, bitemporal tracking (6 tags)
- **VIF↔HHNI:** Retrieval witnessing, context capture, RS-Lift tracking (4 tags)
- **VIF↔APOE:** Execution gating, confidence routing (4 tags)
- **VIF↔SEG:** Provenance chains, witness lineage, evidence weighting (5 tags)
- **VIF↔SDF-CVF:** Quartet parity witnesses, quality gates, trace conversion (6 tags)
- **VIF↔TCS:** Timeline integration, witness tracking, κ-gate events (6 tags)
- **VIF↔CAS:** Cognitive context, confidence enhancement, activation state (5 tags)

**Design Intent (INTENT tags):**
- Enable deterministic replay for debugging (VIF-DESIGN-003)
- Prevent hallucinations via κ-gating (VIF-DESIGN-005)
- Track calibration quality over time (VIF-DESIGN-009)
- Support cross-model witness verification (VIF-DESIGN-012)

**Validation Rules (SPEC tags):**
- Witness schema validation (VIF-SPEC-001)
- Confidence band constraints (VIF-SPEC-002)
- Replay output verification (VIF-SPEC-003)

All VIF functions are semantically tagged for cross-system tracing, design intent preservation, and quintet parity enforcement. See [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md) for complete tag index.

---

## System Overview

VIF (Verifiable Intelligence Framework) makes every AI operation fully traceable and trustworthy through complete provenance envelopes, uncertainty quantification, and deterministic replay. The core innovation: instead of black-box AI where you can't verify how conclusions were reached, VIF captures EVERYTHING—model version, exact prompts, context used, tools invoked, confidence levels, and enables bit-identical reproduction of outputs.

VIF transforms black-box AI into transparent, auditable, verifiable intelligence through:
1. **Complete Provenance:** Every operation has a witness envelope with full traceability
2. **Uncertainty Quantification:** κ-gating prevents hallucinations, ECE tracks calibration
3. **Deterministic Replay:** Bit-identical reproduction enables debugging and auditing

## Subsystem Architecture

VIF is organized into 4 subsystems in a 3-layer hierarchy:

**Layer 2 Subsystems:**

1. **Witness Subsystem** (`packages/vif/witness.py`)
   - Purpose: Cryptographic witness envelopes for complete provenance capture
   - Integration: All 7 systems (CMC, HHNI, APOE, SEG, CAS, SDF-CVF, TCS)
   - Status: Production
   - Components: None (leaf node)

2. **κ-Gating Subsystem** (`packages/vif/kappa_gate.py`)
   - Purpose: Behavioral abstention enforcement (prevents hallucinations)
   - Integration: APOE (step gating), CMC (gated storage), SEG (contradiction resolution), CAS (category recognition), SDF-CVF (quality gates)
   - Status: Production
   - Components: None (leaf node)

3. **Replay Subsystem** (`packages/vif/replay.py`)
   - Purpose: Deterministic replay of AI operations for verification
   - Integration: CMC (snapshot restoration), HHNI (context retrieval), TCS (timeline synchronization)
   - Status: Production
   - Components: None (leaf node)

4. **Confidence Bands Subsystem** (`packages/vif/confidence_bands.py`, `packages/vif/calibration.py`)
   - Purpose: Confidence calibration and band management (A/B/C/D bands)
   - Integration: CMC (band storage), CAS (cognitive analysis)
   - Status: Production
   - Components: ECE (Layer 3)

**Layer 3 Components:**

- **ECE (Expected Calibration Error)** (`packages/vif/calibration.py`)
  - Purpose: Calculates Expected Calibration Error for confidence calibration
  - Parent Subsystem: confidence_bands
  - Status: Production

See `system.map.lucid.json5` for complete subsystem hierarchy and integration topology.

## Components

### 1. Witness Generator
**Purpose:** Create complete provenance envelopes for AI operations

**Tags:** `VIF-WITNESS-001` (primary), `VIF-DESIGN-003` (intent), `VIF-CMC-001` (integration)  
**Files:** `packages/vif/witness.py`, `packages/vif/witness_TAGGED.py`  
**Tests:** `packages/vif/tests/test_witness.py`

**Responsibilities:**
- Capture model identity (ID, weights hash, provider)
- Capture context (CMC snapshot, retrieved atoms)
- Capture prompts (exact text, template, hash)
- Capture tools (invoked tools, parameters, results)
- Calculate uncertainty (confidence, entropy, ECE)
- Generate replay seed for deterministic reproduction
- Store witness in CMC as atom

**Key Operations:**
- `create_witness()` - **Tag:** `VIF-WITNESS-001` | Generate complete witness envelope
- `capture_context()` - **Tag:** `VIF-WITNESS-004` | Create CMC snapshot of input context
- `hash_prompt()` - **Tag:** `VIF-WITNESS-007` | Compute SHA-256 of exact prompt
- `calculate_confidence()` - **Tag:** `VIF-CONF-001` | Extract confidence from model output
- `assign_confidence_band()` - **Tag:** `VIF-CONF-003` | Classify as A/B/C based on confidence
- `generate_replay_seed()` - **Tag:** `VIF-REPLAY-001` | Create deterministic seed for reproduction

**Integration Tags:**
- `VIF-CMC-001`: Store witness as CMC atom with bitemporal tracking
- `VIF-HHNI-001`: Capture retrieval context from HHNI queries

### 2. κ-Gating Module
**Purpose:** Enforce behavioral abstention when confidence is insufficient

**Tags:** `VIF-GATE-001` (primary), `VIF-DESIGN-005` (intent), `VIF-APOE-001` (integration)  
**Files:** `packages/vif/kappa_gate.py`, `packages/vif/kappa_gate_TAGGED.py`  
**Tests:** `packages/vif/tests/test_kappa_gate.py`  
**ADR:** ADR-KAPPA-GATES

**Responsibilities:**
- Determine κ threshold based on task criticality
- Evaluate confidence against threshold
- Decide: PASS (proceed) or ABSTAIN (escalate)
- Provide escalation paths (HITL, retry, alternative)
- Log abstention events for analysis

**Key Operations:**
- `kappa_gate()` - **Tag:** `VIF-GATE-001` | Evaluate confidence against threshold
- `determine_kappa()` - **Tag:** `VIF-GATE-002` | Get threshold for task criticality
- `should_abstain()` - **Tag:** `VIF-GATE-003` | Check if confidence < threshold
- `escalate()` - **Tag:** `VIF-GATE-005` | Route to human-in-the-loop or alternative path
- `get_abstention_reason()` - **Tag:** `VIF-GATE-006` | Explain why abstained

**Integration Tags:**
- `VIF-APOE-001`: Gate APOE execution based on confidence
- `VIF-HITL-001`: Escalate to human-in-the-loop when abstaining

**Design Intent:**
- **VIF-DESIGN-005:** Safety-critical applications require confidence-based abstention
- **VIF-DESIGN-012:** Support task-criticality-based thresholds (CRITICAL: 0.95, IMPORTANT: 0.85, ROUTINE: 0.70, LOW_STAKES: 0.60)

### 3. Confidence Calibrator
**Purpose:** Track and measure calibration quality (ECE)

**Tags:** `VIF-CAL-001` (primary), `VIF-DESIGN-009` (intent), `VIF-SPEC-002` (validation)  
**Files:** `packages/vif/calibration.py`, `packages/vif/calibration_TAGGED.py`  
**Tests:** `packages/vif/tests/test_calibration.py`

**Responsibilities:**
- Record predictions with confidence scores
- Track outcomes (correctness verification)
- Calculate Expected Calibration Error (ECE)
- Monitor calibration degradation over time

**Key Operations:**
- `track_prediction()` - **Tag:** `VIF-CAL-001` | Record prediction with confidence
- `record_outcome()` - **Tag:** `VIF-CAL-002` | Update with actual outcome
- `calculate_ece()` - **Tag:** `VIF-CAL-003` | Compute Expected Calibration Error
- `get_calibration_curve()` - **Tag:** `VIF-CAL-005` | Generate calibration visualization

**Design Intent:**
- **VIF-DESIGN-009:** Track calibration quality to detect model degradation
- **VIF-DESIGN-010:** Enable adaptive threshold adjustment based on ECE
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
- Synchronize replay checkpoints with TCS timeline tracker for chronological audits

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
- VIF witnesses converted to trace text for parity calculation
- NL tags extracted from witnesses for quintet parity

**TCS (Timeline Context System):** (Phase 4 Integration)
- VIF creates timeline entries for witness creation events
- κ-gate events tracked in timeline for audit trail
- Timeline queries enable witness history tracking
- Snapshot-based provenance queries supported
- Confidence range queries for timeline analysis
- Bidirectional integration enables temporal provenance tracking

**CAS (Cognitive Analysis System):** (Phase 4 Integration)
- CAS cognitive context added to VIF witnesses
- Activation state, task categorization, cognitive load captured
- Confidence enhanced based on cognitive state
- Attention narrowing and failure modes detected
- Confidence reduced for high cognitive load or detected issues
- Enables "how AI thought during operation" provenance

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


---

## 🔗 RELATED SYSTEMS

### **Systems We Depend On**

#### **APOE**
**Relationship:** bidirectional
**Integration Point:** apoeIntegration
**Data Exchanged:** execution_validation, confidence_checks, provenance_traces (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/apoe/T0_executive.md`

#### **CMC**
**Relationship:** bidirectional
**Integration Point:** cmcIntegration
**Data Exchanged:** witness_storage, confidence_scores, verification_requests (+ 1 more)
**Security Level:** critical
**Docs:** `knowledge_architecture/systems/cmc/T0_executive.md`

#### **HHNI**
**Relationship:** bidirectional
**Integration Point:** hhniIntegration
**Data Exchanged:** retrieval_operations, rs_lift_metrics, witness_data (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/hhni/T0_executive.md`

#### **SDFCVF**
**Relationship:** bidirectional
**Integration Point:** sdfcvfIntegration
**Data Exchanged:** schema_validation, parity_checks, evolution_artifacts (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/sdfcvf/T0_executive.md`

#### **SEG**
**Relationship:** bidirectional
**Integration Point:** segIntegration
**Data Exchanged:** evidence_validation, contradiction_detection, proof_verification (+ 1 more)
**Security Level:** high
**Docs:** `knowledge_architecture/systems/seg/T0_executive.md`


### **Systems That Depend On Us**

**Other Systems:** aether_memory_system, ai_collaboration_system, auto_recovery_system, autonomous_research_dream, branch_reasoning_system, capability_awareness, ccs, co_agency_trust_layer, confidence_gated_controls, consciousness_analyzer, consciousness_creativity_engine, consciousness_learning_engine, context_fidelity_inspector, context_frames_system, cross_model_consciousness, disconnect_detection_system, dual_prompt_architecture, dynamic_cursor_rules_system, dynamic_onboarding, global_user_rules, intent_classification_system, knowledge_bootstrap_system, memory_pyramid_system, mutation_modes_system, scor

**Layer 1:** cmc, seg

**Layer 2:** hhni, sdfcvf

**Layer 3:** apoe

**Layer 4:** cognitive_analysis, intuitive_intelligence_system, timeline_context_system

**Layer 5 (Infrastructure):** consciousness_enhancement, daemon_rag_system, health_monitoring_system, icip_data_storage_layer, llm_client_integration, lucid_mcp_integration, mcp_integration, mcp_tools, self_improvement_protocol, spec_coverage_index, system_integration_protocols

**Layer 6 (Application):** advanced_monaco_editor, agent_system, aimos_mobile_app, icip_code_property_graph, icip_data_ingestion_layer, icip_gnn_service, icip_graph_construction_service, icip_llm_inference_service, icip_metric_calculation_service, icip_parser_service, icip_platform, icip_predictive_analytics_service, icip_presentation_api_layer, icip_search_service, icip_streaming_processing_layer, lucid_core_console

**Total Dependent Systems:** 60

### **External Systems**

**External Dependencies:** audit

**Integration Details:** See system map (`system.map.lucid.json5`) for complete integration topology.
