# DAC IDE Architecture Analysis

**Date:** 2025-01-27  
**Question:** Where do AIM-OS systems run? Does the IDE depend on Cursor?

---

## 🔍 **CURRENT ARCHITECTURE**

### **What We Have Now:**

```
┌─────────────────────────────────────────────────────────────┐
│                    DAC IDE (Frontend)                       │
│  - React/TypeScript UI                                       │
│  - Vite dev server (port 3002/3003)                         │
│  - Calls: http://localhost:8000/api/system-indexes         │
│  - Calls: http://localhost:5001/mcp/execute (MCP tools)    │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌───────────────────┐      ┌──────────────────────────────┐
│  DAC Backend      │      │  Cursor Extension            │
│  (backend_server) │      │  Command Server              │
│  Port: 8000       │      │  Port: 5001                  │
│                   │      │                              │
│  - System Indexes │      │  - HTTP Server               │
│  - System Maps    │      │  - /mcp/execute endpoint     │
│  - JSON5 parsing  │      │  - Uses MCPClient            │
└───────────────────┘      └──────────┬───────────────────┘
                                      │
                                      ▼
                            ┌──────────────────────────────┐
                            │  MCPClient                   │
                            │  (cursor-addon)              │
                            │  - Spawns Python process     │
                            │  - JSON-RPC 2.0 (stdio)      │
                            └──────────┬───────────────────┘
                                      │
                                      ▼
                            ┌──────────────────────────────┐
                            │  MCP Server                  │
                            │  (lucid_mcp_server.py)        │
                            │  - 59 MCP tools              │
                            │  - Python process            │
                            └──────────┬───────────────────┘
                                      │
                                      ▼
                            ┌──────────────────────────────┐
                            │  AIM-OS Core Systems         │
                            │  - CMC (packages/cmc_service)│
                            │  - HHNI (packages/hhni)      │
                            │  - VIF (packages/vif)        │
                            │  - SEG, APOE, CAS, TCS       │
                            │  - Python packages           │
                            └──────────────────────────────┘
```

---

## ⚠️ **THE PROBLEM**

### **Current Dependencies:**

1. **IDE → Cursor Extension (port 5001)**
   - IDE calls `http://localhost:5001/mcp/execute` for MCP tools
   - **Problem:** Command Server only runs when Cursor is open
   - **Problem:** IDE can't work standalone

2. **IDE → DAC Backend (port 8000)**
   - IDE calls `http://localhost:8000/api/system-indexes` for system data
   - **Status:** ✅ Standalone (we created this)
   - **Works:** Even without Cursor

3. **MCP Tools → AIM-OS Systems**
   - MCP server (`lucid_mcp_server.py`) imports Python packages
   - Packages: `packages/cmc_service`, `packages/hhni`, etc.
   - **Status:** ✅ These are just Python packages (not separate services)
   - **Location:** In the workspace, not a "command center"

---

## 🎯 **WHERE AIM-OS SYSTEMS ACTUALLY RUN**

### **Answer: They're Python Packages, Not Separate Services**

**AIM-OS systems are:**
- **Python packages** in `packages/` directory
- **Imported directly** by `lucid_mcp_server.py`
- **Not separate services** (unless you use Docker Compose)
- **Run in-process** when MCP server starts

**Example:**
```python
# lucid_mcp_server.py
from packages.cmc_service import MemoryStore  # Direct import
from packages.hhni import HierarchicalIndex   # Direct import
```

**They're NOT:**
- ❌ Running in a separate "command center"
- ❌ Separate HTTP services (by default)
- ❌ Requiring Cursor to run

---

## 💡 **THE SOLUTION: Standalone Command Server**

### **What We Need:**

A **standalone command server** that:
1. ✅ Runs independently (not part of Cursor extension)
2. ✅ Spawns MCP server (`lucid_mcp_server.py`)
3. ✅ Exposes HTTP API on port 5001 (or configurable)
4. ✅ Can be started with IDE launch scripts
5. ✅ Works without Cursor

### **Proposed Architecture:**

```
┌─────────────────────────────────────────────────────────────┐
│                    DAC IDE (Frontend)                       │
│  - React/TypeScript UI                                       │
│  - Vite dev server (port 3002/3003)                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                             │
        ▼                             ▼
┌───────────────────┐      ┌──────────────────────────────┐
│  DAC Backend      │      │  Standalone Command Server   │
│  (backend_server) │      │  (NEW - standalone)          │
│  Port: 8000       │      │  Port: 5001                  │
│                   │      │                              │
│  - System Indexes │      │  - HTTP Server               │
│  - System Maps    │      │  - /mcp/execute endpoint     │
│  - JSON5 parsing  │      │  - Spawns MCP server         │
└───────────────────┘      └──────────┬───────────────────┘
                                      │
                                      ▼
                            ┌──────────────────────────────┐
                            │  MCP Server                  │
                            │  (lucid_mcp_server.py)        │
                            │  - 59 MCP tools              │
                            │  - Python process            │
                            └──────────┬───────────────────┘
                                      │
                                      ▼
                            ┌──────────────────────────────┐
                            │  AIM-OS Core Systems         │
                            │  (Python packages)           │
                            │  - CMC, HHNI, VIF, etc.      │
                            └──────────────────────────────┘
```

---

## 🚀 **IMPLEMENTATION PLAN**

### **Option 1: Standalone Node.js Command Server (Recommended)**

**Create:** `ide_orchestration/prototypes/dac/standalone_command_server.ts`

**Features:**
- HTTP server on port 5001
- Spawns `lucid_mcp_server.py` as child process
- Exposes `/mcp/execute` endpoint
- Same API as Cursor extension's Command Server
- Can be started with `launch.ps1`/`launch.sh`

**Benefits:**
- ✅ IDE works standalone
- ✅ No Cursor dependency
- ✅ Same API (easy migration)
- ✅ Can run in background

### **Option 2: Extend DAC Backend (Simpler)**

**Modify:** `ide_orchestration/prototypes/dac/backend_server.py`

**Add:**
- `/mcp/execute` endpoint
- Spawn `lucid_mcp_server.py` process
- Handle JSON-RPC 2.0 communication

**Benefits:**
- ✅ Single backend server
- ✅ Simpler architecture
- ✅ Already running on port 8000

**Trade-offs:**
- ⚠️ Mixes concerns (system indexes + MCP tools)
- ⚠️ Python instead of TypeScript (but that's fine)

---

## 📋 **CURRENT STATE SUMMARY**

### **What Works:**
- ✅ DAC Backend (port 8000) - Standalone, serves system indexes/maps
- ✅ IDE Frontend - Can load system data independently
- ✅ MCP Server (`lucid_mcp_server.py`) - Works when spawned
- ✅ AIM-OS Systems - Python packages, work when imported

### **What's Missing:**
- ❌ Standalone Command Server - IDE depends on Cursor extension
- ❌ MCP tools unavailable when Cursor is closed

### **What We Need:**
- ✅ Standalone command server (Option 1 or 2)
- ✅ Update launch scripts to start it
- ✅ Update IDE services to use it (or keep Cursor as fallback)

---

## 🎯 **RECOMMENDATION**

**Implement Option 1: Standalone Node.js Command Server**

**Why:**
1. **Separation of concerns** - Command server separate from backend
2. **TypeScript** - Matches IDE frontend language
3. **Same API** - Easy migration from Cursor extension
4. **Flexibility** - Can run independently or with Cursor

**Implementation:**
1. Create `standalone_command_server.ts`
2. Copy MCPClient logic from `cursor-addon/src/mcp/mcpClient.ts`
3. Add HTTP server with `/mcp/execute` endpoint
4. Update `launch.ps1`/`launch.sh` to start it
5. Update IDE services to prefer standalone, fallback to Cursor

---

**Status:** Analysis Complete  
**Next Step:** Implement standalone command server  
**Priority:** High (enables standalone IDE operation)

