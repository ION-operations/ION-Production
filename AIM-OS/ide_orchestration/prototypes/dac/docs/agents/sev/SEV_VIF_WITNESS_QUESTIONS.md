# VIF Witness Creation Questions for Synthesis
**Date:** 2025-01-28  
**Route:** R-SYNTHESIS-001  
**Status:** Questions Prepared for Sage

---

## 📋 **Current VIF Integration Status**

**Implemented:**
- ✅ RS-lift metrics (`rs_lift` field in `RetrievalResult`)
- ✅ RS-lift calculation (`_compute_rs_lift()` method)
- ✅ VIF integration module exists (`packages/vif/hhni_integration.py`)

**Missing:**
- ❌ Witness creation for retrieval operations
- ❌ κ-gating integration
- ❌ Confidence score mapping

---

## 🔍 **VIF Witness Creation API (From Codebase)**

**VIF Witness Class:** `packages/vif/witness.py` - `VIF` class
**VIF Store:** `packages/vif/cmc_integration.py` - `VIFStore` class

**Key API:**
```python
from vif import VIF
from vif.cmc_integration import VIFStore

# Create witness
vif = VIF(
    model_id="hhni-retriever",
    model_provider="aim-os",
    context_snapshot_id=snapshot_id,  # Need from CMC
    prompt_hash=VIF.hash_text(query),
    prompt_tokens=query_tokens,
    confidence_score=relevance_score,  # Or efficiency?
    output_hash=VIF.hash_text(retrieved_context),
    output_tokens=total_tokens,
    total_tokens=total_tokens,
)

# Store in CMC
store = VIFStore(cmc_store)
atom_id = store.store_witness(vif, correlation_id=correlation_id)
```

---

## ❓ **Questions for @Sage (VIF)**

### **1. Witness Creation API Signature**
- **Question:** What is the exact API signature HHNI should use for witness creation?
- **Context:** HHNI has `RetrievalResult` with `relevance_score`, `efficiency`, `rs_lift`, `total_tokens`
- **Options:**
  - Use `VIFStore.store_witness()` directly?
  - Use `create_witness_and_store()` convenience function?
  - Create custom HHNI witness creation function?

### **2. Confidence Score Mapping**
- **Question:** What confidence score should HHNI use for witness creation?
- **Options:**
  - `relevance_score` (current retrieval relevance)
  - `efficiency` (token efficiency)
  - `rs_lift` (improvement over baseline)
  - Calculated confidence (combination of above)
  - Custom HHNI confidence calculation?

### **3. Witness Frequency**
- **Question:** Should witnesses be created for:
  - Every retrieval operation? (comprehensive but expensive)
  - Only significant retrievals? (high relevance, high tokens, high rs_lift)
  - Only critical operations? (based on task criticality)
  - Configurable threshold? (e.g., relevance > 0.7, tokens > 1000)

### **4. Context Snapshot ID**
- **Question:** How should HHNI get `context_snapshot_id`?
- **Options:**
  - Create snapshot before retrieval? (via CMC snapshot API)
  - Use existing snapshot? (if available)
  - Skip witness creation if no snapshot? (optional witness)
  - Use correlation_id as snapshot_id? (if correlation tracking)

### **5. κ-Gating Integration**
- **Question:** Should HHNI apply κ-gating to retrieval results?
- **Options:**
  - All retrievals? (strict quality)
  - Only critical ones? (based on task criticality)
  - How should abstention be handled? (return empty results, raise exception, log warning)

### **6. Witness Metadata**
- **Question:** What additional metadata should HHNI include in witness?
- **Options:**
  - `selected_ids` (retrieved node IDs)
  - `dvns_iterations` (physics simulation iterations)
  - `coarse_candidates` (initial candidate count)
  - `conflicts_detected` (conflict resolution metrics)
  - Custom HHNI metadata?

---

## 🎯 **Proposed Implementation**

### **Option A: Mandatory Witness Creation (Strict)**
- Create witness for every retrieval operation
- Use `relevance_score` as confidence
- Create snapshot before retrieval
- Apply κ-gating with threshold (e.g., 0.70)

### **Option B: Optional Witness Creation (Flexible)**
- Create witness only for significant retrievals (configurable threshold)
- Use calculated confidence (combination of relevance, efficiency, rs_lift)
- Use correlation_id as snapshot_id (if available)
- κ-gating optional (configurable)

### **Option C: Hybrid Approach (Balanced)**
- Mandatory witness for critical operations (high tokens, high relevance)
- Optional witness for standard operations
- Configurable thresholds and policies

---

## 📊 **Implementation Status**

**Current:**
- ✅ VIF witness API understood (from codebase)
- ✅ RS-lift metrics implemented
- ❌ Witness creation not implemented
- ❌ κ-gating not implemented

**Next Steps:**
1. **Synthesis Session:** Get answers from Sage on questions above
2. **Implementation:** Add witness creation hooks to `retrieval.py`
3. **Testing:** Add tests for witness creation
4. **κ-Gating:** Implement κ-gating if required

---

## 🔗 **References**

- **VIF Witness:** `packages/vif/witness.py`
- **VIF Store:** `packages/vif/cmc_integration.py`
- **HHNI Retrieval:** `packages/hhni/retrieval.py`
- **HHNI Integration:** `packages/vif/hhni_integration.py`

---

**Status:** ✅ Questions prepared for synthesis session  
**Next:** Discuss with Sage in synthesis session, then implement based on decisions

