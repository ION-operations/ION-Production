# MCP Chat Interface Error Report
**Date:** 2025-01-27  
**Issue:** `get_ai_messages` MCP tool failure, unable to send messages

---

## 🔴 **CRITICAL ISSUES**

### **Issue 1: MCP Tool `get_ai_messages` Failing**
**Error Location:** Cursor Extension → Command Server → MCP Client → MCP Server  
**Symptom:** Tool execution fails when called from Electron app  
**Impact:** Chat interface cannot retrieve messages, appears non-functional

### **Issue 2: Unable to Send Messages**
**Error Location:** Electron App → ServiceBridge → MCPAPI → Command Server  
**Symptom:** Messages cannot be sent  
**Impact:** Complete chat functionality broken

---

## 🔍 **ROOT CAUSE ANALYSIS**

### **1. Tool Name Mismatch**
**Problem:** Tool name format inconsistency
- **MCP Server registers:** `get_ai_messages` (simple name)
- **Extension expects:** `get_ai_messages` (should match)
- **Issue:** Tool might not be found if name doesn't match exactly

**Current Flow:**
```
Electron App → MCPAPI.getAIMessages()
  → executeTool('get_ai_messages', args)
  → POST /mcp/execute {tool: 'get_ai_messages', arguments: {...}}
  → CommandServer.executeMCPTool()
  → MCPClient.callTool('get_ai_messages', args)
  → MCP Server tools/call {name: 'get_ai_messages', arguments: {...}}
```

### **2. MCP Server Not Running**
**Problem:** MCP server process may not be initialized
- **Extension:** Spawns Python MCP server via `MCPClient.initialize()`
- **Command Server:** Creates new `MCPClient` instance but may fail to initialize
- **Error:** Server process dies or fails to start

**Code Location:** `cursor-addon/src/mcp/mcpClient.ts:23-75`

### **3. Response Format Mismatch**
**Problem:** Response parsing expects nested format but gets flat format
- **MCP Server returns:** `{success: true, messages: [...], count: N}`
- **Command Server wraps:** `{success: true, tool: 'get_ai_messages', result: {...}}`
- **MCPAPI expects:** `response.result.messages` or `response.result.result.messages`

**Code Location:** `packages/ide_chat_app/src/services/mcpApi.ts:207-235`

### **4. Error Handling**
**Problem:** Errors are swallowed, no clear error messages to user
- **MCP Client:** Catches errors but doesn't provide detailed info
- **Command Server:** Returns generic error messages
- **Electron App:** No error display in UI

---

## 📋 **VERIFICATION CHECKLIST**

### **Check 1: MCP Server Running**
- [ ] Is Python MCP server process running?
- [ ] Check extension logs for MCP initialization errors
- [ ] Verify `lucid_mcp_server.py` exists and is executable

### **Check 2: Tool Registration**
- [ ] Verify `get_ai_messages` is in tools list
- [ ] Check tool name matches exactly: `get_ai_messages`
- [ ] Verify tool is callable via MCP protocol

### **Check 3: Command Server**
- [ ] Is Command Server running on port 5001?
- [ ] Can Electron app reach `/health` endpoint?
- [ ] Are MCP tool calls reaching Command Server?

### **Check 4: Response Format**
- [ ] What format does MCP server actually return?
- [ ] What format does Command Server wrap it in?
- [ ] Does MCPAPI parse it correctly?

---

## 🛠️ **DIAGNOSTIC STEPS**

### **Step 1: Check MCP Server Logs**
```bash
# Check if MCP server process is running
# Look for Python processes related to MCP
```

### **Step 2: Test MCP Tool Directly**
```bash
# Try calling tool via MCP client directly
# Check if tool exists in tools list
```

### **Step 3: Check Extension Logs**
```bash
# Check Cursor Extension output panel
# Look for MCP initialization errors
# Check Command Server logs
```

### **Step 4: Test Command Server**
```bash
# Test /health endpoint
curl http://localhost:5001/health

# Test MCP tool execution
curl -X POST http://localhost:5001/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "get_ai_messages", "arguments": {}}'
```

---

## 🔧 **FIXES REQUIRED**

### **Fix 1: Add Error Logging**
**File:** `cursor-addon/src/commandServer.ts`
- Add detailed error logging for MCP tool failures
- Log full error stack traces
- Log tool name and arguments

### **Fix 2: Verify Tool Name**
**File:** `packages/ide_chat_app/src/services/mcpApi.ts`
- Verify tool name matches MCP server exactly
- Add tool name validation
- Handle tool not found errors

### **Fix 3: Improve Response Parsing**
**File:** `packages/ide_chat_app/src/services/mcpApi.ts`
- Handle all possible response formats
- Add fallback parsing logic
- Log unexpected formats for debugging

### **Fix 4: Add User Error Display**
**File:** `packages/ide_chat_app/src/components/AgentManagementDashboard/ChatInterfaceTab.tsx`
- Display MCP errors in UI
- Show connection status
- Provide troubleshooting hints

### **Fix 5: MCP Server Health Check**
**File:** `cursor-addon/src/mcp/mcpClient.ts`
- Add server health check before tool calls
- Reinitialize if server dies
- Better error messages

---

## 📊 **EXPECTED BEHAVIOR**

### **Successful Flow:**
1. Electron app calls `MCPAPI.getAIMessages()`
2. HTTP POST to `http://localhost:5001/mcp/execute`
3. Command Server receives request
4. MCP Client initialized (if needed)
5. MCP tool `get_ai_messages` called
6. MCP Server returns `{success: true, messages: [...], count: N}`
7. Command Server wraps: `{success: true, tool: 'get_ai_messages', result: {...}}`
8. MCPAPI parses: `response.result.messages`
9. Chat interface displays messages

### **Current Failure Point:**
- Likely failing at step 4 (MCP Client initialization)
- Or step 5 (MCP tool call)
- Or step 8 (response parsing)

---

## 🚨 **IMMEDIATE ACTIONS**

1. **Add comprehensive error logging** to identify exact failure point
2. **Test MCP server directly** to verify it's working
3. **Check MCP Client initialization** in extension
4. **Verify tool name** matches exactly
5. **Add error display** in Electron UI

---

## 📝 **NEXT STEPS**

1. Review this report
2. Add diagnostic logging
3. Test each component individually
4. Fix identified issues
5. Retest full flow

---

**Status:** Investigation in progress  
**Priority:** CRITICAL  
**Blocking:** Chat interface completely non-functional

