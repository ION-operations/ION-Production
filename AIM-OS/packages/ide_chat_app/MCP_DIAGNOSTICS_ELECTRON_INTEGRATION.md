# MCP Tools for Diagnostics - Electron App Integration

**Date:** 2025-11-02  
**Status:** ✅ **IMPLEMENTED** - Unified Diagnostics Tool Created  
**Purpose:** Use MCP tools to relay diagnostics data from Cursor to Electron app

---

## 🎯 **THE SOLUTION**

**Yes! We can use MCP tools to relay diagnostics data from Cursor to the Electron app.**

The MCP server already has diagnostic tools that connect to Cursor's command server. The Electron app calls these MCP tools via the extension's HTTP endpoint, and the MCP server relays the data from Cursor.

---

## 🔧 **ARCHITECTURE FLOW**

```
Electron App (Dashboard UI)
    ↓ HTTP POST /mcp/execute
    ↓ { tool: "get_unified_diagnostics", arguments: {...} }
Extension Command Server (port 5001)
    ↓ Routes to MCP server
MCP Server (lucid_mcp_server.py)
    ↓ Calls _call_command_server("/cursor/problems", "GET")
Extension Command Server
    ↓ Fetches from Cursor VS Code API
    ↓ Returns diagnostics
MCP Server
    ↓ Aggregates all diagnostics
    ↓ Returns unified result
Extension → Electron App
    ↓ Displays in UI panels
```

---

## 📊 **AVAILABLE MCP DIAGNOSTIC TOOLS**

### **Individual Tools (Already Available):**
1. **`get_problems`** - Get all Cursor IDE diagnostics/problems
2. **`get_problem_summary`** - Get summary by severity
3. **`get_file_problems`** - Get diagnostics for specific file
4. **`list_output_channels`** - List Cursor output channels
5. **`get_output_channel_logs`** - Get output channel content
6. **`get_electron_logs`** - Get Electron app console logs

### **Unified Tool (NEW):**
7. **`get_unified_diagnostics`** - Aggregates all diagnostic sources in one call

---

## 🚀 **HOW TO USE IN ELECTRON APP**

### **Option 1: Use Unified Tool (Recommended)**

```typescript
// Fetch all diagnostics in one call
const response = await fetch('http://localhost:5001/mcp/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tool: 'get_unified_diagnostics',
    arguments: {
      include_problems: true,           // Include Cursor IDE problems
      include_electron_logs: true,      // Include Electron app logs
      include_output_channels: false,   // Optional: include output channels
      problem_severity: 'all',          // Filter: 'all', 'error', 'warning', 'info', 'hint'
      electron_log_limit: 50,           // Max log lines
      electron_log_level: 'all'         // Filter: 'log', 'error', 'warn', 'all'
    }
  })
})

const result = await response.json()
if (result.success && result.result) {
  const diagnostics = JSON.parse(result.result.content[0].text)
  
  // Access unified diagnostics
  const problems = diagnostics.sources.cursor_problems?.problems || []
  const electronLogs = diagnostics.sources.electron_logs?.logs || []
  const summary = diagnostics.summary
  
  // Display in UI
  console.log(`Found ${summary.total_problems} problems, ${summary.total_logs} log lines`)
}
```

### **Option 2: Use Individual Tools**

```typescript
// Fetch just Cursor problems
const problemsResponse = await fetch('http://localhost:5001/mcp/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tool: 'get_problems',
    arguments: {}
  })
})

// Fetch just Electron logs
const logsResponse = await fetch('http://localhost:5001/mcp/execute', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    tool: 'get_electron_logs',
    arguments: {
      limit: 100,
      level: 'error',  // Only errors
      source: 'all'
    }
  })
})
```

---

## 📋 **UNIFIED DIAGNOSTICS RESPONSE FORMAT**

```json
{
  "success": true,
  "timestamp": "2025-11-02T12:34:56.789Z",
  "sources": {
    "cursor_problems": {
      "problems": [
        {
          "file": "src/App.tsx",
          "severity": "error",
          "message": "Type 'string' is not assignable to type 'number'",
          "line": 42,
          "column": 15
        }
      ],
      "summary": {
        "total": 5,
        "errors": 3,
        "warnings": 2,
        "info": 0,
        "hints": 0
      },
      "count": 5
    },
    "electron_logs": {
      "logs": [
        {
          "timestamp": "2025-11-02T12:34:56.789Z",
          "level": "error",
          "source": "RENDERER",
          "message": "Failed to fetch system info"
        }
      ],
      "count": 50,
      "log_file": "/path/to/electron-console.log",
      "level_filter": "all"
    },
    "output_channels": {
      "channels": ["Output", "Debug Console", "Terminal"],
      "count": 3
    }
  },
  "summary": {
    "total_problems": 5,
    "total_errors": 3,
    "total_warnings": 2,
    "total_logs": 50,
    "total_channels": 3
  },
  "message": "Unified diagnostics: 5 problems (3 errors, 2 warnings), 50 log lines, 3 output channels"
}
```

---

## 🎨 **UI INTEGRATION EXAMPLES**

### **Error Detector Panel**

```typescript
// In ErrorDetector.tsx
const fetchDiagnostics = async () => {
  const response = await fetch('http://localhost:5001/mcp/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tool: 'get_unified_diagnostics',
      arguments: {
        include_problems: true,
        include_electron_logs: true,
        problem_severity: 'error',  // Only errors
        electron_log_level: 'error'  // Only error logs
      }
    })
  })
  
  const result = await response.json()
  const diagnostics = JSON.parse(result.result.content[0].text)
  
  // Display errors from both sources
  const cursorErrors = diagnostics.sources.cursor_problems?.problems || []
  const electronErrors = diagnostics.sources.electron_logs?.logs || []
  
  setDetectedErrors([...cursorErrors, ...electronErrors])
}
```

### **System Health Panel**

```typescript
// In SystemHealth.tsx
const fetchAllDiagnostics = async () => {
  const response = await fetch('http://localhost:5001/mcp/execute', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      tool: 'get_unified_diagnostics',
      arguments: {
        include_problems: true,
        include_electron_logs: true,
        include_output_channels: true,
        problem_severity: 'all',
        electron_log_limit: 100
      }
    })
  })
  
  // Display comprehensive health status
  const diagnostics = JSON.parse(result.result.content[0].text)
  updateHealthMetrics(diagnostics.summary)
}
```

---

## 💡 **BENEFITS**

### **Unified Interface**
- **Single API call** - Get all diagnostics at once
- **Consistent format** - Same response structure
- **Easy filtering** - Filter by severity, level, source

### **Efficient**
- **Parallel fetching** - MCP server fetches from multiple sources
- **Reduced HTTP calls** - One call instead of multiple
- **Cached results** - Can cache unified diagnostics

### **Flexible**
- **Optional sources** - Choose which diagnostics to include
- **Filtering** - Filter by severity, level, source
- **Extensible** - Easy to add new diagnostic sources

---

## 🚀 **NEXT STEPS**

1. ✅ **Unified tool created** - `get_unified_diagnostics` in MCP server
2. **Update Electron app** - Use unified tool in Error Detector, System Health panels
3. **Add real-time polling** - Poll for diagnostics updates
4. **Create diagnostics dashboard** - Unified view of all diagnostics

---

**Status:** ✅ **READY TO USE**  
**Tool Name:** `get_unified_diagnostics`  
**MCP Server:** `lucid_mcp_server.py`  
**Electron Integration:** Via `POST http://localhost:5001/mcp/execute`

