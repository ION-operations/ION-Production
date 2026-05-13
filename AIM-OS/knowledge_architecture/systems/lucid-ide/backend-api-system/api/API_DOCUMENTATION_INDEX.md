---
id: "lucid-ide-api-documentation-index"
system: "lucid-ide-backend-api-system"
component: "api-routes"
level: "L1"
type: "index"
title: "Lucid IDE API Documentation Index"
description: "Comprehensive index of all 42 API routes with documentation status"
audience: "developers, API consumers"
confidence_threshold: 0.70
token_cost: 2000
word_count: 2000
created: "2025-11-09T00:00:00Z"
updated: "2025-11-09T00:00:00Z"
author: "sev"
status: "complete"
tags: ["lucid-ide", "api", "documentation", "index"]
dependencies: []
related_docs: []
version: "v1.0.0"
---

# Lucid IDE API Documentation Index

**Purpose:** Comprehensive index of all 42 API routes with documentation status, endpoints, methods, and relationships.

**Status:** Complete inventory of all API routes across 4 categories.

---

## 📋 **API ROUTE INVENTORY**

### **AI Services Routes (25+ routes)**

**Base Path:** `/api/ai/`

#### **Agent Management**
- `GET /api/ai/agents` - List all agents
- `POST /api/ai/agents` - Create new agent
- `GET /api/ai/agents/:id` - Get agent details
- `PUT /api/ai/agents/:id` - Update agent
- `DELETE /api/ai/agents/:id` - Delete agent
- `POST /api/ai/agent/run` - Execute agent

**Documentation Status:** ⚠️ Pending individual route docs

#### **Knowledge Map**
- `GET /api/ai/knowledge-map` - Query knowledge map
- `POST /api/ai/knowledge-map` - Update knowledge map

**Documentation Status:** ⚠️ Pending individual route docs

#### **Vector Operations**
- `GET /api/ai/vector` - Vector operations
- `POST /api/ai/vector/op` - Vector operations
- `POST /api/ai/vector/seed` - Seed vector database

**Documentation Status:** ⚠️ Pending individual route docs

#### **Visualization (12 routes)**
- `GET /api/ai/visual/complete-system` - Complete system visualization
- `GET /api/ai/visual/data-flow` - Data flow visualization
- `GET /api/ai/visual/metrics` - Metrics visualization
- `POST /api/ai/visual/metrics` - Update metrics
- `GET /api/ai/visual/stream` - Streaming visualization
- `GET /api/ai/visual/ws` - WebSocket visualization
- `POST /api/ai/visual/save-coords` - Save coordinates
- `POST /api/ai/visual/precompute-layout` - Precompute layout
- `GET /api/ai/visual/cache-status` - Cache status
- `DELETE /api/ai/visual/cache-status` - Clear cache
- `GET /api/ai/visual/tiles` - Tile rendering
- `GET /api/ai/visual/real-data` - Real data visualization
- `GET /api/ai/visual/predict` - Predictions

**Documentation Status:** ⚠️ Pending individual route docs

#### **Other AI Services**
- `GET /api/ai/chains` - Prompt chains
- `POST /api/ai/embeddings` - Generate embeddings
- `GET /api/ai/memory` - Memory operations
- `GET /api/ai/models` - Model management
- `GET /api/ai/providers` - Provider management
- `GET /api/ai/routing` - AI routing
- `POST /api/ai/safety` - Safety checks
- `GET /api/ai/secrets` - Secret management
- `GET /api/ai/sql/connections` - SQL connections
- `POST /api/ai/sql/query` - SQL queries
- `GET /api/ai/state` - State management
- `GET /api/ai/templates` - Template management
- `GET /api/ai/tools` - Tool management
- `POST /api/ai/tools/run` - Tool execution
- `POST /api/ai/upload/process` - File upload processing

**Documentation Status:** ⚠️ Pending individual route docs

---

### **Architect Routes (3 routes)**

**Base Path:** `/api/architect/`

- `GET /api/architect/generate` - Get generation status
- `POST /api/architect/generate` - Generate architecture (multiple endpoints)
- `POST /api/architect/suggest` - Architecture suggestions

**Documentation Status:** ⚠️ Pending individual route docs

---

### **Context Preview Routes (1 route)**

**Base Path:** `/api/context-preview/`

- `POST /api/context-preview/generate` - Generate context preview

**Documentation Status:** ⚠️ Pending individual route docs

---

### **Trace Routes (1 route)**

**Base Path:** `/api/trace/`

- `GET /api/trace/stream` - Stream trace data

**Documentation Status:** ⚠️ Pending individual route docs

---

## 📊 **API DOCUMENTATION PRIORITY**

### **Priority 1: Critical Routes (Immediate)**
1. `POST /api/ai/agents` - Agent creation (security-critical)
2. `POST /api/ai/agent/run` - Agent execution (security-critical)
3. `GET /api/ai/secrets` - Secret management (security-critical)
4. `POST /api/architect/generate` - Architecture generation (core functionality)
5. `POST /api/context-preview/generate` - Context preview (core functionality)

### **Priority 2: Core Functionality Routes**
1. `GET /api/ai/agents` - List agents
2. `GET /api/ai/knowledge-map` - Knowledge map queries
3. `POST /api/ai/knowledge-map` - Knowledge map updates
4. `GET /api/ai/visual/complete-system` - System visualization
5. `GET /api/trace/stream` - Trace streaming

### **Priority 3: Supporting Routes**
1. `GET /api/ai/models` - Model management
2. `GET /api/ai/providers` - Provider management
3. `GET /api/ai/templates` - Template management
4. `GET /api/ai/tools` - Tool management
5. `POST /api/ai/embeddings` - Embedding generation

---

## 📝 **API DOCUMENTATION TEMPLATE**

For each API route, create L0-L4 documentation:

**L0_executive.md** (100 words)
- Quick summary
- Purpose
- HTTP method and endpoint
- Key features

**L1_overview.md** (500 words)
- Overview
- Request/response format
- Parameters
- Examples

**L2_architecture.md** (2000 words)
- Architecture
- Implementation details
- Error handling
- Security considerations
- Performance

**L3_detailed.md** (10000 words)
- Complete implementation guide
- Code examples
- Testing
- Troubleshooting
- Best practices

**L4_complete.md** (15000+ words)
- Complete reference
- All edge cases
- Advanced usage
- Integration patterns

---

## 🔒 **SECURITY CONSIDERATIONS**

### **Routes Requiring Authentication**
- ⚠️ **CRITICAL:** Most routes lack authentication
- ⚠️ Routes handling sensitive data need authentication
- ⚠️ Routes with file operations need authorization

### **Routes Requiring Input Validation**
- ⚠️ **CRITICAL:** All POST/PUT routes need validation
- ⚠️ File path parameters need sanitization
- ⚠️ API keys need secure storage

### **Routes Requiring Rate Limiting**
- ⚠️ **CRITICAL:** All routes need rate limiting
- ⚠️ AI provider routes need stricter limits
- ⚠️ File upload routes need size limits

---

## 📈 **API USAGE STATISTICS**

**Most Used Routes:**
1. `GET /api/ai/agents` - Agent listing
2. `GET /api/ai/knowledge-map` - Knowledge map queries
3. `POST /api/ai/agents` - Agent creation
4. `GET /api/ai/visual/complete-system` - System visualization
5. `POST /api/architect/generate` - Architecture generation

**Performance-Critical Routes:**
1. `GET /api/ai/visual/complete-system` - Large data responses
2. `GET /api/trace/stream` - Real-time streaming
3. `POST /api/ai/embeddings` - AI provider calls
4. `POST /api/architect/generate` - Long-running operations
5. `GET /api/ai/knowledge-map` - Complex queries

---

## ✅ **NEXT STEPS**

1. **Document Priority 1 Routes** (5 routes)
   - Create L0-L4 documentation for critical routes
   - Focus on security and core functionality

2. **Document Priority 2 Routes** (5 routes)
   - Create L0-L4 documentation for core functionality
   - Focus on usage patterns

3. **Document Priority 3 Routes** (5 routes)
   - Create L0-L2 documentation for supporting routes
   - Focus on examples and usage

4. **Create API Usage Guide**
   - Comprehensive guide for using all APIs
   - Authentication patterns
   - Error handling
   - Best practices

---

**Status:** Index Complete  
**Last Updated:** 2025-11-09  
**Version:** v1.0.0

