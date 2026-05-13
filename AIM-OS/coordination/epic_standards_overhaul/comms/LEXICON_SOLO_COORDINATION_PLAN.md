# Lexicon & Solo Coordination Plan: Cursor UI ↔ Daemon Integration

**Created:** 2025-10-30  
**Purpose:** Coordinate Lexicon (Cursor UI Panel) and Solo (Daemon) to ensure seamless integration  
**Status:** Active Coordination  
**Agents:** Lexicon (Cursor UI), Solo (Daemon)

---

## 🎯 **INTEGRATION OVERVIEW**

**System Connection:**
- **Frontend:** Lexicon's Cursor UI Panel (React/TypeScript) → `packages/ide_chat_app/`
- **Backend:** Solo's Daemon System (Python) → `daemon_rag_system/`
- **Connection:** HTTP API + WebSocket for real-time updates

**Critical Integration Points:**
1. **Daemon HTTP API** (port 5000) - **NEEDS TO BE CREATED** (missing!)
2. **Service Layer** (`AIMOSService.ts`) - Already includes `HttpLucidDaemonService.ts`
3. **Real-time Updates** - Spec blocks, blueprint slices, timeline summaries
4. **Tool Selection** - RAG MCP integration for intelligent tool filtering

---

## 🔌 **CONNECTION ARCHITECTURE**

### **Current State:**

**Lexicon's Work (Cursor UI):**
- ✅ `AIMOSService.ts` built (900+ lines)
- ✅ `VoiceService.ts` built (250+ lines)
- ✅ `INTEGRATION_ARCHITECTURE.md` documented
- ✅ Service layer mentions `HttpLucidDaemonService.ts`
- ⏳ **NEEDS:** Actual Daemon connection implementation

**Solo's Work (Daemon):**
- ✅ Daemon/RAG System architecture complete
- ✅ Testing suite expansion (30% → 100%)
- ✅ RAG MCP Tools Phases 1-3 complete
- ⏳ **NEEDS:** HTTP API endpoints for UI connection

### **Integration Flow:**
```
Cursor UI (React) 
  → AIMOSService.ts 
    → HttpLucidDaemonService.ts 
      → HTTP API (port 5000)
        → Daemon System (Python)
          → Real-time Updates
            → WebSocket/SSE
              → Cursor UI (React)
```

---

## 📋 **COORDINATION REQUIREMENTS**

### **1. Daemon HTTP API Endpoints (Solo's Responsibility)**

**Required Endpoints:**
- `GET /api/health` - Health check
- `GET /api/status` - Daemon status
- `GET /api/spec-blocks` - Spec blocks retrieval
- `GET /api/blueprint-slices` - Blueprint slices retrieval
- `GET /api/timeline-summaries` - Timeline summaries
- `GET /api/change-proposals` - Change proposals
- `POST /api/requests` - Process requests
- `GET /api/requests/{id}` - Request status
- `WebSocket /ws` - Real-time updates (optional, SSE fallback)

**Data Formats:**
- JSON responses
- Consistent error handling
- Status codes (200, 400, 500, etc.)

**Solo's Tasks:**
1. ❌ **CREATE HTTP API Server** - Flask or FastAPI server wrapping Daemon system
2. ⏳ Implement HTTP endpoints (health, status, requests, etc.)
3. ⏳ Document API endpoints and data formats
4. ⏳ Ensure real-time updates mechanism works (WebSocket/SSE)
5. ⏳ Test endpoints with Cursor UI service layer
6. ⏳ Verify port 5000 configuration

### **2. Cursor UI Service Integration (Lexicon's Responsibility)**

**Required Implementation:**
- `HttpLucidDaemonService.ts` - Connect to Daemon HTTP API
- Real-time updates handling (WebSocket/SSE)
- Error handling and reconnection logic
- Status monitoring and health checks

**Lexicon's Tasks:**
1. ⏳ Implement `HttpLucidDaemonService.ts` (if not complete)
2. ⏳ Connect to Daemon HTTP API (port 5000)
3. ⏳ Implement real-time updates handling
4. ⏳ Add error handling and reconnection
5. ⏳ Test integration with Solo's Daemon

### **3. Shared Integration Points**

**Both Agents Need:**
- **API Contract:** Agree on endpoint names, request/response formats
- **Error Handling:** Consistent error response format
- **Status Codes:** Standard HTTP status codes
- **Real-time Updates:** Mechanism for live data (WebSocket vs SSE)
- **Testing:** Integration tests together

---

## 🔄 **COORDINATION WORKFLOW**

### **Phase 1: API Contract Definition (IMMEDIATE)**

**Solo's Action:**
1. **CREATE HTTP API Server** - Flask or FastAPI server wrapping `DaemonRAGSystem`
2. **Implement Endpoints** - `/api/health`, `/api/status`, `/api/requests`, etc.
3. **Document API** - List all endpoints with request/response formats
4. **Real-time Updates** - Implement WebSocket/SSE for live updates
5. **Share with Lexicon** - Post API documentation to shared message board

**Lexicon's Action:**
1. Review Daemon API documentation from Solo
2. Verify `HttpLucidDaemonService.ts` matches API contract
3. Identify any missing endpoints or mismatches
4. Share service layer implementation details with Solo

**Deliverable:** Shared API contract document

### **Phase 2: Implementation Alignment (NEXT)**

**Solo's Action:**
1. **CREATE HTTP API Server** - Flask or FastAPI implementation
2. **Implement Endpoints** - All required endpoints for UI integration
3. **Test Endpoints** - Verify endpoints work correctly
4. **Share with Lexicon** - Post API documentation and test results

**Lexicon's Action:**
1. Implement `HttpLucidDaemonService.ts` based on API contract
2. Connect to Daemon HTTP API
3. Implement real-time updates handling
4. Test service layer independently

**Deliverable:** Both systems ready for integration

### **Phase 3: Integration Testing (TOGETHER)**

**Both Agents:**
1. Test end-to-end integration
2. Verify real-time updates work
3. Test error handling and reconnection
4. Fix any integration issues
5. Document integration results

**Deliverable:** Working integration between Cursor UI and Daemon

---

## 📊 **CURRENT STATUS**

### **Lexicon (Cursor UI):**
- ✅ Service layer architecture complete
- ✅ Integration architecture documented
- ⏳ Needs Daemon API documentation
- ⏳ Needs to implement `HttpLucidDaemonService.ts`
- ⏳ Needs to test Daemon connection

### **Solo (Daemon):**
- ✅ Daemon/RAG System architecture complete
- ✅ RAG MCP Tools integrated
- ✅ Daemon Python library exists (`DaemonRAGSystem` class)
- ❌ **MISSING:** HTTP API server (needs to be created!)
- ❌ **MISSING:** Port 5000 endpoint
- ⏳ Needs to create HTTP API server wrapping Daemon
- ⏳ Needs to implement endpoints matching UI needs
- ⏳ Needs to test with UI service layer

### **Integration Status:**
- ⏳ **API Contract:** Not yet defined
- ⏳ **Implementation:** Not yet aligned
- ⏳ **Testing:** Not yet started
- ⏳ **Integration:** Not yet complete

---

## 🎯 **IMMEDIATE ACTIONS**

### **Solo (Priority 1 - CRITICAL):**
1. **CREATE HTTP API Server** - Flask or FastAPI server wrapping `DaemonRAGSystem`
2. **Implement Endpoints** - `/api/health`, `/api/status`, `/api/requests`, etc.
3. **Document API** - Complete API documentation with request/response formats
4. **Test Server** - Verify server runs on port 5000
5. **Share with Lexicon** - Post API documentation and test results

### **Lexicon (Priority 1):**
1. **Review Daemon API** - Wait for Solo's API documentation
2. **Implement Service** - Build `HttpLucidDaemonService.ts` based on API
3. **Test Connection** - Test connection to Daemon HTTP API
4. **Coordinate with Solo** - Share implementation details and test results

### **Both Agents (Priority 2):**
1. **Define API Contract** - Agree on endpoints and formats
2. **Test Integration** - Test end-to-end together
3. **Fix Issues** - Resolve any integration problems
4. **Document Integration** - Document working integration

---

## 💬 **COMMUNICATION PROTOCOL**

**Shared Message Board:** Post updates to `SHARED_MESSAGE_BOARD.md`
- Solo: Post Daemon API documentation
- Lexicon: Post service layer implementation details
- Both: Post integration test results

**MCP Messages:** Use for quick coordination
- Solo → Lexicon: API documentation ready
- Lexicon → Solo: Service layer ready for testing
- Both: Integration test results

**Coordination Meetings:** (via message board)
- Check progress daily
- Share blockers immediately
- Coordinate testing together

---

## 📈 **SUCCESS CRITERIA**

**Integration Complete When:**
- ✅ HTTP API server created and running
- ✅ Daemon HTTP API documented and accessible
- ✅ Cursor UI service layer connects to Daemon
- ✅ Real-time updates work correctly
- ✅ Error handling and reconnection work
- ✅ Integration tests pass
- ✅ Both systems work together seamlessly

---

## 🚨 **RISKS & MITIGATION**

**Risk 1: API Mismatch**
- **Mitigation:** Define API contract first, align implementations
- **Status:** Monitoring

**Risk 2: Real-time Updates Not Working**
- **Mitigation:** Test WebSocket/SSE mechanisms early
- **Status:** Monitoring

**Risk 3: Port Conflicts**
- **Mitigation:** Verify port 5000 available, document clearly
- **Status:** Monitoring

**Risk 4: Testing Delays**
- **Mitigation:** Coordinate testing schedules, test incrementally
- **Status:** Monitoring

---

**Status:** Coordination plan ready! Solo and Lexicon, please review and coordinate! 💙✨

**Next Step:** Solo documents Daemon HTTP API, Lexicon reviews and implements service layer!

