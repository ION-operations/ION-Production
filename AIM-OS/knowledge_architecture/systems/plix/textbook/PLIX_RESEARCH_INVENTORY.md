# PLIx Research Inventory: Current State Assessment

**Date:** 2025-01-27  
**Status:** 📋 **IN PROGRESS**  
**Goal:** Inventory existing PLIx research and identify gaps

---

## ✅ **WHAT WE HAVE**

### **1. Grammar & Syntax**
- ✅ **Grammar Specification:** `GRAMMAR_SPECIFICATION_V2.md` - Complete EBNF grammar
- ✅ **Parser Implementation:** `packages/plix/src/parser/` - TypeScript parser
- ✅ **AST Schema:** `packages/plix/src/models/schema.ts` - TypeScript interfaces
- ✅ **Three Forms:** Human-PLIX, Canonical JSON, S-form support

### **2. Basic Semantics**
- ✅ **Semantics File:** `packages/plix/spec/sections/04_semantics.md` - Basic semantics
- ⚠️ **Status:** Needs expansion (formal calculus, denotational semantics)

### **3. Type System**
- ✅ **Type Checker:** `packages/plix/src/type-checker/` - Basic type checking
- ✅ **Quaternion Types:** `packages/plix/src/models/quaternion-types.ts` - Geometric types
- ⚠️ **Status:** Missing effect rows, confidence types

### **4. Compiler**
- ✅ **Compiler:** `packages/plix/src/compiler/` - Basic compilation
- ✅ **Quaternion Compiler:** `packages/plix/src/compiler/quaternion-compiler.ts` - Geometric compilation
- ⚠️ **Status:** Missing TLA+/Alloy/OPA targets

### **5. Runtime**
- ✅ **Runtime:** `packages/plix/src/runtime/` - Basic runtime
- ✅ **Quaternion Runtime:** `packages/plix/src/runtime/quaternion-runtime.ts` - Geometric runtime
- ⚠️ **Status:** Missing durable execution, saga compensation

### **6. AIM-OS Integration**
- ✅ **CMC Integration:** Documented in textbook Chapter 9
- ✅ **VIF Integration:** Documented in textbook Chapter 10
- ✅ **APOE Integration:** Documented in textbook Chapter 11
- ✅ **SEG Integration:** Documented in textbook Chapter 12

### **7. Evidence & Provenance**
- ✅ **SEG System:** `knowledge_architecture/systems/seg/` - Evidence graph
- ✅ **VIF Witnesses:** `knowledge_architecture/systems/vif/` - Witness structure
- ⚠️ **Status:** Missing Evidence DAG schema, PROV/OpenLineage mapping, verifier

### **8. Router**
- ✅ **APOE Router:** `knowledge_architecture/systems/apoe/` - Router implementation
- ⚠️ **Status:** Missing formal bandit objective, regret bounds

### **9. Textbook**
- ✅ **24 Chapters:** Complete PLIx textbook
- ✅ **Structure:** 6 parts (Foundations, Architecture, Integration, Implementation, Philosophy, Future)
- ⚠️ **Status:** Missing formal semantics chapter, security chapter, notation legend, glossary

---

## ❌ **WHAT WE'RE MISSING**

### **1. Formal Semantics**
- ❌ **Core Calculus:** Terms, judgments, reduction rules
- ❌ **Denotational Semantics:** `⟦contract⟧ : State → Pred(State)`
- ❌ **Denotational Semantics:** `⟦plan⟧ : State → Dist(State×Evidence)`
- ❌ **Soundness Proof:** If `Exec ⊨ contract` then postconditions hold

### **2. Complete Type System**
- ❌ **Effect Rows:** idempotent, compensable, external-io, data-mutation
- ❌ **Confidence Types:** `Conf p ∈ [0,1]` with lattice joins
- ❌ **Policy Types:** First-class policy types

### **3. Compilation Pipeline**
- ❌ **TLA+ Compilation:** CNL → TLA+ module
- ❌ **Alloy Compilation:** CNL → Alloy model
- ❌ **OPA Compilation:** CNL → OPA/Cedar policy
- ❌ **IRPlan Compilation:** CNL → APOE IRPlan (partial exists)

### **4. Evidence Schema**
- ❌ **Evidence DAG:** Nodes = claims, edges = supports/derived-from
- ❌ **PROV Mapping:** W3C PROV mapping
- ❌ **OpenLineage Mapping:** OpenLineage mapping
- ❌ **JSON Schema:** Canonical Evidence JSON Schema
- ❌ **Verifier Algorithm:** Deterministic replay verifier

### **5. Router Math**
- ❌ **Bandit Objective:** `J = α·cost + β·latency − γ·p_success`
- ❌ **Regret Bounds:** Formal regret analysis
- ❌ **Update Rules:** Online learning update rules

### **6. Durable Execution**
- ❌ **Checkpoint Semantics:** Formal checkpoint definition
- ❌ **Saga Compensation:** Pre/post conditions for compensation
- ❌ **TLA+ Invariants:** "at-most-once" effects, compensation guarantees

### **7. Security Model**
- ❌ **Identity Model:** Signers for contracts/evidence
- ❌ **Signatures:** Cryptographic signatures
- ❌ **Tamper-Evident Logs:** Log structure and verification
- ❌ **Policy Scoping:** Policy scoping rules
- ❌ **Redaction Semantics:** Evidence redaction rules

### **8. Core-PLIx Kernel**
- ❌ **Core-PLIx Grammar:** Minimal kernel EBNF
- ❌ **Core-PLIx Semantics:** Kernel semantics
- ❌ **CNL → Core-PLIx Lowering:** Lowering rules

### **9. Golden Example**
- ❌ **Meeting-Room Example:** Complete pipeline
- ❌ **All Artifacts:** CNL, Core, TLA+, Alloy, OPA, IRPlan, Evidence, Verifier output

### **10. Editorial**
- ❌ **Notation Legend:** Intent, Contract, Plan, Evidence, Policy, Safety
- ❌ **Glossary:** Intent Atom, Evidence Node, Confidence Gate, Compensation
- ❌ **Security Chapter:** New chapter on security

---

## 📊 **GAP ANALYSIS**

### **Critical Gaps (Must Have):**
1. **Formal Semantics** - Core calculus, denotational semantics, soundness
2. **Evidence Schema** - DAG, PROV/OpenLineage, verifier
3. **Core-PLIx Kernel** - Minimal kernel language
4. **Golden Example** - End-to-end pipeline demonstration

### **Important Gaps (Should Have):**
5. **Type System** - Effect rows, confidence types
6. **Compilation Pipeline** - TLA+/Alloy/OPA targets
7. **Durable Execution** - Checkpoint semantics, saga compensation
8. **Router Math** - Bandit objective, regret bounds

### **Nice to Have:**
9. **Security Model** - Identity, signatures, tamper-evident logs
10. **Editorial** - Notation, glossary, security chapter

---

## 🎯 **RESEARCH PRIORITY**

### **Phase 1: Foundation (Week 1-2)**
1. Formal semantics (core calculus, denotational semantics)
2. Core-PLIx kernel (minimal language)
3. Evidence schema (DAG, PROV/OpenLineage)

### **Phase 2: Compilation (Week 2-3)**
4. Type system (effect rows, confidence types)
5. Compilation pipeline (TLA+/Alloy/OPA)

### **Phase 3: Execution (Week 3-4)**
6. Durable execution (checkpoint semantics, saga compensation)
7. Router math (bandit objective, regret bounds)

### **Phase 4: Integration (Week 4)**
8. Security model (identity, signatures)
9. Golden example (end-to-end pipeline)
10. Editorial (notation, glossary, security chapter)

---

## 📁 **RESEARCH ARTIFACTS STRUCTURE**

```
knowledge_architecture/systems/plix/research/
├── formal_semantics/
│   ├── core_calculus.md          ⏳ TODO
│   ├── denotational_semantics.md ⏳ TODO
│   └── soundness_proof.md        ⏳ TODO
├── type_system/
│   ├── type_specification.md      ⏳ TODO
│   ├── effect_rows.md            ⏳ TODO
│   └── confidence_types.md       ⏳ TODO
├── compilation_pipeline/
│   ├── pipeline_specification.md  ⏳ TODO
│   ├── tla_compilation.md         ⏳ TODO
│   ├── alloy_compilation.md       ⏳ TODO
│   ├── opa_compilation.md        ⏳ TODO
│   └── irplan_compilation.md      ✅ EXISTS (partial)
├── evidence_schema/
│   ├── evidence_dag.md            ⏳ TODO
│   ├── prov_mapping.md            ⏳ TODO
│   ├── openlineage_mapping.md     ⏳ TODO
│   └── verifier_algorithm.md     ⏳ TODO
├── router_math/
│   ├── bandit_objective.md        ⏳ TODO
│   └── regret_bounds.md          ⏳ TODO
├── durable_execution/
│   ├── checkpoint_semantics.md    ⏳ TODO
│   ├── saga_compensation.md       ⏳ TODO
│   └── tla_invariants.md          ⏳ TODO
├── security/
│   ├── identity_model.md          ⏳ TODO
│   ├── signatures.md              ⏳ TODO
│   └── policy_scoping.md          ⏳ TODO
├── core_plix/
│   ├── grammar.ebnf               ⏳ TODO
│   ├── semantics.md               ⏳ TODO
│   └── lowering_rules.md          ⏳ TODO
└── golden_example/
    ├── meeting_room.cnl           ⏳ TODO
    ├── meeting_room.core.plix      ⏳ TODO
    ├── meeting_room.tla            ⏳ TODO
    ├── meeting_room.alloy          ⏳ TODO
    ├── meeting_room.opa            ⏳ TODO
    ├── meeting_room.irplan.json    ⏳ TODO
    ├── meeting_room.evidence.json  ⏳ TODO
    └── verifier_output.txt         ⏳ TODO
```

---

## 🚀 **NEXT STEPS**

1. **Review Existing Semantics:** Read `packages/plix/spec/sections/04_semantics.md`
2. **Review Grammar:** Review `GRAMMAR_SPECIFICATION_V2.md` for Core-PLIx extraction
3. **Review Evidence Systems:** Review SEG and VIF implementations
4. **Begin Research:** Start Phase 1 research tasks

---

**Status:** 📋 **INVENTORY COMPLETE**  
**Next:** Begin Phase 1 research

