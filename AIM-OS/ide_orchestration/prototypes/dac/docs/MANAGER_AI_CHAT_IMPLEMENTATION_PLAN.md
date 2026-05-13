# Manager AI Chat - Implementation Plan
## Phase 2: Core Functionality Implementation

**Date:** 2025-01-27  
**Status:** Implementation In Progress  
**Purpose:** Detailed implementation plan for Phase 2 core functionality

---

## ✅ **COMPLETED (Phase 2.1)**

### **1. LLM Service Created** ✅
- **File:** `ide_orchestration/prototypes/dac/src/services/LLMService.ts`
- **Features:**
  - Command Server integration (`/aimos/chat` endpoint)
  - Streaming support
  - Error handling
  - Future: Direct LLM API integration

### **2. Manager AI Chat Enhanced** ✅
- **File:** `ide_orchestration/prototypes/dac/src/components/ManagerAIChat.tsx`
- **Changes:**
  - Integrated LLM service
  - Real LLM calls via Command Server
  - Streaming support (partial)
  - Enhanced system prompts

---

## 🚧 **IN PROGRESS**

### **3. Streaming Response Refinement**
**Status:** Needs refinement
**Issues:**
- Streaming logic needs better integration with response flow
- Need to handle streaming for direct responses only
- Error handling for streaming failures

**Next Steps:**
1. Refine streaming logic in `handleSend`
2. Add proper streaming state management
3. Handle streaming errors gracefully

---

## 📋 **REMAINING TASKS**

### **Phase 2.2: Specialized AI Delegation** ⭐ HIGH PRIORITY

**Tasks:**
1. **Integrate AI Collaboration System MCP Tools**
   - Use `mcp_lucid-mcp_handoff_task_to_ai` for delegation
   - Use `mcp_lucid-mcp_get_ai_messages` for monitoring
   - Use `mcp_lucid-mcp_get_ai_collaboration_summary` for status

2. **Implement Agent Matching Logic**
   - Enhance `analyzeRequest` with better agent matching
   - Use agent profiles and capabilities
   - Match tasks to agent strengths

3. **Implement Task Handoff**
   - Create handoff request with full context
   - Monitor handoff progress
   - Report back to user

4. **Add Delegation Status Display**
   - Show delegation status in message
   - Display agent progress
   - Update when task completes

**Estimated Time:** 3-4 hours

---

### **Phase 2.3: APOE Integration** ⭐ HIGH PRIORITY

**Tasks:**
1. **Integrate APOE Plan Creation**
   - Use `mcp_lucid-mcp_create_plan` for complex tasks
   - Pass proper context and goals
   - Handle plan creation errors

2. **Implement Plan Execution Monitoring**
   - Track plan execution progress
   - Display plan steps
   - Show completion status

3. **Display Plan Progress**
   - Show plan steps in message
   - Display progress percentage
   - Highlight current step

4. **Handle Plan Results**
   - Display plan results
   - Show execution summary
   - Link to related resources

**Estimated Time:** 2-3 hours

---

### **Phase 2.4: System Status Display** ⭐ MEDIUM PRIORITY

**Tasks:**
1. **Create SystemStatusSidebar Component**
   - Display AIM-OS system health
   - Show key metrics
   - Color-coded status indicators

2. **Integrate CAS Metrics**
   - Use `useCAS()` hook
   - Display health scores
   - Show attention metrics

3. **Display System Health**
   - Real-time health updates
   - Alert on degraded systems
   - Show last update timestamp

4. **Add Real-time Updates**
   - Poll for system status
   - Update UI automatically
   - Handle connection errors

**Estimated Time:** 2 hours

---

### **Phase 2.5: Enhanced Message Rendering** ⭐ MEDIUM PRIORITY

**Tasks:**
1. **Enhance Message Component**
   - Display full AIM-OS metadata
   - Show confidence badges
   - Display evidence trails

2. **Add Evidence Trail Display**
   - Clickable evidence sources
   - Show relevance scores
   - Link to CMC atoms

3. **Add System Actions Display**
   - Show which systems were used
   - Display action results
   - Link to system details

4. **Add Canvas Actions Display**
   - "Create Canvas" button
   - "Add to Canvas" button
   - Canvas reference links

**Estimated Time:** 2-3 hours

---

## 🔧 **TECHNICAL IMPROVEMENTS NEEDED**

### **1. Request Analysis Enhancement**
**Current:** Simple keyword matching
**Needed:** 
- LLM-based intent understanding
- Context-aware analysis
- Better agent matching

### **2. Error Handling**
**Current:** Basic error catching
**Needed:**
- Retry logic for LLM calls
- Graceful degradation
- User-friendly error messages

### **3. Performance Optimization**
**Current:** Basic implementation
**Needed:**
- Response caching
- Context optimization
- Lazy loading

### **4. Testing**
**Current:** No tests
**Needed:**
- Unit tests for LLM service
- Integration tests for chat flow
- E2E tests for user interactions

---

## 📊 **PROGRESS TRACKING**

| Phase | Task | Status | Priority |
|-------|------|--------|----------|
| 2.1 | LLM Service | ✅ Complete | HIGH |
| 2.1 | LLM Integration | ✅ Complete | HIGH |
| 2.1 | Streaming Support | 🚧 Partial | HIGH |
| 2.2 | AI Delegation | ⏳ Pending | HIGH |
| 2.3 | APOE Integration | ⏳ Pending | HIGH |
| 2.4 | System Status | ⏳ Pending | MEDIUM |
| 2.5 | Message Rendering | ⏳ Pending | MEDIUM |

---

## 🎯 **NEXT IMMEDIATE STEPS**

1. **Refine Streaming Logic** (30 min)
   - Fix streaming integration
   - Handle errors properly
   - Test streaming flow

2. **Implement AI Delegation** (3-4 hours)
   - Integrate MCP tools
   - Implement handoff
   - Add status display

3. **Implement APOE Integration** (2-3 hours)
   - Create plans
   - Monitor execution
   - Display progress

---

**Status:** Phase 2.1 Complete, Phase 2.2-2.5 Pending  
**Next:** Refine streaming, then implement AI delegation

