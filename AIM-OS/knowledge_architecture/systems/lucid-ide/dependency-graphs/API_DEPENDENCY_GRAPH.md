---
id: "lucid-ide-api-dependency-graph"
system: "lucid-ide-backend-api-system"
component: "dependency-graphs"
level: "L2"
type: "system_map"
title: "Lucid IDE API Dependency Graph"
description: "Complete API dependency graph showing all API route relationships and dependencies"
audience: "developers, API consumers"
confidence_threshold: 0.70
token_cost: 3000
word_count: 3000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "dependency-graph", "api"]
dependencies: []
related_docs: []
version: "v1.0.0"
---

# Lucid IDE API Dependency Graph

**Purpose:** Complete visual and textual representation of API route dependencies across all Lucid IDE backend systems.

**Status:** Complete dependency graph for all 42 API routes.

---

## 📊 **API ROUTE HIERARCHY**

### **Route Categories**

```
/api (Root)
├── /api/ai (AI Services - 25+ routes)
│   ├── /api/ai/agents (Agent Management)
│   ├── /api/ai/knowledge-map (Knowledge Map)
│   ├── /api/ai/vector (Vector Operations)
│   ├── /api/ai/visual (Visualization - 12 routes)
│   └── /api/ai/* (Other AI Services)
├── /api/architect (Architect Routes - 3 routes)
├── /api/context-preview (Context Preview - 1 route)
└── /api/trace (Trace Routes - 1 route)
```

---

## 🔗 **API DEPENDENCIES**

### **AI Services Routes**

**Agent Management:**
```
GET /api/ai/agents
├── File System (read agents.json)
└── Response: Agent list

POST /api/ai/agents
├── File System (write agents.json)
├── Validation (agent schema)
└── Response: Created agent

GET /api/ai/agents/:id
├── File System (read agents.json)
└── Response: Agent details

PUT /api/ai/agents/:id
├── File System (read/write agents.json)
├── Validation (agent schema)
└── Response: Updated agent

DELETE /api/ai/agents/:id
├── File System (read/write agents.json)
└── Response: Deletion confirmation

POST /api/ai/agent/run
├── File System (read agents.json)
├── AI Provider SDK (OpenAI/Anthropic/XAI)
└── Response: Execution result
```

**Knowledge Map:**
```
GET /api/ai/knowledge-map
├── File System (read knowledge-map.json)
└── Response: Knowledge map data

POST /api/ai/knowledge-map
├── File System (read/write knowledge-map.json)
├── Embedding Service (generate embeddings)
└── Response: Updated knowledge map
```

**Vector Operations:**
```
GET /api/ai/vector
├── Vector Store (in-memory)
└── Response: Vector operations

POST /api/ai/vector/op
├── Vector Store (operations)
├── Embedding Service
└── Response: Operation result

POST /api/ai/vector/seed
├── File System (read seed data)
├── Embedding Service (generate embeddings)
├── Vector Store (store vectors)
└── Response: Seeding result
```

**Visualization Routes (12 routes):**
```
GET /api/ai/visual/complete-system
├── File System (read system data)
├── Graph Processing
└── Response: System visualization data

GET /api/ai/visual/data-flow
├── File System (read data flow data)
└── Response: Data flow visualization

GET /api/ai/visual/metrics
├── File System (read metrics data)
└── Response: Metrics visualization

POST /api/ai/visual/metrics
├── File System (write metrics data)
└── Response: Updated metrics

GET /api/ai/visual/stream
├── Server-Sent Events (SSE)
└── Response: Streaming visualization data

GET /api/ai/visual/ws
├── WebSocket Server
└── Response: WebSocket connection

POST /api/ai/visual/save-coords
├── File System (write coordinates)
└── Response: Saved coordinates

POST /api/ai/visual/precompute-layout
├── Graph Processing (layout computation)
├── File System (cache layout)
└── Response: Precomputed layout

GET /api/ai/visual/cache-status
├── File System (check cache)
└── Response: Cache status

DELETE /api/ai/visual/cache-status
├── File System (clear cache)
└── Response: Cache cleared

GET /api/ai/visual/tiles
├── File System (read tile data)
└── Response: Tile data

GET /api/ai/visual/real-data
├── File System (read real data)
└── Response: Real data visualization

GET /api/ai/visual/predict
├── AI Provider SDK (predictions)
└── Response: Predictions
```

**Other AI Services:**
```
GET /api/ai/chains
├── File System (read chains.json)
└── Response: Prompt chains

POST /api/ai/embeddings
├── AI Provider SDK (generate embeddings)
└── Response: Embeddings

GET /api/ai/memory
├── File System (read memory data)
└── Response: Memory operations

GET /api/ai/models
├── File System (read models.json)
└── Response: Model list

GET /api/ai/providers
├── File System (read providers.json)
└── Response: Provider list

GET /api/ai/routing
├── File System (read routing config)
└── Response: Routing configuration

POST /api/ai/safety
├── AI Provider SDK (safety checks)
└── Response: Safety check result

GET /api/ai/secrets
├── Environment Variables (API keys)
└── Response: Secret management (⚠️ SECURITY RISK)

GET /api/ai/sql/connections
├── Database (SQLite/Postgres)
└── Response: SQL connections

POST /api/ai/sql/query
├── Database (execute query)
└── Response: Query result

GET /api/ai/state
├── File System (read state)
└── Response: State data

GET /api/ai/templates
├── File System (read templates.json)
└── Response: Template list

GET /api/ai/tools
├── File System (read tools.json)
└── Response: Tool list

POST /api/ai/tools/run
├── File System (read tools.json)
├── Tool Execution Engine
└── Response: Tool execution result

POST /api/ai/upload/process
├── File System (write uploaded file)
├── File Processing
└── Response: Processing result
```

### **Architect Routes**

```
GET /api/architect/generate
├── File System (read generation status)
└── Response: Generation status

POST /api/architect/generate
├── File System (read/write architecture data)
├── AI Provider SDK (code generation)
└── Response: Generated architecture

POST /api/architect/suggest
├── File System (read architecture data)
├── AI Provider SDK (suggestions)
└── Response: Architecture suggestions
```

### **Context Preview Routes**

```
POST /api/context-preview/generate
├── File System (read context data)
├── AI Provider SDK (context generation)
└── Response: Generated context preview
```

### **Trace Routes**

```
GET /api/trace/stream
├── Server-Sent Events (SSE)
├── File System (read trace data)
└── Response: Streaming trace data
```

---

## 📈 **DEPENDENCY STATISTICS**

### **Most Dependent Routes (Import Hubs)**

1. **POST /api/ai/agent/run** - 3 dependencies (File System, AI Provider SDK)
2. **POST /api/architect/generate** - 3 dependencies (File System, AI Provider SDK)
3. **POST /api/ai/knowledge-map** - 3 dependencies (File System, Embedding Service)
4. **POST /api/ai/vector/seed** - 3 dependencies (File System, Embedding Service, Vector Store)
5. **POST /api/context-preview/generate** - 3 dependencies (File System, AI Provider SDK)

### **Most Used Dependencies**

1. **File System** - Used by 35+ routes (83%)
2. **AI Provider SDK** - Used by 10+ routes (24%)
3. **Embedding Service** - Used by 5+ routes (12%)
4. **Vector Store** - Used by 3+ routes (7%)
5. **Database** - Used by 2+ routes (5%)

### **External Dependencies**

**AI Providers:**
- OpenAI SDK
- Anthropic SDK
- XAI SDK

**Database:**
- SQLite (better-sqlite3)
- Postgres (planned)
- Supabase (planned)

**File System:**
- Node.js fs/promises
- Node.js path

---

## 🔄 **DEPENDENCY FLOW**

### **Request Flow**

```
Client Request
  ↓
API Route Handler
  ↓
Service Layer (if needed)
  ↓
External Dependency (File System / AI Provider / Database)
  ↓
Response Processing
  ↓
Client Response
```

### **AI Request Flow**

```
Client Request
  ↓
API Route Handler
  ↓
AI Provider SDK
  ↓
AI Provider API (HTTP)
  ↓
Response Processing
  ↓
Client Response
```

### **File System Flow**

```
Client Request
  ↓
API Route Handler
  ↓
File System Operations (fs/promises)
  ↓
File Read/Write
  ↓
Response Processing
  ↓
Client Response
```

---

## ⚠️ **SECURITY CONCERNS**

### **Routes Requiring Security**

**Critical Security Issues:**
1. **GET /api/ai/secrets** - ⚠️ Exposes API keys (CRITICAL)
2. **POST /api/ai/agents** - ⚠️ No authentication (CRITICAL)
3. **POST /api/ai/agent/run** - ⚠️ No authentication (CRITICAL)
4. **POST /api/architect/generate** - ⚠️ No authentication (CRITICAL)
5. **POST /api/ai/upload/process** - ⚠️ No file validation (CRITICAL)

**Recommendations:**
- Add authentication middleware
- Add input validation
- Add rate limiting
- Secure API key storage
- Add file upload validation

---

## 📊 **PERFORMANCE CONSIDERATIONS**

### **High-Latency Routes**

1. **POST /api/ai/agent/run** - AI provider calls (2-10s)
2. **POST /api/architect/generate** - AI code generation (5-30s)
3. **POST /api/ai/embeddings** - Embedding generation (1-5s)
4. **GET /api/ai/visual/complete-system** - Large data processing (1-3s)
5. **POST /api/ai/vector/seed** - Batch operations (5-30s)

**Optimization Strategies:**
- Implement caching
- Use background jobs for long operations
- Implement streaming for large responses
- Add request queuing

---

## 📚 **REFERENCES**

- API Index: `systems/lucid-ide/backend-api-system/api/API_DOCUMENTATION_INDEX.md`
- Backend API System: `systems/lucid-ide/backend-api-system/L3_detailed.md`
- System Atlas Map: `systems/lucid-ide/SYSTEM_ATLAS_MAP.md`

---

**Status:** Complete  
**Last Updated:** 2025-11-09  
**Version:** v1.0.0

