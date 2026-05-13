# Codex Task 1.2 Verification Checklist
**Date:** 2025-01-28  
**For:** Codex  
**Purpose:** Execute verification tests to complete Task 1.2

---

## ⚠️ **VERIFICATION REQUIREMENTS**

**Blocker Identified:** Verification requires UI-driven flows (Chat Panel + Code Execution hooks) to trigger `IntegrationTagContext` creation and MCP calls.

**Current Status:**
- ✅ Command Server is alive on `http://localhost:5001`
- ✅ Backend pipeline is reachable
- ⚠️ **BLOCKER:** CLI environment cannot interact with React UI components
- ⚠️ **BLOCKER:** Cannot trigger chat/code actions without UI

**Verification Options:**
1. **UI-Driven Run (Recommended):** Execute tests from actual IDE session
2. **Captured Payloads/Logs:** Use previously captured evidence from UI testing
3. **Test Script (Alternative):** Create script that simulates UI flows (if possible)

**Next Steps:**
- Wait for UI-driven verification run
- OR use captured payloads/logs if available
- OR create test script to simulate flows

---

## ✅ **VERIFICATION CHECKLIST**

### **Test 1: Chat Message Tag Flow** ⏳

**Steps:**
1. [ ] Send a chat message in the IDE
2. [ ] Inspect payload hitting `/mcp/execute` (Command Server logs)
3. [ ] Verify `metadata.integration_tags` includes:
   - [ ] `system:apoe:*` (or appropriate system tag)
   - [ ] `mode:*` (e.g., `mode:synthesis`, `mode:execution`)
   - [ ] `agent:*` (e.g., `agent:planning`, `agent:coding`)
   - [ ] `chat_ide` (base tag)

**Expected Result:** Tags present in MCP payload  
**Location to Check:** Command Server logs for `/mcp/execute` endpoint

---

### **Test 2: Code Execution Tag Flow** ⏳

**Steps:**
1. [ ] Trigger code execution via IDE hook
2. [ ] Verify resulting MCP requests contain expected tag set:
   - [ ] `mcp_lucid-mcp_store_memory` → tags present in metadata
   - [ ] `mcp_lucid-mcp_track_confidence` → tags present in metadata
   - [ ] `mcp_lucid-mcp_add_timeline_entry` → tags present in metadata

**Expected Result:** All MCP calls tagged (chat→MCP)  
**Location to Check:** Command Server logs for each MCP tool call

---

### **Test 3: APOE Plan Tag Flow** ⏳

**Steps:**
1. [ ] Run an APOE plan (e.g., via `PlanExecutor` unit tests)
2. [ ] Check stored witness atoms in CMC/HHNI
3. [ ] Verify `integration_tags` show:
   - [ ] `system:vif:*` (or appropriate system tag)
   - [ ] `integration_type:witness`
   - [ ] Originating action tags (from chat context)

**Expected Result:** Tags flow through MCP→APOE→CMC→HHNI/SEG path  
**Location to Check:** CMC atom storage, HHNI indexes

---

### **Test 4: End-to-End Tag Propagation** ⏳

**Steps:**
1. [ ] Send chat message → Verify tags in MCP payload
2. [ ] Execute code → Verify tags in CMC storage
3. [ ] Create witness → Verify tags in VIF witness
4. [ ] Check HHNI → Verify tags indexed
5. [ ] Check SEG → Verify tags linked (if applicable)

**Expected Result:** Tags flow end-to-end: Chat → MCP → APOE → CMC → HHNI → SEG  
**Location to Check:** Complete flow through all systems

---

## 📝 **VERIFICATION NOTES**

**Quick Verification Tips:**
- Command Server logs should show `metadata.integration_tags` array in MCP payloads
- CMC atoms should have `metadata.integration_tags` field populated
- HHNI indexes should include tags in searchable metadata
- Tags should match the context from `AdvancedChatPanel.tsx` (mode, agent, etc.)

**Verification Evidence Sources:**
1. **Command Server Logs:** `cursor-addon/src/commandServer.ts` (line 439) - Request logging
2. **MCP Payloads:** `/mcp/execute` endpoint requests
3. **CMC Atoms:** Stored atoms with `metadata.integration_tags`
4. **HHNI Indexes:** Indexed metadata with tags

**If Issues Found:**
- Document any missing tags or incorrect formats
- Check tag propagation at each integration point
- Verify `IntegrationTagContext` is being created correctly in UI
- Verify `MCPService.executeTool()` is receiving and injecting context

**Blocker Resolution:**
- Verification requires UI-driven flows (Chat Panel + Code Execution)
- CLI environment cannot trigger UI components
- Need actual IDE session OR captured payloads/logs
- See "Verification Requirements" section above

---

## ✅ **COMPLETION CRITERIA**

**Task 1.2 Complete When:**
- [ ] All 4 verification tests pass
- [ ] Tags visible in MCP payloads
- [ ] Tags visible in CMC atoms
- [ ] Tags visible in HHNI indexes
- [ ] End-to-end flow verified

**After Verification:**
1. Update `CHAT_IDE_IMPLEMENTATION_PROGRESS.md` - Mark Task 1.2 as 100% complete
2. Update `agents/codex/COORDINATION_BOARD.md` - Post completion notice
3. Begin Task 1.3 (Timeline Logging)

---

**Status:** ⏳ **READY FOR VERIFICATION**  
**Next:** Execute tests, document results, mark complete

