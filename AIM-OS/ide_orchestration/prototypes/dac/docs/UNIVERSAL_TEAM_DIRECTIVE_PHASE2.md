# Universal Team Directive — All Agents Read This

**Date:** 2025-01-27  
**Phase:** Phase 2 - Cross-Validation & Integration  
**Status:** Ready to Begin  
**Priority:** P0 (CRITICAL)

---

## 📊 **CURRENT STATUS**

### **Completed Directives:**
- ✅ **Protocol Acknowledgements:** 8/8 complete (100%)
- ✅ **Directive 1 (Consolidate Your Work):** 8/8 complete (100%)
- ✅ **Directive 2 (Contribute to Shared Hierarchy Mapping):** 8/8 complete (100%)
- ✅ **Directive 4 (Create Post-Consolidation Update List):** 8/8 complete (100%)

### **Overall Progress:**
- **Completion:** ~50% (Directives 1, 2, and 4 complete)
- **Next Phase:** Directive 3 (Cross-Validation) and Directive 5 (Subsystem Integration)

---

## 🎯 **WHAT TO DO NEXT**

### **Option 1: Begin Directive 3 (Cross-Validation)** — **RECOMMENDED FIRST**

**Purpose:** Validate bidirectional connections between systems  
**Timeline:** Target completion within 48 hours (collaborative validation)  
**Priority:** P0 (CRITICAL - ensures connection accuracy before integration)

**Process:**
1. Review `SUBSYSTEM_HIERARCHY_MAPPING.md` for all system hierarchies
2. Identify connections your system claims with other systems
3. Check with the other agent(s) to confirm bidirectional agreement
4. Document validation results in your per-agent board
5. Update connection matrices if discrepancies are found

**Detailed Instructions:** See "Directive 3 (Cross-Validation) — Detailed Instructions" below

---

### **Option 2: Begin Directive 5 (Subsystem Integration)** — **CAN RUN IN PARALLEL**

**Purpose:** Execute updates from your post-consolidation update list  
**Timeline:** Ongoing (execute P0 first, then P1/P2 as time permits)  
**Priority:** P0 (CRITICAL - foundation for all documentation updates)

**Process:**
1. Review your `AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md`
2. Start with P0 (Critical) updates first
3. Update system maps, indexes, and documentation as specified
4. Track progress in your update list document
5. Post completion milestones to your per-agent board

**Detailed Instructions:** See "Directive 5 (Subsystem Integration) — Detailed Instructions" below

---

## 💡 **RECOMMENDATION**

**Start with Directive 3 (Cross-Validation)** to ensure connection accuracy before integration. Directive 5 can run in parallel once P0 items are identified.

---

## 📁 **KEY FILES TO REFERENCE**

### **For Directive 3 (Cross-Validation):**
- `SUBSYSTEM_HIERARCHY_MAPPING.md` — Shared hierarchy mapping (all systems)
- Your system map: `knowledge_architecture/systems/[your-system]/system.map.lucid.json5`
- Other agents' system maps (for validation)
- Your per-agent board: `agents/[your-name]/COORDINATION_BOARD.md` (post validation results)

### **For Directive 5 (Subsystem Integration):**
- Your update list: `agents/[your-name]/AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md`
- Your system map: `knowledge_architecture/systems/[your-system]/system.map.lucid.json5`
- Your system index: `knowledge_architecture/systems/[your-system]/system.index.lucid.json5`
- Your T0-T4+ documentation: `knowledge_architecture/systems/[your-system]/T0_executive.md` (and T1, T2, T3, T4)
- Subsystem documentation: `knowledge_architecture/systems/[your-system]/subsystems/`
- `HIERARCHICAL_NAVIGATION_INDEX.md` — Update if needed
- `SUPER_INDEX.md` — Update if needed

### **General Reference Files:**
- `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` — Full directive details
- `AGENT_CONSOLIDATION_PROGRESS_STATUS.md` — Current progress tracking
- `AGENT_COORDINATION_ROUTER.md` — Coordination routing
- `NEW_BOARD_PROTOCOL.md` — Posting protocol

---

## 🔍 **DIRECTIVE 3 (CROSS-VALIDATION) — DETAILED INSTRUCTIONS**

### **Step 1: Identify Your Connections**

1. Review your system's connection matrix in `SUBSYSTEM_HIERARCHY_MAPPING.md`
2. List all systems you claim connections with (bidirectional)
3. Note the connection type, data flow, priority, and integration points

**Example:**
- CMC claims: TCS ↔ CMC, APOE ↔ CMC, SEG ↔ CMC, CAS ↔ CMC, VIF ↔ CMC, HHNI ← CMC, SDF-CVF ↔ CMC

### **Step 2: Validate with Other Agents**

For each connection:
1. Check the other system's hierarchy mapping in `SUBSYSTEM_HIERARCHY_MAPPING.md`
2. Verify they also claim the connection to you
3. Check data flow, priorities, and integration points match
4. Verify connection notation (tags, ports, integration patterns)

**Validation Checklist:**
- [ ] Other system lists connection to your system
- [ ] Connection direction matches (bidirectional ↔ or unidirectional →/←)
- [ ] Data flow patterns match
- [ ] Priority levels match
- [ ] Integration points/ports match
- [ ] Connection notation matches

### **Step 3: Document Validation**

Post to your per-agent board:

**Format:**
```
### [2025-01-27 | Route R-VALIDATE-001] [Your Name] -> Team : Cross-Validation Complete

**Validated Connections (✅):**
- [System A] ↔ [Your System]: Confirmed (data flow, priority, integration points match)
- [System B] ↔ [Your System]: Confirmed (all details verified)

**Discrepancies Found (⚠️):**
- [System C] ↔ [Your System]: Data flow mismatch (your system: X → Y, their system: Y → X)
- [System D] ↔ [Your System]: Priority mismatch (your system: P0, their system: P1)

**Missing Connections (❌):**
- [System E] ↔ [Your System]: Not found in other system's mapping (needs coordination)

**Resolution Actions:**
- [System C]: Coordinated with [Agent Name], updated data flow to match
- [System D]: Coordinated with [Agent Name], aligned priority to P0
- [System E]: Contacted [Agent Name] to add missing connection

**Status:** ✅ Complete - All connections validated and resolved
```

### **Step 4: Resolve Discrepancies**

1. Coordinate with other agents to fix mismatches
2. Update system maps if needed
3. Update `SUBSYSTEM_HIERARCHY_MAPPING.md` if needed
4. Re-validate after fixes

**Coordination Protocol:**
- Post to your per-agent board with route ID: `R-VALIDATE-001`
- Tag the other agent in your post
- Document resolution in both agents' boards
- Update shared mapping document if changes made

---

## 🏗️ **DIRECTIVE 5 (SUBSYSTEM INTEGRATION) — DETAILED INSTRUCTIONS**

### **Step 1: Review Your Update List**

1. Open `agents/[your-name]/AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md`
2. Identify all P0 (Critical) items
3. Prioritize by category: System Map → Index → T0-T4+ → Subsystem Docs

**Update Order:**
1. **System Map** (P0) - Foundation for all other updates
2. **System Index** (P0) - Foundation for navigation and cross-references
3. **T0-T4+ Docs** (P1) - Reflect consolidation in all documentation levels
4. **Subsystem Docs** (P1) - Complete subsystem documentation
5. **Cross-References** (P1) - Verify all bidirectional links
6. **Navigation Index** (P1) - Update master navigation

### **Step 2: Execute P0 Updates**

**System Map Updates:**
- [ ] Add `subsystems` array with all subsystems
- [ ] Add `components` arrays for each subsystem
- [ ] Update `integrationPoints` array with tagged integration points
- [ ] Add/Update `connectionMatrix` section
- [ ] Update `externalEdges` array with connection notation

**System Index Updates:**
- [ ] Add `subsystems` section with subsystem entries
- [ ] Add `crossSystemLinks` section with all connections
- [ ] Add `integrationMetadata` section for each integration

**T0-T4+ Documentation Updates:**
- [ ] Update T0 executive summary (reflect consolidation findings)
- [ ] Update T1 overview (add subsystem sections)
- [ ] Update T2 architecture (hierarchy structure)
- [ ] Update T3 detailed (subsystem details)
- [ ] Update T4 complete (full reference)

**Subsystem Documentation Updates:**
- [ ] Create/Update subsystem README files
- [ ] Document all integration points
- [ ] Document all cross-system connections

### **Step 3: Track Progress**

1. Mark items as complete in your update list document
2. Post milestones to your per-agent board

**Format:**
```
### [2025-01-27 | Route R-INTEGRATE-001] [Your Name] -> Team : P0 Updates Complete

**Completed:**
- ✅ System Map Updates (subsystems, components, integration points, connection matrix)
- ✅ System Index Updates (subsystem references, cross-system links, integration metadata)
- ✅ T0-T4+ Documentation Updates (all 5 levels reflect consolidation findings)

**In Progress:**
- ⏳ Subsystem Documentation Updates (3/3 READMEs complete)

**Next:**
- ⏳ Cross-Reference Updates (verify all bidirectional links)
- ⏳ Navigation Index Updates (add subsystem sections)

**Status:** P0 Complete, P1 In Progress
```

### **Step 4: Continue with P1/P2**

After P0 complete:
1. Proceed with P1 (High) items
2. Then P2 (Medium) items
3. Update tracking documents as you progress
4. Post completion milestones

---

## 📝 **POSTING PROTOCOL**

### **All Updates Go To:**
- Your per-agent board: `agents/[your-name]/COORDINATION_BOARD.md`

### **Route IDs:**
- `R-VALIDATE-001` for Directive 3 (Cross-Validation)
- `R-INTEGRATE-001` for Directive 5 (Subsystem Integration)

### **Post Format:**
```
### [YYYY-MM-DD | Route R-XXX-XXX] [Your Name] -> Audience : Summary

**Details:**
- Item 1: Status
- Item 2: Status

**Links:** [Relevant Documents]

**Status:** OPEN / IN_PROGRESS / DONE
```

### **Follow:**
- `NEW_BOARD_PROTOCOL.md` for posting rules
- Append-only timeline (strike through superseded entries)
- Include timestamps, summaries, and links to relevant documents

---

## ⏰ **TIMELINE**

### **Directive 3 (Cross-Validation):**
- **Target:** Completion within 48 hours (collaborative validation)
- **Priority:** P0 (CRITICAL - ensures connection accuracy)

### **Directive 5 (Subsystem Integration):**
- **P0 Updates:** Target completion within 3-5 days
- **P1 Updates:** Ongoing (execute after P0)
- **P2 Updates:** As time permits

### **Directive 6 (T0-T4+ Documentation Updates):**
- **Start:** After Directive 5 P0 complete
- **Timeline:** Ongoing

---

## ❓ **QUESTIONS?**

### **Check These Files:**
- `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` — Full directive details
- `AGENT_CONSOLIDATION_PROGRESS_STATUS.md` — Current progress tracking
- `AGENT_COORDINATION_ROUTER.md` — Coordination routing
- `NEW_BOARD_PROTOCOL.md` — Posting protocol

### **Post Questions To:**
- Your per-agent board: `agents/[your-name]/COORDINATION_BOARD.md`
- Others can see via router: `AGENT_COORDINATION_ROUTER.md`

### **Coordinate With:**
- Other agents for cross-validation (Directive 3)
- Other agents for connection resolution (Directive 3)
- Team leads for integration questions (Directive 5)

---

## ✅ **SUCCESS CRITERIA**

### **Directive 3 Complete When:**
- [ ] All connections validated with other agents
- [ ] All discrepancies resolved
- [ ] All validation results posted to per-agent boards
- [ ] Connection matrices updated if needed

### **Directive 5 P0 Complete When:**
- [ ] System Map updates complete
- [ ] System Index updates complete
- [ ] T0-T4+ documentation updates complete
- [ ] Subsystem documentation updates complete
- [ ] All P0 items marked complete in update list

---

## 🎯 **NEXT STEPS SUMMARY**

1. **Read this directive** (you're doing it now ✅)
2. **Choose your starting point:**
   - **Recommended:** Begin Directive 3 (Cross-Validation)
   - **Alternative:** Begin Directive 5 P0 (System Map & Index)
3. **Follow detailed instructions** for your chosen directive
4. **Post progress** to your per-agent board
5. **Coordinate with other agents** as needed
6. **Track completion** in your update list and progress status

---

**Status:** Ready to Begin  
**All Agents:** Read, acknowledge, and begin Directive 3 or 5  
**Questions:** Post to your per-agent board  
**Coordination:** Use router and per-agent boards

---

**Last Updated:** 2025-01-27  
**Next Review:** After Directive 3 completion or Directive 5 P0 completion

