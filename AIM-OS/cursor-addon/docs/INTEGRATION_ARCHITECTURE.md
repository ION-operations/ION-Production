# Bulletproof Messaging Protocol - System Integration Architecture

**Date:** 2025-11-03  
**Status:** Integration Design Complete  
**Purpose:** Document how bulletproof messaging integrates with all AIM-OS systems

---

## 🎯 **INTEGRATION OVERVIEW**

The bulletproof messaging protocol serves as the **reliable communication backbone** for all AIM-OS systems, ensuring guaranteed delivery, ordering, and exactly-once processing across all components.

---

## 🔗 **INTEGRATION POINTS**

### **1. VS Code Extension ↔ Webview UI**

**Current:** `vscode.postMessage()` (unreliable)  
**With Bulletproof Messaging:** Envelope protocol via router

**Flow:**
```
React UI (Webview)
    ↓ Envelope Protocol (v1)
Message Router (Extension)
    ↓ Routes to handlers
Extension Handlers (MCP, Commands, etc.)
    ↓ Response Envelope
Message Router
    ↓ ACK + Response
React UI (Webview)
```

**Integration:**
- UI sends envelopes via `vscode.postMessage()`
- Extension router receives and routes
- Handlers process with idempotency + ordering
- Responses sent back via router

**Files:**
- `cursor-addon/src/messaging/router.ts` - Main router
- `cursor-addon/src/webviewProvider.ts` - Webview integration

---

### **2. Extension ↔ MCP Server (Python)**

**Current:** JSON-RPC 2.0 stdio (via MCPClient)  
**With Bulletproof Messaging:** Envelope protocol wrapper

**Flow:**
```
Extension Router
    ↓ Envelope (mcp.callTool)
MCP Envelope Handler
    ↓ Extract tool + args
MCPClient (JSON-RPC)
    ↓ JSON-RPC 2.0
Python MCP Server
    ↓ Response
MCPClient
    ↓ Response Envelope
Extension Router
    ↓ ACK + Response
Caller (UI/Electron)
```

**Integration:**
- MCP tool calls wrapped in envelopes
- Router ensures idempotency
- Dead letter queue for failed MCP calls
- Ordering for sequential MCP operations

**Files:**
- `cursor-addon/src/messaging/router.ts` - Router handles MCP calls
- `cursor-addon/src/mcp/mcpClient.ts` - MCP client unchanged

---

### **3. Extension ↔ Electron App**

**Current:** HTTP API (Command Server on port 5001)  
**With Bulletproof Messaging:** Envelope protocol over HTTP

**Flow:**
```
Electron App
    ↓ HTTP POST (envelope)
Command Server (/messaging/send)
    ↓ Parse envelope
Message Router
    ↓ Route to handler
Extension Handler
    ↓ Process
Message Router
    ↓ Response Envelope
Command Server
    ↓ HTTP Response (envelope)
Electron App
```

**Integration:**
- Electron sends envelopes via HTTP
- Command Server routes to message router
- Router ensures reliability
- Responses sent back as envelopes

**Files:**
- `cursor-addon/src/commandServer.ts` - HTTP endpoint `/messaging/send`
- `cursor-addon/src/messaging/router.ts` - Router processes envelopes

---

### **4. Extension ↔ RAG MCP/Daemon**

**Current:** MCP tools via MCPClient  
**With Bulletproof Messaging:** Envelope protocol with MCP wrapper

**Flow:**
```
Extension Router
    ↓ Envelope (rag.query)
RAG Handler
    ↓ Extract query
MCPClient.callTool('rag_query')
    ↓ JSON-RPC
RAG MCP Server
    ↓ Results
MCPClient
    ↓ Response Envelope
Extension Router
    ↓ ACK + Response
Caller
```

**Integration:**
- RAG queries wrapped in envelopes
- Idempotency prevents duplicate queries
- Dead letter queue for failed queries
- Ordering for sequential queries

**Files:**
- `cursor-addon/src/messaging/router.ts` - Router handles RAG calls
- `cursor-addon/src/mcp/mcpClient.ts` - MCP client unchanged

---

### **5. Extension ↔ Cursor 2.0 Project/User Commands**

**Current:** `vscode.commands.executeCommand()`  
**With Bulletproof Messaging:** Envelope protocol wrapper

**Flow:**
```
Extension Router
    ↓ Envelope (cursor.command)
Cursor Command Handler
    ↓ Extract command + args
vscode.commands.executeCommand()
    ↓ VS Code API
Cursor IDE
    ↓ Command result
Cursor Command Handler
    ↓ Response Envelope
Extension Router
    ↓ ACK + Response
Caller
```

**Integration:**
- Cursor commands wrapped in envelopes
- Idempotency prevents duplicate execution
- Dead letter queue for failed commands
- Ordering for sequential commands

**Files:**
- `cursor-addon/src/messaging/router.ts` - Router handles Cursor commands
- `cursor-addon/src/commandServer.ts` - Command execution endpoint

---

### **6. MCP Tools ↔ Extension**

**Current:** Direct MCP tool calls  
**With Bulletproof Messaging:** Envelope protocol integration

**Flow:**
```
MCP Tool Caller
    ↓ Envelope (mcp.callTool)
Extension Router
    ↓ Check idempotency
MCP Tool Handler
    ↓ Extract tool name + args
MCPClient.callTool()
    ↓ JSON-RPC
MCP Server
    ↓ Result
MCP Tool Handler
    ↓ Response Envelope
Extension Router
    ↓ ACK + Response
Caller
```

**Integration:**
- All MCP tool calls go through router
- Idempotency prevents duplicate tool calls
- Dead letter queue for failed tools
- Ordering for sequential tool calls

**Files:**
- `cursor-addon/src/messaging/router.ts` - Router handles MCP tools
- `cursor-addon/src/mcp/mcpClient.ts` - MCP client unchanged

---

## 📡 **MESSAGE FLOW ARCHITECTURE**

### **Complete Flow Example: UI → MCP Tool → Response**

```
1. React UI creates envelope:
   {
     v: 1,
     id: "msg-123",
     seq: 1,
     kind: "request",
     topic: "mcp.callTool",
     dir: "ui->ext",
     payload: { toolName: "store_memory", params: {...} }
   }

2. UI sends via vscode.postMessage(envelope)

3. Extension Router receives:
   - Checks idempotency (has msg-123 been processed?)
   - Sends immediate ACK
   - Adds to ordered queue

4. Router processes (in order):
   - Dequeues from ordered queue
   - Routes to "mcp.callTool" handler
   - Handler calls MCPClient.callTool()
   - Waits for response

5. Handler creates response envelope:
   {
     v: 1,
     id: "resp-456",
     replyTo: "msg-123",
     kind: "response",
     topic: "mcp.callTool",
     dir: "ext->ui",
     ok: true,
     payload: { result: {...} }
   }

6. Router sends response via webview.postMessage()

7. UI receives response:
   - Matches via replyTo field
   - Processes result
   - Updates UI
```

---

## 🔄 **INTEGRATION WITH EXISTING SYSTEMS**

### **A. MCP Message Sending (Already Working)**

**Current Implementation:**
- ✅ Messages sent via HTTP endpoint `/mcp/execute`
- ✅ Uses `send_ai_message` tool
- ✅ Works for Electron app and UI panels

**Integration with Bulletproof Messaging:**
- Wrap MCP message calls in envelopes
- Use router for reliability
- Ensure idempotency for message sending
- Dead letter queue for failed messages

**Files:**
- `knowledge_architecture/AETHER_MEMORY/MCP_MESSAGE_SENDING_SOLUTION.md`
- `cursor-addon/src/commandServer.ts` - `/mcp/execute` endpoint

---

### **B. Command Server (HTTP API)**

**Current Implementation:**
- ✅ HTTP server on port 5001
- ✅ Endpoints for MCP tools, Cursor commands
- ✅ Used by Electron app

**Integration with Bulletproof Messaging:**
- Add `/messaging/send` endpoint
- Accept envelopes via HTTP
- Route to message router
- Return response envelopes

**Files:**
- `cursor-addon/src/commandServer.ts` - HTTP server
- `cursor-addon/src/messaging/router.ts` - Router

---

### **C. RAG MCP/Daemon**

**Current Implementation:**
- ✅ RAG queries via MCP tools
- ✅ Indexed storage
- ✅ Retrieval capabilities

**Integration with Bulletproof Messaging:**
- Wrap RAG queries in envelopes
- Ensure idempotency (don't query twice)
- Order queries if needed
- Dead letter queue for failed queries

**Files:**
- `cursor-addon/src/messaging/router.ts` - Router handles RAG
- MCP tools: `rag_query`, `rag_index`, etc.

---

### **D. Cursor 2.0 Project/User Commands**

**Research Needed:**
- Cursor 2.0 introduces project-level and user-level commands
- Need to investigate API availability
- May require VS Code API extensions

**Integration Plan:**
- If available: Wrap in envelopes
- Route via message router
- Ensure idempotency
- Dead letter queue for failures

**Status:** ⚠️ **RESEARCH NEEDED**

---

## 🔌 **IMPLEMENTATION PLAN**

### **Phase 1: Core Integration (Extension ↔ Webview)**

**Tasks:**
1. ✅ Router implemented
2. ✅ Webview provider integrated
3. ⚠️ Update React UI to use envelopes
4. ⚠️ Test end-to-end flow

**Files:**
- `cursor-addon/src/messaging/router.ts` ✅
- `cursor-addon/src/webviewProvider.ts` ✅
- `packages/ide_chat_app/src/services/` ⚠️ (needs update)

---

### **Phase 2: MCP Integration**

**Tasks:**
1. ✅ Router handles MCP calls
2. ⚠️ Update MCP handlers to use envelopes
3. ⚠️ Test MCP tool reliability

**Files:**
- `cursor-addon/src/messaging/router.ts` ✅
- `cursor-addon/src/mcp/mcpClient.ts` (unchanged)

---

### **Phase 3: Command Server Integration**

**Tasks:**
1. ⚠️ Add `/messaging/send` endpoint
2. ⚠️ Integrate with router
3. ⚠️ Test HTTP envelope flow

**Files:**
- `cursor-addon/src/commandServer.ts` ⚠️ (needs update)
- `cursor-addon/src/messaging/router.ts` ✅

---

### **Phase 4: Cursor 2.0 Commands**

**Tasks:**
1. ⚠️ Research Cursor 2.0 API
2. ⚠️ Create command handlers
3. ⚠️ Integrate with router

**Files:**
- `cursor-addon/src/messaging/router.ts` ✅
- New handlers for Cursor 2.0 ⚠️

---

## 📋 **INTEGRATION CHECKLIST**

### **Extension ↔ Webview**
- [x] Router implemented
- [x] Webview provider integrated
- [ ] React UI updated to send envelopes
- [ ] React UI updated to receive envelopes
- [ ] End-to-end tests

### **Extension ↔ MCP Server**
- [x] Router handles MCP calls
- [ ] MCP handlers use envelopes
- [ ] Idempotency for MCP calls
- [ ] Dead letter queue for MCP failures

### **Extension ↔ Electron App**
- [x] Command Server exists
- [ ] `/messaging/send` endpoint added
- [ ] Router integration
- [ ] HTTP envelope tests

### **Extension ↔ RAG MCP/Daemon**
- [ ] RAG query handlers
- [ ] Envelope wrapping
- [ ] Idempotency
- [ ] Dead letter queue

### **Extension ↔ Cursor 2.0 Commands**
- [ ] Research Cursor 2.0 API
- [ ] Create handlers
- [ ] Envelope wrapping
- [ ] Integration tests

---

## 🎯 **NEXT STEPS**

1. **Implement ChatGPT Improvements** (resequencer, KV contract, idle helper)
2. **Add `/messaging/send` endpoint** to Command Server
3. **Update React UI** to use envelope protocol
4. **Research Cursor 2.0** project/user commands API
5. **Integration tests** for all flows

---

*Created: 2025-11-03*  
*Status: Integration Architecture Complete*  
*Next: Implement improvements and integrations*

