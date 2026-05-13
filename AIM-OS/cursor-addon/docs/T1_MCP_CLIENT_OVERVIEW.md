---
id: "mcp_client_T1_overview"
system: "mcp_client"
component: null
level: "T1"
type: "overview"
title: "MCP Client - Overview"
description: "500-word overview of MCP Client JSON-RPC connection system"
audience: "developers, architects, integrators"
confidence_threshold: 0.80
token_cost: 500
word_count: 500
created: "2025-11-03T23:55:00Z"
updated: "2025-11-03T23:55:00Z"
author: "aether"
status: "complete"
tags: ["mcp-client", "json-rpc", "python", "cursor-addon", "t0-t6", "transitional"]
dependencies: ["mcp_client_T0_executive"]
related_docs: ["SYSTEM_INTEGRATION_ARCHITECTURE_T2.md", "system.map.lucid.json5"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# MCP Client - T1 Overview (≈500 words)

**Date:** 2025-11-03  
**Status:** Production Ready ✅  
**Purpose:** JSON-RPC 2.0 client connecting Extension to Python MCP server

---

## 🎯 **PROBLEM STATEMENT**

Cursor's built-in MCP client is limited and doesn't expose all AIM-OS MCP tools. Extension needs independent connection to Python MCP server (`lucid_mcp_server.py`) to access 59 AIM-OS tools (memory, collaboration, timeline, autonomous operation). Must handle process lifecycle, JSON-RPC 2.0 protocol, and error recovery.

---

## 🔧 **SOLUTION OVERVIEW**

MCP Client spawns Python MCP server process and communicates via JSON-RPC 2.0 over stdio. Manages process lifecycle, parses stdout/stderr, handles request/response matching, and provides timeout protection. Used by Command Server to execute MCP tools for external clients.

---

## 🏗️ **ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────┐
│  VS Code Extension                                         │
│  - Command Server                                          │
│  - Extension Code                                          │
└────────────────────┬────────────────────────────────────────┘
                     │ TypeScript API
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  MCP Client (TypeScript)                                   │
│  - Process Manager                                          │
│  - JSON-RPC Parser                                          │
│  - Request Manager                                          │
│  - Event Emitter                                            │
└────────────────────┬────────────────────────────────────────┘
                     │ stdio (stdin/stdout/stderr)
                     ▼
┌─────────────────────────────────────────────────────────────┐
│  Python MCP Server                                         │
│  lucid_mcp_server.py                                       │
│  - 59 MCP Tools                                             │
│  - JSON-RPC 2.0 Handler                                     │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔑 **KEY FEATURES**

### **Process Management**
- Spawns Python process: `python -u lucid_mcp_server.py`
- Reads configuration from VS Code settings (`aimos.mcpServerPath`)
- Monitors process lifecycle (close, error events)
- Automatic cleanup on disconnect

### **JSON-RPC 2.0 Protocol**
- Sends requests: `{ jsonrpc: "2.0", id: number, method: string, params: object }`
- Parses responses: `{ jsonrpc: "2.0", id: number, result: any }`
- Handles errors: `{ jsonrpc: "2.0", id: number, error: object }`
- Supports notifications: `{ jsonrpc: "2.0", method: string, params: object }`

### **Request Management**
- Pending request tracking (Map<id, Promise>)
- 30-second timeout per request
- Automatic cleanup on timeout
- Error propagation to caller

### **Event Emission**
- `disconnected` event when process dies
- `notification` event for server notifications
- Integration with VS Code EventEmitter pattern

---

## 📡 **API METHODS**

### **Core Methods**
- `initialize()` - Start MCP server process and initialize connection
- `sendRequest(method, params?)` - Send JSON-RPC request, return Promise<result>
- `listTools()` - Get list of available MCP tools
- `callTool(name, arguments)` - Execute specific MCP tool
- `disconnect()` - Stop process and cleanup

### **Convenience Methods**
- `storeMemory(content, tags)` - Store memory via MCP
- `retrieveMemory(query, limit)` - Retrieve memory via MCP
- `getMemoryStats()` - Get memory statistics
- `createPlan(goal, priority)` - Create execution plan
- `trackConfidence(task, confidence, reasoning)` - Track confidence
- `synthesizeKnowledge(topics)` - Synthesize knowledge

---

## 🔄 **MESSAGE FLOW**

### **Request Flow:**
```
1. Extension calls: mcpClient.callTool('store_memory', { content, tags })
   ↓
2. MCP Client sends: { jsonrpc: "2.0", id: 1, method: "tools/call", params: {...} }
   ↓
3. Python server processes tool call
   ↓
4. Python server responds: { jsonrpc: "2.0", id: 1, result: {...} }
   ↓
5. MCP Client parses response, resolves Promise
   ↓
6. Extension receives result
```

### **Error Flow:**
```
1. Python server error: { jsonrpc: "2.0", id: 1, error: { code: -32603, message: "..." } }
   ↓
2. MCP Client rejects Promise with Error
   ↓
3. Extension catches error, handles gracefully
```

---

## 🚀 **USAGE EXAMPLE**

```typescript
// Initialize
const mcpClient = new MCPClient();
await mcpClient.initialize();

// Listen for notifications
mcpClient.on('notification', (message) => {
    console.log('MCP notification:', message);
});

// Call tool
try {
    const result = await mcpClient.callTool('store_memory', {
        content: 'Test memory',
        tags: ['test']
    });
    console.log('Stored:', result);
} catch (error) {
    console.error('MCP error:', error);
}

// Cleanup
mcpClient.disconnect();
```

---

## ✅ **PRODUCTION STATUS**

- **Status:** Production Ready ✅
- **Protocol Compliance:** Full JSON-RPC 2.0 support
- **Error Handling:** Graceful timeout and error recovery
- **Process Management:** Automatic cleanup on disconnect
- **Performance:** <500ms latency for most tools

---

**See:** [T0 Executive](./T0_MCP_CLIENT_EXECUTIVE.md) | [T2 Architecture](./T2_MCP_CLIENT_ARCHITECTURE.md) | [System Map](../systems/mcp_client/system.map.lucid.json5)

