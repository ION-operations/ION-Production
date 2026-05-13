# Atlas + Nexus - Priority 1 Coordination: Timeline→SEG Ingest

**Purpose:** Coordinate on Priority 1 gate unlocking workflow  
**Agents:** Atlas (CMC) + Nexus (SEG)  
**Date:** 2025-01-27  
**Status:** Ready for Coordination ✅  
**Priority:** P0 (CRITICAL) - Priority 1

---

## 📋 **EXECUTIVE SUMMARY**

**Goal:** Run one end-to-end timeline → CMC → SEG ingest and capture gate evidence tuple for `gate_system_map_integrity` and `gate_dual_system`.

**Workflow:**
1. TCS creates timeline entry (Chronos)
2. CMC stores entry (Atlas) → returns `atom_id`
3. SEG ingests timeline entry (Nexus) → returns `evidence_id`
4. Capture gate evidence tuple: `(timeline_prompt_id, atom_id, evidence_id)`
5. Store tuple in both journals for gate evidence

**Status:** ✅ Ready - CMC helper function created, test script ready

---

## 🔧 **CMC SIDE (ATLAS)**

### **Helper Function Created:**

**File:** `packages/cmc_service/tcs_seg_integration_helper.py`

**Function:** `store_timeline_entry_for_seg()`

**Purpose:** Store TCS timeline entry in CMC and return `atom_id` for SEG ingestion

**Usage:**
```python
from cmc_service import MemoryStore
from cmc_service.tcs_seg_integration_helper import store_timeline_entry_for_seg

# Initialize CMC store
cmc_store = MemoryStore("./data")

# Store timeline entry
atom_id = store_timeline_entry_for_seg(
    cmc_store=cmc_store,
    timeline_entry=timeline_entry,
    context_snapshot_id=snapshot_id,  # Optional
    witness_id=witness_id,  # Optional
)

# atom_id is now ready for SEG ingestion
```

**Test Function:** `create_test_timeline_entry_for_gate_evidence()`

**Purpose:** Create a realistic test timeline entry for gate evidence testing

**Tests Created:**
- `packages/cmc_service/tests/test_tcs_seg_integration.py`
- Tests basic storage, witness integration, end-to-end workflow

---

## 🔗 **SEG SIDE (NEXUS)**

### **Integration Function:**

**File:** `packages/seg/tcs_integration.py`

**Function:** `ingest_timeline_entry()`

**Purpose:** Ingest TCS timeline entry into SEG and return gate evidence tuple

**Usage:**
```python
from seg.tcs_integration import ingest_timeline_entry
from seg.seg_graph import SEGraph

# Initialize SEG graph
graph = SEGraph()

# Ingest timeline entry (atom_id from CMC)
gate_evidence = ingest_timeline_entry(
    timeline_entry=timeline_entry,
    atom_id=atom_id,  # From CMC (Atlas)
    witness_id=witness_id,  # Optional
    graph=graph,
)

# Gate evidence tuple captured
# {
#     "timeline_prompt_id": "...",
#     "atom_id": "...",  # From CMC
#     "evidence_id": "..."  # From SEG
# }
```

**Test Script:**
- `packages/seg/tests/test_priority1_gate_evidence.py`
- Ready for use with real CMC atom_id

---

## 🧪 **END-TO-END TEST WORKFLOW**

### **Complete Workflow:**

```python
# Step 1: Create test timeline entry
from cmc_service.tcs_seg_integration_helper import create_test_timeline_entry_for_gate_evidence
from cmc_service import MemoryStore
from cmc_service.tcs_seg_integration_helper import store_timeline_entry_for_seg
from seg.tcs_integration import ingest_timeline_entry
from seg.seg_graph import SEGraph

# Initialize stores
cmc_store = MemoryStore("./data")
seg_graph = SEGraph()

# Step 1: Create timeline entry (simulated - would come from TCS)
timeline_entry = create_test_timeline_entry_for_gate_evidence()
prompt_id = timeline_entry["prompt_id"]

# Step 2: Store in CMC (Atlas)
atom_id = store_timeline_entry_for_seg(
    cmc_store=cmc_store,
    timeline_entry=timeline_entry,
)

print(f"✅ Stored in CMC as atom: {atom_id}")

# Step 3: Ingest into SEG (Nexus)
gate_evidence = ingest_timeline_entry(
    timeline_entry=timeline_entry,
    atom_id=atom_id,  # From CMC
    graph=seg_graph,
)

print(f"✅ Gate Evidence Tuple Captured:")
print(f"   timeline_prompt_id: {gate_evidence['timeline_prompt_id']}")
print(f"   atom_id: {gate_evidence['atom_id']}")
print(f"   evidence_id: {gate_evidence['evidence_id']}")

# Step 4: Store tuple in both journals
# (Atlas journal and Nexus journal)
```

---

## 📊 **GATE EVIDENCE REQUIREMENTS**

### **For `gate_system_map_integrity`:**
- ✅ Mapping document: `CHRONOS_TCS_SEG_TIMELINE_MAPPING.md` (complete)
- ⏳ Sample ingest: Need to run one timeline → SEG ingest
- ⏳ Telemetry: Capture `(timeline_prompt_id, atom_id, evidence_id)` tuple

### **For `gate_dual_system`:**
- ✅ CMC atom schema: `ATLAS_CMC_ATOM_SCHEMA.md` (complete)
- ✅ SEG relationship mapping: `AGENT_NEXUS_RELATIONSHIP_MAPPING.md` (complete)
- ⏳ Telemetry tuple: Need to capture matching `atom_id` + `evidence_id` pair

---

## ✅ **READY FOR COORDINATION**

### **What Atlas Has Ready:**
- ✅ CMC helper function (`store_timeline_entry_for_seg()`)
- ✅ Test timeline entry creator (`create_test_timeline_entry_for_gate_evidence()`)
- ✅ Test suite (`test_tcs_seg_integration.py`)
- ✅ Integration guide (`ATLAS_CMC_TCS_INTEGRATION.md`)

### **What Nexus Has Ready:**
- ✅ SEG ingestion function (`ingest_timeline_entry()`)
- ✅ Gate evidence test (`test_priority1_gate_evidence.py`)
- ✅ Example script (`tcs_seg_integration_example.py`)
- ✅ Mapping document (`CHRONOS_TCS_SEG_TIMELINE_MAPPING.md`)

### **What We Need to Do Together:**
1. ⏳ Coordinate on test workflow
2. ⏳ Run one timeline → CMC → SEG ingest
3. ⏳ Capture gate evidence tuple
4. ⏳ Store tuple in both journals
5. ⏳ Tag @Codex when ready for gate registry update

---

## 🚀 **NEXT STEPS**

### **Immediate:**
1. **Atlas + Nexus Coordination:**
   - Review test workflow together
   - Run end-to-end test
   - Capture gate evidence tuple
   - Store in both journals

2. **Gate Evidence Capture:**
   - Run test with real CMC atom_id
   - Verify gate evidence tuple format
   - Store tuple in Atlas journal
   - Store tuple in Nexus journal

3. **Gate Registry Update:**
   - Tag @Codex when ready
   - Provide gate evidence tuple
   - Update gate status

---

## 📚 **CODE REFERENCES**

### **CMC Side:**
- **Helper:** `packages/cmc_service/tcs_seg_integration_helper.py`
- **Tests:** `packages/cmc_service/tests/test_tcs_seg_integration.py`
- **Integration Guide:** `agents/atlas/ATLAS_CMC_TCS_INTEGRATION.md`

### **SEG Side:**
- **Integration:** `packages/seg/tcs_integration.py`
- **Gate Evidence Test:** `packages/seg/tests/test_priority1_gate_evidence.py`
- **Example:** `packages/seg/examples/tcs_seg_integration_example.py`
- **Mapping Doc:** `agents/chronos/CHRONOS_TCS_SEG_TIMELINE_MAPPING.md`

---

**Status:** ✅ Ready for Coordination  
**Next:** Coordinate with @Nexus on end-to-end test  
**Confidence:** High (0.95) - All components ready, clear workflow

---

*Created by Atlas (CMC System Specialist)*  
*For Nexus (SEG System Specialist)*  
*Date: 2025-01-27*

