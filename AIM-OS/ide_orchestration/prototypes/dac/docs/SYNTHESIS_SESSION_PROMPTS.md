# Synthesis Session - Agent Prompts
**Date:** 2025-01-28  
**Route:** R-SYNTHESIS-001  
**Status:** ✅ **SESSION SCHEDULED**

---

## 🌟 **Universal Prompt (All Agents)**

---

**Subject: Final Consolidation Synthesis Session - Preparation Required**

**All Agents:**

The final consolidation synthesis session has been scheduled. This is a critical 2-hour session to finalize all consolidation work, validate system integrations, answer open questions, and prepare for chat/IDE orchestration integration.

### **📋 What You Need to Do:**

1. **Read These Documents (Required):**
   - `ide_orchestration/prototypes/dac/docs/SYNTHESIS_SESSION_SCHEDULE.md` - Full session schedule and agenda
   - `ide_orchestration/prototypes/dac/docs/SYNTHESIS_AGENDA_2025-01-28.md` - Detailed synthesis agenda
   - `ide_orchestration/prototypes/dac/docs/SYNTHESIS_TEAM_RESPONSE_SUMMARY.md` - Team response summary

2. **Review Orchestration Recommendations (Required):**
   - `ide_orchestration/prototypes/dac/docs/agents/sage/VIF_ORCHESTRATION_PATTERN_RECOMMENDATIONS.md` - VIF orchestration patterns
   - `ide_orchestration/prototypes/dac/docs/agents/META/CAS_ORCHESTRATION_PATTERN_RECOMMENDATIONS.md` - CAS orchestration patterns

3. **Prepare Your 3-5 Minute Status Presentation:**
   - Test status (passing/failing counts)
   - Integration validation status (which integrations are validated)
   - Goal progress (G1/G2/G3 status)
   - Blockers (if any)
   - Open questions (if any)

4. **Review Your Status Summary:**
   - Check your coordination board for your R-SYNTHESIS-001 entry
   - Ensure all blockers are documented
   - Ensure all open questions are listed

### **🎯 Session Structure:**

- **Part 1: Status Review (30 min)** - Each agent presents 3-5 min status
- **Part 2: Blocker Resolution (30 min)** - Resolve or coordinate all blockers
- **Part 3: Open Questions (45 min)** - Answer all open questions with team decisions
- **Part 4: Orchestration Planning (15 min)** - Plan next steps for chat/IDE integration

### **📊 Key Decisions Needed:**

1. VIF witness orchestration patterns (mandatory vs optional)
2. Default κ-gate/retry policies
3. Integration tagging standardization
4. SDF-CVF enhancement priorities
5. CAS activation exports pattern
6. HHNI E2E run timing

### **✅ Pre-Session Checklist:**

- [ ] Read synthesis session schedule
- [ ] Read synthesis agenda
- [ ] Review orchestration recommendations (VIF + CAS)
- [ ] Prepare 3-5 min status presentation
- [ ] Review your status summary on coordination board
- [ ] Document any new blockers or questions

### **🔗 Key Files to Review:**

**Session Documents:**
- `SYNTHESIS_SESSION_SCHEDULE.md` - Session schedule
- `SYNTHESIS_AGENDA_2025-01-28.md` - Detailed agenda
- `SYNTHESIS_TEAM_RESPONSE_SUMMARY.md` - Team responses

**Orchestration Recommendations:**
- `agents/sage/VIF_ORCHESTRATION_PATTERN_RECOMMENDATIONS.md`
- `agents/META/CAS_ORCHESTRATION_PATTERN_RECOMMENDATIONS.md`

**Your Status:**
- Your coordination board: `agents/[your-name]/COORDINATION_BOARD.md`
- Look for your R-SYNTHESIS-001 entry

**Ready?** Review the documents, prepare your presentation, and be ready to participate in the synthesis session.

---

## 🎯 **Agent-Specific Prompts**

---

### **Atlas (CMC) - Specific Preparation**

**Additional Tasks:**

1. **Review Meta's CAS Activation Exports Proposal:**
   - File: `ide_orchestration/prototypes/dac/docs/agents/atlas/COORDINATION_BOARD.md`
   - Look for: Route R-CAS-CMC-EXPORTS (around line 481)
   - Action: Prepare response to Meta's coordination request
   - Questions to Answer:
     - Modality: `cas_activation_export` / `cas_summary_snapshot` or reuse `cognitive_analysis`?
     - Tags: Are proposed tags compatible with CMC tag patterns?
     - Metadata Schema: Does proposed structure align with CMC expectations?
     - Registry Mirroring: Recommended pattern for mirroring CMC atom IDs?

2. **Review APOE→CMC v1 Sample Payloads:**
   - File: `ide_orchestration/prototypes/dac/docs/agents/atlas/ATLAS_APOE_CMC_V1_SAMPLE_PAYLOADS.md`
   - Action: Be ready to present sample payloads during session

3. **Prepare CMC Integration Status:**
   - Test status: 148/150 passing
   - Integration validation: 5/7 fully validated, 2/7 partially validated
   - APOE→CMC v1: Contract locked, sample payloads ready

**Key Files:**
- `agents/atlas/COORDINATION_BOARD.md` - Your status summary (line 426)
- `agents/atlas/ATLAS_APOE_CMC_V1_SAMPLE_PAYLOADS.md` - Sample payloads
- `SYNTHESIS_SESSION_SCHEDULE.md` - Session schedule

---

### **Sev (HHNI) - Specific Preparation**

**Additional Tasks:**

1. **Prepare HHNI E2E Run Coordination Plan:**
   - Coordinate with Chronos on timing
   - Review E2E runbook requirements
   - Prepare timeline proposal

2. **Review SDF-CVF Quartet Parity Hooks:**
   - File: `ide_orchestration/prototypes/dac/docs/agents/sev/COORDINATION_BOARD.md`
   - Look for: Nova's API recommendation (R-HHNI-INTEGRATIONS-005)
   - Action: Prepare implementation plan

3. **Review VIF Witness Creation API:**
   - Coordinate with Sage on VIF witness creation API
   - Prepare questions for synthesis discussion

4. **Prepare HHNI Integration Status:**
   - Test status: Core tests passing
   - Integration validation: 4/7 fully closed, 1/7 pattern only, 1/7 partial, 1/7 pending
   - CAS hooks: Implemented and tested (2/2 passing)

**Key Files:**
- `agents/sev/COORDINATION_BOARD.md` - Your status summary (line 427)
- `agents/sev/SEV_SYNTHESIS_PREPARATION.md` - Comprehensive status summary
- `SYNTHESIS_SESSION_SCHEDULE.md` - Session schedule

---

### **Nexus (SEG) - Specific Preparation**

**Additional Tasks:**

1. **Review SEG Evidence Linking Answer:**
   - File: `ide_orchestration/prototypes/dac/docs/agents/nexus/COORDINATION_BOARD.md`
   - Look for: Route R-SYNTHESIS-002 (around line 800)
   - Action: Confirm answer is complete, prepare to present during session

2. **Prepare SEG Integration Matrix Presentation:**
   - 7 integrations, 22 functions, 37 tests
   - All integrations verified
   - Be ready to walk through DUO gate evidence pipeline

3. **Review Integration Re-Scan Results:**
   - File: `ide_orchestration/prototypes/dac/docs/agents/nexus/NEXUS_INTEGRATION_RESCAN_COMPLETE.md`
   - Action: Be ready to present re-scan findings

4. **Prepare SEG Status:**
   - Test status: 100/100 passing (63 core + 37 integration)
   - Integration validation: 7/7 verified
   - Documentation: 100% aligned with code

**Key Files:**
- `agents/nexus/COORDINATION_BOARD.md` - Your status summary (line 771)
- `agents/nexus/NEXUS_SYNTHESIS_PREPARATION.md` - Status summary
- `agents/nexus/NEXUS_INTEGRATION_RESCAN_COMPLETE.md` - Integration re-scan
- `SYNTHESIS_SESSION_SCHEDULE.md` - Session schedule

---

### **Sage (VIF) - Specific Preparation**

**Additional Tasks:**

1. **Review VIF Orchestration Recommendations:**
   - File: `ide_orchestration/prototypes/dac/docs/agents/sage/VIF_ORCHESTRATION_PATTERN_RECOMMENDATIONS.md`
   - Action: Be ready to present recommendations during session
   - Key Points:
     - P0 mandatory flows (7 critical flows)
     - Default κ-gate/retry policies
     - Mandatory vs optional patterns
     - Integration tagging standardization

2. **Prepare VIF Orchestration Presentation:**
   - Present P0 mandatory witness creation flows
   - Present κ-gate/retry policy recommendations
   - Present integration tagging standardization proposal

3. **Coordinate with Sev on VIF Witness Creation API:**
   - Prepare questions for synthesis discussion
   - Review HHNI integration requirements

4. **Prepare VIF Status:**
   - Test status: 219/219 passing (100%)
   - Integration validation: 7/7 integration modules exist and tested
   - Orchestration gaps: Witness creation not yet mandatory in all paths

**Key Files:**
- `agents/sage/COORDINATION_BOARD.md` - Your status summary (line 508)
- `agents/sage/VIF_ORCHESTRATION_PATTERN_RECOMMENDATIONS.md` - Orchestration recommendations
- `SYNTHESIS_SESSION_SCHEDULE.md` - Session schedule

---

### **Chronos (TCS) - Specific Preparation**

**Additional Tasks:**

1. **Prepare HHNI E2E Run Coordination Plan:**
   - Coordinate with Sev on timing
   - Review E2E runbook requirements
   - Prepare timeline proposal

2. **Review TCS Test Import Fixes:**
   - Status: Pre-existing import issues (non-blocking)
   - Action: Prepare post-synthesis cleanup plan (P2)

3. **Prepare Partner Validation Confirmations:**
   - Coordinate with Nova (SDF-CVF) and Meta (CAS)
   - Prepare confirmation requests

4. **Prepare TCS Status:**
   - Test status: Integration tests verified (4/7 explicit tests)
   - Integration validation: 7/7 integrations validated (code + docs)
   - Documentation: 17/17 updates complete (100%)

**Key Files:**
- `agents/chronos/COORDINATION_BOARD.md` - Your status summary (line 337)
- `agents/chronos/CHRONOS_SYNTHESIS_PREPARATION_STATUS.md` - Status summary
- `SYNTHESIS_SESSION_SCHEDULE.md` - Session schedule

---

### **Meta (CAS) - Specific Preparation**

**Additional Tasks:**

1. **Review CAS Orchestration Recommendations:**
   - File: `ide_orchestration/prototypes/dac/docs/agents/META/CAS_ORCHESTRATION_PATTERN_RECOMMENDATIONS.md`
   - Action: Be ready to present recommendations during session
   - Key Points:
     - When to use CAS in chat/IDE flows
     - CAS integration patterns
     - Standard CAS orchestration flows
     - CAS activation exports pattern

2. **Review CAS Activation Exports Coordination Request:**
   - File: `ide_orchestration/prototypes/dac/docs/agents/META/COORDINATION_BOARD.md`
   - Look for: Route R-SYNTHESIS-001-PREP (around line 401)
   - Action: Check status of Atlas response, prepare to discuss during session

3. **Prepare CAS Activation Exports Presentation:**
   - Present proposed integration pattern
   - Present payload schemas
   - Present delivery mechanism proposal

4. **Prepare CAS Status:**
   - Test status: 81/81 passing (100%)
   - Integration validation: All 8 systems verified
   - Documentation: 100% aligned (code ↔ docs)

**Key Files:**
- `agents/META/COORDINATION_BOARD.md` - Your status summary (line 334)
- `agents/META/CAS_ORCHESTRATION_PATTERN_RECOMMENDATIONS.md` - Orchestration recommendations
- `agents/META/CAS_FOLLOWUPS_R-CONS-002.md` - Follow-ups and open questions
- `SYNTHESIS_SESSION_SCHEDULE.md` - Session schedule

---

### **Nova (SDF-CVF) - Specific Preparation**

**Additional Tasks:**

1. **Review Nexus's SEG Evidence Linking Answer:**
   - File: `ide_orchestration/prototypes/dac/docs/agents/nexus/COORDINATION_BOARD.md`
   - Look for: Route R-SYNTHESIS-002 (around line 800)
   - Action: Confirm answer, prepare implementation plan

2. **Prepare SDF-CVF Enhancement Priorities:**
   - P0: HHNI, SEG, CAS production wiring
   - P1: CMC query API for parity history
   - Action: Be ready to present priorities during session

3. **Review Production Wiring Requirements:**
   - HHNI → `TwoStageRetriever.retrieve()` for change context
   - SEG → `SEGraph.add_relation/add_evidence()` for evidence tracking
   - CAS → `FailureModeAnalyzer` / `IntrospectionProtocol` for failure analysis

4. **Prepare SDF-CVF Status:**
   - Test status: 136/154 passing (88.3%), 18 failures expected
   - Integration validation: All 7 integrations validated
   - Production wiring: P0 priorities identified

**Key Files:**
- `agents/nova/COORDINATION_BOARD.md` - Your status summary (line 515)
- `agents/nova/NOVA_CROSS_VALIDATION_P0_UPDATES_REPORT.md` - Cross-validation report
- `SYNTHESIS_SESSION_SCHEDULE.md` - Session schedule

---

### **Alex (APOE) - Specific Preparation**

**Additional Tasks:**

1. **Review APOE→CMC v1 Integration Status:**
   - Test status: 18/18 passing (100%)
   - Spec compliance: Complete
   - All decisions: Implemented
   - Status: ✅ **COMPLETE** - Ready for synthesis

2. **Prepare Spec Sync Tool Updates Plan:**
   - Current: Validates modality/tags
   - May need: Validate all 5 tags explicitly (`apoe`, `plan`, `execution`, `plan_name:<name>`, `status:<status>`)
   - Action: Prepare update plan for synthesis discussion (non-blocking)
   - Note: Already documented in open questions (coordination board line 640)

3. **Review System Map/Index Alignment:**
   - Status: ✅ **VERIFIED** - All connections match code
   - System maps: Updated with all 7 integrations, connection pattern tags, Layer 3 components
   - System index: Updated with subsystems array, all integration points
   - Action: Confirm alignment during synthesis (already verified)

4. **Prepare APOE Status Presentation:**
   - Test status: 18/18 CMC integration tests passing (100%)
   - Integration validation: 7/7 integrations have code + tests
   - APOE→CMC v1: Complete, spec compliant
   - Goal status: G1 ✅, G2 ✅, G3 ✅ (all complete)
   - Blockers: None
   - Open questions: Spec sync tool updates, T-level doc timeline, system map verification

**Key Files:**
- `agents/alex/COORDINATION_BOARD.md` - Your status summary (line 603) ✅ **POSTED**
- `agents/alex/APOE_CMC_V1_DECISIONS.md` - Decisions document
- `agents/alex/APOE_CMC_PAYLOAD_SPEC_v1.md` - Payload spec
- `agents/alex/APOE_CMC_INTEGRATION_R-CONS-002.md` - R-CONS-002 audit report
- `SYNTHESIS_SESSION_SCHEDULE.md` - Session schedule

**Status:** ✅ **PREPARATION COMPLETE** - Status summary posted, ready for synthesis session

---

## 📋 **Quick Reference Checklist**

### **All Agents:**
- [ ] Read `SYNTHESIS_SESSION_SCHEDULE.md`
- [ ] Read `SYNTHESIS_AGENDA_2025-01-28.md`
- [ ] Review VIF orchestration recommendations
- [ ] Review CAS orchestration recommendations
- [ ] Prepare 3-5 min status presentation
- [ ] Review your coordination board status summary
- [ ] Document any new blockers or questions

### **Agent-Specific:**
- [ ] **Atlas:** Review Meta's CAS activation exports proposal, prepare response
- [ ] **Sev:** Prepare HHNI E2E run coordination plan, review SDF-CVF hooks
- [ ] **Nexus:** Review SEG evidence linking answer, prepare integration matrix presentation
- [ ] **Sage:** Review VIF orchestration recommendations, prepare presentation
- [ ] **Chronos:** Prepare HHNI E2E run coordination plan, review test fixes
- [ ] **Meta:** Review CAS orchestration recommendations, check Atlas response status
- [ ] **Nova:** Review Nexus's SEG evidence linking answer, prepare enhancement priorities
- [ ] **Alex:** Review APOE→CMC v1 status, prepare spec sync tool updates plan

---

## 🎯 **Session Goals Reminder**

**Must Achieve:**
- ✅ All blockers resolved or coordinated
- ✅ All open questions answered
- ✅ Integration patterns standardized
- ✅ Orchestration integration plan created

**Key Decisions:**
- VIF witness orchestration patterns
- Default κ-gate/retry policies
- Integration tagging standardization
- SDF-CVF enhancement priorities
- CAS activation exports pattern
- HHNI E2E run timing

---

**Status:** ✅ **SESSION SCHEDULED**  
**All Agents:** Please review your specific prompt, complete preparation tasks, and be ready for the synthesis session.

