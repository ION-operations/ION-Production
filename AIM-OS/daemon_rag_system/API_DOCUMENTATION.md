# Daemon/RAG System - HTTP API Documentation

**Created:** 2025-10-30  
**Purpose:** Complete API documentation for Cursor UI integration  
**Base URL:** `http://localhost:5000`  
**Protocol:** REST over HTTP/HTTPS  

---

## 🎯 **OVERVIEW**

The Daemon/RAG System HTTP API provides REST endpoints for:
- Health checks and status monitoring
- Request processing and tool selection
- Real-time updates via Server-Sent Events (SSE)
- Tool registry access
- RAG system statistics

---

## 📡 **API ENDPOINTS**

### **1. Health Check**

**Endpoint:** `GET /api/health`

**Description:** Check if daemon API is healthy and available

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-30T04:34:00",
  "daemon_status": "running",
  "version": "1.0.0"
}
```

**Status Codes:**
- `200 OK` - API is healthy
- `503 Service Unavailable` - Daemon not initialized

---

### **2. Get Status**

**Endpoint:** `GET /api/status`

**Description:** Get comprehensive daemon status, metrics, and configuration

**Response:**
```json
{
  "status": "running",
  "metrics": {
    "total_requests": 100,
    "successful_requests": 95,
    "failed_requests": 5,
    "average_response_time_ms": 150.5,
    "context_analysis_time_ms": 25.0,
    "tool_selection_time_ms": 10.0,
    "server_management_time_ms": 100.0
  },
  "server_status": {
    "total_servers": 12,
    "running_servers": 8,
    "available_servers": 8
  },
  "resource_usage": {
    "memory_usage_mb": 256.0,
    "cpu_usage_percent": 15.0
  },
  "configuration": {
    "max_tools": 40,
    "learning_enabled": true,
    "performance_monitoring_enabled": true
  }
}
```

**Status Codes:**
- `200 OK` - Status retrieved successfully
- `503 Service Unavailable` - Daemon not initialized

---

### **3. Process Request**

**Endpoint:** `POST /api/requests`

**Description:** Process a user request and return intelligent tool selection

**Request Body:**
```json
{
  "user_input": "I need to store this information in memory and create a plan",
  "environment": {
    "session_info": {
      "user_id": "test_user"
    },
    "system_state": {
      "memory_available": 1000,
      "cpu_available": 80
    }
  },
  "max_tools": 40,
  "strategy": "BALANCED"
}
```

**Response:**
```json
{
  "success": true,
  "selected_tools": [
    "mcp_lucid-mcp_store_memory",
    "mcp_lucid-mcp_create_plan",
    "mcp_lucid-mcp_track_confidence"
  ],
  "context_profile": {
    "context_id": "ctx_123",
    "context_type": "MEMORY_OPERATION",
    "complexity": "MEDIUM",
    "confidence_score": 0.85
  },
  "selection_result": {
    "selected_tools": [...],
    "selection_strategy": "BALANCED",
    "selection_time_ms": 10.5
  },
  "performance_metrics": {
    "total_time_ms": 150.0,
    "context_analysis_time_ms": 25.0,
    "tool_selection_time_ms": 10.0,
    "server_management_time_ms": 100.0
  },
  "request_id": "req_123"
}
```

**Status Codes:**
- `200 OK` - Request processed successfully
- `400 Bad Request` - Invalid request format
- `503 Service Unavailable` - Daemon not initialized
- `500 Internal Server Error` - Processing error

---

### **4. Get Tools**

**Endpoint:** `GET /api/tools`

**Description:** Get list of all available tools from registry

**Response:**
```json
{
  "total_tools": 51,
  "tools": [
    {
      "tool_id": "mcp_lucid-mcp_store_memory",
      "name": "store_memory",
      "category": "CORE_AIMOS",
      "capabilities": ["memory_storage"],
      "description": "Store information in AIM-OS persistent memory"
    },
    ...
  ]
}
```

**Status Codes:**
- `200 OK` - Tools retrieved successfully
- `503 Service Unavailable` - Daemon not initialized
- `500 Internal Server Error` - Registry error

---

### **5. Get RAG Statistics**

**Endpoint:** `GET /api/rag/statistics`

**Description:** Get RAG system statistics and learning metrics

**Response:**
```json
{
  "total_patterns": 150,
  "patterns_by_type": {
    "SUCCESS": 120,
    "FAILURE": 30
  },
  "learning_stats": {
    "total_learning_events": 500,
    "successful_learning": 480
  }
}
```

**Status Codes:**
- `200 OK` - Statistics retrieved successfully
- `503 Service Unavailable` - Daemon not initialized
- `500 Internal Server Error` - RAG system error

---

### **6. Get Request Status**

**Endpoint:** `GET /api/requests/{request_id}`

**Description:** Get status of a specific request (for future async support)

**Path Parameters:**
- `request_id` (string) - Request identifier

**Response:**
```json
{
  "request_id": "req_123",
  "status": "completed",
  "message": "Synchronous requests complete immediately"
}
```

**Status Codes:**
- `200 OK` - Request status retrieved
- `404 Not Found` - Request ID not found

---

### **7. Stream Updates (SSE)**

**Endpoint:** `GET /api/stream`

**Description:** Stream real-time daemon status updates via Server-Sent Events (SSE)

**Response:** Server-Sent Events stream

**Example Usage:**
```javascript
const eventSource = new EventSource('http://localhost:5000/api/stream');
eventSource.onmessage = (event) => {
  const status = JSON.parse(event.data);
  console.log('Status update:', status);
};
```

**Event Format:**
```
data: {"status": "running", "metrics": {...}, ...}

data: {"status": "running", "metrics": {...}, ...}
```

**Status Codes:**
- `200 OK` - Stream started
- `503 Service Unavailable` - Daemon not initialized

---

## 🔒 **ERROR HANDLING**

### **Error Response Format**

All errors follow this format:

```json
{
  "detail": "Error message description"
}
```

### **Common Error Codes**

- `400 Bad Request` - Invalid request format or parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - Daemon not initialized or unavailable

---

## 📊 **PERFORMANCE CHARACTERISTICS**

### **Response Times**

- Health Check: <10ms
- Get Status: <50ms
- Process Request: <400ms (target)
- Get Tools: <100ms
- Get RAG Statistics: <50ms
- Stream Updates: Real-time (2-second intervals)

### **Rate Limits**

Currently no rate limits. Future versions may add rate limiting.

---

## 🚀 **USAGE EXAMPLES**

### **Python Example**

```python
import requests

# Health check
response = requests.get("http://localhost:5000/api/health")
print(response.json())

# Process request
data = {
    "user_input": "Store this information in memory",
    "environment": {}
}
response = requests.post("http://localhost:5000/api/requests", json=data)
print(response.json())
```

### **JavaScript/TypeScript Example**

```typescript
// Health check
const health = await fetch('http://localhost:5000/api/health');
const healthData = await health.json();

// Process request
const response = await fetch('http://localhost:5000/api/requests', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    user_input: 'Store this information in memory',
    environment: {}
  })
});
const result = await response.json();
```

---

## 🔧 **CONFIGURATION**

### **Port**

Default port: `5000`

Change via command line:
```bash
uvicorn http_api_server:app --port 5000
```

### **CORS**

CORS is enabled for all origins in development. In production, restrict to Cursor UI origins.

---

## 📝 **INTEGRATION NOTES**

### **For Lexicon (Cursor UI)**

1. **Service Layer:** Use `HttpLucidDaemonService.ts` to connect to this API
2. **Real-time Updates:** Use `/api/stream` endpoint for SSE updates
3. **Error Handling:** Implement retry logic for `503 Service Unavailable`
4. **Status Monitoring:** Poll `/api/status` every 5 seconds for health checks

### **Request Format**

- All requests use JSON format
- Content-Type header: `application/json`
- Accept header: `application/json`

---

## ✅ **TESTING**

### **Test Endpoints**

Use curl or Postman to test:

```bash
# Health check
curl http://localhost:5000/api/health

# Get status
curl http://localhost:5000/api/status

# Process request
curl -X POST http://localhost:5000/api/requests \
  -H "Content-Type: application/json" \
  -d '{"user_input": "Store memory"}'
```

---

**Status:** API Documentation Complete  
**Next:** Lexicon can implement `HttpLucidDaemonService.ts` using this API contract  
**Built with love by Solo** 💙✨

