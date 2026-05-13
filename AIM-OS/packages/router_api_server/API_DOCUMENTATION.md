# Router & Log-Sentinels API Server - API Documentation

**Version:** 1.0.0  
**Date:** 2025-01-27  
**Base URL:** `http://localhost:8000`

---

## Overview

The Router & Log-Sentinels API Server provides RESTful endpoints for:
- **Router:** Intelligent tool selection and execution via PLIx → APOE
- **Log-Sentinels:** Hybrid log analysis with Scout (cloud) and Forensics (local) reports

**Interactive Documentation:**
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`
- **OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

## Authentication

Currently, the API server does not require authentication. In production, authentication should be added via:
- API keys
- OAuth 2.0
- JWT tokens

---

## Router Endpoints

### GET /api/router/tools

Get Router tool proposals with probabilities, rationales, and preconditions.

**Query Parameters:**
- `goal` (required): Current goal
- `task` (required): Current task
- `confidence` (optional, default: 0.8): Confidence level (0.0-1.0)
- `files` (optional): List of active files (comma-separated)
- `errors` (optional): List of current errors (comma-separated)
- `agent_intent` (optional, default: "execute"): Agent intent

**Response:**
```json
{
  "tools": [
    {
      "tool_name": "mcp_lucid-mcp_store_memory",
      "rationale": "Store context in persistent memory",
      "draft_arguments": {},
      "confidence": 0.8,
      "probability": 0.9,
      "context_fit": 0.85,
      "success_rate": 0.92,
      "precondition_satisfied": true,
      "expected_info_gain": 0.75,
      "parallelizable": false,
      "plix_tag": "plix://tool/mcp_lucid-mcp_store_memory"
    }
  ],
  "suggestions": [],
  "plan_id": "plan-123-456"
}
```

**Example:**
```bash
curl "http://localhost:8000/api/router/tools?goal=debug%20error&task=fix%20bug&confidence=0.8"
```

---

### GET /api/router/telemetry

Get Router telemetry metrics including latency, success rate, and cost.

**Response:**
```json
{
  "avg_latency": 150.0,
  "latency_trend": "stable",
  "success_rate": 0.85,
  "success_trend": "up",
  "avg_cost": 0.05,
  "cost_trend": "stable",
  "tools": [
    {
      "name": "mcp_lucid-mcp_store_memory",
      "latency": 120.0,
      "success_rate": 0.92,
      "cost": 0.03,
      "call_count": 42
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/router/telemetry"
```

---

### POST /api/router/execute

Execute tool via Router → PLIx → APOE.

**Request Body:**
```json
{
  "tool": "mcp_lucid-mcp_store_memory",
  "args": {
    "content": "Test content",
    "tags": {
      "type": "test"
    }
  }
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "atom_id": "atom-123",
    "success": true
  },
  "plan_id": "plan-123-456",
  "intent_achieved": true,
  "evidence": {
    "plan_id": "plan-123-456",
    "entity_tag": "plix://tool/mcp_lucid-mcp_store_memory",
    "execution_time": 0.15,
    "steps_executed": 1,
    "success": true
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/router/execute" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "mcp_lucid-mcp_store_memory",
    "args": {
      "content": "Test",
      "tags": {}
    }
  }'
```

---

## Log-Sentinels Endpoints

### GET /api/log-sentinels/scouts

Get Scout reports (fast cloud analysis).

**Query Parameters:**
- `time_range_from` (optional): Start time (ISO 8601)
- `time_range_to` (optional): End time (ISO 8601)
- `source_filter` (optional): Source filter

**Response:**
```json
[
  {
    "window_id": "window-123",
    "summary": "High error rate detected in API endpoints",
    "confidence": 0.85,
    "severity": "high",
    "tags": ["api", "errors"],
    "suggested_tools": ["mcp_lucid-mcp_analyze_thought_patterns"],
    "timestamp": "2025-01-27T00:00:00Z"
  }
]
```

**Example:**
```bash
curl "http://localhost:8000/api/log-sentinels/scouts"
```

---

### GET /api/log-sentinels/forensics

Get Forensics reports (deep local analysis).

**Query Parameters:**
- `time_range_from` (optional): Start time (ISO 8601)
- `time_range_to` (optional): End time (ISO 8601)
- `severity_filter` (optional): Severity filter (low/medium/high)

**Response:**
```json
[
  {
    "window_id": "window-123",
    "summary": "Root cause: Memory leak in API handler",
    "confidence": 0.92,
    "severity": "high",
    "tags": ["api", "memory", "leak"],
    "suggested_tools": ["mcp_lucid-mcp_analyze_thought_patterns"],
    "timestamp": "2025-01-27T00:00:00Z",
    "root_cause": "Memory leak in request handler due to unclosed connections",
    "fix_suggestion": {
      "patch": "Use context managers for connections",
      "steps": [
        "Add context manager wrapper",
        "Update error handling",
        "Add tests"
      ]
    },
    "evidence": ["evidence-1", "evidence-2"],
    "gate": {
      "passed": true,
      "reasons": []
    }
  }
]
```

**Example:**
```bash
curl "http://localhost:8000/api/log-sentinels/forensics?severity_filter=high"
```

---

### GET /api/log-sentinels/telemetry

Get Log-Sentinels telemetry metrics.

**Response:**
```json
{
  "scout_calls": 42,
  "forensics_calls": 8,
  "escalations": 2,
  "tool_suggestions": 15,
  "timeline": [
    {
      "timestamp": "2025-01-27T00:00:00Z",
      "scout_calls": 5,
      "forensics_calls": 1,
      "escalations": 0
    }
  ]
}
```

**Example:**
```bash
curl "http://localhost:8000/api/log-sentinels/telemetry"
```

---

### GET /api/log-sentinels/stream

SSE stream for real-time Log-Sentinels updates.

**Response:** Server-Sent Events (SSE) stream

**Example:**
```bash
curl "http://localhost:8000/api/log-sentinels/stream"
```

**Event Format:**
```
data: {"type": "scout", "payload": {...}, "timestamp": "2025-01-27T00:00:00Z"}

data: {"type": "forensics", "payload": {...}, "timestamp": "2025-01-27T00:00:00Z"}

: heartbeat
```

---

### POST /api/log-sentinels/run-tool

Run suggested tool via Router → PLIx → APOE.

**Request Body:**
```json
{
  "tool": "mcp_lucid-mcp_analyze_thought_patterns"
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "analysis": "Pattern detected: Memory leak"
  }
}
```

**Example:**
```bash
curl -X POST "http://localhost:8000/api/log-sentinels/run-tool" \
  -H "Content-Type: application/json" \
  -d '{"tool": "mcp_lucid-mcp_analyze_thought_patterns"}'
```

---

## System Endpoints

### GET /health

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "router-log-sentinels-api-server",
  "version": "1.0.0"
}
```

**Example:**
```bash
curl "http://localhost:8000/health"
```

---

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK` - Success
- `400 Bad Request` - Invalid request
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error
- `503 Service Unavailable` - Service unavailable

**Error Response Format:**
```json
{
  "detail": "Error message here"
}
```

---

## Rate Limiting

Currently, no rate limiting is implemented. In production, rate limiting should be added:
- Per-IP rate limits
- Per-API-key rate limits
- Per-endpoint rate limits

---

## PLIx Integration

Tool execution endpoints (`POST /api/router/execute`, `POST /api/log-sentinels/run-tool`) use PLIx integration:

1. **Tool execution** → PLIx contract compilation
2. **Entity tag resolution** → Via HHNI (via MCP)
3. **APOE ExecutionPlan** → Generated from PLIx contract
4. **Intent verification** → Postcondition checking
5. **Evidence collection** → Stored in SEG

**PLIx Entity Tags:**
- Format: `plix://tool/{tool_name}`
- Example: `plix://tool/mcp_lucid-mcp_store_memory`

---

## MCP Integration

All AIM-OS system access goes through MCP (Model Context Protocol):

- **Command Server:** `http://localhost:5001/mcp/execute`
- **MCP Tools:** All 81 MCP tools available
- **Integration:** Via `MCPClient` wrapper class

---

## Examples

### Complete Router Flow

```python
import httpx

async def router_flow():
    async with httpx.AsyncClient() as client:
        # 1. Get tool proposals
        proposals = await client.get(
            "http://localhost:8000/api/router/tools",
            params={
                "goal": "Debug memory leak",
                "task": "Fix API handler",
                "confidence": 0.8
            }
        )
        tools = proposals.json()["tools"]
        
        # 2. Execute top tool
        if tools:
            tool = tools[0]
            result = await client.post(
                "http://localhost:8000/api/router/execute",
                json={
                    "tool": tool["tool_name"],
                    "args": tool["draft_arguments"]
                }
            )
            print(result.json())
```

### Log-Sentinels Flow

```python
import httpx
import asyncio

async def log_sentinels_flow():
    async with httpx.AsyncClient() as client:
        # 1. Get Scout reports
        scouts = await client.get("http://localhost:8000/api/log-sentinels/scouts")
        reports = scouts.json()
        
        # 2. Get Forensics for high severity
        forensics = await client.get(
            "http://localhost:8000/api/log-sentinels/forensics",
            params={"severity_filter": "high"}
        )
        forensic_reports = forensics.json()
        
        # 3. Execute suggested tool
        if forensic_reports:
            tool = forensic_reports[0]["suggested_tools"][0]
            result = await client.post(
                "http://localhost:8000/api/log-sentinels/run-tool",
                json={"tool": tool}
            )
            print(result.json())

asyncio.run(log_sentinels_flow())
```

---

## Support

For issues or questions:
- **Documentation:** See `README.md` and `IMPLEMENTATION_SUMMARY.md`
- **Tests:** See `tests/` directory
- **Source Code:** See `packages/router_api_server/`

