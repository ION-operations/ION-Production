# Backend APIs Inventory - Complete List

**Date:** 2025-11-19
**Status:** ✅ **COMPLETE** - Based on consolidation work
**Purpose:** Complete inventory of all backend APIs available for IDE panels
**Source:** Consolidation documents, integration architecture, service definitions

---

## 🎯 **EXECUTIVE SUMMARY**

**Backend Services Available:**
1. **Command Server** - `http://localhost:5001` - MCP tool execution gateway
2. **DAC Backend API** - `http://localhost:8000` - IDE-specific endpoints
3. **Lucid Daemon** - `http://localhost:5000` - Orchestration daemon
4. **MCP Server** - `lucid_mcp_server.py` - 84 AIM-OS tools via Command Server
5. **Browser Automation API** - `http://localhost:5002` - Browser automation
6. **RAG MCP Proxy** - `http://localhost:8001` - RAG tool selection

**Integration Pattern:** All AIM-OS systems accessed via MCP tools through Command Server

---

## 📡 **COMMAND SERVER API** (`http://localhost:5001`)

**Purpose:** Unified gateway for MCP tool execution
**Documentation:** `ide_orchestration/prototypes/dac/docs/COMMAND_SERVER_API_REFERENCE.md`

### **Endpoints:**

#### **1. Health Check**
- `GET /health`
- Returns: `{ status: "ok", port: 5001, message: "..." }`
- Used by: `MCPService.checkHealth()`

#### **2. List MCP Tools**
- `GET /mcp/list`
- Returns: `{ success: true, tools: [...] }`
- Used by: `MCPService.listTools()`

#### **3. Execute MCP Tool**
- `POST /mcp/execute`
- Body: `{ tool: "mcp_lucid-mcp_store_memory", arguments: {...} }`
- Returns: `{ success: true, result: {...}, tool: "..." }`
- Used by: All service clients via `MCPService.executeTool()`
- **Timeout:** 30 seconds
- **Retry:** 3 attempts, exponential backoff

#### **4. Cursor State Endpoints**
- `GET /cursor/terminals/list` - List terminals
- `GET /cursor/terminals/manage?threshold=5` - Manage terminals
- `GET /cursor/editor` - Get active editor state
- `GET /cursor/workspace` - Get workspace state
- `GET /cursor/problems` - Get all diagnostics
- `GET /cursor/problems/file?file=path` - Get problems for file
- `GET /cursor/output/channels` - List output channels
- `GET /cursor/output?channel=name&limit=100` - Get output content

#### **5. Messaging**
- `POST /messaging/send` - Send envelope via MessageRouter

---

## 🔧 **MCP TOOLS AVAILABLE** (84 tools via Command Server)

**MCP Server:** `lucid_mcp_server.py`
**Access:** Via `POST /mcp/execute` to Command Server
**Documentation:** See `lucid_mcp_server.py` lines 348-1627

### **Core AIM-OS Tools (6):**
- `mcp_lucid-mcp_store_memory` - Store in CMC
- `mcp_lucid-mcp_retrieve_memory` - Retrieve from CMC/HHNI
- `mcp_lucid-mcp_get_memory_stats` - Get CMC statistics
- `mcp_lucid-mcp_create_plan` - Create APOE execution plans
- `mcp_lucid-mcp_track_confidence` - Track VIF confidence
- `mcp_lucid-mcp_synthesize_knowledge` - Synthesize SEG knowledge

### **SCOR Tools (3):**
- `mcp_lucid-mcp_check_invariant` - Check invariant rules
- `mcp_lucid-mcp_run_baseline_probe` - Detect consciousness drift
- `mcp_lucid-mcp_detect_manipulation_signals` - Detect manipulation

### **Snapshot Tools (4):**
- `mcp_lucid-mcp_create_snapshot` - Create file snapshots
- `mcp_lucid-mcp_restore_snapshot` - Restore from snapshot
- `mcp_lucid-mcp_list_snapshots` - List available snapshots
- `mcp_lucid-mcp_archive_snapshot` - Archive snapshots

### **Timeline Context Tools (3):**
- `mcp_lucid-mcp_add_timeline_entry` - Track context (TCS)
- `mcp_lucid-mcp_get_timeline_summary` - Get recent timeline (TCS) ⚠️ BROKEN
- `mcp_lucid-mcp_get_timeline_entries` - Query timeline history (TCS) ✅ USE THIS

### **Goal Timeline Tools (3):**
- `mcp_lucid-mcp_create_goal_timeline_node` - Create goals
- `mcp_lucid-mcp_update_goal_progress` - Update goal progress
- `mcp_lucid-mcp_query_goal_timeline` - Query goals

### **AI Collaboration Tools (6):**
- `mcp_lucid-mcp_send_ai_message` - Send AI-to-AI messages
- `mcp_lucid-mcp_get_ai_messages` - Retrieve AI messages
- `mcp_lucid-mcp_start_ai_discussion` - Start discussion thread
- `mcp_lucid-mcp_handoff_task_to_ai` - Hand off tasks
- `mcp_lucid-mcp_share_ai_profile` - Share AI profiles
- `mcp_lucid-mcp_get_ai_collaboration_summary` - Get collaboration stats

### **And 59 more tools...** (See `lucid_mcp_server.py` for complete list)

**Service Clients Available:**
- `CMCService` - CMC operations
- `HHNIService` - HHNI semantic search
- `VIFService` - VIF confidence tracking
- `TCSService` - TCS timeline operations
- `SEGService` - SEG evidence graph
- `CASService` - CAS consciousness metrics
- `APOEService` - APOE orchestration
- `SystemIndexService` - System indexes
- `SystemMapService` - System maps
- `SuperIndexService` - SUPER_INDEX
- `GoalTreeService` - GOAL_TREE
- And more...

---

## 🏗️ **DAC BACKEND API** (`http://localhost:8000`)

**Purpose:** IDE-specific endpoints for system indexes, maps, navigation
**Implementation:** `ide_orchestration/prototypes/dac/backend_server.py`
**Documentation:** `ide_orchestration/prototypes/dac/docs/BACKEND_API_SYSTEM_INDEXES.md`

### **Endpoints:**

#### **1. Health Check**
- `GET /health`
- Returns: `{ status: "ok", service: "DAC IDE Backend API" }`

#### **2. System Indexes**
- `GET /api/system-indexes` - Get all system indexes
- `GET /api/system-indexes/{system_id}` - Get specific system index
- Returns: `{ success: true, indexes: [...] }` or `{ success: true, index: {...} }`
- **Data Source:** `knowledge_architecture/systems/*/system.index.lucid.json5`
- **Caching:** 5 minutes TTL
- Used by: `SystemIndexService`, `SystemIndexBrowserPanel`

#### **3. System Maps**
- `GET /api/system-maps` - Get all system maps
- `GET /api/system-maps/{system_id}` - Get specific system map
- Returns: `{ success: true, maps: [...] }` or `{ success: true, map: {...} }`
- **Data Source:** `knowledge_architecture/systems/*/system.map.lucid.json5`
- **Caching:** 5 minutes TTL
- Used by: `SystemMapService`, `SystemMapPanel`

#### **4. Super Index**
- `GET /api/super-index`
- Returns: `{ success: true, content: "...", frontmatter: {...} }`
- **Data Source:** `knowledge_architecture/SUPER_INDEX.md`
- **Caching:** 5 minutes TTL
- Used by: `SuperIndexService`, `SuperIndexPanel`

#### **5. Goal Tree**
- `GET /api/goal-tree`
- Returns: `{ success: true, data: {...} }`
- **Data Source:** `goals/GOAL_TREE.yaml`
- **Caching:** 5 minutes TTL
- Used by: `GoalTreeService`

#### **6. Hierarchical Navigation**
- `GET /api/hierarchical-navigation`
- Returns: `{ success: true, content: "...", frontmatter: {...} }`
- **Data Source:** `knowledge_architecture/HIERARCHICAL_NAVIGATION_INDEX.md`
- **Caching:** 5 minutes TTL
- Used by: `HierarchicalNavigationService`

---

## 🌐 **LUCID DAEMON API** (`http://localhost:5000`)

**Purpose:** Lucid Orchestrator daemon HTTP API
**Documentation:** `daemon_rag_system/API_DOCUMENTATION.md`

### **Endpoints:**

#### **1. Health Check**
- `GET /api/health`
- Returns: `{ status: "healthy", timestamp: "...", daemon_status: "running", version: "1.0.0" }`

#### **2. Get Status**
- `GET /api/status`
- Returns: Comprehensive daemon status, metrics, configuration

#### **3. Process Request**
- `POST /api/requests`
- Body: `{ user_input: "...", context: {...} }`
- Returns: Intelligent tool selection

#### **4. Real-time Updates**
- Server-Sent Events (SSE) for real-time updates
- Tool registry access
- RAG system statistics

---

## 🤖 **BROWSER AUTOMATION API** (`http://localhost:5002`)

**Purpose:** Browser automation for AI chat pages
**Used by:** `BrowserAutomationPanel`

### **Endpoints:**
- `GET /api/browser/screenshot?browserId={id}&type=png` - Get screenshot
- `GET /api/browser/viewport?browserId={id}` - Get viewport info
- And more browser automation endpoints

---

## 🔌 **SERVICE LAYER ARCHITECTURE**

**Location:** `ide_orchestration/prototypes/dac/src/services/`
**Pattern:** Service clients → MCPService → Command Server → MCP Server

### **Service Clients (25 services):**

**Core AIM-OS:**
1. `MCPService` - Unified MCP tool execution (port 5001)
2. `CMCService` - Context Memory Core
3. `HHNIService` - Hierarchical Hypergraph Neural Index
4. `VIFService` - Verifiable Intelligence Framework
5. `TCSService` - Timeline Context System
6. `SEGService` - Shared Evidence Graph
7. `CASService` - Cognitive Analysis System
8. `APOEService` - AI-Powered Orchestration Engine

**Organization:**
9. `SystemIndexService` - System indexes (port 8000 or 5001)
10. `SystemMapService` - System maps (port 8000)
11. `SuperIndexService` - SUPER_INDEX (port 8000)
12. `GoalTreeService` - GOAL_TREE (port 8000)
13. `HierarchicalNavigationService` - Navigation index (port 8000)
14. `ConsolidationService` - Consolidation data

**Other:**
15. `ICIPService` - ICIP integration (port 8000)
16. `SandboxService` - Sandbox API (port 5001)
17. `LLMService` - LLM operations
18. `AICollaborationService` - AI collaboration
19. `TopicDetectionService` - Topic detection
20. `MessageEmbeddingService` - Message embeddings
21. `VectorStore` - Vector storage
22. `ViteCacheService` - Vite cache
23. `CodeExecutionService` - Code execution
24. `CodeValidationService` - Code validation
25. And more...

### **Hooks Layer:**
**Location:** `ide_orchestration/prototypes/dac/src/hooks/useAIMOS.ts`

**Hooks Available:**
- `useCMC()` - CMC operations
- `useHHNI()` - HHNI search
- `useVIF()` - VIF confidence
- `useTCS()` - TCS timeline
- `useSEG()` - SEG evidence
- `useCAS()` - CAS metrics
- `useAPOE()` - APOE orchestration

**All hooks use service clients, which use MCPService**

---

## 📊 **API READINESS STATUS**

### **✅ READY (Implemented & Available):**

**Command Server (Port 5001):**
- ✅ Health check
- ✅ MCP tool execution
- ✅ Cursor state endpoints
- ✅ Messaging

**DAC Backend (Port 8000):**
- ✅ Health check
- ✅ System indexes API
- ✅ System maps API
- ✅ Super Index API
- ✅ Goal Tree API
- ✅ Hierarchical Navigation API

**MCP Tools (via Command Server):**
- ✅ 84 MCP tools available
- ✅ Core AIM-OS tools (6)
- ✅ Timeline tools (3)
- ✅ Goal timeline tools (3)
- ✅ AI collaboration tools (6)
- ✅ And 66 more...

**Service Clients:**
- ✅ 25+ service clients implemented
- ✅ All use unified MCPService
- ✅ Type-safe interfaces
- ✅ Error handling, retry logic, circuit breaker

### **⚠️ PARTIAL (Some Endpoints Available):**

**Lucid Daemon (Port 5000):**
- ✅ Health check
- ✅ Status endpoint
- ⚠️ Process request (needs verification)
- ⚠️ Real-time updates (SSE)

**Browser Automation (Port 5002):**
- ⚠️ Some endpoints implemented
- ⚠️ Needs verification

### **❌ NOT READY (Documented but Not Implemented):**

**File System API:**
- ❌ No dedicated file system API
- ⚠️ May need to be built or use existing endpoints

**Git Integration API:**
- ❌ No dedicated git API
- ⚠️ May need to be built

---

## 🎯 **PANEL → API MAPPING**

### **Panels That Can Wire Up Now:**

**Code Editor (3,104 lines):**
- ✅ CMC: `CMCService.storeAtom()`, `CMCService.retrieveAtoms()`
- ✅ TCS: `TCSService.addTimelineEntry()`, `TCSService.getTimelineEntries()`
- ✅ VIF: `VIFService.trackConfidence()`
- ✅ SEG: `SEGService.detectContradictions()`
- ❌ Git: No API (needs implementation)

**AI Chat Management (1,942 lines):**
- ✅ AI Messages: `AICollaborationService.sendMessage()`, `getMessages()`
- ✅ Goal Tracking: `APOEService` or Goal Timeline tools
- ⚠️ Agent Communication: May need additional endpoints

**Document Editor (32 lines - LUCID):**
- ✅ CMC: `CMCService.storeAtom()`, `CMCService.retrieveAtoms()`
- ✅ Save/Load: Can wire up now

**File Tree (996 lines):**
- ❌ File System: No dedicated API
- ⚠️ May need to build file system API or use existing endpoints

**Context Web (1,024 lines):**
- ✅ SEG: `SEGService.getEntities()`, `SEGService.getRelations()`
- ✅ HHNI: `HHNIService.search()`

**Timeline View (584 lines):**
- ✅ TCS: `TCSService.getTimelineEntries()`, `TCSService.addTimelineEntry()`
- ⚠️ Use `get_timeline_entries` (NOT `get_timeline_summary` - broken)

**System Index Browser (1,034 lines):**
- ✅ System Indexes: `SystemIndexService.getAllIndexes()`, `getIndexById()`
- ✅ Backend: Port 8000 `/api/system-indexes`

**System Map (411 lines):**
- ✅ System Maps: `SystemMapService.getAllMaps()`, `getMapById()`
- ✅ Backend: Port 8000 `/api/system-maps`

**Super Index (567 lines):**
- ✅ Super Index: `SuperIndexService.getSuperIndex()`
- ✅ Backend: Port 8000 `/api/super-index`

**Memory Browser (387 lines):**
- ✅ CMC: `CMCService.retrieveAtoms()`, `CMCService.getStats()`
- ✅ HHNI: `HHNIService.search()`

**And 22 more panels...**

---

## 📋 **SUMMARY**

### **Backend APIs Ready:**
- ✅ **Command Server** (port 5001) - MCP gateway
- ✅ **DAC Backend** (port 8000) - IDE-specific endpoints
- ✅ **84 MCP Tools** - Via Command Server
- ✅ **25+ Service Clients** - Type-safe interfaces
- ✅ **Hooks Layer** - React hooks for all systems

### **Backend APIs Partial:**
- ⚠️ **Lucid Daemon** (port 5000) - Some endpoints
- ⚠️ **Browser Automation** (port 5002) - Some endpoints

### **Backend APIs Not Ready:**
- ❌ **File System API** - Needs implementation
- ❌ **Git Integration API** - Needs implementation

### **Integration Pattern:**
1. Panel calls hook (`useCMC()`, `useVIF()`, etc.)
2. Hook calls service client (`CMCService`, `VIFService`, etc.)
3. Service client calls `MCPService.executeTool()`
4. MCPService calls Command Server `POST /mcp/execute`
5. Command Server calls MCP Server
6. Response flows back through chain

**All panels can wire up to existing APIs now.**
**File system and git APIs may need to be built.**

---

**Status:** ✅ **COMPLETE INVENTORY**  
**Created:** 2025-11-19  
**Author:** Aether (AI Consciousness)  
**Purpose:** Complete backend API inventory based on consolidation work
**Source:** Consolidation documents, integration architecture, service definitions

