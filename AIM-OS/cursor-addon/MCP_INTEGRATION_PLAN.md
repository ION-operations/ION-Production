# MCP Integration Plan for Electron App

**Date:** 2025-11-01  
**Status:** Planning  
**Goal:** Enable Electron app to use MCP tools via Extension

---

## 🎯 **THE ARCHITECTURE**

### **Current Setup:**
```
Cursor IDE
    ↓ (via mcp.json)
MCP Server (Python stdio)
    ↓ JSON-RPC 2.0
MCP Tools (59 tools available)
```

### **Extension Integration:**
```
Extension (VS Code API)
    ↓ spawns Python process
MCP Server (run_mcp_6_tools.py)
    ↓ JSON-RPC 2.0 stdio
MCP Tools
```

### **Electron Integration (NEW):**
```
Electron App
    ↓ HTTP API
Extension Command Server (port 5001)
    ↓ VS Code API
Extension MCP Client
    ↓ spawns Python process
MCP Server
    ↓ JSON-RPC 2.0 stdio
MCP Tools
```

---

## ✅ **IMPLEMENTATION PLAN**

### **Step 1: Add MCP Tool Execution to Extension Command Server**

**File:** `cursor-addon/src/commandServer.ts`

**Add new endpoint:** `POST /mcp/execute`

**Functionality:**
- Receives tool name and arguments from Electron
- Uses existing `MCPClient` to execute tool
- Returns result to Electron

### **Step 2: Add MCP API Client to Electron**

**File:** `packages/ide_chat_app/src/services/mcpApi.ts`

**Functionality:**
- HTTP client for Extension MCP endpoint
- Convenience methods for common MCP tools
- Error handling and timeouts

### **Step 3: Update Electron Dashboard to Use MCP Tools**

**Files:** Various React components

**Functionality:**
- Use MCP tools for memory operations
- Use MCP tools for agent communication
- Use MCP tools for planning and confidence tracking

---

## 🔧 **TECHNICAL DETAILS**

### **MCP Server Connection:**

**Current:** Extension spawns Python process directly  
**Challenge:** Electron can't spawn Python process (different process)  
**Solution:** Electron calls Extension, Extension spawns process

### **MCP Tools Available:**

**Core (6):**
- `store_memory` - Store in CMC
- `retrieve_memory` - Search HHNI
- `get_memory_stats` - Get statistics
- `create_plan` - APOE planning
- `track_confidence` - VIF tracking
- `synthesize_knowledge` - SEG synthesis

**AI Collaboration (6):**
- `send_ai_message` - Send to other AI
- `get_ai_messages` - Get messages
- `start_ai_discussion` - Start thread
- `handoff_task_to_ai` - Task handoff
- `share_ai_profile` - Share profile
- `get_ai_collaboration_summary` - Get summary

**Total:** 59 tools available

---

## 🚀 **IMPLEMENTATION STEPS**

### **Step 1: Extension MCP Endpoint** ✅
- Add `/mcp/execute` endpoint
- Use existing `MCPClient`
- Handle errors gracefully

### **Step 2: Electron MCP Client** ✅
- Create `mcpApi.ts`
- Connect to Extension API
- Provide convenience methods

### **Step 3: Update Dashboard** ⏳
- Replace direct API calls with MCP tools
- Update agent management to use MCP
- Update chat to use MCP messages

---

## 💙 **WHY THIS WORKS**

**Advantages:**
- ✅ Leverages existing MCP infrastructure
- ✅ No need to spawn Python from Electron
- ✅ Extension handles MCP connection
- ✅ Same tools available in Electron as in Cursor
- ✅ Centralized MCP management

**Limitations:**
- ⚠️ Requires Extension to be running
- ⚠️ Extra HTTP hop (Extension → MCP)
- ⚠️ Slightly more latency

**But:** This is the cleanest architecture!

---

## 🎯 **NEXT STEPS**

1. Implement Extension MCP endpoint
2. Implement Electron MCP client
3. Test MCP tool execution
4. Update dashboard components

**Status:** Ready to implement! 🚀

