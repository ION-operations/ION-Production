# PLIx Integration: AIM-OS System Requirements Analysis

**Date:** 2025-11-09  
**Question:** Do all AIM-OS systems need to be altered for PLIx integration?  
**Answer:** **NO - Most systems work as-is. PLIx integrates via adapters.**

---

## 🎯 Summary: Minimal Changes Required

**Most AIM-OS systems are already compatible with PLIx.** PLIx integrates via **adapter layers** that translate PLIx concepts to existing AIM-OS APIs. Only **SEG** and **SIS** need enhancement.

---

## ✅ Systems That Work As-Is (No Changes Needed)

### **1. APOE (AI-Powered Orchestration Engine)** ✅

**Status:** 90% complete, 139 tests, production-ready

**Current Capabilities:**
- ✅ Accepts `ExecutionPlan` with DAG, Steps, Budgets, Gates
- ✅ Compiles ACL → ExecutionPlan
- ✅ Executes plans with dependency resolution
- ✅ Supports gates (quality, safety, policy, budget)
- ✅ Handles retries, backoff, circuit breakers
- ✅ Integrates with CMC for checkpoints

**PLIx Integration:**
- **PLIx → APOE Compiler** generates `ExecutionPlan` structures
- **No APOE changes needed** - it already accepts the structure PLIx produces
- **Adapter:** `packages/plix/src/compiler/apoe-generator.ts` (translates PLIx IR → APOE ExecutionPlan)

**Example:**
```typescript
// PLIx IR
const plixIR = {
  intent: "BookMeeting",
  tasks: [...],
  dependencies: [...],
  compensations: [...]
};

// PLIx → APOE Adapter (no APOE changes needed)
const apoePlan = plixToAPOE(plixIR);
// Returns ExecutionPlan that APOE already accepts
```

---

### **2. CMC (Context Memory Core)** ✅

**Status:** ~70% complete, foundation stable, production-ready for storage

**Current Capabilities:**
- ✅ Flexible atom schema with metadata dict
- ✅ Tags system (key-value pairs with weights)
- ✅ Modality support (text, code, event, tool)
- ✅ Bitemporal storage (valid_from, valid_to)
- ✅ Content references (inline or URI)
- ✅ Provenance (VIF witness integration)

**PLIx Integration:**
- **PLIx stores intent atoms** using existing CMC atom schema
- **No CMC changes needed** - metadata/tags are flexible enough
- **Adapter:** `packages/plix/src/integration/cmc-integration.ts` (creates atoms with PLIx-specific tags)

**Example:**
```typescript
// PLIx creates CMC atom (no CMC changes needed)
const intentAtom = {
  atom_id: "atom_...",
  modality: "event",
  content: { intent: "BookMeeting", ... },
  tags: [
    { key: "plix_intent", value: "BookMeeting", weight: 1.0 },
    { key: "plix_status", value: "pending", weight: 1.0 }
  ],
  metadata: {
    plix_contract: {...},
    plix_postconditions: [...]
  }
};
// CMC.store() accepts this as-is
```

---

### **3. VIF (Verifiable Intelligence Framework)** ✅

**Status:** 95% complete, 153 tests, production-ready

**Current Capabilities:**
- ✅ Confidence tracking (0.0-1.0)
- ✅ κ-gating (confidence threshold gates)
- ✅ Witness creation (cryptographic provenance)
- ✅ ECE (Expected Calibration Error) calculation
- ✅ Deterministic replay
- ✅ CMC integration (stores witnesses as atoms)

**PLIx Integration:**
- **PLIx uses VIF confidence gates** via existing κ-gating API
- **No VIF changes needed** - gates already support conditional routing
- **Adapter:** `packages/plix/src/guards/confidence-gate.ts` (wraps VIF κ-gate)

**Example:**
```typescript
// PLIx uses VIF gate (no VIF changes needed)
const confidence = await vif.getConfidence(operation);
if (confidence < 0.75) {
  // Route to SIS.research (PLIx-specific logic)
  routeToSIS(operation);
} else {
  // Proceed (VIF gate passes)
  proceed();
}
```

---

### **4. HHNI (Hierarchical Hypergraph Neural Index)** ✅

**Status:** 100% complete, production-ready

**Current Capabilities:**
- ✅ Semantic search (embeddings)
- ✅ Hierarchical indexing (6-level fractal)
- ✅ Physics simulation (DVNS)
- ✅ Retrieval with deduplication

**PLIx Integration:**
- **PLIx retrieves similar intents** via existing HHNI search
- **No HHNI changes needed** - it already indexes CMC atoms
- **Adapter:** `packages/plix/src/integration/hhni-integration.ts` (queries HHNI for intent patterns)

**Example:**
```typescript
// PLIx queries HHNI (no HHNI changes needed)
const similarIntents = await hhni.search({
  query: "BookMeeting",
  filters: { tags: ["plix_intent"] },
  limit: 10
});
// Returns similar past intents for learning
```

---

## ⚠️ Systems That Need Enhancement (Minor Changes)

### **5. SEG (Shared Evidence Graph)** ⚠️

**Status:** ~10% complete, early stage

**Current Capabilities:**
- ✅ Basic graph structure
- ✅ Evidence storage (atoms reference)
- ⚠️ Missing: Contradiction detection
- ⚠️ Missing: Intent vs outcome comparison

**PLIx Integration:**
- **PLIx needs:** Intent violation detection, postcondition failure detection
- **Enhancement needed:** Add contradiction detection logic
- **New component:** `packages/seg/src/contradiction_detector.ts`

**Required Changes:**
```typescript
// NEW: SEG contradiction detection
class ContradictionDetector {
  async detectViolation(
    intent: PLIxIntent,
    outcome: ExecutionOutcome
  ): Promise<Contradiction[]> {
    // Compare postconditions with actual outcomes
    // Detect violations
    // Return contradictions
  }
}
```

**Impact:** Low - new component, doesn't break existing SEG

---

### **6. SIS (Self-Improvement System)** ❓

**Status:** Unknown - may not exist yet

**Current Capabilities:**
- ❓ Not found in codebase search
- ❓ May need to be built

**PLIx Integration:**
- **PLIx needs:** Dream generation, pattern extraction, improvement hypotheses
- **Enhancement needed:** Build SIS if it doesn't exist, or extend if it does

**Required Changes:**
```typescript
// NEW: SIS dream generator
class SISDreamGenerator {
  async extractPatterns(failures: CMCAtom[]): Promise<FailurePattern[]> {
    // Extract common failure patterns
  }
  
  async generateHypotheses(
    patterns: FailurePattern[]
  ): Promise<ImprovementHypothesis[]> {
    // Generate improvement hypotheses
  }
  
  async validateHypothesis(
    hypothesis: ImprovementHypothesis
  ): Promise<boolean> {
    // Run SDF-CVF gates
  }
}
```

**Impact:** Medium - new system or significant extension

---

## 🔧 Integration Architecture: Adapter Pattern

**PLIx integrates via adapters, not direct system modifications:**

```
PLIx Contract
    ↓
PLIx IR (Intermediate Representation)
    ↓
┌─────────────────────────────────────┐
│   PLIx → AIM-OS Adapters             │
├─────────────────────────────────────┤
│ • PLIx → APOE Compiler               │  ← Generates ExecutionPlan
│ • PLIx → CMC Integration              │  ← Creates atoms with tags
│ • PLIx → VIF Gate Wrapper            │  ← Uses κ-gating API
│ • PLIx → HHNI Query                   │  ← Searches for intents
│ • PLIx → SEG Contradiction Detector   │  ← NEW: Detects violations
│ • PLIx → SIS Dream Generator         │  ← NEW: Learns from failures
└─────────────────────────────────────┘
    ↓
AIM-OS Systems (mostly unchanged)
```

---

## 📋 Required Changes Summary

| System | Changes Needed | Impact | Priority |
|--------|---------------|--------|----------|
| **APOE** | None | None | ✅ Works as-is |
| **CMC** | None | None | ✅ Works as-is |
| **VIF** | None | None | ✅ Works as-is |
| **HHNI** | None | None | ✅ Works as-is |
| **SEG** | Add contradiction detector | Low | ⚠️ Enhancement |
| **SIS** | Build or extend | Medium | ❓ New/Extend |

---

## 🎯 Implementation Strategy

### **Phase 1: Use Existing Systems (Week 1-2)**
- ✅ Build PLIx → APOE compiler (uses existing ExecutionPlan)
- ✅ Build PLIx → CMC integration (uses existing atom schema)
- ✅ Build PLIx → VIF gate wrapper (uses existing κ-gating)

### **Phase 2: Enhance SEG (Week 3)**
- ⚠️ Add contradiction detection to SEG
- ⚠️ Build PLIx → SEG contradiction detector

### **Phase 3: Build/Extend SIS (Week 4)**
- ❓ Build SIS dream generator (if doesn't exist)
- ❓ Or extend existing SIS with PLIx-specific learning

---

## 💡 Key Insight

**PLIx is designed to integrate with existing AIM-OS systems, not replace them.**

The adapter pattern means:
- ✅ **No breaking changes** to existing systems
- ✅ **Backward compatible** - existing AIM-OS usage continues to work
- ✅ **Incremental integration** - can add PLIx support gradually
- ✅ **Testable** - each adapter can be tested independently

**This is why Perplexity called it "elegant integration"** - PLIx leverages existing infrastructure rather than requiring rewrites.

---

**Status:** ✅ **MINIMAL CHANGES REQUIRED**  
**Conclusion:** Most systems work as-is. Only SEG and SIS need enhancement.

