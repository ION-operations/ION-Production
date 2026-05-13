# Chat/IDE Integration Coordination Prompts
**Date:** 2025-01-28  
**Status:** ✅ **CODEX ORCHESTRATION DESIGN READY** - Coordination Needed

---

## 🎯 **COORDINATION CONTEXT**

**Codex has completed the chat/IDE orchestration layer design and needs coordination with:**
- **Sage (VIF):** Witness creation API alignment
- **Atlas (CMC):** Integration tagging standardization
- **Chronos (TCS):** Timeline logging hooks
- **Meta (CAS):** Cognitive context streaming

**Codex's Design:** See `CODEX_CHAT_IDE_COORDINATION_PROMPT.md` (section: CHAT/IDE ORCHESTRATION DESIGN)

**Codex's Coordination Board:** `agents/codex/COORDINATION_BOARD.md` (Post-Synthesis section)

---

## 📋 **SAGE (VIF) - COORDINATION PROMPT**

```
Sage:

🎯 CHAT/IDE INTEGRATION COORDINATION - VIF Witness API Alignment

Codex has completed the chat/IDE orchestration layer design and needs to coordinate with you on VIF witness creation for chat/IDE actions.

COORDINATION NEEDS:

1. VIF Witness Creation API Alignment:
   - Codex needs: `create_witness_and_store()` API signature and payload format
   - Codex needs: How to attach `witness_request` payload in `MCPService.ts`
   - Codex needs: How backend invokes witness creation before responses reach UI
   - Timeline: 1-2 weeks (Codex can stub API now, wire real API when ready)

2. κ-Gate Policy Alignment:
   - Codex needs: Confirm κ thresholds (ROUTINE=0.70, IMPORTANT=0.85, CRITICAL=0.95)
   - Codex needs: Confirm retry policy (CRITICAL=0, IMPORTANT=1, ROUTINE=2, LOW_STAKES=3)
   - Codex needs: How to enforce κ-gates in chat/IDE orchestration layer
   - Timeline: 1-2 weeks (align with witness API)

3. Chat/IDE Orchestrated Actions (7th P0 Mandatory Flow):
   - Codex needs: Confirm chat/IDE user actions are mandatory witness creation flow
   - Codex needs: How to create witnesses for all user-facing actions
   - Codex needs: Integration with chat/IDE orchestration layer
   - Timeline: 1-2 weeks (with witness API)

YOUR TASKS:

1. Review Codex's Orchestration Design:
   - Read: `CODEX_CHAT_IDE_COORDINATION_PROMPT.md` (section: CHAT/IDE ORCHESTRATION DESIGN)
   - Review: VIF witness + κ-gate flow section
   - Understand: Codex's implementation approach

2. Provide VIF Witness API Details:
   - Document: `create_witness_and_store()` API signature
   - Document: Payload format for witness creation
   - Document: How to integrate with `MCPService.ts`
   - Document: Error handling and retry policies

3. Confirm κ-Gate Policies:
   - Confirm: κ thresholds match synthesis decisions
   - Confirm: Retry policies match synthesis decisions
   - Document: How to enforce in orchestration layer

4. Coordinate Implementation:
   - Work with Codex on witness API implementation timeline
   - Support Codex's orchestration router implementation
   - Test witness creation flow with chat/IDE actions

POST UPDATES:
- Post VIF witness API details on your coordination board
- Use format: [2025-01-28 | Chat/IDE Coordination] Sage -> Codex : VIF Witness API Details
- Coordinate with Codex on implementation timeline

START NOW - Help Codex integrate VIF witness creation into chat/IDE orchestration! 🚀
```

---

## 📋 **ATLAS (CMC) - COORDINATION PROMPT**

```
Atlas:

🎯 CHAT/IDE INTEGRATION COORDINATION - Integration Tagging Standardization

Codex has completed the chat/IDE orchestration layer design and needs to coordinate with you on integration tagging standardization for chat/IDE events.

COORDINATION NEEDS:

1. Integration Tagging Standardization:
   - Codex needs: Apply standardized format to all chat/IDE events
   - Codex needs: Format: ["system:<name>:<priority>", "integration_type:<type>", "connection:<direction>", "modality:<modality>"]
   - Codex needs: How to stamp tags in APOE DAG nodes
   - Timeline: Can start immediately (Codex ready now)

2. CMC Atom Creation with Tags:
   - Codex needs: How to create CMC atoms with standardized tags
   - Codex needs: How tags flow through orchestration layer
   - Codex needs: Tag format for chat/IDE events
   - Timeline: Can start immediately

3. Witness Storage Integration:
   - Codex needs: How CMC stores VIF witnesses (already documented, verify)
   - Codex needs: How witness + tags work together
   - Codex needs: Integration with chat/IDE orchestration
   - Timeline: Ready now (verify functionality)

YOUR TASKS:

1. Review Codex's Orchestration Design:
   - Read: `CODEX_CHAT_IDE_COORDINATION_PROMPT.md` (section: CHAT/IDE ORCHESTRATION DESIGN)
   - Review: Unified orchestration layer section
   - Understand: Codex's tagging approach

2. Provide Integration Tagging Details:
   - Document: Standardized tag format for chat/IDE events
   - Document: Example tags for chat/IDE actions
   - Document: How tags flow through CMC atom creation
   - Document: Tag format for witness storage

3. Support Codex Implementation:
   - Help Codex apply tags to chat/IDE events
   - Verify tag format matches CMC requirements
   - Test tag flow through orchestration layer

4. Coordinate with Other Agents:
   - Ensure tag format works with HHNI indexing
   - Ensure tag format works with SDF-CVF quartet parity
   - Ensure tag format works with all integrations

POST UPDATES:
- Post integration tagging details on your coordination board
- Use format: [2025-01-28 | Chat/IDE Coordination] Atlas -> Codex : Integration Tagging Details
- Provide example tags for chat/IDE events

START NOW - Help Codex standardize integration tags for chat/IDE! 🚀
```

---

## 📋 **CHRONOS (TCS) - COORDINATION PROMPT**

```
Chronos:

🎯 CHAT/IDE INTEGRATION COORDINATION - Timeline Logging Hooks

Codex has completed the chat/IDE orchestration layer design and needs to coordinate with you on timeline logging for chat/IDE actions.

COORDINATION NEEDS:

1. Timeline Logging Hooks:
   - Codex needs: How to hook timeline logging for all chat/IDE actions
   - Codex needs: How to emit `timeline_event` records for κ-gate transitions
   - Codex needs: How to emit `timeline_event` records for APOE plan milestones
   - Timeline: Ready now (TCS ready, Codex can implement immediately)

2. TCS Timeline Integration:
   - Codex needs: How dual drawers render timeline chips referencing `TCS_EVENT_ID`
   - Codex needs: How timeline events flow through orchestration layer
   - Codex needs: Integration with chat/IDE UI
   - Timeline: Ready now

3. κ-Gate Timeline Entries:
   - Codex needs: How to create κ-gate timeline entries for all chat/IDE decisions
   - Codex needs: How `create_kappa_gate_timeline_entry()` works
   - Codex needs: Integration with VIF κ-gate enforcement
   - Timeline: Ready now

YOUR TASKS:

1. Review Codex's Orchestration Design:
   - Read: `CODEX_CHAT_IDE_COORDINATION_PROMPT.md` (section: CHAT/IDE ORCHESTRATION DESIGN)
   - Review: CAS + TCS integration section
   - Understand: Codex's timeline logging approach

2. Provide Timeline Logging Details:
   - Document: How to create timeline entries for chat/IDE actions
   - Document: How to create κ-gate timeline entries
   - Document: How to create APOE plan milestone entries
   - Document: MCP tool `add_timeline_entry` usage

3. Support Codex Implementation:
   - Help Codex hook timeline logging in orchestration layer
   - Verify timeline entry creation works with chat/IDE events
   - Test timeline chip rendering in dual drawers

4. Coordinate with Other Agents:
   - Ensure timeline logging works with VIF κ-gate enforcement
   - Ensure timeline logging works with APOE plan execution
   - Ensure timeline logging works with CAS cognitive events

POST UPDATES:
- Post timeline logging details on your coordination board
- Use format: [2025-01-28 | Chat/IDE Coordination] Chronos -> Codex : Timeline Logging Details
- Provide example timeline entries for chat/IDE events

START NOW - Help Codex integrate timeline logging into chat/IDE orchestration! 🚀
```

---

## 📋 **META (CAS) - COORDINATION PROMPT**

```
Meta:

🎯 CHAT/IDE INTEGRATION COORDINATION - CAS Cognitive Context Streaming

Codex has completed the chat/IDE orchestration layer design and needs to coordinate with you on CAS cognitive context streaming for chat/IDE drawer HUDs.

COORDINATION NEEDS:

1. CAS Cognitive Event Streaming:
   - Codex needs: How to post `cognitive_event` entries for every orchestrated decision
   - Codex needs: How CAS API works for cognitive event creation
   - Codex needs: Integration with chat/IDE orchestration layer
   - Timeline: Ready now (CAS ready, Codex can implement immediately)

2. CAS Mood/Context Badges:
   - Codex needs: How to display CAS mood/context badges in chat/IDE UI
   - Codex needs: How CAS mood/context ties into thinking-mode HUDs
   - Codex needs: Integration with dual-drawer UI
   - Timeline: Ready now

3. CAS Cognitive Context Enhancement:
   - Codex needs: How CAS enhances VIF witnesses with cognitive context
   - Codex needs: How `create_witness_with_cognitive_context()` works
   - Codex needs: Integration with chat/IDE witness creation
   - Timeline: Ready now

YOUR TASKS:

1. Review Codex's Orchestration Design:
   - Read: `CODEX_CHAT_IDE_COORDINATION_PROMPT.md` (section: CHAT/IDE ORCHESTRATION DESIGN)
   - Review: CAS + TCS integration section
   - Understand: Codex's cognitive context approach

2. Provide CAS Integration Details:
   - Document: How to create cognitive_event entries for chat/IDE actions
   - Document: How to stream CAS mood/context to UI
   - Document: How to enhance VIF witnesses with cognitive context
   - Document: MCP tool usage for CAS operations

3. Support Codex Implementation:
   - Help Codex integrate CAS cognitive events in orchestration layer
   - Help Codex display CAS mood/context badges in drawer HUDs
   - Test cognitive context enhancement with VIF witnesses

4. Coordinate with Other Agents:
   - Ensure CAS cognitive events work with VIF witness creation
   - Ensure CAS mood/context works with TCS timeline logging
   - Ensure CAS integration works with chat/IDE orchestration

POST UPDATES:
- Post CAS integration details on your coordination board
- Use format: [2025-01-28 | Chat/IDE Coordination] Meta -> Codex : CAS Cognitive Context Details
- Provide example cognitive events for chat/IDE actions

START NOW - Help Codex integrate CAS cognitive context into chat/IDE orchestration! 🚀
```

---

## 🔗 **COORDINATION WORKFLOW**

### **Step 1: Codex Posts Orchestration Design**
- ✅ **DONE** - Codex posted design to coordination board
- Reference: `agents/codex/COORDINATION_BOARD.md` (Post-Synthesis section)

### **Step 2: Agents Review and Respond**
- **Sage:** Review VIF witness API requirements, provide API details
- **Atlas:** Review integration tagging requirements, provide tag format
- **Chronos:** Review timeline logging requirements, provide logging details
- **Meta:** Review CAS cognitive context requirements, provide integration details

### **Step 3: Codex Implements with Agent Support**
- Codex implements orchestration layer with agent-provided details
- Agents support Codex during implementation
- Test integration points together

### **Step 4: Validate Integration**
- Test chat/IDE orchestration with all AIM-OS systems
- Validate witness creation, tagging, timeline logging, cognitive context
- Run end-to-end tests

---

## 📚 **KEY DOCUMENTS FOR COORDINATION**

**Codex's Design:**
- `CODEX_CHAT_IDE_COORDINATION_PROMPT.md` - Complete orchestration design
- `agents/codex/COORDINATION_BOARD.md` - Codex's coordination board

**Synthesis Outcomes:**
- `SYNTHESIS_SESSION_FINAL_OUTCOMES.md` - All synthesis decisions
- `SYNTHESIS_SESSION_PART4_STATUS.md` - Orchestration integration planning

**Orchestration Patterns:**
- `agents/sage/VIF_ORCHESTRATION_PATTERN_RECOMMENDATIONS.md` - VIF patterns
- `agents/META/CAS_ORCHESTRATION_PATTERN_RECOMMENDATIONS.md` - CAS patterns

---

**Status:** ✅ **COORDINATION PROMPTS READY**  
**Next:** Send prompts to Sage, Atlas, Chronos, and Meta for chat/IDE integration coordination

