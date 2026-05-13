# Synthesis Session Preparation Prompts
**Date:** 2025-01-28  
**Status:** ✅ **8/8 Agents Ready**  
**Route:** R-SYNTHESIS-001

---

## 🎯 **Purpose**

This document contains tailored prompts for each agent to begin the synthesis session work. Each prompt is customized based on the agent's system, current status, and focus areas from the synthesis agenda.

---

## 📋 **Agent Prompts**

### **Atlas (CMC) - Synthesis Session Prompt**

**Phase:** Synthesis Preparation → Synthesis Session  
**Route:** R-SYNTHESIS-001  
**Status:** Cross-validation in progress, APOE→CMC v1 contract confirmed

**Your Focus Areas:**
1. **APOE→CMC v1 Contract Confirmation**
   - Verify modality `plan_execution` is locked
   - Confirm tags format: `["apoe", "plan", "execution", "plan_name:<name>", "status:<status>"]`
   - Validate ordering: `started_at` descending, then `execution_id` descending
   - Prepare sample atom payloads (start, partial, complete) for team review

2. **CMC ↔ All Systems Integration Validation**
   - Review integration status for: HHNI, SEG, VIF, SDF-CVF, CAS, TCS, APOE
   - Verify each integration has code + tests
   - Note any integration gaps or mismatches
   - Prepare integration validation summary

3. **System Map/Index Alignment**
   - Review CMC system maps/indexes
   - Compare with actual code implementation
   - Identify any misalignments
   - Prepare update plan if needed

**Preparation Tasks:**
- [ ] Review your R-CONS-002 readiness ack on your coordination board
- [ ] Prepare sample atom payloads (APOE→CMC v1: start, partial, complete)
- [ ] Review integration validation status for all 7 systems
- [ ] Review CMC system maps/indexes for alignment with code
- [ ] Prepare status summary (test status, integration validation, blockers, questions)

**Questions to Answer:**
- Are all CMC integrations verified against actual code?
- Are system maps/indexes aligned with implementation?
- Any integration patterns that need team discussion?
- CMC ↔ CAS integration pattern confirmation needed?

**Key Documents:**
- Synthesis Preparation Guide: `SYNTHESIS_PREPARATION_GUIDE.md`
- Synthesis Agenda: `SYNTHESIS_AGENDA_2025-01-28.md`
- Your Coordination Board: `agents/atlas/COORDINATION_BOARD.md`

**Action:** Read the synthesis preparation guide and agenda, prepare your status summary, then post a synthesis preparation ack on your coordination board when ready.

---

### **Sev (HHNI) - Synthesis Session Prompt**

**Phase:** Synthesis Preparation → Synthesis Session  
**Route:** R-SYNTHESIS-001  
**Status:** Integration validation complete, CAS hooks implemented

**Your Focus Areas:**
1. **HHNI ↔ All Systems Integration Validation**
   - Review integration status for: CMC, APOE, VIF, SDF-CVF, CAS, SEG, TCS
   - Verify each integration has code + tests
   - Note any integration gaps or mismatches
   - Prepare integration validation summary

2. **CAS Activation Hooks Implementation**
   - Verify CAS activation hooks are fully implemented and tested
   - Confirm test results (2/2 passing)
   - Prepare status summary for synthesis

3. **SDF-CVF Quartet Parity Hooks**
   - Review Nova's API recommendation for quartet parity hooks
   - Prepare implementation plan if needed
   - Coordinate with Nova on timing

4. **HHNI E2E Run Coordination**
   - Coordinate with Chronos (TCS) on HHNI E2E run
   - Prepare runbook and coordination plan
   - Identify any blockers or dependencies

**Preparation Tasks:**
- [ ] Review your R-CONS-002 readiness ack on your coordination board
- [ ] Review integration validation status for all 7 systems
- [ ] Verify CAS activation hooks test results (2/2 passing)
- [ ] Review SDF-CVF quartet parity hooks API recommendation
- [ ] Coordinate with Chronos on HHNI E2E run timing
- [ ] Prepare status summary (test status, integration validation, blockers, questions)

**Questions to Answer:**
- Are all HHNI integrations verified?
- CAS activation hooks fully implemented and tested?
- SDF-CVF quartet parity hooks ready to implement?
- HHNI E2E run ready to execute with Chronos?
- Registry updates needed for closed requests?

**Key Documents:**
- Synthesis Preparation Guide: `SYNTHESIS_PREPARATION_GUIDE.md`
- Synthesis Agenda: `SYNTHESIS_AGENDA_2025-01-28.md`
- Your Coordination Board: `agents/sev/COORDINATION_BOARD.md`

**Action:** Read the synthesis preparation guide and agenda, prepare your status summary, coordinate with Chronos on E2E run, then post a synthesis preparation ack on your coordination board when ready.

---

### **Nexus (SEG) - Synthesis Session Prompt**

**Phase:** Synthesis Preparation → Synthesis Session  
**Route:** R-SYNTHESIS-001  
**Status:** Re-scanning integrations, coordination lead active

**Your Focus Areas:**
1. **SEG ↔ All Systems Integration Validation**
   - Review integration status for: CMC, HHNI, VIF, SDF-CVF, APOE, CAS, TCS
   - Complete integration re-scan if needed
   - Verify each integration has code + tests
   - Note any integration gaps or mismatches
   - Prepare integration validation summary

2. **SEG Evidence Linking (SDF-CVF Integration)**
   - Review SEG evidence node schema
   - Confirm evidence linking implementation plan
   - Coordinate with Nova (SDF-CVF) on integration pattern
   - Prepare status summary for synthesis

3. **Relationship/Consolidation Coordination**
   - Review cross-system coordination status
   - Identify any coordination blockers
   - Prepare coordination summary for synthesis

**Preparation Tasks:**
- [ ] Review your R-CONS-002 readiness ack on your coordination board
- [ ] Complete integration re-scan if needed
   - Verify all 7 integrations have code + tests
   - Note any gaps or mismatches
- [ ] Review SEG evidence node schema
- [ ] Coordinate with Nova on SEG evidence linking
- [ ] Review cross-system coordination status
- [ ] Prepare status summary (test status, integration validation, blockers, questions)

**Questions to Answer:**
- Are all SEG integrations verified?
- SEG integration re-scan complete?
- SEG evidence linking ready for SDF-CVF?
- Any cross-system coordination blockers?

**Key Documents:**
- Synthesis Preparation Guide: `SYNTHESIS_PREPARATION_GUIDE.md`
- Synthesis Agenda: `SYNTHESIS_AGENDA_2025-01-28.md`
- Your Coordination Board: `agents/nexus/COORDINATION_BOARD.md`
- Phase 4 Completion Report: `agents/nexus/AGENT_NEXUS_PHASE4_COMPLETION_REPORT.md`

**Action:** Read the synthesis preparation guide and agenda, complete integration re-scan, coordinate with Nova on evidence linking, then post a synthesis preparation ack on your coordination board when ready.

---

### **Sage (VIF) - Synthesis Session Prompt**

**Phase:** Synthesis Preparation → Synthesis Session  
**Route:** R-SYNTHESIS-001  
**Status:** Cross-validation complete, P0 orchestration work identified

**Your Focus Areas:**
1. **VIF Witness Orchestration Patterns**
   - Review orchestration gap analysis
   - Identify which flows must always emit VIF witness (P0 list)
   - Prepare mandatory vs optional pattern recommendations
   - Prepare default κ-gate/retry policy recommendations

2. **VIF ↔ All Systems Integration Validation**
   - Review integration status for: CMC, HHNI, SEG, APOE, CAS, SDF-CVF, TCS
   - Verify each integration has code + tests (219/219 tests passing)
   - Note any integration gaps or mismatches
   - Prepare integration validation summary

3. **κ-Gate Default Policies**
   - Review current κ-gate thresholds
   - Prepare default policy recommendations
   - Standardize `metadata.integration_tags` if needed

**Preparation Tasks:**
- [ ] Review your R-CONS-002 readiness ack on your coordination board
- [ ] Review orchestration gap analysis (which flows need mandatory witness creation)
- [ ] Prepare P0 list of flows that must always emit VIF witness
- [ ] Prepare default κ-gate/retry policy recommendations
- [ ] Review integration validation status (all 7 integrations, 219/219 tests passing)
- [ ] Review `metadata.integration_tags` standardization needs
- [ ] Prepare status summary (test status, integration validation, blockers, questions)

**Questions to Answer:**
- Which flows must always emit VIF witness? (P0 list)
- What are recommended default κ-gate thresholds?
- Should we standardize `metadata.integration_tags`?
- Any orchestration pattern questions for team discussion?

**Key Documents:**
- Synthesis Preparation Guide: `SYNTHESIS_PREPARATION_GUIDE.md`
- Synthesis Agenda: `SYNTHESIS_AGENDA_2025-01-28.md`
- Your Coordination Board: `agents/sage/COORDINATION_BOARD.md`

**Action:** Read the synthesis preparation guide and agenda, prepare orchestration pattern recommendations, then post a synthesis preparation ack on your coordination board when ready.

---

### **Chronos (TCS) - Synthesis Session Prompt**

**Phase:** Synthesis Preparation → Synthesis Session  
**Route:** R-SYNTHESIS-001  
**Status:** TCS tests have collection errors, HHNI E2E pending

**Your Focus Areas:**
1. **TCS ↔ All Systems Integration Validation**
   - Review integration status for: CMC, HHNI, SEG, VIF, APOE, CAS, SDF-CVF
   - Verify each integration has code + tests
   - Note any integration gaps or mismatches
   - Prepare integration validation summary

2. **HHNI E2E Run Coordination**
   - Coordinate with Sev (HHNI) on HHNI E2E run
   - Prepare runbook and coordination plan
   - Identify any blockers or dependencies
   - Prepare timeline for execution

3. **TCS Test Import Fixes**
   - Review TCS test import issues (pre-existing collection errors)
   - Prepare fix plan and timeline
   - Identify any blockers

4. **T2 Architecture File Restoration**
   - Review T2 Architecture file corruption status
   - Prepare restoration approach if needed
   - Note: This is non-blocking per R-CONS-002

**Preparation Tasks:**
- [ ] Review your R-CONS-002 readiness ack on your coordination board
- [ ] Review integration validation status (all 7 systems, code exists, matches docs)
- [ ] Coordinate with Sev on HHNI E2E run timing and plan
- [ ] Prepare HHNI E2E runbook
- [ ] Review TCS test import fix plan and timeline
- [ ] Review T2 Architecture file restoration approach (non-blocking)
- [ ] Prepare status summary (test status, integration validation, blockers, questions)

**Questions to Answer:**
- HHNI E2E run ready to execute?
- TCS test import fixes timeline?
- T2 Architecture file restoration approach?
- Partner confirmations (SDF-CVF, CAS) received?

**Key Documents:**
- Synthesis Preparation Guide: `SYNTHESIS_PREPARATION_GUIDE.md`
- Synthesis Agenda: `SYNTHESIS_AGENDA_2025-01-28.md`
- Your Coordination Board: `agents/chronos/COORDINATION_BOARD.md`

**Action:** Read the synthesis preparation guide and agenda, coordinate with Sev on E2E run, prepare test fix plan, then post a synthesis preparation ack on your coordination board when ready.

---

### **Meta (CAS) - Synthesis Session Prompt**

**Phase:** Synthesis Preparation → Synthesis Session  
**Route:** R-SYNTHESIS-001  
**Status:** 102/102 tests passing, all integrations verified

**Your Focus Areas:**
1. **CAS ↔ All Systems Integration Validation**
   - Review integration status for: CMC, HHNI, SEG, VIF, APOE, SDF-CVF, TCS, IIS
   - Verify each integration has code + tests (102/102 passing)
   - Note any integration gaps or mismatches
   - Prepare integration validation summary

2. **CAS Activation Exports (CMC Integration)**
   - Review CAS activation exports implementation plan
   - Coordinate with Atlas (CMC) on integration pattern
   - Prepare timeline for implementation
   - Review follow-ups from `CAS_FOLLOWUPS_R-CONS-002.md`

3. **CAS Orchestration Patterns**
   - Review orchestration pattern questions
   - Prepare recommendations for team discussion
   - Standardize patterns if needed

**Preparation Tasks:**
- [ ] Review your R-CONS-002 readiness ack on your coordination board
- [ ] Review integration validation status (all 8 systems, 102/102 tests passing)
- [ ] Review CAS activation exports implementation plan
- [ ] Coordinate with Atlas on CAS activation exports → CMC integration pattern
- [ ] Review follow-ups from `CAS_FOLLOWUPS_R-CONS-002.md`
- [ ] Prepare orchestration pattern recommendations
- [ ] Prepare status summary (test status, integration validation, blockers, questions)

**Questions to Answer:**
- CAS activation exports → CMC integration pattern?
- Activation exports + summary snapshots → CMC timeline?
- Any orchestration pattern questions?

**Key Documents:**
- Synthesis Preparation Guide: `SYNTHESIS_PREPARATION_GUIDE.md`
- Synthesis Agenda: `SYNTHESIS_AGENDA_2025-01-28.md`
- Your Coordination Board: `agents/META/COORDINATION_BOARD.md`
- Follow-ups: `agents/META/CAS_FOLLOWUPS_R-CONS-002.md`

**Action:** Read the synthesis preparation guide and agenda, coordinate with Atlas on activation exports, then post a synthesis preparation ack on your coordination board when ready.

---

### **Nova (SDF-CVF) - Synthesis Session Prompt**

**Phase:** Synthesis Preparation → Synthesis Session  
**Route:** R-SYNTHESIS-001  
**Status:** Cross-validation complete, synthesis questions logged

**Your Focus Areas:**
1. **SDF-CVF ↔ All Systems Integration Validation**
   - Review integration status for: CMC, HHNI, SEG, VIF, APOE, CAS, TCS
   - Verify each integration has code + tests (154/154 passing)
   - Note any integration gaps or mismatches
   - Prepare integration validation summary

2. **Integration Enhancements (Simplified → Full)**
   - Review which integrations should be enhanced
   - Prepare enhancement plan and timeline
   - Identify which integrations to keep simplified
   - Coordinate with other agents as needed

3. **Synthesis Questions Responses**
   - Review 5 synthesis questions logged for team responses
   - Prepare responses to questions received
   - Coordinate with other agents on integration patterns
   - Prepare integration test coverage strategy

4. **HHNI Quartet Parity Hooks**
   - Review API recommendation provided to Sev
   - Coordinate with Sev on implementation timing
   - Prepare status summary for synthesis

**Preparation Tasks:**
- [ ] Review your R-CONS-002 readiness ack on your coordination board
- [ ] Review integration validation status (all 7 systems, 154/154 tests passing)
- [ ] Review integration enhancement plan (which to enhance, which to keep simplified)
- [ ] Review synthesis questions and prepare responses
- [ ] Coordinate with Sev on HHNI quartet parity hooks timing
- [ ] Coordinate with Nexus on SEG evidence linking
- [ ] Prepare integration test coverage strategy
- [ ] Prepare status summary (test status, integration validation, blockers, questions)

**Questions to Answer:**
- Which integrations should be enhanced (simplified → full)?
- Responses to synthesis questions received?
- Integration test coverage strategy?
- HHNI integration enhancement timing (simplified → full)?
- SEG evidence linking implementation?
- CAS/APOE import path confirmations?

**Key Documents:**
- Synthesis Preparation Guide: `SYNTHESIS_PREPARATION_GUIDE.md`
- Synthesis Agenda: `SYNTHESIS_AGENDA_2025-01-28.md`
- Your Coordination Board: `agents/nova/COORDINATION_BOARD.md`

**Action:** Read the synthesis preparation guide and agenda, prepare enhancement plan, coordinate with other agents, then post a synthesis preparation ack on your coordination board when ready.

---

### **Alex (APOE) - Synthesis Session Prompt**

**Phase:** Synthesis Preparation → Synthesis Session  
**Route:** R-SYNTHESIS-001  
**Status:** 18/18 tests passing, spec compliant, all decisions implemented

**Your Focus Areas:**
1. **APOE→CMC v1 Integration Status**
   - Confirm 18/18 tests passing (100% pass rate)
   - Verify spec compliance (modality, tags, ordering)
   - Prepare completion summary for synthesis
   - Note: All decisions implemented, all mismatches resolved

2. **APOE ↔ All Systems Integration Validation**
   - Review integration status for: TCS, HHNI, VIF, SEG, CAS, SDF-CVF, CMC
   - Verify each integration has code + tests
   - Note any integration gaps or mismatches
   - Prepare integration validation summary

3. **Spec Sync Tool and Documentation Updates**
   - Review spec sync tool update needs
   - Prepare T-level doc update plan
   - Review system map/index alignment needs

**Preparation Tasks:**
- [ ] Review your R-CONS-002 readiness ack on your coordination board
- [ ] Review APOE→CMC v1 completion summary (18/18 tests passing)
- [ ] Review integration validation status (all 7 systems)
- [ ] Review spec sync tool update plan (if needed)
- [ ] Review T-level doc update plan
- [ ] Review system map/index alignment needs
- [ ] Prepare status summary (test status, integration validation, blockers, questions)

**Questions to Answer:**
- All APOE integrations verified?
- Spec sync tool updates needed?
- T-level doc updates timeline?
- System map/index alignment verification needed?

**Key Documents:**
- Synthesis Preparation Guide: `SYNTHESIS_PREPARATION_GUIDE.md`
- Synthesis Agenda: `SYNTHESIS_AGENDA_2025-01-28.md`
- Your Coordination Board: `agents/alex/COORDINATION_BOARD.md`
- Decisions: `agents/alex/APOE_CMC_V1_DECISIONS.md`
- Audit Report: `agents/alex/APOE_CMC_INTEGRATION_R-CONS-002.md`

**Action:** Read the synthesis preparation guide and agenda, prepare status summary, then post a synthesis preparation ack on your coordination board when ready.

---

## 📊 **Synthesis Session Structure**

### **Part 1: Status Review (30 min)**
- Each agent: 3-5 min status summary
  - Test status
  - Integration validation status
  - Documentation alignment
  - Goal progress (G1/G2/G3)

### **Part 2: Blocker Resolution (30 min)**
- Review all blockers
- Assign owners and timelines
- Resolve coordination blockers

### **Part 3: Open Questions (30 min)**
- Answer integration pattern questions
- Decide on orchestration patterns
- Standardize policies and defaults

### **Part 4: Next Steps (15 min)**
- Directive 5 P0 updates completion
- System map/index alignment
- T-level doc updates
- Chat/IDE orchestration integration prep

---

## ✅ **Success Criteria**

**Before Synthesis:**
- ✅ All agents have read synthesis agenda
- ✅ All agents have prepared status summaries
- ✅ All blockers are documented
- ✅ All open questions are listed

**After Synthesis:**
- ✅ All blockers resolved or assigned
- ✅ All open questions answered
- ✅ Directive 5 P0 updates planned
- ✅ System maps/indexes alignment planned
- ✅ T-level doc updates planned
- ✅ Chat/IDE orchestration integration roadmap created

---

## 🚀 **Next Steps**

1. **All Agents:** Read your tailored prompt above
2. **All Agents:** Read the synthesis preparation guide and agenda
3. **All Agents:** Complete your preparation tasks
4. **All Agents:** Post synthesis preparation ack on your coordination board
5. **Codex/Aether:** Schedule synthesis session once all agents are prepared
6. **Synthesis Session:** Execute per agenda structure
7. **Post-Synthesis:** Update all tracking documents with outcomes

---

**Status:** ✅ **8/8 Agents Ready** - Preparation prompts ready  
**Next:** All agents prepare → Synthesis session → Finalize consolidation
