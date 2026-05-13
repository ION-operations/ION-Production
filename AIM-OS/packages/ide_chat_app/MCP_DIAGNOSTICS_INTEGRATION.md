# MCP Tools for Diagnostics Integration

**Date:** 2025-11-02  
**Status:** ✅ **YES - FULLY POSSIBLE**  
**Purpose:** Use MCP tools to retrieve diagnostics data dynamically based on what's needed

---

## 🎯 **THE ANSWER: YES, ABSOLUTELY!**

**We can use MCP tools to retrieve diagnostics data** depending on what's needed. The Electron app already has access to MCP tools via the Cursor extension, and we can use them to fetch diagnostics dynamically.

---

## 🔧 **AVAILABLE MCP DIAGNOSTIC TOOLS**

### **1. Problem Detection Tools**
- `mcp_lucid-mcp_get_problems` - Get all diagnostics/problems from Cursor IDE (errors, warnings, info, hints)
- `mcp_lucid-mcp_get_problem_summary` - Get summary of problems by severity (error/warning/info/hint counts)
- `mcp_lucid-mcp_get_file_problems` - Get diagnostics/problems for a specific file

### **2. Output Channel Tools**
- `mcp_lucid-mcp_list_output_channels` - List all known output channels in Cursor IDE
- `mcp_lucid-mcp_get_output_channel_logs` - Get output channel content with optional line limit

### **3. Electron Logs**
- `mcp_lucid-mcp_get_electron_logs` - Get console logs from Electron application (main process and renderer process)

---

## 📊 **IMPLEMENTATION STRATEGY**

### **Dynamic Diagnostics Fetching**

**Scenario: User needs specific diagnostics**

1. **User clicks "Get Diagnostics"** in Electron app
2. **Electron app sends MCP request** via HTTP endpoint:
   ```typescript
   POST http://localhost:5001/mcp/execute
   {
     "tool": "get_problems",
     "arguments": {} // Get all problems
   }
   ```

3. **MCP tool returns diagnostics:**
   ```json
   {
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
       "errors": 5,
       "warnings": 12,
       "info": 3,
       "hints": 8
     }
   }
   ```

4. **Electron app displays diagnostics** in a dedicated panel

### **Context-Aware Diagnostics**

**Different panels can request different diagnostics:**

- **Error Detector Panel:** Uses `get_problems` filtered by severity='error'
- **File Changes Panel:** Uses `get_file_problems` for each changed file
- **System Health Panel:** Uses `get_electron_logs` + `get_output_channel_logs`
- **Dev Tools Panel:** Uses `get_electron_logs` + `get_output_channel_logs`

---

## 🚀 **INTEGRATION EXAMPLES**

### **Example 1: Error Detector Enhancement**

```typescript
// In ErrorDetector.tsx
const fetchDiagnostics = async () => {
  try {
    const response = await fetch('http://localhost:5001/mcp/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tool: 'get_problems',
        arguments: {}
      })
    })
    
    const result = await response.json()
    if (result.success && result.result) {
      // Filter by severity
      const errors = result.result.problems?.filter(p => p.severity === 'error') || []
      setDetectedErrors(errors)
    }
  } catch (error) {
    console.error('Failed to fetch diagnostics:', error)
  }
}
```

### **Example 2: File-Specific Diagnostics**

```typescript
// In FileChangesViewer.tsx
const fetchFileDiagnostics = async (filePath: string) => {
  try {
    const response = await fetch('http://localhost:5001/mcp/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tool: 'get_file_problems',
        arguments: {
          file_path: filePath
        }
      })
    })
    
    const result = await response.json()
    if (result.success && result.result) {
      // Display file-specific problems
      setFileProblems(result.result.problems || [])
    }
  } catch (error) {
    console.error('Failed to fetch file diagnostics:', error)
  }
}
```

### **Example 3: Output Channel Logs**

```typescript
// In LogViewer.tsx or DevTools panel
const fetchOutputLogs = async (channelName: string) => {
  try {
    const response = await fetch('http://localhost:5001/mcp/execute', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        tool: 'get_output_channel_logs',
        arguments: {
          channel_name: channelName,
          limit: 100
        }
      })
    })
    
    const result = await response.json()
    if (result.success && result.result) {
      // Display output channel logs
      setLogs(result.result.logs || [])
    }
  } catch (error) {
    console.error('Failed to fetch output logs:', error)
  }
}
```

---

## 📋 **BENEFITS**

### **Dynamic & Context-Aware**
- **Fetch only what's needed** - don't load all diagnostics upfront
- **Context-aware** - different panels request different data
- **Real-time updates** - can poll for changes

### **Unified Interface**
- **Single API** - all diagnostics via MCP tools
- **Consistent format** - same response structure
- **Error handling** - unified error handling

### **Extensible**
- **Easy to add new diagnostic types** - just add new MCP tool calls
- **Custom filtering** - filter by severity, file, etc.
- **Custom display** - each panel can display diagnostics differently

---

## 🎨 **UI INTEGRATION**

### **Error Detector Panel**
- Uses `get_problems` to fetch all errors
- Filters by severity (error/warning/info)
- Displays in organized list with file paths

### **File Changes Panel**
- Uses `get_file_problems` for each changed file
- Shows problems inline with file changes
- Highlights problematic lines

### **System Health Panel**
- Uses `get_electron_logs` for Electron app logs
- Uses `get_output_channel_logs` for Cursor output channels
- Combines with system metrics

---

## 🚀 **NEXT STEPS**

1. **Integrate MCP diagnostic tools** into Error Detector panel
2. **Add file-specific diagnostics** to File Changes panel
3. **Create unified diagnostic service** that wraps MCP calls
4. **Add real-time polling** for diagnostics updates
5. **Create diagnostics dashboard** combining all sources

---

**Status:** Ready for implementation  
**Priority:** HIGH - Will significantly improve debugging capabilities  
**Dependencies:** MCP tools already available, just need to integrate

