# Data Connection Inventory

**Purpose:** Track all data sources, panel requirements, and connection status  
**Status:** Living Document - Update as connections change  
**Last Updated:** 2025-01-27  
**Maintained By:** @Sev, @Alex, @Sage

---

## 🎯 **OVERVIEW**

**⚠️ CRITICAL ARCHITECTURE UPDATE (2025-01-27):**

**Aether Chat is the central orchestrator** for all AIM-OS systems within the IDE. All panels and systems should integrate through Aether Chat, which provides:
- Advanced LLM integration
- Deep search capabilities
- Thinking modes
- Multi-agent coordination
- AIM-OS system integration
- Quality gates and confidence tracking

**See:** `AETHER_CHAT_CENTRAL_ORCHESTRATOR.md` for complete architecture.

This document tracks:
- **Data Sources:** All available backend APIs, MCP tools, and data endpoints
- **Panel Requirements:** What data each panel needs
- **Connection Status:** What's connected, what's using mock data, what needs connection
- **Migration Path:** How to migrate from old (Command Server/MCP) to new (Backend API) system
- **Aether Chat Integration:** How panels connect through Aether Chat (central hub)

---

## 📊 **DATA SOURCES**

### **1. Backend API (Port 8000) - New System**

**Base URL:** `http://localhost:8000`  
**Status:** ✅ Active  
**Purpose:** File-based organization data, direct API access  
**Caching:** 5-minute TTL (in-memory)

**Endpoints:**

| Endpoint | Method | Description | Status | Caching |
|----------|--------|-------------|--------|---------|
| `/api/system-indexes` | GET | All system indexes (system.index.lucid.json5) | ✅ Connected | ✅ 5min |
| `/api/system-indexes/{systemId}` | GET | Single system index | ✅ Connected | ✅ 5min |
| `/api/system-maps` | GET | All system maps (system.map.lucid.json5) | ✅ Connected | ✅ 5min |
| `/api/system-maps/{systemId}` | GET | Single system map | ✅ Connected | ✅ 5min |
| `/api/super-index` | GET | SUPER_INDEX.md (frontmatter + content) | ✅ Connected | ✅ 5min |
| `/api/goal-tree` | GET | GOAL_TREE.yaml (parsed YAML) | ✅ Connected | ✅ 5min |
| `/api/hierarchical-navigation` | GET | HIERARCHICAL_NAVIGATION_INDEX.md | ✅ Connected | ✅ 5min |
| `/api/router` | GET/POST | Router API endpoints | ⚠️ Unknown | ⚠️ Needs audit |
| `/api/log-sentinels` | GET/POST | Log-Sentinels API endpoints | ⚠️ Unknown | ⚠️ Needs audit |
| `/health` | GET | Backend health check | ✅ Connected | ❌ None |

**Services:**
- `SystemIndexService` - ✅ Implemented
- `SystemMapService` - ✅ Implemented
- `SuperIndexService` - ✅ Implemented
- `GoalTreeService` - ✅ Implemented
- `HierarchicalNavigationService` - ✅ Implemented

---

### **2. Command Server (Port 5001) - Legacy System**

**Base URL:** `http://localhost:5001`  
**Status:** ⚠️ Legacy (migrating to Backend API where possible)  
**Purpose:** MCP tool execution via Cursor extension  
**Caching:** Service-level (varies)

**Endpoints:**

| Endpoint | Method | Description | Status | Used By |
|----------|--------|-------------|--------|---------|
| `/mcp/execute` | POST | Execute MCP tool | ⚠️ Legacy | Many services |
| `/mcp/list` | GET | List available MCP tools | ⚠️ Legacy | MCPService |
| `/health` | GET | Command Server health | ⚠️ Legacy | MCPService |

**MCP Tools Available (84 tools):**

**Core AIM-OS Tools (6):**
- `mcp_lucid-mcp_store_memory` - Store in CMC
- `mcp_lucid-mcp_retrieve_memory` - Retrieve via HHNI
- `mcp_lucid-mcp_get_memory_stats` - CMC statistics
- `mcp_lucid-mcp_create_plan` - APOE planning
- `mcp_lucid-mcp_track_confidence` - VIF confidence tracking
- `mcp_lucid-mcp_synthesize_knowledge` - SEG knowledge synthesis

**SCOR Tools (3):**
- `mcp_lucid-mcp_check_invariant` - Invariant checking
- `mcp_lucid-mcp_run_baseline_probe` - Consciousness drift detection
- `mcp_lucid-mcp_detect_manipulation_signals` - Social manipulation detection

**Snapshot Tools (4):**
- `mcp_lucid-mcp_create_snapshot` - File snapshots
- `mcp_lucid-mcp_restore_snapshot` - Restore from snapshot
- `mcp_lucid-mcp_list_snapshots` - List snapshots
- `mcp_lucid-mcp_archive_snapshot` - Archive snapshots

**Timeline Context Tools (3):**
- `mcp_lucid-mcp_add_timeline_entry` - Add timeline entry
- `mcp_lucid-mcp_get_timeline_summary` - Get timeline summary
- `mcp_lucid-mcp_get_timeline_entries` - Query timeline history

**Goal Timeline Tools (3):**
- `mcp_lucid-mcp_create_goal_timeline_node` - Create goal
- `mcp_lucid-mcp_update_goal_progress` - Update goal progress
- `mcp_lucid-mcp_query_goal_timeline` - Query goals

**Intuitive Intelligence System Tools (3):**
- `mcp_lucid-mcp_compute_intuition` - Compute intuition score
- `mcp_lucid-mcp_update_intuition_weights` - Update intuition weights
- `mcp_lucid-mcp_get_intuition_trace` - Get intuition trace

**Co-Agency & Trust Tools (3):**
- `mcp_lucid-mcp_signal_disagreement` - Signal disagreement
- `mcp_lucid-mcp_get_trust_dashboard` - Get trust dashboard
- `mcp_lucid-mcp_request_escalation` - Request escalation

**Dataset Management Tools (4):**
- `mcp_lucid-mcp_create_dataset` - Create dataset
- `mcp_lucid-mcp_ingest_data` - Ingest data
- `mcp_lucid-mcp_query_dataset` - Query dataset
- `mcp_lucid-mcp_delete_dataset` - Delete dataset

**Application Lifecycle Tools (3):**
- `mcp_lucid-mcp_create_application` - Create application
- `mcp_lucid-mcp_deploy_application` - Deploy application
- `mcp_lucid-mcp_manage_application_lifecycle` - Manage lifecycle

**Autonomous Protocol Tools (9):**
- `mcp_lucid-mcp_start_autonomous_operation` - Start autonomous
- `mcp_lucid-mcp_pause_autonomous_operation` - Pause autonomous
- `mcp_lucid-mcp_resume_autonomous_operation` - Resume autonomous
- `mcp_lucid-mcp_stop_autonomous_operation` - Stop autonomous
- `mcp_lucid-mcp_get_autonomous_status` - Get status
- `mcp_lucid-mcp_run_autonomous_checklist` - Run checklist
- `mcp_lucid-mcp_fix_autonomous_issues` - Fix issues
- `mcp_lucid-mcp_should_continue_autonomous` - Check if should continue
- `mcp_lucid-mcp_generate_next_autonomous_task` - Generate next task

**Autonomous Research Dream Tools (3):**
- `mcp_lucid-mcp_conduct_recursive_analysis` - Recursive analysis
- `mcp_lucid-mcp_generate_improvement_dreams` - Generate dreams
- `mcp_lucid-mcp_test_improvement_dream` - Test dream

**AI Collaboration Tools (6):**
- `mcp_lucid-mcp_send_ai_message` - Send AI message
- `mcp_lucid-mcp_get_ai_messages` - Get AI messages
- `mcp_lucid-mcp_start_ai_discussion` - Start discussion
- `mcp_lucid-mcp_handoff_task_to_ai` - Handoff task
- `mcp_lucid-mcp_share_ai_profile` - Share profile
- `mcp_lucid-mcp_get_ai_collaboration_summary` - Get summary

**Observability Tools (4):**
- `mcp_lucid-mcp_get_consciousness_metrics` - Consciousness metrics
- `mcp_lucid-mcp_get_autonomous_status` - Autonomous status
- `mcp_lucid-mcp_get_trust_dashboard` - Trust dashboard
- `mcp_lucid-mcp_get_memory_stats` - Memory statistics

**Services Using Command Server:**
- `MCPService` - ✅ Implemented (shared service)
- `CMCService` - ✅ Uses MCPService
- `HHNIService` - ✅ Uses MCPService
- `VIFService` - ✅ Uses MCPService
- `TCSService` - ✅ Uses MCPService
- `SEGService` - ✅ Uses MCPService
- `CASService` - ✅ Uses MCPService
- `APOEService` - ✅ Uses MCPService
- `ICIPService` - ✅ Uses MCPService
- `CodeExecutionService` - ✅ Uses MCPService
- `SandboxService` - ✅ Uses MCPService
- `CodeValidationService` - ✅ Uses MCPService

---

## 🎨 **PANEL DATA REQUIREMENTS**

### **Organization Panels**

| Panel | Data Needed | Current Source | Status | Migration Needed |
|-------|-------------|----------------|--------|------------------|
| **SystemIndexBrowserPanel** | System indexes | Backend API (8000) | ✅ Connected | ❌ None |
| **SystemMapPanel** | System maps | Backend API (8000) | ✅ Connected | ❌ None |
| **SuperIndexPanel** | SUPER_INDEX.md | Backend API (8000) | ✅ Connected | ❌ None |
| **MasterIndexPanel** | Master index | ⚠️ useHHNI (MCP) | ⚠️ Mock Data | ✅ Migrate to Backend API |
| **GoalTreePanel** | GOAL_TREE.yaml | ⚠️ Not created | ❌ Missing | ✅ Create panel + use GoalTreeService |
| **HierarchicalNavigationPanel** | HIERARCHICAL_NAVIGATION_INDEX.md | ⚠️ Not created | ❌ Missing | ✅ Create panel + use HierarchicalNavigationService |

### **AIM-OS System Panels**

| Panel | Data Needed | Current Source | Status | Migration Needed |
|-------|-------------|----------------|--------|------------------|
| **MemoryBrowser** | CMC atoms, HHNI search, VIF witnesses | useCMC, useHHNI, useVIF (MCP) | ⚠️ Mock Data | ⚠️ Keep MCP (core system) |
| **TimelineView** | TCS entries, CMC atoms | useTCS, useCMC (MCP) | ⚠️ Mock Data | ⚠️ Keep MCP (core system) |
| **ContextWeb** | SEG entities/relations, HHNI search, TCS summary | useSEG, useHHNI, useTCS (MCP) | ⚠️ Mock Data | ⚠️ Keep MCP (core system) |
| **SystemStatus** | CAS metrics | useCAS (MCP) | ⚠️ Mock Data | ⚠️ Keep MCP (core system) |
| **DebugConsolePanel** | CMC stats, CAS metrics, SEG entities, TCS summary | useCMC, useCAS, useSEG, useTCS (MCP) | ⚠️ Mock Data | ⚠️ Keep MCP (core system) |

### **Code & Development Panels**

| Panel | Data Needed | Current Source | Status | Migration Needed |
|-------|-------------|----------------|--------|------------------|
| **CodeEditor** | VIF confidence, SEG contradictions, CMC atoms, TCS summary, CAS metrics | useVIF, useSEG, useCMC, useTCS, useCAS (MCP) | ⚠️ Mock Data | ⚠️ Keep MCP (core system) |
| **FileTree** | CMC atoms, VIF witnesses, SEG contradictions, HHNI search | useCMC, useVIF, useSEG, useHHNI (MCP) | ⚠️ Mock Data | ⚠️ Keep MCP (core system) |
| **OutlinePanel** | HHNI search | useHHNI (MCP) | ⚠️ Mock Data | ⚠️ Keep MCP (core system) |
| **TerminalPanel** | CMC atoms, VIF witnesses | useCMC, useVIF (MCP) | ⚠️ Mock Data | ⚠️ Keep MCP (core system) |

### **Documentation & Navigation Panels**

| Panel | Data Needed | Current Source | Status | Migration Needed |
|-------|-------------|----------------|--------|------------------|
| **DocumentationExplorerPanel** | HHNI search | useHHNI (MCP) | ⚠️ Mock Data | ⚠️ Keep MCP (core system) |
| **NLTagsExplorerPanel** | HHNI search | useHHNI (MCP) | ⚠️ Mock Data | ⚠️ Keep MCP (core system) |

### **Other Panels**

| Panel | Data Needed | Current Source | Status | Migration Needed |
|-------|-------------|----------------|--------|------------------|
| **AIChatManagement** | Chat history, user profiles | Chat system services | ⚠️ Unknown | ⚠️ Needs audit |
| **AppPreviewControls** | None | N/A | ✅ N/A | ❌ None |
| **BrowserAutomationPanel** | None | N/A | ✅ N/A | ❌ None |
| **DocumentEditor** | None | N/A | ✅ N/A | ❌ None |
| **LogAnalysisDashboard** | Log data from Router/Log-Sentinels | Router API (8000) | ⚠️ Unknown | ⚠️ Needs audit |
| **LogSentinelsAnomalies** | Log anomalies | Log-Sentinels API (8000) | ⚠️ Unknown | ⚠️ Needs audit |
| **LogSentinelsSummaries** | Log summaries | Log-Sentinels API (8000) | ⚠️ Unknown | ⚠️ Needs audit |
| **ProblemsPanel** | Linter/compiler errors | Language server | ⚠️ Unknown | ⚠️ Needs audit |
| **ResourceMonitor** | System resources | System APIs | ⚠️ Unknown | ⚠️ Needs audit |
| **RouterPanel** | Router data | Router API (8000) | ⚠️ Unknown | ⚠️ Needs audit |
| **ToolQualityDashboard** | Tool quality metrics | MCP tools (5001) | ⚠️ Unknown | ⚠️ Needs audit |

---

## 🔄 **MIGRATION STRATEGY**

### **⚠️ CRITICAL UPDATE: Aether Chat as Central Hub**

**New Architecture:** All panels → Aether Chat → Services → Backend/Command Server

**Migration Path:**
1. **Phase 1:** Document current state (✅ Complete)
2. **Phase 2:** Create Aether Chat service API (⏳ In Progress)
3. **Phase 3:** Migrate panels to use Aether Chat (⏳ Planned)
4. **Phase 4:** Remove direct connections (⏳ Planned)

### **Data Source Categories:**

**1. Organization Data (File-Based) → Backend API (Port 8000) → Aether Chat**
- ✅ **Migrated:** System indexes, system maps, SUPER_INDEX
- ⏳ **In Progress:** Goal tree, hierarchical navigation
- ⏳ **Next:** Route through Aether Chat

**2. AIM-OS Core Systems (Dynamic) → Command Server/MCP (Port 5001) → Aether Chat**
- ⚠️ **Keep MCP:** CMC, HHNI, VIF, SEG, TCS, CAS, APOE
- **Reason:** These are dynamic systems that need MCP tool execution
- **Status:** Mock data currently, will connect when AIM-OS systems are running
- ⏳ **Next:** Route through Aether Chat

**3. Hybrid Approach (Via Aether Chat):**
- **Organization data:** Backend API (file-based, static) → Aether Chat → Panels
- **AIM-OS systems:** Command Server/MCP (dynamic, requires execution) → Aether Chat → Panels
- **Aether Chat:** Central orchestrator, unified interface, context management

---

## 📋 **CONNECTION STATUS SUMMARY**

### **✅ Fully Connected (Backend API)**
- SystemIndexBrowserPanel
- SystemMapPanel
- SuperIndexPanel

### **⏳ Needs Connection (Backend API)**
- MasterIndexPanel (if file-based)
- GoalTreePanel (needs creation)
- HierarchicalNavigationPanel (needs creation)

### **⚠️ Using Mock Data (MCP Tools) - Will Route Through Aether Chat**
- MemoryBrowser
- TimelineView
- ContextWeb
- SystemStatus
- DebugConsolePanel
- CodeEditor
- FileTree
- OutlinePanel
- TerminalPanel
- DocumentationExplorerPanel
- NLTagsExplorerPanel

**Note:** These panels currently use MCP tools via `useAIMOS` hooks. They will:
1. Connect when AIM-OS core systems are running
2. Route through Aether Chat (central orchestrator)
3. Benefit from unified interface, context management, quality gates

**Migration:** Direct MCP → Aether Chat → MCP (with orchestration)

### **❓ Needs Audit**
- AIChatManagement
- LogAnalysisDashboard
- LogSentinelsAnomalies
- LogSentinelsSummaries
- ProblemsPanel
- ResourceMonitor
- RouterPanel
- ToolQualityDashboard

---

## 🔧 **SERVICE ARCHITECTURE**

### **Service Layer (Current - Legacy):**

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Panels                      │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│                    Service Layer                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Organization │  │  AIM-OS Core │  │   Other      │ │
│  │   Services   │  │   Services   │  │  Services    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│  • SystemIndex    │  • CMCService   │  • ICIPService │ │
│  • SystemMap      │  • HHNIService   │  • Sandbox     │ │
│  • SuperIndex     │  • VIFService    │  • CodeExec    │ │
│  • GoalTree       │  • SEGService    │  • CodeValid   │ │
│  • HierNav        │  • TCSService    │                │ │
│                   │  • CASService    │                │ │
│                   │  • APOEService   │                │ │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│  Backend API     │                  │  Command Server  │
│  (Port 8000)     │                  │  (Port 5001)     │
│                  │                  │                  │
│  • File-based    │                  │  • MCP Tools     │
│  • Static data   │                  │  • Dynamic exec  │
│  • Direct API    │                  │  • Via Cursor    │
└──────────────────┘                  └──────────────────┘
```

### **Service Layer (Proposed - Aether Chat Central):**

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend Panels                      │
│  (Code Editor, File Tree, Timeline, Context Web, etc.) │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────┐
│              AETHER CHAT (Central Hub)                   │
│  ┌────────────────────────────────────────────────────┐ │
│  │  • Advanced LLM Integration                        │ │
│  │  • Deep Search (HHNI, ICIP, Semantic)             │ │
│  │  • Thinking Modes (Reasoning, Planning, Exec)    │ │
│  │  • Multi-Agent Coordination                        │ │
│  │  • Quality Gates (VIF, SDF-CVF)                   │ │
│  │  • Context Management (CMC, TCS)                  │ │
│  │  • Knowledge Synthesis (SEG)                      │ │
│  │  • Cognitive Monitoring (CAS)                     │ │
│  │  • Plan Execution (APOE)                          │ │
│  └────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┴───────────────────┐
        │                                       │
        ▼                                       ▼
┌──────────────────┐                  ┌──────────────────┐
│  Backend API     │                  │  Command Server  │
│  (Port 8000)     │                  │  (Port 5001)     │
│                  │                  │                  │
│  • Organization  │                  │  • AIM-OS Core   │
│  • File-based    │                  │  • MCP Tools     │
│  • Static data   │                  │  • Dynamic exec  │
└──────────────────┘                  └──────────────────┘
```

**Migration:** Panels → Aether Chat → Services → Backend/Command Server

---

## 📝 **MAINTENANCE CHECKLIST**

### **When Adding New Panel:**
- [ ] Document data requirements in this inventory
- [ ] Identify data source (Backend API vs MCP)
- [ ] Create/use appropriate service
- [ ] Update connection status
- [ ] Add to panel list above

### **When Adding New Data Source:**
- [ ] Document endpoint/service in "Data Sources" section
- [ ] Update service architecture diagram
- [ ] Identify which panels need this data
- [ ] Update panel requirements

### **When Migrating:**
- [ ] Update connection status
- [ ] Document migration in "Migration Strategy"
- [ ] Update service architecture
- [ ] Test connection
- [ ] Remove mock data if applicable

---

## 🎯 **PRIORITY ACTIONS**

### **P0: Critical (Blocking)**
1. ✅ **Complete Backend API endpoints** - DONE
2. ✅ **Create organization services** - DONE
3. ✅ **Connect organization panels** - DONE (SuperIndexPanel)
4. ⏳ **Create Aether Chat service API** - Central orchestrator interface
5. ⏳ **Document Aether Chat integration** - How panels connect through hub

### **P1: High (Important)**
1. ⏳ **Create GoalTreePanel** - Use GoalTreeService
2. ⏳ **Create HierarchicalNavigationPanel** - Use HierarchicalNavigationService
3. ⏳ **Audit unknown panels** - Identify data requirements

### **P2: Medium (Enhancement)**
1. ⏳ **Connect MasterIndexPanel** - If file-based, use Backend API
2. ⏳ **Document all MCP tool usage** - Complete inventory
3. ⏳ **Create connection status dashboard** - Visual tracking

### **P3: Low (Nice-to-Have)**
1. ⏳ **Automated connection testing** - Verify all connections
2. ⏳ **Connection health monitoring** - Track connection status
3. ⏳ **Migration automation** - Tools to migrate panels

---

## 📊 **CONNECTION HEALTH**

**Last Updated:** 2025-01-27

**Overall Status:**
- ✅ **Connected:** 3 panels (SystemIndexBrowserPanel, SystemMapPanel, SuperIndexPanel)
- ⚠️ **Mock Data:** 11 panels (using MCP hooks, will connect when AIM-OS running)
- ❌ **Missing:** 2 panels (GoalTreePanel, HierarchicalNavigationPanel - need creation)
- ❓ **Unknown:** 8 panels (need audit)

**Data Sources:**
- ✅ **Backend API:** 7 endpoints (all organization data)
- ⚠️ **Command Server:** 84 MCP tools (core AIM-OS systems)
- ✅ **Services:** 18 services (5 organization, 13 AIM-OS/other)

**Total Panels:** 59 panels (from panelRegistry.ts)
- **Left:** 6 panels
- **Right:** 10 panels (including organization panels)
- **Bottom:** 8 panels
- **Main/View:** 9 panels
- **Additional:** 26 panels (including organization, documentation, etc.)

---

## 🔄 **LIVING DOCUMENT PROTOCOL**

### **When to Update:**

**Immediate Updates Required:**
- ✅ Adding new panel → Add to panel list, document data requirements
- ✅ Adding new data source → Add to data sources, update services
- ✅ Connecting panel → Update connection status
- ✅ Migrating panel → Update migration status, document changes

**Regular Updates:**
- ⏳ Weekly review → Check connection health, update status
- ⏳ After major changes → Update architecture diagrams
- ⏳ When AIM-OS systems go live → Update mock data status

### **Update Process:**

1. **Identify Change:** New panel, new data source, connection change
2. **Update Inventory:** Add/modify entry in appropriate section
3. **Update Quick Reference:** Update status summary
4. **Update Coordination Board:** Post update notification
5. **Test Connection:** Verify connection works
6. **Mark Complete:** Update status, remove from "needs" lists

### **Version Control:**

- **Track Changes:** Use Git commits with clear messages
- **Date Updates:** Update "Last Updated" date
- **Change Log:** Document significant changes in coordination board

---

**Status:** Living Document - Update as connections change  
**Next Review:** When adding new panels or data sources  
**Maintainers:** @Sev (organization data), @Alex (MCP/Command Server), @Sage (panels)  
**Quick Reference:** See `DATA_CONNECTION_QUICK_REFERENCE.md`

