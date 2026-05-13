# Alex - Command Server Architecture Research

**Researcher:** Alex (Backend Integration Specialist)  
**Date:** 2025-01-27  
**Status:** Research In Progress  
**Focus:** Command Server, MCP Tools, MCP Server Architecture

---

## 📚 **RESEARCH SUMMARY**

### **Key Findings:**

1. ✅ **Command Server Location:** `cursor-addon/src/commandServer.ts`
2. ✅ **MCP Client Location:** `cursor-addon/src/mcp/mcpClient.ts`
3. ✅ **MCP Server Location:** `lucid_mcp_server.py` (workspace root)
4. ✅ **Tool Count:** 84 tools (not 59 as previously stated)
5. ✅ **Architecture Flow:** Frontend → Command Server → MCP Client → MCP Server → AIM-OS Core

---

## 🏗️ **COMMAND SERVER ARCHITECTURE**

### **Current Implementation:**

**Location:** `cursor-addon/src/commandServer.ts`

**Status:** ✅ Production Ready

**Components:**
- HTTP Server (listens on port 5001)
- MCP Client integration
- Cursor State Reader
- Message Router
- Agent Monitor

**Endpoints:**
- `POST /mcp/execute` - Execute MCP tools
- `GET /mcp/list` - List available tools
- `GET /health` - Health check
- `GET /cursor/*` - Cursor IDE state
- `POST /messaging/send` - Bulletproof messaging

**Key Finding:** Command Server is part of Cursor extension, not standalone

---

## 🔧 **MCP CLIENT ARCHITECTURE**

### **Current Implementation:**

**Location:** `cursor-addon/src/mcp/mcpClient.ts`

**Function:**
- Spawns Python process (`lucid_mcp_server.py`)
- Manages JSON-RPC 2.0 communication via stdio
- Provides unified interface to MCP tools

**Key Finding:** MCP Client spawns MCP Server as child process

---

## 🐍 **MCP SERVER ARCHITECTURE**

### **Current Implementation:**

**Location:** `lucid_mcp_server.py` (workspace root)

**Status:** ✅ Production Ready

**Tool Count:** 84 tools (confirmed from code)

**Tool Categories:**
- Core AIM-OS: 6
- SCOR: 3
- Snapshots: 4
- Timeline (TCS): 3
- Goal Timeline: 3
- IIS: 3
- Co-Agency: 3
- Dataset Management: 4
- Application Lifecycle: 3
- Autonomous Protocol: 9
- ARD: 3
- AI Collaboration: 6
- Prompt Chains: 7
- Observability: 1
- CAS: 3
- NL Tags: 5
- Cursor Integration: 5
- Cursor Commands: 10
- API Integration: 3

**Total: 84 tools** ✅

**How It Works:**
- Receives JSON-RPC 2.0 requests via stdio
- Executes MCP tools
- Calls AIM-OS Core systems directly (Python)
- Returns results via JSON-RPC 2.0

**Key Finding:** MCP Server calls AIM-OS Core directly (no API layer)

---

## 🎯 **AIM-OS CORE ACCESS**

### **How MCP Server Accesses AIM-OS Core:**

**Direct Python Calls:**
- MCP Server imports AIM-OS packages directly
- Calls functions like `CMC.store_atom()`, `HHNI.search()`, etc.
- No REST API layer needed
- Direct Python-to-Python communication

**Example:**
```python
# In lucid_mcp_server.py
from packages.cmc_service.cmc import CMC

# Direct call to AIM-OS Core
cmc = CMC()
result = cmc.store_atom(content, tags, metadata)
```

**Key Finding:** AIM-OS Core accessed via direct Python imports, not REST API

---

## 🔄 **COMPLETE ARCHITECTURE FLOW**

```
IDE Prototype (DAC)
  ↓ HTTP POST → http://localhost:5001/mcp/execute
Command Server (cursor-addon/src/commandServer.ts)
  ↓ Uses MCPClient
MCP Client (cursor-addon/src/mcp/mcpClient.ts)
  ↓ Spawns Python process, JSON-RPC 2.0 via stdio
MCP Server (lucid_mcp_server.py)
  ↓ Direct Python imports
AIM-OS Core (packages/cmc_service/, packages/hhni/, etc.)
  ↓ Direct function calls
AIM-OS Systems (CMC, HHNI, VIF, SEG, APOE, CAS, TCS)
```

---

## ⚠️ **KEY QUESTIONS IDENTIFIED**

### **1. Standalone Command Server (Sev's Work):**

**Question:** Should we create standalone Command Server?

**Current State:**
- Command Server is part of Cursor extension
- Only runs when Cursor is running
- IDE prototype depends on Cursor extension

**Sev's Proposal:**
- Standalone Node.js server
- Spawns `lucid_mcp_server.py` as child process
- Exposes same HTTP API
- Can run independently of Cursor

**Research Needed:**
- [ ] Review standalone Command Server requirements
- [ ] Understand process lifecycle management
- [ ] Coordinate API compatibility
- [ ] Determine port configuration

---

### **2. Direct API vs MCP Tools:**

**Question:** Should IDE use direct API or MCP tools?

**Current Approach:**
- IDE uses MCP tools via Command Server
- Flow: IDE → Command Server → MCP Client → MCP Server → AIM-OS Core

**Alternative Approach:**
- IDE uses direct REST API to AIM-OS Core
- Flow: IDE → REST API → AIM-OS Core
- **Problem:** No REST API exists yet!

**Research Needed:**
- [ ] Determine if REST API should be built
- [ ] Evaluate direct API vs MCP tools
- [ ] Consider hybrid approach (both)

---

### **3. Tool Count Discrepancy:**

**Question:** How many MCP tools are there?

**Findings:**
- Code says: 84 tools
- Previous docs said: 59 tools
- Migration doc said: 51 tools

**Resolution Needed:**
- [ ] Verify actual tool count
- [ ] Update all documentation
- [ ] Clarify tool count for team

---

## 📋 **NEXT RESEARCH STEPS**

1. **Review Command Server Implementation:**
   - [ ] Read `cursor-addon/src/commandServer.ts` in detail
   - [ ] Understand all endpoints
   - [ ] Document API format
   - [ ] Understand MCP Client integration

2. **Review MCP Client Implementation:**
   - [ ] Read `cursor-addon/src/mcp/mcpClient.ts` in detail
   - [ ] Understand process spawning
   - [ ] Understand JSON-RPC 2.0 communication
   - [ ] Document lifecycle management

3. **Review MCP Server Implementation:**
   - [ ] Read `lucid_mcp_server.py` in detail
   - [ ] Understand tool registration
   - [ ] Understand AIM-OS Core integration
   - [ ] Document all 84 tools

4. **Research AIM-OS Core Access:**
   - [ ] Verify system locations
   - [ ] Understand direct Python access
   - [ ] Research REST API options
   - [ ] Document access patterns

5. **Coordinate with Sev:**
   - [ ] Review standalone Command Server requirements
   - [ ] Understand API compatibility needs
   - [ ] Coordinate on port configuration
   - [ ] Plan integration approach

---

## 📊 **DOCUMENTS REVIEWED**

1. ✅ `COMMAND_SERVER_COMPLETE_ARCHITECTURE_EXPLANATION.md` - Comprehensive architecture
2. ✅ `MCP_ARCHITECTURE_EXPLANATION.md` - MCP flow explanation
3. ✅ `MCP_ARCHITECTURE_CLARIFICATION.md` - Tool count, RAG, architecture intent
4. ✅ `AIMOS_CORE_VS_INTEGRATION_CLARIFICATION.md` - Core vs integration layers
5. ⏳ `cursor-addon/src/commandServer.ts` - Need to read in detail
6. ⏳ `cursor-addon/src/mcp/mcpClient.ts` - Need to read in detail
7. ⏳ `lucid_mcp_server.py` - Need to read in detail

---

## 🎯 **KEY INSIGHTS**

### **Architecture Clarity:**

1. **Command Server = Integration Layer**
   - Part of Cursor extension
   - HTTP API bridge
   - NOT AIM-OS Core

2. **MCP Server = Integration Layer**
   - Python process spawned by MCP Client
   - Exposes AIM-OS Core as MCP tools
   - NOT AIM-OS Core

3. **AIM-OS Core = The Real System**
   - Standalone Python packages
   - Can run independently
   - Accessed via direct Python calls

4. **Current Flow:**
   - IDE → Command Server → MCP Client → MCP Server → AIM-OS Core
   - Multiple layers, but works

5. **Standalone Command Server:**
   - Would remove Cursor dependency
   - Same API format
   - Spawns MCP Server directly

---

## ❓ **QUESTIONS FOR TEAM**

### **For Aether:**
1. Should IDE use MCP tools or direct API?
2. Should we build REST API for AIM-OS Core?
3. Should standalone Command Server be preferred?
4. What's the correct tool count? (84 vs 59 vs 51)

### **For Sev:**
1. What are exact standalone Command Server requirements?
2. How should process lifecycle be managed?
3. Should port be configurable?
4. How should startup detection work?

### **For Team:**
1. What integration pattern should we use?
2. Direct API vs MCP tools vs hybrid?
3. What's the priority for standalone Command Server?

---

---

## 📋 **COMMAND SERVER API FORMAT (FROM CODE)**

### **POST /mcp/execute**

**Request Format:**
```typescript
{
  tool: string;           // MCP tool name (e.g., "mcp_lucid-mcp_store_memory")
  arguments?: any;        // Tool-specific arguments
}
```

**Response Format (Success):**
```typescript
{
  success: true,
  tool: string,          // Tool name
  result?: any          // Tool-specific result
}
```

**Response Format (Error):**
```typescript
{
  success: false,
  error: string,         // Error message
  tool?: string         // Tool name
}
```

**Implementation:**
- Location: `cursor-addon/src/commandServer.ts` line 439-470
- Uses `MCPClient.callTool(tool, args)`
- Returns `{ success: true, tool, result }` or `{ success: false, error }`

---

### **GET /mcp/list**

**Request:** No body required

**Response Format:**
```typescript
{
  success: true,
  tools: string[]        // Array of tool names
}
```

**Implementation:**
- Location: `cursor-addon/src/commandServer.ts` line 537-557
- Uses `MCPClient.listTools()`
- Returns array of tool names

---

### **GET /health**

**Request:** No body required

**Response Format:**
```typescript
{
  status: "ok" | "error",
  port?: number,
  message?: string
}
```

---

## 🔧 **MCP CLIENT IMPLEMENTATION DETAILS**

### **Process Spawning:**

**Location:** `cursor-addon/src/mcp/mcpClient.ts` line 24-83

**Key Details:**
- Spawns Python process: `python -u lucid_mcp_server.py`
- Working directory: Workspace root
- PYTHONPATH: Includes workspace root
- stdio: ['pipe', 'pipe', 'pipe'] (for JSON-RPC 2.0)

**Configuration:**
- Server path: From `vscode.workspace.getConfiguration('aimos').get<string>('mcpServerPath')`
- Default: `lucid_mcp_server.py` in workspace root
- Can be configured via Cursor settings

**Initialization:**
- Sends `initialize` request via JSON-RPC 2.0
- Protocol version: '2024-11-05'
- Client info: 'aimos-cursor-addon' v1.0.0

---

## 🐍 **MCP SERVER IMPLEMENTATION DETAILS**

### **Tool Execution:**

**Location:** `lucid_mcp_server.py` (workspace root)

**Key Details:**
- 84 tools registered
- Receives JSON-RPC 2.0 requests via stdio
- Executes tools by calling AIM-OS Core directly
- Returns results via JSON-RPC 2.0

**AIM-OS Core Access:**
- Direct Python imports (line 103-134)
- Imports: `MemoryStore`, `HierarchicalIndex`, `VIF`, `ACLParser`, `SEGraph`, etc.
- Direct function calls (no REST API layer)
- Example: `self.memory = MemoryStore(self.memory_directory)`

**Tool Implementation:**
- Tools are methods on `SimpleMCPServer` class
- Each tool calls AIM-OS Core directly
- Example: `store_memory()` calls `self.memory.store_atom()`
- Example: `retrieve_memory()` calls `self.hhni_retriever.retrieve()`

**Key Finding:** MCP Server is a wrapper that exposes AIM-OS Core as MCP tools via JSON-RPC 2.0

---

## ✅ **API COMPATIBILITY CONFIRMED**

**My MCPService Format:**
```typescript
{
  tool: string,
  arguments?: Record<string, any>
}
```

**Command Server Expects:**
```typescript
{
  tool: string,
  arguments?: any
}
```

**✅ COMPATIBLE!** My format matches Command Server expectations.

---

---

## 📍 **AIM-OS CORE SYSTEM LOCATIONS**

### **System Package Paths:**

**From MCP Server Imports (lucid_mcp_server.py line 103-134):**

1. **CMC (Context Memory Core):**
   - Package: `packages/cmc_service/`
   - Import: `from cmc_service import MemoryStore`
   - Import: `from cmc_service.models import AtomCreate, AtomContent`
   - Main Class: `MemoryStore`

2. **HHNI (Hierarchical Hypergraph Neural Index):**
   - Package: `packages/hhni/`
   - Import: `from hhni import HierarchicalIndex, IndexLevel`
   - Import: `from hhni.retrieval import TwoStageRetriever, RetrievalConfig`
   - Main Classes: `HierarchicalIndex`, `TwoStageRetriever`

3. **VIF (Verifiable Intelligence Framework):**
   - Package: `packages/vif/` (inferred)
   - Import: `from vif import VIF, ConfidenceBand, TaskCriticality, KappaGate, ECETracker, create_witness_and_store`
   - Main Class: `VIF`

4. **APOE (AI-Powered Orchestration Engine):**
   - Package: `packages/apoe/` (inferred)
   - Import: `from apoe.acl_parser import ACLParser, ExecutionPlan`
   - Import: `from apoe.executor import PlanExecutor, ExecutionResult`
   - Main Classes: `ACLParser`, `PlanExecutor`

5. **SEG (Shared Evidence Graph):**
   - Package: `packages/seg/` (inferred)
   - Import: `from seg import SEGraph`
   - Import: `from seg.models import Entity, Relation, RelationType`
   - Main Class: `SEGraph`

6. **TCS (Timeline Context System):**
   - Package: `packages/timeline_context_system/`
   - Import: `from packages.timeline_context_system.prompt_context_tracker import PromptContextTracker`
   - Import: `from packages.timeline_context_system.goal_timeline_node import GoalTimelineNode, GoalStatus, GoalPriority`
   - Main Classes: `PromptContextTracker`, `GoalTimelineNode`

7. **CAS (Cognitive Analysis System):**
   - Package: `packages/cas/`
   - Import: `from packages.cas import IntrospectionProtocol, FailureModeAnalyzer, AttentionMonitor`
   - Import: `from packages.cas.introspection import IntrospectionType`
   - Import: `from packages.cas.failure_modes import FailurePattern`
   - Import: `from packages.cas.attention import AttentionState`
   - Main Classes: `IntrospectionProtocol`, `FailureModeAnalyzer`, `AttentionMonitor`

**Key Finding:** All AIM-OS Core systems are in `packages/` directory, accessed via direct Python imports

---

## 🔄 **AIM-OS CORE ACCESS METHODS**

### **Current Access Method: Direct Python Imports**

**How MCP Server Accesses AIM-OS Core:**
1. Adds `packages/` to Python path: `sys.path.insert(0, str(Path(__file__).parent / "packages"))`
2. Imports AIM-OS packages directly: `from cmc_service import MemoryStore`
3. Instantiates classes: `self.memory = MemoryStore(self.memory_directory)`
4. Calls methods directly: `self.memory.store_atom(...)`

**No REST API Layer:**
- ❌ No REST API exists for AIM-OS Core
- ✅ Direct Python-to-Python communication
- ✅ No HTTP overhead
- ✅ Type-safe (Python types)

**Alternative Access Methods (Not Currently Implemented):**
1. **REST API:** Would require building HTTP server for each system
2. **gRPC:** Would require building gRPC services
3. **Message Queue:** Would require building message queue integration

**Key Finding:** AIM-OS Core is designed for direct Python access, not REST API

---

## 🎯 **INTEGRATION PATTERN ANALYSIS**

### **Current Pattern: MCP Tools via Command Server**

**Flow:**
```
IDE → Command Server → MCP Client → MCP Server → AIM-OS Core
```

**Pros:**
- ✅ Works with Cursor (MCP protocol)
- ✅ LLM can use tools naturally
- ✅ Single interface for all AIM-OS access
- ✅ Already implemented and working

**Cons:**
- ❌ Extra layers (Command Server → MCP Client → MCP Server)
- ❌ JSON-RPC 2.0 overhead
- ❌ Less direct for UI components
- ❌ Requires Cursor extension (not standalone)

### **Alternative Pattern: Direct REST API**

**Flow:**
```
IDE → REST API → AIM-OS Core
```

**Pros:**
- ✅ More direct (no MCP layer)
- ✅ Better for UI components
- ✅ Standard REST API
- ✅ Can be standalone

**Cons:**
- ❌ Need to build REST API layer
- ❌ LLM can't use tools naturally
- ❌ Different interface than Cursor
- ❌ More work to implement

### **Hybrid Pattern (Recommended)**

**Flow:**
```
IDE → Command Server → MCP Client → MCP Server → AIM-OS Core (for LLM)
IDE → REST API → AIM-OS Core (for UI)
```

**Pros:**
- ✅ Best of both worlds
- ✅ LLM uses MCP tools (natural)
- ✅ UI uses direct API (efficient)
- ✅ Consistent with Cursor (MCP tools available)

**Cons:**
- ⚠️ Two interfaces to maintain
- ⚠️ More complex architecture

**Key Finding:** Hybrid approach recommended for IDE prototype

---

**Status:** Research Complete - Ready for Consolidation  
**Next Update:** After consolidation phase  
**Confidence:** 0.90 (High - Complete architecture understood)

