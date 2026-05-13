# Codex Chat/IDE Orchestration Implementation Prompt
**Date:** 2025-01-28  
**Status:** ✅ **IMPLEMENTATION IN PROGRESS** - Codex Acknowledged, Continue Work  
**Priority:** P0 - MVP-Critical

---

## 🎯 **MISSION: IMPLEMENT CHAT/IDE ORCHESTRATION LAYER**

**Codex, you are the Chat/IDE Integration Specialist. You've already acknowledged the implementation plan and begun work. Continue implementing the orchestration layer that connects chat/IDE events to AIM-OS systems.**

**Your Progress:** ✅ **ACKNOWLEDGED** - You've reviewed the implementation plan and are ready to proceed

---

## ✅ **COORDINATION STATUS: ALL AGENTS READY**

**All 4 agents have provided complete coordination details:**

1. ✅ **Atlas (CMC)** - Integration Tagging Guide complete
2. ✅ **Sage (VIF)** - VIF Witness API Details complete
3. ✅ **Chronos (TCS)** - Timeline Logging Details complete
4. ✅ **Meta (CAS)** - CAS Cognitive Context Streaming Details complete

**Reference:** `CHAT_IDE_COORDINATION_STATUS.md` - Complete status summary

---

## 📋 **YOUR IMPLEMENTATION TASKS**

### **PHASE 1: FOUNDATION (Week 1, Days 1-3) - START NOW**

#### **Task 1.1: Review All Agent Guides** ⏳ **IMMEDIATE**

**Read these documents in order:**

1. **Atlas's Integration Tagging Guide:**
   - `agents/atlas/ATLAS_CODEX_INTEGRATION_TAGGING_GUIDE.md`
   - **Key:** Tag format, conversion helper, 5 event examples, tag flow diagram
   - **Action:** Understand how to stamp tags in orchestration layer

2. **Sage's VIF Witness API Details:**
   - `agents/sage/COORDINATION_BOARD.md` (section: Chat/IDE Coordination)
   - **Key:** `create_witness_and_store()` signature, payload format, κ-gate policies
   - **Action:** Understand witness creation API (stub now, wire real API in 1-2 weeks)

3. **Chronos's Timeline Logging Details:**
   - `agents/chronos/CHRONOS_CODEX_TIMELINE_LOGGING_DETAILS.md`
   - **Key:** Timeline hooks, MCP tool usage, κ-gate entries, UI integration
   - **Action:** Understand how to emit timeline entries for all actions

4. **Meta's CAS Cognitive Context Details:**
   - `agents/META/COORDINATION_BOARD.md` (section: Chat/IDE Coordination)
   - **Key:** Cognitive event creation, mood/context badges, VIF enhancement
   - **Action:** Understand how to stream cognitive context to UI

**Deliverable:** Post acknowledgment on your coordination board that you've reviewed all guides

---

#### **Task 1.2: Implement Integration Tagging** ⏳ **IMMEDIATE (Day 1-2)**

**Goal:** Stamp standardized integration tags on all chat/IDE events

**Implementation Steps:**

1. **Create Tag Conversion Helper:**
   - Location: `cursor-addon/src/orchestration/tagHelpers.ts` (or similar)
   - Function: Convert list format to CMC weighted dict format
   - Use Atlas's `create_integration_tags()` pattern as reference

2. **Update MCPService.ts:**
   - Add integration tag attachment to all chat events
   - Tag format: `["system:<name>:<priority>", "integration_type:<type>", "connection:<direction>", "modality:<modality>"]`
   - Apply tags before events reach APOE/CMC

3. **Update APOE Executor Integration:**
   - Stamp tags in APOE DAG nodes
   - Ensure tags flow through: Chat/IDE → MCPService → APOE → CMC → HHNI → SEG

4. **Test Tag Flow:**
   - Verify tags appear in CMC atoms
   - Verify tags work with HHNI indexing
   - Verify tags work with SDF-CVF quartet parity

**Reference:** `agents/atlas/ATLAS_CODEX_INTEGRATION_TAGGING_GUIDE.md`

**Deliverable:** Integration tagging working end-to-end, tags visible in CMC atoms

---

#### **Task 1.3: Hook Timeline Logging** ⏳ **IMMEDIATE (Day 1-2)**

**Goal:** Emit timeline entries for all chat/IDE actions

**Implementation Steps:**

1. **Integrate MCP Tool:**
   - Use `mcp_lucid-mcp_add_timeline_entry()` for all chat/IDE actions
   - Location: `MCPService.ts` or orchestration router
   - Emit entries for: κ-gate transitions, APOE plan milestones, user actions

2. **Create Timeline Entry Helpers:**
   - Helper for κ-gate timeline entries (use Chronos's pattern)
   - Helper for APOE plan milestone entries
   - Helper for general chat/IDE action entries

3. **Integrate with UI:**
   - Ensure dual drawers can render timeline chips referencing `TCS_EVENT_ID`
   - Display timeline entries in chat/IDE UI

4. **Test Timeline Logging:**
   - Verify timeline entries created for all actions
   - Verify entries stored in CMC with `modality="tcs_timeline"`
   - Verify UI displays timeline chips correctly

**Reference:** `agents/chronos/CHRONOS_CODEX_TIMELINE_LOGGING_DETAILS.md`

**Deliverable:** Timeline logging working for all chat/IDE actions, entries visible in UI

---

#### **Task 1.4: Stream CAS Cognitive Context** ⏳ **IMMEDIATE (Day 1-3)**

**Goal:** Display CAS mood/context badges in chat/IDE drawer HUDs

**Implementation Steps:**

1. **Integrate CAS MCP Tools:**
   - Use CAS MCP tools to get cognitive context for decisions
   - Location: `MCPService.ts` or orchestration router
   - Post `cognitive_event` entries for every orchestrated decision

2. **Create Cognitive Context Helpers:**
   - Helper to extract cognitive context from CAS
   - Helper to enhance VIF witnesses with cognitive context (use Meta's pattern)
   - Helper to format cognitive context for UI display

3. **Integrate with UI:**
   - Display CAS mood/context badges in drawer HUDs
   - Tie cognitive context into thinking-mode HUDs
   - Show cognitive context in dual-drawer UI

4. **Test Cognitive Context Streaming:**
   - Verify cognitive events created for all decisions
   - Verify mood/context badges display in UI
   - Verify VIF witnesses enhanced with cognitive context

**Reference:** `agents/META/COORDINATION_BOARD.md` (section: Chat/IDE Coordination)

**Deliverable:** CAS cognitive context streaming working, badges visible in UI

---

### **PHASE 2: VIF WITNESS INTEGRATION (Week 1-2, Days 3-7)**

#### **Task 2.1: Stub VIF Witness API** ⏳ **IMMEDIATE (Day 3-4)**

**Goal:** Create stub for VIF witness creation (wire real API in 1-2 weeks)

**Implementation Steps:**

1. **Create Witness Request Interface:**
   - Location: `cursor-addon/src/orchestration/witnessTypes.ts`
   - Use Sage's `WitnessRequest` payload format
   - Include all required fields: `operation_name`, `prompt`, `output`, `confidence`, `context_snapshot_id`, etc.

2. **Create Stub Witness Creation:**
   - Location: `cursor-addon/src/orchestration/witnessStub.ts`
   - Stub function that accepts `WitnessRequest` and returns `WitnessID`
   - Log witness creation for now (wire real API when Sage ready)

3. **Integrate with Orchestration Layer:**
   - Call stub witness creation before responses reach UI
   - Attach witness ID to chat/IDE events
   - Store witness metadata in CMC (via integration tags)

4. **Prepare for Real API:**
   - Document where to wire real `create_witness_and_store()` call
   - Ensure stub interface matches Sage's API signature
   - Test stub integration with orchestration layer

**Reference:** `agents/sage/COORDINATION_BOARD.md` (section: Chat/IDE Coordination)

**Deliverable:** Stub witness creation working, ready to wire real API in 1-2 weeks

---

#### **Task 2.2: Implement κ-Gate Enforcement** ⏳ **Week 1-2**

**Goal:** Enforce κ-gates for all chat/IDE actions (mandatory witness creation flow)

**Implementation Steps:**

1. **Integrate κ-Gate Policies:**
   - Use Sage's confirmed κ thresholds: ROUTINE=0.70, IMPORTANT=0.85, CRITICAL=0.95
   - Use Sage's retry policies: CRITICAL=0, IMPORTANT=1, ROUTINE=2, LOW_STAKES=3
   - Location: `cursor-addon/src/orchestration/kappaGate.ts`

2. **Enforce κ-Gates in Orchestration:**
   - Check κ-gate before responses reach UI
   - Block actions that fail κ-gate (CRITICAL/IMPORTANT)
   - Retry actions based on retry policy
   - Escalate if retry exhausted

3. **Integrate with Timeline Logging:**
   - Emit κ-gate timeline entries for all decisions (use Chronos's pattern)
   - Display κ-gate status in UI
   - Log κ-gate failures for debugging

4. **Test κ-Gate Enforcement:**
   - Verify κ-gates enforced for all chat/IDE actions
   - Verify retry policies work correctly
   - Verify escalation triggers correctly

**Reference:** `agents/sage/COORDINATION_BOARD.md` (section: Chat/IDE Coordination)

**Deliverable:** κ-Gate enforcement working, all actions gated correctly

---

#### **Task 2.3: Wire Real VIF Witness API** ⏳ **Week 1-2 (When Sage Ready)**

**Goal:** Replace stub with real VIF witness creation API

**Implementation Steps:**

1. **Coordinate with Sage:**
   - Confirm real API is ready (1-2 weeks timeline)
   - Get final API signature and payload format
   - Test API integration

2. **Replace Stub with Real API:**
   - Update witness creation to call real `create_witness_and_store()`
   - Ensure payload format matches Sage's specification
   - Handle API errors gracefully

3. **Test Real API Integration:**
   - Verify witnesses created correctly
   - Verify witnesses stored in CMC
   - Verify witness IDs flow through orchestration

**Reference:** `agents/sage/COORDINATION_BOARD.md` (section: Chat/IDE Coordination)

**Deliverable:** Real VIF witness API wired, witnesses created for all actions

---

### **PHASE 3: END-TO-END INTEGRATION (Week 2-3)**

#### **Task 3.1: Test Complete Orchestration Flow** ⏳ **Week 2-3**

**Goal:** Verify all orchestration flows work end-to-end

**Test Scenarios:**

1. **Chat Message Flow:**
   - User sends message → MCPService → APOE → CMC → VIF witness → Timeline entry → CAS cognitive context → UI response
   - Verify: Tags stamped, witness created, timeline entry logged, cognitive context displayed

2. **Code Generation Flow:**
   - User requests code → MCPService → APOE → CMC → VIF witness → Timeline entry → CAS cognitive context → UI response
   - Verify: Tags stamped, witness created, timeline entry logged, cognitive context displayed

3. **Plan Execution Flow:**
   - User requests plan → MCPService → APOE → CMC → VIF witness → Timeline entry → CAS cognitive context → UI response
   - Verify: Tags stamped, witness created, timeline entry logged, cognitive context displayed

4. **κ-Gate Enforcement Flow:**
   - Low confidence action → κ-gate check → Block/Retry/Escalate → Timeline entry → UI notification
   - Verify: κ-gate enforced, retry policies work, escalation triggers correctly

**Deliverable:** All orchestration flows tested and working

---

#### **Task 3.2: Validate Integration Points** ⏳ **Week 2-3**

**Goal:** Verify all integration points work correctly

**Validation Checklist:**

- [ ] Integration tags flow through all systems (CMC, HHNI, SEG)
- [ ] Timeline entries created for all actions
- [ ] CAS cognitive context displayed in UI
- [ ] VIF witnesses created for all actions (stub or real API)
- [ ] κ-Gates enforced for all actions
- [ ] Retry policies work correctly
- [ ] Escalation triggers correctly
- [ ] UI displays all orchestration data correctly

**Deliverable:** All integration points validated

---

## 📚 **KEY DOCUMENTS TO REFERENCE**

**Your Orchestration Design:**
- `CODEX_CHAT_IDE_COORDINATION_PROMPT.md` - Your complete orchestration design

**Agent Coordination Guides:**
- `CHAT_IDE_COORDINATION_STATUS.md` - Complete status summary
- `agents/atlas/ATLAS_CODEX_INTEGRATION_TAGGING_GUIDE.md` - Integration tagging
- `agents/sage/COORDINATION_BOARD.md` - VIF witness API (Chat/IDE Coordination section)
- `agents/chronos/CHRONOS_CODEX_TIMELINE_LOGGING_DETAILS.md` - Timeline logging
- `agents/META/COORDINATION_BOARD.md` - CAS cognitive context (Chat/IDE Coordination section)

**Synthesis Outcomes:**
- `SYNTHESIS_SESSION_FINAL_OUTCOMES.md` - All synthesis decisions
- `SYNTHESIS_SESSION_PART4_STATUS.md` - Orchestration integration planning

**Your Deep Brief:**
- `agents/codex/CODEX_CHAT_IDE_DEEP_BRIEF.md` - Complete chat/IDE vision

---

## 🎯 **SUCCESS CRITERIA**

**Phase 1 Complete When:**
- ✅ Integration tagging working end-to-end
- ✅ Timeline logging working for all actions
- ✅ CAS cognitive context streaming working
- ✅ Stub VIF witness API integrated

**Phase 2 Complete When:**
- ✅ κ-Gate enforcement working
- ✅ Real VIF witness API wired (when Sage ready)
- ✅ All orchestration flows tested

**Phase 3 Complete When:**
- ✅ All integration points validated
- ✅ End-to-end orchestration working
- ✅ UI displays all orchestration data correctly

---

## 📊 **PROGRESS TRACKING**

**Post Updates on Your Coordination Board:**

**Format:** `[2025-01-28 | Chat/IDE Implementation] Codex -> Team : [Task Name] Status`

**Update Frequency:**
- Daily updates during active implementation
- Milestone updates when phases complete
- Blocker updates if issues arise

**Coordination Needed:**
- Post coordination requests if you need clarification from agents
- Post blockers if implementation is blocked
- Post questions if you need help

---

## 🚀 **CONTINUE IMPLEMENTATION**

**You've already acknowledged the plan. Your immediate next steps:**

1. ✅ **Read all agent coordination guides** (Task 1.1) - **COMPLETE**
2. ✅ **Post acknowledgment** on your coordination board - **COMPLETE**
3. ⏳ **Begin Phase 1 implementation** (Tasks 1.2, 1.3, 1.4) - **IN PROGRESS**
4. ⏳ **Post daily progress updates** on your coordination board - **ONGOING**

**Current Focus:**
- **Task 1.2:** Implement Integration Tagging (Day 1-2)
- **Task 1.3:** Hook Timeline Logging (Day 1-2)
- **Task 1.4:** Stream CAS Cognitive Context (Day 1-3)

**Timeline:**
- **Week 1:** Phase 1 (Foundation) - Integration tagging, timeline logging, CAS cognitive context, stub VIF API
- **Week 1-2:** Phase 2 (VIF Integration) - κ-Gate enforcement, real VIF API wiring
- **Week 2-3:** Phase 3 (End-to-End) - Testing, validation, UI integration

**All agents are ready. All coordination details are complete. Continue implementation!** 🚀

---

## 📝 **IMPLEMENTATION NOTES**

**As you work, keep these in mind:**

1. **Start with Integration Tagging (Task 1.2):**
   - This is the foundation for all other integrations
   - Once tags are flowing, other systems can discover and link events
   - Atlas's guide has complete examples - use them as reference

2. **Timeline Logging (Task 1.3) can run in parallel:**
   - Uses MCP tools that are already ready
   - Can be implemented alongside integration tagging
   - Chronos's guide has all the hooks documented

3. **CAS Cognitive Context (Task 1.4) enhances the experience:**
   - Makes the UI more informative
   - Can be added incrementally
   - Meta's guide has complete patterns

4. **VIF Witness API (Task 2.1) can be stubbed initially:**
   - Don't wait for Sage's real API (1-2 weeks)
   - Create stub that matches Sage's interface
   - Wire real API when Sage is ready

5. **Post Progress Regularly:**
   - Daily updates help track progress
   - Share blockers immediately
   - Celebrate milestones!

**You've got this! All the pieces are in place. Build the orchestration layer that makes AIM-OS come alive in the chat/IDE!** 💙

---

**Status:** ✅ **READY TO IMPLEMENT**  
**Confidence:** Very High (0.95) - All coordination details received, implementation plan clear  
**Next:** Read agent guides, begin Phase 1 implementation

