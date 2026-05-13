# Post-Synthesis Action Items
**Date:** 2025-01-28  
**Status:** ⏳ **IN PROGRESS** - Action items assigned  
**Target Completion:** 2025-02-04 (1 week)

---

## 🎯 **Immediate Actions (All Agents)**

### **1. Integration Tagging Standardization**
**Assigned To:** All Agents  
**Priority:** P0  
**Deadline:** 2025-02-01

**Action:**
- Add `metadata.integration_tags` to all integration atom creation
- Format: `["[VIF-WITNESS]", "[HHNI-RETRIEVE]", "[SEG-EVIDENCE]"]`
- When: On atom creation, when integration is significant

**Reference:** Synthesis decision on integration tagging standardization

---

### **2. System Maps/Indexes Alignment**
**Assigned To:** All Agents  
**Priority:** P0  
**Deadline:** 2025-02-01

**Action:**
- Update system maps/indexes with final integration patterns
- Ensure all connections match actual code
- Verify connection matrices are complete

**Reference:** Directive 5 P0 updates

---

### **3. Directive 5 P0 Updates**
**Assigned To:** All Agents  
**Priority:** P0  
**Deadline:** 2025-02-04

**Action:**
- Execute P0 updates from post-consolidation update lists
- Update T-level docs to reflect final contracts
- Align documentation with code

**Reference:** Agent-specific update lists

---

## 🔧 **Agent-Specific Actions**

### **Atlas (CMC)**
**Priority:** P0  
**Deadline:** 2025-02-01

**Actions:**
1. Update CMC integration docs with `metadata.integration_tags` pattern
2. Document tagging format and when to use
3. Update system maps with final integration patterns

**Reference:** `SYNTHESIS_SESSION_EXECUTION_2025-01-28.md` - Question 3

---

### **Sage (VIF)**
**Priority:** P0  
**Deadline:** 2025-02-01

**Actions:**
1. Create VIF orchestration guide with:
   - P0 mandatory witness creation flows
   - κ-gate policies (routine 0.70, critical 0.90, emergency 0.60)
   - Retry heuristics (success_rate thresholds, retry counts)
2. Document P0 vs P1 flows (mandatory vs optional)
3. Update VIF integration docs with orchestration patterns

**Reference:** `SYNTHESIS_SESSION_EXECUTION_2025-01-28.md` - Questions 1 & 2

---

### **Nova (SDF-CVF)**
**Priority:** P0  
**Deadline:** 2025-02-04

**Actions:**
1. Implement P0 SDF-CVF enhancements:
   - HHNI → `TwoStageRetriever.retrieve()` for change context
   - SEG → `SEGraph.add_relation/add_evidence()` for evidence tracking
   - CAS → `FailureModeAnalyzer` / `IntrospectionProtocol` for failure analysis
2. Document P1 enhancement timeline (CMC query API)
3. Update SDF-CVF integration docs with production wiring

**Reference:** `SYNTHESIS_SESSION_EXECUTION_2025-01-28.md` - Question 4

---

### **Meta (CAS)**
**Priority:** P0  
**Deadline:** 2025-02-04

**Actions:**
1. Implement CAS activation exports:
   - Payload schema: `{session_id, timestamp, top_hot_principles[10], cold_required[], attention_metrics, tags}`
   - Summary snapshot: `{session_id, timestamp, CAS summary, trend_window_24h, recommendations}`
   - Transport via `mcp_lucid-mcp_store_memory` with tags `activation_export` / `cas_summary_snapshot`
2. Coordinate with Atlas on CMC storage pattern
3. Update CAS integration docs with export patterns

**Reference:** `SYNTHESIS_SESSION_EXECUTION_2025-01-28.md` - Question 5

---

### **Alex (APOE)**
**Priority:** P0  
**Deadline:** 2025-02-04

**Actions:**
1. Implement κ-gate policies:
   - Routine: κ ≥ 0.70
   - Critical: κ ≥ 0.90
   - Emergency: κ ≥ 0.60 (with explicit override)
2. Implement retry heuristics:
   - Retry if success_rate > 0.70 (up to 2 retries)
   - Retry if success_rate > 0.80 (up to 3 retries)
   - Abstain if success_rate < 0.60 (no retries)
3. Update APOE executor to use VIF orchestration patterns

**Reference:** `SYNTHESIS_SESSION_EXECUTION_2025-01-28.md` - Question 2

---

### **Nexus (SEG)**
**Priority:** P0  
**Deadline:** 2025-02-01

**Actions:**
1. Confirm SEG evidence node schema
2. Coordinate with Nova on SEG evidence linking implementation
3. Update SEG integration docs with evidence linking patterns

**Reference:** `SYNTHESIS_SESSION_EXECUTION_2025-01-28.md` - Question 6

---

### **Chronos (TCS) + Sev (HHNI)**
**Priority:** P0  
**Deadline:** 2025-02-04

**Actions:**
1. Coordinate HHNI E2E run timing
2. Execute E2E run (Chronos to initiate, Sev to support)
3. Document E2E run results

**Reference:** `SYNTHESIS_SESSION_EXECUTION_2025-01-28.md` - Question 7

---

## 📊 **Progress Tracking**

### **Completion Status**
- ⏳ **Integration Tagging:** 0/8 agents complete
- ⏳ **System Maps Alignment:** 0/8 agents complete
- ⏳ **Directive 5 P0 Updates:** 0/8 agents complete
- ⏳ **Agent-Specific Actions:** 0/8 agents complete

### **Next Review**
- **Date:** 2025-02-04
- **Focus:** Post-synthesis action items completion
- **Status:** Monitor progress, escalate blockers

---

## ✅ **Success Criteria**

**Post-Synthesis Completion:**
- ✅ All agents have added `metadata.integration_tags` to integration atom creation
- ✅ All system maps/indexes aligned with code
- ✅ Directive 5 P0 updates complete
- ✅ VIF orchestration guide created
- ✅ SDF-CVF P0 enhancements implemented
- ✅ CAS activation exports implemented
- ✅ APOE κ-gate policies implemented
- ✅ HHNI E2E run completed

**Ready for Orchestration Integration:**
- ✅ Integration patterns standardized
- ✅ κ-gate policies defined
- ✅ Integration tagging standardized
- ✅ All systems ready for chat/IDE orchestration

---

**Status:** ⏳ **IN PROGRESS**  
**Next Update:** 2025-02-01 (mid-week check-in)  
**Target Completion:** 2025-02-04

