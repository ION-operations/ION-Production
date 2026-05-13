# Universal Team Directive — All Agents Read This
**Date:** 2025-01-27  
**Status:** ACTIVE - Next Phase Ready  
**Priority:** P0 (CRITICAL)  
**Applicable To:** All 8 System Specialist Agents

---

## 📊 **CURRENT STATUS**

### **Completed Directives (8/8 - 100%):**

✅ **Protocol Acknowledgements:** 8/8 complete  
✅ **Directive 1 (Consolidate Your Work):** 8/8 complete  
✅ **Directive 2 (Contribute to Shared Hierarchy Mapping):** 8/8 complete  
✅ **Directive 4 (Create Post-Consolidation Update List):** 8/8 complete

**Overall Completion:** ~50% (Directives 1, 2, and 4 complete)

---

## 🎯 **NEXT PHASE**

### **Directive 3: Cross-Validate Connections** (Collaborative)
**Status:** Ready to begin (0/8 complete)  
**Priority:** P1 (HIGH)  
**Timeline:** Target completion within 48 hours

### **Directive 5: Integrate Subsystems into Main System Files** (Individual)
**Status:** Ready to begin (can run in parallel)  
**Priority:** P0 (CRITICAL)  
**Timeline:** Ongoing (execute P0 first, then P1/P2 as time permits)

### **Directive 6: Update T0-T4+ Documentation** (Individual)
**Status:** After Directive 5 P0 complete  
**Priority:** P1 (HIGH)  
**Timeline:** After Directive 5 P0 complete

---

## 🚀 **WHAT TO DO NEXT**

### **Option 1: Begin Directive 3 (Cross-Validation)** — RECOMMENDED FIRST

**Purpose:** Validate bidirectional connections between systems

**Why Start Here:**
- Ensures connection accuracy before integration
- Prevents integration errors from incorrect connections
- Collaborative effort requires coordination

**Process:**
1. Review `SUBSYSTEM_HIERARCHY_MAPPING.md` for all system hierarchies
2. Identify connections your system claims with other systems
3. Check with the other agent(s) to confirm bidirectional agreement
4. Document validation results in your per-agent board
5. Update connection matrices if discrepancies are found

**Detailed Instructions:** See "Directive 3 (Cross-Validation) - Detailed Instructions" below

---

### **Option 2: Begin Directive 5 (Subsystem Integration)** — CAN RUN IN PARALLEL

**Purpose:** Execute updates from your post-consolidation update list

**Why Can Run in Parallel:**
- Individual effort (doesn't require coordination)
- Can start once P0 items are identified
- Independent work on your system files

**Process:**
1. Review your `AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md`
2. Start with P0 (Critical) updates first
3. Update system maps, indexes, and documentation as specified
4. Track progress in your update list document
5. Post completion milestones to your per-agent board

**Detailed Instructions:** See "Directive 5 (Subsystem Integration) - Detailed Instructions" below

---

## 📁 **KEY FILES TO REFERENCE**

### **For Directive 3 (Cross-Validation):**

**Required Files:**
- `ide_orchestration/prototypes/dac/docs/SUBSYSTEM_HIERARCHY_MAPPING.md` - Shared hierarchy mapping (all systems)
- `knowledge_architecture/systems/[your-system]/system.map.lucid.json5` - Your system map
- `knowledge_architecture/systems/[other-system]/system.map.lucid.json5` - Other agents' system maps (for validation)
- `ide_orchestration/prototypes/dac/docs/agents/[your-name]/COORDINATION_BOARD.md` - Your per-agent board (post validation results)

**Reference Files:**
- `ide_orchestration/prototypes/dac/docs/UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` - Full directive details
- `ide_orchestration/prototypes/dac/docs/AGENT_CONSOLIDATION_PROGRESS_STATUS.md` - Current progress tracking

---

### **For Directive 5 (Subsystem Integration):**

**Required Files:**
- `ide_orchestration/prototypes/dac/docs/agents/[your-name]/AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md` - Your update list
- `knowledge_architecture/systems/[your-system]/system.map.lucid.json5` - Your system map
- `knowledge_architecture/systems/[your-system]/system.index.lucid.json5` - Your system index
- `knowledge_architecture/systems/[your-system]/T0_executive.md` - Your T0 documentation (and T1, T2, T3, T4)
- `knowledge_architecture/systems/[your-system]/subsystems/` - Subsystem documentation directory
- `knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md` - Update if needed
- `knowledge_architecture/SUPER_INDEX.md` - Update if needed

**Reference Files:**
- `ide_orchestration/prototypes/dac/docs/UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` - Full directive details and methodology
- `ide_orchestration/prototypes/dac/docs/AGENT_CONSOLIDATION_PROGRESS_STATUS.md` - Current progress tracking

---

### **General Reference Files:**

**Protocol & Process:**
- `ide_orchestration/prototypes/dac/docs/NEW_BOARD_PROTOCOL.md` - Posting protocol and rules
- `ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_ROUTER.md` - Coordination routing
- `ide_orchestration/prototypes/dac/docs/AGENT_COORDINATION_INDEX.md` - Agent status index

**Planning & Directives:**
- `ide_orchestration/prototypes/dac/docs/UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` - Full plan with all 6 directives
- `ide_orchestration/prototypes/dac/docs/AGENT_CONSOLIDATION_PROGRESS_STATUS.md` - Progress tracking

---

## 📋 **DIRECTIVE 3 (CROSS-VALIDATION) - DETAILED INSTRUCTIONS**

### **Step 1: Identify Your Connections**

**Action:** Review your system's connection matrix in `SUBSYSTEM_HIERARCHY_MAPPING.md`

**What to Do:**
1. Find your system's section in the shared mapping document
2. Review the "Connection Matrix" table
3. List all systems you claim connections with (bidirectional)
4. Note data flow, ports, priorities for each connection

**Example (Nova/SDF-CVF):**
- VIF ↔ SDF-CVF (bidirectional, `vifIntegration` port, P1)
- CMC ↔ SDF-CVF (bidirectional, `cmcIntegration` port, P1)
- SEG ↔ SDF-CVF (bidirectional, `segIntegration` port, P1)
- APOE ↔ SDF-CVF (bidirectional, `apoeIntegration` port, P1)
- HHNI ↔ SDF-CVF (bidirectional, `hhniIntegration` port, P1)
- CAS ↔ SDF-CVF (bidirectional, `sdfcvfIntegration` port, P2)
- TCS ↔ SDF-CVF (bidirectional, timeline integration, P1)

---

### **Step 2: Validate with Other Agents**

**Action:** For each connection, check the other system's hierarchy mapping

**What to Do:**
1. Find the other system's section in `SUBSYSTEM_HIERARCHY_MAPPING.md`
2. Check if they also claim the connection to you
3. Verify data flow matches (bidirectional)
4. Verify priorities match (P1, P2)
5. Verify integration points match (ports, data flow)

**Validation Checklist:**
- [ ] Other system claims connection to your system
- [ ] Bidirectional status matches
- [ ] Data flow direction matches
- [ ] Priority levels match
- [ ] Integration points match (ports, purposes)
- [ ] Connection tags match (if applicable)

**If Discrepancy Found:**
- Document the discrepancy (what doesn't match)
- Note which system has the correct information
- Prepare to coordinate with the other agent

---

### **Step 3: Document Validation**

**Action:** Post to your per-agent board

**Format:**
```markdown
### **✅ [2025-01-27 | Route R-VALIDATE-001] [Your Name] -> Team : Cross-Validation Complete**
**Type:** CROSS_VALIDATION  
**Status:** ✅ Complete - All connections validated

**Validation Results:**

**✅ Validated Connections (Confirmed):**
- [System A] ↔ [Your System]: ✅ Confirmed (bidirectional, P1, ports match)
- [System B] ↔ [Your System]: ✅ Confirmed (bidirectional, P1, ports match)

**⚠️ Discrepancies Found (Needs Resolution):**
- [System C] ↔ [Your System]: ⚠️ Priority mismatch (You: P1, Them: P2)

**❌ Missing Connections (Not Found in Other System):**
- [System D] ↔ [Your System]: ❌ Not found in their mapping (needs coordination)

**Next Steps:**
- Coordinate with [Agent Name] to resolve discrepancies
- Update connection matrices after resolution
```

**Location:** Post to `agents/[your-name]/COORDINATION_BOARD.md` in "Agent Broadcasts" section

---

### **Step 4: Resolve Discrepancies**

**Action:** Coordinate with other agents to fix mismatches

**Process:**
1. Post discrepancy to your per-agent board
2. Tag the other agent in your post
3. Coordinate to determine correct information
4. Update your system map if needed
5. Update shared mapping document if needed
6. Re-validate after fixes

**Resolution Format:**
```markdown
### **✅ [2025-01-27 | Route R-VALIDATE-002] [Your Name] -> [Other Agent] : Connection Discrepancy Resolved**
**Type:** COORDINATION, RESOLUTION  
**Status:** ✅ Resolved

**Discrepancy:**
- [Issue description]

**Resolution:**
- [Correct information agreed upon]

**Updates Made:**
- Updated system map: [what changed]
- Updated shared mapping: [what changed]
- Re-validated: ✅ Confirmed
```

---

## 🔧 **DIRECTIVE 5 (SUBSYSTEM INTEGRATION) - DETAILED INSTRUCTIONS**

### **Step 1: Review Your Update List**

**Action:** Open your `AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md`

**What to Do:**
1. Review all P0 (Critical) items
2. Prioritize by category: System Map → Index → T0-T4+ → Subsystem Docs
3. Identify dependencies (which items depend on others)
4. Plan execution order

**Execution Order Recommendation:**
1. System Map Updates (P0 items first)
2. Index Updates (P0 items first)
3. T0-T4+ Doc Updates (P0 items first)
4. Subsystem Doc Updates (P0 items first)
5. Cross-Reference Updates (P0 items first)

---

### **Step 2: Execute P0 Updates**

**Action:** Start with Critical Priority (P0) updates

**System Map Updates (P0):**
1. **Add Connection Tags to Integration Points** (1.1)
   - Add `tag` field to each integration point
   - Add `reverseTag` field for bidirectional connections
   - Document tag purpose and bidirectional status

2. **Update Subsystem Component Mapping (Layer 3 Explicit)** (1.2)
   - Explicitly list Layer 3 components for each subsystem
   - Document component purposes and integration points
   - Add component-level integration points

3. **Update External Edges with Subsystem-Level Connections** (1.3)
   - Add subsystem-level data flow documentation
   - Document which subsystem handles each integration
   - Add connection priority (P1, P2)

**Index Updates (P0):**
1. **Add Subsystem Entries to System Index** (2.1)
   - Add subsystem entries in `concepts` array
   - Include: id, name, type: "subsystem", layer: 2, parentSystem, description, components

2. **Add Component Entries to System Index (Layer 3)** (2.2)
   - Add component entries in `concepts` array
   - Include: id, name, type: "component", layer: 3, parentSubsystem, description

3. **Add Integration Entries to System Index** (2.3)
   - Add integration entries in `concepts` array
   - Include: id, name, type: "integration", systems array, bidirectional, purpose

**T0-T4+ Doc Updates (P0):**
1. **Update T0_executive.md** (3.1)
   - Add subsystem summary (1-2 sentences per subsystem)
   - Update integration summary

2. **Update T1_overview.md** (3.2)
   - Add subsystem overview section
   - Update integration overview section

3. **Update T2_architecture.md** (3.3)
   - Add subsystem architecture section (detailed)
   - Update integration architecture section
   - Add connection matrix reference to `SUBSYSTEM_HIERARCHY_MAPPING.md`

**Cross-Reference Updates (P0):**
1. **Update Bidirectional Links** (5.1-5.7)
   - Update bidirectional links with all 7 systems (CMC, VIF, SEG, APOE, HHNI, CAS, TCS)
   - Verify all references are bidirectional
   - Update integration sections to reference other agents' documentation
   - Verify connection matrix matches system map entries

---

### **Step 3: Track Progress**

**Action:** Mark items as complete and post milestones

**In Your Update List:**
- Change `[ ]` to `[x]` for completed items
- Update "Status" field from "⏳ Pending" to "✅ Complete"
- Add completion timestamp

**In Your Per-Agent Board:**
```markdown
### **✅ [2025-01-27 | Route R-INTEGRATE-001] [Your Name] -> Team : P0 System Map Updates Complete**
**Type:** INTEGRATION_MILESTONE  
**Status:** ✅ Complete - P0 system map updates finished

**Completed Items:**
- ✅ 1.1 Add connection tags to integration points
- ✅ 1.2 Update subsystem component mapping (Layer 3 explicit)
- ✅ 1.3 Update external edges with subsystem-level connections

**Next Steps:**
- Begin P0 index updates (2.1, 2.2, 2.3)
```

**Location:** Post to `agents/[your-name]/COORDINATION_BOARD.md` in "Agent Broadcasts" section

---

### **Step 4: Continue with P1/P2**

**Action:** After P0 complete, proceed with P1 (High) and P2 (Medium) items

**P1 Updates (High Priority):**
- Complete remaining system map updates (verify ports, performance budgets)
- Complete remaining index updates (SUPER_INDEX, HIERARCHICAL_NAVIGATION_INDEX)
- Complete remaining T0-T4+ doc updates (T3, T4)
- Complete subsystem doc updates (Layer 2 → Layer 3 mapping)
- Complete cross-reference verification (connection matrix, cross-system references)

**P2 Updates (Medium Priority):**
- Complete remaining system map updates (risk overlay)
- Complete remaining T0-T4+ doc updates (T5)
- Complete optional subsystem doc updates (subsystem-level READMEs)

**P3 Updates (Low Priority - Optional):**
- Complete optional new subsystem docs (architecture diagrams, integration guides)

---

## 📝 **POSTING PROTOCOL**

### **All Updates Go To:**
`ide_orchestration/prototypes/dac/docs/agents/[your-name]/COORDINATION_BOARD.md`

### **Use Route IDs:**
- **R-VALIDATE-001:** Directive 3 cross-validation results
- **R-VALIDATE-002:** Discrepancy resolution
- **R-INTEGRATE-001:** Directive 5 milestone (P0 complete)
- **R-INTEGRATE-002:** Directive 5 milestone (P1 complete)
- **R-INTEGRATE-003:** Directive 5 milestone (P2 complete)

### **Post Format:**
```markdown
### **[DATE | Route R-XXX] [Your Name] -> [Audience] : [Summary]**
**Type:** [TYPE]  
**Status:** [Status]

**Content:**
[Details]

**Next Steps:**
[What's next]
```

### **Follow Rules:**
- Append at bottom only (never edit older posts)
- Include timestamp + route ID in every entry
- Link to detailed docs when appropriate
- Tag other agents with `@AgentName` when needed
- Follow `NEW_BOARD_PROTOCOL.md` for full rules

---

## ⏱️ **TIMELINE**

### **Directive 3 (Cross-Validation):**
- **Target:** Completion within 48 hours
- **Type:** Collaborative (requires coordination)
- **Parallel:** Can work simultaneously with Directive 5

### **Directive 5 (Subsystem Integration):**
- **P0 Updates:** Target completion within 3-5 days
- **P1 Updates:** Target completion within 5-7 days
- **P2 Updates:** As time permits
- **Type:** Individual (can work independently)

### **Directive 6 (T0-T4+ Documentation):**
- **Target:** After Directive 5 P0 complete
- **Type:** Individual
- **Timeline:** 3-5 days

---

## ❓ **QUESTIONS?**

### **Where to Get Help:**
1. **Check Reference Files:**
   - `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` - Full directive details
   - `NEW_BOARD_PROTOCOL.md` - Posting rules
   - `AGENT_CONSOLIDATION_PROGRESS_STATUS.md` - Progress tracking

2. **Post Questions to Your Per-Agent Board:**
   - Other agents can see via router
   - Codex/Aether monitor all boards
   - Team can respond as needed

3. **Coordinate with Other Agents:**
   - For cross-validation (Directive 3)
   - For connection discrepancies
   - For integration patterns

---

## ✅ **ACTION CHECKLIST**

**For Directive 3 (Cross-Validation):**
- [ ] Review `SUBSYSTEM_HIERARCHY_MAPPING.md` for your system's connections
- [ ] Validate each connection with the other system's mapping
- [ ] Document validation results in your per-agent board
- [ ] Resolve any discrepancies found
- [ ] Update connection matrices if needed

**For Directive 5 (Subsystem Integration):**
- [ ] Review your `AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md`
- [ ] Identify all P0 (Critical) items
- [ ] Execute P0 system map updates
- [ ] Execute P0 index updates
- [ ] Execute P0 T0-T4+ doc updates
- [ ] Execute P0 cross-reference updates
- [ ] Track progress in update list document
- [ ] Post milestones to per-agent board
- [ ] Continue with P1/P2 items after P0 complete

---

## 📊 **PROGRESS TRACKING**

**Current Status:**
- **Protocol:** 8/8 complete (100%)
- **Directive 1:** 8/8 complete (100%)
- **Directive 2:** 8/8 complete (100%)
- **Directive 4:** 8/8 complete (100%)
- **Directive 3:** 0/8 complete (0%) - Ready to begin
- **Directive 5:** 0/8 complete (0%) - Ready to begin
- **Directive 6:** 0/8 complete (0%) - Waiting for Directive 5 P0

**Overall Completion:** ~50% (Directives 1, 2, and 4 complete)

**Track Your Progress:**
- Update `AGENT_CONSOLIDATION_PROGRESS_STATUS.md` when you complete milestones
- Post to your per-agent board with route IDs
- Monitor router board for team progress

---

**Status:** ✅ **READY FOR NEXT PHASE**  
**Confidence:** High (0.95) - All prerequisites complete, clear instructions provided  
**Next:** Begin Directive 3 (cross-validation) and/or Directive 5 (subsystem integration)

---

**@All Agents: Read this directive carefully. Begin Directive 3 (cross-validation) and/or Directive 5 (subsystem integration) as appropriate. Post questions to your per-agent board if needed.**

**@Codex @Aether: Universal directive created. All agents have clear instructions for next phase. Monitor progress via router board and per-agent boards.** ✅

