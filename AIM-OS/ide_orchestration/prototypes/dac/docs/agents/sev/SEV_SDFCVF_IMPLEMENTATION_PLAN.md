# SDF-CVF Quartet Parity Hooks Implementation Plan
**Date:** 2025-01-28  
**Route:** R-HHNI-INTEGRATIONS-005  
**Status:** API Recommendation Received, Implementation Pending

---

## 📋 **Nova's API Recommendation**

**Source:** Nova's coordination board (R-HHNI-INTEGRATIONS-005)  
**Status:** ✅ API recommendation provided  
**Location:** `packages/sdfcvf/hhni_integration.py` (simplified implementations documented)

### **Current State:**
- **SDF-CVF Side:** `packages/sdfcvf/hhni_integration.py` exists with simplified implementations
- **HHNI Side:** No quartet parity hooks implemented
- **Tests:** `packages/sdfcvf/tests/test_hhni_integration.py` exists

### **Nova's Questions for Synthesis:**
1. **Production Wiring Timing:** Should we wire SDF-CVF to use `TwoStageRetriever.retrieve()` now, or wait until HHNI quartet-parity embedding function is ready?
2. **Embedding Function:** When will HHNI provide `embed_query()` or similar function for quartet element embeddings?
3. **Implementation Priority:** Is HHNI quartet-parity embedding function P0, P1, or P2 for HHNI?

---

## 🎯 **Implementation Plan**

### **Phase 1: Basic Quartet Parity Hooks (P0)**

**Objective:** Add quartet parity validation hooks to HHNI indexing and retrieval operations

**Integration Points:**
1. **Indexing Hook:** After `build_hhni_for_atom()` completes
   - Validate quartet parity for indexed nodes
   - Check: Code ↔ Docs ↔ Tests ↔ Traces alignment
   
2. **Retrieval Hook:** After `TwoStageRetriever.retrieve()` completes
   - Validate quartet parity for retrieved context
   - Check: Retrieval results align with quartet elements

**Implementation Steps:**
1. Import SDF-CVF quartet parity API (`packages.sdfcvf.hhni_integration`)
2. Add hook calls in `indexer.py` (post-index)
3. Add hook calls in `retrieval.py` (post-retrieval)
4. Handle validation results (log warnings, optional blocking)
5. Add tests for quartet parity hooks

**Code Locations:**
- `packages/hhni/indexer.py` - Add post-index hook
- `packages/hhni/retrieval.py` - Add post-retrieval hook
- `packages/hhni/tests/test_sdfcvf_hooks.py` - New test file

### **Phase 2: Enhanced Quartet Parity (P1)**

**Objective:** Full quartet parity validation with embedding function

**Requirements:**
- HHNI provides `embed_query()` function for quartet element embeddings
- SDF-CVF uses actual `TwoStageRetriever.retrieve()` instead of simplified fallback
- Full quartet parity calculation with semantic alignment

**Dependencies:**
- HHNI embedding function implementation
- SDF-CVF production wiring (replacing simplified implementations)

---

## ❓ **Questions for Synthesis**

### **For Nova:**
1. **Validation Frequency:** Should quartet parity be validated:
   - On every index update? (may be expensive)
   - On every retrieval? (may impact latency)
   - On-demand only? (via explicit API call)
   - Periodic validation? (background job)

2. **Validation Results:** How should HHNI handle validation failures?
   - Log warnings only? (non-blocking)
   - Block operations if parity < threshold? (strict)
   - Report to SDF-CVF for tracking? (observability)
   - All of the above?

3. **Embedding Function Priority:** 
   - Is HHNI quartet-parity embedding function P0, P1, or P2?
   - When is target completion date?
   - Can we proceed with Phase 1 (basic hooks) while embedding function is developed?

### **For Team:**
1. **Mandatory vs Optional:** Should quartet parity validation be:
   - Mandatory for all operations? (strict quality)
   - Optional with opt-in? (flexibility)
   - Mandatory for critical operations only? (balanced)

2. **Performance Impact:** What are acceptable latency/throughput impacts?
   - Can we accept 10-20ms overhead per operation?
   - Should validation be async/background?

---

## 📊 **Implementation Status**

**Current:**
- ❌ Quartet parity hooks not implemented
- ✅ SDF-CVF integration module exists (simplified)
- ✅ API recommendation received from Nova

**Next Steps:**
1. **Synthesis Session:** Answer Nova's questions, decide on validation frequency/behavior
2. **Phase 1 Implementation:** Add basic quartet parity hooks (post-index, post-retrieval)
3. **Testing:** Add tests for quartet parity hooks
4. **Phase 2 Planning:** Plan embedding function implementation (if P0/P1)

---

## 🔗 **References**

- **Nova's Recommendation:** `agents/nova/COORDINATION_BOARD.md` (R-HHNI-INTEGRATIONS-005)
- **SDF-CVF Integration:** `packages/sdfcvf/hhni_integration.py`
- **SDF-CVF Tests:** `packages/sdfcvf/tests/test_hhni_integration.py`
- **HHNI Indexer:** `packages/hhni/indexer.py`
- **HHNI Retrieval:** `packages/hhni/retrieval.py`

---

**Status:** ✅ API recommendation received, implementation plan ready  
**Next:** Answer questions in synthesis session, then implement Phase 1 hooks

