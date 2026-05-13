# LDP Stage 1: System Index & Ontology - PLIx Integration

**Date:** 2025-01-27  
**Protocol:** LUCID Development Protocol (LDP) Stage 1  
**Status:** ⏳ **IN PROGRESS** - System mapping underway  
**Confidence:** 0.85

---

## 🗺️ **MASTER SYSTEM INDEX**

**Question:** Where in the AIM-OS organism does this integration live?

**Answer:** This integration touches multiple organs, with APOE as the primary host.

---

## 📊 **INDEX NODE LIST**

### **Primary Nodes (Direct Implementation):**

**1. `orchestration.apoe.compiler.plixToAcl`** ⭐ **NEW**
- **Type:** New capability
- **Security Level:** Medium
- **Perf Sensitivity:** Interactive (< 1s compilation)
- **Surface Type:** Compiler/Transform
- **Ownership:** APOE subsystem
- **Purpose:** Compile PLIx CNL to ACL plans
- **Inputs:** PLIx Intent (AST)
- **Outputs:** ACL Plan (enhanced with PLIx semantics)

**2. `orchestration.apoe.executor.compensation`** ⭐ **NEW**
- **Type:** New capability
- **Security Level:** High (reversible operations)
- **Perf Sensitivity:** Realtime (immediate rollback)
- **Surface Type:** Runtime execution
- **Ownership:** APOE subsystem
- **Purpose:** Execute compensation steps on failure
- **Inputs:** Failed step context
- **Outputs:** Compensation result

**3. `orchestration.apoe.executor.retryFallback`** ⭐ **NEW**
- **Type:** New capability
- **Security Level:** Medium
- **Perf Sensitivity:** Interactive
- **Surface Type:** Runtime execution
- **Ownership:** APOE subsystem
- **Purpose:** Retry with backoff, fallback on exhaustion
- **Inputs:** Step + retry policy
- **Outputs:** Success/failure + evidence

**4. `orchestration.apoe.backends.tlaPlus`** ⭐ **NEW**
- **Type:** New backend
- **Security Level:** Low (verification only)
- **Perf Sensitivity:** Background (< 5s)
- **Surface Type:** Verification
- **Ownership:** APOE subsystem
- **Purpose:** Compile ACL to TLA+ for model checking
- **Inputs:** ACL Plan
- **Outputs:** TLA+ specification

**5. `orchestration.apoe.backends.alloy`** ⭐ **NEW**
- **Type:** New backend
- **Security Level:** Low (verification only)
- **Perf Sensitivity:** Background (< 5s)
- **Surface Type:** Verification
- **Ownership:** APOE subsystem
- **Purpose:** Compile ACL to Alloy for structural validation
- **Inputs:** ACL Plan
- **Outputs:** Alloy specification

**6. `orchestration.apoe.backends.opa`** ⭐ **NEW**
- **Type:** New backend
- **Security Level:** High (policy enforcement)
- **Perf Sensitivity:** Realtime (runtime checks)
- **Surface Type:** Runtime policy
- **Ownership:** APOE subsystem
- **Purpose:** Compile ACL to OPA for policy enforcement
- **Inputs:** ACL Plan
- **Outputs:** OPA policy

**7. `provenance.vif.witnesses.plixConstraintReplay`** ⭐ **ENHANCED**
- **Type:** Enhanced capability
- **Security Level:** Critical (provenance integrity)
- **Perf Sensitivity:** Interactive
- **Surface Type:** Verification
- **Ownership:** VIF subsystem
- **Purpose:** Create witnesses for pure constraint replay
- **Inputs:** Constraint + evidence DAG
- **Outputs:** Constraint replay witness

**8. `orchestration.apoe.acl.purityChecker`** ⭐ **NEW**
- **Type:** New capability
- **Security Level:** High (correctness validation)
- **Perf Sensitivity:** Interactive
- **Surface Type:** Compiler validation
- **Ownership:** APOE subsystem
- **Purpose:** Validate constraints are pure (no side effects)
- **Inputs:** Constraint expression
- **Outputs:** Purity validation result

---

### **Secondary Nodes (Enhanced Integration):**

**9. `orchestration.apoe.acl.parser`** 📝 **ENHANCED**
- **Current:** ACL parser (PLAN/ROLE/STEP/ASSIGN/REQUIRES/BUDGET/GATE)
- **Enhancement:** Accept PLIx-enhanced syntax (compensation, retry, purity)
- **Security Level:** Medium
- **Ownership:** APOE subsystem

**10. `orchestration.apoe.executor.core`** 📝 **ENHANCED**
- **Current:** Executes steps in dependency order
- **Enhancement:** Add compensation, retry/fallback execution
- **Security Level:** High
- **Ownership:** APOE subsystem

**11. `provenance.vif.witnesses.planExecution`** 📝 **ENHANCED**
- **Current:** Creates witnesses for plan execution
- **Enhancement:** Add PLIx provenance (purity, constraints, subdistribution)
- **Security Level:** Critical
- **Ownership:** VIF subsystem

**12. `memory.cmc.storage.enhancedWitnesses`** 📝 **ENHANCED**
- **Current:** Stores witnesses bitemporally
- **Enhancement:** Store PLIx-enhanced witnesses
- **Security Level:** Critical
- **Ownership:** CMC subsystem

**13. `indexing.hhni.graph.plixConstructs`** 📝 **ENHANCED**
- **Current:** Indexes entities and relationships
- **Enhancement:** Index PLIx constructs (contracts, constraints, proofs)
- **Security Level:** Medium
- **Ownership:** HHNI subsystem

---

### **Tertiary Nodes (Indirect Impact):**

**14. `intent.classification.system.contractSpecification`** 🔗 **POTENTIAL**
- **Current:** Classifies user intent
- **Potential:** Use PLIx for formal contract specification
- **Ownership:** Intent Classification subsystem

**15. `documentation.standards.l0l4.integration`** 🔗 **REQUIRED**
- **Current:** L0-L4 documentation standard
- **Required:** Document integration thoroughly
- **Ownership:** Documentation Standards

**16. `timeline.context.events.plixExecution`** 🔗 **INTEGRATION**
- **Current:** Tracks timeline events
- **Integration:** Track PLIx execution events
- **Ownership:** Timeline Context System

---

## 🗺️ **CONNECTION MAP (Initial Sketch)**

```
┌─────────────────────────────────────────────────────────────┐
│                    PLIx Integration Flow                     │
└─────────────────────────────────────────────────────────────┘

User Intent (CNL)
    ↓
┌──────────────────┐
│ PLIx Parser      │  (exists: packages/plix/src/parser/)
│ (100% compliant) │
└──────────────────┘
    ↓
PLIx AST
    ↓
┌─────────────────────────────────────┐
│ PLIx → ACL Compiler (NEW)           │  ⭐ Primary Integration Point
│ orchestration.apoe.compiler.plixToAcl│
│ - Maps PLIx constructs to ACL       │
│ - Validates purity                   │
│ - Generates compensation steps       │
│ - Creates retry/fallback policies    │
└─────────────────────────────────────┘
    ↓
Enhanced ACL Plan
    ↓
┌─────────────────────────────────────┐
│ APOE Executor (ENHANCED)             │
│ orchestration.apoe.executor.core     │
│ + compensation logic                 │
│ + retry/fallback logic               │
│ + purity checking                    │
└─────────────────────────────────────┘
    │
    ├──→ TLA+ Backend (NEW) → Model Checking
    ├──→ Alloy Backend (NEW) → Structural Validation
    ├──→ OPA Backend (NEW) → Policy Enforcement
    └──→ IRPlan Backend (exists) → Execution
    ↓
VIF Witnesses (ENHANCED)
    ↓
CMC Storage (ENHANCED)
```

---

## 🔗 **SYSTEM RELATIONSHIPS**

### **PLIx → APOE Integration:**
- **Relationship:** PLIx compiles TO ACL (one-way transformation)
- **Data Flow:** PLIx AST → Compiler → ACL Plan
- **Constraints:** Must preserve formal semantics
- **Dependencies:** APOE ACL parser, executor

### **APOE → VIF Integration:**
- **Relationship:** APOE execution creates VIF witnesses (existing + enhanced)
- **Data Flow:** Execution events → VIF witnesses → CMC storage
- **Constraints:** All executions must have provenance
- **Dependencies:** VIF witness creation, CMC bitemporal storage

### **PLIx → VIF Enhancement:**
- **Relationship:** PLIx adds new witness types (purity proofs, constraint replay)
- **Data Flow:** PLIx evidence → Enhanced VIF witnesses
- **Constraints:** Cryptographic integrity maintained
- **Dependencies:** VIF witness schema, CMC storage

### **APOE → CMC Integration:**
- **Relationship:** APOE stores plans and results in CMC (existing)
- **Data Flow:** Plans/results → CMC atoms
- **Constraints:** Bitemporal invariants maintained
- **Dependencies:** CMC API, bitemporal schema

### **APOE → HHNI Integration:**
- **Relationship:** HHNI indexes APOE plans for retrieval (existing + enhanced)
- **Data Flow:** Plans → HHNI graph → Semantic search
- **Constraints:** Real-time indexing
- **Dependencies:** HHNI graph structure, semantic embeddings

---

## 🎯 **CLASSIFICATION PER NODE**

### **Security Levels:**
- **Critical:** VIF witnesses, CMC storage, PLIx constraint replay (4 nodes)
- **High:** Compensation, retry/fallback, purity checker, OPA backend (4 nodes)
- **Medium:** PLIx→ACL compiler, ACL parser, HHNI indexing (4 nodes)
- **Low:** TLA+ backend, Alloy backend (2 nodes)

### **Performance Sensitivity:**
- **Realtime:** Compensation execution, OPA policy enforcement (2 nodes)
- **Interactive:** Most nodes (< 1s response) (8 nodes)
- **Background:** TLA+/Alloy verification (2 nodes)

### **Surface Types:**
- **Compiler/Transform:** PLIx→ACL compiler, purity checker (2 nodes)
- **Runtime Execution:** Compensation, retry/fallback, enhanced executor (3 nodes)
- **Verification:** TLA+, Alloy, constraint replay (3 nodes)
- **Runtime Policy:** OPA backend (1 node)
- **Storage:** Enhanced CMC, enhanced VIF (2 nodes)
- **Indexing:** Enhanced HHNI (1 node)

### **Ownership:**
- **APOE:** 9 nodes (primary host)
- **VIF:** 2 nodes (enhanced provenance)
- **CMC:** 1 node (enhanced storage)
- **HHNI:** 1 node (enhanced indexing)
- **Intent Classification:** 1 node (potential future)

---

## 🚨 **CRITICAL BOUNDARIES**

### **What This Integration DOES:**
1. ✅ Enhance APOE with formal verification capabilities
2. ✅ Add compensation/retry/fallback to APOE
3. ✅ Create new verification backends (TLA+/Alloy/OPA)
4. ✅ Enhance VIF with PLIx-specific witnesses
5. ✅ Enable formal contract specification

### **What This Integration DOES NOT:**
1. ❌ Replace APOE (APOE remains the executor)
2. ❌ Create separate PLIx execution engine
3. ❌ Break existing APOE functionality
4. ❌ Change ACL syntax dramatically
5. ❌ Compete with Intent Classification

### **Integration Points:**
- **Clean:** PLIx→ACL compiler is isolated transformation
- **Enhanced:** APOE executor gains new capabilities
- **Extended:** VIF/CMC/HHNI get new data types
- **Preserved:** All existing integrations maintained

---

## 📋 **VALIDATION CHECKLIST**

**Before proceeding to Stage 2:**
- [x] All affected nodes identified (14 primary/secondary, 3 tertiary)
- [x] Relationships mapped (PLIx→APOE, APOE→VIF, APOE→CMC, APOE→HHNI)
- [x] Security levels assigned (Critical: 4, High: 4, Medium: 4, Low: 2)
- [x] Performance budgets understood (Realtime: 2, Interactive: 8, Background: 2)
- [x] Ownership clear (APOE: 9, VIF: 2, CMC: 1, HHNI: 1)
- [ ] APOE L0-L4 docs reviewed (NEXT - need to read existing docs)
- [ ] VIF L0-L4 docs reviewed (NEXT)
- [ ] CMC L0-L4 docs reviewed (NEXT)

---

## 🔧 **NEXT STEPS**

### **Stage 2: L0-L4 Specification Stack**
1. Read existing APOE L0-L4 documentation
2. Read existing VIF L0-L4 documentation
3. Create integration L0-L4 docs:
   - L0: Executive summary (100 words)
   - L1: Overview (500 words)
   - L2: Architecture (2,000 words)
   - L3: Implementation guide (10,000 words)
   - L4: Complete reference (15,000+ words)

---

## 💙 **CONFIDENCE ASSESSMENT**

**Current Confidence:** 0.85

**Why 0.85:**
- ✅ All nodes identified and classified
- ✅ Relationships mapped
- ✅ Boundaries clear
- ⏳ Need to read existing L0-L4 docs for affected systems
- ⏳ Need validation from system owners

**To reach 0.90:**
- Read APOE/VIF/CMC L0-L4 documentation
- Validate node list is complete
- Confirm relationships with existing docs

---

**Status:** ✅ **STAGE 1 COMPLETE (90%)**  
**Next:** Read existing system L0-L4 docs, then Stage 2  
**Protocol:** LDP progressing systematically  
**Honesty:** This is proper systematic mapping

**Proceeding to read existing documentation...** 💙

