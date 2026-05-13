# PLIx Textbook Research Plan: Addressing ChatGPT Feedback

**Date:** 2025-01-27  
**Status:** 📋 **RESEARCH PHASE**  
**Goal:** Gather research to address gaps identified by ChatGPT before finalizing unified textbook

---

## 🎯 **FEEDBACK SUMMARY**

ChatGPT identified critical gaps to make PLIx a **specification** rather than just a treatise:

1. **Formal semantics** (core calculus, denotational semantics, soundness)
2. **Type system** (Intent/Task/Evidence/Policy types, effect rows, confidence)
3. **Contract compilation pipeline** (CNL → Core-PLIx → TLA+/Alloy/OPA/IRPlan)
4. **Evidence schema** (Evidence DAG, PROV/OpenLineage, verifier)
5. **Economic router math** (bandit objective, regret bounds)
6. **Durable execution** (checkpoint semantics, saga compensation, TLA+ invariants)
7. **Security** (identity, signatures, tamper-evident logs, policy scoping)
8. **Core-PLIx kernel** (minimal, orthogonal language)
9. **Golden example** (end-to-end meeting-room pipeline)
10. **Editorial refinements** (notation legend, glossary, security chapter)

---

## 📚 **RESEARCH TASKS**

### **Task 1: Formal Semantics Research**
**Status:** ⏳ **PENDING**

**Research Areas:**
- Core calculus for PLIx (terms, judgments, reduction rules)
- Denotational semantics: `⟦contract⟧ : State → Pred(State)`
- Denotational semantics: `⟦plan⟧ : State → Dist(State×Evidence)`
- Soundness: if `Exec ⊨ contract` then postconditions hold

**Sources to Review:**
- Current PLIx grammar specification
- Formal methods literature (TLA+, Alloy, Coq)
- Domain-specific language semantics
- Contract-based programming semantics

**Deliverables:**
- Core-PLIx calculus definition
- Denotational semantics specification
- Soundness proof sketch

---

### **Task 2: Type System Research**
**Status:** ⏳ **PENDING**

**Research Areas:**
- Types for Intents, Tasks, Evidence, Policies
- Effect rows (idempotent, compensable, external-io, data-mutation)
- Confidence as first-class type: `Conf p ∈ [0,1]` with lattice joins

**Sources to Review:**
- Effect systems literature (Koka, Eff, Frank)
- Dependent type systems
- Refinement types
- Confidence/uncertainty type systems

**Deliverables:**
- Type system specification
- Effect row system
- Confidence type calculus

---

### **Task 3: Compilation Pipeline Research**
**Status:** ⏳ **PENDING**

**Research Areas:**
- CNL → AST transformation
- AST → Core-PLIx lowering
- Core-PLIx → TLA+ compilation
- Core-PLIx → Alloy compilation
- Core-PLIx → OPA/Cedar compilation
- Core-PLIx → IRPlan compilation

**Sources to Review:**
- Current PLIx parser implementation
- TLA+ specification examples
- Alloy model examples
- OPA/Cedar policy examples
- APOE IRPlan format

**Deliverables:**
- Compilation pipeline specification
- Transformation rules for each target
- Example transformations

---

### **Task 4: Evidence Schema Research**
**Status:** ⏳ **PENDING**

**Research Areas:**
- Evidence DAG structure (nodes = claims, edges = supports/derived-from)
- W3C PROV mapping
- OpenLineage mapping
- JSON Schema for Evidence
- Hash-anchoring (content-hash, time, tool-id, inputs)
- Verifier algorithm (deterministic replay)

**Sources to Review:**
- W3C PROV specification
- OpenLineage specification
- Current SEG implementation
- VIF witness structure
- Provenance verification literature

**Deliverables:**
- Evidence DAG schema
- PROV/OpenLineage mapping
- Verifier algorithm specification

---

### **Task 5: Economic Router Math Research**
**Status:** ⏳ **PENDING**

**Research Areas:**
- Bandit objective: minimize `J = α·cost + β·latency − γ·p_success`
- Online updates
- Regret bounds
- Update rules

**Sources to Review:**
- Multi-armed bandit literature
- Online learning algorithms
- Current APOE router implementation
- Cost optimization literature

**Deliverables:**
- Router objective specification
- Update rules
- Regret bound analysis

---

### **Task 6: Durable Execution Research**
**Status:** ⏳ **PENDING**

**Research Areas:**
- Checkpoint semantics
- Saga compensation pre/post conditions
- TLA+ safety invariants for "at-most-once" effects
- Compensation guarantees

**Sources to Review:**
- Saga pattern literature
- Durable execution systems (Temporal, Cadence)
- TLA+ specification examples
- Current APOE execution implementation

**Deliverables:**
- Checkpoint semantics specification
- Saga compensation specification
- TLA+ invariants

---

### **Task 7: Security Research**
**Status:** ⏳ **PENDING**

**Research Areas:**
- Identity of signers for contracts/evidence
- Tamper-evident logs
- Policy scoping
- Redaction semantics for evidence

**Sources to Review:**
- VIF witness structure
- CMSE residue masks
- Current security implementations
- Cryptographic signatures
- Policy-based access control

**Deliverables:**
- Security model specification
- Signature scheme
- Policy scoping rules

---

### **Task 8: Core-PLIx Kernel Design**
**Status:** ⏳ **PENDING**

**Research Areas:**
- Minimal, orthogonal kernel language
- Core-PLIx syntax (from ChatGPT example)
- Relationship to CNL (CNL lowers to Core-PLIx)

**Sources to Review:**
- Current PLIx grammar
- Minimal language design principles
- Domain-specific language kernels

**Deliverables:**
- Core-PLIx grammar (EBNF)
- Core-PLIx semantics
- CNL → Core-PLIx lowering rules

---

### **Task 9: Golden Example Creation**
**Status:** ⏳ **PENDING**

**Research Areas:**
- Meeting-room booking intent
- Complete pipeline: CNL → Core → TLA+/Alloy/OPA → IR → Evidence → Verifier
- All artifacts for one example

**Deliverables:**
- CNL source
- Core-PLIx representation
- TLA+ module
- Alloy model
- OPA policy
- IRPlan JSON
- Evidence DAG
- Verifier output

---

### **Task 10: Editorial Refinements**
**Status:** ⏳ **PENDING**

**Research Areas:**
- Notation legend (Intent, Contract, Plan, Evidence, Policy, Safety)
- Glossary (Intent Atom, Evidence Node, Confidence Gate, Compensation)
- Security chapter structure
- Remove repetition

**Deliverables:**
- Notation legend
- Glossary
- Security chapter outline
- Repetition removal plan

---

## 📊 **CURRENT STATE ASSESSMENT**

### **What We Have:**
- ✅ PLIx grammar specification (EBNF)
- ✅ PLIx parser implementation
- ✅ PLIx type checker (basic)
- ✅ PLIx compiler (basic)
- ✅ Integration with AIM-OS systems (CMC, VIF, APOE, SEG)
- ✅ Textbook chapters (24 chapters)

### **What We're Missing:**
- ❌ Formal semantics (core calculus, denotational semantics)
- ❌ Complete type system (effect rows, confidence types)
- ❌ Compilation pipeline (TLA+/Alloy/OPA targets)
- ❌ Evidence schema (DAG, PROV/OpenLineage mapping)
- ❌ Router math (bandit objective, regret bounds)
- ❌ Durable execution (checkpoint semantics, saga compensation)
- ❌ Security model (identity, signatures, tamper-evident logs)
- ❌ Core-PLIx kernel specification
- ❌ Golden end-to-end example
- ❌ Editorial refinements (notation, glossary, security chapter)

---

## 🚀 **RESEARCH STRATEGY**

### **Phase 1: Literature Review** (Week 1)
- Review formal methods literature
- Review type system literature
- Review evidence/provenance literature
- Review durable execution literature
- Review security literature

### **Phase 2: Current Implementation Review** (Week 1-2)
- Review current PLIx parser/compiler
- Review current AIM-OS integrations
- Review current evidence/provenance systems
- Review current router implementation

### **Phase 3: Specification Design** (Week 2-3)
- Design Core-PLIx kernel
- Design formal semantics
- Design type system
- Design compilation pipeline
- Design evidence schema
- Design security model

### **Phase 4: Golden Example** (Week 3-4)
- Create meeting-room example
- Generate all artifacts
- Validate pipeline
- Document example

### **Phase 5: Integration** (Week 4)
- Integrate research into textbook
- Add notation legend
- Add glossary
- Add security chapter
- Remove repetition

---

## 📁 **RESEARCH ARTIFACTS**

**Target Structure:**
```
knowledge_architecture/systems/plix/research/
├── formal_semantics/
│   ├── core_calculus.md
│   ├── denotational_semantics.md
│   └── soundness_proof.md
├── type_system/
│   ├── type_specification.md
│   ├── effect_rows.md
│   └── confidence_types.md
├── compilation_pipeline/
│   ├── pipeline_specification.md
│   ├── tla_compilation.md
│   ├── alloy_compilation.md
│   ├── opa_compilation.md
│   └── irplan_compilation.md
├── evidence_schema/
│   ├── evidence_dag.md
│   ├── prov_mapping.md
│   ├── openlineage_mapping.md
│   └── verifier_algorithm.md
├── router_math/
│   ├── bandit_objective.md
│   └── regret_bounds.md
├── durable_execution/
│   ├── checkpoint_semantics.md
│   ├── saga_compensation.md
│   └── tla_invariants.md
├── security/
│   ├── identity_model.md
│   ├── signatures.md
│   └── policy_scoping.md
├── core_plix/
│   ├── grammar.ebnf
│   ├── semantics.md
│   └── lowering_rules.md
└── golden_example/
    ├── meeting_room.cnl
    ├── meeting_room.core.plix
    ├── meeting_room.tla
    ├── meeting_room.alloy
    ├── meeting_room.opa
    ├── meeting_room.irplan.json
    ├── meeting_room.evidence.json
    └── verifier_output.txt
```

---

## 🎯 **SUCCESS CRITERIA**

### **Research Quality:**
- ✅ All 10 research tasks complete
- ✅ Formal specifications created
- ✅ Golden example complete
- ✅ All artifacts generated

### **Integration Quality:**
- ✅ Research integrated into textbook
- ✅ Notation legend added
- ✅ Glossary added
- ✅ Security chapter added
- ✅ Repetition removed

### **Specification Quality:**
- ✅ PLIx is a specification, not just a treatise
- ✅ All gaps addressed
- ✅ Ready for unified textbook integration

---

**Status:** 📋 **RESEARCH PLAN CREATED**  
**Next:** Begin Phase 1 - Literature Review

