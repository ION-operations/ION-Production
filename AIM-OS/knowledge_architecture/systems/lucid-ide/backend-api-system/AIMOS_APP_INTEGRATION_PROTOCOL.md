# AIM-OS Application Integration Protocol (AIP)
# Comprehensive protocol for app integration with AIM-OS

**Status:** Design Phase  
**Version:** 1.0.0  
**Date:** 2025-01-27  
**Purpose:** Define standard protocol for apps to integrate with AIM-OS systems

---

## 🎯 **CORE PRINCIPLE**

**AIM-OS is always integrated, apps are always AIM-OS-aware**

Every app in the AIM-OS ecosystem:
- Declares its AIM-OS dependencies
- Registers with AIM-OS on startup
- Uses AIM-OS services for memory, verification, orchestration
- Exposes its capabilities to other apps
- Participates in the unified consciousness substrate

---

## 📋 **PROTOCOL OVERVIEW**

### **Three Layers of Integration**

1. **Declaration Layer** - App declares what it needs and provides
2. **Registration Layer** - App registers with AIM-OS backend
3. **Runtime Layer** - App uses AIM-OS services during execution

---

## 🔧 **LAYER 1: DECLARATION LAYER**

### **App Manifest (`aimos.json`)**

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
      "cas"       // Cognitive analysis (optional)
    ],
    
    "capabilities": {
      "provides_memory": false,        // Does this app provide memory storage?
      "provides_verification": false,   // Does this app provide verification?
      "provides_orchestration": false,  // Does this app provide orchestration?
      "exposes_api": true,              // Does this app expose an API?
      "exposes_ui": true                // Does this app expose a UI?
    },
    
    "api_endpoints": {
      "base_url": "http://localhost:3000",
      "endpoints": [
        {
          "path": "/api/memory",
          "method": "POST",
          "description": "Store memory",
          "aimos_service": "cmc"
        }
      ]
    },
    
    "ui_integration": {
      "panels": [
        {
          "id": "app-panel-1",
          "name": "App Panel",
          "location": "left" | "right" | "bottom" | "main",
          "lazy_load": true
        }
      ],
      "routes": [
        {
          "path": "/app/dashboard",
          "component": "Dashboard"
        }
      ]
    },
    
    "resource_requirements": {
      "estimated_memory_mb": 50,
      "estimated_cpu_percent": 5,
      "requires_persistent_storage": true,
      "requires_network_access": true
    },
    
    "lifecycle_hooks": {
      "on_startup": "app/scripts/startup.js",
      "on_shutdown": "app/scripts/shutdown.js",
      "on_error": "app/scripts/error_handler.js"
    }
  },
  
  "dependencies": {
    "aimos_core": "^1.0.0",
    "other_apps": ["app-id-1", "app-id-2"]
  }
}
```

### **Manifest Validation**

- **Required Fields:** `app_id`, `app_name`, `app_version`, `aimos_integration`
- **Service Validation:** AIM-OS validates that required services exist
- **Dependency Resolution:** AIM-OS resolves app dependencies
- **Resource Check:** AIM-OS validates resource availability

---

## 🔌 **LAYER 2: REGISTRATION LAYER**

### **⚠️ CURRENT STATE: Application Management Exists**

**Application lifecycle management already exists via MCP tools:**
- `create_application` - Creates app record (stores in CMC)
- `deploy_application` - Deploys app to environment
- `manage_application_lifecycle` - Manages app lifecycle

**However, these tools are basic and need enhancement for full app registry protocol.**

### **Registration Flow (ENHANCED PROTOCOL)**

```
1. App Startup
   ↓
2. App loads aimos.json manifest
   ↓
3. App calls MCP tool via Command Server
   POST http://localhost:5001/mcp/execute
   {
     "tool": "create_application",
     "arguments": {
       "app_name": "my-app",
       "app_type": "ide",
       "config": {
         "manifest": { ... },
         "runtime_info": {
           "host": "localhost",
           "port": 3000,
           "pid": 12345,
           "started_at": "2025-01-27T10:00:00Z"
         }
       },
       "dependencies": ["app-id-1", "app-id-2"]
     }
   }
   ↓
4. MCP Server validates manifest (via create_application tool)
   ↓
5. MCP Server checks dependencies
   ↓
6. MCP Server allocates resources (future enhancement)
   ↓
7. MCP Server creates app record in CMC (already implemented)
   ↓
8. MCP Server returns app_id and atom_id
   {
     "success": true,
     "application": {
       "app_id": "uuid",
       "app_name": "my-app",
       "status": "created",
       ...
     },
     "atom_id": "atom_abc123..."  // CMC atom ID
   }
   ↓
9. App stores app_id for future operations
   ↓
10. App calls lifecycle hooks (future enhancement)
```

### **Enhanced Registration API (FUTURE)**

**Current:** Apps use `create_application` MCP tool directly.

**Future:** Enhanced app registry service with:
- Manifest validation
- Dependency resolution
- Resource allocation
- Token generation
- Service endpoint discovery

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
  app_token: string  // JWT token for authenticated requests (future)
  command_server_url: string  // "http://localhost:5001"
  registered_at: string
  status: 'registered' | 'pending' | 'rejected'
  message?: string
  atom_id: string  // CMC atom ID for app record
}
```

### **App Discovery (FUTURE)**

**Current:** Apps query CMC directly via `retrieve_memory` with tags.

**Future:** Enhanced app discovery endpoint.

**Proposed Endpoint:** `GET /api/apps` (new Command Server endpoint)

**Query Parameters:**
- `type`: Filter by app type
- `service`: Filter by required service
- `status`: Filter by status (active, inactive, error)

**Response:**
```typescript
interface AppListResponse {
  apps: Array<{
    app_id: string
    app_name: string
    app_type: string
    status: 'active' | 'inactive' | 'error'
    registered_at: string
    last_heartbeat: string
    services_used: string[]
    resource_usage: {
      memory_mb: number
      cpu_percent: number
    }
  }>
  total: number
}
```

---

## ⚙️ **LAYER 3: RUNTIME LAYER**

### **⚠️ CRITICAL: AIM-OS Integration Architecture**

**AIM-OS does NOT expose REST APIs directly.** All integration happens via **MCP (Model Context Protocol) tools** through the **Command Server HTTP API**.

**Integration Flow:**
```
App → Command Server (HTTP) → MCP Client → MCP Server (stdio) → AIM-OS System
```

### **Service Integration Patterns**

#### **Pattern 1: MCP Tool Integration via Command Server (PRIMARY METHOD)**

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

#### **Pattern 2: SDK Integration (RECOMMENDED - FUTURE)**

Apps use AIM-OS SDK (wraps Command Server):

```typescript
import { AIMOSClient } from '@aimos/sdk'

const aimos = new AIMOSClient({
  appId: 'my-app',
  appToken: appToken,  // From registration
  commandServerUrl: 'http://localhost:5001'  // Command Server URL
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

#### **Pattern 3: Direct MCP Protocol (ADVANCED)**

Apps can use MCP protocol directly (JSON-RPC 2.0 over stdio):

```typescript
// Advanced: Direct MCP protocol connection
// Requires spawning Python process and managing stdio
// Not recommended for most apps - use Command Server instead
```

### **Available MCP Tools (81 Total)**

#### **Core AIM-OS Tools (6):**
- `store_memory` - Store memory atom in CMC
- `retrieve_memory` - Retrieve memories via HHNI
- `get_memory_stats` - Get CMC statistics
- `create_plan` - Create APOE execution plan
- `track_confidence` - Track VIF confidence
- `synthesize_knowledge` - Synthesize SEG knowledge

#### **Application Lifecycle Tools (3):**
- `create_application` - Create new application (already exists)
- `deploy_application` - Deploy application to environment (already exists)
- `manage_application_lifecycle` - Start/stop/monitor applications (already exists)

#### **Snapshot Tools (4):**
- `create_snapshot` - Create CMC snapshot
- `restore_snapshot` - Restore from snapshot
- `list_snapshots` - List available snapshots
- `archive_snapshot` - Archive snapshots

#### **Timeline Context Tools (3):**
- `add_timeline_entry` - Track context at each prompt
- `get_timeline_summary` - Get recent timeline entries
- `get_timeline_entries` - Query timeline history

#### **Goal Timeline Tools (3):**
- `create_goal_timeline_node` - Create goals as timeline planning nodes
- `update_goal_progress` - Update goal progress and status
- `query_goal_timeline` - Query goals with filtering

#### **AI Collaboration Tools (6):**
- `send_ai_message` - Send message to another AI
- `get_ai_messages` - Retrieve AI-to-AI messages
- `start_ai_discussion` - Start discussion thread
- `handoff_task_to_ai` - Hand off task to another AI
- `share_ai_profile` - Share AI profile
- `get_ai_collaboration_summary` - Get collaboration summary

#### **Plus 56 more tools** (autonomous operation, observability, etc.)

### **Command Server Endpoints**

**Base URL:** `http://localhost:5001`

**Endpoints:**
- `POST /mcp/execute` - Execute MCP tool (PRIMARY)
- `GET /mcp/list` - List available MCP tools
- `GET /health` - Health check
- `POST /cursor/chat/send` - Send message to Cursor chat
- `GET /cursor/*` - Cursor state endpoints

**Authentication:** Currently none (future: app registration tokens)

### **MCP Tool → AIM-OS System Mapping**

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

---

## 🔄 **APP LIFECYCLE MANAGEMENT**

### **Lifecycle States**

```
UNREGISTERED → REGISTERING → ACTIVE → PAUSED → STOPPED → UNREGISTERED
                                      ↓
                                   ERROR
```

### **Lifecycle Events**

**Registration:**
- `app.registered` - App successfully registered
- `app.registration_failed` - Registration failed

**Runtime:**
- `app.started` - App started
- `app.stopped` - App stopped
- `app.paused` - App paused
- `app.resumed` - App resumed
- `app.error` - App error occurred

**Health:**
- `app.heartbeat` - App heartbeat (every 30s)
- `app.health_check` - Health check request
- `app.unhealthy` - App marked unhealthy

### **Heartbeat System**

Apps MUST send heartbeat every 30 seconds:

```typescript
// App heartbeat
setInterval(async () => {
  await fetch('http://localhost:8000/api/apps/heartbeat', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${appToken}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      app_id: appId,
      status: 'active',
      resource_usage: {
        memory_mb: getMemoryUsage(),
        cpu_percent: getCPUUsage()
      },
      timestamp: new Date().toISOString()
    })
  })
}, 30000)
```

**If heartbeat fails:**
- AIM-OS marks app as `unhealthy`
- After 3 missed heartbeats → `inactive`
- After 10 missed heartbeats → `stopped`

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

---

## 📡 **INTER-APP COMMUNICATION**

### **App-to-App Messaging**

Apps can communicate via AIM-OS message bus:

```typescript
// App A sends message to App B
await aimos.messaging.send({
  to_app: 'app-b-id',
  message_type: 'data_request',
  content: { query: 'get user data' },
  priority: 'normal'
})

// App B receives message
aimos.messaging.onMessage((message) => {
  if (message.from_app === 'app-a-id') {
    // Handle message
  }
})
```

### **Event Broadcasting**

Apps can broadcast events to all apps:

```typescript
// App broadcasts event
await aimos.events.broadcast({
  event_type: 'user_action',
  data: { action: 'file_opened', file: 'example.ts' },
  target_apps: ['all'] // or specific app IDs
})
```

### **Shared State**

Apps can share state via AIM-OS:

```typescript
// App A sets shared state
await aimos.state.set('user_preferences', {
  theme: 'dark',
  language: 'en'
})

// App B reads shared state
const preferences = await aimos.state.get('user_preferences')
```

---

## 🎨 **UI INTEGRATION PROTOCOL**

### **Panel Registration**

Apps register UI panels in manifest:

```json
{
  "ui_integration": {
    "panels": [
      {
        "id": "app-panel-1",
        "name": "App Panel",
        "location": "left",
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
2. IDE loads panel metadata
   ↓
3. User opens panel
   ↓
4. IDE lazy-loads panel component
   ↓
5. Panel mounts and calls AIM-OS services
   ↓
6. Panel receives updates via AIM-OS events
   ↓
7. User closes panel
   ↓
8. Panel unmounts (but stays cached)
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
  action: 'user_clicked_button',
  data: { button: 'save' }
})
```

---

## 🔧 **BACKEND ARCHITECTURE**

### **Current Architecture (REALITY)**

**AIM-OS Integration Stack:**
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
└─────────────────────────────────────────────────────────┘
                        ↓ JSON-RPC 2.0 (stdio)
┌─────────────────────────────────────────────────────────┐
│  MCP Server (lucid_mcp_server.py)                      │
│  - 81 MCP tools                                         │
│  - Tool adapters                                        │
│  - JSON-RPC 2.0 handler                                 │
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

### **Application Management (CURRENT)**

**Location:** `lucid_mcp_server.py` (lines 5114-5611)

**MCP Tools:**
- `create_application` - Creates app record, stores in CMC
- `deploy_application` - Deploys app to environment
- `manage_application_lifecycle` - Manages app lifecycle

**Storage:**
- App metadata → CMC atoms (bitemporal)
- App state → In-memory dict or SQLite
- App metrics → CMC atoms with tags

**Current Implementation:**
```python
# lucid_mcp_server.py
def create_application(self, args):
    app_name = args.get("app_name")
    app_type = args.get("app_type")
    config = args.get("config", {})
    
    # Create app record
    app_id = str(uuid.uuid4())
    application = {
        "app_id": app_id,
        "app_name": app_name,
        "app_type": app_type,
        "config": config,
        "created_at": datetime.now().isoformat(),
        "status": "created"
    }
    
    # Store in CMC
    atom = self.memory.create_atom(AtomCreate(
        modality="text",
        content=AtomContent(inline=json.dumps(application)),
        tags={"type": "application", "app_id": app_id}
    ))
    
    return {"success": True, "application": application, "atom_id": atom.id}
```

### **App Registry Service (FUTURE ENHANCEMENT)**

**Location:** `packages/app_registry/` (to be created)

**Responsibilities:**
- Enhanced manifest validation
- Dependency resolution
- Resource allocation
- Token generation
- Service endpoint discovery
- Health monitoring

**Storage:**
- App metadata → CMC (bitemporal) ✅ (already implemented)
- App state → CMC atoms ✅ (already implemented)
- App metrics → VIF witnesses (future)

### **Command Server (CURRENT)**

**Location:** `cursor-addon/src/commandServer.ts`

**Endpoints:**
- `POST /mcp/execute` - Execute MCP tool ✅
- `GET /mcp/list` - List available MCP tools ✅
- `GET /health` - Health check ✅
- `POST /cursor/chat/send` - Send message to Cursor chat ✅
- `GET /cursor/*` - Cursor state endpoints ✅

**Future Endpoints (to be added):**
- `POST /api/apps/register` - Enhanced app registration
- `GET /api/apps` - App discovery
- `GET /api/apps/:app_id` - Get app details
- `POST /api/apps/:app_id/heartbeat` - Send heartbeat
- `GET /api/apps/:app_id/metrics` - Get app metrics

### **Service Gateway (FUTURE)**

**Location:** `packages/service_gateway/` (to be created)

**Responsibilities:**
- Route requests to MCP tools (via Command Server)
- Validate app tokens (future)
- Enforce service permissions (future)
- Rate limiting (future)
- Request logging (future)

**Architecture:**
```
App Request → Command Server → Token Validation → Permission Check → MCP Tool → AIM-OS System
```

---

## 📊 **MONITORING & OBSERVABILITY**

### **App Metrics**

Every app exposes metrics:

```typescript
interface AppMetrics {
  app_id: string
  uptime_seconds: number
  request_count: number
  error_count: number
  resource_usage: {
    memory_mb: number
    cpu_percent: number
    network_bytes: number
  }
  service_calls: {
    cmc: number
    vif: number
    apoe: number
  }
  last_heartbeat: string
}
```

### **AIM-OS Dashboard**

AIM-OS provides unified dashboard showing:
- All registered apps
- App health status
- Resource usage
- Service call statistics
- Error rates
- Inter-app communication

---

## 🚀 **IMPLEMENTATION ROADMAP**

### **Phase 0: Current State (COMPLETE)**
- [x] MCP tools for application management (`create_application`, `deploy_application`, `manage_application_lifecycle`)
- [x] Command Server HTTP API (`POST /mcp/execute`)
- [x] CMC storage for app records (bitemporal)
- [x] 81 MCP tools available for AIM-OS integration

### **Phase 1: Enhanced App Registry (Week 1-2)**
- [ ] App manifest schema (`aimos.json`) - Standardize format
- [ ] Enhanced `create_application` MCP tool - Add manifest validation
- [ ] Dependency resolution - Check app dependencies
- [ ] Resource allocation - Allocate resources based on manifest
- [ ] Token generation - Generate JWT tokens for apps
- [ ] Command Server endpoint: `POST /api/apps/register` - Enhanced registration API

### **Phase 2: App Discovery & Management (Week 3-4)**
- [ ] Command Server endpoint: `GET /api/apps` - App discovery
- [ ] Command Server endpoint: `GET /api/apps/:app_id` - Get app details
- [ ] Command Server endpoint: `POST /api/apps/:app_id/heartbeat` - Heartbeat system
- [ ] Command Server endpoint: `GET /api/apps/:app_id/metrics` - App metrics
- [ ] Health monitoring - Track app health via heartbeats
- [ ] Resource monitoring - Track resource usage per app

### **Phase 3: SDK Development (Week 5-6)**
- [ ] TypeScript SDK (`@aimos/sdk`) - Wraps Command Server HTTP API
- [ ] Python SDK (`aimos-sdk`) - Wraps Command Server HTTP API
- [ ] SDK documentation - Complete API reference
- [ ] SDK examples - Integration examples for common use cases

### **Phase 4: UI Integration (Week 7-8)**
- [ ] Panel registration system - Register panels from manifest
- [ ] Lazy loading infrastructure - Already exists in IDE DAC
- [ ] Panel communication protocol - Via MCP tools / Command Server
- [ ] Event system - Inter-app messaging via MCP tools

### **Phase 5: Advanced Features (Week 9-10)**
- [ ] Inter-app messaging - Via `send_ai_message` MCP tool
- [ ] Shared state system - Via CMC atoms with tags
- [ ] Service gateway - Token validation, permissions, rate limiting
- [ ] Auto-scaling - Resource-based scaling decisions

---

## 💡 **DESIGN PRINCIPLES**

### **1. Declarative Over Imperative**
Apps declare what they need, AIM-OS provides it automatically.

### **2. Always Integrated**
AIM-OS is not optional - every app is AIM-OS-aware by default.

### **3. Service-Oriented**
Apps consume AIM-OS services, don't reimplement them.

### **4. Observable**
All app operations are observable via AIM-OS monitoring.

### **5. Secure by Default**
Apps have minimal permissions, expanded only when needed.

### **6. Resource-Aware**
Apps declare resource needs, AIM-OS manages allocation.

### **7. Lifecycle-Managed**
Apps have clear lifecycle states managed by AIM-OS.

---

## 📚 **EXAMPLES**

### **Example 1: Simple Web App**

```json
{
  "app_id": "my-web-app",
  "app_name": "My Web App",
  "app_version": "1.0.0",
  "app_type": "web",
  "aimos_integration": {
    "required_services": ["cmc"],
    "optional_services": [],
    "capabilities": {
      "exposes_api": true,
      "exposes_ui": true
    },
    "api_endpoints": {
      "base_url": "http://localhost:3000"
    }
  }
}
```

### **Example 2: IDE Extension**

```json
{
  "app_id": "my-ide-extension",
  "app_name": "My IDE Extension",
  "app_version": "1.0.0",
  "app_type": "ide",
  "aimos_integration": {
    "required_services": ["cmc", "vif", "apoe"],
    "capabilities": {
      "exposes_ui": true
    },
    "ui_integration": {
      "panels": [
        {
          "id": "my-panel",
          "name": "My Panel",
          "location": "right",
          "lazy_load": true
        }
      ]
    }
  }
}
```

### **Example 3: CLI Tool**

```json
{
  "app_id": "my-cli-tool",
  "app_name": "My CLI Tool",
  "app_version": "1.0.0",
  "app_type": "cli",
  "aimos_integration": {
    "required_services": ["cmc", "apoe"],
    "capabilities": {
      "exposes_api": false,
      "exposes_ui": false
    }
  }
}
```

---

## 🎯 **NEXT STEPS**

1. **Review & Refine Protocol** - Get feedback on design
2. **Implement Core** - Build registration system
3. **Create SDK** - Build TypeScript/Python SDKs
4. **Document Examples** - Create integration examples
5. **Test with Real Apps** - Integrate existing apps
6. **Iterate** - Refine based on real-world usage

---

---

## 📋 **SUMMARY: KEY FINDINGS**

### **✅ What Already Exists**
1. **MCP Tools:** 81 MCP tools available, including `create_application`, `deploy_application`, `manage_application_lifecycle`
2. **Command Server:** HTTP API wrapper (`POST /mcp/execute`) for MCP tools
3. **CMC Integration:** App records stored in CMC atoms (bitemporal)
4. **Resource Tracking:** Frontend resource tracker exists (`resourceTracker.ts`)

### **🚧 What Needs Enhancement**
1. **App Registry:** Basic app management exists, needs manifest validation, dependency resolution, token generation
2. **App Discovery:** No discovery endpoint - apps query CMC directly
3. **SDK:** No SDK exists - apps call Command Server HTTP API directly
4. **Authentication:** No app tokens - all requests unauthenticated
5. **Resource Management:** Basic tracking exists, needs allocation and limits

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

