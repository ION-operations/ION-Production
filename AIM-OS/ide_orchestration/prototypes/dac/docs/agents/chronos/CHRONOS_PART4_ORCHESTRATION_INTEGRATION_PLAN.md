# Chronos (TCS) - Part 4: Orchestration Integration Planning

**Agent:** Chronos (TCS System Specialist)  
**Date:** 2025-01-28  
**Route:** R-SYNTHESIS-001-SESSION  
**Session Part:** Part 4 - Orchestration Integration Planning

---

## 📋 **PART 4A: ORCHESTRATION RECOMMENDATIONS REVIEW**

### **1. VIF Orchestration Patterns (Sage Leads)**

**TCS Integration with VIF Orchestration:**

**Approved P0 Mandatory Flows:**
- ✅ **1.6 TCS Timeline Events (κ-Gate Decisions)** - **APPROVED**
  - **Flow:** `KappaGate.check()` → κ-gate decision made
  - **Witness Type:** κ-gate timeline entry (via TCS)
  - **Implementation:** `vif/tcs_integration.py::create_kappa_gate_timeline_entry()`
  - **Status:** ⚠️ Integration exists, needs to be mandatory for all κ-gate decisions
  - **TCS Action:** Ready to support mandatory κ-gate timeline entries

- ✅ **1.7 Chat/IDE Orchestrated Actions** - **APPROVED**
  - **Flow:** Router/Orchestrator → Action executed (code generation, file modification, etc.)
  - **Witness Type:** Action witness with full context (prompt, output, tools, confidence)
  - **TCS Integration:** Timeline entries can track orchestrated actions
  - **Status:** ⚠️ Integration exists, needs to be mandatory in orchestration paths
  - **TCS Action:** Ready to create timeline entries for all orchestrated actions

**TCS Confirmation:**
- ✅ **Support VIF Orchestration:** TCS ready to create timeline entries for all P0 mandatory flows
- ✅ **κ-Gate Timeline Entries:** Integration ready, can make mandatory
- ✅ **Orchestrated Action Tracking:** Timeline entries can track all user-facing actions

---

### **2. CAS Orchestration Patterns (Meta Leads)**

**TCS Integration with CAS Orchestration:**

**Approved Patterns:**
- ✅ **Pattern A: Continuous Monitoring** - **APPROVED**
  - **MCP Tool Used:** `mcp_lucid-mcp_add_timeline_entry` - Record cognitive events
  - **TCS Integration:** Timeline entries track CAS cognitive events (hourly introspection, drift detection)
  - **Status:** ✅ Ready - MCP tool available, integration documented

- ✅ **Pattern B: On-Demand Introspection** - **APPROVED**
  - **MCP Tool Used:** `mcp_lucid-mcp_add_timeline_entry` - Record cognitive events
  - **TCS Integration:** Timeline entries track pre/post-operation cognitive analysis
  - **Status:** ✅ Ready - MCP tool available, integration documented

- ✅ **Pattern C: Event-Driven Monitoring** - **APPROVED**
  - **MCP Tool Used:** `mcp_lucid-mcp_add_timeline_entry` - Record cognitive events
  - **TCS Integration:** Timeline entries track post-failure cognitive analysis
  - **Status:** ✅ Ready - MCP tool available, integration documented

**TCS Confirmation:**
- ✅ **Support CAS Orchestration:** TCS ready to track all CAS cognitive events via timeline entries
- ✅ **MCP Tool Available:** `add_timeline_entry` ready for CAS integration
- ✅ **Integration Documented:** `CHRONOS_TCS_CAS_INTEGRATION.md` complete

---

### **3. Integration Tagging Standardization (Atlas Leads)**

**TCS Integration Tagging:**

**Current Tags:**
- `type: "timeline_entry"` - Standard timeline entry tag
- `prompt_id: <id>` - Prompt identifier
- `entry_id: <id>` - Entry identifier
- `event_type: <type>` - Event type (e.g., "e2e_test", "kappa_gate", "cognitive_event")
- `hhni_index: True` - Flag for HHNI indexing

**Standardization Support:**
- ✅ **Support Standard Format:** TCS ready to use standardized `metadata.integration_tags` format
- ✅ **Current Tags Compatible:** Existing tags can be mapped to standard format
- ✅ **Integration Points:** All 7 integrations can use standardized tags

**TCS Recommendation:**
- Use `metadata.integration_tags` for cross-system integration tracking
- Preserve existing tags for backward compatibility
- Map existing tags to standard format during orchestration

---

## 🔗 **PART 4B: TCS INTEGRATION POINTS FOR CHAT/IDE FLOWS**

### **1. How TCS Integrates with Chat/IDE Flows**

**Integration Pattern:** **MCP Tools + Direct API Calls**

**Primary Integration:**
- **MCP Tools:** `add_timeline_entry`, `get_timeline_entries`, `get_timeline_summary`
- **Direct API:** `packages/timeline_context_system/prompt_context_tracker.py`
- **CMC Integration:** Timeline entries stored in CMC with `modality="tcs_timeline"`

---

### **2. What APIs/Functions Chat/IDE Calls**

**MCP Tools (Primary Interface):**

**1. `mcp_lucid-mcp_add_timeline_entry`**
- **Purpose:** Create timeline entry for interaction/event
- **When Called:**
  - User sends message → Create timeline entry
  - AI responds → Create timeline entry
  - κ-gate decision made → Create timeline entry (VIF integration)
  - Cognitive event occurs → Create timeline entry (CAS integration)
  - Plan executed → Create timeline entry (APOE integration)
- **Parameters:**
  - `event_type`: Type of event (e.g., "user_message", "ai_response", "kappa_gate", "cognitive_event")
  - `title`: Short title for the entry
  - `description`: Detailed description
  - `tags`: Array of tags (e.g., `["hhni_index", "e2e"]`)
  - `metadata`: Additional metadata (e.g., `{"correlation_id": "...", "confidence": 0.85}`)
- **Returns:** Timeline entry with `entry_id`, `prompt_id`, `timestamp`
- **Storage:** CMC atom with `modality="tcs_timeline"`

**2. `mcp_lucid-mcp_get_timeline_entries`**
- **Purpose:** Retrieve timeline entries for analysis/context
- **When Called:**
  - Session restoration → Get recent timeline entries
  - Context retrieval → Get timeline entries for specific time range
  - Analysis → Get timeline entries for cognitive analysis (CAS integration)
- **Parameters:**
  - `limit`: Number of entries to retrieve (default: 10)
  - `start_time`: Start timestamp (optional)
  - `end_time`: End timestamp (optional)
  - `event_type`: Filter by event type (optional)
  - `tags`: Filter by tags (optional)
- **Returns:** Array of timeline entries with full context
- **Source:** CMC atoms with `modality="tcs_timeline"`

**3. `mcp_lucid-mcp_get_timeline_summary`**
- **Purpose:** Get summary of recent timeline entries (session restoration)
- **When Called:**
  - Session start → Get timeline summary for context restoration
  - Context refresh → Get updated timeline summary
  - Dashboard display → Show recent timeline activity
- **Parameters:**
  - `limit`: Number of entries to include in summary (default: 10)
- **Returns:** Timeline summary with last N entries, key events, context highlights
- **Source:** CMC atoms with `modality="tcs_timeline"`

**Direct API (Alternative Interface):**

**1. `PromptContextTracker.track_prompt_context()`**
- **Purpose:** Track prompt context with full snapshot
- **When Called:** Direct Python integration (not via MCP)
- **Returns:** `ContextSnapshot` with full context state

**2. `TimelineAPI.get_timeline_entries()`**
- **Purpose:** Retrieve timeline entries via direct API
- **When Called:** Direct Python integration (not via MCP)
- **Returns:** Array of timeline entries

---

### **3. What Events TCS Emits**

**Timeline Entry Events:**
- **User Message:** Timeline entry created when user sends message
- **AI Response:** Timeline entry created when AI responds
- **κ-Gate Decision:** Timeline entry created when κ-gate decision made (VIF integration)
- **Cognitive Event:** Timeline entry created when cognitive event occurs (CAS integration)
- **Plan Execution:** Timeline entry created when plan executed (APOE integration)
- **Quality Validation:** Timeline entry created when quality validated (SDF-CVF integration)
- **Evidence Linking:** Timeline entry created when evidence linked (SEG integration)

**Event Flow:**
```
Chat/IDE Action
  → Orchestrator routes to appropriate system
  → System creates timeline entry via MCP tool
  → TCS stores in CMC (modality="tcs_timeline")
  → HHNI polls and indexes (indirect integration)
  → Timeline entry available for retrieval
```

---

### **4. What Orchestration Patterns Apply to TCS**

**Pattern 1: Session Continuity (MVP-Critical)**
- **Flow:** Session start → `get_timeline_summary()` → Restore context → Continue work
- **TCS Role:** Provide timeline summary for context restoration
- **Integration:** MCP tool `get_timeline_summary`
- **Priority:** P0 (MVP-Critical)

**Pattern 2: Action Tracking (MVP-Critical)**
- **Flow:** User action → Orchestrator → `add_timeline_entry()` → Store in CMC
- **TCS Role:** Track all user-facing actions for provenance
- **Integration:** MCP tool `add_timeline_entry`
- **Priority:** P0 (MVP-Critical)

**Pattern 3: κ-Gate Timeline Entries (P0 Mandatory)**
- **Flow:** κ-gate decision → VIF → `create_kappa_gate_timeline_entry()` → TCS → CMC
- **TCS Role:** Track all κ-gate decisions for audit trail
- **Integration:** `vif/tcs_integration.py::create_kappa_gate_timeline_entry()`
- **Priority:** P0 (Mandatory per VIF orchestration)

**Pattern 4: Cognitive Event Tracking (P1 Helper)**
- **Flow:** Cognitive event → CAS → `add_timeline_entry()` → TCS → CMC
- **TCS Role:** Track cognitive events for analysis
- **Integration:** MCP tool `add_timeline_entry` with CAS metadata
- **Priority:** P1 (Helper for MVP)

**Pattern 5: Plan Execution Tracking (P2 Post-MVP)**
- **Flow:** Plan executed → APOE → `create_execution_timeline_entry()` → TCS → CMC
- **TCS Role:** Track plan execution for timeline visualization
- **Integration:** `apoe/tcs_integration.py::create_execution_timeline_entry()`
- **Priority:** P2 (Post-MVP)

---

### **5. Integration Dependencies**

**TCS Dependencies:**
- **CMC (P0):** Required for timeline entry storage (MVP-Critical)
- **HHNI (P0):** Required for temporal context retrieval (MVP-Critical, indirect via CMC)
- **VIF (P1):** Helper for κ-gate timeline entries (P0 mandatory flow)
- **CAS (P1):** Helper for cognitive event tracking
- **SEG (P1):** Helper for evidence linking
- **SDF-CVF (P1):** Helper for quality validation tracking
- **APOE (P2):** Post-MVP for execution timeline tracking

**Dependencies on TCS:**
- **Chat/IDE:** Requires TCS for session continuity (MVP-Critical)
- **VIF:** Requires TCS for κ-gate timeline entries (P0 mandatory)
- **CAS:** Uses TCS for cognitive event tracking (P1 helper)
- **APOE:** Uses TCS for execution timeline tracking (P2 post-MVP)

---

## 🎯 **PART 4C: PRIORITIZE ORCHESTRATION WORK**

### **P0 (MVP-Critical) - Must Have for MVP**

**1. Session Continuity Integration** ✅ **READY**
- **Work:** Wire `get_timeline_summary()` into chat/IDE session start flow
- **Status:** MCP tool ready, integration documented
- **Effort:** ~2-4 hours (chat/IDE integration work)
- **Dependencies:** None (TCS ready)

**2. Action Tracking Integration** ✅ **READY**
- **Work:** Wire `add_timeline_entry()` into chat/IDE action flows
- **Status:** MCP tool ready, integration documented
- **Effort:** ~4-6 hours (chat/IDE integration work)
- **Dependencies:** None (TCS ready)

**3. κ-Gate Timeline Entries (VIF Integration)** ⚠️ **NEEDS MANDATORY FLAG**
- **Work:** Make `create_kappa_gate_timeline_entry()` mandatory in VIF κ-gate paths
- **Status:** Integration exists, needs to be mandatory
- **Effort:** ~2-3 hours (VIF integration work, TCS ready)
- **Dependencies:** VIF orchestration decision (approved P0)

**4. CMC Integration Verification** ✅ **COMPLETE**
- **Work:** Verify CMC integration works in orchestration flows
- **Status:** Integration complete, modality fixed
- **Effort:** ~1 hour (verification)
- **Dependencies:** None (TCS ready)

**5. HHNI E2E Validation** ⏳ **SCHEDULED**
- **Work:** Execute E2E runbook (post-session, 24-48 hours)
- **Status:** Coordination confirmed, runbook ready
- **Effort:** ~15-20 minutes (execution)
- **Dependencies:** @Sev availability (scheduled)

---

### **P1 (Post-MVP) - Nice to Have**

**1. Cognitive Event Tracking (CAS Integration)**
- **Work:** Enhance CAS integration for cognitive event tracking
- **Status:** Integration exists, can be enhanced
- **Effort:** ~4-6 hours
- **Dependencies:** CAS orchestration patterns (approved)

**2. Evidence Linking Tracking (SEG Integration)**
- **Work:** Enhance SEG integration for evidence linking tracking
- **Status:** Integration exists, can be enhanced
- **Effort:** ~4-6 hours
- **Dependencies:** SEG evidence linking (approved)

**3. Quality Validation Tracking (SDF-CVF Integration)**
- **Work:** Enhance SDF-CVF integration for quality validation tracking
- **Status:** Integration exists, can be enhanced
- **Effort:** ~4-6 hours
- **Dependencies:** SDF-CVF enhancement priorities

**4. Full Integration Test Coverage**
- **Work:** Add explicit tests for VIF and HHNI integrations
- **Status:** 4/7 explicit tests, can add more
- **Effort:** ~6-8 hours
- **Dependencies:** None (TCS ready)

---

### **P2 (Post-MVP) - Future Enhancements**

**1. Plan Execution Tracking (APOE Integration)**
- **Work:** Enhance APOE integration for execution timeline tracking
- **Status:** Integration exists, can be enhanced
- **Effort:** ~4-6 hours
- **Dependencies:** APOE orchestration patterns

**2. Advanced Timeline Features**
- **Work:** Evolution explorer, dual prompt enhancements
- **Status:** Features exist, can be enhanced
- **Effort:** ~10-15 hours
- **Dependencies:** None (TCS ready)

**3. Core Test Import Fixes**
- **Work:** Fix pre-existing import issues in core test suite
- **Status:** Fix plan ready
- **Effort:** ~1.5 hours
- **Dependencies:** None (TCS ready)

---

## 📅 **PART 4D: TIMELINE FOR INTEGRATION**

### **Immediate (Post-Synthesis)**

**Week 1 (2025-01-29 to 2025-02-04):**

**TCS Work:**
- [ ] Execute HHNI E2E runbook (2025-01-29 or 2025-01-30, ~15-20 min)
- [ ] Post E2E results to coordination board
- [ ] Update G3 goal status (E2E complete = G3 100%)

**Chat/IDE Integration Work (Codex):**
- [ ] Wire `get_timeline_summary()` into session start flow (~2-4 hours)
- [ ] Wire `add_timeline_entry()` into action flows (~4-6 hours)
- [ ] Test session continuity demonstration

**VIF Integration Work (Sage):**
- [ ] Make `create_kappa_gate_timeline_entry()` mandatory in κ-gate paths (~2-3 hours)
- [ ] Test κ-gate timeline entries in orchestration flows

**Total TCS Effort:** ~1 hour (E2E execution + results)
**Total Chat/IDE Effort:** ~6-10 hours (session continuity + action tracking)
**Total VIF Effort:** ~2-3 hours (mandatory κ-gate timeline entries)

---

### **Short-Term (Next 1-2 Weeks)**

**Week 2 (2025-02-05 to 2025-02-11):**

**TCS Work:**
- [ ] Partner validation confirmations (SDF-CVF, CAS) - if not done in Part 3
- [ ] Monitor orchestration integration progress
- [ ] Support chat/IDE integration testing

**Chat/IDE Integration Work (Codex):**
- [ ] Complete session continuity integration
- [ ] Complete action tracking integration
- [ ] Test end-to-end orchestration flows

**VIF Integration Work (Sage):**
- [ ] Complete mandatory κ-gate timeline entries
- [ ] Test κ-gate timeline entries in production flows

**Total TCS Effort:** ~2-4 hours (support + validation)
**Total Chat/IDE Effort:** ~10-15 hours (complete integration + testing)
**Total VIF Effort:** ~4-6 hours (complete integration + testing)

---

### **Timeline Dependencies**

**TCS Dependencies:**
- **None** - TCS ready, no dependencies on other agents for MVP work

**Dependencies on TCS:**
- **Chat/IDE (Codex):** Requires TCS MCP tools for session continuity (P0)
- **VIF (Sage):** Requires TCS integration for κ-gate timeline entries (P0 mandatory)
- **CAS (Meta):** Uses TCS for cognitive event tracking (P1 helper)

**Critical Path:**
1. TCS E2E validation (post-session, 24-48 hours) → Completes G3 goal
2. Chat/IDE session continuity integration (Week 1) → MVP demonstration
3. VIF mandatory κ-gate timeline entries (Week 1) → P0 mandatory flow
4. Chat/IDE action tracking integration (Week 1-2) → MVP demonstration

---

## 🎯 **TCS ORCHESTRATION INTEGRATION SUMMARY**

### **MVP-Critical Integration Points (P0)**

**1. Session Continuity (Chat/IDE → TCS)**
- **API:** `mcp_lucid-mcp_get_timeline_summary()`
- **When:** Session start, context restoration
- **Status:** ✅ Ready
- **Effort:** ~2-4 hours (chat/IDE integration)

**2. Action Tracking (Chat/IDE → TCS)**
- **API:** `mcp_lucid-mcp_add_timeline_entry()`
- **When:** User actions, AI responses, orchestrated actions
- **Status:** ✅ Ready
- **Effort:** ~4-6 hours (chat/IDE integration)

**3. κ-Gate Timeline Entries (VIF → TCS)**
- **API:** `vif/tcs_integration.py::create_kappa_gate_timeline_entry()`
- **When:** κ-gate decisions (P0 mandatory flow)
- **Status:** ⚠️ Integration exists, needs mandatory flag
- **Effort:** ~2-3 hours (VIF integration)

**4. CMC Storage (TCS → CMC)**
- **API:** Direct CMC integration via `modality="tcs_timeline"`
- **When:** All timeline entry creation
- **Status:** ✅ Complete
- **Effort:** None (already working)

**5. HHNI Indexing (TCS → CMC → HHNI)**
- **API:** Indirect via CMC atoms, HHNI poller
- **When:** Timeline entries with `hhni_index` tag
- **Status:** ⏳ E2E validation scheduled
- **Effort:** ~15-20 minutes (E2E execution)

---

### **Post-MVP Integration Points (P1+)**

**P1 Helpers:**
- Cognitive event tracking (CAS → TCS)
- Evidence linking tracking (SEG → TCS)
- Quality validation tracking (SDF-CVF → TCS)

**P2 Post-MVP:**
- Plan execution tracking (APOE → TCS)
- Advanced timeline features
- Full integration test coverage

---

## ✅ **TCS ORCHESTRATION READINESS**

**MVP Status:** ✅ **READY**

**Integration Points:**
- ✅ Session continuity (MCP tool ready)
- ✅ Action tracking (MCP tool ready)
- ✅ κ-Gate timeline entries (integration ready, needs mandatory flag)
- ✅ CMC storage (complete)
- ⏳ HHNI indexing (E2E validation scheduled)

**Orchestration Patterns:**
- ✅ Support VIF orchestration (P0 mandatory flows)
- ✅ Support CAS orchestration (P1 helper patterns)
- ✅ Support integration tagging standardization

**Timeline:**
- ✅ Immediate work ready (E2E execution, support chat/IDE integration)
- ✅ Short-term work ready (partner validations, support testing)

**Dependencies:**
- ✅ No TCS dependencies on other agents for MVP
- ✅ Other agents can depend on TCS (MCP tools available)

---

**Status:** ✅ **ORCHESTRATION READY** - All MVP integration points ready, timeline defined  
**Confidence:** High (0.95) - MCP tools available, integrations documented, orchestration patterns supported

