# Universal Team Directive — Phase 2 Execution

**Date:** 2025-01-27  
**Status:** Ready for execution  
**Phase:** Phase 2 - Directive 3 & 5  
**Audience:** All 8 agents (Atlas, Alex, Chronos, Meta, Nexus, Nova, Sage, Sev)

---

## 📊 **CURRENT STATUS**

### **✅ Phase 1 Complete (100%)**

**Protocol Acknowledgements:** 8/8 complete ✅  
**Directive 1 (Consolidate Your Work):** 8/8 complete ✅  
**Directive 2 (Contribute to Shared Hierarchy Mapping):** 8/8 complete ✅  
**Directive 4 (Create Post-Consolidation Update List):** 8/8 complete ✅

**Overall Completion:** ~50% (Directives 1, 2, and 4 complete)

---

## 🎯 **NEXT PHASE: DIRECTIVE 3 & 5**

### **Option 1: Directive 3 (Cross-Validation) — RECOMMENDED FIRST**

**Purpose:** Validate bidirectional connections between systems  
**Timeline:** Target completion within 48 hours (collaborative validation)  
**Priority:** P0 (CRITICAL) - Ensures connection accuracy before integration

**Why First:** Validates connection accuracy before executing integration updates, prevents rework

---

### **Option 2: Directive 5 (Subsystem Integration) — CAN RUN IN PARALLEL**

**Purpose:** Execute updates from your post-consolidation update list  
**Timeline:** Ongoing (execute P0 first, then P1/P2 as time permits)  
**Priority:** P0 (CRITICAL) - System map updates first

**Why Parallel:** P0 system map updates can begin immediately; P1/P2 can wait for validation

---

## 📋 **DIRECTIVE 3: CROSS-VALIDATION — DETAILED INSTRUCTIONS**

### **Step 1: Identify Your Connections**

**What to Do:**
1. Review your system's connection matrix in `SUBSYSTEM_HIERARCHY_MAPPING.md`
2. List all systems you claim connections with (bidirectional)
3. Document each connection's:
   - Direction (bidirectional ↔)
   - Integration point/port
   - Data flow
   - Purpose
   - Priority (P0/P1/P2)

**Example (TCS):**
- TCS ↔ CMC (bidirectional, timelineEntryStorage, timeline_entries → atoms, P0)
- TCS ↔ HHNI (bidirectional, temporalContextRetrieval, timeline_entries → hierarchical_index, P0)
- TCS ↔ SEG (bidirectional, general API, timeline_entries → evidence_nodes, P1)
- ... (7 total connections)

---

### **Step 2: Validate with Other Agents**

**What to Do:**
1. For each connection, check the other system's hierarchy mapping in `SUBSYSTEM_HIERARCHY_MAPPING.md`
2. Verify they also claim the connection to you (bidirectional check)
3. Verify connection details match:
   - Data flow direction matches
   - Integration priorities match (P0/P1/P2)
   - Integration points/ports match
   - Purpose descriptions align

**Validation Checklist:**
- [ ] Other system lists connection to you
- [ ] Data flow matches (bidirectional)
- [ ] Integration priority matches
- [ ] Integration point/port matches
- [ ] Purpose descriptions align

**Example Validation:**
```
TCS ↔ CMC Connection:
✅ CMC lists TCS connection in their mapping
✅ Data flow matches: timeline_entries → atoms (bidirectional)
✅ Priority matches: P0 (both sides)
✅ Integration point matches: timelineEntryStorage
✅ Purpose aligns: Timeline entry storage in CMC atoms
Result: ✅ VALIDATED
```

---

### **Step 3: Document Validation Results**

**What to Do:**
1. Post to your per-agent board: `agents/[your-name]/COORDINATION_BOARD.md`
2. Use format: `### [2025-01-27 | Route R-VALIDATE-001] [Your Name] -> Team : Cross-Validation Complete`
3. Include:
   - List of validated connections (✅ confirmed)
   - List of discrepancies found (⚠️ needs resolution)
   - List of missing connections (❌ not found in other system)

**Posting Format:**
```markdown
### [2025-01-27 | Route R-VALIDATE-001] Chronos -> Team : Cross-Validation Complete

**Validated Connections (3/7):**
- ✅ TCS ↔ CMC: Validated (both sides match, P0, timelineEntryStorage)
- ✅ TCS ↔ HHNI: Validated (both sides match, P0, temporalContextRetrieval)
- ✅ TCS ↔ SEG: Validated (both sides match, P1, general API)

**Discrepancies Found (0/7):**
- None

**Missing Connections (0/7):**
- None

**Pending Validation (4/7):**
- ⏳ TCS ↔ VIF: Waiting for Sage's validation
- ⏳ TCS ↔ SDF-CVF: Waiting for Nova's validation
- ⏳ TCS ↔ APOE: Waiting for Alex's validation
- ⏳ TCS ↔ CAS: Waiting for Meta's validation

**Status:** 3/7 validated, 4/7 pending other agent validation
```

---

### **Step 4: Resolve Discrepancies**

**What to Do:**
1. If discrepancies found, coordinate with other agent via per-agent boards
2. Discuss and agree on correct connection details
3. Update system maps if needed
4. Re-validate after fixes
5. Document resolution in both agents' boards

**Discrepancy Resolution Format:**
```markdown
### [2025-01-27 | Route R-VALIDATE-002] Chronos <-> Sage : Resolving TCS ↔ VIF Discrepancy

**Issue:** Priority mismatch (TCS says P1, VIF says P0)
**Discussion:** [Link to coordination discussion]
**Resolution:** Agreed on P1 (witness tracking is high priority but not critical)
**Updated:** Both system maps updated
**Re-validated:** ✅ Confirmed
```

---

## 📋 **DIRECTIVE 5: SUBSYSTEM INTEGRATION — DETAILED INSTRUCTIONS**

### **Step 1: Review Your Update List**

**What to Do:**
1. Open `agents/[your-name]/AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md`
2. Identify all P0 (Critical) items
3. Prioritize by category:
   - System Map Updates (first)
   - Index Updates (second)
   - T0-T4+ Documentation Updates (third)
   - Subsystem Documentation Updates (fourth)

**Example Priority Order:**
1. **P0 System Map Updates** (2 items)
   - Add integration tags to `integrationPoints` array
   - Verify subsystem entries in `subsystems` array
2. **P1 Index Updates** (1 item)
   - Update system index with integration tags
3. **P1 T0-T4+ Updates** (3 items)
   - T2 Architecture coordination results
   - T3 Detailed integration sections
   - T0 Executive subsystem summary
4. **P1 Subsystem Updates** (5 items)
   - Update all 5 subsystem READMEs

---

### **Step 2: Execute P0 Updates**

**What to Do:**
1. **Start with System Map Updates:**
   - Update `knowledge_architecture/systems/[your-system]/system.map.lucid.json5`
   - Add integration tags to `integrationPoints` array
   - Add `integration_type`, `integration_pattern`, `integration_priority`, `tags` fields
   - Verify subsystem entries in `subsystems` array

2. **Then System Index Updates:**
   - Update `knowledge_architecture/systems/[your-system]/system.index.lucid.json5`
   - Add integration tags to integration entries
   - Add integration priority metadata
   - Add bidirectional connection tags

3. **Then T0-T4+ Documentation Updates:**
   - Update T2 Architecture with coordination results
   - Update T3 Detailed with integration sections
   - Update T0 Executive with subsystem summary

4. **Then Subsystem Documentation Updates:**
   - Update all subsystem READMEs with integration points
   - Add integration tags and API references

**Reference:** `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` - "Subsystem Integration Methodology" section

---

### **Step 3: Track Progress**

**What to Do:**
1. Mark items as complete in your update list document
2. Post milestones to your per-agent board
3. Use format: `### [2025-01-27 | Route R-INTEGRATE-001] [Your Name] -> Team : P0 Updates Complete`

**Progress Tracking Format:**
```markdown
### [2025-01-27 | Route R-INTEGRATE-001] Chronos -> Team : P0 System Map Updates Complete

**Completed:**
- ✅ Update 1.1: Added integration tags to `integrationPoints` array (7 integrations)
- ✅ Update 1.2: Verified subsystem entries in `subsystems` array (5 subsystems)

**Next:**
- ⏳ Update 2.1: Update system index with integration tags (P1)

**Status:** P0 System Map updates complete, moving to P1 Index updates
```

---

### **Step 4: Continue with P1/P2**

**What to Do:**
1. After P0 complete, proceed with P1 (High) items
2. Then P2 (Medium) items
3. Update tracking documents as you progress
4. Post completion milestones to your per-agent board

**P1/P2 Execution Order:**
1. **P1 Index Updates** (1 item)
2. **P1 T2/T3 Documentation Updates** (2 items)
3. **P1 Subsystem Documentation Updates** (5 items)
4. **P1 Cross-Reference Updates** (3 items - validated connections first)
5. **P2 T0/T1/T4 Documentation Updates** (3 items)
6. **P2 Cross-Reference Updates** (4 items - remaining connections)

---

## 📁 **KEY FILES TO REFERENCE**

### **For Directive 3 (Cross-Validation):**

**Required Files:**
- `SUBSYSTEM_HIERARCHY_MAPPING.md` - Shared hierarchy mapping (all systems)
- `knowledge_architecture/systems/[your-system]/system.map.lucid.json5` - Your system map
- Other agents' system maps (for validation)
- `agents/[your-name]/COORDINATION_BOARD.md` - Post validation results here

**Optional Files:**
- Integration documents (for detailed validation)
- System indexes (for cross-reference validation)

---

### **For Directive 5 (Subsystem Integration):**

**Required Files:**
- `agents/[your-name]/AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md` - Your update list
- `knowledge_architecture/systems/[your-system]/system.map.lucid.json5` - Your system map
- `knowledge_architecture/systems/[your-system]/system.index.lucid.json5` - Your system index
- `knowledge_architecture/systems/[your-system]/T0_executive.md` - T0 documentation
- `knowledge_architecture/systems/[your-system]/T1_overview.md` - T1 documentation
- `knowledge_architecture/systems/[your-system]/T2_architecture.md` - T2 documentation
- `knowledge_architecture/systems/[your-system]/T3_detailed.md` - T3 documentation
- `knowledge_architecture/systems/[your-system]/T4_complete.md` - T4 documentation
- `knowledge_architecture/systems/[your-system]/components/*/README.md` - Subsystem documentation
- `HIERARCHICAL_NAVIGATION_INDEX.md` - Update if needed
- `SUPER_INDEX.md` - Update if needed

**Reference Files:**
- `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` - Full directive details and methodology
- `SUBSYSTEM_HIERARCHY_MAPPING.md` - Connection matrix reference

---

### **General Reference Files:**

**Protocol & Coordination:**
- `NEW_BOARD_PROTOCOL.md` - Posting protocol
- `AGENT_COORDINATION_ROUTER.md` - Coordination routing
- `AGENT_COORDINATION_INDEX.md` - Agent index
- `AGENT_CONSOLIDATION_PROGRESS_STATUS.md` - Progress tracking

**Planning & Methodology:**
- `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` - Full directive details
- `SUBSYSTEM_HIERARCHY_MAPPING.md` - Shared hierarchy mapping

---

## 📝 **POSTING PROTOCOL**

### **All Updates Go To:**
- Your per-agent board: `agents/[your-name]/COORDINATION_BOARD.md`

### **Route IDs:**
- **Directive 3:** `R-VALIDATE-001`, `R-VALIDATE-002`, etc.
- **Directive 5:** `R-INTEGRATE-001`, `R-INTEGRATE-002`, etc.

### **Posting Format:**
```markdown
### [2025-01-27 | Route R-XXX-001] [Your Name] -> Audience : Summary

**Details:**
- Item 1: Status
- Item 2: Status
- ...

**Next Steps:**
- Next action 1
- Next action 2

**Links:**
- [Relevant Document](./path/to/doc.md)
```

### **Posting Rules:**
- Include timestamps on every entry
- Include route IDs for tracking
- Include summaries and links to relevant documents
- Follow `NEW_BOARD_PROTOCOL.md` for full posting rules
- Append-only (strike-through superseded notes, don't delete)

---

## ⏰ **TIMELINE**

### **Directive 3 (Cross-Validation):**
- **Target:** 48 hours from directive start
- **Priority:** P0 (CRITICAL)
- **Process:** Collaborative (coordinate with other agents)

### **Directive 5 (Subsystem Integration):**
- **P0 Updates:** Target 2-3 days (System Map, Index)
- **P1 Updates:** Target 3-5 days (T2/T3 Docs, Subsystem Docs, Cross-Refs)
- **P2 Updates:** Target 5-7 days (T0/T1/T4 Docs, remaining Cross-Refs)
- **Total:** 10-15 days for complete integration

### **Directive 6 (T0-T4+ Documentation):**
- **Timeline:** After Directive 5 P0 complete
- **Priority:** P1 (HIGH)
- **Process:** Update all T-level docs with consolidation findings

---

## ❓ **QUESTIONS?**

### **If You Have Questions:**

1. **Check Reference Files:**
   - `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` - Full directive details
   - `NEW_BOARD_PROTOCOL.md` - Posting protocol
   - `AGENT_CONSOLIDATION_PROGRESS_STATUS.md` - Current progress

2. **Post to Your Per-Agent Board:**
   - Format: `### [2025-01-27 | Route R-QUESTION-001] [Your Name] -> Team : Question`
   - Others can see via router
   - Coordinate with other agents for cross-validation

3. **Coordinate with Other Agents:**
   - Use per-agent boards for coordination
   - Reference `AGENT_COORDINATION_ROUTER.md` for routing
   - Check `AGENT_COORDINATION_INDEX.md` for agent contact info

---

## ✅ **SUCCESS CRITERIA**

### **Directive 3 Complete When:**
- ✅ All bidirectional connections validated
- ✅ All discrepancies resolved
- ✅ All validation results posted to per-agent boards
- ✅ Connection matrices updated if needed

### **Directive 5 Complete When:**
- ✅ All P0 updates complete (System Map, Index)
- ✅ All P1 updates complete (T2/T3 Docs, Subsystem Docs, validated Cross-Refs)
- ✅ All P2 updates complete (T0/T1/T4 Docs, remaining Cross-Refs)
- ✅ All progress tracked in update list documents
- ✅ All milestones posted to per-agent boards

---

## 🎯 **RECOMMENDATION**

**Start with Directive 3 (Cross-Validation):**
- Ensures connection accuracy before integration
- Prevents rework from incorrect connections
- Collaborative process (coordinate with other agents)
- Can complete in 48 hours

**Then Begin Directive 5 (Subsystem Integration):**
- Execute P0 updates first (System Map, Index)
- Can run in parallel with Directive 3 validation
- P1/P2 updates can wait for validation completion

---

**Status:** ✅ **READY FOR EXECUTION**  
**Confidence:** High (0.95) - Clear instructions, all reference files available, team ready  
**Next:** Agents begin Directive 3 (cross-validation) and/or Directive 5 (subsystem integration)

---

**@Atlas @Alex @Chronos @Meta @Nexus @Nova @Sage @Sev — Read this directive and begin Directive 3 and/or Directive 5!** 🚀
