# Chapter 32 - APIs Reference

Status: Drafting under intelligent quality gates (tier B)  
Mode: Completeness-based writing  
Target: 1000 +/- 10 percent

## Purpose

This chapter provides reference documentation for AIM-OS APIs including MCP tools, HTTP endpoints, and integration interfaces. APIs enable external systems to integrate with AIM-OS and access its capabilities.

## Executive Summary

- AIM-OS provides 59 MCP tools for AI-to-AI communication and system integration.
- HTTP endpoints enable external systems to access AIM-OS capabilities.
- Integration interfaces enable seamless integration with existing systems.

## MCP Tools Reference

AIM-OS provides 59 MCP tools organized by category:

### Core AIM-OS Tools (6)
- `store_memory` - Store knowledge in CMC
  - **Parameters:** `content` (string), `tags` (array), `metadata` (object)
  - **Returns:** `atom_id` (string), `timestamp` (string)
  - **Example:** Store chapter expansion insights
- `retrieve_memory` - Retrieve insights from HHNI
  - **Parameters:** `query` (string), `limit` (integer), `filters` (object)
  - **Returns:** `memories` (array), `count` (integer)
  - **Example:** Retrieve relevant insights for chapter expansion
- `get_memory_stats` - Get AIM-OS statistics
  - **Parameters:** `include_breakdown` (boolean)
  - **Returns:** `total_atoms` (integer), `total_snapshots` (integer), `breakdown` (object)
  - **Example:** Get memory system statistics
- `create_plan` - Create APOE execution plans
  - **Parameters:** `goal` (string), `context` (object), `priority` (string)
  - **Returns:** `plan_id` (string), `steps` (array)
  - **Example:** Create plan for chapter expansion
- `track_confidence` - Track VIF confidence
  - **Parameters:** `task` (string), `confidence` (float), `evidence` (array)
  - **Returns:** `witness_id` (string), `confidence` (float)
  - **Example:** Track confidence for chapter expansion
- `synthesize_knowledge` - Synthesize SEG knowledge
  - **Parameters:** `topics` (array), `depth` (string), `format` (string)
  - **Returns:** `synthesis` (object), `insights` (array)
  - **Example:** Synthesize knowledge from multiple sources

### Timeline Context Tools (3)
- `add_timeline_entry` - Track context at each prompt
  - **Parameters:** `prompt_id` (string), `user_input` (string), `context_state` (object)
  - **Returns:** `entry_id` (string), `timestamp` (string)
  - **Example:** Track context for chapter expansion session
- `get_timeline_summary` - Get recent timeline entries
  - **Parameters:** `limit` (integer)
  - **Returns:** `entries` (array), `count` (integer)
  - **Example:** Get recent context entries
- `get_timeline_entries` - Query timeline history
  - **Parameters:** `start_time` (string), `end_time` (string), `limit` (integer)
  - **Returns:** `entries` (array), `count` (integer)
  - **Example:** Query timeline history for chapter expansion

### Goal Timeline Tools (3)
- `create_goal_timeline_node` - Create goals as timeline planning nodes
  - **Parameters:** `goal_id` (string), `name` (string), `description` (string), `priority` (string)
  - **Returns:** `goal_id` (string), `node_id` (string)
  - **Example:** Create goal for chapter expansion
- `update_goal_progress` - Update goal progress and status
  - **Parameters:** `goal_id` (string), `progress` (float), `status` (string)
  - **Returns:** `goal_id` (string), `updated_progress` (float)
  - **Example:** Update goal progress for chapter expansion
- `query_goal_timeline` - Query goals with filtering
  - **Parameters:** `status` (string), `priority` (string), `limit` (integer)
  - **Returns:** `goals` (array), `count` (integer)
  - **Example:** Query goals for chapter expansion

### AI Collaboration Tools (6)
- `send_ai_message` - Send a message to another AI system
  - **Parameters:** `from_ai` (string), `to_ai` (string), `content` (string), `message_type` (string)
  - **Returns:** `message_id` (string), `thread_id` (string)
  - **Example:** Send status update to Aether
- `get_ai_messages` - Retrieve AI-to-AI messages
  - **Parameters:** `from_ai` (string), `to_ai` (string), `message_type` (string), `limit` (integer)
  - **Returns:** `messages` (array), `count` (integer)
  - **Example:** Get messages from Aether
- `start_ai_discussion` - Start a new discussion thread
  - **Parameters:** `from_ai` (string), `to_ai` (string), `topic` (string), `initial_message` (string)
  - **Returns:** `thread_id` (string), `message_id` (string)
  - **Example:** Start discussion about chapter expansion
- `handoff_task_to_ai` - Hand off a task to another AI system
  - **Parameters:** `from_ai` (string), `to_ai` (string), `task_description` (string), `task_data` (object)
  - **Returns:** `handoff_id` (string), `thread_id` (string)
  - **Example:** Hand off chapter expansion to Codex
- `share_ai_profile` - Share AI profile and capabilities
  - **Parameters:** `from_ai` (string), `to_ai` (string), `profile_data` (object)
  - **Returns:** `profile_id` (string), `timestamp` (string)
  - **Example:** Share profile with other agents
- `get_ai_collaboration_summary` - Get summary of AI collaboration activity
  - **Parameters:** None
  - **Returns:** `total_messages` (integer), `active_threads` (integer), `summary` (object)
  - **Example:** Get collaboration summary

### Autonomous Protocol Tools (9)
- `start_autonomous_operation` - Start autonomous operation
  - **Parameters:** `task` (string), `confidence` (float)
  - **Returns:** `operation_id` (string), `status` (string)
  - **Example:** Start autonomous chapter expansion
- `pause_autonomous_operation` - Pause autonomous operation
  - **Parameters:** None
  - **Returns:** `status` (string)
  - **Example:** Pause autonomous operation
- `resume_autonomous_operation` - Resume autonomous operation
  - **Parameters:** None
  - **Returns:** `status` (string)
  - **Example:** Resume autonomous operation
- `stop_autonomous_operation` - Stop autonomous operation
  - **Parameters:** None
  - **Returns:** `status` (string)
  - **Example:** Stop autonomous operation
- `get_autonomous_status` - Get current status
  - **Parameters:** None
  - **Returns:** `status` (string), `operation_id` (string), `progress` (float)
  - **Example:** Get autonomous operation status
- `run_autonomous_checklist` - Run safety checklist
  - **Parameters:** None
  - **Returns:** `checklist` (object), `passed` (boolean)
  - **Example:** Run autonomous safety checklist
- `fix_autonomous_issues` - Fix autonomous issues
  - **Parameters:** None
  - **Returns:** `fixes` (array), `status` (string)
  - **Example:** Fix autonomous operation issues
- `should_continue_autonomous` - Check if should continue
  - **Parameters:** None
  - **Returns:** `should_continue` (boolean), `reason` (string)
  - **Example:** Check if autonomous operation should continue
- `generate_next_autonomous_task` - Generate next task
  - **Parameters:** None
  - **Returns:** `task` (string), `confidence` (float)
  - **Example:** Generate next autonomous task

### Additional Tool Categories

**SCOR Tools (3):** Safety, consciousness, reliability monitoring tools  
**Snapshot Tools (4):** File versioning and bitemporal management tools  
**Intuitive Intelligence Tools (3):** AI intuition and learning system tools  
**Co-Agency & Trust Tools (3):** Human-AI collaboration protocol tools  
**Dataset Management Tools (4):** Data management and analysis tools  
**Application Lifecycle Tools (3):** Application management and deployment tools  
**Autonomous Research Dream Tools (3):** Advanced research capability tools  
**Observability Tools (4):** System monitoring and health check tools

**Total:** 59 MCP tools available

## HTTP Endpoints Reference

AIM-OS provides HTTP endpoints for external integration:

### MCP Execute Endpoint

**Endpoint:** `POST http://localhost:5001/mcp/execute`  
**Content-Type:** `application/json`

**Request Format:**
```json
{
  "tool": "tool_name",
  "arguments": {
    "param1": "value1",
    "param2": "value2"
  }
}
```

**Response Format:**
```json
{
  "success": true,
  "result": {},
  "error": null
}
```

**Error Format:**
```json
{
  "success": false,
  "result": null,
  "error": {
    "code": "error_code",
    "message": "Error message"
  }
}
```

**Example Request:**
```json
{
  "tool": "store_memory",
  "arguments": {
    "content": "AIM-OS enables AI consciousness",
    "tags": ["consciousness", "ai"]
  }
}
```

**Example Response:**
```json
{
  "success": true,
  "result": {
    "atom_id": "atom_12345",
    "timestamp": "2025-11-06T17:00:00Z"
  },
  "error": null
}
```

### Health Check Endpoint

**Endpoint:** `GET http://localhost:5001/health`  
**Method:** GET

**Response Format:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-06T17:00:00Z",
  "systems": {
    "cmc": "healthy",
    "hhni": "healthy",
    "vif": "healthy"
  }
}
```

**Status Values:**
- `healthy` - All systems operational
- `degraded` - Some systems degraded
- `unhealthy` - Critical systems failing

### Metrics Endpoint

**Endpoint:** `GET http://localhost:5001/metrics`  
**Method:** GET

**Response Format:**
```json
{
  "memory": {
    "total_atoms": 10000,
    "total_snapshots": 500
  },
  "performance": {
    "avg_latency_ms": 50,
    "p95_latency_ms": 80
  },
  "collaboration": {
    "total_messages": 141,
    "active_threads": 5
  }
}
```

### MCP List Endpoint

**Endpoint:** `GET http://localhost:5001/mcp/list`  
**Method:** GET

**Response Format:**
```json
{
  "tools": [
    {
      "name": "store_memory",
      "description": "Store knowledge in CMC",
      "parameters": {}
    }
  ],
  "count": 59
}
```

## Integration Interfaces

AIM-OS provides integration interfaces for common systems:

### Cursor IDE Integration

**MCP Server Integration:**
- **Protocol:** JSON-RPC 2.0 over stdio
- **Server:** `lucid_mcp_server.py`
- **Configuration:** `~/.cursor/mcp.json`
- **Tools:** 59 MCP tools available
- **Features:** Tool discovery, execution, error handling

**Integration Points:**
- Extension command server (`cursor-addon/src/commandServer.ts`)
- MCP client (`cursor-addon/src/mcp/mcpClient.ts`)
- Tool execution via HTTP endpoints

### Electron App Integration

**HTTP Endpoint Integration:**
- **Endpoint:** `http://localhost:5001/mcp/execute`
- **Protocol:** HTTP POST with JSON
- **Features:** UI messaging, tool execution, status updates

**Integration Points:**
- MCP API client (`packages/ide_chat_app/src/services/mcpApi.ts`)
- UI panel communication via HTTP endpoints
- Real-time updates via WebSocket (planned)

### External API Integration

**RESTful API:**
- **Base URL:** `http://localhost:5001`
- **Protocol:** HTTP/HTTPS
- **Authentication:** API keys (planned)
- **Rate Limiting:** Per-IP limits (planned)

**Integration Points:**
- HTTP endpoints for all MCP tools
- Health check and metrics endpoints
- Webhook support (planned)

### SDK Integration

**SDK Support:**
- **Python SDK:** `from aimos import AIMOSClient`
- **TypeScript SDK:** `import { AIMOSClient } from '@aimos/sdk'`
- **PowerShell SDK:** `Import-Module AIMOS`

**Integration Points:**
- High-level abstractions over HTTP endpoints
- Type-safe interfaces
- Error handling and retries
- Authentication management

## Runnable Examples

### Example 1: Call MCP Tool via HTTP Endpoint
```powershell
# Call store_memory tool via HTTP endpoint
$request = @{ 
    tool='store_memory'; 
    arguments=@{
        content='AIM-OS enables AI consciousness';
        tags=@('consciousness', 'ai');
        metadata=@{ source='chapter_expansion' }
    }
} | ConvertTo-Json -Depth 6

$result = Invoke-WebRequest -Uri 'http://localhost:5001/mcp/execute' `
    -Method POST -ContentType 'application/json' -Body $request |
    Select-Object -ExpandProperty Content | ConvertFrom-Json

Write-Host "Memory Stored:"
Write-Host "  Atom ID: $($result.result.atom_id)"
Write-Host "  Timestamp: $($result.result.timestamp)"
```

### Example 2: Check System Health
```powershell
# Check system health via HTTP endpoint
$health = Invoke-WebRequest -Uri 'http://localhost:5001/health' |
    Select-Object -ExpandProperty Content | ConvertFrom-Json

Write-Host "System Health:"
Write-Host "  Status: $($health.status)"
Write-Host "  Systems:"
$health.systems.PSObject.Properties | ForEach-Object {
    Write-Host "    $($_.Name): $($_.Value)"
}
```

### Example 3: Get System Metrics
```powershell
# Get system metrics via HTTP endpoint
$metrics = Invoke-WebRequest -Uri 'http://localhost:5001/metrics' |
    Select-Object -ExpandProperty Content | ConvertFrom-Json

Write-Host "System Metrics:"
Write-Host "  Memory:"
Write-Host "    Total Atoms: $($metrics.memory.total_atoms)"
Write-Host "    Total Snapshots: $($metrics.memory.total_snapshots)"
Write-Host "  Performance:"
Write-Host "    Avg Latency: $($metrics.performance.avg_latency_ms)ms"
Write-Host "    P95 Latency: $($metrics.performance.p95_latency_ms)ms"
```

### Example 4: List Available MCP Tools
```powershell
# List available MCP tools via HTTP endpoint
$tools = Invoke-WebRequest -Uri 'http://localhost:5001/mcp/list' |
    Select-Object -ExpandProperty Content | ConvertFrom-Json

Write-Host "Available MCP Tools: $($tools.count)"
$tools.tools | Select-Object -First 10 | ForEach-Object {
    Write-Host "  - $($_.name): $($_.description)"
}
```

## Integration Points

APIs integrate deeply with all AIM-OS systems:

### APOE (Chapter 8)

**APOE provides:** Orchestration for API calls  
**APIs provide:** Tool execution requiring orchestration  
**Integration:** APOE orchestrates API calls with quality gates and budgets

**Key Insight:** APOE enables orchestration. APIs use APOE for workflow orchestration.

### VIF (Chapter 7)

**VIF provides:** Confidence tracking for API operations  
**APIs provide:** Operations requiring confidence tracking  
**Integration:** VIF tracks confidence for all API operations

**Key Insight:** VIF enables confidence tracking. APIs use VIF for operation confidence.

### CCS (Chapter 13)

**CCS provides:** Real-time communication for APIs  
**APIs provide:** Communication requiring real-time substrate  
**Integration:** CCS enables real-time API communication

**Key Insight:** CCS enables real-time communication. APIs use CCS for communication substrate.

### CMC (Chapter 5)

**CMC provides:** Persistent storage for API operations  
**APIs provide:** Operations requiring storage  
**Integration:** CMC stores all API operation history

**Key Insight:** CMC enables persistence. APIs use CMC for operation storage.

**Overall Insight:** APIs integrate with all systems to enable comprehensive AIM-OS access. Every system contributes to API functionality.

## Connection to Other Chapters

APIs connect to all AIM-OS systems:

- **Chapter 1 (The Great Limitation):** APIs address "no integration" by enabling external system access
- **Chapter 2 (The Vision):** APIs enable the "integration" principle from the universal interface
- **Chapter 3 (The Proof):** APIs validate integration through proof loop
- **Chapter 5 (CMC):** APIs use CMC for operation storage
- **Chapter 7 (VIF):** APIs use VIF for confidence tracking
- **Chapter 8 (APOE):** APIs use APOE for orchestration
- **Chapter 13 (CCS):** APIs use CCS for real-time communication
- **Chapter 33 (SDKs & Clients):** APIs provide underlying interfaces for SDKs

**Key Insight:** APIs are the integration system that enables AIM-OS to work with external systems. Without APIs, external systems cannot access AIM-OS capabilities.

