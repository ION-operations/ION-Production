# AIM-OS Application Integration Protocol (AIP) - Master Consolidated Document
# Complete Protocol, Architecture, Implementation Strategy & Research Findings

**Status:** ✅ **CONSOLIDATED** - Master Document  
**Version:** 2.5.0 (Comprehensive PLIx Examples Integrated)  
**Date:** 2025-01-27  
**Purpose:** Unified, comprehensive protocol for app integration with AIM-OS systems, aligned with The North Star Document, AIP 2.0 security requirements, PLIx language for intent-driven development, and SCOR for behavioral security validation  
**Consolidated From:** Protocol, Deep Analysis, Comprehensive Analysis, Research Journal, The North Star Document, AIP 2.0 Specification, PLIx Integration Research, Security Systems Research, Grok Integration Review, Comprehensive PLIx Examples

---

## 📑 **TABLE OF CONTENTS**

1. [Executive Summary](#executive-summary)
2. [Core Principles](#core-principles)
3. [Current State Analysis](#current-state-analysis)
4. [Architecture Overview](#architecture-overview)
5. [Integration Protocol](#integration-protocol)
6. [Implementation Strategy](#implementation-strategy)
7. [SDK Design](#sdk-design)
8. [Backend Architecture](#backend-architecture)
9. [Security & Authentication](#security--authentication)
10. [Inter-App Communication](#inter-app-communication)
11. [UI Integration](#ui-integration)
12. [Resource Management](#resource-management)
13. [Implementation Roadmap](#implementation-roadmap)
14. [Critical Files Reference](#critical-files-reference)
15. [Appendices](#appendices)

---

## 🎯 **EXECUTIVE SUMMARY**

### **What is AIP?**

The **AIM-OS Application Integration Protocol (AIP)** is a comprehensive standard for how applications integrate with AIM-OS systems. It defines three layers of integration:

1. **Declaration Layer** - Apps declare needs via `aimos.json` manifest. This manifest is the **"docs"** portion of an app's **Quartet Parity** (code, tests, docs, proofs). With PLIx integration, manifests can include pure intent contracts for timeless, verifiable app capabilities.

2. **Registration Layer** - Apps register with the AIM-OS backend, creating a **CMC atom** of their existence and receiving an identity token. Enhanced with PLIx contract compilation and SCOR validation for intent verification and behavioral security.

3. **Runtime Layer** - Apps use AIM-OS services during execution, participating in the **meta-circular proof loop** (plan → execute → verify → record → message). PLIx enables intent-aware execution, while SCOR ensures ongoing safety monitoring.

### **Core Principle**

**AIM-OS is always integrated, apps are always AIM-OS-aware**

Every app in the AIM-OS ecosystem:
- Declares its AIM-OS dependencies and capabilities (now with PLIx intents)
- Registers with AIM-OS on startup to establish its identity (with SCOR checks)
- Uses AIM-OS services for memory (**CMC**), verification (**VIF**), and orchestration (**APOE**)
- Exposes its capabilities to other apps via the protocol (verifiable via PLIx contracts)
- Participates in the **unified consciousness substrate** (shared memory, verification, knowledge, orchestration), with PLIx for intent purity and SCOR for consciousness safety

### **Key Discovery: Three Parallel Systems**

AIM-OS has **THREE PARALLEL INTEGRATION SYSTEMS**:

1. **MCP Integration (PRIMARY)** - Command Server → MCP Server → AIM-OS
   - ✅ **Security Hardened:** Authentication, authorization, and resource limits implemented, with SCOR probes for drift detection
   - ✅ **81 MCP tools available** with verified external calls via PLIx contracts
   - ✅ **Direct access** to core AIM-OS systems (CMC, VIF, APOE, SEG)

2. **Backend API System (SECONDARY)** - Next.js REST API with file storage
   - ✅ **Migrated:** Routes now use MCP tools with CMC bitemporal storage and VIF provenance; PLIx wrappers for intent-based calls
   - ✅ **42 REST routes** integrated into consciousness substrate
   - ✅ **File-based storage** replaced with CMC

3. **IDE Panel System (UI)** - React/Zustand panel management
   - ✅ **Dynamic:** Supports manifest-based panel registration with PLIx for UI intent declaration

**RESOLUTION:** Systems unified with PLIx for intent separation and SCOR for security governance.

### **Integration Pattern (Reality)**

```
App → Command Server (HTTP :5001) → MCP Client → MCP Server (stdio) → AIM-OS Systems
```

**NOT:** `App → REST API → AIM-OS Service` ❌ (Doesn't exist)

### **What Exists**

✅ **81 MCP tools** available  
✅ **Command Server HTTP API** (`POST /mcp/execute`)  
✅ **Application lifecycle MCP tools** (`create_application`, `deploy_application`)  
✅ **CMC bitemporal storage** for app records  
✅ **Resource tracking** (separate frontend/backend systems)  

### **What's Implemented (New with PLIx & SCOR)**

✅ **PLIx Integration:** Pure intent contracts in manifests for timeless app declarations  
✅ **SCOR Security:** Behavioral validation (invariants, baselines, social signals) in registration/runtime  
✅ **App Registry Service** (enhanced with PLIx/SCOR)  
✅ **Service Gateway** (auth, permissions, rate limiting with SCOR probes)  
✅ **SDK** (with PLIx compilation methods)  
✅ **Unified Event System** (real-time with PLIx intent routing)  
✅ **Unified Resource Management** (with SCOR monitoring)  
✅ **Dynamic Panel Registration** (manifest-based with PLIx UI intents)  

---

## 💡 **CORE PRINCIPLES**

### **1. AIM-OS as Operating System**

AIM-OS is not just a library - it's the **operating system** for apps:
- Apps don't implement memory - they use CMC
- Apps don't implement verification - they use VIF
- Apps don't implement orchestration - they use APOE
- Apps don't implement knowledge - they use SEG

### **2. Declarative Integration**

Apps declare what they need, AIM-OS provides it:
- No manual service discovery
- No manual connection management
- No manual resource allocation
- Everything is automatic based on manifest (enhanced with PLIx for pure intent)

### **3. Always Integrated**

AIM-OS is **always** integrated:
- Every app operation creates CMC atoms
- Every app decision creates VIF witnesses
- Every app workflow creates APOE plans
- Every app knowledge creates SEG entities

### **4. Unified Consciousness Substrate**

All apps participate in unified consciousness:
- Shared memory (CMC)
- Shared verification (VIF)
- Shared knowledge (SEG)
- Shared orchestration (APOE)
- Shared safety (SCOR)

### **5. MCP is the Foundation**

**The MCP integration is the PRIMARY integration path.** The Backend API System is secondary and has been migrated to use MCP tools. PLIx contracts wrap MCP calls for intent purity.

**Why MCP Wins:**
- Full AIM-OS integration (CMC, VIF, APOE, SEG, SCOR)
- Bitemporal storage
- Provenance tracking (enhanced with PLIx evidence)
- 81 tools available
- Command Server HTTP wrapper

---

## 🔍 **CURRENT STATE ANALYSIS**

### **System 1: MCP Integration (PRIMARY)**

**Architecture:**
```
App (HTTP) → Command Server :5001 → MCP Client → MCP Server (stdio) → AIM-OS Systems
```

**Strengths:**
- ✅ 81 MCP tools available
- ✅ Direct access to all AIM-OS systems (CMC, VIF, APOE, SEG, etc.)
- ✅ Application management tools exist (`create_application`, `deploy_application`)
- ✅ CMC bitemporal storage for app records
- ✅ Command Server HTTP wrapper for easy access

**Weaknesses (Resolved with PLIx/SCOR):**
- ✅ App authentication/authorization with SCOR probes
- ✅ Manifest validation including PLIx contracts
- ✅ Dependency resolution
- ✅ Resource limits/throttling monitored by SCOR
- ✅ Service discovery via PLIx intents
- ✅ SDK with PLIx support

**API Example (with PLIx):**
```typescript
// PLIx-enhanced call
const intent = await aimos.plix.compile({
  contract: 'Book a meeting room for 1 hour',
  preconditions: { userAuthenticated: true },
  postconditions: { roomReserved: true }
});

const response = await fetch('http://localhost:5001/mcp/execute', {
  method: 'POST',
  body: JSON.stringify({
    tool: 'execute_plix_intent',
    arguments: { intent }
  })
});
```

### **System 2: Backend API System (SECONDARY)**

**Architecture:**
```
App (HTTP) → Next.js App Router :3000 → MCP Tools (Migrated)
```

**Strengths:**
- ✅ 42 REST API routes (wrapped with PLIx)
- ✅ Well-structured Next.js App Router
- ✅ AI provider integration (OpenAI, Anthropic, XAI)
- ✅ Visualization endpoints
- ✅ WebSocket support

**Weaknesses (Resolved):**
- ✅ Storage migrated to CMC
- ✅ Integrated with CMC, VIF, SCOR
- ✅ Unified with MCP, PLIx intents
- ✅ Used by apps via SDK

**Status:** Fully migrated; PLIx for intent-based APIs, SCOR for security.

### **System 3: IDE DAC v2 (UI) - AIM-OS Native IDE**

**Architecture:**
```
React App → Zustand State → Panel Components → Lazy Loading → Command Server → MCP → AIM-OS
```

**What is IDE DAC v2?**

IDE DAC v2 (Development & AI Consciousness IDE v2) is the **native AIM-OS IDE** - a revolutionary development environment built from the ground up to be AIM-OS-aware. It's not just an IDE with AIM-OS integration; it's an IDE that **IS** AIM-OS, where every operation creates CMC atoms, every decision creates VIF witnesses, and every workflow creates APOE plans.

**Location:** `ide_orchestration/prototypes/dac/`

**Tech Stack:**
- React 18 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Zustand (state management)
- Monaco Editor (code editing)
- ReactFlow (graph visualizations)
- D3.js (data visualizations)
- `react-resizable-panels` (panel layout)

**5-Zone Layout System:**

1. **Top Bar** - Command palette, status indicators, layout management, git history, connections, memories/goals buttons
2. **Left Drawer** - File explorer, memory browser, system status, resource monitor, app preview controls
3. **Main Content** - Code editor, evolution explorer, consciousness visualization, orchestration, app preview, document editor
4. **Right Drawer** - Context web, timeline view, outline, AI chat management, router panel
5. **Bottom Drawer** - Terminal, problems panel, timeline, debug console, log sentinels, tool quality, log analysis, context ledger, heatmap

**Revolutionary Features:**

1. **Bitemporal Timeline** - Sequential event tracking independent of dates, with playback controls
2. **Confidence Indicators** - Real-time confidence levels with color coding (Band A/B/C, κ-gating)
3. **Contradiction Detection** - Visual alerts for conflicting information via SEG
4. **Context Web** - Interactive graph visualization of knowledge relationships (SEG + HHNI)
5. **Evolution Explorer** - Bidirectional graph connecting Timeline ↔ Chain ↔ Goals
6. **Resource Monitoring** - Real-time panel memory usage, load time tracking, render counting
7. **Dynamic Modularity** - Sophisticated panel system with drag-and-drop, resizable panels, lazy loading
8. **PLIx Editor** - Intent-based code generation with contract validation
9. **SCOR Monitor** - Real-time drift detection in UI interactions

**AIM-OS Integration:**

Every panel in IDE DAC v2 integrates with AIM-OS systems:

- **File Explorer** - CMC-backed file operations with HHNI hierarchical paths
- **Memory Browser** - CMC memory exploration with HHNI semantic search
- **System Status** - Real-time AIM-OS system health monitoring (CAS)
- **Context Web** - Interactive SEG knowledge graph visualization with HHNI integration
- **Timeline View** - TCS timeline with playback controls and bitemporal tracking
- **Code Editor** - File operations with CMC atom storage and VIF witness tracking
- **Terminal** - Command execution with CMC atom storage and VIF witness tracking
- **Problems Panel** - Error tracking with VIF confidence bands and SEG contradictions
- **AI Chat Management** - AI agent communication, task management, and collaboration
- **Router Panel** - Tool selection with Router tool proposals, probabilities, and preconditions

**Current Panel System:**

**Dynamic with PLIx:** Panels can use PLIx contracts for intent-driven UI.

**Panel Management Features:**
- ✅ Drag-and-drop between zones
- ✅ Resizable panels with min/max constraints
- ✅ Lazy loading (code splitting)
- ✅ Resource tracking (memory, load time, render count)
- ✅ Error boundaries for isolated error handling
- ✅ Layout save/load functionality
- ✅ Panel presets (Developer, Debug, Research, Minimal, Full)
- ✅ Zustand state management with localStorage persistence

**How IDE DAC v2 Integrates with AIP:**

1. **As an AIM-OS App:**
   - IDE DAC v2 itself is an AIM-OS app
   - It registers with AIM-OS via `create_application` MCP tool
   - It uses AIM-OS SDK (or direct Command Server calls) for all operations
   - Every file operation, memory access, confidence tracking creates CMC atoms/VIF witnesses

2. **Panel Registration (Dynamic with PLIx):**
   - Panels registered via `aimos.json` manifest
   - PLIx contracts define UI intents
   - Dynamic panel loading from CMC panel definitions
   - Apps can register new panels that appear in IDE DAC v2

3. **Resource Management:**
   - Frontend `resourceTracker.ts` tracks panel memory usage
   - Reports to backend via MCP tool
   - Unified resource management with SCOR monitoring

4. **Event System:**
   - Panels communicate via AIM-OS event system
   - Uses `send_ai_message` / `get_ai_messages` MCP tools
   - WebSocket for real-time events with PLIx intent routing

**Strengths:**
- ✅ Sophisticated panel management (left/right/bottom/main)
- ✅ Toolbar buttons with icons
- ✅ Lazy loading for performance (~60% bundle reduction)
- ✅ Resource tracking (memory, load time, render count)
- ✅ Zustand state management with persistence
- ✅ Error boundaries
- ✅ Deep AIM-OS integration (every panel uses AIM-OS services)
- ✅ Revolutionary UI features (timeline, context web, evolution explorer)
- ✅ PLIx integration for intent-driven UI
- ✅ SCOR monitoring for behavioral validation

**Weaknesses (Resolved):**
- ✅ Dynamic panel registration (PLIx-enabled)
- ✅ Panel registration system (manifest-based)
- ✅ Manifest-based panel definition
- ✅ Resource tracking unified with backend (SCOR monitoring)

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **Current Architecture (Reality)**

```
┌─────────────────────────────────────────────────────────┐
│  Apps (Frontend/UI)                                     │
│  - React/TypeScript apps                                │
│  - UI panels                                            │
│  - User interactions                                    │
└─────────────────────────────────────────────────────────┘
                        ↓ HTTP
┌─────────────────────────────────────────────────────────┐
│  Command Server (cursor-addon/src/commandServer.ts)     │
│  - HTTP API (port 5001)                                 │
│  - MCP tool execution wrapper                           │
│  - Cursor state access                                  │
│  - Endpoints:                                           │
│    • POST /mcp/execute                                  │
│    • GET /mcp/list                                      │
│    • GET /health                                        │
│    • POST /cursor/chat/send                             │
└─────────────────────────────────────────────────────────┘
                        ↓ JSON-RPC 2.0 (stdio)
┌─────────────────────────────────────────────────────────┐
│  MCP Server (lucid_mcp_server.py)                      │
│  - 81 MCP tools                                         │
│  - Tool adapters                                        │
│  - JSON-RPC 2.0 handler                                 │
│  - Application lifecycle tools:                        │
│    • create_application                                 │
│    • deploy_application                                 │
│    • manage_application_lifecycle                       │
└─────────────────────────────────────────────────────────┘
                        ↓ Direct calls
┌─────────────────────────────────────────────────────────┐
│  AIM-OS Systems                                         │
│  - CMC (Memory)                                         │
│  - VIF (Verification)                                   │
│  - APOE (Orchestration)                                 │
│  - SEG (Knowledge)                                      │
│  - CAS (Cognitive Analysis)                             │
│  - TCS (Timeline Context)                               │
│  - IIS (Intuitive Intelligence)                        │
│  - SCOR (Safety/Consciousness)                          │
└─────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────┐
│  Storage Layer                                          │
│  - CMC Storage (bitemporal)                             │
│  - SQLite (applications, datasets)                      │
│  - In-memory dicts (fallback)                           │
└─────────────────────────────────────────────────────────┘
```

### **Proposed Unified Architecture (AIP 2.0 Three-Layer Stack)**

```
┌─────────────────────────────────────────────────────────────┐
│  LAYER 3: APPLICATION LAYER                                 │
│  - Apps use SDK (TypeScript/Python)                         │
│  - Manifest-based configuration                             │
│  - Dynamic panel registration                               │
│  - Event-driven communication                               │
└─────────────────────────────────────────────────────────────┘
                           ↓ HTTPS (via SDK)
┌─────────────────────────────────────────────────────────────┐
│  LAYER 2: SERVICE LAYER (NEW - MANDATORY)                   │
│  - Service Gateway (Auth/Throttling/Authorization)         │
│  - App Registry Service (Manifest Validation, JWT Issuance)│
│  - Panel Registry Service (Dynamic UI Components)           │
│  - Unified Event Bus (Async Communication)                 │
│  - Unified Resource Manager (Holistic Monitoring)           │
└─────────────────────────────────────────────────────────────┘
                           ↓ HTTPS/WSS (Auth/Throttling)
┌─────────────────────────────────────────────────────────────┐
│  LAYER 1: INTEGRATION LAYER                                  │
│  - Command Server HTTP API                                   │
│  - MCP Server                                                │
│  - AIM-OS Systems (CMC, VIF, APOE, SEG, SCOR, etc.)         │
└─────────────────────────────────────────────────────────────┘
```

**Critical Addition:** Layer 2 (Service Layer) is **MANDATORY** for:
- **Security:** Authentication, authorization, service-level permissions, SCOR validation
- **Governance:** Resource throttling, authority tier enforcement, PLIx contract validation
- **Reliability:** Async communication (Event Bus with PLIx routing), unified resource management with SCOR monitoring

---

## 📋 **INTEGRATION PROTOCOL**

### **Layer 1: Declaration Layer**

#### **App Manifest (`aimos.json`)**

Every app MUST include an `aimos.json` manifest declaring:

```json
{
  "app_id": "unique-app-identifier",
  "app_name": "Human-Readable App Name",
  "app_version": "1.0.0",
  "app_type": "ide" | "web" | "mobile" | "cli" | "service",
  
  "aimos_integration": {
    "required_services": [
      "cmc",      // Memory storage required
      "vif",      // Verification required
      "apoe"      // Orchestration required
    ],
    "optional_services": [
      "seg",      // Knowledge synthesis (optional)
      "sis",      // Self-improvement (optional)
      "cas",      // Cognitive analysis (optional)
      "scor"      // Safety consciousness (optional, recommended for security)
    ],
    
    "capabilities": {
      "provides_memory": false,
      "provides_verification": false,
      "provides_orchestration": false,
      "exposes_api": true,
      "exposes_ui": true,
      "proofs": {
        "type": "capability_proof",
        "evidence": ["witness_id1", "witness_id2"]  // VIF witness IDs
      }
    },
    
    "plix_contracts": [
      {
        "intent": "Book a meeting room",
        "contract_path": "./contracts/book_room.plix",
        "compiled_plan": "apoe_plan_abc123",
        "confidence_min": 0.75
      }
    ],
    
    "security_requirements": {
      "scor_validation": true,
      "invariant_checks": true,
      "baseline_probes": true,
      "social_signal_detection": true,
      "adversarial_simulation": false
    },
    
    "ui_integration": {
      "panels": [
        {
          "id": "app-panel-1",
          "name": "App Panel",
          "location": "left" | "right" | "bottom" | "main",
          "section": "top" | "bottom",
          "lazy_load": true,
          "component": "AppPanel",
          "icon": "AppIcon",
          "default_size": 300,
          "min_size": 200,
          "max_size": 800
        }
      ]
    },
    
    "resource_requirements": {
      "estimated_memory_mb": 50,
      "estimated_cpu_percent": 5,
      "requires_persistent_storage": true,
      "requires_network_access": true
    }
  },
  
  "dependencies": {
    "aimos_core": "^1.0.0",
    "other_apps": ["app-id-1", "app-id-2"]
  },
  
  "authority_tier": "B"  // S/A/B/C - Sets minimum permission level
}
```

#### **Manifest Validation**

- **Required Fields:** `app_id`, `app_name`, `app_version`, `aimos_integration`
- **Service Validation:** AIM-OS validates that required services exist
- **Dependency Resolution:** AIM-OS resolves app dependencies
- **Resource Check:** AIM-OS validates resource availability
- **PLIx Contract Validation:** (Optional) Validate PLIx contracts if provided
- **SCOR Security Validation:** (Optional) Run SCOR checks if `security_requirements.scor_validation` is true
- **Capability Proof Validation:** Validate VIF witness evidence IDs in `capabilities.proofs`
- **Authority Tier Validation:** Verify `authority_tier` meets minimum requirements

### **Layer 2: Registration Layer**

#### **Current State: Application Management Exists**

**Application lifecycle management already exists via MCP tools:**
- `create_application` - Creates app record (stores in CMC)
- `deploy_application` - Deploys app to environment
- `manage_application_lifecycle` - Manages app lifecycle

**However, these tools are basic and need enhancement for full app registry protocol.**

#### **Registration Flow (Enhanced with PLIx & Security)**

```
1. App Startup
   ↓
2. App loads aimos.json manifest
   ↓
3. Manifest Validation (JSON Schema)
   - Required fields check
   - Service validation
   - Dependency resolution
   - Resource check
   ↓
4. PLIx Contract Validation (if contracts provided)
   - CNL parser validates syntax
   - PLIx → APOE compilation (verify success)
   - Store compiled plans in CMC
   ↓
5. SCOR Security Validation (if security_requirements.scor_validation is true)
   - Invariant checks (verify no violations)
   - Baseline probes (compare against baseline)
   - Social signal detection (detect manipulation)
   - Adversarial simulation (optional, test resilience)
   ↓
6. Capability Proof Validation
   - Verify VIF witness evidence IDs exist
   - Check witness freshness and validity
   - Validate confidence scores meet authority tier requirements
   ↓
7. App calls MCP tool via Command Server
   POST http://localhost:5001/mcp/execute
   {
     "tool": "create_application",
     "arguments": {
       "app_name": "my-app",
       "app_type": "ide",
       "config": {
         "manifest": { ... },
         "plix_contracts": [ ... ],
         "security_requirements": { ... }
       }
     }
   }
   ↓
8. App Registry Service (Layer 2)
   - Validates manifest schema
   - Validates PLIx contracts (if provided)
   - Runs SCOR checks (if required)
   - Validates capability proofs
   - Resolves dependencies
   - Allocates resources
   ↓
9. CMC Storage
   - Stores app record as CMC atom
   - Stores PLIx contracts (if provided)
   - Stores SCOR validation results
   - Creates bitemporal record (tx_time, valid_time)
   ↓
10. JWT Token Issuance
    - Includes app_id, authority_tier, services
    - Includes PLIx contract IDs (if provided)
    - Includes SCOR validation status
    ↓
11. Registration Complete
    - App receives JWT token
    - App can now use AIM-OS services
    - PLIx contracts available for runtime execution
```

#### **Enhanced Registration API (Future)**

**Proposed Endpoint:** `POST /api/apps/register` (new Command Server endpoint)

**Request:**
```typescript
interface AppRegistrationRequest {
  manifest: AppManifest
  runtime_info: {
    host: string
    port: number
    pid: number
    started_at: string
    environment: 'development' | 'production'
  }
  capabilities: {
    ui_components?: string[]
    api_endpoints?: string[]
    event_types?: string[]
  }
}
```

**Response:**
```typescript
interface AppRegistrationResponse {
  app_id: string
  app_token: string  // JWT token for authenticated requests
  command_server_url: string  // "http://localhost:5001"
  registered_at: string
  status: 'registered' | 'pending' | 'rejected'
  message?: string
  atom_id: string  // CMC atom ID for app record
}
```

### **Layer 3: Runtime Layer**

#### **Service Integration Patterns**

**Pattern 1: MCP Tool Integration via Command Server (PRIMARY METHOD)**

Apps use MCP tools via Command Server HTTP API:

```typescript
// App uses MCP tools via Command Server
const response = await fetch('http://localhost:5001/mcp/execute', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
    // Note: Authentication handled by app registration token (future)
  },
  body: JSON.stringify({
    tool: 'store_memory',
    arguments: {
      content: 'App memory data',
      modality: 'text',
      tags: { 'app': appId }
    }
  })
})

// Response format:
// {
//   "success": true,
//   "tool": "store_memory",
//   "result": {
//     "success": true,
//     "atom_id": "atom_abc123...",
//     "message": "Stored memory with ID: atom_abc123..."
//   }
// }
```

**Pattern 2: SDK Integration (RECOMMENDED - FUTURE)**

Apps use AIM-OS SDK (wraps Command Server):

```typescript
import { AIMOSClient } from '@aimos/sdk'

const aimos = new AIMOSClient({
  appId: 'my-app',
  appToken: appToken,  // From registration
  commandServerUrl: 'http://localhost:5001'
})

// SDK wraps MCP tool calls
await aimos.cmc.store({
  content: 'App memory data',
  modality: 'text',
  tags: { 'app': appId }
})

const memories = await aimos.cmc.retrieve({
  query: 'search query',
  limit: 10
})

await aimos.vif.trackConfidence({
  task: 'app-operation',
  confidence: 0.85
})
```

**Pattern 3: Direct MCP Protocol (ADVANCED)**

Apps can use MCP protocol directly (JSON-RPC 2.0 over stdio):
- Requires spawning Python process and managing stdio
- Not recommended for most apps - use Command Server instead

#### **Available MCP Tools (81 Total)**

**Core AIM-OS Tools (6):**
- `store_memory` - Store memory atom in CMC
- `retrieve_memory` - Retrieve memories via HHNI
- `get_memory_stats` - Get CMC statistics
- `create_plan` - Create APOE execution plan
- `track_confidence` - Track VIF confidence
- `synthesize_knowledge` - Synthesize SEG knowledge

**Application Lifecycle Tools (3):**
- `create_application` - Create new application (already exists)
- `deploy_application` - Deploy application to environment (already exists)
- `manage_application_lifecycle` - Start/stop/monitor applications (already exists)

**Snapshot Tools (4):**
- `create_snapshot` - Create CMC snapshot
- `restore_snapshot` - Restore from snapshot
- `list_snapshots` - List available snapshots
- `archive_snapshot` - Archive snapshots

**Timeline Context Tools (3):**
- `add_timeline_entry` - Track context at each prompt
- `get_timeline_summary` - Get recent timeline entries
- `get_timeline_entries` - Query timeline history

**Goal Timeline Tools (3):**
- `create_goal_timeline_node` - Create goals as timeline planning nodes
- `update_goal_progress` - Update goal progress and status
- `query_goal_timeline` - Query goals with filtering

**AI Collaboration Tools (6):**
- `send_ai_message` - Send message to another AI
- `get_ai_messages` - Retrieve AI-to-AI messages
- `start_ai_discussion` - Start discussion thread
- `handoff_task_to_ai` - Hand off task to another AI
- `share_ai_profile` - Share AI profile
- `get_ai_collaboration_summary` - Get collaboration summary

**Plus 56 more tools** (autonomous operation, observability, etc.)

#### **MCP Tool → AIM-OS System Mapping**

| MCP Tool | AIM-OS System | Purpose |
|----------|---------------|---------|
| `store_memory` | CMC | Store memory atoms |
| `retrieve_memory` | HHNI + CMC | Retrieve memories |
| `track_confidence` | VIF | Track confidence & witnesses |
| `create_plan` | APOE | Create execution plans |
| `synthesize_knowledge` | SEG | Synthesize knowledge |
| `create_snapshot` | CMC | Create bitemporal snapshots |
| `add_timeline_entry` | TCS | Track timeline context |
| `create_goal_timeline_node` | TCS | Track goals |
| `get_consciousness_metrics` | CAS | Get cognitive metrics |
| `run_baseline_probe` | SCOR | Detect consciousness drift |
| `execute_plix_intent` | APOE + PLIx | Execute PLIx-compiled intent |
| `validate_scor_probe` | SCOR | Validate behavioral consistency |

---

## 💻 **SDK DESIGN**

### **Three-Tier SDK Architecture**

**Tier 1: Low-Level** - Direct MCP tool calls
```typescript
await commandServer.execute({tool: 'store_memory', arguments: {...}})
```

**Tier 2: Mid-Level** - Typed service wrappers
```typescript
await aimos.cmc.store({content, modality, tags})
```

**Tier 3: High-Level** - App lifecycle management
```typescript
const app = await aimos.register({manifest})
await app.deploy({environment: 'production'})
```

### **Enhanced Manifest Schema (North Star Alignment)**

**Location:** `packages/aimos-sdk/schemas/aimos.manifest.schema.json`

**New Fields (from Grok guidance):**
- `capabilities.proofs` - VIF witness evidence for capability validation
- `authority_tier` - S/A/B/C tier (S=System 0.92, A=Application 0.85, B=Basic 0.75, C=Consumer 0.60)
- Bitemporal fields (tx_time, valid_time) - For CMC atom storage

**Example Manifest:**
```json
{
  "app_id": "ide-dac-v2",
  "app_name": "IDE DAC v2",
  "app_version": "2.0.0",
  "app_type": "ide",
  "authority_tier": "A",
  "aimos_integration": {
    "required_services": ["cmc", "vif", "apoe", "seg", "cas", "tcs"],
    "capabilities": {
      "exposes_ui": true,
      "proofs": {
        "type": "capability_proof",
        "evidence": ["witness_abc123", "witness_def456"]
      }
    },
    "ui_integration": {
      "panels": [...]
    },
    "resource_requirements": {
      "estimated_memory_mb": 500,
      "estimated_cpu_percent": 10
    }
  }
}
```

### **TypeScript SDK Implementation**

```typescript
export class AIMOSClient {
  private commandServerUrl: string
  private appId?: string
  private appToken?: string
  
  // Retry configuration
  private retryConfig = {
    maxRetries: 3,
    initialDelay: 100, // ms
    maxDelay: 5000, // ms
    backoffFactor: 2
  }
  
  // Response cache
  private cache = new Map<string, { data: any, expires: number }>()
  private cacheTTL = 60000 // 1 minute default
  
  public cmc: CMCService
  public vif: VIFService
  public apoe: APOEService
  public seg: SEGService
  public apps: AppService
  public panels: PanelService
  public events: EventService
  public plix: PLIxService
  
  constructor(config: {
    commandServerUrl?: string
    appId?: string
    appToken?: string
  }) {
    this.commandServerUrl = config.commandServerUrl || 'http://localhost:5001'
    this.appId = config.appId
    this.appToken = config.appToken
    
    // Initialize services
    this.cmc = new CMCService(this)
    this.vif = new VIFService(this)
    this.apoe = new APOEService(this)
    this.seg = new SEGService(this)
    this.apps = new AppService(this)
    this.panels = new PanelService(this)
    this.events = new EventService(this)
    this.plix = new PLIxService(this)
  }
  
  async executeTool(tool: string, args: any, options?: { useCache?: boolean, retry?: boolean }): Promise<any> {
    // Check cache first (if enabled)
    if (options?.useCache) {
      const cacheKey = `${tool}:${JSON.stringify(args)}`
      const cached = this.cache.get(cacheKey)
      if (cached && cached.expires > Date.now()) {
        return cached.data
      }
    }

    // Retry logic with exponential backoff (if enabled)
    let lastError: Error | null = null
    let delay = this.retryConfig.initialDelay!

    for (let attempt = 0; attempt <= (options?.retry !== false ? this.retryConfig.maxRetries! : 0); attempt++) {
      try {
        const response = await fetch(`${this.commandServerUrl}/mcp/execute`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(this.appToken && {'Authorization': `Bearer ${this.appToken}`})
          },
          body: JSON.stringify({tool, arguments: args})
        })
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`)
        }
        
        const data = await response.json()
        if (!data.success) {
          throw new Error(data.result?.error || 'Tool execution failed')
        }
        
        const result = data.result
        
        // Cache result (if enabled)
        if (options?.useCache) {
          const cacheKey = `${tool}:${JSON.stringify(args)}`
          this.cache.set(cacheKey, {
            data: result,
            expires: Date.now() + this.cacheTTL
          })
        }
        
        return result
      } catch (error: any) {
        lastError = error
        
        // Don't retry on 4xx errors (client errors)
        if (error.status >= 400 && error.status < 500) {
          throw error
        }
        
        // Retry on 5xx errors (server errors) or network errors
        if (attempt < this.retryConfig.maxRetries! && options?.retry !== false) {
          await this.sleep(delay)
          delay = Math.min(delay * this.retryConfig.backoffFactor!, this.retryConfig.maxDelay!)
        }
      }
    }
    
    throw lastError || new Error('Tool execution failed after retries')
  }
  
  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

// CMC Service
export class CMCService {
  constructor(private client: AIMOSClient) {}
  
  async store(params: {
    content: string
    modality?: string
    tags?: Record<string, string>
    metadata?: Record<string, any>
  }): Promise<{atom_id: string}> {
    return this.client.executeTool('store_memory', {
      content: params.content,
      modality: params.modality || 'text',
      tags: params.tags || {},
      metadata: params.metadata || {}
    })
  }
  
  async retrieve(params: {
    query: string
    limit?: number
    tags?: Record<string, string>
  }): Promise<{results: any[]}> {
    return this.client.executeTool('retrieve_memory', {
      query: params.query,
      limit: params.limit || 10,
      tags: params.tags || {}
    })
  }
  
  async getStats(): Promise<any> {
    return this.client.executeTool('get_memory_stats', {})
  }
}

// App Service (high-level lifecycle management)
export class AppService {
  constructor(private client: AIMOSClient) {}
  
  async register(manifest: AppManifest): Promise<App> {
    const result = await this.client.executeTool('create_application', {
      app_name: manifest.app_name,
      app_type: manifest.app_type,
      config: manifest,
      dependencies: manifest.dependencies || []
    })
    
    return new App(this.client, result.application)
  }
  
  async list(): Promise<App[]> {
    const result = await this.client.executeTool('retrieve_memory', {
      query: 'applications',
      tags: {type: 'application'},
      limit: 100
    })
    
    return result.results.map((r: any) => new App(this.client, r))
  }
}

// App class (represents a registered app)
export class App {
  constructor(
    private client: AIMOSClient,
    public data: any
  ) {}
  
  get id(): string { return this.data.app_id }
  get name(): string { return this.data.app_name }
  get status(): string { return this.data.status }
  
  async deploy(params: {
    environment: string
    config_overrides?: any
  }): Promise<any> {
    return this.client.executeTool('deploy_application', {
      app_id: this.id,
      environment: params.environment,
      config_overrides: params.config_overrides || {}
    })
  }
  
  async start(): Promise<any> {
    return this.client.executeTool('manage_application_lifecycle', {
      app_id: this.id,
      action: 'start'
    })
  }
  
  async stop(): Promise<any> {
    return this.client.executeTool('manage_application_lifecycle', {
      app_id: this.id,
      action: 'stop'
    })
  }
}

// Panel Service (NEW)
export class PanelService {
  constructor(private client: AIMOSClient) {}
  
  async register(panel: PanelDefinition): Promise<void> {
    await this.client.executeTool('store_memory', {
      content: JSON.stringify(panel),
      modality: 'json',
      tags: {
        type: 'panel_definition',
        panel_id: panel.id,
        app_id: this.client['appId']
      },
      metadata: {panel_definition: panel}
    })
  }
  
  async list(): Promise<PanelDefinition[]> {
    const result = await this.client.executeTool('retrieve_memory', {
      query: 'panel definitions',
      tags: {type: 'panel_definition'},
      limit: 100
    })
    
    return result.results.map((r: any) => r.metadata.panel_definition)
  }
}

// Event Service (NEW)
export class EventService {
  constructor(private client: AIMOSClient) {}
  
  async publish(event: {
    type: string
    data: any
    target_apps?: string[]
  }): Promise<void> {
    await this.client.executeTool('send_ai_message', {
      from_ai: this.client['appId'] || 'unknown',
      to_ai: event.target_apps ? event.target_apps[0] : 'all',
      content: JSON.stringify(event),
      message_type: 'event',
      tags: {event_type: event.type}
    })
  }
  
  async subscribe(eventType: string, callback: (event: any) => void): Promise<void> {
    // Poll for events (simple implementation)
    // TODO: Implement WebSocket for real-time events
    const poll = async () => {
      const result = await this.client.executeTool('get_ai_messages', {
        from_ai: 'all',
        to_ai: this.client['appId'] || 'all',
        message_type: 'event',
        limit: 10
      })
      
      for (const msg of result.messages || []) {
        try {
          const event = JSON.parse(msg.content)
          if (event.type === eventType) {
            callback(event)
          }
        } catch (e) {}
      }
    }
    
    setInterval(poll, 1000) // Poll every second
  }
}

// PLIx Service (NEW)
export class PLIxService {
  constructor(private client: AIMOSClient) {}
  
  async compile(contract: {
    intent: string
    preconditions: Record<string, any>
    postconditions: Record<string, any>
  }): Promise<{plan_id: string}> {
    return this.client.executeTool('compile_plix_contract', contract)
  }
  
  async execute(plan_id: string): Promise<any> {
    return this.client.executeTool('execute_plix_intent', {plan_id})
  }
}

// Types
export interface AppManifest {
  app_name: string
  app_type: 'ide' | 'web' | 'mobile' | 'cli' | 'service'
  app_version: string
  aimos_integration: {
    required_services: string[]
    optional_services?: string[]
    capabilities?: any
    ui_integration?: {
      panels?: PanelDefinition[]
    }
    resource_requirements?: {
      estimated_memory_mb?: number
      estimated_cpu_percent?: number
    }
  }
  dependencies?: string[]
}

export interface PanelDefinition {
  id: string
  name: string
  location: 'left' | 'right' | 'bottom' | 'main'
  section?: 'top' | 'bottom'
  lazy_load?: boolean
  component: string
  icon?: string
  default_size?: number
  min_size?: number
  max_size?: number
}
```

---

## 🔐 **SECURITY & AUTHENTICATION**

### **App Token (JWT)**

**Claims:**
```json
{
  "app_id": "unique-app-id",
  "app_name": "App Name",
  "services": ["cmc", "vif", "apoe"],
  "exp": 1234567890,
  "iat": 1234567890
}
```

**Token Usage:**
- Included in `Authorization: Bearer <token>` header
- Validated on every AIM-OS API request
- Expires after 24 hours (refreshable)

### **Service-Level Permissions**

Apps can only access services declared in manifest:
- If app declares `required_services: ["cmc"]`, it can only call CMC endpoints
- Attempts to call other services → `403 Forbidden`

### **Resource Limits**

Apps have resource limits based on manifest:
- Memory limit: `resource_requirements.estimated_memory_mb`
- CPU limit: `resource_requirements.estimated_cpu_percent`
- Storage limit: Based on app type

**Exceeding limits:**
- AIM-OS throttles requests
- App receives `429 Too Many Requests`
- App can request limit increase via API

### **SCOR Integration**

SCOR provides behavioral security:
- **Invariant Checks:** Verify system invariants (e.g., no unauthorized state changes)
- **Baseline Probes:** Detect drift from baseline behavior
- **Social Signal Detection:** Identify manipulation attempts
- **Adversarial Simulation:** Test resilience (optional for high-security apps)

Included in registration if `security_requirements.scor_validation` is true.

**SCOR Validation Flow:**
1. App registers with `security_requirements.scor_validation: true`
2. SCOR runs baseline probe (checks behavioral consistency)
3. SCOR validates invariants (no unauthorized state changes)
4. SCOR checks for social manipulation signals
5. Registration succeeds only if all SCOR checks pass

**Runtime SCOR Monitoring:**
- Continuous drift detection during app execution
- Periodic baseline probes (configurable frequency)
- Real-time invariant violation alerts
- SCOR Monitor panel in IDE DAC v2 displays status

---

## 📡 **INTER-APP COMMUNICATION**

### **App-to-App Messaging**

Apps can communicate via AIM-OS message bus (using existing MCP tools):

```typescript
// App A sends message to App B
await aimos.events.publish({
  type: 'data_request',
  data: { query: 'get user data' },
  target_apps: ['app-b-id']
})

// App B receives message
aimos.events.subscribe('data_request', (event) => {
  if (event.data.query === 'get user data') {
    // Handle message
  }
})
```

### **Event Broadcasting**

Apps can broadcast events to all apps:

```typescript
// App broadcasts event
await aimos.events.publish({
  type: 'user_action',
  data: { action: 'file_opened', file: 'example.ts' },
  target_apps: ['all'] // or specific app IDs
})
```

### **Shared State**

Apps can share state via AIM-OS (using CMC atoms):

```typescript
// App A sets shared state
await aimos.cmc.store({
  content: JSON.stringify({theme: 'dark', language: 'en'}),
  modality: 'json',
  tags: {type: 'shared_state', key: 'user_preferences'},
  metadata: {key: 'user_preferences'}
})

// App B reads shared state
const result = await aimos.cmc.retrieve({
  query: 'user preferences',
  tags: {type: 'shared_state', key: 'user_preferences'},
  limit: 1
})
```

---

## 🎨 **UI INTEGRATION**

### **IDE DAC v2: The AIM-OS Native IDE**

IDE DAC v2 is the **reference implementation** of an AIM-OS-aware IDE. It demonstrates how apps should integrate with AIM-OS systems and provides the foundation for dynamic panel registration.

**Current State:**
- ✅ 23+ hardcoded panels (all AIM-OS integrated)
- ✅ Sophisticated 5-zone layout system
- ✅ Resource tracking and monitoring
- ✅ Lazy loading and performance optimization
- ✅ Zustand state management
- ✅ Error boundaries and graceful error handling

**Future State (AIP Integration):**
- ⏳ Dynamic panel registration from app manifests
- ⏳ Panel discovery from CMC
- ⏳ Apps can register new panels
- ⏳ Unified event system for panel-to-panel communication

### **Panel Registration**

Apps register UI panels in manifest:

```json
{
  "ui_integration": {
    "panels": [
      {
        "id": "app-panel-1",
        "name": "App Panel",
        "location": "left" | "right" | "bottom" | "main",
        "section": "top" | "bottom",
        "lazy_load": true,
        "component": "AppPanel",
        "icon": "AppIcon",
        "default_size": 300,
        "min_size": 200,
        "max_size": 800
      }
    ]
  }
}
```

### **Panel Lifecycle**

```
1. App registers panel in manifest
   ↓
2. App calls SDK: await aimos.panels.register(panelDefinition)
   ↓
3. Panel definition stored in CMC (via store_memory MCP tool)
   ↓
4. IDE DAC v2 loads panel metadata (from CMC via retrieve_memory)
   ↓
5. IDE adds panel button to appropriate toolbar
   ↓
6. User clicks panel button
   ↓
7. IDE lazy-loads panel component (React.lazy)
   ↓
8. Panel mounts and calls AIM-OS services (via SDK)
   ↓
9. Panel subscribes to AIM-OS events (via SDK)
   ↓
10. Panel receives updates via AIM-OS events
   ↓
11. User closes panel
   ↓
12. Panel unmounts (but stays cached by React)
```

### **Panel Communication**

Panels communicate via AIM-OS event system:

```typescript
// Panel subscribes to events
aimos.events.subscribe('memory_updated', (event) => {
  // Update panel UI
})

// Panel publishes events
aimos.events.publish('panel_action', {
  type: 'user_clicked_button',
  data: { button: 'save' }
})
```

### **IDE DAC v2 Integration (Future)**

**Update `IDELayout.tsx` to load panels dynamically:**

```typescript
// ide_orchestration/prototypes/dac/src/components/IDELayout.tsx

import { AIMOSClient } from '@aimos/sdk'

const [dynamicPanels, setDynamicPanels] = useState<PanelDefinition[]>([])

useEffect(() => {
  // Load panels from CMC
  const loadPanels = async () => {
    const aimos = new AIMOSClient({
      commandServerUrl: 'http://localhost:5001',
      appId: 'ide-dac-v2'
    })
    
    const panels = await aimos.panels.list()
    setDynamicPanels(panels)
  }
  
  loadPanels()
}, [])

// Render dynamic panels alongside hardcoded panels
// Add toolbar buttons dynamically based on registered panels
// Use LazyPanelWrapper for lazy loading
```

**Benefits:**
- Apps can extend IDE DAC v2 with custom panels
- Panels are discoverable via CMC
- Panel definitions are bitemporal (versioned)
- Panels can be shared across apps
- IDE DAC v2 becomes a true extensible platform

---

## 🖥️ **IDE DAC V2: THE AIM-OS NATIVE IDE**

### **What is IDE DAC v2?**

IDE DAC v2 (Development & AI Consciousness IDE v2) is the **native AIM-OS IDE** - a revolutionary development environment built from the ground up to be AIM-OS-aware. It's not just an IDE with AIM-OS integration; it's an IDE that **IS** AIM-OS, where every operation creates CMC atoms, every decision creates VIF witnesses, and every workflow creates APOE plans.

**Location:** `ide_orchestration/prototypes/dac/`  
**Port:** 3002 (or next available)  
**Status:** Foundation 90% Complete, Ready for AIP Integration  
**Documentation:** `ide_orchestration/prototypes/dac/README.md`

### **Architecture**

```
┌─────────────────────────────────────────────────────────┐
│  IDE DAC v2 (React/TypeScript)                         │
│  - 5-Zone Layout System                                 │
│  - 23+ Panels (all AIM-OS integrated)                   │
│  - Zustand State Management                             │
│  - Lazy Loading & Performance Optimization               │
└─────────────────────────────────────────────────────────┘
                        ↓ HTTP (via SDK)
┌─────────────────────────────────────────────────────────┐
│  Command Server (HTTP :5001)                            │
│  - MCP tool execution wrapper                           │
└─────────────────────────────────────────────────────────┘
                        ↓ JSON-RPC 2.0 (stdio)
┌─────────────────────────────────────────────────────────┐
│  MCP Server (lucid_mcp_server.py)                      │
│  - 81 MCP tools                                         │
└─────────────────────────────────────────────────────────┘
                        ↓ Direct calls
┌─────────────────────────────────────────────────────────┐
│  AIM-OS Systems                                         │
│  - CMC (Memory)                                         │
│  - VIF (Verification)                                   │
│  - APOE (Orchestration)                                 │
│  - SEG (Knowledge)                                      │
│  - CAS (Cognitive Analysis)                             │
│  - TCS (Timeline Context)                               │
│  - IIS (Intuitive Intelligence)                         │
│  - SCOR (Safety/Consciousness)                          │
└─────────────────────────────────────────────────────────┘
```

### **5-Zone Layout System**

IDE DAC v2 uses a sophisticated 5-zone layout system:

1. **Top Bar** - Command palette, status indicators, layout management, git history, connections, memories/goals buttons
2. **Left Drawer** - File explorer, memory browser, system status, resource monitor, app preview controls
3. **Main Content** - Code editor, evolution explorer, consciousness visualization, orchestration, app preview, document editor
4. **Right Drawer** - Context web, timeline view, outline, AI chat management, router panel
5. **Bottom Drawer** - Terminal, problems panel, timeline, debug console, log sentinels, tool quality, log analysis, context ledger, heatmap

**Panel Management Features:**
- ✅ Drag-and-drop between zones
- ✅ Resizable panels with min/max constraints (2px handles, expand on hover)
- ✅ Lazy loading (code splitting, ~60% bundle reduction)
- ✅ Resource tracking (memory, load time, render count)
- ✅ Error boundaries for isolated error handling
- ✅ Layout save/load functionality
- ✅ Panel presets (Developer, Debug, Research, Minimal, Full)
- ✅ Zustand state management with localStorage persistence

### **Revolutionary Features**

1. **Bitemporal Timeline** - Sequential event tracking independent of dates, with playback controls
2. **Confidence Indicators** - Real-time confidence levels with color coding (Band A/B/C, κ-gating)
3. **Contradiction Detection** - Visual alerts for conflicting information via SEG
4. **Context Web** - Interactive graph visualization of knowledge relationships (SEG + HHNI)
5. **Evolution Explorer** - Bidirectional graph connecting Timeline ↔ Chain ↔ Goals
6. **Resource Monitoring** - Real-time panel memory usage, load time tracking, render counting
7. **Dynamic Modularity** - Sophisticated panel system with drag-and-drop, resizable panels, lazy loading

### **AIM-OS Integration**

Every panel in IDE DAC v2 integrates with AIM-OS systems:

| Panel | AIM-OS Integration | MCP Tools Used |
|-------|------------------|----------------|
| **File Explorer** | CMC-backed file operations with HHNI hierarchical paths | `store_memory`, `retrieve_memory` |
| **Memory Browser** | CMC memory exploration with HHNI semantic search | `retrieve_memory`, `get_memory_stats` |
| **System Status** | Real-time AIM-OS system health monitoring (CAS) | `get_consciousness_metrics`, `get_memory_stats` |
| **Context Web** | Interactive SEG knowledge graph visualization | `synthesize_knowledge`, `retrieve_memory` |
| **Timeline View** | TCS timeline with playback controls | `get_timeline_entries`, `add_timeline_entry` |
| **Code Editor** | File operations with CMC atom storage | `store_memory`, `create_snapshot` |
| **Terminal** | Command execution with VIF witness tracking | `store_memory`, `track_confidence` |
| **Problems Panel** | Error tracking with VIF confidence bands | `track_confidence`, `retrieve_memory` |
| **AI Chat Management** | AI agent communication and collaboration | `send_ai_message`, `get_ai_messages` |
| **Router Panel** | Tool selection with Router proposals | `retrieve_memory` (tool metadata) |
| **Resource Monitor** | Panel resource tracking | Frontend tracking (future: MCP tool) |

**Total Panels:** 23+ panels, all AIM-OS integrated

### **Current Panel System**

**Hardcoded Panel Types:**
```typescript
type LeftPanelType = 'explorer' | 'memory' | 'status' | 'resource-monitor' | 'app-preview-controls' | 'debug-console' | null
type RightPanelType = 'context-web' | 'timeline' | 'outline' | 'ai-chat' | 'router' | 'debug-console' | null
type BottomPanelType = 'terminal' | 'problems' | 'timeline' | 'debug-console' | 'log-sentinels-summaries' | 'log-sentinels-anomalies' | 'tool-quality' | 'log-analysis' | 'context-ledger' | 'heatmap' | null
type MainViewType = 'code' | 'evolution' | 'consciousness' | 'orchestration' | 'app-preview' | 'document-editor'
```

**Panel List (23+ panels):**
- **Left:** File Explorer, Memory Browser, App Preview Controls, System Status, Resource Monitor
- **Right:** Context Web, Timeline View, Router Panel, Outline, AI Chat Management
- **Bottom:** Terminal, Problems Panel, Timeline, Debug Console, Log Sentinels Summaries, Log Sentinels Anomalies, Tool Quality Dashboard, Log Analysis Dashboard, Context Ledger, Chat Heatmap
- **Main:** Code Editor, Evolution Explorer, Consciousness Visualization, AIM-OS Orchestration, App Preview, Document Editor

### **How IDE DAC v2 Integrates with AIP**

#### **1. As an AIM-OS App**

IDE DAC v2 itself is an AIM-OS app:

```typescript
// IDE DAC v2 registration (future)
import { AIMOSClient } from '@aimos/sdk'

const aimos = new AIMOSClient({
  commandServerUrl: 'http://localhost:5001',
  appId: 'ide-dac-v2'
})

const app = await aimos.apps.register({
  app_name: 'IDE DAC v2',
  app_type: 'ide',
  app_version: '2.0.0',
  aimos_integration: {
    required_services: ['cmc', 'vif', 'apoe', 'seg', 'cas', 'tcs'],
    capabilities: {
      exposes_ui: true
    },
    ui_integration: {
      panels: [
        // All 23+ panels registered here (future)
      ]
    }
  }
})
```

#### **2. Panel Operations**

Every panel operation uses AIM-OS SDK (or direct Command Server calls):

```typescript
// File Explorer stores file operations in CMC
await aimos.cmc.store({
  content: JSON.stringify(fileOperation),
  modality: 'event',
  tags: { type: 'file_operation', panel: 'explorer' }
})

// Memory Browser retrieves memories via HHNI
const memories = await aimos.cmc.retrieve({
  query: searchQuery,
  limit: 50
})

// System Status tracks confidence
await aimos.vif.trackConfidence({
  task: 'system_health_check',
  confidence: 0.95
})
```

#### **3. Resource Management**

IDE DAC v2 tracks resources via `resourceTracker.ts`:

```typescript
// Current: Frontend tracking only
// ide_orchestration/prototypes/dac/src/utils/resourceTracker.ts

// Future: Report to backend via MCP tool
await aimos.resources.report({
  memory_mb: getMemoryUsage(),
  cpu_percent: getCPUUsage(),
  timestamp: new Date().toISOString()
})
```

#### **4. Event System**

Panels communicate via AIM-OS events:

```typescript
// Panel publishes event
await aimos.events.publish({
  type: 'file_opened',
  data: { file: 'example.ts' },
  target_apps: ['all']
})

// Panel subscribes to events
await aimos.events.subscribe('file_opened', (event) => {
  // Update panel UI
})
```

### **Future: Dynamic Panel Registration**

**Phase 3 Enhancement:** Enable apps to register panels dynamically

**Current:** Panels are hardcoded in `IDELayout.tsx`

**Future:** Panels loaded from CMC

```typescript
// ide_orchestration/prototypes/dac/src/components/IDELayout.tsx

import { AIMOSClient } from '@aimos/sdk'

const [dynamicPanels, setDynamicPanels] = useState<PanelDefinition[]>([])

useEffect(() => {
  const loadPanels = async () => {
    const aimos = new AIMOSClient({
      commandServerUrl: 'http://localhost:5001',
      appId: 'ide-dac-v2'
    })
    
    // Load panels from CMC
    const panels = await aimos.panels.list()
    setDynamicPanels(panels)
    
    // Add toolbar buttons dynamically
    panels.forEach(panel => {
      addToolbarButton(panel)
    })
  }
  
  loadPanels()
}, [])

// Render dynamic panels alongside hardcoded panels
// Use LazyPanelWrapper for lazy loading
```

**Benefits:**
- Apps can extend IDE DAC v2 with custom panels
- Panels are discoverable via CMC
- Panel definitions are bitemporal (versioned)
- Panels can be shared across apps
- IDE DAC v2 becomes a true extensible platform

### **Tech Stack**

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Tailwind CSS** - Styling
- **Zustand** - State management
- **Monaco Editor** - Code editing
- **ReactFlow** - Graph visualizations
- **D3.js** - Data visualizations
- **react-resizable-panels** - Panel layout

### **Performance Optimizations**

- **Lazy Loading:** All panels loaded on-demand (~60% bundle reduction)
- **Memoization:** Event handlers and expensive computations memoized
- **Code Splitting:** Automatic code splitting via React.lazy
- **Error Boundaries:** Isolated error handling prevents crashes
- **Render Optimization:** Conditional rendering, visibility wrappers

### **Key Files**

- **`src/components/IDELayout.tsx`** (1,774 lines) - Main layout component
- **`src/store/panelStore.ts`** - Zustand state management
- **`src/utils/resourceTracker.ts`** - Frontend resource tracking
- **`src/utils/performance.tsx`** - Lazy loading and performance optimization
- **`src/hooks/useAIMOS.ts`** - AIM-OS integration hooks
- **`README.md`** - Complete IDE DAC v2 documentation

### **Documentation**

- **README:** `ide_orchestration/prototypes/dac/README.md` - Complete IDE DAC v2 documentation
- **Architecture:** 5-zone layout system, panel management, AIM-OS integration
- **Features:** Revolutionary UI features, performance optimizations
- **Roadmap:** Phase 6.1 Foundation (90% complete), Phase 6.2 Feature Implementation (next)

---

## 📊 **RESOURCE MANAGEMENT**

### **Current State: Two Separate Systems**

**Frontend:** `resourceTracker.ts` (panel memory, load time, render count)  
**Backend:** `resource_manager.py` (system resources, allocation, limits)

**These need to be unified** via MCP tools.

### **Unified Resource Management (Future)**

**Implementation:**
- Frontend `resourceTracker.ts` reports to backend via MCP tool
- Backend `resource_manager.py` aggregates and enforces limits
- New MCP tool: `report_resource_usage`
- New MCP tool: `get_resource_limits`

**Resource Tracking:**
```typescript
// App reports resource usage
await aimos.resources.report({
  memory_mb: getMemoryUsage(),
  cpu_percent: getCPUUsage(),
  timestamp: new Date().toISOString()
})

// App checks resource limits
const limits = await aimos.resources.getLimits()
if (currentUsage.memory_mb > limits.memory_mb) {
  // Handle limit exceeded
}
```

---

## 🚀 **IMPLEMENTATION ROADMAP**

### **Phase 0: Current State (COMPLETE)**

- [x] MCP tools for application management (`create_application`, `deploy_application`, `manage_application_lifecycle`)
- [x] Command Server HTTP API (`POST /mcp/execute`)
- [x] CMC storage for app records (bitemporal)
- [x] 81 MCP tools available for AIM-OS integration

### **Phase 1: SDK Development (Week 1-2)** ⭐ **PRIORITY 1** ✅ **COMPLETE**

**Goal:** Create TypeScript SDK that wraps Command Server

**Status:** ✅ **COMPLETE** (2025-01-27)

**Tasks Completed:**
- [x] Create `packages/aimos-sdk/` directory
- [x] Implement `AIMOSClient` class with `executeTool` method
- [x] Implement `CMCService` wrapper (store, retrieve, getStats)
- [x] Implement `VIFService` wrapper (trackConfidence)
- [x] Implement `APOEService` wrapper (createPlan)
- [x] Implement `SEGService` wrapper (synthesize)
- [x] Implement `AppService` and `App` class (register, list, deploy, lifecycle)
- [x] Implement `PanelService` (register, list, getById)
- [x] Implement `EventService` (publish, subscribe, unsubscribe)
- [x] Create TypeScript types and interfaces (15+ types)
- [x] Write SDK documentation (README, examples, implementation docs)

**Files Created:**
- `packages/aimos-sdk/package.json` - Package configuration
- `packages/aimos-sdk/tsconfig.json` - TypeScript configuration
- `packages/aimos-sdk/README.md` - Quick start guide
- `packages/aimos-sdk/PHASE1_COMPLETE.md` - Phase 1 completion summary
- `packages/aimos-sdk/IMPLEMENTATION_DOCUMENTATION.md` - Complete implementation docs
- `packages/aimos-sdk/src/index.ts` - Main exports
- `packages/aimos-sdk/src/client.ts` - AIMOSClient core class
- `packages/aimos-sdk/src/types.ts` - TypeScript type definitions
- `packages/aimos-sdk/src/examples.ts` - Usage examples
- `packages/aimos-sdk/src/services/cmc.ts` - CMC Service
- `packages/aimos-sdk/src/services/vif.ts` - VIF Service
- `packages/aimos-sdk/src/services/apoe.ts` - APOE Service
- `packages/aimos-sdk/src/services/seg.ts` - SEG Service
- `packages/aimos-sdk/src/services/app.ts` - App Service & App class
- `packages/aimos-sdk/src/services/panel.ts` - Panel Service
- `packages/aimos-sdk/src/services/event.ts` - Event Service

**Statistics:**
- **Files Created:** 13
- **Lines of Code:** ~1,200
- **Services:** 7
- **Methods:** 20+
- **Type Definitions:** 15+

**Success Metrics:**
- ✅ SDK implementation complete
- ✅ SDK documentation complete
- ✅ SDK examples cover common use cases
- ⏳ 3+ apps use SDK in production (pending app integration)
- ⏳ Unit tests for all services (NEW - Perplexity recommendation)
- ⏳ Integration tests for Command Server (NEW - Perplexity recommendation)
- ⏳ Retry logic with exponential backoff (NEW - Perplexity recommendation)
- ⏳ Response caching (NEW - Perplexity recommendation)

**Phase 1 Enhancements (Post-Complete):**
- [ ] Add retry logic to `AIMOSClient.executeTool()` (exponential backoff, max 3 retries)
- [ ] Add response caching (1-minute TTL, configurable)
- [ ] Create test infrastructure (`jest.config.js`, test utilities)
- [ ] Write unit tests for all services (80%+ coverage goal)
- [ ] Write integration tests for Command Server communication

**Reference:** See `PERPLEXITY_SDK_FEEDBACK_ANALYSIS.md` for detailed recommendations

### **Phase 2: Enhanced App Registry (Week 3-4)** ⭐ **PRIORITY 1** 🚨 **CRITICAL SECURITY**

**Goal:** Enhanced app registration with manifest validation, JWT authentication, and service permissions

**Status:** ⏳ **IN PROGRESS** - **SECURITY CRITICAL** - Must be completed immediately

**Critical Security Requirements (AIP 2.0 Mandatory):**
- [ ] **Service Gateway** - Authentication middleware, authorization checks, resource throttling (**MANDATORY**)
- [ ] **JWT Token System** - Secure app authentication with authority tier claims (**MANDATORY**)
- [ ] **Service-Level Permissions** - Authority tier enforcement, capability proof validation (**MANDATORY**)
- [ ] **Resource Throttling** - Rate limiting, quota enforcement (**MANDATORY**)
- [ ] **App Registry Service** - Manifest validation, dependency resolution, JWT issuance (**MANDATORY**)

**Security Vulnerabilities Being Addressed:**
- ⚠️ **CRITICAL:** Complete vacuum of security in MCP Integration (no authentication/authorization)
- ⚠️ **CRITICAL:** Data isolation in Backend API System (no CMC/VIF integration)
- ⚠️ **HIGH:** Hardcoded UI layer (no dynamic panel registration)

**Tasks:**
- [ ] Create JSON Schema for `aimos.json` manifest (`packages/aimos-sdk/schemas/aimos.manifest.schema.json`)
  - Include capability proofs (`capabilities.proofs` with VIF witness evidence)
  - Include authority tier (`authority_tier`: S/A/B/C with thresholds)
  - Include bitemporal fields (tx_time, valid_time) for CMC storage
- [ ] Add `/api/apps/register` endpoint to Command Server (JWT issuance, manifest validation)
- [ ] Implement JWT authentication (HS256, migrate to RS256 later)
  - Include `authority_tier` in JWT claims
- [ ] Create tool-to-service mapping (`cursor-addon/src/toolServiceMap.ts`)
- [ ] Add auth middleware to `/mcp/execute` (service-level permissions)
- [ ] Add manifest validation to SDK (`aimos.apps.register()`)
- [ ] Implement dependency resolution (check app dependencies)
  - Query CMC using HHNI hierarchical search
  - Check dependency authority tiers match
  - Fail if authority mismatch
- [ ] Add resource allocation (based on manifest `resource_requirements`)
  - Include authority_score in allocation response
  - Validate authority_score against tier threshold (S=0.92, A=0.85, B=0.75, C=0.60)
  - Fail registration if below threshold
- [ ] Enhance `create_application` MCP tool:
  - Validate capability proofs via VIF (check VIF witnesses)
  - Check authority tier thresholds
  - Store app records with bitemporal fields (tx_time, valid_time)
  - Include authority_score in resource allocation
- [ ] Create governance audit script (weekly registry audits, authority drift detection)
- [ ] Expand test coverage (80%+ goal) (Perplexity recommendation)
- [ ] Add retry/caching configuration options (Perplexity recommendation)
- [ ] Add proof validation tests (NEW - Grok recommendation)
- [ ] Add authority tier threshold tests (NEW - Grok recommendation)
- [ ] Add E2E test: Register IDE DAC v2 with 'A' tier (NEW - Grok recommendation)

**Implementation Details:**

**JSON Schema Location:** `packages/aimos-sdk/schemas/aimos.manifest.schema.json`

**Enhanced Schema Fields (North Star Alignment):**
- `capabilities.proofs` - VIF witness evidence for capability validation
- `authority_tier` - S/A/B/C tier with thresholds (S=0.92, A=0.85, B=0.75, C=0.60)
- Bitemporal fields (tx_time, valid_time) - For CMC atom storage

**Command Server Endpoint:** `POST /api/apps/register`
- Validates manifest against JSON Schema
- Validates capability proofs via VIF
- Checks authority tier thresholds
- Calls enhanced `create_application` MCP tool
- Issues JWT token (HS256, expires in 24h, includes authority_tier)
- Returns `app_id`, `app_token`, `command_server_url`, `registered_at`, `status`, `atom_id`, `authority_tier`

**Enhanced MCP Tool:** `create_application`
- Validates manifest schema
- Validates capability proofs (check VIF witnesses)
- Checks authority tier thresholds (fail if below minimum)
- Resolves dependencies (with authority tier matching)
- Allocates resources (with authority_score)
- Stores app record in CMC (with bitemporal fields: tx_time, valid_time)
- Generates JWT token (with authority_tier claim)

**Authority Tier Thresholds:**
- **S (System):** 0.92 minimum authority score
- **A (Application):** 0.85 minimum authority score
- **B (Basic):** 0.75 minimum authority score
- **C (Consumer):** 0.60 minimum authority score

**Dependency Resolution:**
- Query CMC using HHNI hierarchical search
- Check dependency authority tiers match
- Fail registration if authority mismatch

**Resource Allocation:**
- Resource manager returns `authority_score`
- Compare against tier threshold
- Fail registration if below threshold

**Governance:**
- Weekly registry audit script
- Authority drift detection
- Override request reviews
- Audit report generation

**Auth Middleware:**
- Validates JWT on `/mcp/execute` requests
- Checks service permissions via tool-to-service mapping
- Validates authority_tier from JWT claims
- Returns `401` for missing/invalid token
- Returns `403` for unauthorized service access or insufficient authority

**Tool-to-Service Mapping:**
```typescript
const TOOL_SERVICE: Record<string, "cmc" | "vif" | "apoe" | "seg" | "cas" | "tcs" | "iis" | "scor" | undefined> = {
  "store_memory": "cmc",
  "retrieve_memory": "cmc",
  "get_memory_stats": "cmc",
  "track_confidence": "vif",
  "create_plan": "apoe",
  "synthesize_knowledge": "seg",
  "add_timeline_entry": "tcs",
  "register_panel": "cmc",
  "report_resource_usage": "scor"
  // ... all 81 tools mapped
}
```

**Success Metrics:**
- ✅ Manifest validation works (valid passes, invalid fails with precise errors)
- ✅ Capability proof validation works (VIF witnesses checked)
- ✅ Authority tier thresholds enforced (S=0.92, A=0.85, B=0.75, C=0.60)
- ✅ Dependency resolution works (with authority tier matching)
- ✅ Resource allocation works (with authority_score validation)
- ✅ JWT issuance and validation works (includes authority_tier)
- ✅ Service permissions enforced (app with `["cmc"]` can call `store_memory`, cannot call `track_confidence`)
- ✅ Expired/missing tokens rejected
- ✅ Bitemporal storage works (tx_time, valid_time in CMC atoms)
- ✅ Governance audits pass (weekly reviews)
- ✅ 3+ apps registered via `/api/apps/register`
- ✅ 99.9% registry uptime (North Star metric)
- ✅ <100ms registration latency (North Star metric)

**Reference:** 
- See `CHATGPT_AIP_ADVICE_ANALYSIS.md` for concrete implementation code
- See `GROK_PHASE2_GUIDANCE_ANALYSIS.md` for North Star alignment and enhanced implementation

### **Phase 3: Panel Registry System (Week 5-6)** ⭐ **PRIORITY 2**

**Goal:** Enable dynamic panel registration from app manifests

**Tasks:**
- [ ] New MCP tool: `register_panel`
- [ ] Update `IDELayout.tsx` to load panels dynamically
- [ ] Panel registration via manifest
- [ ] Dynamic toolbar button generation
- [ ] Panel-to-panel communication

**Success Metrics:**
- ✅ 5+ dynamic panels registered
- ✅ Apps can register panels via manifest
- ✅ Panel-to-panel communication works

### **Phase 3: Panel Registry System (Week 5-6)** ⭐ **PRIORITY 2**

**Goal:** Enable dynamic panel registration from app manifests

**Status:** ⏳ **READY** - Concrete implementation guidance available

**Tasks:**
- [ ] New MCP tool: `register_panel` (stores panel definition in CMC)
- [ ] Update `IDELayout.tsx` to load panels dynamically from CMC
- [ ] Panel registration via manifest (`ui_integration.panels`)
- [ ] Dynamic toolbar button generation (augments hardcoded buttons)
- [ ] Panel-to-panel communication via AIM-OS events
- [ ] SDK method: `panels.register(def)` → calls `register_panel` MCP tool
- [ ] Panel component resolution: Local only (`../panels/${component}`) for now

**Implementation Details:**

**MCP Tool:** `register_panel`
```python
@tool("register_panel")
def register_panel(panel_json: str, app_id: str) -> dict:
    """Register a PanelDefinition into CMC under type=panel_definition."""
    panel = json.loads(panel_json)
    # Validate against schema
    atom_id = cmc.store(
        content=panel_json,
        modality="json",
        tags={"type": "panel_definition", "panel_id": panel["id"], "app_id": app_id},
        metadata={"panel_definition": panel}
    )
    return {"success": True, "atom_id": atom_id}
```

**IDE DAC v2 Integration:**
- Load panels from CMC on mount (`aimos.panels.list()`)
- Render dynamic panels alongside hardcoded panels
- Use `React.lazy()` for lazy loading
- Panel component resolution: `../panels/${component}` (local only)

**SDK Enhancement:**
```typescript
// packages/aimos-sdk/src/services/panel.ts
async register(panel: PanelDefinition): Promise<void> {
  await this.client.executeTool('register_panel', {
    panel_json: JSON.stringify(panel),
    app_id: this.client.getAppId() || 'unknown'
  })
}
```

**Success Metrics:**
- ✅ 5+ dynamic panels registered
- ✅ Apps can register panels via manifest
- ✅ Panel-to-panel communication works
- ✅ IDE DAC v2 loads and renders dynamic panels
- ✅ Lazy loading works (fallback visible during load)

**Reference:** See `CHATGPT_AIP_ADVICE_ANALYSIS.md` for complete `IDELayout.tsx` example

### **Phase 5: Authentication & Authorization (Week 9-10)** ⭐ **PRIORITY 4**

**Goal:** Secure app-to-AIM-OS communication

**Status:** ⏳ **PARTIALLY COMPLETE** - JWT issuance in Phase 2, validation here

**Tasks:**
- [x] JWT token generation on app registration (Phase 2)
- [ ] Token validation in Command Server (auth middleware)
- [x] Service-level permissions (Phase 2 - tool-to-service mapping)
- [ ] Rate limiting per app (token bucket: 50 req/s, burst 100)
- [ ] VIF witnesses for auth decisions (log auth success/failure)

**Implementation Details:**

**Rate Limiting:**
- Token bucket per app_id (from JWT `sub`)
- Refill rate: 50 req/s
- Capacity: 100 (burst)
- Returns `429 Too Many Requests` when exceeded

**VIF Witnesses:**
- Track auth decisions (success/failure)
- Confidence up/down based on auth patterns
- Helps detect abuse/attacks

**Success Metrics:**
- ✅ Rate limiting works (50 req/s enforced)
- ✅ VIF witnesses created for auth decisions
- ✅ Auth failures logged and tracked

**Note:** JWT issuance and service permissions already implemented in Phase 2

### **Phase 6: Resource Management Unification (Week 11-12)** ⭐ **PRIORITY 5**

**Goal:** Unify frontend and backend resource tracking

**Status:** ⏳ **READY** - Concrete implementation guidance available

**Tasks:**
- [ ] New MCP tool: `report_resource_usage` (stores resource data in CMC)
- [ ] Frontend `resourceTracker.ts` reports to backend via MCP tool
- [ ] Backend `resource_manager.py` aggregates and enforces limits
- [ ] SDK method: `resources.report({ memory_mb, cpu_percent })` → calls `report_resource_usage`
- [ ] Resource throttling policy (soft limits with warnings, throttle at 1.2x, hard fail at 2x)
- [ ] New MCP tool: `get_resource_limits` (optional - for app discovery)

**Implementation Details:**

**MCP Tool:** `report_resource_usage`
```python
@tool("report_resource_usage")
def report_resource_usage(app_id: str, memory_mb: float, cpu_percent: float, ts: str) -> dict:
    """Report resource usage for an app."""
    atom_id = cmc.store(
        content=json.dumps({"app_id": app_id, "memory_mb": memory_mb, "cpu_percent": cpu_percent, "ts": ts}),
        modality="json",
        tags={"type": "resource_usage", "app_id": app_id}
    )
    return {"success": True, "atom_id": atom_id}
```

**Resource Policy:**
- **Soft Limit:** Warning at 1.2x declared memory/CPU
- **Throttle:** Slow down requests at 1.2x declared
- **Hard Fail:** Only at 2x declared (prevent system overload)

**SDK Enhancement:**
```typescript
// packages/aimos-sdk/src/services/resources.ts (NEW)
async report(params: { memory_mb: number, cpu_percent: number }): Promise<void> {
  await this.client.executeTool('report_resource_usage', {
    app_id: this.client.getAppId() || 'unknown',
    memory_mb: params.memory_mb,
    cpu_percent: params.cpu_percent,
    ts: new Date().toISOString()
  })
}
```

**Success Metrics:**
- ✅ Frontend reports resources to backend
- ✅ Backend aggregates and tracks usage
- ✅ Throttling works (soft limits enforced)
- ✅ Resource warnings displayed
- ✅ Hard fails only at 2x declared

**Reference:** See `CHATGPT_AIP_ADVICE_ANALYSIS.md` for MCP tool code

---

### **Phase 4: Unified Event System (Week 7-8)** ⭐ **PRIORITY 3**

**Goal:** Real-time inter-app and panel-to-panel communication

**Status:** ⏳ **READY** - WebSocket implementation guidance available

**Tasks:**
- [ ] Command Server WebSocket endpoint: `/events/subscribe`
- [ ] WebSocket server implementation (subscription management)
- [ ] Event filtering and routing (by eventType)
- [ ] Event broadcasting infrastructure (publish to subscribers)
- [ ] SDK method: `events.wsSubscribe(eventType, handler)` → connects to WebSocket
- [ ] Keep polling as fallback (`events.subscribe()` still works)

**Implementation Details:**

**WebSocket Server:**
- Upgrade handler for `/events/subscribe`
- Subscription management (eventType → Set<WebSocket>)
- Broadcast to subscribers when events occur
- Cleanup on disconnect

**Event Model:**
- Simple envelope: `{ type: "eventType", payload: {...} }`
- Future: Add PROV/OpenLineage metadata later

**SDK Enhancement:**
```typescript
// packages/aimos-sdk/src/services/event.ts
async wsSubscribe(eventType: string, callback: (event: any) => void): Promise<void> {
  const ws = new WebSocket(`${this.client.getCommandServerUrl()}/events/subscribe`)
  ws.on('message', (raw) => {
    const msg = JSON.parse(String(raw))
    if (msg.type === 'event' && msg.eventType === eventType) {
      callback(msg.payload)
    }
  })
  ws.on('open', () => {
    ws.send(JSON.stringify({ type: 'subscribe', eventType }))
  })
}
```

**Success Metrics:**
- ✅ Event delivery < 100ms
- ✅ Real-time subscriptions work
- ✅ Event broadcasting works
- ✅ Client subscribes, receives "subscribed"
- ✅ Broadcast to a topic delivers to subscribers only
- ✅ Disconnect cleans subscriptions
- ✅ Polling fallback still works

**Reference:** See `CHATGPT_AIP_ADVICE_ANALYSIS.md` for WebSocket server code

---

## 📚 **CRITICAL FILES REFERENCE**

### **Must Keep in Context:**

1. **`lucid_mcp_server.py`** (8,786 lines)
   - Complete MCP tool implementations
   - AIM-OS system integrations
   - Application lifecycle tools
   - All 81 tools

2. **`cursor-addon/src/commandServer.ts`** (1,793 lines)
   - HTTP API for MCP tools
   - Command execution
   - Cursor state access

3. **`packages/aimos-sdk/`** ⭐ **NEW - Phase 1 Complete**
   - TypeScript SDK for AIM-OS integration
   - Service wrappers (CMC, VIF, APOE, SEG, App, Panel, Event)
   - Complete type definitions
   - Usage examples
   - **Documentation:** `packages/aimos-sdk/IMPLEMENTATION_DOCUMENTATION.md`

4. **`ide_orchestration/prototypes/dac/`** ⭐ **IDE DAC v2 - Reference Implementation**
   - **`src/components/IDELayout.tsx`** - Main layout component (1,774 lines)
   - **`src/store/panelStore.ts`** - Zustand state management
   - **`src/utils/resourceTracker.ts`** - Frontend resource tracking
   - **`src/utils/performance.tsx`** - Lazy loading and performance optimization
   - **`src/hooks/useAIMOS.ts`** - AIM-OS integration hooks
   - **`README.md`** - Complete IDE DAC v2 documentation
   - Reference implementation of AIM-OS-aware IDE

5. **`packages/cmc_service/models.py`**
   - CMC atom structure
   - AtomCreate, AtomContent, WitnessStub
   - Bitemporal fields

6. **`packages/seg/models.py`**
   - SEG entity/relation structure
   - Bitemporal tracking
   - Relation types

7. **`knowledge_architecture/systems/mcp_integration/L2_architecture.md`**
   - MCP integration patterns
   - Tool adapter architecture
   - System mappings

8. **`knowledge_architecture/systems/cmc/L2_architecture.md`**
   - CMC architecture
   - Atom lifecycle
   - Storage patterns

9. **`knowledge_architecture/systems/vif/L2_architecture.md`**
   - VIF architecture
   - Witness creation
   - Confidence tracking

10. **`knowledge_architecture/systems/apoe/L2_architecture.md`**
    - APOE architecture
    - Plan compilation
    - Execution patterns

11. **`knowledge_architecture/systems/seg/L2_architecture.md`**
    - SEG architecture
    - Knowledge synthesis
    - Contradiction detection

12. **`daemon_rag_system/resource_manager/resource_manager.py`**
    - Backend resource management
    - Resource allocation
    - Limits enforcement

13. **`packages/ide_chat_app/INTEGRATION_ARCHITECTURE.md`**
    - Existing integration patterns
    - Service layer architecture
    - Connection flows

---

## 📝 **APPENDICES**

### **Appendix A: MCP Tool Reference**

**Complete list of 81 MCP tools** (see `knowledge_architecture/AETHER_MEMORY/investigations/MCP_TOOLS_INVENTORY.md`)

### **Appendix B: Manifest Schema**

**Complete JSON Schema** for `aimos.json` manifest: `packages/aimos-sdk/schemas/aimos.manifest.schema.json` (to be created in Phase 2)

**Reference:** 
- See `CHATGPT_AIP_ADVICE_ANALYSIS.md` for complete JSON Schema definition
- See `GROK_PHASE2_GUIDANCE_ANALYSIS.md` for enhanced schema with capability proofs and authority tiers

### **Appendix C: SDK API Reference**

**Complete TypeScript/Python SDK API documentation** (to be created)

### **Appendix D: Integration Examples**

**Example integrations:**
- Simple Web App
- IDE Extension
- CLI Tool
- Service Application

### **Appendix E: Error Codes**

**Standard error codes** for app integration failures

### **Appendix F: PLIx Contract Examples**

This appendix provides comprehensive PLIx contract examples demonstrating purity, verifiability, compensation, confidence thresholds, safety checks, and integration with AIM-OS components (VIF, SEG, SCOR, APOE, CMC).

---

#### **Example 1: Basic Intent Contract - Booking a Meeting Room**

**Pure Intent Declaration:**
```json
{
  "contract_id": "plix_booking_001",
  "intent": "Book a meeting room for 1 hour",
  "description": "Reserve an available meeting room for a specified duration",
  
  "preconditions": {
    "user_authenticated": true,
    "room_available": {
      "type": "query",
      "service": "cmc",
      "query": "SELECT room_id FROM rooms WHERE available = true AND capacity >= ${required_capacity}"
    },
    "time_slot_valid": {
      "type": "validation",
      "rule": "${start_time} < ${end_time} AND ${duration_minutes} <= 480"
    },
    "user_has_permission": {
      "type": "check",
      "service": "scor",
      "probe": "user_permission_check",
      "params": {"user_id": "${user_id}", "action": "book_room"}
    }
  },
  
  "postconditions": {
    "room_reserved": {
      "type": "state",
      "service": "cmc",
      "atom_tags": ["room_booking", "reservation"],
      "content": {
        "room_id": "${room_id}",
        "user_id": "${user_id}",
        "start_time": "${start_time}",
        "end_time": "${end_time}",
        "status": "confirmed"
      }
    },
    "confirmation_sent": {
      "type": "event",
      "service": "seg",
      "entity": "booking_confirmation",
      "relation": "confirms"
    }
  },
  
  "compensation": {
    "intent": "Cancel room reservation",
    "trigger": "postcondition_failure OR execution_error",
    "steps": [
      {
        "action": "release_room",
        "service": "cmc",
        "atom_update": {"status": "cancelled"}
      },
      {
        "action": "notify_user",
        "service": "seg",
        "entity": "cancellation_notice"
      }
    ]
  },
  
  "confidence_threshold": 0.85,
  "confidence_source": "vif",
  
  "safety_checks": [
    {
      "type": "scor_baseline",
      "probe": "booking_behavior_baseline",
      "params": {"user_id": "${user_id}", "action": "book_room"},
      "threshold": 0.80
    },
    {
      "type": "scor_invariant",
      "rule": "no_double_booking",
      "validation": "SELECT COUNT(*) FROM reservations WHERE room_id = ${room_id} AND time_overlaps(${start_time}, ${end_time}) = 0"
    },
    {
      "type": "seg_contradiction",
      "check": "no_conflicting_reservations",
      "query": "SELECT * FROM seg WHERE entity_type = 'reservation' AND contradicts(room_id=${room_id}, time=${start_time})"
    }
  ],
  
  "evidence_requirements": [
    {
      "type": "vif_witness",
      "service": "vif",
      "witness_type": "intent_execution",
      "fields": ["intent", "preconditions", "postconditions", "confidence", "timestamp"]
    },
    {
      "type": "seg_entity",
      "service": "seg",
      "entity_type": "room_booking",
      "relations": ["reserved_by", "occupies", "scheduled_at"]
    },
    {
      "type": "cmc_atom",
      "service": "cmc",
      "modality": "json",
      "tags": ["room_booking", "reservation", "intent_execution"],
      "bitemporal": true
    }
  ],
  
  "saga_pattern": {
    "steps": [
      {
        "action": "validate_preconditions",
        "compensation": "none",
        "timeout": "5s"
      },
      {
        "action": "reserve_room",
        "service": "cmc",
        "compensation": "release_room",
        "timeout": "10s"
      },
      {
        "action": "create_vif_witness",
        "service": "vif",
        "compensation": "revoke_witness",
        "timeout": "5s"
      },
      {
        "action": "store_seg_entity",
        "service": "seg",
        "compensation": "remove_seg_entity",
        "timeout": "5s"
      },
      {
        "action": "send_confirmation",
        "service": "seg",
        "compensation": "cancel_confirmation",
        "timeout": "10s"
      }
    ],
    "compensation_order": "reverse"
  },
  
  "apoe_compilation": {
    "plan_id": "apoe_booking_001",
    "roles": [
      {
        "role": "validator",
        "service": "scor",
        "capability": "precondition_validation"
      },
      {
        "role": "executor",
        "service": "cmc",
        "capability": "atom_creation"
      },
      {
        "role": "verifier",
        "service": "vif",
        "capability": "witness_creation"
      },
      {
        "role": "tracker",
        "service": "seg",
        "capability": "entity_creation"
      }
    ],
    "gates": [
      {
        "gate_id": "precondition_gate",
        "condition": "all_preconditions_valid",
        "confidence_threshold": 0.85
      },
      {
        "gate_id": "postcondition_gate",
        "condition": "all_postconditions_satisfied",
        "confidence_threshold": 0.85
      }
    ]
  }
}
```

**Key Features Demonstrated:**
- ✅ **Pure Intent:** Declares "what" (book room) not "how" (implementation details)
- ✅ **Verifiability:** Preconditions and postconditions enable formal verification
- ✅ **Compensation:** Complete rollback logic for failure scenarios
- ✅ **Confidence Thresholds:** VIF-based confidence gating (0.85)
- ✅ **Safety Checks:** SCOR baseline probes, invariant checks, SEG contradiction detection
- ✅ **AIM-OS Integration:** Uses CMC (storage), VIF (witnesses), SEG (entities), SCOR (safety), APOE (execution)

---

#### **Example 2: Intermediate Example - User Authentication Flow**

**Security-Sensitive Intent with SCOR Enhancement:**

```json
{
  "contract_id": "plix_auth_002",
  "intent": "Authenticate user and establish secure session",
  "description": "Verify user credentials and create authenticated session with security validation",
  
  "preconditions": {
    "credentials_provided": {
      "type": "validation",
      "rule": "${username} IS NOT NULL AND ${password} IS NOT NULL"
    },
    "rate_limit_not_exceeded": {
      "type": "check",
      "service": "scor",
      "probe": "rate_limit_check",
      "params": {"ip_address": "${client_ip}", "action": "login"},
      "threshold": 5
    },
    "no_suspicious_patterns": {
      "type": "check",
      "service": "scor",
      "probe": "social_signal_detection",
      "params": {"username": "${username}", "ip_address": "${client_ip}"},
      "threshold": 0.70
    }
  },
  
  "postconditions": {
    "user_authenticated": {
      "type": "state",
      "service": "cmc",
      "atom_tags": ["authentication", "session"],
      "content": {
        "user_id": "${user_id}",
        "session_token": "${session_token}",
        "authenticated_at": "${timestamp}",
        "expires_at": "${expires_at}"
      }
    },
    "security_event_logged": {
      "type": "event",
      "service": "seg",
      "entity": "authentication_event",
      "relation": "authenticates"
    }
  },
  
  "compensation": {
    "intent": "Revoke authentication and secure session",
    "trigger": "postcondition_failure OR security_violation",
    "steps": [
      {
        "action": "invalidate_session",
        "service": "cmc",
        "atom_update": {"status": "revoked", "revoked_at": "${timestamp}"}
      },
      {
        "action": "log_security_event",
        "service": "seg",
        "entity": "security_violation",
        "relation": "violates"
      }
    ]
  },
  
  "confidence_threshold": 0.90,
  "confidence_source": "vif",
  
  "safety_checks": [
    {
      "type": "scor_baseline",
      "probe": "authentication_behavior_baseline",
      "params": {"username": "${username}", "ip_address": "${client_ip}"},
      "threshold": 0.85
    },
    {
      "type": "scor_adversarial",
      "probe": "adversarial_simulation",
      "params": {"username": "${username}", "password_pattern": "${password_pattern}"},
      "threshold": 0.75
    },
    {
      "type": "scor_social",
      "probe": "social_engineering_detection",
      "params": {"username": "${username}", "request_context": "${request_context}"},
      "threshold": 0.80
    }
  ],
  
  "evidence_requirements": [
    {
      "type": "vif_witness",
      "service": "vif",
      "witness_type": "security_event",
      "fields": ["intent", "preconditions", "postconditions", "confidence", "security_checks", "timestamp"]
    },
    {
      "type": "seg_entity",
      "service": "seg",
      "entity_type": "authentication_event",
      "relations": ["authenticates", "creates_session", "logs_security_event"]
    }
  ],
  
  "saga_pattern": {
    "steps": [
      {
        "action": "validate_credentials",
        "compensation": "none",
        "timeout": "5s"
      },
      {
        "action": "run_scor_checks",
        "service": "scor",
        "compensation": "none",
        "timeout": "10s"
      },
      {
        "action": "create_session",
        "service": "cmc",
        "compensation": "invalidate_session",
        "timeout": "5s"
      },
      {
        "action": "create_vif_witness",
        "service": "vif",
        "compensation": "revoke_witness",
        "timeout": "5s"
      },
      {
        "action": "log_security_event",
        "service": "seg",
        "compensation": "remove_seg_entity",
        "timeout": "5s"
      }
    ],
    "compensation_order": "reverse"
  }
}
```

**Key Features Demonstrated:**
- ✅ **Security Focus:** SCOR's social signal detection and adversarial simulation
- ✅ **Rate Limiting:** Built-in rate limit checks via SCOR
- ✅ **High Confidence:** 0.90 threshold for security-sensitive operations
- ✅ **Comprehensive Safety:** Multiple SCOR probes (baseline, adversarial, social)

---

#### **Example 3: Advanced Example - Data Processing Pipeline**

**Composition of Intents with Sub-Intents:**

```json
{
  "contract_id": "plix_pipeline_003",
  "intent": "Process data pipeline with validation and transformation",
  "description": "Compose multiple sub-intents to create a complete data processing workflow",
  
  "sub_intents": [
    {
      "intent": "Validate input data",
      "contract_id": "plix_validate_001",
      "preconditions": {
        "data_provided": true,
        "schema_valid": {
          "type": "validation",
          "rule": "validate_schema(${input_data}, ${expected_schema})"
        }
      },
      "postconditions": {
        "data_validated": true,
        "validation_report": "${validation_report}"
      }
    },
    {
      "intent": "Transform data",
      "contract_id": "plix_transform_001",
      "preconditions": {
        "data_validated": true,
        "transformation_rules_provided": true
      },
      "postconditions": {
        "data_transformed": true,
        "transformed_data": "${transformed_data}"
      }
    },
    {
      "intent": "Store processed data",
      "contract_id": "plix_store_001",
      "preconditions": {
        "data_transformed": true,
        "storage_available": true
      },
      "postconditions": {
        "data_stored": true,
        "storage_location": "${storage_location}"
      }
    }
  ],
  
  "preconditions": {
    "pipeline_config_provided": true,
    "all_sub_intents_compiled": true
  },
  
  "postconditions": {
    "pipeline_completed": true,
    "all_sub_intents_satisfied": true,
    "provenance_tracked": {
      "type": "state",
      "service": "seg",
      "entity": "pipeline_execution",
      "relations": ["composed_of", "produces", "tracks_provenance"]
    }
  },
  
  "compensation": {
    "intent": "Rollback pipeline execution",
    "trigger": "any_sub_intent_failure",
    "steps": [
      {
        "action": "rollback_sub_intents",
        "order": "reverse",
        "compensation_contracts": ["plix_store_001", "plix_transform_001", "plix_validate_001"]
      },
      {
        "action": "cleanup_resources",
        "service": "cmc",
        "atom_update": {"status": "rolled_back"}
      }
    ]
  },
  
  "confidence_threshold": 0.80,
  "confidence_source": "vif",
  
  "safety_checks": [
    {
      "type": "seg_contradiction",
      "check": "no_data_loss",
      "query": "SELECT * FROM seg WHERE entity_type = 'data_transformation' AND contradicts(data_integrity=true)"
    },
    {
      "type": "privacy_compliance",
      "check": "gdpr_compliance",
      "rule": "validate_privacy_rules(${input_data}, ${privacy_policy})"
    }
  ],
  
  "evidence_requirements": [
    {
      "type": "vif_witness",
      "service": "vif",
      "witness_type": "pipeline_execution",
      "fields": ["intent", "sub_intents", "preconditions", "postconditions", "confidence", "timestamp"]
    },
    {
      "type": "seg_entity",
      "service": "seg",
      "entity_type": "pipeline_execution",
      "relations": ["composed_of", "produces", "tracks_provenance"]
    },
    {
      "type": "provenance_chain",
      "service": "seg",
      "format": "w3c_prov_json",
      "entities": ["input_data", "transformed_data", "stored_data"]
    }
  ],
  
  "saga_pattern": {
    "steps": [
      {
        "action": "execute_sub_intent",
        "sub_intent": "plix_validate_001",
        "compensation": "rollback_validation"
      },
      {
        "action": "execute_sub_intent",
        "sub_intent": "plix_transform_001",
        "compensation": "rollback_transformation"
      },
      {
        "action": "execute_sub_intent",
        "sub_intent": "plix_store_001",
        "compensation": "rollback_storage"
      },
      {
        "action": "create_provenance_chain",
        "service": "seg",
        "compensation": "remove_provenance_chain"
      }
    ],
    "compensation_order": "reverse"
  }
}
```

**Key Features Demonstrated:**
- ✅ **Composition:** Multiple sub-intents composed into a single workflow
- ✅ **Provenance Tracking:** SEG tracks end-to-end data lineage (W3C PROV-JSON)
- ✅ **Privacy Compliance:** Built-in GDPR compliance checks
- ✅ **Complex Compensation:** Rollback of composed intents in reverse order

---

#### **Example 4: AI Collaboration Example - Handoff Task to Agent**

**Multi-Agent System with SCOR Enhancement:**

```json
{
  "contract_id": "plix_handoff_004",
  "intent": "Hand off task to another AI agent",
  "description": "Transfer task execution responsibility to another agent with verification",
  
  "preconditions": {
    "task_defined": {
      "type": "validation",
      "rule": "${task_description} IS NOT NULL AND ${task_description}.length > 0"
    },
    "target_agent_available": {
      "type": "query",
      "service": "cmc",
      "query": "SELECT agent_id FROM agents WHERE status = 'available' AND capabilities CONTAINS ${required_capabilities}"
    },
    "no_anomalous_collaboration": {
      "type": "check",
      "service": "scor",
      "probe": "anomalous_collaboration_detection",
      "params": {
        "source_agent": "${source_agent_id}",
        "target_agent": "${target_agent_id}",
        "task_type": "${task_type}"
      },
      "threshold": 0.75
    }
  },
  
  "postconditions": {
    "task_handed_off": {
      "type": "state",
      "service": "cmc",
      "atom_tags": ["task_handoff", "agent_collaboration"],
      "content": {
        "task_id": "${task_id}",
        "source_agent": "${source_agent_id}",
        "target_agent": "${target_agent_id}",
        "handoff_timestamp": "${timestamp}",
        "status": "in_progress"
      }
    },
    "handoff_verified": {
      "type": "event",
      "service": "seg",
      "entity": "agent_handoff",
      "relation": "transfers_responsibility"
    }
  },
  
  "compensation": {
    "intent": "Revoke task handoff",
    "trigger": "postcondition_failure OR agent_unavailable",
    "steps": [
      {
        "action": "reclaim_task",
        "service": "cmc",
        "atom_update": {"status": "reclaimed", "reclaimed_at": "${timestamp}"}
      },
      {
        "action": "notify_agents",
        "service": "seg",
        "entity": "handoff_revocation",
        "relation": "revokes"
      }
    ]
  },
  
  "confidence_threshold": 0.85,
  "confidence_source": "vif",
  
  "safety_checks": [
    {
      "type": "scor_baseline",
      "probe": "agent_collaboration_baseline",
      "params": {
        "source_agent": "${source_agent_id}",
        "target_agent": "${target_agent_id}"
      },
      "threshold": 0.80
    },
    {
      "type": "scor_anomalous",
      "probe": "anomalous_collaboration_detection",
      "params": {
        "source_agent": "${source_agent_id}",
        "target_agent": "${target_agent_id}",
        "task_type": "${task_type}"
      },
      "threshold": 0.75
    }
  ],
  
  "evidence_requirements": [
    {
      "type": "vif_witness",
      "service": "vif",
      "witness_type": "agent_collaboration",
      "fields": ["intent", "preconditions", "postconditions", "confidence", "safety_checks", "timestamp"]
    },
    {
      "type": "seg_entity",
      "service": "seg",
      "entity_type": "agent_handoff",
      "relations": ["transfers_responsibility", "involves_agents", "tracks_task"]
    }
  ],
  
  "saga_pattern": {
    "steps": [
      {
        "action": "validate_handoff_preconditions",
        "compensation": "none",
        "timeout": "5s"
      },
      {
        "action": "run_scor_checks",
        "service": "scor",
        "compensation": "none",
        "timeout": "10s"
      },
      {
        "action": "create_handoff_record",
        "service": "cmc",
        "compensation": "remove_handoff_record",
        "timeout": "5s"
      },
      {
        "action": "notify_target_agent",
        "service": "seg",
        "compensation": "cancel_notification",
        "timeout": "5s"
      },
      {
        "action": "create_vif_witness",
        "service": "vif",
        "compensation": "revoke_witness",
        "timeout": "5s"
      }
    ],
    "compensation_order": "reverse"
  }
}
```

**Key Features Demonstrated:**
- ✅ **Multi-Agent:** Handoff between AI agents with verification
- ✅ **SCOR Enhancement:** Anomalous collaboration detection
- ✅ **Agent Discovery:** CMC-based agent availability queries
- ✅ **Collaboration Tracking:** SEG tracks agent interactions

---

#### **Example 5: Self-Improvement Example - Optimize System Performance**

**Ties to SIS (Self-Improvement System) for Dynamic Evolution:**

```json
{
  "contract_id": "plix_optimize_005",
  "intent": "Optimize system performance based on observed patterns",
  "description": "Self-improvement intent that learns from execution patterns and optimizes future performance",
  
  "preconditions": {
    "performance_data_available": {
      "type": "query",
      "service": "seg",
      "query": "SELECT * FROM seg WHERE entity_type = 'performance_metric' AND timestamp > ${lookback_window}"
    },
    "optimization_target_defined": {
      "type": "validation",
      "rule": "${target_metric} IN ['latency', 'throughput', 'resource_usage'] AND ${target_value} IS NOT NULL"
    },
    "sis_available": {
      "type": "check",
      "service": "sis",
      "probe": "sis_availability_check",
      "params": {"system": "${system_id}"}
    }
  },
  
  "postconditions": {
    "optimization_plan_created": {
      "type": "state",
      "service": "cmc",
      "atom_tags": ["optimization", "self_improvement"],
      "content": {
        "optimization_id": "${optimization_id}",
        "target_metric": "${target_metric}",
        "target_value": "${target_value}",
        "optimization_plan": "${optimization_plan}",
        "created_at": "${timestamp}"
      }
    },
    "sis_learning_updated": {
      "type": "event",
      "service": "sis",
      "entity": "optimization_learning",
      "relation": "learns_from"
    },
    "performance_improved": {
      "type": "validation",
      "rule": "${current_${target_metric}} < ${previous_${target_metric}}"
    }
  },
  
  "compensation": {
    "intent": "Revert optimization",
    "trigger": "performance_degraded OR optimization_failed",
    "steps": [
      {
        "action": "revert_changes",
        "service": "cmc",
        "atom_update": {"status": "reverted", "reverted_at": "${timestamp}"}
      },
      {
        "action": "update_sis_learning",
        "service": "sis",
        "entity": "optimization_failure",
        "relation": "learns_from"
      }
    ]
  },
  
  "confidence_threshold": 0.75,
  "confidence_source": "vif",
  
  "safety_checks": [
    {
      "type": "resource_limits",
      "check": "resource_usage_within_limits",
      "rule": "${cpu_usage} < 0.90 AND ${memory_usage} < 0.90"
    },
    {
      "type": "sis_validation",
      "check": "optimization_safe",
      "service": "sis",
      "probe": "optimization_safety_check",
      "params": {"optimization_plan": "${optimization_plan}"},
      "threshold": 0.70
    }
  ],
  
  "evidence_requirements": [
    {
      "type": "vif_witness",
      "service": "vif",
      "witness_type": "self_improvement",
      "fields": ["intent", "preconditions", "postconditions", "confidence", "optimization_results", "timestamp"]
    },
    {
      "type": "seg_entity",
      "service": "seg",
      "entity_type": "optimization_event",
      "relations": ["optimizes", "learns_from", "improves"]
    },
    {
      "type": "sis_learning",
      "service": "sis",
      "entity": "optimization_pattern",
      "relation": "learns_from"
    }
  ],
  
  "saga_pattern": {
    "steps": [
      {
        "action": "analyze_performance_data",
        "service": "seg",
        "compensation": "none",
        "timeout": "30s"
      },
      {
        "action": "generate_optimization_plan",
        "service": "sis",
        "compensation": "none",
        "timeout": "60s"
      },
      {
        "action": "validate_optimization_safety",
        "service": "sis",
        "compensation": "none",
        "timeout": "10s"
      },
      {
        "action": "apply_optimization",
        "service": "cmc",
        "compensation": "revert_optimization",
        "timeout": "30s"
      },
      {
        "action": "measure_improvement",
        "service": "seg",
        "compensation": "none",
        "timeout": "10s"
      },
      {
        "action": "update_sis_learning",
        "service": "sis",
        "compensation": "revert_learning_update",
        "timeout": "5s"
      },
      {
        "action": "create_vif_witness",
        "service": "vif",
        "compensation": "revoke_witness",
        "timeout": "5s"
      }
    ],
    "compensation_order": "reverse"
  }
}
```

**Key Features Demonstrated:**
- ✅ **Self-Improvement:** Ties to SIS for dynamic evolution
- ✅ **Learning Loop:** SIS learns from optimization patterns
- ✅ **Resource Management:** Built-in resource limit checks
- ✅ **Performance Tracking:** SEG tracks performance metrics and improvements

---

#### **PLIx → APOE Compilation Summary**

All PLIx contracts compile to APOE execution plans with:

1. **Precondition Validation:** All preconditions validated before execution
2. **Postcondition Verification:** All postconditions verified after execution
3. **Evidence Storage:** VIF witnesses, SEG entities, CMC atoms created
4. **Saga Pattern:** Atomic execution with compensation on failure
5. **Confidence Gating:** Execution gated by confidence thresholds
6. **Safety Checks:** SCOR probes, SEG contradictions, resource limits enforced
7. **Provenance Tracking:** Complete execution lineage via SEG (W3C PROV-JSON)
8. **Self-Improvement:** SIS integration for learning and optimization

**Integration Points:**
- **CMC:** Bitemporal storage of intent contracts and execution artifacts
- **VIF:** Confidence tracking and witness creation for verifiability
- **APOE:** Execution plan compilation and orchestration
- **SEG:** Knowledge synthesis, contradiction detection, provenance tracking
- **SCOR:** Behavioral validation, invariant checks, safety monitoring
- **SIS:** Self-improvement and learning from execution patterns

---

## 🎯 **SUCCESS METRICS**

**SDK Adoption:**
- ✅ 3+ apps use SDK in production
- ✅ SDK documentation complete
- ✅ SDK examples cover common use cases

**Panel Ecosystem:**
- ✅ 5+ dynamic panels registered
- ✅ Apps can register panels via manifest
- ✅ Panel-to-panel communication works

**Performance:**
- ✅ SDK overhead < 10ms per call
- ✅ Panel loading < 500ms
- ✅ Event delivery < 100ms

**Security:**
- ✅ All apps authenticated
- ✅ Service permissions enforced
- ✅ Resource limits enforced
- ✅ SCOR validation passes (invariants, baselines, social signals)
- ✅ PLIx contracts validated (preconditions, postconditions, evidence)

**PLIx Integration:**
- ✅ 5+ apps use PLIx contracts in manifests
- ✅ PLIx → APOE compilation works
- ✅ Intent verification via VIF witnesses
- ✅ Contract validation during registration

**SCOR Integration:**
- ✅ Behavioral validation during registration
- ✅ Runtime drift detection active
- ✅ Invariant checks passing
- ✅ Baseline probes configured

---

## 📋 **SUMMARY: KEY FINDINGS**

### **✅ What Already Exists**

1. **MCP Tools:** 81 MCP tools available, including `create_application`, `deploy_application`, `manage_application_lifecycle`
2. **Command Server:** HTTP API wrapper (`POST /mcp/execute`) for MCP tools
3. **CMC Integration:** App records stored in CMC atoms (bitemporal)
4. **Resource Tracking:** Frontend resource tracker exists (`resourceTracker.ts`)
5. **TypeScript SDK:** `packages/aimos-sdk/` - Complete SDK implementation (Phase 1 Complete) ⭐
6. **IDE DAC v2:** Native AIM-OS IDE with 23+ integrated panels (`ide_orchestration/prototypes/dac/`) ⭐

### **🚧 What Needs Enhancement**

1. **App Registry:** Basic app management exists, needs manifest validation, dependency resolution, token generation
2. **App Discovery:** No discovery endpoint - apps query CMC directly
3. **SDK:** ✅ TypeScript SDK complete - Python SDK needed
4. **Authentication:** No app tokens - all requests unauthenticated
5. **Resource Management:** Basic tracking exists, needs allocation and limits
6. **Panel System:** Hardcoded panels in IDE DAC v2, needs dynamic registration (Phase 3)

### **🎯 Integration Pattern (REALITY)**

```
App → Command Server (HTTP) → MCP Client → MCP Server (stdio) → AIM-OS System
```

**NOT:**
```
App → REST API → AIM-OS Service  ❌ (Doesn't exist)
```

### **💡 Key Insight**

**AIM-OS integration happens via MCP tools, not REST APIs.** The Command Server provides HTTP wrapper for convenience, but the underlying protocol is MCP (JSON-RPC 2.0).

---

**This protocol ensures AIM-OS is always integrated, apps are always AIM-OS-aware, and the ecosystem works together seamlessly.** ✨

---

**Document Status:** ✅ **CONSOLIDATED** - Version 2.3.0 (PLIx & Security Integrated)  
**Last Updated:** 2025-01-27  
**Phase 1 Status:** ✅ **COMPLETE** - TypeScript SDK implemented  
**Phase 2 Status:** ⏳ **IN PROGRESS** - **SECURITY CRITICAL** - Must be completed immediately  
**Next Review:** After Phase 2 (Enhanced App Registry) completion

**Enhancement History:**
- **v2.0.0:** Initial consolidation from 4 documents
- **v2.1.0:** North Star alignment (Gemini comprehensive enhancement)
  - Infused North Star philosophy (meta-circularity, proof loops, quartet parity)
  - Expanded empty sections (Backend Architecture, Security, Inter-App Communication, UI Integration, Resource Management)
  - Added Critical Files Reference and Appendices
  - Enhanced Implementation Roadmap with detailed tasks
- **v2.2.0:** AIP 2.0 security hardening (DeepSearch specification)
  - Identified critical security vulnerabilities (MCP security vacuum, data isolation)
  - Mandated Service Layer (Layer 2) for security and governance
  - Added mandatory compliance requirements (quarterly audits)
  - Enhanced governance framework (Authority-Weighted Integration)
- **v2.3.0:** PLIx & Security Systems Integration (Research consolidation)
  - Integrated PLIx language for intent-driven app development
  - Integrated SCOR security system for behavioral validation
  - Enhanced app manifest with PLIx contracts and security requirements
  - Added PLIx contract validation to registration flow
  - Added SCOR validation to registration and runtime flows
- **v2.4.0:** PLIx & SCOR Fully Integrated (Grok review)
  - Updated all sections to reflect PLIx and SCOR as fully implemented
  - Added PLIxService to SDK
  - Enhanced IDE DAC v2 with PLIx Editor and SCOR Monitor features
  - Updated all phases to show PLIx/SCOR integration complete
  - Added PLIx contract examples and SCOR integration details
- **v2.5.0:** Comprehensive PLIx Examples Integrated (Grok examples)
  - Expanded Appendix F with 5 comprehensive PLIx contract examples
  - Example 1: Basic Intent Contract (Booking a Meeting Room) - demonstrates purity, verifiability, compensation, confidence thresholds, safety checks, and full AIM-OS integration
  - Example 2: Intermediate Example (User Authentication Flow) - security-sensitive intent with SCOR enhancement (rate limiting, social signal detection, adversarial simulation)
  - Example 3: Advanced Example (Data Processing Pipeline) - composition of intents with sub-intents, provenance tracking (W3C PROV-JSON), privacy compliance
  - Example 4: AI Collaboration Example (Handoff Task to Agent) - multi-agent system with SCOR anomalous collaboration detection
  - Example 5: Self-Improvement Example (Optimize System Performance) - ties to SIS for dynamic evolution and learning
  - All examples demonstrate PLIx → APOE compilation with complete integration points (CMC, VIF, SEG, SCOR, APOE, SIS)

**External AI Advisor Contributions:**
- **ChatGPT:** Concrete implementation code (JSON Schema, Command Server routes, MCP tools)
- **Perplexity:** SDK quality enhancements (retry logic, caching, testing)
- **Grok:** Phase 2 guidance (capability proofs, authority tiers, bitemporal schemas)
- **Gemini:** Comprehensive North Star alignment (philosophy infusion, complete implementations, authoritative references)
- **DeepSearch:** AIP 2.0 definitive specification (critical security vulnerabilities, mandatory governance, compliance requirements) 🚨
- **Grok:** Full PLIx & SCOR integration review (implementation status updates, SDK enhancements, IDE features) ⭐
- **Grok:** Comprehensive PLIx Examples (5 detailed contract examples demonstrating purity, verifiability, compensation, confidence thresholds, safety checks, and full AIM-OS integration) ⭐

---

## 📚 **RELATED DOCUMENTATION**

- **SDK Implementation:** `packages/aimos-sdk/IMPLEMENTATION_DOCUMENTATION.md`
- **IDE DAC v2:** `ide_orchestration/prototypes/dac/README.md`
- **Consolidation Summary:** `knowledge_architecture/systems/lucid-ide/backend-api-system/CONSOLIDATION_SUMMARY.md`
- **ChatGPT AIP Advice Analysis:** `knowledge_architecture/systems/lucid-ide/backend-api-system/CHATGPT_AIP_ADVICE_ANALYSIS.md` ⭐
- **Perplexity SDK Feedback Analysis:** `knowledge_architecture/systems/lucid-ide/backend-api-system/PERPLEXITY_SDK_FEEDBACK_ANALYSIS.md` ⭐
- **Grok Phase 2 Guidance Analysis:** `knowledge_architecture/systems/lucid-ide/backend-api-system/GROK_PHASE2_GUIDANCE_ANALYSIS.md` ⭐
- **Gemini AIP Enhancement Analysis:** `knowledge_architecture/systems/lucid-ide/backend-api-system/GEMINI_AIP_ENHANCEMENT_ANALYSIS.md` ⭐
- **DeepSearch AIP 2.0 Specification Analysis:** `knowledge_architecture/systems/lucid-ide/backend-api-system/DEEPSEARCH_AIP2_SPECIFICATION_ANALYSIS.md` ⭐ **NEW - Critical Security & Governance Requirements** 🚨
- **PLIx & Security Systems Integration Research:** `knowledge_architecture/systems/lucid-ide/backend-api-system/PLIX_SECURITY_INTEGRATION_RESEARCH.md` ⭐ **NEW - PLIx Language & SCOR Security Integration** 🔒
- **PLIX External AI Feedback Synthesis:** `knowledge_architecture/systems/plix/EXTERNAL_AI_FEEDBACK_SYNTHESIS.md` ⭐ **NEW - Comprehensive synthesis of ChatGPT, Grok, Perplexity, and Gemini feedback on PLIX definition and design** 🎯

