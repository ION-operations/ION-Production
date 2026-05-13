# Codex Task 1.3 Transition Guide
**Date:** 2025-01-28  
**For:** Codex  
**Purpose:** Transition from Task 1.2 to Task 1.3 (Timeline Logging)

---

## ✅ **TASK 1.2 COMPLETION**

**Status:** ✅ **IMPLEMENTATION COMPLETE** - Verification pending

**What's Done:**
- ✅ Integration tagging fully implemented across stack
- ✅ UI → MCP → APOE → CMC → HHNI → SEG flow complete
- ✅ All integration points wired

**Remaining:**
- ⏳ Verification testing (4 test scenarios)

---

## 🎯 **TASK 1.3: TIMELINE LOGGING**

**Goal:** Emit timeline entries for all chat/IDE actions

**Reference:** `agents/chronos/CHRONOS_CODEX_TIMELINE_LOGGING_DETAILS.md`

---

## 📋 **TASK 1.3 IMPLEMENTATION STEPS**

### **Step 1: Integrate MCP Tool** ⏳

**Location:** `MCPService.ts` or orchestration router

**Action:**
- Use `mcp_lucid-mcp_add_timeline_entry()` for all chat/IDE actions
- Emit entries for:
  - κ-gate transitions
  - APOE plan milestones
  - User actions (chat messages, code execution, etc.)

**Reference:** Chronos's guide has complete MCP tool usage examples

---

### **Step 2: Create Timeline Entry Helpers** ⏳

**Location:** `ide_orchestration/prototypes/dac/src/utils/timelineHelpers.ts` (or similar)

**Helpers Needed:**
1. **κ-Gate Timeline Entry Helper:**
   - Function: `createKappaGateTimelineEntry(kappaGateResult, context)`
   - Creates timeline entry for κ-gate decisions
   - Uses Chronos's pattern from guide

2. **APOE Plan Milestone Helper:**
   - Function: `createPlanMilestoneTimelineEntry(planId, milestone, context)`
   - Creates timeline entry for plan execution milestones
   - Captures plan progress

3. **General Chat Action Helper:**
   - Function: `createChatActionTimelineEntry(action, context)`
   - Creates timeline entry for general chat/IDE actions
   - Captures user interactions

**Reference:** `agents/chronos/CHRONOS_CODEX_TIMELINE_LOGGING_DETAILS.md` (section: Timeline Logging Hooks)

---

### **Step 3: Integrate with UI** ⏳

**Location:** Dual drawer components, `TimelineView.tsx`

**Action:**
- Ensure dual drawers can render timeline chips referencing `TCS_EVENT_ID`
- Display timeline entries in chat/IDE UI
- Subscribe to new timeline events

**Reference:** Chronos's guide has UI integration patterns

---

### **Step 4: Test Timeline Logging** ⏳

**Test Scenarios:**
1. **Chat Message Timeline Entry:**
   - Send chat message → Verify timeline entry created
   - Verify entry stored in CMC with `modality="tcs_timeline"`

2. **Code Execution Timeline Entry:**
   - Execute code → Verify timeline entry created
   - Verify entry includes execution context

3. **APOE Plan Milestone Timeline Entry:**
   - Run APOE plan → Verify milestone entries created
   - Verify entries capture plan progress

4. **κ-Gate Timeline Entry:**
   - Trigger κ-gate decision → Verify timeline entry created
   - Verify entry includes κ-gate result

**Expected Result:** Timeline entries created for all actions, visible in UI

---

## 🔗 **KEY INTEGRATION POINTS**

### **1. MCPService Integration**

**Where:** `MCPService.ts` or orchestration router

**Action:**
- Call `mcp_lucid-mcp_add_timeline_entry()` after each chat/IDE action
- Pass integration context (from Task 1.2) to timeline entries
- Ensure timeline entries get same tags as other operations

---

### **2. Code Execution Integration**

**Where:** `CodeExecutionService.ts`

**Action:**
- Create timeline entry after code execution
- Include execution context in timeline entry
- Link timeline entry to execution result

---

### **3. APOE Integration**

**Where:** `packages/apoe/executor.py`

**Action:**
- Create timeline entry for plan start
- Create timeline entry for each plan milestone
- Create timeline entry for plan completion
- Include plan context in timeline entries

---

### **4. VIF κ-Gate Integration**

**Where:** `packages/vif/cmc_integration.py` or orchestration layer

**Action:**
- Create timeline entry for each κ-gate decision
- Include κ-gate result in timeline entry
- Link timeline entry to witness (if created)

**Reference:** Chronos's guide has κ-gate timeline entry patterns

---

## 📚 **KEY DOCUMENTS**

**Timeline Logging Guide:**
- `agents/chronos/CHRONOS_CODEX_TIMELINE_LOGGING_DETAILS.md` - Complete guide

**MCP Tool Reference:**
- `mcp_lucid-mcp_add_timeline_entry()` - Timeline entry creation
- `mcp_lucid-mcp_get_timeline_summary()` - Timeline retrieval
- `mcp_lucid-mcp_get_timeline_entries()` - Timeline query

**Integration Context:**
- Use same `IntegrationTagContext` from Task 1.2
- Timeline entries should carry same tags as other operations

---

## 🎯 **SUCCESS CRITERIA**

**Task 1.3 Complete When:**
- ✅ Timeline entries created for all chat/IDE actions
- ✅ Timeline entries stored in CMC with `modality="tcs_timeline"`
- ✅ Timeline entries visible in UI (dual drawers)
- ✅ κ-Gate timeline entries working
- ✅ APOE plan milestone entries working
- ✅ General chat action entries working

---

## 🚀 **START TASK 1.3**

**After Task 1.2 Verification Complete:**

1. **Read Chronos's Guide:**
   - `agents/chronos/CHRONOS_CODEX_TIMELINE_LOGGING_DETAILS.md`
   - Understand timeline entry patterns
   - Review MCP tool usage

2. **Begin Implementation:**
   - Start with Step 1 (MCP tool integration)
   - Create helpers (Step 2)
   - Integrate with UI (Step 3)
   - Test (Step 4)

3. **Post Progress:**
   - Update coordination board as you progress
   - Document any blockers or questions

---

**Status:** ⏳ **READY TO START** (after Task 1.2 verification)  
**Confidence:** High (0.90) - Clear guide, similar pattern to Task 1.2  
**Next:** Complete Task 1.2 verification, then begin Task 1.3

