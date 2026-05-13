# Team Prompts - Finalization Phase Continuation
**Date:** 2025-01-28  
**Status:** R-CONS-002 at 7/8 ready (Alex pending APOE→CMC v1 tests)  
**Phase:** Finalization + Integration (Directives 3 & 5 active)

---

## 🎯 **Universal Context**

**Current Status:**
- ✅ R-CONS-002: 7/8 agents ready (Atlas, Sev, Nexus, Sage, Chronos, Meta, Nova)
- ⏳ Alex: APOE→CMC v1 tests need to pass (import/attribute fixes required)
- ✅ All agents: Directives 1, 2, 4 complete
- 🔄 All agents: Directives 3 & 5 active (cross-validation + P0 integration updates)

**Next Milestone:**
- Once APOE tests are green → 8/8 R-CONS-002 ready → Synthesis session prep

---

## 📋 **Agent-Specific Prompts**

### **Alex (APOE) - Priority P0**

**Status:** ✅ **Decisions provided!** Audit complete, all decisions made. Ready to update tests.

**Immediate Actions:**
1. **Read decisions document:** `ide_orchestration/prototypes/dac/docs/agents/alex/APOE_CMC_V1_DECISIONS.md` (all questions answered)
2. **Update test file** (`packages/apoe/tests/test_cmc_integration.py`):
   - Replace `_memory_cache` with `_cache` (or add property alias per decisions)
   - Remove `test_retrieve_similar_plans` (method not required)
   - Update `test_store_to_cmc_calls_client_create_atom` to check both `AtomCreate` payload and legacy kwargs paths
   - Update `test_plan_execution_dataclass` to expect `status="partial"` (not `"running"`)
   - Add tag assertions for `"execution"` and `"status:<status>"` patterns (all 5 tags must be verified)
3. **Run tests:** `pytest packages/apoe/tests/test_cmc_integration.py -v` (should be 19/19 passing after updates)
4. **Post R-CONS-002 ack:** Once tests are green, post a short readiness ack on your board with:
   - Test status (19/19 passing)
   - Sample atom payload link (start + partial + complete)
   - Any remaining blockers (should be none)

**Reference:** 
- **Decisions:** `ide_orchestration/prototypes/dac/docs/agents/alex/APOE_CMC_V1_DECISIONS.md` ⭐ **READ THIS FIRST**
- **Audit:** `ide_orchestration/prototypes/dac/docs/agents/alex/APOE_CMC_INTEGRATION_R-CONS-002.md`
- **Implementation:** `packages/apoe/cmc_integration_v1.py`
- **Tests:** `packages/apoe/tests/test_cmc_integration.py`
- **Spec:** `ide_orchestration/prototypes/dac/docs/agents/alex/APOE_CMC_PAYLOAD_SPEC_v1.md`

---

### **Atlas (CMC) - Directive 3 & 5**

**Status:** R-CONS-002 ready ✅. Continue with cross-validation and P0 updates.

**Actions:**
1. **Directive 3 (Cross-Validation):** Systematically verify each documented CMC ↔ (HHNI, APOE, SEG, VIF, SDF-CVF, CAS, TCS) connection:
   - Locate actual integration modules in codebase
   - Verify module signatures match system maps/hierarchy docs
   - Confirm tests exist and pass
   - Document any gaps or mismatches
2. **Directive 5 (P0 Updates):** Execute P0 items from your post-consolidation update list:
   - Update system maps/indexes to reflect actual code
   - Align T0-T2 docs with current implementation
   - Fix any connection matrix mismatches
3. **APOE→CMC v1:** Once Alex's tests are green, capture one concrete atom triplet (start, partial, complete) and post on your board as the canonical example, confirming stable contract for HHNI/SDF-CVF.
4. **Update R-CONS-002 section:** Keep it current with validation status and any blockers for synthesis.

**Reference:** Your post-consolidation update list, system maps, `SUBSYSTEM_HIERARCHY_MAPPING.md`

---

### **Sev (HHNI) - Directive 3 & 5**

**Status:** R-CONS-002 ready ✅. Continue with integration validation and P0 updates.

**Actions:**
1. **Directive 3 (HHNI Integrations):** For each documented integration (CMC, APOE, VIF, SDF-CVF, CAS, SEG, TCS):
   - Verify actual HHNI code + tests exist and match docs
   - Confirm CAS activation hooks are implemented and tested
   - Verify SDF-CVF quartet parity hooks (once Nova's API recommendation is confirmed)
2. **Directive 5 (P0 Updates):** Execute P0 items from your HHNI update list:
   - Align main HHNI modules with shared hierarchy/system maps
   - Update docs to match actual code
   - Fix any connection matrix mismatches
3. **R-COORD-001/Registry:** Post concise status for each HHNI integration request (closed vs open), with links to actual tests proving the integration.
4. **Update R-CONS-002 section:** Keep it current with integration validation status.

**Reference:** Your HHNI update list, `COORDINATION_REQUEST_REGISTRY.md`, Nova's quartet-parity API recommendation

---

### **Sage (VIF) - Directive 3 & 5**

**Status:** R-CONS-002 ready ✅. Cross-validation complete, continue with P0 orchestration work.

**Actions:**
1. **Directive 5 (P0 Orchestration):** Focus on making VIF witness creation and κ-gate logging **mandatory** in each system's execution flows:
   - **CMC P0:** Ensure single canonical path for "store a VIF witness" (`create_witness_and_store` + `VIFStore.store_witness`)
   - **HHNI P0:** Provide helper to "take a `RetrievalResult` and emit/store a VIF witness", ensure core retrieval flows call it
   - **SEG P0:** Ensure main "commit graph update" path has optional VIF witness ID parameter
   - **APOE P0:** Ensure canonical executor path calls VIF for both witness creation and κ-gate enforcement
   - **CAS P0:** Confirm "happy path" where CAS activation + cognitive context always ends in updated VIF witness
   - **SDF-CVF P0:** Provide straightforward "given a file set, fetch witnesses and compute parity" entrypoint
   - **TCS P0:** Standardize that all κ-gate decisions go through `create_kappa_gate_timeline_entry`
2. **Synthesis Questions:** Keep your R-CONS-002 section updated with:
   - Tagging/Discovery question (standardize `metadata.integration_tags`?)
   - Default κ-gate/retry policies question
   - Mandatory vs Optional question (which flows must always emit witness?)

**Reference:** Your R-CONS-002 recap, VIF integration modules, system maps

---

### **Chronos (TCS) - Directive 3 & 5**

**Status:** R-CONS-002 ready ✅. TCS tests have collection errors, continue with validation.

**Actions:**
1. **Fix TCS Test Collection Errors:** Address the pre-existing import issues in TCS core test suite (legacy import patterns, not introduced by recent work).
2. **Directive 3 (Cross-Validation):** Your cross-validation is effectively complete. Remaining work:
   - Partner confirmations (SDF-CVF, CAS) - wait for Nova/Meta responses
   - HHNI E2E run (R-VALIDATE-HHNI-E2E-001) - coordinate with Sev
3. **Directive 5 (P0 Updates):** Once TCS tests are clean and HHNI E2E is run, TCS can be marked fully green.
4. **Update R-CONS-002 section:** Keep it current with:
   - TCS test status (collection errors → fixed)
   - HHNI E2E status (pending → complete)
   - Partner confirmations (pending → received)

**Reference:** Your TCS test files, `CHRONOS_PHASE1_CROSS_VALIDATION_REPORT.md`, HHNI E2E route

---

### **Meta (CAS) - Directive 3 & 5**

**Status:** R-CONS-002 ready ✅. CAS tests green (102/102), cross-validation complete.

**Actions:**
1. **Directive 5 (P0 Follow-Ups):** Execute P0 items from your follow-ups doc:
   - Activation exports + summary snapshots → CMC + registry mirror
   - Ensure CAS activation hooks are fully reflected in HHNI implementation (coordinate with Sev)
2. **Update R-CONS-002 section:** Keep it current with follow-up status and any blockers.
3. **Synthesis Prep:** CAS is in excellent shape (102/102 tests, all integrations verified). Ready for synthesis discussion on orchestration patterns.

**Reference:** `CAS_FOLLOWUPS_R-CONS-002.md`, CAS integration tests, HHNI CAS hooks spec

---

### **Nova (SDF-CVF) - Directive 3 & 5**

**Status:** R-CONS-002 ready ✅. Cross-validation complete, synthesis questions logged.

**Actions:**
1. **Directive 5 (Integration Enhancements):** Based on team responses to your synthesis questions:
   - **HHNI Integration:** If team confirms, wire actual HHNI query APIs (replace simplified fallbacks)
   - **SEG Evidence Linking:** If team confirms, implement full SEG graph linking
   - **CAS/APOE Import Paths:** Verify and fix import paths based on team confirmations
   - **Integration Test Coverage:** Add integration tests for actual external system calls if confirmed
2. **Update R-CONS-002 section:** Keep it current with:
   - Synthesis questions status (pending → responses received)
   - Integration enhancement status (simplified → full implementations)
3. **Synthesis Prep:** SDF-CVF is well-documented and tested. Ready for synthesis discussion on quartet-parity orchestration.

**Reference:** Your synthesis questions on coordination board, integration modules, `SUBSYSTEM_HIERARCHY_MAPPING.md`

---

### **Nexus (SEG) - Directive 3 & 5**

**Status:** R-CONS-002 ready ✅. Re-scanning SEG integrations.

**Actions:**
1. **Directive 3 (Cross-Validation):** Complete your re-scan of SEG integrations:
   - Verify all 7 integration modules exist and match docs
   - Confirm tests pass and cover integration patterns
   - Document any gaps or mismatches
2. **Directive 5 (P0 Updates):** Execute P0 items from your SEG update list:
   - Align system maps/indexes with actual code
   - Update T0-T2 docs to match implementation
   - Fix connection matrix mismatches
3. **Update R-CONS-002 section:** Keep it current with cross-validation status and any blockers.
4. **Coordination:** As relationship/consolidation lead, help coordinate any cross-system questions that arise.

**Reference:** Your SEG update list, integration modules, `SUBSYSTEM_HIERARCHY_MAPPING.md`

---

## 🎯 **Synthesis Prep (Once 8/8 Ready)**

**Once Alex posts R-CONS-002 ack:**
- Codex will draft synthesis agenda with:
  - 1-2 bullets per system (what's done, what's missing for G2/G3)
  - Open questions from all agents
  - Blockers list
  - Next steps for chat/IDE integration

**Target:** Synthesis session scheduled once 8/8 ready.

---

## 📊 **Coordination Health**

**Pending Requests:**
- Check `COORDINATION_REQUEST_REGISTRY.md` for open requests
- Respond to any requests directed at you
- Update registry when requests are closed

**Daily Digest:**
- Check `COORDINATION_DIGEST_YYYY-MM-DD.md` for daily summary
- Next digest: 2025-01-29 09:00 UTC

---

**Questions?** Post on your per-agent board or route via `AGENT_COORDINATION_ROUTER.md`.

**Status Updates:** Keep your R-CONS-002 section current as you progress through Directives 3 & 5.

