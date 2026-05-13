# PLIx Implementation Blueprint - ChatGPT5 Integration Summary

**Date:** 2025-11-09  
**Status:** ✅ **INTEGRATION GUIDE COMPLETE**  
**Purpose:** Help ChatGPT5 understand AIM-OS systems for proper PLIx integration

---

## Executive Summary

ChatGPT5's implementation blueprint is excellent, but needs **AIM-OS system context** to integrate properly. This document provides:

1. **Answers to ChatGPT5's 5 open questions**
2. **Corrected AIM-OS system interfaces**
3. **Integration strategy (don't replace, enhance)**
4. **Revised `plix-runtime.runPlan` implementation**

---

## Answers to ChatGPT5's Questions

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

## Corrected AIM-OS System Interfaces

### APOE (Plan Execution)
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

**PLIx Integration:** Compile PLIx IR → APOE ExecutionPlan format, use `PlanExecutor.execute()`

---

### Router (Economic Gate - Already Has BaRP!)
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

**PLIx Integration:** Use `Router.decide()` - it already does economic routing!

---

### SEG (Evidence Chains)
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

**PLIx Integration:** Use `add_entity()` and `add_relation()` for evidence chains

---

### CMC (Durable State)
```python
# packages/cmc_service/ (various implementations)
# CMC stores atoms with bitemporal tracking
# Interface varies, but core concept:
# - create_atom(content, tags, metadata) -> Atom
# - Atoms have transaction_time (TT) and valid_time (VT)
```

**PLIx Integration:** Use `create_atom()` for checkpoints (bitemporal)

---

### VIF (Confidence Gate)
```python
# packages/vif/witness.py
class VIF:
    confidence_score: float  # 0-1
    confidence_band: ConfidenceBand  # A/B/C
    kappa_gate_passed: bool
```

**PLIx Integration:** Use `VIF.confidence_score` and `confidence_band` for gates

---

### TCS (Timeline Tracking)
```python
# packages/timeline_context_system/ (various implementations)
# TCS tracks bitemporal timeline
# Core concept:
# - add_entry(entry_type, content, valid_from, valid_to) -> entry_id
```

**PLIx Integration:** Use `add_entry()` for timeline tracking

---

## Key Integration Principles

### 1. Don't Replace, Enhance

**Wrong:** Build new plan execution system  
**Right:** Enhance APOE with PLIx contracts

**Wrong:** Build new routing system  
**Right:** Use Router's existing bandit routing (already has BaRP!)

**Wrong:** Build new state persistence  
**Right:** Use CMC's existing bitemporal storage

---

### 2. Use Existing Interfaces

**APOE:**
```typescript
const executor = new PlanExecutor();
executor.register_role_handler(role, handler);
await executor.execute(apoePlan);
```

**Router:**
```typescript
const toolPlan = await router.decide({
  goal: ir.intent,
  task: node.action,
  context: { node_id: node.id },
});
// Router.decide() → BanditScorer.score() → Economic routing!
```

**SEG:**
```typescript
const claimEntity = await seg.add_entity({ type: 'claim', name: claimContent });
const sourceEntity = await seg.add_entity({ type: 'source', name: 'execution_result' });
const relation = new Relation({
  source_id: sourceEntity.id,
  target_id: claimEntity.id,
  relation_type: RelationType.SUPPORTS,
  confidence: 1.0,
});
await seg.add_relation(relation);
```

**CMC:**
```typescript
const checkpoint = await cmc.create_atom({
  content: { type: 'plix_checkpoint', node_id, state },
});
```

**VIF:**
```typescript
const witness = new VIF({ confidence_score, confidence_band });
if (witness.confidence_band === 'C') throw new Error('Low confidence');
```

**TCS:**
```typescript
await tcs.add_entry({
  entry_type: 'plix_node_start',
  content: { node_id, action },
});
```

---

## Default Configuration

```typescript
export const PLIX_DEFAULTS = {
  constraints: { default_hard: true, allow_soft_override: true },
  confidence: { global_minimum: 0.70, allow_per_task_override: true },
  execution: { primary_backend: 'aimos', temporal_adapter: false },
  policy: { primary_language: 'rego', cedar_adapter: false },
  cnl: { style: 'english-like', structured_keywords: true },
};
```

---

## What ChatGPT5 Should Build

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

## Critical Notes

### Router Already Has BaRP!
**ChatGPT5's Blueprint:** Build new routing system  
**Reality:** Router's `BanditScorer.score()` IS the BaRP equivalent!

**What to Do:** Use `Router.decide()` - it already does economic routing!

### APOE Already Executes Plans
**ChatGPT5's Blueprint:** Build new execution engine  
**Reality:** APOE's `PlanExecutor.execute()` already executes plans!

**What to Do:** Compile PLIx IR → APOE ExecutionPlan format, use `PlanExecutor.execute()`

### CMC Already Has Bitemporal Storage
**ChatGPT5's Blueprint:** Build new state persistence  
**Reality:** CMC already has bitemporal atoms (valid time + transaction time)!

**What to Do:** Use `CMC.create_atom()` for checkpoints

### SEG Already Has Evidence Chains
**ChatGPT5's Blueprint:** Build new evidence system  
**Reality:** SEG already has graph structure (entities + relations)!

**What to Do:** Use `SEG.add_entity()` and `SEG.add_relation()` for evidence

---

**Key Message:** AIM-OS already has 80% of PLIx's requirements. Focus on the **20% new components** (CNL compiler, formal validation, policy emission) and **integrate** with existing systems rather than replacing them.

