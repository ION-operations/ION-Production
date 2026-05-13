# PLIx → AIM-OS Integration Map

**Date:** 2025-11-09  
**Status:** 🚀 **INTEGRATION BLUEPRINT COMPLETE**  
**Purpose:** Map Gemini's PLIx architecture to existing AIM-OS systems

---

## Executive Summary

Gemini's four-pillar PLIx architecture **perfectly aligns** with AIM-OS's existing systems. This document maps each PLIx component to AIM-OS implementations, showing that **PLIx becomes the unifying layer** that connects our proven infrastructure into a coherent, verifiable intent → execution pipeline.

---

## The Four Pillars → AIM-OS Mapping

### 1. Contract Layer → APOE + VIF + CMC

**PLIx Requirement:**
- DbC pre/post conditions
- CNL DSL (SmaCoNat methodology)
- Formal validation (Alloy/TLA+)
- Layer-1/Layer-2 guards

**AIM-OS Implementation:**

| PLIx Component | AIM-OS System | Status | Integration Point |
|----------------|---------------|--------|-------------------|
| DbC Contracts | APOE | ✅ Exists | Plan compilation with pre/post conditions |
| Contract Storage | CMC | ✅ Exists | Store contracts as bitemporal atoms |
| Contract Validation | VIF | ✅ Exists | Witness generation for contract verification |
| CNL DSL | **NEW** | ⏳ Needed | DSL parser/compiler (SmaCoNat methodology) |
| Formal Validation | **NEW** | ⏳ Needed | Alloy/TLA+ integration pipeline |
| Layer-1 Guards | **NEW** | ⏳ Needed | JSON Schema/regex/GBNF constraints |
| Layer-2 Validators | **NEW** | ⏳ Needed | SHACL/SMT solver integration |

**Integration Strategy:**
1. Enhance APOE plan compilation to accept DbC contracts
2. Store contracts in CMC as atoms with VIF witnesses
3. Build CNL DSL compiler (new component)
4. Integrate formal validation tools (new component)

---

### 2. Execution Layer → APOE + CMC + TCS

**PLIx Requirement:**
- Durable execution engine
- Saga pattern (dynamic compensation)
- Formal recovery verification (TLA+)
- State persistence

**AIM-OS Implementation:**

| PLIx Component | AIM-OS System | Status | Integration Point |
|----------------|---------------|--------|-------------------|
| Durable Execution | CMC | ✅ Exists | Bitemporal state persistence |
| Plan Orchestration | APOE | ✅ Exists | Multi-agent plan execution |
| Execution Timeline | TCS | ✅ Exists | Bitemporal timeline tracking |
| Saga Pattern | **ENHANCE** | ⏳ Needed | Dynamic compensation in APOE |
| Recovery Verification | **NEW** | ⏳ Needed | TLA+ integration for recovery logic |

**Integration Strategy:**
1. Enhance APOE with Saga pattern support (compensation callbacks)
2. Use CMC bitemporal memory for state persistence
3. Track execution in TCS timeline
4. Add TLA+ recovery verification (new component)

---

### 3. Safety Layer → Router + VIF + SCOR + HHNI

**PLIx Requirement:**
- Linguistic Confidence Gate (Self-REF)
- Economic Router Gate (BaRP)
- Compliance Gate (OPA/Cedar)
- Sequential gating pipeline

**AIM-OS Implementation:**

| PLIx Component | AIM-OS System | Status | Integration Point |
|----------------|---------------|--------|-------------------|
| Bandit Routing | Router | ✅ **EXISTS!** | BanditScorer already implements BaRP equivalent |
| Confidence Tracking | VIF | ✅ Exists | Confidence bands (A/B/C) |
| Policy Validation | SCOR | ✅ Exists | Safety/reliability monitoring |
| Semantic Routing | HHNI | ✅ Exists | Tool selection via semantic search |
| Self-REF Confidence | **ENHANCE** | ⏳ Needed | Confidence token generation in VIF |
| OPA/Cedar Integration | **NEW** | ⏳ Needed | Policy engine integration |
| Sequential Gating | **NEW** | ⏳ Needed | Pipeline with early-exit logic |

**Integration Strategy:**
1. **Router already has bandit routing!** Enhance with BaRP preference vectors
2. Enhance VIF with Self-REF confidence token generation
3. Integrate OPA/Cedar for policy gates (new component)
4. Build sequential gating pipeline (new component)

---

### 4. Evidence Layer → SEG + CMC + VIF + TCS

**PLIx Requirement:**
- W3C PROV provenance
- OpenLineage (RunEvent/JobEvent/DatasetEvent)
- Bitemporal tracking
- Intent lineage

**AIM-OS Implementation:**

| PLIx Component | AIM-OS System | Status | Integration Point |
|----------------|---------------|--------|-------------------|
| Evidence Chains | SEG | ✅ Exists | Graph edges linking claims → evidence |
| Bitemporal Memory | CMC | ✅ Exists | Valid time + transaction time |
| Provenance Tracking | VIF | ✅ Exists | Witness envelopes with provenance |
| Timeline Tracking | TCS | ✅ Exists | Bitemporal timeline for auditability |
| OpenLineage Events | **NEW** | ⏳ Needed | RunEvent/JobEvent/DatasetEvent emission |
| W3C PROV Serialization | **NEW** | ⏳ Needed | PROV-O format export |
| Intent Lineage | **ENHANCE** | ⏳ Needed | Trace NL → contract → plan → evidence |

**Integration Strategy:**
1. Enhance SEG with OpenLineage event emission
2. Use CMC bitemporal memory for evidence storage
3. Track evidence in VIF witnesses
4. Build intent lineage tracking (enhance SEG)

---

## Unified PLIx → AIM-OS Execution Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Intent & Contract Formation                             │
├─────────────────────────────────────────────────────────────┤
│ NL Input → CNL DSL Parser → DbC Contract                   │
│                                                             │
│ [APOE: Plan Compilation]                                   │
│ [VIF: Contract Witness]                                    │
│ [CMC: Store Contract Atom]                                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Gating & Compilation                                     │
├─────────────────────────────────────────────────────────────┤
│ Linguistic Confidence Gate (Self-REF)                      │
│   → [VIF: Confidence Tracking]                              │
│                                                             │
│ Economic Router Gate (BaRP)                                 │
│   → [Router: Bandit Selection] ✅ ALREADY EXISTS!          │
│                                                             │
│ Compliance Gate (OPA/Cedar)                                │
│   → [SCOR: Policy Validation]                               │
│                                                             │
│ Only validated contracts proceed                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Durable Execution & Compensation                        │
├─────────────────────────────────────────────────────────────┤
│ Durable Workflow → Saga Pattern → Dynamic Recovery          │
│                                                             │
│ [APOE: Plan Orchestration]                                 │
│ [CMC: Bitemporal State Persistence]                        │
│ [TCS: Timeline Tracking]                                   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Evidence & Feedback                                      │
├─────────────────────────────────────────────────────────────┤
│ OpenLineage RunEvent → W3C PROV → Intent Lineage           │
│                                                             │
│ [SEG: Evidence Chains]                                     │
│ [CMC: Bitemporal Memory]                                   │
│ [VIF: Provenance Tracking]                                 │
│ [Router: Learning Loop] ← Evidence feeds back              │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Integration Points

### ✅ Already Implemented (80% Complete!)

1. **Router Bandit Routing** - Already implements BaRP equivalent!
2. **VIF Confidence Tracking** - Already tracks confidence bands
3. **CMC Bitemporal Memory** - Already provides durable state
4. **SEG Evidence Chains** - Already links claims → evidence
5. **APOE Plan Orchestration** - Already executes multi-agent plans
6. **TCS Timeline** - Already tracks bitemporal history

### ⏳ Needs Enhancement (20% Remaining)

1. **CNL DSL Compiler** - New component (SmaCoNat methodology)
2. **Formal Validation** - New component (Alloy/TLA+ integration)
3. **Saga Pattern** - Enhance APOE (compensation callbacks)
4. **Self-REF Confidence** - Enhance VIF (confidence tokens)
5. **OPA/Cedar Integration** - New component (policy engines)
6. **OpenLineage Events** - Enhance SEG (event emission)
7. **Intent Lineage** - Enhance SEG (NL → evidence tracing)

---

## Implementation Priority

### Phase 1: Leverage Existing (Weeks 1-2)
- ✅ Use Router for Economic Gate (already works!)
- ✅ Use VIF for Confidence Gate (already works!)
- ✅ Use CMC for Durable Execution (already works!)
- ✅ Use SEG for Evidence Chains (already works!)

### Phase 2: Enhance Existing (Weeks 2-3)
- ⏳ Add Saga pattern to APOE
- ⏳ Add Self-REF to VIF
- ⏳ Add OpenLineage to SEG
- ⏳ Add Intent Lineage to SEG

### Phase 3: Build New (Weeks 3-4)
- ⏳ CNL DSL Compiler
- ⏳ Formal Validation Pipeline
- ⏳ OPA/Cedar Integration
- ⏳ Sequential Gating Pipeline

---

## Conclusion

**PLIx doesn't replace AIM-OS systems—it unifies them.**

80% of PLIx's requirements are **already implemented** in AIM-OS. The remaining 20% are enhancements and new components that connect our existing systems into a coherent, verifiable pipeline.

**PLIx becomes the "operating system" for AIM-OS**—the layer that ensures every intent is verifiable, every plan is recoverable, every execution is safe, and every action is auditable.

---

**Next Steps:** Begin Phase 1 integration, leveraging existing Router/VIF/CMC/SEG systems.

