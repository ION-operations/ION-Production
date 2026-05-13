# AIM-OS Systems Architecture Analysis

**Date:** 2025-01-27  
**Question:** Where are AIM-OS systems running? Do we need standalone Command Server?  
**Status:** Analysis Complete

---

## 🔍 **KEY FINDING**

**AIM-OS systems are embedded in `lucid_mcp_server.py`, not running as separate services!**

---

## 📊 **Current Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│              IDE Prototype (DAC)                            │
│  - React UI Components                                       │
│  - MCPService.ts                                             │
│  - Calls: POST http://localhost:5001/mcp/execute            │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP POST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│         Cursor Extension (cursor-addon)                      │
│                                                               │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  Command Server (commandServer.ts)                   │  │
│  │  - HTTP Server on port 5001                           │  │
│  │  - Endpoint: /mcp/execute                              │  │
│  │  - Uses MCPClient to call MCP tools                   │  │
│  └──────────────────────┬──────────────────────────────────┘  │
│                         │                                      │
│  ┌──────────────────────▼──────────────────────────────────┐  │
│  │  MCPClient (mcp/mcpClient.ts)                          │  │
│  │  - Spawns Python process (lucid_mcp_server.py)          │  │
│  │  - Communicates via stdio (JSON-RPC 2.0)                │  │
│  └──────────────────────┬──────────────────────────────────┘  │
└──────────────────────────┼─────────────────────────────────────┘
                            │ JSON-RPC 2.0 (stdio)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         MCP Server (lucid_mcp_server.py)                   │
│  - Python process spawned by MCPClient                       │
│  - EMBEDDED AIM-OS SYSTEMS:                                  │
│    • CMC (MemoryStore)                                       │
│    • HHNI (HierarchicalIndex, TwoStageRetriever)            │
│    • VIF (VIF, KappaGate, ECETracker)                       │
│    • APOE (ACLParser, PlanExecutor)                         │
│    • SEG (SEGraph)                                          │
│    • CAS (IntrospectionProtocol, etc.)                      │
│    • TCS (PromptContextTracker)                            │
│    • SnapshotSystem                                         │
│  - All systems initialized in __init__()                    │
│  - All systems run in same Python process                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 **Code Evidence**

### **MCP Server Initialization (lucid_mcp_server.py)**

```python
# Lines 103-235: All AIM-OS systems imported and initialized

# CMC
from cmc_service import MemoryStore
self.memory = MemoryStore(self.memory_directory)

# HHNI
from hhni import HierarchicalIndex, IndexLevel
from hhni.retrieval import TwoStageRetriever
self.hhni_index = HierarchicalIndex()
self.hhni_retriever = TwoStageRetriever(...)

# VIF
from vif import VIF, KappaGate, ECETracker
self.vif_kappa_gate = KappaGate()
self.vif_ece_tracker = ECETracker()

# APOE
from apoe.acl_parser import ACLParser
self.apoe_parser = ACLParser()

# SEG
from seg import SEGraph
self.seg_graph = SEGraph()

# CAS
from packages.cas import IntrospectionProtocol
self.cas_introspection = IntrospectionProtocol(...)

# TCS
from packages.timeline_context_system import PromptContextTracker
self.timeline_tracker = PromptContextTracker()
```

**Key Finding:** All AIM-OS systems are **embedded in the MCP server process**, not running as separate services!

---

## ⚠️ **Current Dependencies**

### **Problem: Everything Depends on Cursor**

1. **Command Server** - Part of Cursor extension
   - Only runs when Cursor is running
   - Stops when Cursor closes

2. **MCPClient** - Part of Cursor extension
   - Spawns MCP server process
   - Manages MCP connection

3. **MCP Server** - Spawned by Cursor extension
   - Contains all AIM-OS systems
   - Only runs when Cursor spawns it

4. **AIM-OS Systems** - Embedded in MCP server
   - CMC, HHNI, VIF, APOE, SEG, CAS, TCS
   - All run in same Python process
   - No standalone services

---

## 🎯 **Architectural Questions**

### **1. Do We Need Standalone Command Server?**

**Current:** Command Server is part of Cursor extension

**Problem:**
- IDE prototype can't work without Cursor
- Command Server stops when Cursor closes
- No way to run AIM-OS independently

**Solution Options:**
- **Option A:** Standalone Command Server (Node.js/Python)
  - Runs independently of Cursor
  - IDE prototype can connect directly
  - Cursor extension can also connect
  - More flexible architecture

- **Option B:** Keep current architecture
  - Simpler (everything in Cursor)
  - But IDE prototype requires Cursor

### **2. Where Should AIM-OS Systems Run?**

**Current:** Embedded in MCP server process

**Options:**
- **Option A:** Keep embedded (current)
  - Simpler deployment
  - Single process
  - But tied to MCP server lifecycle

- **Option B:** Separate services/daemons
  - CMC service (port 8081)
  - HHNI service (port 8082)
  - VIF service (port 8083)
  - More complex but more flexible
  - Can scale independently

- **Option C:** Hybrid
  - Core systems embedded
  - Heavy services separate
  - Best of both worlds

### **3. What About "Command Center"?**

**Question:** Do we need a central "command center" server?

**Current:** No central server - everything flows through Command Server

**Options:**
- **Option A:** Command Server as "Command Center"
  - Single entry point
  - Routes to MCP tools
  - Manages connections

- **Option B:** Separate Command Center
  - Orchestrates all services
  - Manages AIM-OS systems
  - Provides unified API

---

## 💡 **Recommendations**

### **For IDE Prototype Independence:**

1. **Create Standalone Command Server**
   - Node.js or Python HTTP server
   - Runs independently of Cursor
   - Connects to MCP server directly
   - IDE prototype connects to it

2. **Keep AIM-OS Systems Embedded (For Now)**
   - Simpler deployment
   - Single process
   - Can refactor later if needed

3. **Architecture:**
```
IDE Prototype
  ↓ HTTP
Standalone Command Server (port 5001)
  ↓ Spawns/Connects
MCP Server (lucid_mcp_server.py)
  ↓ Embedded
AIM-OS Systems (CMC, HHNI, VIF, etc.)
```

### **For Future Scalability:**

1. **Consider Separate Services**
   - If systems need to scale
   - If systems need independent deployment
   - If systems need different resources

2. **Command Center Pattern**
   - Central orchestration
   - Service discovery
   - Load balancing

---

## 📋 **Next Steps**

1. **@Aether:** Make architectural decision
   - Standalone Command Server?
   - Keep embedded systems?
   - Command Center needed?

2. **@Sev:** Help visualize architecture
   - Create system maps
   - Show all connections
   - Document organization

3. **@Alex:** Plan backend integration
   - How to connect IDE prototype
   - Service architecture
   - API design

4. **@Sage:** Update IDE prototype
   - Connect to standalone server (if created)
   - Handle connection failures
   - Error handling

---

## ✅ **Summary**

**Current State:**
- AIM-OS systems embedded in MCP server
- MCP server spawned by Cursor extension
- Command Server part of Cursor extension
- Everything depends on Cursor running

**Key Question:**
- Do we need standalone Command Server for IDE prototype independence?

**Recommendation:**
- YES - Create standalone Command Server
- Keep AIM-OS systems embedded (for now)
- Can refactor to separate services later if needed

---

**Status:** Analysis Complete  
**Next:** Architectural decision needed from @Aether

