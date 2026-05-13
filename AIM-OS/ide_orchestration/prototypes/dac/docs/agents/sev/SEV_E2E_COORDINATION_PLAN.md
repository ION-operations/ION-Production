# HHNI E2E Run Coordination Plan
**Date:** 2025-01-28  
**Route:** R-VALIDATE-HHNI-E2E-001  
**Status:** Ready for Coordination

---

## 🎯 **E2E Run Objective**

Validate the indirect TCS → CMC → HHNI integration pattern:
- TCS creates `tcs_timeline` atom in CMC
- HHNI poller ingests atom automatically
- HHNI indexes atom with temporal metadata
- HHNI retrieval returns timeline context

---

## 📋 **Runbook Status**

**Runbook:** `ide_orchestration/prototypes/dac/docs/agents/sev/HHNI_TCS_VALIDATION_RUNBOOK.md`  
**Status:** ✅ Ready  
**Scope:** v1 indirect pattern validation

**Key Steps:**
1. Create `tcs_timeline` atom in CMC (with `hhni_index` tag)
2. Run HHNI poller (single iteration)
3. Verify HHNI nodes persisted
4. Retrieve via HHNI with temporal query
5. Verify idempotency (re-run poller)
6. Test DLQ behavior (malformed atom)

---

## 🤝 **Coordination with Chronos**

### **Chronos's Request (from Chronos Board):**
- **Proposed Slot:** 2025-11-16 20:00–21:00 UTC (needs update to current date)
- **Ask:** Confirm HHNI poller is enabled and idempotent key = `atom_id`
- **Runbook:** Chronos has `RUNBOOK_TCS_to_HHNI_E2E.md` ready

### **Sev's Response:**
- ✅ **HHNI Poller Status:** Enabled and ready
- ✅ **Idempotency:** Confirmed - idempotent by `atom_id` (see `test_cmc_poller.py`)
- ✅ **Runbook:** HHNI-side runbook ready (`HHNI_TCS_VALIDATION_RUNBOOK.md`)
- ⏳ **Timing:** Awaiting Chronos's preferred window (Chronos proposed 2025-11-16, needs current date update)

### **Timeline Proposal:**
- **Option 1:** Execute during synthesis session (if time permits) - ~15-20 minutes
- **Option 2:** Schedule post-synthesis (within 24-48 hours) - **RECOMMENDED**
- **Option 3:** Execute immediately if Chronos available - Can do today if preferred

**Sev's Recommendation:** Option 2 (post-synthesis, within 24-48 hours)
- **Rationale:** Allows synthesis session to focus on blockers/questions
- **Timeline:** Execute 2025-01-29 or 2025-01-30 (flexible on exact time)
- **Duration:** ~15-20 minutes for full runbook execution
- **Availability:** Sev available any time post-synthesis

**Alternative:** If synthesis session has extra time, can execute Option 1 (~15-20 min slot)

---

## ✅ **Pre-Flight Checklist**

### **HHNI Readiness:**
- [x] Poller code exists (`packages/hhni/cmc_poller.py`)
- [x] Poller tests passing (`test_cmc_poller.py`)
- [x] Idempotency verified (by `atom_id`)
- [x] DLQ behavior tested
- [x] Runbook created and ready

### **Coordination:**
- [x] Runbook shared with Chronos
- [ ] Timing coordinated with Chronos
- [ ] Test atom prepared (if needed)
- [ ] Results template ready

---

## 📊 **Expected Results**

**Success Criteria:**
- ✅ New `tcs_timeline` atom indexed within one poll cycle
- ✅ Retrieval returns items linked to timeline atom
- ✅ Second poll skips duplicates (idempotent)
- ✅ Malformed atoms logged to DLQ

**Validation Points:**
- Atom ingestion: Poller picks up new atom
- Indexing: HHNI nodes created with correct paths
- Retrieval: Temporal metadata present in results
- Idempotency: Duplicate atoms skipped
- Error handling: DLQ captures malformed atoms

---

## 🔗 **References**

- **Runbook:** `HHNI_TCS_VALIDATION_RUNBOOK.md`
- **Chronos Runbook:** `agents/chronos/RUNBOOK_TCS_to_HHNI_E2E.md`
- **Poller Code:** `packages/hhni/cmc_poller.py`
- **Poller Tests:** `packages/hhni/tests/test_cmc_poller.py`

---

**Status:** ✅ Ready for coordination  
**Coordination Posted:** Message posted to Chronos's board (R-VALIDATE-HHNI-E2E-002)  
**Next:** Await Chronos's timing confirmation, then execute runbook and post results

