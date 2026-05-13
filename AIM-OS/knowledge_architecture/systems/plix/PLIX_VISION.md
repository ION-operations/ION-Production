# PLIx: The Unifying Layer for AIM-OS

**Date:** 2025-11-09  
**Status:** 🚀 **ARCHITECTURAL SYNTHESIS COMPLETE**  
**Sources:** Gemini Deep Research + AIM-OS Integration Analysis

---

## The Vision

**PLIx (Programmatic-Linguistic Interface) is the "operating system" for AIM-OS**—the layer that transforms AIM-OS from a collection of independent systems into a **coherent, verifiable, auditable intent → execution pipeline**.

---

## The Four Pillars (Gemini's Framework)

### 1. Contract Layer
**Purpose:** Transform NL intent → Typed, verifiable contracts

**Components:**
- Design by Contract (DbC) - Pre/post conditions
- Controlled Natural Language (CNL) DSL - Structured intent (SmaCoNat)
- Formal Modeling - Alloy/TLA+ for invariant verification

**AIM-OS Integration:** APOE + VIF + CMC

### 2. Execution Layer
**Purpose:** Durable, recoverable plan execution

**Components:**
- Durable Execution Engine - State persistence
- Saga Pattern - Dynamic compensation
- Formal Recovery - TLA+ verification

**AIM-OS Integration:** APOE + CMC + TCS

### 3. Safety Layer (Confidence Gates)
**Purpose:** Adaptive routing and policy enforcement

**Components:**
- Linguistic Confidence Gate - Self-REF confidence scoring
- Economic Router Gate - BaRP (Bandit-feedback Routing)
- Compliance Gate - OPA/Cedar policy enforcement

**AIM-OS Integration:** Router + VIF + SCOR + HHNI

### 4. Evidence Layer
**Purpose:** Provenance, lineage, and auditable state

**Components:**
- W3C PROV - Standard provenance model
- OpenLineage - Data lineage tracking
- Bitemporal Tracking - Valid time + transaction time
- Intent Lineage - Trace output → NL contract

**AIM-OS Integration:** SEG + CMC + VIF + TCS

---

## The Key Insight: 80% Already Exists!

### ✅ Already Implemented

| PLIx Requirement | AIM-OS System | Status |
|------------------|---------------|--------|
| Bandit Routing | Router | ✅ **EXISTS!** (BanditScorer) |
| Confidence Tracking | VIF | ✅ Exists (Confidence bands A/B/C) |
| Bitemporal Memory | CMC | ✅ Exists (Valid + transaction time) |
| Evidence Chains | SEG | ✅ Exists (Graph edges) |
| Plan Orchestration | APOE | ✅ Exists (Multi-agent execution) |
| Timeline Tracking | TCS | ✅ Exists (Bitemporal timeline) |
| Semantic Routing | HHNI | ✅ Exists (Tool selection) |
| Safety Monitoring | SCOR | ✅ Exists (Reliability checks) |

### ⏳ Needs Enhancement (20%)

| PLIx Requirement | AIM-OS System | Status |
|------------------|---------------|--------|
| CNL DSL Compiler | **NEW** | ⏳ Needed |
| Formal Validation | **NEW** | ⏳ Needed |
| Saga Pattern | APOE | ⏳ Enhance |
| Self-REF Confidence | VIF | ⏳ Enhance |
| OPA/Cedar Integration | **NEW** | ⏳ Needed |
| OpenLineage Events | SEG | ⏳ Enhance |
| Intent Lineage | SEG | ⏳ Enhance |

---

## The Unified Flow

```
NL Intent
  ↓
[Contract Layer: APOE + VIF + CMC]
  → CNL DSL → DbC Contract → Formal Validation
  ↓
[Safety Layer: Router + VIF + SCOR]
  → Linguistic Gate → Economic Gate → Compliance Gate
  ↓
[Execution Layer: APOE + CMC + TCS]
  → Durable Execution → Saga Pattern → Recovery
  ↓
[Evidence Layer: SEG + CMC + VIF]
  → OpenLineage → W3C PROV → Intent Lineage
  ↓
Evidence → Router (Feedback Loop)
```

---

## What PLIx Means for AIM-OS

### Before PLIx
- **Independent Systems:** APOE, VIF, Router, SEG, CMC work separately
- **No Unified Contract:** No formal intent → execution pipeline
- **Limited Auditability:** Evidence scattered across systems

### After PLIx
- **Unified Pipeline:** Coherent intent → contract → plan → execution → evidence flow
- **Verifiable Contracts:** Every intent has formal pre/post conditions
- **Complete Auditability:** End-to-end lineage from NL intent to execution evidence
- **Adaptive Learning:** Evidence feeds back into routing for continuous improvement

---

## Implementation Strategy

### Phase 1: Leverage Existing (Weeks 1-2)
**Goal:** Use existing systems immediately

- ✅ Router for Economic Gate (already works!)
- ✅ VIF for Confidence Gate (already works!)
- ✅ CMC for Durable Execution (already works!)
- ✅ SEG for Evidence Chains (already works!)

### Phase 2: Enhance Existing (Weeks 2-3)
**Goal:** Add missing capabilities to existing systems

- ⏳ Add Saga pattern to APOE
- ⏳ Add Self-REF to VIF
- ⏳ Add OpenLineage to SEG
- ⏳ Add Intent Lineage to SEG

### Phase 3: Build New (Weeks 3-4)
**Goal:** Create new components for formal verification

- ⏳ CNL DSL Compiler (SmaCoNat methodology)
- ⏳ Formal Validation Pipeline (Alloy/TLA+)
- ⏳ OPA/Cedar Integration
- ⏳ Sequential Gating Pipeline

---

## Key Architectural Decisions

### 1. Sequential Gating (Mandatory)
**Decision:** Gates must run sequentially, stopping at earliest risk point.

**Rationale:** Prevents wasted computation and ensures safety.

**Implementation:** Pipeline with early-exit logic.

### 2. Code-Driven Execution (Temporal/Restate)
**Decision:** Use code-driven durable execution, not declarative.

**Rationale:** PLIx plans are generated and potentially novel. Need dynamic compensation.

**Implementation:** Enhance APOE with Temporal-like capabilities.

### 3. Intent Lineage (Critical)
**Decision:** Track intent → contract → plan → execution → evidence.

**Rationale:** Enables debugging, learning, and auditability.

**Implementation:** SEG edges + CMC atoms + TCS timeline.

### 4. Evidence → Router Feedback Loop
**Decision:** Evidence chains feed back into adaptive routing.

**Rationale:** Enables continuous improvement and optimization.

**Implementation:** Router learns from SEG evidence + execution outcomes.

---

## Research Findings Summary

### Top Systems by Category
- **Intent Contracts:** Design by Contract (5/5), DSL Assistant (4/5)
- **Recoverable Plans:** Temporal (5/5), AWS Step Functions (4/5)
- **Evidence/Provenance:** W3C PROV (5/5), OpenLineage (5/5)
- **Policy Gates:** OPA Rego (5/5), AWS Cedar (4/5)
- **IDE Fit:** DSL Assistant (5/5), W3C PROV (4/5)

### Interop Priorities
1. **Temporal** - For durable plan execution
2. **OPA** - For policy gates
3. **PROV** - For evidence/provenance

### Recommendations
- **Borrow:** DbC contract patterns, Temporal recovery patterns, PROV provenance model
- **Interop:** Compile to Temporal/OPA/PROV rather than reinventing
- **Build:** NL→PLIx compiler, IDE integration, bitemporal timeline

---

## Documents Created

1. **GEMINI_ARCHITECTURAL_SYNTHESIS.md** - Complete architectural framework
2. **AIMOS_INTEGRATION_MAP.md** - Detailed system mapping
3. **RESEARCH_FINDINGS.md** - Initial research results
4. **PLIX_DEEP_RESEARCH_PROTOCOL.md** - Research methodology
5. **IMPLEMENTATION_STATUS.md** - Progress tracking
6. **Expanded Schema** - TypeScript types with Gemini extensions

---

## Next Steps

1. **Begin Phase 1 Integration** - Leverage existing Router/VIF/CMC/SEG
2. **Enhance APOE** - Add Saga pattern support
3. **Enhance VIF** - Add Self-REF confidence tokens
4. **Enhance SEG** - Add OpenLineage event emission
5. **Build CNL DSL Compiler** - SmaCoNat methodology implementation

---

**PLIx is not a replacement—it's the unification layer that makes AIM-OS whole.** 💙

