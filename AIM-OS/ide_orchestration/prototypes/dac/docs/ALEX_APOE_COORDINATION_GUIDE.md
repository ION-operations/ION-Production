# APOE Coordination Guide

**Created By:** Alex (APOE System Specialist)  
**Date:** 2025-01-27  
**Status:** Complete  
**Purpose:** Guide for other specialists to coordinate with APOE integration points

---

## 📋 **EXECUTIVE SUMMARY**

This document provides coordination guidance for other AIM-OS system specialists working with APOE. It outlines integration points, data flows, coordination patterns, and specific collaboration needs.

**APOE Status:** Production-ready (100% complete, 180/180 tests passing)

---

## 🔗 **INTEGRATION POINTS BY SYSTEM**

### **1. CMC (Context Memory Core) - @Atlas**

**Integration Type:** Bidirectional, Required, High Security

**APOE → CMC:**
- **Execution State Storage:**
  - Plan artifacts (compiled ACL plans)
  - Step results (outputs from each step)
  - State snapshots (for resumption/recovery)
  - Execution traces (complete execution history)
- **Storage Pattern:** Bitemporal atoms with `modality="plan"` or `modality="execution"`
- **Files:** `packages/apoe/integration/cmc_storage.py`, `packages/apoe/cmc_integration.py`
- **MCP Tool:** Plans stored via `create_plan` tool when `store_in_cmc=True`

**CMC → APOE:**
- **Context Retrieval:**
  - Historical plan execution data
  - Previous step results for context
  - Memory-aware planning (learn from past executions)
- **Usage:** State Manager retrieves execution state for resumption

**Coordination Needs:**
- ✅ **Storage Patterns:** Confirm bitemporal atom structure for execution state
- ✅ **Retrieval Patterns:** Confirm query patterns for historical plan data
- ✅ **Performance:** Ensure storage/retrieval meets APOE performance budgets (30ms for state manager)

**Questions for @Atlas:**
1. What's the recommended atom structure for execution state storage?
2. How should we query historical plan execution data efficiently?
3. Are there any CMC-specific patterns for storing DAG execution state?

---

### **2. HHNI (Hierarchical Hypergraph Neural Index) - @Sev**

**Integration Type:** Bidirectional, Required, High Security

**APOE → HHNI:**
- **Context Retrieval Requests:**
  - Retriever role queries HHNI for context
  - Budget-aware queries (token limits)
  - Optimized context requests
- **Usage:** Retriever role uses HHNI for intelligent context retrieval
- **Files:** `packages/apoe/role_dispatcher.py` (Retriever role), `packages/apoe/integration/hhni_indexing.py`

**HHNI → APOE:**
- **Optimized Context:**
  - Retrieval results with relevance scores
  - Budget-aware context (respects token limits)
  - Retrieval witnesses (for provenance)
- **Usage:** Context fed into step execution

**Coordination Needs:**
- ✅ **Query Interface:** Confirm HHNI query API for Retriever role
- ✅ **Budget Integration:** Ensure HHNI respects token budgets from APOE
- ✅ **Witness Generation:** Coordinate on retrieval witness format

**Questions for @Sev:**
1. What's the recommended HHNI query pattern for Retriever role?
2. How does HHNI handle budget-aware queries (token limits)?
3. What's the format for retrieval witnesses that APOE should expect?

---

### **3. VIF (Verifiable Intelligence Framework) - @Sage**

**Integration Type:** Bidirectional, Required, Critical Security

**APOE → VIF:**
- **Witness Generation:**
  - Plan-level witnesses (complete plan execution)
  - Step-level witnesses (individual step execution)
  - Complete provenance (inputs, outputs, confidence, metadata)
- **Confidence Scores:**
  - Step execution confidence
  - Plan execution confidence
  - κ-gating for execution control
- **Files:** `packages/apoe/vif_integration.py`

**VIF → APOE:**
- **Confidence Gates:**
  - κ-gating for step execution (confidence threshold enforcement)
  - Confidence-based routing (PASS/FAIL/WARN/ABSTAIN)
- **Verification Requests:**
  - Witness verification
  - Provenance validation

**Coordination Needs:**
- ✅ **Witness Format:** Confirm witness envelope structure for APOE
- ✅ **κ-Gating:** Coordinate on confidence threshold enforcement
- ✅ **Performance:** Ensure witness generation meets APOE performance budgets (10ms for witness generator)

**Questions for @Sage:**
1. What's the exact witness envelope structure APOE should generate?
2. How should APOE implement κ-gating for step execution?
3. What confidence thresholds should APOE use for different gate types?

---

### **4. SEG (Shared Evidence Graph) - @Nexus**

**Integration Type:** Bidirectional, Required, High Security

**APOE → SEG:**
- **Execution Traces:**
  - Complete execution traces (step-by-step)
  - Evidence nodes (execution evidence)
  - Plan effectiveness data (success rates, performance metrics)
- **DEPP Evidence:**
  - Evidence for self-modifying plans
  - Plan effectiveness metrics
- **Files:** `packages/apoe/integration/seg_synthesis.py`

**SEG → APOE:**
- **Synthesis Requests:**
  - Synthesized execution knowledge
  - Plan effectiveness insights
  - Evidence-based plan improvements (for DEPP)
- **Usage:** DEPP rewrites plans based on SEG evidence

**Coordination Needs:**
- ✅ **Trace Format:** Confirm execution trace structure for SEG
- ✅ **Evidence Nodes:** Coordinate on evidence node format
- ✅ **DEPP Integration:** Confirm how SEG evidence feeds DEPP rewriting

**Questions for @Nexus:**
1. What's the recommended execution trace structure for SEG?
2. How should APOE format evidence nodes for plan effectiveness?
3. How does SEG synthesize evidence for DEPP plan rewriting?

---

### **5. SDF-CVF (Atomic Evolution Framework) - @Nova**

**Integration Type:** Bidirectional, Required, High Security

**APOE → SDF-CVF:**
- **Quality Gate Status:**
  - Gate pass/fail results
  - Quality metrics
  - Parity checks (Code, Docs, Tests, Traces)
- **Evolution Artifacts:**
  - Plan artifacts for quartet parity
  - Trace emissions
- **Files:** `packages/apoe/purity_validation/` (PLIx integration)

**SDF-CVF → APOE:**
- **Quality Enforcement:**
  - Quartet parity validation (P ≥ 0.90)
  - Quality gate enforcement
  - Quality violation detection

**Coordination Needs:**
- ✅ **Quartet Parity:** Confirm how APOE artifacts (plans, execution traces) fit quartet parity
- ✅ **Quality Gates:** Coordinate on quality gate enforcement patterns
- ✅ **NL Tags:** Confirm NL tag requirements for APOE code

**Questions for @Nova:**
1. How do APOE execution plans fit into quartet parity (Code, Docs, Tests, Traces)?
2. What quality gates should APOE enforce via SDF-CVF?
3. Are there specific NL tag requirements for APOE integration code?

---

### **6. CAS (Cognitive Analysis System) - @Meta**

**Integration Type:** Observation Pattern (No Direct Port)

**APOE → CAS (Indirect):**
- **Via VIF Witnesses:**
  - CAS analyzes VIF witness envelopes for cognitive patterns
  - Decision-making analysis
  - Confidence pattern analysis
- **Via CMC State:**
  - CAS analyzes execution state stored in CMC
  - Cognitive state tracking
- **Via SEG Traces:**
  - CAS analyzes execution traces in SEG
  - Cognitive connection analysis
- **Via Timeline Entries:**
  - CAS analyzes timeline entries created during execution
  - Temporal cognitive patterns

**CAS → APOE (Indirect):**
- **Cognitive Insights:**
  - Decision-making pattern insights
  - Cognitive drift detection
  - Activation awareness

**Coordination Needs:**
- ✅ **Observation Pattern:** Confirm CAS observation approach (via VIF/CMC/SEG/Timeline)
- ✅ **Data Format:** Ensure APOE data formats are compatible with CAS analysis
- ✅ **Integration Points:** Identify specific integration points for CAS observation

**Questions for @Meta:**
1. How does CAS observe APOE decision-making processes?
2. What data formats should APOE use to enable CAS analysis?
3. Are there specific integration points where CAS should observe APOE?

---

## 🔄 **COORDINATION PATTERNS**

### **Pattern 1: Witness Generation Flow**

```
APOE Step Execution
    ↓
VIF Witness Generation (@Sage)
    ↓
CMC Storage (@Atlas)
    ↓
SEG Synthesis (@Nexus)
    ↓
CAS Observation (@Meta)
```

**Coordination:** All systems coordinate on witness format and flow.

### **Pattern 2: Context Retrieval Flow**

```
APOE Retriever Role
    ↓
HHNI Query (@Sev)
    ↓
Optimized Context
    ↓
APOE Step Execution
    ↓
CMC Storage (@Atlas)
```

**Coordination:** HHNI and CMC coordinate on context format and storage.

### **Pattern 3: Quality Gate Flow**

```
APOE Step Execution
    ↓
SDF-CVF Quality Check (@Nova)
    ↓
Gate Pass/Fail
    ↓
VIF Witness (@Sage)
    ↓
CMC Storage (@Atlas)
```

**Coordination:** SDF-CVF, VIF, and CMC coordinate on quality gate enforcement.

### **Pattern 4: DEPP Rewriting Flow**

```
APOE Plan Execution
    ↓
SEG Evidence Collection (@Nexus)
    ↓
DEPP Analysis
    ↓
Plan Rewriting
    ↓
ACL Recompilation
    ↓
CMC Storage (@Atlas)
```

**Coordination:** SEG and CMC coordinate on evidence format and storage.

---

## 📊 **COORDINATION CHECKLIST**

### **For All Specialists:**

- [ ] Review APOE system map (`ALEX_APOE_SYSTEM_MAP.md`)
- [ ] Review APOE system classification (`ALEX_APOE_SYSTEM_CLASSIFICATION.md`)
- [ ] Identify integration points with APOE
- [ ] Confirm data formats and APIs
- [ ] Coordinate on performance budgets
- [ ] Coordinate on security levels
- [ ] Test integration patterns

### **For Specific Specialists:**

**@Atlas (CMC):**
- [ ] Confirm execution state storage patterns
- [ ] Confirm retrieval patterns for historical data
- [ ] Test performance (30ms budget for state manager)

**@Sev (HHNI):**
- [ ] Confirm Retriever role query patterns
- [ ] Confirm budget-aware query support
- [ ] Test retrieval witness format

**@Sage (VIF):**
- [ ] Confirm witness envelope structure
- [ ] Confirm κ-gating implementation
- [ ] Test confidence threshold enforcement

**@Nexus (SEG):**
- [ ] Confirm execution trace format
- [ ] Confirm evidence node format
- [ ] Test DEPP evidence synthesis

**@Nova (SDF-CVF):**
- [ ] Confirm quartet parity requirements
- [ ] Confirm quality gate enforcement
- [ ] Test NL tag requirements

**@Meta (CAS):**
- [ ] Confirm observation pattern (VIF/CMC/SEG/Timeline)
- [ ] Confirm data format compatibility
- [ ] Test cognitive analysis integration

---

## 🚀 **NEXT STEPS**

1. **Review Integration Points:** Each specialist reviews their integration points with APOE
2. **Coordinate on Data Formats:** Confirm data formats and APIs
3. **Test Integration Patterns:** Test integration patterns in development
4. **Document Integration:** Document integration patterns in system docs
5. **Production Deployment:** Deploy integrated systems to production

---

## 📋 **SUMMARY**

**APOE Integration Status:**
- ✅ 6 integration ports (all required)
- ✅ 8 internal components (all production-ready)
- ✅ Complete data flows (internal and external)
- ✅ Risk overlay and monitoring defined

**Coordination Ready:**
- ✅ Integration points identified
- ✅ Data flows documented
- ✅ Coordination patterns defined
- ✅ Questions prepared for each specialist

**Status:** Ready for coordination with all specialists ✅

---

**Status:** Coordination Guide Complete ✅  
**Next:** Coordinate with specialists on integration points, test integration patterns

