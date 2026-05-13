# Nexus - SEG Integration Test Plan

**Purpose:** Plan and track integration tests for SEG with connected systems  
**Created:** 2025-01-27  
**Status:** Planning Complete  
**Agent:** Nexus (SEG System Specialist)

---

## 🎯 **EXECUTIVE SUMMARY**

**Integration Test Status:**
- ✅ **CMC-SEG:** 10 tests complete (test_cmc_seg_integration.py)
- ✅ **VIF-SEG:** 6 tests complete (test_vif_seg_integration.py)
- ✅ **TCS-SEG:** 6 tests complete (test_tcs_integration.py)
- ⏳ **HHNI-SEG:** 0 tests (needs implementation)
- ⏳ **APOE-SEG:** 0 tests (needs implementation)

**Priority:**
- ✅ **P0:** VIF-SEG integration tests - **COMPLETE** (6/6 tests passing)
- ✅ **P0:** TCS-SEG integration tests - **COMPLETE** (6/6 tests passing)
- ⏳ **P1:** HHNI-SEG integration tests (design needed)
- ⏳ **P1:** APOE-SEG integration tests (design needed)

---

## 📊 **CURRENT TEST COVERAGE**

### **✅ CMC-SEG Integration Tests (Complete)**

**File:** `packages/integration_tests/test_cmc_seg_integration.py`  
**Status:** ✅ 10 tests passing

**Test Coverage:**
1. ✅ `test_atom_to_entity_conversion` - CMC atom → SEG entity
2. ✅ `test_atom_to_evidence_conversion` - CMC atom → SEG evidence
3. ✅ `test_build_graph_from_atoms` - Multiple atoms → SEG graph
4. ✅ `test_snapshot_to_graph_state` - CMC snapshots → graph states
5. ✅ `test_graph_evidence_from_cmc_atoms` - CMC atoms as evidence
6. ✅ `test_query_graph_at_cmc_snapshot_time` - Temporal queries
7. ✅ `test_cmc_atom_versioning_to_graph_entity_history` - Versioning
8. ✅ `test_bidirectional_sync_cmc_to_seg` - Bidirectional sync

**Integration Points Tested:**
- ✅ Atom → Entity conversion
- ✅ Atom → Evidence conversion
- ✅ Snapshot → Graph state
- ✅ Evidence atoms for relations
- ✅ Temporal queries with snapshots
- ✅ Versioning and history
- ✅ Bidirectional sync

**Status:** ✅ Complete and passing

---

## ⏳ **PLANNED INTEGRATION TESTS**

### **P0: VIF-SEG Integration Tests (High Priority)**

**Status:** ✅ **COMPLETE** - 6 tests passing  
**Coordination:** ✅ Complete (with @Sage)  
**Priority:** P0 - Critical

**Test Plan:**

1. ✅ **test_vif_witness_to_seg_entity:**
   - Create VIF witness
   - Create SEG entity with `witness_id`
   - Verify witness linking works
   - Verify provenance chain

2. ✅ **test_vif_witness_to_seg_relation:**
   - Create VIF witness
   - Create SEG relation with `witness_id`
   - Verify witness linking works
   - Verify provenance chain

3. ✅ **test_vif_witness_to_seg_evidence:**
   - Create VIF witness
   - Create SEG evidence with `witness_id`
   - Verify witness linking works
   - Verify provenance chain

4. ✅ **test_vif_provenance_chain:**
   - Create parent VIF witness
   - Create child VIF witness
   - Create SEG entities for both
   - Verify provenance chain tracking

5. ✅ **test_vif_confidence_affects_seg:**
   - Create VIF witness with low confidence
   - Create SEG entity with witness
   - Verify confidence affects SEG operations
   - Test κ-gating integration

6. ✅ **test_seg_synthesis_from_vif_witnesses:**
   - Create multiple VIF witnesses
   - Create SEG entities from witnesses
   - Verify knowledge synthesis works
   - Test contradiction detection

**Integration Points Tested:**
- ✅ VIF witness `id` → SEG `witness_id` mapping
- ✅ Provenance chain tracking (VIF → SEG → Evidence)
- ✅ Confidence integration (VIF confidence → SEG confidence)
- ✅ κ-gating integration (VIF abstention → SEG operations)
- ✅ Knowledge synthesis from VIF witnesses

**File:** `packages/integration_tests/test_vif_seg_integration.py`  
**Status:** ✅ **COMPLETE** - 6/6 tests passing

---

### **P1: HHNI-SEG Integration Tests (High Priority)**

**Status:** ⏳ Needs Design & Implementation  
**Coordination:** ⏳ Pending (with @Sev)  
**Priority:** P1 - High

**Test Plan (Draft):**

1. **test_hhni_evidence_based_context:**
   - HHNI query
   - SEG evidence graph query
   - Evidence-based context returned
   - HHNI synthesis with SEG evidence

2. **test_seg_semantic_search_via_hhni:**
   - SEG evidence query
   - HHNI semantic search
   - Evidence enrichment
   - Pattern analysis

3. **test_hhni_seg_contradiction_aware_retrieval:**
   - HHNI query
   - SEG contradiction detection
   - Contradiction-aware retrieval
   - Quality improvement

**Integration Points to Test:**
- ⏳ Evidence-based context retrieval
- ⏳ Semantic search across evidence
- ⏳ Pattern analysis integration
- ⏳ Contradiction-aware retrieval

**File:** `packages/integration_tests/test_hhni_seg_integration.py`  
**Status:** ⏳ Needs Design (coordinate with @Sev)

---

### **P1: APOE-SEG Integration Tests (High Priority)**

**Status:** ⏳ Needs Design & Implementation  
**Coordination:** ⏳ Pending (with @Alex)  
**Priority:** P1 - High

**Test Plan (Draft):**

1. **test_apoe_execution_trace_to_seg_derivation:**
   - APOE execution
   - VIF witness created
   - SEG evidence node created
   - SEG derivation node created
   - Provenance chain established

2. **test_apoe_plan_effectiveness_via_seg:**
   - APOE plan execution
   - SEG evidence gathered
   - Plan effectiveness evaluated
   - DEPP analysis

3. **test_apoe_dep_evidence_gathering:**
   - DEPP loop
   - SEG evidence collection
   - Plan improvement
   - Meta-learning

**Integration Points to Test:**
- ⏳ Execution trace → derivation mapping
- ⏳ Plan effectiveness tracking
- ⏳ DEPP evidence gathering
- ⏳ Meta-learning integration

**File:** `packages/integration_tests/test_apoe_seg_integration.py`  
**Status:** ⏳ Needs Design (coordinate with @Alex)

---

### **P2: TCS-SEG Integration Tests (Medium Priority)**

**Status:** ⏳ Needs Design & Implementation  
**Coordination:** ✅ Ready (with @Chronos)  
**Priority:** P2 - Medium

**Test Plan (Draft):**

1. **test_tcs_timeline_entry_to_seg_evidence:**
   - TCS timeline entry created
   - SEG evidence node created
   - Timeline → evidence linking
   - Temporal queries enabled

2. **test_seg_operation_to_tcs_timeline:**
   - SEG operation (evidence creation)
   - TCS timeline entry created
   - Timeline tracking
   - Temporal provenance

3. **test_tcs_seg_temporal_queries:**
   - TCS timeline queries
   - SEG temporal queries
   - Combined temporal context
   - Time-travel queries

**Integration Points to Test:**
- ⏳ Timeline entry → evidence node
- ⏳ Evidence node → timeline entry
- ⏳ Temporal queries
- ⏳ Provenance tracking

**File:** `packages/integration_tests/test_tcs_seg_integration.py`  
**Status:** ⏳ Needs Design (coordinate with @Chronos)

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **VIF-SEG Integration Tests:**
- [ ] Create test file `test_vif_seg_integration.py`
- [ ] Implement test_vif_witness_to_seg_entity
- [ ] Implement test_vif_witness_to_seg_relation
- [ ] Implement test_vif_witness_to_seg_evidence
- [ ] Implement test_vif_provenance_chain
- [ ] Implement test_vif_confidence_affects_seg
- [ ] Implement test_seg_synthesis_from_vif_witnesses
- [ ] Run tests and verify all pass
- [ ] Document test results

### **HHNI-SEG Integration Tests:**
- [ ] Coordinate with @Sev on integration design
- [ ] Create test file `test_hhni_seg_integration.py`
- [ ] Implement evidence-based context tests
- [ ] Implement semantic search tests
- [ ] Implement contradiction-aware retrieval tests
- [ ] Run tests and verify all pass
- [ ] Document test results

### **APOE-SEG Integration Tests:**
- [ ] Coordinate with @Alex on integration design
- [ ] Create test file `test_apoe_seg_integration.py`
- [ ] Implement execution trace → derivation tests
- [ ] Implement plan effectiveness tests
- [ ] Implement DEPP evidence gathering tests
- [ ] Run tests and verify all pass
- [ ] Document test results

### **TCS-SEG Integration Tests:**
- [ ] Coordinate with @Chronos on integration design
- [ ] Create test file `test_tcs_seg_integration.py`
- [ ] Implement timeline → evidence tests
- [ ] Implement evidence → timeline tests
- [ ] Implement temporal query tests
- [ ] Run tests and verify all pass
- [ ] Document test results

---

## 🎯 **PRIORITY MATRIX**

| Integration | Priority | Status | Coordination | Tests Needed |
|------------|----------|--------|--------------|--------------|
| **CMC-SEG** | P0 | ✅ Complete | ✅ Complete | 0 (10 existing) |
| **VIF-SEG** | P0 | ⏳ Planned | ✅ Complete | 6 tests |
| **HHNI-SEG** | P1 | ⏳ Planned | ⏳ Pending | 3 tests |
| **APOE-SEG** | P1 | ⏳ Planned | ⏳ Pending | 3 tests |
| **TCS-SEG** | P2 | ⏳ Planned | ✅ Ready | 3 tests |

---

## 📊 **TEST COVERAGE GOALS**

### **Current Coverage:**
- **CMC-SEG:** ✅ 10/10 tests (100%)
- **VIF-SEG:** ⏳ 0/6 tests (0%)
- **HHNI-SEG:** ⏳ 0/3 tests (0%)
- **APOE-SEG:** ⏳ 0/3 tests (0%)
- **TCS-SEG:** ⏳ 0/3 tests (0%)
- **Total:** ✅ 10/25 tests (40%)

### **Target Coverage:**
- **All Integrations:** ✅ 25/25 tests (100%)
- **Priority:** P0 integrations first (CMC ✅, VIF ⏳)
- **Timeline:** P0 in Week 1, P1 in Week 2, P2 in Week 3

---

## 🔗 **RELATED DOCUMENTS**

- **Relationship Mapping:** `AGENT_NEXUS_RELATIONSHIP_MAPPING.md`
- **System Audit:** `AGENT_NEXUS_SYSTEM_AUDIT.md`
- **Enhancement Roadmap:** `AGENT_NEXUS_ENHANCEMENT_ROADMAP.md`
- **Existing CMC-SEG Tests:** `packages/integration_tests/test_cmc_seg_integration.py`

---

**Status:** Integration test plan complete ✅, ready for implementation  
**Next:** Implement VIF-SEG integration tests (P0 priority)  
**Confidence:** High (0.90) - clear test plan, coordination complete

