---
id: "system_integration_architecture_T2_architecture"
system: "cursor_addon"
component: "integration"
level: "T2"
type: "architecture"
title: "System Integration Architecture - Complete System Diagram"
description: "2,000-word architecture document explaining how Extension UI, MCP Server, Daemon, RAG, and all components integrate together"
audience: "developers, architects, system integrators"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-03T22:40:00Z"
updated: "2025-11-03T23:00:00Z"
author: "aether"
status: "complete"
tags: ["integration", "architecture", "mcp", "daemon", "rag", "extension", "electron", "t0-t6", "transitional"]
dependencies: ["T0_AGENT_AUTOMATION_EXECUTIVE.md", "T0_BULLETPROOF_MESSAGING_EXECUTIVE.md"]
related_docs: ["AUTOMATION_SYSTEMS_EXPLAINED_T2.md", "INTEGRATION_ARCHITECTURE.md"]
version: "v1.0.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs.

# 🔗 System Integration Architecture - Complete System Diagram

**Date:** 2025-11-03  
**Status:** Production Architecture  
**Purpose:** Complete integration map for all AIM-OS systems  
**Tier:** T2 (Architecture Overview)

---

## 🎯 **OVERVIEW**

This document explains how all AIM-OS systems integrate together:

- **Extension UI** (React dashboard in Cursor webview)
- **MCP Server** (Python - 59 tools)
- **Daemon/RAG System** (Intelligent tool selection)
- **Command Server** (HTTP API bridge)
- **Electron App** (Standalone dashboard)
- **AgentMonitor** (Cursor Background Agents)

---

## 🏗️ **COMPLETE SYSTEM ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CURSOR IDE (Host Process)                           │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Cursor Built-in MCP Client                         │  │
│  │  - Reads ~/.cursor/mcp.json                                           │  │
│  │  - Spawns lucid_mcp_server.py automatically                          │  │
│  │  - Communicates via stdio (JSON-RPC 2.0)                             │  │
│  │  - Available to Cursor AI agents directly                            │  │
│  └───────────────────────┬─────────────────────────────────────────────┘  │
│                          │ JSON-RPC 2.0 stdio                              │
│                          ↓                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │              Extension UI (React Dashboard)                         │  │
│  │  - Right sidebar webview (aimosDashboard)                           │  │
│  │  - Uses vscode.postMessage() for communication                      │  │
│  │  - Can call MCP tools via Command Server                            │  │
│  └───────────────────────┬─────────────────────────────────────────────┘  │
│                          │ vscode.postMessage()                             │
│                          ↓                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │              Extension Host (TypeScript)                             │  │
│  │                                                                       │  │
│  │  ┌───────────────────────────────────────────────────────────────┐ │  │
│  │  │         Command Server (HTTP API - Port 5001)                  │ │  │
│  │  │  - POST /mcp/execute       → Execute MCP tool                 │ │  │
│  │  │  - GET  /mcp/list          → List available tools              │ │  │
│  │  │  - POST /cursor/command    → Execute VS Code command            │ │  │
│  │  │  - GET  /cursor/state      → Get Cursor state                  │ │  │
│  │  │  - POST /messaging/send    → Bulletproof messaging             │ │  │
│  │  └───────────────────┬───────────────────────────────────────────┘ │  │
│  │                      │ HTTP (localhost:5001)                        │  │
│  │                      ↓                                              │  │
│  │  ┌───────────────────────────────────────────────────────────────┐ │  │
│  │  │              MCP Client (TypeScript)                          │ │  │
│  │  │  - Spawns Python process (lucid_mcp_server.py)                 │ │  │
│  │  │  - Manages JSON-RPC 2.0 communication                         │ │  │
│  │  │  - Provides methods: storeMemory, retrieveMemory, etc.         │ │  │
│  │  └───────────────────┬───────────────────────────────────────────┘ │  │
│  │                      │ JSON-RPC 2.0 stdio                          │  │
│  │                      ↓                                              │  │
│  │  ┌───────────────────────────────────────────────────────────────┐ │  │
│  │  │           Message Router (Bulletproof Messaging)               │ │  │
│  │  │  - Envelope protocol (v1)                                      │ │  │
│  │  │  - Idempotency + Ordering + DLQ                                │ │  │
│  │  │  - Routes messages to handlers                                 │ │  │
│  │  └───────────────────────────────────────────────────────────────┘ │  │
│  │                                                                       │  │
│  │  ┌───────────────────────────────────────────────────────────────┐ │  │
│  │  │              AgentMonitor (Cursor Agents)                      │ │  │
│  │  │  - startAgent()         → Cloud API (GitHub repos)            │ │  │
│  │  │  - startLocalAgent()    → CLI Agent (local repos)              │ │  │
│  │  │  - startAgentSmart()    → Auto-detects method                 │ │  │
│  │  └───────────────────────────────────────────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                          │
                          │ HTTP (localhost:5001)
                          ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    ELECTRON APP (Standalone Process)                        │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │              Electron Dashboard (React UI)                           │  │
│  │  - Can run independently of Cursor                                  │  │
│  │  - Uses HTTP API to call Extension                                   │  │
│  └───────────────────────┬─────────────────────────────────────────────┘  │
│                          │ fetch('http://localhost:5001/...')              │
│                          ↓                                                  │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │              MCP API Client (mcpApi.ts)                             │  │
│  │  - executeTool(tool, args) → POST /mcp/execute                      │  │
│  │  - listTools()            → GET /mcp/list                           │  │
│  │  - checkExtension()       → GET /health                             │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                          │
                          │ JSON-RPC 2.0 stdio / HTTP
                          ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    PYTHON MCP SERVER (Independent Process)                   │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │              lucid_mcp_server.py                                     │  │
│  │  - 59 MCP tools registered                                           │  │
│  │  - Core AIM-OS tools (store_memory, retrieve_memory, etc.)           │  │
│  │  - AI Collaboration tools (send_ai_message, etc.)                    │  │
│  │  - Timeline & Goal tools                                             │  │
│  │  - Autonomous operation tools                                        │  │
│  │  - Observability tools                                               │  │
│  └───────────────────┬─────────────────────────────────────────────────┘  │
│                      │ Direct Python calls                                 │
│                      ↓                                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │              AIM-OS Backend Systems                                  │  │
│  │  - CMC (Memory Storage)                                              │  │
│  │  - HHNI (Hierarchical Index)                                        │  │
│  │  - VIF (Verification Framework)                                      │  │
│  │  - APOE (Orchestration Engine)                                       │  │
│  │  - SEG (Knowledge Synthesis)                                         │  │
│  │  - SDF-CVF (Quality Framework)                                       │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                          │
                          │ HTTP (localhost:5000) [Optional]
                          ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    DAEMON/RAG SYSTEM (Future Enhancement)                    │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │              DaemonRAGSystem (Python)                                │  │
│  │  - Intelligent tool selection (solves 40-tool limit)                  │  │
│  │  - Context-aware tool loading/unloading                             │  │
│  │  - RAG-enhanced tool recommendations                                │  │
│  │  - Performance optimization                                          │  │
│  │                                                                       │  │
│  │  Status: Not currently active, planned for future                    │  │
│  │  Integration: Would sit between MCP Client and MCP Server             │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                          │
                          │ HTTP API (api.cursor.com/v0)
                          ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                    CURSOR CLOUD AGENTS API (External)                       │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │              Cursor Background Agents                               │  │
│  │  - Runs agents in Cursor's VMs                                      │  │
│  │  - Requires GitHub repository URLs                                  │  │
│  │  - Webhook support for status updates                               │  │
│  │  - Long-running automation                                          │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 **MESSAGE FLOW EXAMPLES**

### **Example 1: Extension UI → MCP Tool → Backend**

```
1. User clicks "Store Memory" in React dashboard
   ↓
2. React UI calls: vscode.postMessage({ command: 'mcpCall', tool: 'store_memory', args: {...} })
   ↓
3. Extension webviewProvider.ts receives message
   ↓
4. Extension calls: fetch('http://localhost:5001/mcp/execute', {...})
   ↓
5. Command Server receives HTTP POST /mcp/execute
   ↓
6. Command Server calls: mcpClient.callTool('store_memory', args)
   ↓
7. MCP Client spawns Python process (if not already running)
   ↓
8. MCP Client sends JSON-RPC 2.0 message to Python process
   ↓
9. Python MCP Server (lucid_mcp_server.py) receives request
   ↓
10. Python calls AIM-OS backend (CMC.store())
   ↓
11. Result flows back: Backend → Python → MCP Client → Command Server → Extension → UI
```

### **Example 2: Electron App → MCP Tool → Backend**

```
1. Electron app calls: mcpApi.executeTool('retrieve_memory', { query: '...' })
   ↓
2. Electron app sends: fetch('http://localhost:5001/mcp/execute', {...})
   ↓
3. Command Server receives HTTP POST /mcp/execute
   ↓
4. Command Server calls: mcpClient.callTool('retrieve_memory', {...})
   ↓
5. Rest of flow same as Example 1 (steps 7-11)
```

### **Example 3: Cursor AI Agent → MCP Tool → Backend**

```
1. Cursor AI agent wants to store memory
   ↓
2. Cursor's built-in MCP Client reads ~/.cursor/mcp.json
   ↓
3. Cursor spawns lucid_mcp_server.py automatically
   ↓
4. Cursor sends JSON-RPC 2.0 message via stdio
   ↓
5. Python MCP Server receives request
   ↓
6. Python calls AIM-OS backend (CMC.store())
   ↓
7. Result flows back: Backend → Python → Cursor MCP Client → Cursor AI Agent
```

### **Example 4: AgentMonitor → Cursor Cloud API → Agent VM**

```
1. Extension calls: agentMonitor.startAgent({ repoPath: 'https://github.com/...', ... })
   ↓
2. AgentMonitor sends: POST https://api.cursor.com/v0/agents
   ↓
3. Cursor Cloud API creates agent run in VM
   ↓
4. AgentMonitor receives: { id: 'bc_abc123', status: 'running', ... }
   ↓
5. AgentMonitor sends event via bulletproof messaging: router.route(envelope('agent.started'))
   ↓
6. Event flows to UI (Extension or Electron app)
   ↓
7. Webhook callback (if configured) receives status updates
   ↓
8. AgentMonitor updates status via: GET /v0/agents/{id}
```

---

## 🔌 **INTEGRATION POINTS**

### **1. Extension UI ↔ Command Server**

**Interface:** HTTP API (localhost:5001)  
**Protocol:** REST (JSON)  
**Purpose:** React webview can call MCP tools and VS Code commands

**Key Endpoints:**
- `POST /mcp/execute` - Execute MCP tool
- `POST /cursor/command` - Execute VS Code command
- `GET /cursor/state` - Get Cursor state

**Implementation:**
- Extension webview uses `fetch()` to call Command Server
- Command Server routes to MCP Client or VS Code API

---

### **2. Command Server ↔ MCP Client**

**Interface:** TypeScript method calls  
**Protocol:** Direct function calls  
**Purpose:** Command Server uses MCP Client to execute tools

**Key Methods:**
- `mcpClient.callTool(name, args)` - Execute any MCP tool
- `mcpClient.storeMemory(content, tags)` - Store in CMC
- `mcpClient.retrieveMemory(query, limit)` - Search HHNI

**Implementation:**
- Command Server creates MCP Client instance
- MCP Client spawns Python process if needed
- Communication via JSON-RPC 2.0 stdio

---

### **3. MCP Client ↔ MCP Server**

**Interface:** JSON-RPC 2.0 over stdio  
**Protocol:** JSON-RPC 2.0  
**Purpose:** Execute MCP tools in Python backend

**Key Messages:**
- `initialize` - Handshake
- `tools/list` - List available tools
- `tools/call` - Execute tool

**Implementation:**
- MCP Client spawns Python process (`lucid_mcp_server.py`)
- Messages sent via `process.stdin.write()`
- Responses received via `process.stdout.on('data')`

---

### **4. MCP Server ↔ AIM-OS Backend**

**Interface:** Direct Python imports/calls  
**Protocol:** Python function calls  
**Purpose:** MCP tools execute AIM-OS operations

**Key Systems:**
- CMC (Memory Storage)
- HHNI (Hierarchical Index)
- VIF (Verification Framework)
- APOE (Orchestration Engine)
- SEG (Knowledge Synthesis)
- SDF-CVF (Quality Framework)

**Implementation:**
- MCP Server imports AIM-OS packages
- Tools call backend functions directly
- Results returned as JSON-RPC responses

---

### **5. Electron App ↔ Command Server**

**Interface:** HTTP API (localhost:5001)  
**Protocol:** REST (JSON)  
**Purpose:** Electron app can use MCP tools without Cursor

**Key Services:**
- `mcpApi.ts` - MCP API client
- `cursorApi.ts` - VS Code command client
- `serviceBridge.ts` - Smart routing (MCP → HTTP → Cache)

**Implementation:**
- Electron app uses `fetch()` to call Command Server
- Command Server routes to MCP Client or VS Code API
- Results returned as HTTP responses

---

### **6. AgentMonitor ↔ Cursor Cloud API**

**Interface:** HTTP API (api.cursor.com/v0)  
**Protocol:** REST (JSON) with Bearer Token  
**Purpose:** Automate Cursor Background Agents

**Key Endpoints:**
- `POST /v0/agents` - Start agent (Cloud API)
- `GET /v0/agents/{id}` - Get agent status
- `DELETE /v0/agents/{id}` - Stop agent
- `POST /v0/agents/{id}/followup` - Add follow-up

**Implementation:**
- AgentMonitor sends HTTP requests to Cursor API
- Requires API key (Bearer token authentication)
- Returns agent run IDs and status updates

---

### **7. Daemon/RAG System ↔ MCP Server** [Future]

**Interface:** HTTP API (localhost:5000) or MCP Protocol  
**Protocol:** HTTP REST or JSON-RPC 2.0  
**Purpose:** Intelligent tool selection and server management

**Key Features:**
- Context-aware tool loading/unloading
- RAG-enhanced tool recommendations
- Performance optimization (stay under 40-tool limit)

**Status:** Not currently active, planned for future enhancement

---

## 🎯 **KEY DESIGN DECISIONS**

### **Why Command Server?**

**Problem:** Electron app can't access VS Code API directly  
**Solution:** Command Server provides HTTP bridge  
**Benefit:** Electron app can use MCP tools without Cursor

### **Why Two MCP Connections?**

**Problem:** Cursor has its own MCP connection, Extension needs separate one  
**Solution:** Extension spawns its own Python process  
**Benefit:** Extension can use MCP tools independently of Cursor

### **Why Bulletproof Messaging?**

**Problem:** `vscode.postMessage()` is unreliable (no ACK, no ordering)  
**Solution:** Envelope protocol with ACK/NACK, ordering, idempotency  
**Benefit:** Guaranteed delivery, exactly-once processing, ordering

### **Why AgentMonitor?**

**Problem:** Need to automate long-running Cursor agents  
**Solution:** Use Cursor Cloud Agents API + CLI Agent  
**Benefit:** Cloud execution (VMs) or local execution (CLI)

---

## 📊 **SYSTEM STATUS**

| Component | Status | Integration Method |
|-----------|--------|-------------------|
| Extension UI | ✅ Active | HTTP API (Command Server) |
| Command Server | ✅ Active | HTTP (localhost:5001) |
| MCP Client | ✅ Active | JSON-RPC 2.0 stdio |
| MCP Server | ✅ Active | JSON-RPC 2.0 stdio |
| Electron App | ✅ Active | HTTP API (Command Server) |
| AgentMonitor | ✅ Active | HTTP API (Cursor Cloud) |
| Daemon/RAG | ⚠️ Planned | HTTP API (future) |
| Bulletproof Messaging | ✅ Active | Envelope protocol |

---

## 🔗 **RELATED DOCUMENTATION**

- **T0 Executive:** `AUTOMATION_SIMPLE_EXPLANATION_T0.md`
- **T1 Overview:** `AUTOMATION_SYSTEMS_EXPLAINED_T1.md`
- **T2 Detailed:** `AUTOMATION_SYSTEMS_EXPLAINED_T2.md`
- **Integration Guide:** `INTEGRATION_ARCHITECTURE.md`
- **MCP Integration:** `MCP_INTEGRATION_PLAN.md`
- **Cursor API Research:** `CURSOR_API_RESEARCH.md`

---

**Last Updated:** 2025-11-03  
**Status:** Production Architecture ✅  
**Next:** Test all integration points end-to-end

