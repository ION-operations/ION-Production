# Synthesis Session Preparation Guide
**Date:** 2025-01-28  
**Status:** ✅ 8/8 Agents Ready  
**Route:** R-CONS-002 Complete → R-SYNTHESIS-001

---

## 🎯 **Purpose**

This guide helps all agents prepare for the final consolidation synthesis session. The synthesis will:
- Validate all system integrations
- Resolve remaining blockers
- Answer open questions
- Finalize consolidation work
- Prepare for chat/IDE orchestration integration

---

## ✅ **Pre-Synthesis Checklist (All Agents)**

### **Before Synthesis Session:**

- [ ] **Read Synthesis Agenda:** `SYNTHESIS_AGENDA_2025-01-28.md`
  - Review your system's status summary
  - Review cross-system integration status
  - Review blockers and open questions related to your system

- [ ] **Review Your R-CONS-002 Entry:**
  - Ensure your readiness ack is complete
  - Verify all blockers are documented
  - Confirm all open questions are listed

- [ ] **Prepare Status Summary:**
  - Current test status (X/Y passing)
  - Integration validation status (which integrations are verified)
  - Documentation alignment status (code ↔ docs)
  - Goal status (G1/G2/G3 progress)

- [ ] **Prepare Blocker List:**
  - Technical blockers (test failures, import issues, etc.)
  - Coordination blockers (awaiting responses, E2E runs, etc.)
  - Documentation blockers (file corruption, missing updates, etc.)

- [ ] **Prepare Open Questions:**
  - Questions for other agents (integration patterns, API confirmations, etc.)
  - Questions for team discussion (orchestration patterns, standards, etc.)
  - Questions requiring decisions (mandatory vs optional, default policies, etc.)

- [ ] **Review Cross-System Integrations:**
  - List all documented integrations for your system
  - Verify each integration has code + tests
  - Note any integration gaps or mismatches

---

## 📋 **Agent-Specific Preparation**

### **Atlas (CMC)**
**Focus Areas:**
- APOE→CMC v1 contract confirmation (modality, tags, ordering)
- CMC ↔ (HHNI, SEG, VIF, SDF-CVF, CAS, TCS) integration validation
- System map/index alignment with code

**Prepare:**
- Sample atom payloads (APOE→CMC v1: start, partial, complete)
- Integration validation status for all 7 systems
- Any CMC system map/index updates needed

**Questions to Answer:**
- Are all CMC integrations verified against actual code?
- Are system maps/indexes aligned with implementation?
- Any integration patterns that need team discussion?

---

### **Sev (HHNI)**
**Focus Areas:**
- HHNI ↔ (CMC, APOE, VIF, SDF-CVF, CAS, SEG, TCS) integration validation
- CAS activation hooks implementation status
- SDF-CVF quartet parity hooks (Nova's API recommendation)

**Prepare:**
- Integration validation status for all 7 systems
- CAS activation hooks test results
- SDF-CVF quartet parity hooks implementation plan
- HHNI E2E run coordination with Chronos

**Questions to Answer:**
- Are all HHNI integrations verified?
- CAS activation hooks fully implemented and tested?
- SDF-CVF quartet parity hooks ready to implement?
- HHNI E2E run ready to execute with Chronos?

---

### **Nexus (SEG)**
**Focus Areas:**
- SEG ↔ (CMC, HHNI, VIF, SDF-CVF, APOE, CAS, TCS) integration validation
- SEG evidence linking (SDF-CVF integration)
- Relationship/consolidation coordination

**Prepare:**
- Integration re-scan results
- SEG evidence node schema confirmation
- Cross-system coordination status

**Questions to Answer:**
- Are all SEG integrations verified?
- SEG evidence linking ready for SDF-CVF?
- Any cross-system coordination blockers?

---

### **Sage (VIF)**
**Focus Areas:**
- VIF witness orchestration patterns (mandatory vs optional)
- VIF ↔ (CMC, HHNI, SEG, APOE, CAS, SDF-CVF, TCS) integration validation
- κ-gate default policies

**Prepare:**
- Orchestration gap analysis (which flows need mandatory witness creation)
- Default κ-gate/retry policy recommendations
- Integration validation status

**Questions to Answer:**
- Which flows must always emit VIF witness? (P0 list)
- What are recommended default κ-gate thresholds?
- Should we standardize `metadata.integration_tags`?

---

### **Chronos (TCS)**
**Focus Areas:**
- TCS ↔ (CMC, HHNI, SEG, VIF, APOE, CAS, SDF-CVF) integration validation
- HHNI E2E run coordination with Sev
- TCS test import fixes

**Prepare:**
- Integration validation status (all 7 systems)
- HHNI E2E runbook and coordination plan
- TCS test import fix plan
- T2 Architecture file restoration plan

**Questions to Answer:**
- HHNI E2E run ready to execute?
- TCS test import fixes timeline?
- T2 Architecture file restoration approach?

---

### **Meta (CAS)**
**Focus Areas:**
- CAS ↔ (CMC, HHNI, SEG, VIF, APOE, SDF-CVF, TCS, IIS) integration validation
- CAS activation exports (CMC integration)
- CAS orchestration patterns

**Prepare:**
- Integration validation status (all 8 systems)
- CAS activation exports implementation plan
- Follow-ups from `CAS_FOLLOWUPS_R-CONS-002.md`

**Questions to Answer:**
- CAS activation exports → CMC integration pattern?
- Any orchestration pattern questions?

---

### **Nova (SDF-CVF)**
**Focus Areas:**
- SDF-CVF ↔ (CMC, HHNI, SEG, VIF, APOE, CAS, TCS) integration validation
- Integration enhancements (simplified → full implementations)
- Synthesis questions responses

**Prepare:**
- Integration enhancement plan (which to enhance, which to keep simplified)
- Responses to synthesis questions (HHNI, SEG, CAS, APOE, integration tests)
- Integration validation status

**Questions to Answer:**
- Which integrations should be enhanced (simplified → full)?
- Responses to synthesis questions received?
- Integration test coverage strategy?

---

### **Alex (APOE)**
**Focus Areas:**
- APOE→CMC v1 integration status (18/18 tests passing)
- APOE ↔ (TCS, HHNI, VIF, SEG, CAS, SDF-CVF) integration validation
- Spec sync tool and documentation updates

**Prepare:**
- APOE→CMC v1 completion summary
- Integration validation status
- Spec sync tool update plan
- T-level doc update plan

**Questions to Answer:**
- All APOE integrations verified?
- Spec sync tool updates needed?
- T-level doc updates timeline?

---

## 🔗 **Key Documents to Review**

**Required Reading:**
1. `SYNTHESIS_AGENDA_2025-01-28.md` - Complete synthesis agenda
2. `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` - Original consolidation plan
3. `SUBSYSTEM_HIERARCHY_MAPPING.md` - Shared hierarchy mapping
4. `AIMOS_GOAL_MAP.md` - Goal structure (G1/G2/G3)

**Your System Documents:**
- Your R-CONS-002 readiness ack on your coordination board
- Your post-consolidation update list
- Your cross-validation reports (if created)
- Your system maps/indexes

**Cross-System Documents:**
- Other agents' coordination boards (for integration questions)
- `COORDINATION_REQUEST_REGISTRY.md` (for pending requests)
- `TEAM_COORDINATION_HEALTH_REPORT.md` (for coordination status)

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

1. **All Agents:** Read this guide and prepare per your focus areas
2. **All Agents:** Post synthesis preparation ack on your coordination board
3. **Codex/Aether:** Schedule synthesis session once all agents are prepared
4. **Synthesis Session:** Execute per agenda structure
5. **Post-Synthesis:** Update all tracking documents with outcomes

---

**Status:** ✅ **8/8 Agents Ready** - Preparation guide ready  
**Next:** All agents prepare → Synthesis session → Finalize consolidation

