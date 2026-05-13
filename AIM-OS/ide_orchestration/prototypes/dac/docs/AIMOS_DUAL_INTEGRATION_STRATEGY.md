---
id: "aimos_dual_integration_strategy"
type: "architecture"
title: "AIM-OS Dual Integration Strategy - MCP + REST API"
description: "Dual integration approach: MCP for bootstrapping to existing tools, REST API for true LLM integration"
author: "aether"
version: "v1.0.0"
created: "2025-01-27T00:00:00Z"
updated: "2025-01-27T00:00:00Z"
status: "ready"
tags: ["architecture", "strategy", "mcp", "rest-api", "integration"]
---

# AIM-OS Dual Integration Strategy

**Purpose:** Dual integration approach - MCP for bootstrapping to existing tools, REST API for true LLM integration  
**Strategy:** Build both - MCP for compatibility, REST API for direct integration  
**Status:** Strategy Document

---

## 🎯 **THE DUAL STRATEGY**

### **Two Integration Paths:**

1. **MCP Server + AIM-OS Core**
   - ✅ **For:** Bootstrapping AIM-OS to existing tools (Cursor, chat AIs)
   - ✅ **Benefit:** Works with any MCP-compatible tool
   - ✅ **Use Case:** Quick integration with existing ecosystems

2. **REST API + AIM-OS Core**
   - ✅ **For:** True LLM API connection, custom LLM integration, evolving systems
   - ✅ **Benefit:** Direct access, full control, custom protocols
   - ✅ **Use Case:** Deep integration, custom LLMs, future evolution

**Both coexist and serve different purposes!**

---

## 🏗️ **COMPLETE ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────────────────┐
│              AIM-OS CORE (The Real System)                              │
│              Standalone Python Backend                                  │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  CMC, HHNI, VIF, APOE, SEG, CAS, TCS                            │  │
│  │  Production-ready, independent systems                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└───────────────────┬───────────────────────────┬───────────────────────────┘
                    │                           │
                    │ Direct Python calls       │ Direct Python calls
                    │                           │
        ┌───────────▼───────────┐   ┌───────────▼───────────┐
        │                       │   │                       │
        │   MCP Server          │   │   REST API Server     │
        │   (Integration 1)     │   │   (Integration 2)     │
        │                       │   │                       │
        │  - Exposes as MCP     │   │  - Direct HTTP API    │
        │  - JSON-RPC 2.0        │   │  - REST endpoints     │
        │  - stdio/HTTP          │   │  - Full control       │
        │                       │   │  - Custom protocols   │
        └───────────┬───────────┘   └───────────┬───────────┘
                    │                           │
                    │ MCP Protocol              │ HTTP/REST
                    │                           │
        ┌───────────▼───────────┐   ┌───────────▼───────────┐
        │                       │   │                       │
        │   Existing Tools      │   │   Custom LLMs         │
        │                       │   │                       │
        │  - Cursor IDE         │   │  - Custom LLM APIs     │
        │  - Chat AIs           │   │  - Evolving systems   │
        │  - MCP-compatible     │   │  - Direct integration │
        │                       │   │  - Future protocols   │
        └───────────────────────┘   └───────────────────────┘
```

---

## 🔌 **INTEGRATION PATH 1: MCP SERVER**

### **Purpose: Bootstrapping to Existing Tools**

**Target Users:**
- Cursor IDE users
- Chat AI applications
- Any MCP-compatible tool
- Quick integration scenarios

**Benefits:**
- ✅ **Compatibility:** Works with existing MCP ecosystem
- ✅ **Quick Integration:** No custom API needed
- ✅ **Standard Protocol:** JSON-RPC 2.0 (MCP standard)
- ✅ **Tool Discovery:** Automatic tool listing
- ✅ **Low Friction:** Works out of the box

**Architecture:**
```
Existing Tool (Cursor, Chat AI)
    ↓ MCP Protocol (JSON-RPC 2.0)
MCP Server (lucid_mcp_server.py)
    ↓ Direct Python calls
AIM-OS Core (CMC, HHNI, VIF, etc.)
```

**Current Status:**
- ✅ **MCP Server exists** (`lucid_mcp_server.py`)
- ✅ **59 tools registered**
- ✅ **Working with Cursor**
- ✅ **Can work with any MCP-compatible tool**

**Use Cases:**
1. **Cursor IDE Integration**
   - Users get AIM-OS capabilities in Cursor
   - No Cursor modification needed
   - Works with standard Cursor

2. **Chat AI Integration**
   - Chat AIs can use AIM-OS via MCP
   - Memory, retrieval, orchestration
   - Standard protocol

3. **Tool Ecosystem**
   - Any MCP-compatible tool
   - Quick integration
   - No custom API needed

---

## 🌐 **INTEGRATION PATH 2: REST API**

### **Purpose: True LLM Integration & Custom Systems**

**Target Users:**
- Custom LLM applications
- Direct API integration
- Evolving systems
- Future protocols

**Benefits:**
- ✅ **Direct Access:** No protocol translation
- ✅ **Full Control:** Custom endpoints, protocols
- ✅ **Performance:** Direct calls, no overhead
- ✅ **Flexibility:** Custom authentication, rate limiting
- ✅ **Evolution:** Can evolve with custom protocols

**Architecture:**
```
Custom LLM / Evolving System
    ↓ HTTP/REST
REST API Server (New - To Build)
    ↓ Direct Python calls
AIM-OS Core (CMC, HHNI, VIF, etc.)
```

**To Build:**
- ⚠️ **REST API Server** (new component)
- ⚠️ **Endpoints for all AIM-OS systems**
- ⚠️ **Authentication & security**
- ⚠️ **Rate limiting & monitoring**

**Proposed Endpoints:**
```
# CMC (Memory)
POST   /api/v1/cmc/store          → Store memory atom
GET    /api/v1/cmc/retrieve       → Retrieve atoms
GET    /api/v1/cmc/stats          → Memory statistics

# HHNI (Search)
POST   /api/v1/hhni/search        → Semantic search
GET    /api/v1/hhni/context        → Get context
POST   /api/v1/hhni/index         → Index content

# VIF (Verification)
POST   /api/v1/vif/track          → Track confidence
GET    /api/v1/vif/witness        → Get witness
POST   /api/v1/vif/validate       → Validate operation

# APOE (Orchestration)
POST   /api/v1/apoe/create-plan   → Create execution plan
POST   /api/v1/apoe/execute       → Execute plan
GET    /api/v1/apoe/status         → Plan status

# SEG (Knowledge)
POST   /api/v1/seg/synthesize     → Synthesize knowledge
GET    /api/v1/seg/contradictions → Find contradictions
POST   /api/v1/seg/entities       → Get entities

# CAS (Cognitive)
GET    /api/v1/cas/metrics         → Cognitive metrics
POST   /api/v1/cas/analyze         → Cognitive analysis
GET    /api/v1/cas/drift           → Detect drift

# TCS (Timeline)
POST   /api/v1/tcs/add-entry       → Add timeline entry
GET    /api/v1/tcs/summary         → Get timeline summary
GET    /api/v1/tcs/entries         → Query timeline
```

**Use Cases:**
1. **Custom LLM Integration**
   - Direct API calls from custom LLMs
   - Full control over integration
   - Custom protocols possible

2. **Evolving Systems**
   - Systems that need to evolve
   - Custom authentication
   - Future protocol support

3. **True LLM API Connection**
   - Direct connection to LLM APIs
   - No protocol translation
   - Maximum performance

---

## 🔄 **HOW BOTH COEXIST**

### **Shared Core:**

```
┌─────────────────────────────────────────────────────────────┐
│              AIM-OS CORE (Shared)                           │
│              Single source of truth                          │
│                                                              │
│  - CMC, HHNI, VIF, APOE, SEG, CAS, TCS                     │
│  - All systems accessible via both paths                   │
│  - Same data, same operations                               │
└───────────────────┬───────────────────┬─────────────────────┘
                    │                   │
        ┌───────────▼───────────┐   ┌───▼──────────────────────┐
        │                       │   │                          │
        │   MCP Server          │   │   REST API Server        │
        │   (Path 1)            │   │   (Path 2)                │
        │                       │   │                          │
        │  - MCP Protocol       │   │  - REST Protocol          │
        │  - JSON-RPC 2.0       │   │  - HTTP/JSON             │
        │  - Tool discovery     │   │  - Custom endpoints       │
        │                       │   │                          │
        └───────────────────────┘   └──────────────────────────┘
```

**Key Points:**
- ✅ **Same Core:** Both use same AIM-OS Core
- ✅ **Same Data:** Both access same memory, same systems
- ✅ **Different Protocols:** MCP vs REST
- ✅ **Different Use Cases:** Existing tools vs custom systems

---

## 🎯 **WHEN TO USE WHICH**

### **Use MCP Server When:**
- ✅ Integrating with Cursor IDE
- ✅ Integrating with existing chat AIs
- ✅ Quick integration needed
- ✅ Standard MCP protocol works
- ✅ Tool discovery needed

### **Use REST API When:**
- ✅ Custom LLM integration
- ✅ Direct API access needed
- ✅ Custom protocols required
- ✅ Performance critical
- ✅ Evolving systems
- ✅ Future protocol support

---

## 🚀 **IMPLEMENTATION PLAN**

### **Phase 1: Keep MCP Server (Current)**
- ✅ **Status:** Already working
- ✅ **Action:** Maintain and enhance
- ✅ **Goal:** Keep bootstrapping capability

### **Phase 2: Build REST API (New)**
- ⚠️ **Status:** To be built
- ⚠️ **Action:** Create REST API server
- ⚠️ **Goal:** Direct integration capability

### **Phase 3: Enhance Both**
- ⚠️ **Status:** Future
- ⚠️ **Action:** Optimize both paths
- ⚠️ **Goal:** Best of both worlds

---

## 📋 **REST API IMPLEMENTATION PLAN**

### **Step 1: Create REST API Server**

**File:** `packages/aimos_api_server/aimos_api.py`

**Framework Options:**
- FastAPI (recommended - async, auto-docs, type hints)
- Flask (simpler, but less features)
- Django REST (overkill for API-only)

**Structure:**
```python
# packages/aimos_api_server/aimos_api.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from packages.cmc_service import CMCService
from packages.hhni import HHNIService
# ... other imports

app = FastAPI(title="AIM-OS REST API", version="1.0.0")

# CORS for browser access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AIM-OS services
cmc = CMCService()
hhni = HHNIService()
# ... other services

# CMC Endpoints
@app.post("/api/v1/cmc/store")
async def store_memory(atom_data: dict):
    """Store memory atom in CMC"""
    result = await cmc.store_atom(**atom_data)
    return {"success": True, "atom_id": result.atom_id}

@app.get("/api/v1/cmc/retrieve")
async def retrieve_memory(query: str, limit: int = 10):
    """Retrieve memory atoms from CMC"""
    atoms = await cmc.retrieve_atoms(query, limit)
    return {"success": True, "atoms": atoms}

# ... more endpoints for all systems
```

### **Step 2: Add Authentication**

**Options:**
- API Keys (simple)
- JWT tokens (standard)
- OAuth2 (enterprise)

**Recommended:** Start with API keys, evolve to JWT

### **Step 3: Add Rate Limiting**

**Options:**
- Token bucket
- Sliding window
- Per-user limits

**Recommended:** Token bucket (simple, effective)

### **Step 4: Add Monitoring**

**Options:**
- Prometheus metrics
- Custom logging
- Health checks

**Recommended:** Health checks + basic metrics

### **Step 5: Documentation**

**Options:**
- OpenAPI/Swagger (auto-generated with FastAPI)
- Custom docs
- Postman collection

**Recommended:** OpenAPI (auto-generated)

---

## 🎯 **BENEFITS OF DUAL STRATEGY**

### **For Users:**
- ✅ **Choice:** Use MCP for quick integration, REST for deep integration
- ✅ **Compatibility:** Works with existing tools (MCP) and custom systems (REST)
- ✅ **Flexibility:** Choose the right integration path

### **For AIM-OS:**
- ✅ **Broader Reach:** MCP for ecosystem, REST for custom
- ✅ **Future-Proof:** Both paths can evolve independently
- ✅ **Performance:** REST for direct access, MCP for compatibility

### **For Development:**
- ✅ **Clear Separation:** MCP = compatibility, REST = direct access
- ✅ **Independent Evolution:** Can enhance each path separately
- ✅ **Testing:** Can test both paths independently

---

## 📊 **COMPARISON TABLE**

| Feature | MCP Server | REST API |
|---------|-----------|----------|
| **Protocol** | JSON-RPC 2.0 (MCP) | HTTP/REST |
| **Use Case** | Existing tools | Custom systems |
| **Integration** | Quick, standard | Direct, flexible |
| **Performance** | Protocol overhead | Direct calls |
| **Discovery** | Automatic (MCP) | Manual (docs) |
| **Flexibility** | Standard protocol | Custom protocols |
| **Status** | ✅ Working | ⚠️ To build |

---

## 🚀 **NEXT STEPS**

### **Immediate:**
1. ✅ **Keep MCP Server** - Maintain current functionality
2. ⚠️ **Design REST API** - Plan endpoints and structure
3. ⚠️ **Create REST API Server** - Build FastAPI server

### **Short-term:**
1. ⚠️ **Add Authentication** - API keys or JWT
2. ⚠️ **Add Rate Limiting** - Protect API
3. ⚠️ **Add Documentation** - OpenAPI/Swagger

### **Long-term:**
1. ⚠️ **Optimize Both** - Performance improvements
2. ⚠️ **Enhance Features** - Add capabilities
3. ⚠️ **Evolve Protocols** - Future support

---

## 📋 **SUMMARY**

### **The Strategy:**
- ✅ **MCP Server** - For bootstrapping to existing tools (Cursor, chat AIs)
- ✅ **REST API** - For true LLM integration, custom systems, evolving protocols

### **Both Coexist:**
- ✅ Same AIM-OS Core
- ✅ Same data, same operations
- ✅ Different protocols, different use cases

### **Benefits:**
- ✅ **Compatibility:** MCP works with existing ecosystem
- ✅ **Flexibility:** REST allows custom integration
- ✅ **Future-Proof:** Both can evolve independently

**This is the perfect dual-strategy approach!** 🎯

---

**Status:** Strategy Document Complete  
**Confidence:** 0.95 (High - clear strategy)

**Build both - MCP for compatibility, REST for true integration!**

