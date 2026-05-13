# PLIx Design Decisions - Quick Reference

**Date:** 2025-11-09  
**Status:** 🔒 **LOCKED**  
**Purpose:** Quick answers to ChatGPT's 10 design questions

---

## ✅ 10 Quick Answers

### 1. Observable Postconditions
**Answer:** **Hybrid - State queries + Events**
- State queries: CMC atoms for idempotency
- Events: SEG event stream for real-time
- Adapters: Custom read models

### 2. Types & Units
**Answer:** **Lock at grammar level**
- Types: `datetime`, `duration`, `money`, `uri`, `email`, `uuid`
- Validation: Compile-time + runtime

### 3. Constraint Calculus
**Answer:** **Hybrid - Boolean + Arithmetic**
- Boolean: `==`, `!=`, `&&`, `||`, `!`
- Comparison: `<=`, `>=`, `<`, `>`
- Arithmetic: `+`, `-`, `*`, `/` (durations, money)
- Functions: `len()`, `contains()`, `matches()`
- Compilation: GBNF → AST → SMT

### 4. IR Shape
**Answer:** **Per-node checkpoints, task+params+intent-hash idempotency**
- Checkpoints: `per-node` (default)
- Idempotency: `${intent_hash}.${task_id}.${params_hash}`
- Retry: `max`, `policy` (linear/exponential), `ms`

### 5. Confidence Gate Math
**Answer:** **Global 0.70 + per-task override + evidence learning**
- Global min: `0.70`
- Per-task: Optional `confidence_min` override
- Evidence: Store deltas in SEG, learn from outcomes

### 6. Policy Bridge
**Answer:** **Static compile-time + Runtime OPA**
- Static: Type checking, syntax validation, dependency analysis
- Runtime: OPA evaluation with claim schema
- Both: Fail fast on static, gate on runtime

### 7. Lineage Schema
**Answer:** **PROV + OpenLineage + CMC atom references**
- Events: `RunEvent`, `JobEvent`, `DatasetEvent`
- PROV: Entities, activities, relations
- CMC: Reference atom IDs in events

### 8. Round-Trip Fidelity
**Answer:** **Strict for core, lossy for notes**
- Perfect: Contract text, step IDs, params, dependencies, constraints
- Lossy: Notes, formatting, ordering, metadata

### 9. Compensation Catalog
**Answer:** **Required for side-effects, CI enforced**
- Rule: Every side-effecting task MUST declare `compensate: <task_id>` or `compensate: none` with justification
- CI: Static analysis + build failure if missing

### 10. Error Taxonomy
**Answer:** **5 fault types + saga reaction table**
- Types: `PreconditionFault`, `PolicyFault`, `LowConfidenceFault`, `TransportFault`, `SideEffectFault`
- Reactions: Retry/compensate/escalate based on type

---

## 🚀 Thin-Slice MVP (6 Components)

1. **Parser + JSON Schema** - CNL → PLIx, types/units validation
2. **Lowering to IR** - PLIx → IR, idempotency, retries, compensations
3. **Guards** - VIF confidence + OPA policy gates
4. **Execution Adapter** - Mock API + happy/saga paths
5. **Evidence Emitters** - PROV + OpenLineage → SEG/CMC
6. **Tests** - Contract, constraint, safety, execution, evidence tests

---

## 📊 Implementation Timeline

**Week 1:** Parser + Schema  
**Week 2:** Lowering + Guards  
**Week 3:** Execution + Evidence  
**Week 4:** Tests + Integration

**Total:** 4 weeks for thin-slice MVP

---

**Status:** 🔒 **READY FOR IMPLEMENTATION**

