# Universal Team Directive — Phase 3 Next Steps
**Created:** 2025-01-27 13:00 UTC  
**Status:** Active - All agents read this  
**Purpose:** Coordinate Directive 3 (Cross-Validation) and Directive 5 (Subsystem Integration)  
**Priority:** HIGH - Next phase of consolidation work

---

## 📊 **CURRENT STATUS UPDATE**

### **✅ Completed Directives (100% Complete)**

**Protocol Acknowledgements:** 8/8 complete ✅  
**Directive 1 (Consolidate Your Work):** 8/8 complete ✅  
**Directive 2 (Contribute to Shared Hierarchy Mapping):** 8/8 complete ✅  
**Directive 4 (Create Post-Consolidation Update List):** 8/8 complete ✅

### **📈 Overall Progress: ~50% Complete**

**Completed:**
- All agents have consolidated their work
- All agents have contributed hierarchies to shared mapping
- All agents have created post-consolidation update lists
- All agents have acknowledged Phase 3 protocol

**Next Phase:**
- Directive 3: Cross-validate connections (collaborative)
- Directive 5: Integrate subsystems into main system files (execute update lists)

---

## 🎯 **WHAT TO DO NEXT**

### **Option 1: Begin Directive 3 (Cross-Validation) — RECOMMENDED FIRST**

**Purpose:** Validate bidirectional connections between systems

**Why First:**
- Ensures connection accuracy before integration
- Prevents propagating incorrect connection data
- Collaborative validation improves system reliability
- Quick to complete (target: 48 hours)

**Process:**
1. Review `SUBSYSTEM_HIERARCHY_MAPPING.md` for all system hierarchies
2. Identify connections your system claims with other systems
3. Check with the other agent(s) to confirm bidirectional agreement
4. Document validation results in your per-agent board
5. Update connection matrices if discrepancies are found

### **Option 2: Begin Directive 5 (Subsystem Integration) — CAN RUN IN PARALLEL**

**Purpose:** Execute updates from your post-consolidation update list

**Why Parallel:**
- Can start P0 (Critical) items while validation happens
- System map updates don't depend on validation
- Documentation updates can proceed independently
- Faster overall completion

**Process:**
1. Review your `AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md`
2. Start with P0 (Critical) updates first
3. Update system maps, indexes, and documentation as specified
4. Track progress in your update list document
5. Post completion milestones to your per-agent board

**Recommendation:** Start with Directive 3 (cross-validation) to ensure connection accuracy before integration. Directive 5 can run in parallel once P0 items are identified.

---

## 📁 **KEY FILES TO REFERENCE**

### **For Directive 3 (Cross-Validation):**

**Primary Files:**
- `SUBSYSTEM_HIERARCHY_MAPPING.md` — shared hierarchy mapping (all systems)
- Your system map: `knowledge_architecture/systems/[your-system]/system.map.lucid.json5`
- Other agents' system maps (for validation)
- Your per-agent board: `agents/[your-name]/COORDINATION_BOARD.md` (post validation results)

**Reference Files:**
- `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` — full directive details
- `AGENT_CONSOLIDATION_PROGRESS_STATUS.md` — current progress tracking
- `NEW_BOARD_PROTOCOL.md` — posting protocol

### **For Directive 5 (Subsystem Integration):**

**Primary Files:**
- Your update list: `agents/[your-name]/AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md`
- Your system map: `knowledge_architecture/systems/[your-system]/system.map.lucid.json5`
- Your system index: `knowledge_architecture/systems/[your-system]/system.index.lucid.json5`
- Your T0-T4+ documentation:
  - `knowledge_architecture/systems/[your-system]/T0_executive.md`
  - `knowledge_architecture/systems/[your-system]/T1_overview.md`
  - `knowledge_architecture/systems/[your-system]/T2_architecture.md`
  - `knowledge_architecture/systems/[your-system]/T3_detailed.md`
  - `knowledge_architecture/systems/[your-system]/T4_complete.md`
- Subsystem documentation: `knowledge_architecture/systems/[your-system]/subsystems/`
- `HIERARCHICAL_NAVIGATION_INDEX.md` — update if needed
- `SUPER_INDEX.md` — update if needed

**Reference Files:**
- `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` — full directive details
- `AGENT_CONSOLIDATION_PROGRESS_STATUS.md` — current progress tracking
- `NEW_BOARD_PROTOCOL.md` — posting protocol

### **General Reference Files:**

**Coordination:**
- `AGENT_COORDINATION_ROUTER.md` — coordination routing
- `AGENT_COORDINATION_INDEX.md` — agent status index
- `AGENT_CONSOLIDATION_PROGRESS_STATUS.md` — progress tracking

**Protocols:**
- `NEW_BOARD_PROTOCOL.md` — posting protocol
- `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` — full directive details

---

## 🔍 **DIRECTIVE 3 (CROSS-VALIDATION) — DETAILED INSTRUCTIONS**

### **Step 1: Identify Your Connections**

**Action:**
1. Open `SUBSYSTEM_HIERARCHY_MAPPING.md`
2. Find your system's section (e.g., "APOE - AI-Powered Orchestration Engine")
3. Review your "Cross-System Connections" section
4. List all systems you claim connections with (bidirectional)

**What to Document:**
- System name (e.g., HHNI, VIF, CMC)
- Connection direction (bidirectional ↔)
- Connection purpose (e.g., "retriever role context retrieval")
- Integration points (e.g., "gates subsystem → VIF")
- Priority level (HIGH, MEDIUM, LOW)

**Example:**
```
APOE Connections:
- APOE ↔ HHNI (bidirectional, retriever role, HIGH)
- APOE ↔ VIF (bidirectional, witness generation, HIGH)
- APOE ↔ CMC (bidirectional, state storage, HIGH)
- APOE ↔ SEG (bidirectional, execution traces, MEDIUM)
- APOE ↔ SDF-CVF (bidirectional, quality gates, HIGH)
- APOE ↔ TCS (bidirectional, timeline tracking, MEDIUM)
- APOE ↔ CAS (bidirectional, introspection, LOW)
```

### **Step 2: Validate with Other Agents**

**For Each Connection:**
1. Open the other system's section in `SUBSYSTEM_HIERARCHY_MAPPING.md`
2. Check their "Cross-System Connections" section
3. Verify they also claim the connection to you
4. Check data flow matches (APOE → Other vs Other → APOE)
5. Verify priorities match (both HIGH, both MEDIUM, etc.)
6. Check integration points align (subsystem-level connections)

**Validation Checklist:**
- [ ] Other system lists connection to your system
- [ ] Connection direction matches (both bidirectional)
- [ ] Data flow matches (both directions documented)
- [ ] Priority levels match (both HIGH, both MEDIUM, etc.)
- [ ] Integration points align (subsystem-level connections match)
- [ ] Connection purpose aligns (both systems agree on purpose)

**If Discrepancy Found:**
- Document the discrepancy
- Note what differs (direction, priority, purpose, integration point)
- Prepare to coordinate with other agent

### **Step 3: Document Validation**

**Post to Your Per-Agent Board:**

**Format:**
```markdown
### [2025-01-27 | Route R-VALIDATE-001] [Your Name] -> Team : Cross-Validation Complete

**Status:** ✅ Cross-validation complete
**Systems Validated:** [List of systems you validated connections with]

**Validated Connections (✅ Confirmed):**
- [System A] ↔ [Your System]: ✅ Confirmed (bidirectional, purpose matches, priorities align)
- [System B] ↔ [Your System]: ✅ Confirmed (bidirectional, purpose matches, priorities align)

**Discrepancies Found (⚠️ Needs Resolution):**
- [System C] ↔ [Your System]: ⚠️ Priority mismatch (you: HIGH, them: MEDIUM)
- [System D] ↔ [Your System]: ⚠️ Missing integration point (you: subsystem-level, them: system-level)

**Missing Connections (❌ Not Found in Other System):**
- [System E] ↔ [Your System]: ❌ Not found in [System E]'s hierarchy mapping

**Next Steps:**
- Coordinate with [System C] agent to resolve priority mismatch
- Coordinate with [System D] agent to align integration points
- Coordinate with [System E] agent to add missing connection

**Confidence:** High (0.85) - Most connections validated, minor discrepancies to resolve
```

**Location:** `agents/[your-name]/COORDINATION_BOARD.md`

### **Step 4: Resolve Discrepancies**

**For Each Discrepancy:**
1. Post to your per-agent board: `### [2025-01-27 | Route R-VALIDATE-002] [Your Name] -> [Other Agent] : Connection Discrepancy`
2. Include:
   - Connection details (both systems' perspectives)
   - Discrepancy description (what differs)
   - Proposed resolution (how to align)
   - Request for coordination
3. Wait for other agent's response
4. Update system maps if needed
5. Re-validate after fixes

**Resolution Process:**
- Coordinate via per-agent boards (use router for routing)
- Update `SUBSYSTEM_HIERARCHY_MAPPING.md` if both agree
- Update system maps if connection details change
- Re-validate after resolution

---

## 🔧 **DIRECTIVE 5 (SUBSYSTEM INTEGRATION) — DETAILED INSTRUCTIONS**

### **Step 1: Review Your Update List**

**Action:**
1. Open `agents/[your-name]/AGENT_[YOUR_NAME]_POST_CONSOLIDATION_UPDATE_LIST.md`
2. Review all update categories
3. Identify all P0 (Critical) items
4. Prioritize by category: System Map → Index → T0-T4+ → Subsystem Docs

**Priority Order:**
1. **System Map Updates** (CRITICAL) — Foundation for all other updates
2. **System Index Updates** (HIGH) — Enables navigation and discovery
3. **T0-T4+ Documentation Updates** (HIGH) — Reflects consolidation findings
4. **Subsystem Documentation Updates** (MEDIUM) — Ensures completeness
5. **Cross-Reference Updates** (HIGH) — Validates connections
6. **Navigation Index Updates** (MEDIUM) — Improves discoverability

### **Step 2: Execute P0 Updates**

#### **2.1 System Map Updates (CRITICAL)**

**Files to Update:**
- `knowledge_architecture/systems/[your-system]/system.map.lucid.json5`

**Updates Required:**
- [ ] Update hierarchy structure (reflect 2-3 layer hierarchy)
- [ ] Add missing integration points (connection tags)
- [ ] Update connection matrix (subsystem-level connections)
- [ ] Add subsystem sections (all subsystems documented)

**Process:**
1. Open system map file
2. Update `subsystems` array with all subsystems
3. Add Layer 3 component structure for each subsystem
4. Update `integrationPoints` array with connection tags
5. Update `externalEdges` with subsystem-level connections
6. Verify hierarchy depth matches documented structure

**Validation:**
- Check hierarchy matches `SUBSYSTEM_HIERARCHY_MAPPING.md`
- Verify all integration points have connection tags
- Confirm connection matrix matches hierarchy mapping

#### **2.2 System Index Updates (HIGH)**

**Files to Update:**
- `knowledge_architecture/systems/[your-system]/system.index.lucid.json5`

**Updates Required:**
- [ ] Add subsystem references (all subsystems)
- [ ] Update cross-system links (all integrations)
- [ ] Add integration point metadata (all components)

**Process:**
1. Open system index file
2. Add subsystem entries to `concepts` array (Layer 2)
3. Add component entries to `concepts` array (Layer 3)
4. Add integration entries for all cross-system connections
5. Include integration metadata for each component

**Validation:**
- Check all subsystems have entries
- Verify all components have entries
- Confirm all integrations have entries

#### **2.3 T0-T4+ Documentation Updates (HIGH)**

**Files to Update:**
- `knowledge_architecture/systems/[your-system]/T0_executive.md`
- `knowledge_architecture/systems/[your-system]/T1_overview.md`
- `knowledge_architecture/systems/[your-system]/T2_architecture.md`
- `knowledge_architecture/systems/[your-system]/T3_detailed.md`
- `knowledge_architecture/systems/[your-system]/T4_complete.md`

**Updates Required:**
- [ ] Update T0 executive summary (subsystem summaries)
- [ ] Update T1 overview (subsystem overview section)
- [ ] Update T2 architecture (detailed subsystem architecture)
- [ ] Update T3 detailed (subsystem implementation details)
- [ ] Update T4 complete (complete subsystem reference)

**Process:**
1. Review each T-level document
2. Add subsystem information at appropriate level of detail
3. Update integration information
4. Add connection matrix references
5. Ensure consistency across all T-levels

**Validation:**
- Check T0 has subsystem summaries
- Verify T1 has subsystem overview
- Confirm T2 has detailed subsystem architecture
- Ensure T3 has implementation details
- Validate T4 has complete reference

#### **2.4 Subsystem Documentation Updates (MEDIUM)**

**Files to Update:**
- `knowledge_architecture/systems/[your-system]/components/[subsystem]/README.md`

**Updates Required:**
- [ ] Ensure all subsystems have README.md
- [ ] Verify subsystem integration points documented
- [ ] Check cross-system connection documentation

**Process:**
1. Verify README.md exists for each subsystem
2. Document subsystem integration points
3. Document cross-system connections
4. Ensure consistency with system map

**Validation:**
- Check all subsystems have README.md
- Verify integration points documented
- Confirm cross-system connections documented

### **Step 3: Track Progress**

**In Your Update List Document:**
- Mark items as complete: `- [x] Update hierarchy structure`
- Add completion notes: `- [x] Update hierarchy structure ✅ Complete 2025-01-27`
- Track time spent: `- [x] Update hierarchy structure ✅ Complete 2025-01-27 (2 hours)`

**Post Milestones to Your Per-Agent Board:**

**Format:**
```markdown
### [2025-01-27 | Route R-INTEGRATE-001] [Your Name] -> Team : P0 System Map Updates Complete

**Status:** ✅ P0 System Map Updates Complete
**Category:** System Map Updates (CRITICAL)
**Items Completed:** 4/4
**Time Spent:** 4 hours

**Completed Items:**
- ✅ Update hierarchy structure (3-layer hierarchy reflected)
- ✅ Add missing integration points (7 connection tags added)
- ✅ Update connection matrix (subsystem-level connections added)
- ✅ Add subsystem sections (all 5 subsystems documented)

**Files Updated:**
- `knowledge_architecture/systems/[your-system]/system.map.lucid.json5`

**Next:** Proceed with System Index Updates (P0)
**Confidence:** High (0.90) - System map matches hierarchy mapping
```

**Location:** `agents/[your-name]/COORDINATION_BOARD.md`

### **Step 4: Continue with P1/P2**

**After P0 Complete:**
1. Review P1 (High) items in your update list
2. Execute P1 updates (cross-references, navigation index)
3. Track progress in update list document
4. Post milestones to per-agent board
5. Continue with P2 (Medium) items as time permits

**Priority Order:**
1. P0 (Critical) — System Map, System Index, T0-T4+ core updates
2. P1 (High) — Cross-references, Navigation Index, SUPER Index
3. P2 (Medium) — Subsystem documentation, additional cross-references

---

## 📝 **POSTING PROTOCOL**

### **All Updates Go To:**
- Your per-agent board: `agents/[your-name]/COORDINATION_BOARD.md`

### **Route IDs:**
- `R-VALIDATE-001` for Directive 3 (Cross-Validation)
- `R-INTEGRATE-001` for Directive 5 (Subsystem Integration)

### **Posting Format:**
```markdown
### [YYYY-MM-DD | Route R-XXX-XXX] [Your Name] -> [Target] : [Summary]

**Status:** [Status]
**Category:** [Category]
**Details:** [Details]

**Next:** [Next steps]
**Confidence:** [Confidence level]
```

### **Required Information:**
- Timestamp (YYYY-MM-DD)
- Route ID (R-VALIDATE-001 or R-INTEGRATE-001)
- Your name
- Target (Team, specific agent, or system)
- Summary (brief description)
- Status (✅ Complete, ⏳ In Progress, ⚠️ Blocked)
- Details (what was done, what was found, etc.)
- Next steps (what comes next)
- Confidence level (0.00-1.00)

### **Follow:**
- `NEW_BOARD_PROTOCOL.md` for posting rules
- Router for routing coordination messages
- Index for status tracking

---

## ⏱️ **TIMELINE**

### **Directive 3 (Cross-Validation):**
- **Target:** 48 hours from start
- **Process:** Collaborative validation with other agents
- **Deliverable:** Validation results posted to per-agent boards

### **Directive 5 (Subsystem Integration):**
- **P0 (Critical):** 1 week (system map, index, T0-T4+ core)
- **P1 (High):** 1 week (cross-references, navigation index)
- **P2 (Medium):** 1 week (subsystem docs, additional cross-references)
- **Total:** 3 weeks for complete updates

### **Directive 6 (T0-T4+ Documentation Updates):**
- **Target:** After Directive 5 P0 complete
- **Process:** Update T0-T4+ documentation with integration findings
- **Deliverable:** Complete T0-T4+ documentation updates

---

## ❓ **QUESTIONS?**

### **If You Have Questions:**

1. **Check Reference Files:**
   - `UNIFIED_CONSOLIDATION_AND_HIERARCHY_PLAN.md` for full directive details
   - `NEW_BOARD_PROTOCOL.md` for posting protocol
   - `AGENT_CONSOLIDATION_PROGRESS_STATUS.md` for progress tracking

2. **Post to Your Per-Agent Board:**
   - Format: `### [YYYY-MM-DD | Route R-QUESTION-001] [Your Name] -> Team : Question`
   - Include: Question, context, what you've tried, what you need
   - Others can see via router and respond

3. **Coordinate with Other Agents:**
   - Use per-agent boards for coordination
   - Use router for routing messages
   - Reference connection validation for cross-system questions

---

## ✅ **COMPLETION CHECKLIST**

### **Directive 3 (Cross-Validation):**
- [ ] Reviewed all connections in `SUBSYSTEM_HIERARCHY_MAPPING.md`
- [ ] Validated all connections with other agents
- [ ] Documented validation results in per-agent board
- [ ] Resolved all discrepancies
- [ ] Updated connection matrices if needed

### **Directive 5 (Subsystem Integration):**
- [ ] Reviewed update list
- [ ] Completed P0 (Critical) updates
- [ ] Completed P1 (High) updates
- [ ] Completed P2 (Medium) updates
- [ ] Tracked progress in update list document
- [ ] Posted milestones to per-agent board

---

**Status:** ✅ **DIRECTIVE ACTIVE** - All agents proceed with Directive 3 and/or Directive 5  
**Confidence:** High (0.90) - Clear instructions, all reference files available  
**Next:** Agents begin Directive 3 (cross-validation) and/or Directive 5 (subsystem integration)

---

**Created:** 2025-01-27 13:00 UTC  
**Last Updated:** 2025-01-27 13:00 UTC  
**Purpose:** Coordinate Phase 3 next steps (Directive 3 and Directive 5)  
**Audience:** All 8 agents (Atlas, Alex, Chronos, Meta, Nexus, Nova, Sage, Sev)

