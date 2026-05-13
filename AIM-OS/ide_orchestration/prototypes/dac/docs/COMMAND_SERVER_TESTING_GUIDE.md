# Command Server Testing Guide

**Purpose:** Verify Command Server connectivity and test all priority MCP tools  
**Created by:** Alex (Backend Integration Specialist)  
**Date:** 2025-01-27

---

## Overview

This guide explains how to test Command Server connectivity and verify that all MCP tools are working correctly. The test utilities are located in `src/services/__tests__/MCPService.test.ts`.

---

## Prerequisites

1. **Command Server Running**
   - Command Server must be running on `http://localhost:5001`
   - Verify with: `curl http://localhost:5001/health` or open in browser

2. **MCP Server Connected**
   - MCP server must be connected to Command Server
   - Verify MCP tools are available via Command Server

---

## Testing Methods

### Method 1: Browser Console (Recommended for Frontend)

1. **Start the development server:**
   ```bash
   npm run dev
   ```

2. **Open browser console** (F12 or Right-click → Inspect → Console)

3. **Import and run tests:**
   ```javascript
   // Import test utilities (adjust path as needed)
   import { 
     testCommandServerHealth, 
     listAvailableMCPTools, 
     testAllPriorityMCPTools 
   } from './src/services/__tests__/MCPService.test'
   
   // Test health
   await testCommandServerHealth()
   
   // List tools
   await listAvailableMCPTools()
   
   // Test all priority tools
   await testAllPriorityMCPTools()
   ```

### Method 2: Test Script (Node.js)

1. **Install ts-node** (if not already installed):
   ```bash
   npm install --save-dev ts-node @types/node
   ```

2. **Run test script:**
   ```bash
   npx ts-node scripts/test-command-server.ts
   ```

### Method 3: Manual Testing via MCPService

```typescript
import { mcpService } from './src/services/MCPService'

// Check health
const health = await mcpService.checkHealth()
console.log('Health:', health)

// List tools
const tools = await mcpService.listTools()
console.log('Available tools:', tools)

// Execute a tool
const result = await mcpService.executeTool('mcp_lucid-mcp_store_memory', {
  content: 'Test content',
  tags: { test: 1.0 },
  metadata: { source: 'test' }
})
console.log('Result:', result)
```

---

## Priority MCP Tools to Test

The following 8 MCP tools are tested in priority order:

1. **`mcp_lucid-mcp_store_memory`** - CMC integration
   - Stores memory atoms in CMC
   - Test args: `{ content: 'Test', tags: { test: 1.0 }, metadata: { source: 'test' } }`

2. **`mcp_lucid-mcp_retrieve_memory`** - CMC/HHNI integration
   - Retrieves memory atoms via HHNI search
   - Test args: `{ query: 'test', limit: 5 }`

3. **`mcp_lucid-mcp_track_confidence`** - VIF integration
   - Tracks confidence scores with VIF witnesses
   - Test args: `{ model_id: 'test', confidence_score: 0.85, task_criticality: 'routine' }`

4. **`mcp_lucid-mcp_create_plan`** - APOE integration
   - Creates execution plans via APOE
   - Test args: `{ goal: 'Test goal', context: 'Test context', priority: 'medium' }`

5. **`mcp_lucid-mcp_synthesize_knowledge`** - SEG integration
   - Synthesizes knowledge via SEG
   - Test args: `{ query: 'test', limit: 5 }`

6. **`mcp_lucid-mcp_add_timeline_entry`** - TCS integration
   - Adds timeline entries to TCS
   - Test args: `{ entry_type: 'test', content: 'Test entry', metadata: { source: 'test' } }`

7. **`mcp_lucid-mcp_get_timeline_summary`** - TCS integration
   - Retrieves timeline summary from TCS
   - Test args: `{ limit: 10 }`

8. **`mcp_lucid-mcp_get_consciousness_metrics`** - CAS integration
   - Gets consciousness metrics from CAS
   - Test args: `{}`

---

## Expected Results

### Health Check
```json
{
  "status": "ok",
  "port": 5001,
  "message": "Command Server is healthy"
}
```

### Tool List
```json
{
  "success": true,
  "tools": [
    "mcp_lucid-mcp_store_memory",
    "mcp_lucid-mcp_retrieve_memory",
    "mcp_lucid-mcp_track_confidence",
    // ... more tools
  ]
}
```

### Tool Execution
```json
{
  "success": true,
  "result": {
    // Tool-specific result
  },
  "tool": "mcp_lucid-mcp_store_memory"
}
```

---

## Troubleshooting

### Command Server Not Responding

**Error:** `ECONNREFUSED` or `Network error`

**Solutions:**
1. Verify Command Server is running: `curl http://localhost:5001/health`
2. Check Command Server logs for errors
3. Verify port 5001 is not blocked by firewall
4. Check if another service is using port 5001

### MCP Tools Not Available

**Error:** `Tool not found` or `Tool list empty`

**Solutions:**
1. Verify MCP server is connected to Command Server
2. Check MCP server logs for connection errors
3. Verify MCP server configuration in Command Server
4. Restart MCP server and Command Server

### Tool Execution Fails

**Error:** `Tool execution failed` or `500 Internal Server Error`

**Solutions:**
1. Check tool arguments match expected format
2. Verify backend service (CMC, HHNI, etc.) is running
3. Check backend service logs for errors
4. Verify database connections if applicable

---

## Test Results Documentation

After running tests, document results:

1. **Health Check:** ✅ Pass / ❌ Fail
2. **Tool Count:** Number of available tools
3. **Priority Tools:** List pass/fail for each tool
4. **Errors:** Document any errors encountered
5. **Recommendations:** Next steps or fixes needed

---

## Next Steps

After successful testing:

1. ✅ All hooks updated to use real backend services
2. ⏳ Verify Command Server connectivity
3. ⏳ Test all priority MCP tools
4. ⏳ Document test results
5. ⏳ Share results with team (Nova, Sage, Aether)

---

**Status:** Test utilities ready, awaiting Command Server availability  
**Created by:** Alex  
**Last Updated:** 2025-01-27

