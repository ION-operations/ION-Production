# Command Server API Reference

**Purpose:** API specification for Command Server compatibility  
**Created by:** Alex (Backend Integration Specialist)  
**For:** @Sev (Standalone Command Server Implementation)  
**Date:** 2025-01-27

---

## Overview

This document specifies the API format that my integration code expects from the Command Server. This ensures compatibility between my backend integration and Sev's standalone Command Server implementation.

---

## Base URL

**Current:** `http://localhost:5001`  
**Note:** Port should be configurable for standalone server

---

## Endpoints

### 1. Health Check

**Endpoint:** `GET /health`

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:5001
Content-Type: application/json
```

**Response:**
```json
{
  "status": "ok",
  "port": 5001,
  "message": "Command Server is healthy"
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Command Server unavailable"
}
```

**Used by:** `MCPService.checkHealth()`

---

### 2. List MCP Tools

**Endpoint:** `GET /mcp/list`

**Request:**
```http
GET /mcp/list HTTP/1.1
Host: localhost:5001
Content-Type: application/json
```

**Response:**
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

**Error Response:**
```json
{
  "success": false,
  "error": "Failed to list tools"
}
```

**Used by:** `MCPService.listTools()`

---

### 3. Execute MCP Tool

**Endpoint:** `POST /mcp/execute`

**Request:**
```http
POST /mcp/execute HTTP/1.1
Host: localhost:5001
Content-Type: application/json

{
  "tool": "mcp_lucid-mcp_store_memory",
  "arguments": {
    "content": "Test content",
    "tags": { "test": 1.0 },
    "metadata": { "source": "test" }
  }
}
```

**Response (Success):**
```json
{
  "success": true,
  "result": {
    // Tool-specific result
    "atom_id": "atom_123",
    "atom": { /* CMCAtom */ }
  },
  "tool": "mcp_lucid-mcp_store_memory"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Tool execution failed: ...",
  "tool": "mcp_lucid-mcp_store_memory"
}
```

**Used by:** `MCPService.executeTool()` (all service clients)

---

## Request Format

### MCP Tool Request

```typescript
interface MCPToolRequest {
  tool: string                    // MCP tool name (e.g., "mcp_lucid-mcp_store_memory")
  arguments?: Record<string, any>  // Tool-specific arguments
}
```

### Examples

**Store Memory:**
```json
{
  "tool": "mcp_lucid-mcp_store_memory",
  "arguments": {
    "content": "Test content",
    "tags": { "test": 1.0 },
    "metadata": { "source": "test" }
  }
}
```

**Retrieve Memory:**
```json
{
  "tool": "mcp_lucid-mcp_retrieve_memory",
  "arguments": {
    "query": "test",
    "limit": 5
  }
}
```

**Track Confidence:**
```json
{
  "tool": "mcp_lucid-mcp_track_confidence",
  "arguments": {
    "model_id": "gpt-4-turbo",
    "confidence_score": 0.85,
    "task_criticality": "routine"
  }
}
```

---

## Response Format

### Success Response

```typescript
interface MCPToolResponse<T = any> {
  success: true
  result?: T              // Tool-specific result
  tool?: string          // Tool name (for logging)
}
```

### Error Response

```typescript
interface MCPToolResponse {
  success: false
  error: string          // Error message
  tool?: string          // Tool name (for logging)
}
```

---

## HTTP Headers

**Required:**
- `Content-Type: application/json` (for POST requests)

**Optional:**
- `CORS` headers should be enabled for cross-origin requests

---

## Error Handling

**HTTP Status Codes:**
- `200 OK` - Request successful (check `success` field in body)
- `400 Bad Request` - Invalid request format
- `404 Not Found` - Endpoint not found
- `500 Internal Server Error` - Server error

**Response Body:**
- Always includes `success` boolean
- Errors include `error` string
- Tool name included for logging

---

## Timeout Requirements

**Request Timeout:** 30 seconds per request  
**Note:** My MCPService uses `AbortController` with 30-second timeout

---

## Retry Behavior

**My MCPService Retry Logic:**
- Max retries: 3
- Initial delay: 500ms
- Max delay: 5s
- Exponential backoff
- Retries on: network errors, timeouts, 5xx errors

**Standalone Server Should:**
- Handle retries gracefully
- Return consistent error format
- Not duplicate retry logic

---

## Priority MCP Tools

These are the 8 priority tools my integration uses:

1. `mcp_lucid-mcp_store_memory` - CMC integration
2. `mcp_lucid-mcp_retrieve_memory` - CMC/HHNI integration
3. `mcp_lucid-mcp_track_confidence` - VIF integration
4. `mcp_lucid-mcp_create_plan` - APOE integration
5. `mcp_lucid-mcp_synthesize_knowledge` - SEG integration
6. `mcp_lucid-mcp_add_timeline_entry` - TCS integration
7. `mcp_lucid-mcp_get_timeline_summary` - TCS integration
8. `mcp_lucid-mcp_get_consciousness_metrics` - CAS integration

---

## Testing

**Test Utilities Available:**
- `src/services/__tests__/MCPService.test.ts` - Test utilities
- `scripts/test-command-server.ts` - Test script
- `docs/COMMAND_SERVER_TESTING_GUIDE.md` - Testing guide

**Can Test:**
- Health check
- Tool listing
- Tool execution
- Error handling
- Timeout handling

---

## Compatibility Checklist

For standalone Command Server to work with my integration:

- [ ] Same endpoint: `POST /mcp/execute`
- [ ] Same request format: `{ tool: string, arguments?: object }`
- [ ] Same response format: `{ success: boolean, result?: any, error?: string }`
- [ ] Health endpoint: `GET /health`
- [ ] Tool list endpoint: `GET /mcp/list`
- [ ] Port 5001 (or configurable)
- [ ] 30-second timeout support
- [ ] CORS headers enabled
- [ ] JSON request/response format
- [ ] Consistent error format

---

## Questions for Sev

1. **Port Configuration:** Can port be configurable? (currently hardcoded to 5001)
2. **Startup Detection:** How will IDE know when standalone server is ready?
3. **Process Management:** How will standalone server handle MCP server process lifecycle?
4. **Error Format:** Will error format match current Command Server?
5. **Tool Availability:** Will all MCP tools be available immediately on startup?

---

## Integration Code Reference

**MCPService:** `src/services/MCPService.ts`  
**Service Clients:** `src/services/*Service.ts` (all use MCPService)  
**Hooks:** `src/hooks/useAIMOS.ts` (all use service clients)

**All integration code assumes this API format.**

---

**Status:** API Reference Complete  
**For:** @Sev  
**Purpose:** Ensure standalone Command Server compatibility

