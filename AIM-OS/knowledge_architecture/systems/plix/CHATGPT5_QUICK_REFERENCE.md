# ChatGPT5 Integration Guide - Summary & Answers

**Date:** 2025-11-09  
**Purpose:** Quick reference for ChatGPT5's implementation blueprint integration  
**Status:** ✅ **COMPLETE**

---

## ChatGPT5's Questions → Answers

### 1. Constraint Semantics: Hard vs Soft
**Answer:** **Hard by default, soft with explicit override**

```typescript
constraints: [
  { condition: "duration <= 4h", hard: true },  // Default: hard
  { condition: "user_preference == 'video'", hard: false },  // Soft: warning only
]
```

**Rationale:** AIM-OS uses VIF confidence gates (hard fail below threshold), SCOR monitors safety (hard fail on violations), but allow explicit `soft: true` flag for warnings.

---

### 2. Confidence Thresholds: Global vs Per-Task
**Answer:** **Per-task overrides, global default**

```typescript
telemetry: {
  confidenceThresholds: {
    minimum: 0.70,  // Global default (matches AIM-OS standard)
    warning: 0.80,
    critical: 0.90,
  }
}

// Per-task override
tasks: [{
  id: "critical_step",
  confidence_threshold: 0.90,  // Override for critical tasks
}]
```

**Rationale:** VIF already supports per-operation confidence. Some tasks are critical (0.9), others routine (0.7). Global default: 0.70.

---

### 3. Primary Durable Backend: Temporal vs In-House
**Answer:** **Start with `plix-runtime` in-house, add Temporal adapter**

**Rationale:**
- CMC already provides durable state (bitemporal)
- APOE already executes plans
- Temporal adapter can be added later for external workflows
- In-house gives us full control and AIM-OS integration

**Implementation:**
- Phase 1: `plix-runtime` using CMC + APOE
- Phase 2: Temporal adapter for external workflows
- Phase 3: Both supported (choose via config)

---

### 4. Policy Language: OPA vs Cedar
**Answer:** **OPA (Rego) first, Cedar later**

**Rationale:**
- OPA is domain-agnostic (matches PLIx's flexibility)
- Rego is more expressive for complex constraints
- Cedar is AWS-specific (less flexible)
- OPA integrates better with SCOR

**Implementation:**
- Phase 1: OPA/Rego integration
- Phase 2: Cedar adapter (if needed for AWS-specific policies)

---

### 5. CNL Flavor: English-like vs Codespeak
**Answer:** **English-like (Gherkin-style) with structured keywords**

**Rationale:**
- AIM-OS emphasizes human-legibility
- LLMs parse English better than codespeak
- Gherkin-style is familiar to developers
- Structured keywords reduce ambiguity

**Implementation:**
```cnl
Intent: Book a meeting room  # English-like
Task check_availability:     # Structured keyword
  Action: api.check_room_availability  # Machine-executable
```

---

## Default Configuration (`plix.config.ts`)

```typescript
export const PLIX_DEFAULTS = {
  // Constraint semantics
  constraints: {
    default_hard: true,  // Hard by default (fail on violation)
    allow_soft_override: true,  // But allow soft: true flag
  },
  
  // Confidence thresholds
  confidence: {
    global_minimum: 0.70,  // Matches AIM-OS standard
    global_warning: 0.80,
    global_critical: 0.90,
    allow_per_task_override: true,  // Per-task thresholds allowed
  },
  
  // Durable backend
  execution: {
    primary_backend: 'aimos',  // Use CMC + APOE (in-house)
    temporal_adapter: false,  // Add later for external workflows
  },
  
  // Policy language
  policy: {
    primary_language: 'rego',  // OPA/Rego first
    cedar_adapter: false,  // Add later if needed
  },
  
  // CNL flavor
  cnl: {
    style: 'english-like',  // Gherkin-style (human-legible)
    structured_keywords: true,  // But with structured keywords
  },
};
```

---

## Key AIM-OS System Interfaces (Corrected)

### APOE
```python
# packages/apoe/executor.py
class PlanExecutor:
    def execute(self, plan: ExecutionPlan) -> ExecutionResult:
        # Executes plan steps in topological order
        # Handles dependencies via get_ready_steps()
        # Returns ExecutionResult with metrics
    
    def register_role_handler(self, role_name: str, handler: Callable):
        # Register handler for role execution
```

### Router
```python
# packages/router/core/router.py
class Router:
    async def decide(self, ctx: RouterContext) -> ToolCallPlan:
        # Uses BanditScorer.score() internally (BaRP equivalent!)
        # Returns ToolCallPlan ready for execution

# packages/router/core/bandit.py
class BanditScorer:
    async def score(self, proposals, snapshot, manifest) -> List[RankedTool]:
        # Multi-armed bandit scoring (BaRP equivalent!)
        # Considers cost/performance trade-off
```

### SEG
```python
# packages/seg/seg_graph.py
class SEGraph:
    def add_entity(self, entity: Entity) -> Entity:
        # Creates entity (Claim, Source, Derivation, Agent)
        # Returns entity with ID
    
    def add_relation(self, relation: Relation) -> Relation:
        # Creates relation (edge) between entities
        # Relation has: source_id, target_id, relation_type, confidence
        # RelationType: SUPPORTS, CONTRADICTS, REFERENCES, DERIVES_FROM, RELATES_TO
```

### CMC
```python
# packages/cmc_service/ (various implementations)
# CMC stores atoms with bitemporal tracking
# Interface varies, but core concept:
# - create_atom(content, tags, metadata) -> Atom
# - Atoms have transaction_time (TT) and valid_time (VT)
```

### VIF
```python
# packages/vif/witness.py
class VIF:
    confidence_score: float  # 0-1
    confidence_band: ConfidenceBand  # A/B/C
    kappa_gate_passed: bool
```

### TCS
```python
# packages/timeline_context_system/ (various implementations)
# TCS tracks bitemporal timeline
# Core concept:
# - add_entry(entry_type, content, valid_from, valid_to) -> entry_id
```

---

## Revised `plix-runtime.runPlan` Integration

**Key Changes from ChatGPT5's Blueprint:**

1. **APOE Integration:** Use `PlanExecutor.execute()` with `register_role_handler()`
2. **Router Integration:** Use `Router.decide()` (already has BanditScorer internally!)
3. **SEG Integration:** Use `add_entity()` and `add_relation()` (Relation object, not separate params)
4. **CMC Integration:** Use `create_atom()` for checkpoints (bitemporal)
5. **VIF Integration:** Use `VIF.confidence_score` and `confidence_band` for gates
6. **TCS Integration:** Use `add_entry()` for timeline tracking

**Don't Replace, Enhance:**
- ✅ Use APOE for plan execution (don't build new executor)
- ✅ Use Router for economic routing (already has BaRP!)
- ✅ Use CMC for durable state (already has bitemporal!)
- ✅ Use SEG for evidence chains (already has graph structure!)
- ✅ Use VIF for confidence gates (already tracks confidence!)
- ✅ Use TCS for timeline (already has bitemporal timeline!)

---

## What ChatGPT5 Should Build (New Components)

### ✅ New Components (20%)
1. **CNL Compiler** (`plix-cnl`) - Gherkin-style + SmaCoNat
2. **Formal Validation** (`plix-compiler/validation`) - Alloy/TLA+ integration
3. **Policy Emission** (`plix-policy`) - OPA/Rego generation
4. **Provenance Emitters** (`plix-provenance`) - PROV/OpenLineage (enhance SEG)
5. **LLM Adapters** (`plix-adapters`) - LangChain, AutoGen, DSPy, LangGraph
6. **IDE Integration** (`plix-ide`) - Contract panel, execution heatmap

### ⏳ Enhance Existing (20%)
1. **Saga Pattern** - Add to APOE (compensation callbacks)
2. **Self-REF Confidence** - Add to VIF (confidence tokens)
3. **OpenLineage Events** - Add to SEG (RunEvent/JobEvent/DatasetEvent)
4. **Intent Lineage** - Add to SEG (NL → evidence tracing)

---

## Critical Integration Notes

### 1. Router Already Has BaRP!
**ChatGPT5's Blueprint:** Build new routing system  
**Reality:** Router's `BanditScorer.score()` IS the BaRP equivalent!

**What to Do:** Use `Router.decide()` - it already does economic routing!

### 2. APOE Already Executes Plans
**ChatGPT5's Blueprint:** Build new execution engine  
**Reality:** APOE's `PlanExecutor.execute()` already executes plans!

**What to Do:** Compile PLIx IR → APOE ExecutionPlan format, use `PlanExecutor.execute()`

### 3. CMC Already Has Bitemporal Storage
**ChatGPT5's Blueprint:** Build new state persistence  
**Reality:** CMC already has bitemporal atoms (valid time + transaction time)!

**What to Do:** Use `CMC.create_atom()` for checkpoints

### 4. SEG Already Has Evidence Chains
**ChatGPT5's Blueprint:** Build new evidence system  
**Reality:** SEG already has graph structure (entities + relations)!

**What to Do:** Use `SEG.add_entity()` and `SEG.add_relation()` for evidence

---

## Revised Monorepo Structure

```
plix/
├─ packages/
│  ├─ plix-core/                 # AST, JSON Schema, type-checker, CNL parser
│  ├─ plix-compiler/             # Lowering → IR → APOE ExecutionPlan
│  ├─ plix-policy/               # OPA/Rego emission + SCOR integration
│  ├─ plix-provenance/           # PROV/OpenLineage emitters → SEG
│  ├─ plix-runtime/              # Durable runtime using CMC + APOE + Saga
│  ├─ plix-adapters/
│  │   ├─ langchain/             # PLIx → LangChain chains
│  │   ├─ langgraph/              # PLIx → LangGraph stateful agents
│  │   ├─ dspy/                   # PLIx → DSPy modules
│  │   └─ autogen/                # PLIx → AutoGen dialogues
│  ├─ plix-cnl/                  # Gherkin-style grammar + SmaCoNat compiler
│  ├─ plix-ide/                  # VSCode/Cursor panel + heatmap context widget
│  └─ plix-tests/                # Golden specs; round-trip; property tests
└─ integrations/
   ├─ apoe/                       # APOE integration (plan execution)
   ├─ router/                     # Router integration (economic gate)
   ├─ vif/                        # VIF integration (confidence gate)
   ├─ seg/                        # SEG integration (evidence chains)
   ├─ cmc/                        # CMC integration (durable state)
   └─ tcs/                        # TCS integration (timeline tracking)
```

---

## Next Steps for ChatGPT5

1. **Review AIM-OS System Interfaces** - Understand existing APIs (this document)
2. **Revise `plix-runtime`** - Integrate with APOE, Router, VIF, SEG, CMC, TCS
3. **Build CNL Compiler** - Gherkin-style + SmaCoNat methodology
4. **Build Formal Validation** - Alloy/TLA+ integration
5. **Build Policy Emission** - OPA/Rego generation
6. **Build LLM Adapters** - LangChain, AutoGen, DSPy, LangGraph

---

**Key Message:** AIM-OS already has 80% of PLIx's requirements. Focus on the **20% new components** (CNL compiler, formal validation, policy emission) and **integrate** with existing systems rather than replacing them.

