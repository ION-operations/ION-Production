# AIM-OS Infrastructure Architecture Overview

**Purpose:** Clarify the relationship between Command Server, Cursor Extension, Daemon RAG System, and Organizer App.

---

## 🏗️ **SYSTEM ARCHITECTURE**

### **1. Cursor Extension (Command Server)**
**Location:** `cursor-addon/src/commandServer.ts`  
**Port:** `5001`  
**Type:** HTTP Server (Node.js/TypeScript)  
**Purpose:** Bridge between VS Code/Cursor IDE and external clients

**Key Features:**
- Exposes VS Code API via HTTP endpoints
- Executes MCP tools via MCP Client
- Reads Cursor IDE state (terminals, editor, workspace, problems)
- Handles bulletproof messaging protocol
- Manages agent automation (Cursor Cloud API)

**Endpoints:**
- `GET /health` - Health check
- `POST /mcp/execute` - Execute MCP tools
- `GET /cursor/*` - Read Cursor state
- `POST /messaging/send` - Send messages
- `POST /agent/*` - Agent automation
- `POST /aimos/chat` - AIM-OS chat integration

**Relationship:**
- Runs inside Cursor IDE extension host
- Can be called by external clients (Electron app, daemon, CLI)
- Connects to Python MCP Server via stdio

---

### **2. Daemon RAG System**
**Location:** `daemon_rag_system/`  
**Port:** `5000` (HTTP API Server)  
**Type:** Python FastAPI Server  
**Purpose:** Intelligent MCP tool selection and server management

**Key Features:**
- Context-aware tool selection (solves 40-tool limit)
- Dynamic MCP server loading/unloading
- RAG-based learning and pattern recognition
- Performance monitoring and optimization
- Resource management

**HTTP API Server:**
- `GET /health` - Health check
- `POST /request` - Process request with tool selection
- `GET /status` - System status
- `GET /tools` - List available tools

**Relationship:**
- Can be called by Command Server or directly by clients
- Manages MCP tool selection intelligently
- Learns from usage patterns
- Works alongside Command Server (different ports)

---

### **3. Organizer App**
**Location:** `Documentation/appexamples/organizer/organizerapp/`  
**Type:** React/Vite Application  
**Purpose:** Example application demonstrating Helixion architecture

**Key Features:**
- Helixion core visualization
- Query interface
- Results display
- Control panel
- Glyph visualization

**Relationship:**
- Standalone example application
- Demonstrates architectural patterns
- Not directly connected to Command Server or Daemon
- Can be used as reference for DAC v2 IDE development

---

## 🔄 **HOW THEY RELATE**

### **Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                    External Clients                         │
│  (Electron App, CLI Tools, Browser Apps)                   │
└─────┬───────────────────────┬───────────────────────────────┘
      │                       │
      │ HTTP (5001)           │ HTTP (5000)
      │                       │
      ▼                       ▼
┌─────────────────┐   ┌──────────────────────────────┐
│  Command Server  │   │  Daemon RAG System          │
│  (Cursor Ext)    │   │  (Python FastAPI)           │
│  Port: 5001      │   │  Port: 5000                  │
└─────┬────────────┘   └──────┬───────────────────────┘
      │                       │
      │ VS Code API           │ Tool Selection
      │ MCP Client             │ Server Management
      │                        │
      ▼                       ▼
┌─────────────────┐   ┌──────────────────────────────┐
│  Cursor IDE     │   │  Python MCP Server          │
│  (VS Code API)  │   │  (lucid_mcp_server.py)     │
└─────────────────┘   └──────────────────────────────┘
```

### **Communication Flow**

**Scenario 1: External Client → Command Server → MCP**
```
Electron App → POST /mcp/execute → Command Server → MCP Client → Python MCP Server
```

**Scenario 2: External Client → Daemon RAG → Tool Selection**
```
CLI Tool → POST /request → Daemon RAG → Selects Tools → Returns Results
```

**Scenario 3: Command Server → Daemon RAG (Future Integration)**
```
Command Server → POST /request → Daemon RAG → Intelligent Tool Selection
```

---

## 🎯 **FOR DAC V2 IDE CACHE CLEARING**

### **Option 1: Add to Command Server (Recommended)**
**Why:**
- Command Server already handles dev server management
- Can be called from IDE UI or external tools
- Integrates with existing infrastructure
- Port 5001 already in use

**Implementation:**
- Add `/dev/vite/cache/clear` endpoint to `commandServer.ts`
- Can detect DAC v2 IDE project path
- Clear Vite cache directories
- Optionally restart dev server

**Pros:**
- Uses existing infrastructure
- Consistent with other dev server endpoints
- Can be called from IDE or external tools

**Cons:**
- Requires Cursor extension to be running
- Only works when Cursor is active

---

### **Option 2: Add to Daemon RAG System**
**Why:**
- Daemon already has HTTP API server
- Can be called independently
- Could learn from cache clearing patterns

**Implementation:**
- Add `/dev/vite/cache/clear` endpoint to `http_api_server.py`
- Use Python file system operations
- Can integrate with tool selection

**Pros:**
- Independent of Cursor extension
- Can learn and optimize cache clearing
- Works even if Cursor isn't running

**Cons:**
- Less integrated with IDE
- Requires separate server running
- Different port (5000 vs 5001)

---

### **Option 3: Standalone Service**
**Why:**
- Completely independent
- Can be called from anywhere
- Simple implementation

**Implementation:**
- Create new HTTP server (port 5002 or different)
- Simple cache clearing endpoints
- No dependencies on other systems

**Pros:**
- Simple and focused
- No dependencies
- Easy to test

**Cons:**
- Another service to manage
- Less integrated
- More infrastructure overhead

---

## 💡 **RECOMMENDATION**

### **Hybrid Approach: Command Server + IDE UI**

**Phase 1: Command Server Endpoint**
- Add `/dev/vite/cache/clear` to Command Server
- Can be called programmatically
- Works with existing infrastructure

**Phase 2: IDE UI Button**
- Add "Clear Cache" button to DAC v2 IDE
- Calls Command Server endpoint
- Shows cache statistics

**Phase 3: Optional Daemon Integration**
- Daemon can learn cache clearing patterns
- Optimize cache clearing strategies
- Provide recommendations

---

## 📋 **IMPLEMENTATION PLAN**

### **Step 1: Add Command Server Endpoint**
```typescript
// In commandServer.ts
if (pathname === '/dev/vite/cache/clear') {
    const projectPath = query.project as string || workspaceRoot;
    const cacheTypes = query.types ? (query.types as string).split(',') : ['all'];
    const restart = query.restart === 'true';
    const result = await this.handleClearViteCache(projectPath, cacheTypes, restart);
    this.sendSuccess(res, result);
    return;
}
```

### **Step 2: Implement Cache Clearing Logic**
```typescript
private async handleClearViteCache(
    projectPath: string,
    cacheTypes: string[],
    restart: boolean
): Promise<any> {
    // Clear Vite cache directories
    // Optionally restart dev server
    // Return statistics
}
```

### **Step 3: Add IDE UI Button**
```tsx
// In DAC v2 IDE toolbar
<button onClick={handleClearCache}>
    <RefreshCw /> Clear Cache
</button>
```

---

## 🔗 **INTEGRATION POINTS**

### **Command Server**
- Already has dev server management patterns
- Can detect workspace root
- Has file system access
- Can execute shell commands

### **DAC v2 IDE**
- Can call Command Server via HTTP
- Has UI for buttons and dialogs
- Can show cache statistics
- Can trigger dev server restart

### **Daemon RAG System**
- Could learn optimal cache clearing strategies
- Could predict when cache clearing is needed
- Could optimize cache sizes

---

## 🎯 **NEXT STEPS**

1. **Review Architecture** - Confirm understanding of systems
2. **Choose Approach** - Command Server vs Daemon vs Standalone
3. **Implement Endpoint** - Add cache clearing to chosen system
4. **Add UI Integration** - Create IDE button and UI
5. **Test & Iterate** - Verify functionality and improve

---

**Status:** Ready for implementation  
**Recommendation:** Start with Command Server endpoint (Phase 1)  
**Integration:** Can extend to Daemon RAG later for learning

