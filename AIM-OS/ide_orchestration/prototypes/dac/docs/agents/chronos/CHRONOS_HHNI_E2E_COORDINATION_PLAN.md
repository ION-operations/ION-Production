# HHNI E2E Run Coordination Plan

**Agent:** Chronos (TCS System Specialist)  
**Date:** 2025-01-28  
**Route:** R-VALIDATE-HHNI-E2E-001  
**Status:** ⏳ **Ready for Coordination**

---

## 🎯 **COORDINATION OBJECTIVE**

**Goal:** Execute end-to-end validation of TCS → HHNI indirect integration via CMC.

**Integration Pattern:** TCS → CMC (`tcs_timeline` atoms) → HHNI poller → HHNI retrieval

**Purpose:** Validate that timeline entries are properly indexed by HHNI and available for temporal context retrieval.

---

## 📋 **E2E RUNBOOK STATUS**

**Runbook:** `RUNBOOK_TCS_to_HHNI_E2E.md` ✅ **Complete**

**Steps Defined:**
1. Create TCS timeline entry via MCP tool (`mcp_lucid-mcp_add_timeline_entry`)
2. Verify atom persisted in CMC with `modality="tcs_timeline"`
3. Wait for HHNI poller to index atom (or trigger manual run)
4. Validate HHNI retrieval contains temporal metadata
5. Record results in report

**Success Criteria:**
- ✅ Atom stored with `modality="tcs_timeline"`
- ✅ HHNI indexes atom (node exists)
- ✅ Retrieval returns node with temporal metadata present

**Correlation ID:** `tcs_hhni_e2e_001` (for tracking)

---

## 🤝 **COORDINATION WITH @SEV**

### **Coordination Request Status**

**Posted:** Route R-VALIDATE-HHNI-E2E-001 on @Sev's coordination board  
**Date:** 2025-11-16  
**Status:** ⏳ **Awaiting Response**

**Request Details:**
- Proposed slot: 2025-11-16 20:00–21:00 UTC (flexible)
- Duration: ~30 minutes (execution + validation)
- Requirements:
  - HHNI poller enabled and running
  - CMC service accessible
  - HHNI retrieval API available for testing

**Questions for @Sev:**
1. **Timing:** When is a good time to schedule the E2E run? (proposed: 2025-11-16 20:00–21:00 UTC, flexible)
2. **Poller Status:** Is HHNI poller currently enabled and running?
3. **Poller Configuration:** Confirm idempotent key = `atom_id` for duplicate prevention?
4. **Manual Trigger:** If poller is disabled, can we trigger manual ingest for this test?
5. **Retrieval API:** Is `hhni.search_with_temporal_context()` available for testing?

---

## 📅 **TIMELINE PROPOSAL**

### **Option 1: During Synthesis Session (Recommended)**
- **Timing:** Part 2 (Blocker Resolution) or Part 3 (Open Questions)
- **Duration:** 5-10 minutes coordination discussion
- **Action:** Schedule execution for post-session (within 24-48 hours)
- **Benefits:** 
  - Immediate coordination
  - Clear timeline established
  - Team awareness

### **Option 2: Post-Session Coordination**
- **Timing:** Within 24 hours after synthesis session
- **Duration:** ~30 minutes execution + validation
- **Action:** Coordinate via coordination boards or direct communication
- **Benefits:**
  - More time for preparation
  - Less pressure during session

### **Option 3: Immediate Execution (If @Sev Available)**
- **Timing:** During synthesis session break or immediately after
- **Duration:** ~30 minutes execution + validation
- **Action:** Execute runbook, record results immediately
- **Benefits:**
  - Immediate validation
  - Results available for session discussion

**Recommendation:** **Option 1** - Coordinate timing during session, execute post-session within 24-48 hours.

---

## 🔧 **PRE-REQUISITES CHECKLIST**

**Before Execution:**
- [ ] CMC service running and accessible
- [ ] HHNI poller enabled (or manual trigger available)
- [ ] `modality="tcs_timeline"` fix confirmed in code (✅ already done)
- [ ] HHNI retrieval API available for testing
- [ ] Correlation ID `tcs_hhni_e2e_001` ready for tracking
- [ ] Results document ready: `RUNBOOK_TCS_to_HHNI_E2E_RESULTS.md`

**TCS Side (Chronos):**
- ✅ Runbook complete
- ✅ MCP tool available (`mcp_lucid-mcp_add_timeline_entry`)
- ✅ Modality fix applied
- ✅ Results document template ready

**HHNI Side (@Sev):**
- ⏳ Poller status confirmation needed
- ⏳ Poller configuration confirmation needed
- ⏳ Retrieval API availability confirmation needed

---

## 📊 **EXECUTION PLAN**

### **Step 1: Pre-Execution Coordination (5 min)**
- Confirm poller status with @Sev
- Verify CMC service accessible
- Confirm retrieval API available
- Set correlation ID: `tcs_hhni_e2e_001`

### **Step 2: Execute Runbook (15 min)**
1. Create TCS timeline entry via MCP tool
2. Verify atom in CMC (query by correlation_id)
3. Wait for/trigger HHNI poller
4. Validate HHNI retrieval with temporal metadata
5. Record all results

### **Step 3: Results Documentation (10 min)**
- Record atom_id, indexed node id, retrieval score
- Document temporal metadata fields present
- Note any issues or discrepancies
- Update `RUNBOOK_TCS_to_HHNI_E2E_RESULTS.md`

**Total Duration:** ~30 minutes

---

## ✅ **SUCCESS CRITERIA**

**Must Pass:**
1. ✅ Atom stored in CMC with `modality="tcs_timeline"`
2. ✅ Atom indexed by HHNI (node exists in HHNI index)
3. ✅ Retrieval returns node with temporal metadata

**Nice to Have:**
- Retrieval score above threshold
- All expected temporal fields present
- No duplicate indexing (idempotency verified)

---

## 📝 **POST-EXECUTION ACTIONS**

**If Successful:**
- ✅ Mark HHNI E2E as complete
- ✅ Update TCS-G3 goal status (E2E validation complete)
- ✅ Document results in coordination board
- ✅ Close coordination request

**If Issues Found:**
- Document issues in results report
- Coordinate with @Sev on fixes
- Schedule re-execution if needed
- Update blockers list if critical

---

## 🔗 **KEY DOCUMENTS**

**Runbook:**
- `RUNBOOK_TCS_to_HHNI_E2E.md` - Complete execution steps

**Results:**
- `RUNBOOK_TCS_to_HHNI_E2E_RESULTS.md` - Results template (ready for execution)

**Coordination:**
- @Sev's board: Route R-VALIDATE-HHNI-E2E-001
- TCS coordination board: Route R-VALIDATE-HHNI-E2E-001

**Integration Docs:**
- `CHRONOS_TCS_HHNI_INTEGRATION.md` - Integration documentation
- `knowledge_architecture/systems/timeline_context_system/T2_architecture.md` - Architecture (indirect pattern documented)

---

**Status:** ⏳ **Ready for Coordination**  
**Next:** Coordinate timing with @Sev during synthesis session or post-session  
**Timeline:** Execute within 24-48 hours after coordination

