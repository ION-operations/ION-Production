# MCP Architecture Explanation

**Date:** 2025-01-27  
**Question:** Does the IDE prototype use the Cursor MCP extension?  
**Answer:** YES, but indirectly via Command Server HTTP API

---

## 🔄 **Complete Architecture Flow**

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
│  │  Command Server (commandServer.ts)                    │  │
│  │  - HTTP Server on port 5001                           │  │
│  │  - Endpoint: /mcp/execute                              │  │
│  │  - Uses MCPClient to call MCP tools                   │  │
│  └──────────────────────┬──────────────────────────────────┘  │
│                         │                                      │
│  ┌──────────────────────▼──────────────────────────────────┐  │
│  │  MCPClient (mcp/mcpClient.ts)                          │  │
│  │  - Spawns Python process (lucid_mcp_server.py)         │  │
│  │  - Communicates via stdio (JSON-RPC 2.0)               │  │
│  └──────────────────────┬──────────────────────────────────┘  │
└──────────────────────────┼─────────────────────────────────────┘
                            │ JSON-RPC 2.0 (stdio)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│         MCP Server (lucid_mcp_server.py)                    │
│  - Python process spawned by MCPClient                       │
│  - Implements 59 MCP tools                                  │
│  - Connects to AIM-OS backend                              │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              AIM-OS Backend                                  │
│  - CMC, HHNI, VIF, SEG, APOE, CAS, TCS                      │
│  - All systems and services                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ **Yes, It Uses Cursor MCP Extension!**

**The IDE prototype DOES use the Cursor MCP extension, but:**

1. **Not directly via MCP protocol** - It doesn't use JSON-RPC 2.0 directly
2. **Via Command Server HTTP API** - It calls `http://localhost:5001/mcp/execute`
3. **Command Server is part of Cursor extension** - It's in `cursor-addon/src/commandServer.ts`
4. **Command Server uses MCPClient** - Which connects to MCP server via JSON-RPC 2.0

---

## 📋 **Key Components**

### **1. IDE Prototype (DAC)**
- **MCPService.ts** - Calls Command Server HTTP API
- **Location:** `ide_orchestration/prototypes/dac/src/services/MCPService.ts`
- **Endpoint:** `http://localhost:5001/mcp/execute`

### **2. Command Server (Cursor Extension)**
- **commandServer.ts** - HTTP server on port 5001
- **Location:** `cursor-addon/src/commandServer.ts`
- **Endpoint:** `/mcp/execute` - Receives HTTP requests, calls MCPClient

### **3. MCPClient (Cursor Extension)**
- **mcpClient.ts** - Connects to MCP server
- **Location:** `cursor-addon/src/mcp/mcpClient.ts`
- **Function:** Spawns Python process, communicates via stdio (JSON-RPC 2.0)

### **4. MCP Server (Python)**
- **lucid_mcp_server.py** - Python MCP server
- **Location:** Workspace root
- **Function:** Implements 59 MCP tools, connects to AIM-OS backend

---

## 🔍 **Code Evidence**

### **IDE Prototype Calls Command Server:**
```typescript
// ide_orchestration/prototypes/dac/src/services/MCPService.ts
const COMMAND_SERVER_URL = 'http://localhost:5001'
const MCP_EXECUTE_ENDPOINT = '/mcp/execute'

async executeTool(tool: string, arguments_: Record<string, any>) {
  const response = await fetch(`${this.commandServerUrl}${MCP_EXECUTE_ENDPOINT}`, {
    method: 'POST',
    body: JSON.stringify({ tool, arguments: arguments_ })
  })
}
```

### **Command Server Uses MCPClient:**
```typescript
// cursor-addon/src/commandServer.ts
private async executeMCPTool(request: { tool: string; arguments?: any }) {
  if (!this.mcpClient) {
    this.mcpClient = new MCPClient();
    await this.mcpClient.initialize();
  }
  const result = await this.mcpClient.callTool(tool, args);
  return { success: true, result };
}
```

### **MCPClient Spawns Python Process:**
```typescript
// cursor-addon/src/mcp/mcpClient.ts
async initialize() {
  const mcpServerPath = 'lucid_mcp_server.py';
  this.process = spawn('python', ['-u', mcpServerPath], {
    stdio: ['pipe', 'pipe', 'pipe']
  });
  // Communicates via JSON-RPC 2.0 over stdio
}
```

---

## 🎯 **Why This Architecture?**

### **Benefits:**
1. **Separation of Concerns** - IDE prototype doesn't need to manage MCP protocol
2. **HTTP API** - Easier for React/web apps to use
3. **Single MCP Connection** - Command Server manages one MCP connection
4. **Reusability** - Other clients can use Command Server too

### **Trade-offs:**
1. **Extra Hop** - IDE → Command Server → MCPClient → MCP Server
2. **HTTP Overhead** - But minimal for localhost
3. **Dependency** - IDE prototype requires Cursor extension to be running

---

## ✅ **Conclusion**

**YES, the IDE prototype uses the Cursor MCP extension!**

- ✅ Uses Command Server (part of Cursor extension)
- ✅ Command Server uses MCPClient (part of Cursor extension)
- ✅ MCPClient connects to MCP server (lucid_mcp_server.py)
- ✅ All 59 MCP tools available via HTTP API

**The architecture is:**
```
IDE Prototype → HTTP → Command Server → MCPClient → MCP Server → AIM-OS
```

**This is correct and working!** 🎉

---

**Status:** Architecture Confirmed  
**Last Updated:** 2025-01-27

