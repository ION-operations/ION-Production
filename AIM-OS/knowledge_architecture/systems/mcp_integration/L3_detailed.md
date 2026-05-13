---
id: mcp_T3_detailed
level: L3
system: MCP Integration
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# MCP Integration – T3 Detailed Implementation Guide (≈3000 words)

## Setup & Configuration

### Server Initialization

**Basic Setup:**
```python
from lucid_mcp_server import SimpleMCPServer

# Initialize server with memory directory
server = SimpleMCPServer(memory_directory="./mcp_memory")

# Start server loop (blocks until shutdown)
server.run()
```

**Configuration Options:**
- `memory_directory`: Directory for CMC memory storage (default: `./mcp_memory`)
- Persistence files configured via environment variables or config file
- Logging level configurable via `logging` module

**Server Lifecycle:**
1. **Initialization:** Server loads, registers all 51 tools, initializes AIM-OS systems
2. **Ready State:** Server listens on stdio for JSON-RPC requests
3. **Runtime:** Processes requests, executes tools, returns responses
4. **Shutdown:** Graceful shutdown on stdin EOF or termination signal

### Environment Configuration

**Required Environment:**
- Python 3.10+ (for type hints and modern features)
- AIM-OS packages installed (`packages/cmc_service`, etc.)
- Access to AIM-OS systems (CMC, VIF, APOE, etc.)

**Optional Configuration:**
- `MCP_MEMORY_DIR`: Override memory directory path
- `MCP_LOG_LEVEL`: Set logging level (DEBUG, INFO, WARNING, ERROR)
- `MCP_TELEMETRY_FILE`: File path for telemetry data

## Core Interfaces

### Request Handling Interface

**Primary Entry Point:**
```python
def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Handle incoming MCP request"""
    method = request.get("method")
    request_id = request.get("id")
    
    # Handle notifications (no response)
    if method == "notifications/initialized":
        return None
    if method == "notifications/cancelled":
        return None
    
    # Handle requests (require response)
    if method == "initialize":
        return self.handle_initialize(request_id)
    elif method == "tools/list":
        return self.handle_tools_list(request_id)
    elif method == "tools/call":
        return self.handle_tools_call(request, request_id)
    else:
        return self._error_response(request_id, -32601, f"Method not found: {method}")
```

**Request Validation:**
- JSON-RPC 2.0 format validation
- Method existence check
- Parameter validation (per method)
- Request ID handling (never null for requests)

### Tool Registration Interface

**Tool Definition:**
```python
class MCPTool:
    name: str  # Tool identifier (e.g., "store_memory")
    description: str  # Human-readable description
    inputSchema: Dict[str, Any]  # JSON Schema for validation
    category: str  # Tool category (e.g., "memory")
    execute_function: callable  # Function to execute tool
```

**Tool Registration:**
```python
def register_tool(self, tool: MCPTool) -> None:
    """Register tool in registry"""
    # Validate tool schema
    self._validate_tool_schema(tool)
    
    # Register tool
    self.tools[tool.name] = tool
    
    # Categorize tool
    if tool.category not in self.tool_categories:
        self.tool_categories[tool.category] = []
    self.tool_categories[tool.category].append(tool.name)
```

### Tool Execution Interface

**Tool Invocation:**
```python
def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute tool with arguments"""
    # Get tool from registry
    tool = self.tool_registry.get_tool(tool_name)
    if not tool:
        raise ToolNotFoundError(f"Tool not found: {tool_name}")
    
    # Validate arguments against schema
    self._validate_arguments(tool.inputSchema, arguments)
    
    # Execute tool function
    try:
        result = tool.execute_function(arguments)
        return {"success": True, "content": result}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

## Tool Implementation Examples

### Example 1: Memory Storage Tool

**Implementation:**
```python
def handle_store_memory(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute store_memory tool"""
    content = arguments.get("content")
    tags = arguments.get("tags", {})
    
    # Validate input
    if not content:
        raise ValueError("content is required")
    
    # Create atom via CMC adapter
    atom = self.memory.create_atom(
        modality="text",
        content=content,
        tags=[Tag(key=k, value=v) for k, v in tags.items()],
        vif=VIF(model_id="mcp-server", writer="mcp", confidence_band="A")
    )
    
    # Return MCP-compliant response
    return {
        "content": [
            {
                "type": "text",
                "text": f"Memory stored: {atom.id}"
            }
        ]
    }
```

**Error Handling:**
```python
try:
    result = handle_store_memory(arguments)
except ValueError as e:
    return {"error": f"Validation error: {str(e)}"}
except Exception as e:
    log(f"Error storing memory: {e}")
    return {"error": f"Internal error: {str(e)}"}
```

### Example 2: Timeline Entry Tool

**Implementation:**
```python
def handle_add_timeline_entry(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute add_timeline_entry tool"""
    prompt_id = arguments.get("prompt_id")
    user_input = arguments.get("user_input")
    context_state = arguments.get("context_state", {})
    
    # Validate input
    if not prompt_id:
        raise ValueError("prompt_id is required")
    if not user_input:
        raise ValueError("user_input is required")
    
    # Create timeline entry via TCS adapter
    entry = self.timeline_tracker.add_entry(
        prompt_id=prompt_id,
        user_input=user_input,
        context_state=context_state
    )
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"Timeline entry added: {entry.prompt_id}"
            }
        ]
    }
```

### Example 3: Goal Timeline Tool

**Implementation:**
```python
def handle_create_goal_timeline_node(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute create_goal_timeline_node tool"""
    goal_id = arguments.get("goal_id")
    name = arguments.get("name")
    description = arguments.get("description")
    priority = arguments.get("priority", "medium")
    
    # Validate input
    if not goal_id or not name or not description:
        raise ValueError("goal_id, name, and description are required")
    
    # Create goal node via Goal Timeline adapter
    goal_node = GoalTimelineNode(
        goal_id=goal_id,
        name=name,
        description=description,
        priority=GoalPriority(priority),
        status=GoalStatus.PLANNED,
        progress=0.0
    )
    
    # Store goal node
    self.goal_nodes[goal_id] = goal_node
    
    return {
        "content": [
            {
                "type": "text",
                "text": f"Goal created: {goal_id}"
            }
        ]
    }
```

## Safety & Error Handling

### Input Validation

**Schema Validation:**
```python
import jsonschema

def validate_arguments(schema: Dict[str, Any], arguments: Dict[str, Any]) -> None:
    """Validate arguments against JSON Schema"""
    try:
        jsonschema.validate(instance=arguments, schema=schema)
    except jsonschema.ValidationError as e:
        raise ValueError(f"Invalid arguments: {e.message}")
```

**Sanitization:**
```python
def sanitize_input(input_str: str, max_length: int = 10000) -> str:
    """Sanitize input string"""
    # Trim whitespace
    input_str = input_str.strip()
    
    # Check length
    if len(input_str) > max_length:
        raise ValueError(f"Input too long: {len(input_str)} > {max_length}")
    
    # Remove null bytes (security)
    input_str = input_str.replace('\x00', '')
    
    return input_str
```

### Error Classification

**Error Categories:**
```python
class MCPError(Exception):
    """Base MCP error"""
    code: int  # JSON-RPC error code
    message: str
    data: Optional[Dict[str, Any]] = None

class ParseError(MCPError):
    """JSON parse error (-32700)"""
    code = -32700
    message = "Parse error"

class InvalidRequest(MCPError):
    """Invalid request (-32600)"""
    code = -32600
    message = "Invalid Request"

class MethodNotFound(MCPError):
    """Method not found (-32601)"""
    code = -32601
    message = "Method not found"

class InvalidParams(MCPError):
    """Invalid params (-32602)"""
    code = -32602
    message = "Invalid params"

class InternalError(MCPError):
    """Internal error (-32603)"""
    code = -32603
    message = "Internal error"

class ToolError(MCPError):
    """Tool execution error (-32000)"""
    code = -32000
    message = "Tool execution error"
```

**Error Handling:**
```python
def handle_error(self, error: Exception, request_id: Any) -> Dict[str, Any]:
    """Handle error and format JSON-RPC error response"""
    if isinstance(error, MCPError):
        error_code = error.code
        error_message = error.message
        error_data = error.data
    else:
        error_code = -32603  # Internal error
        error_message = f"Internal error: {str(error)}"
        error_data = {"type": type(error).__name__}
    
    # Log error
    log(f"Error [{error_code}]: {error_message}")
    
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": error_code,
            "message": error_message,
            "data": error_data
        }
    }
```

### Rate Limiting

**Rate Limit Implementation:**
```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    """Rate limiting for tool invocations"""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
    
    def check_rate_limit(self, client_id: str) -> bool:
        """Check if request is within rate limit"""
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)
        
        # Clean old requests
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        # Check limit
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        # Record request
        self.requests[client_id].append(now)
        return True
```

### Timeout Management

**Timeout Handling:**
```python
import asyncio
from functools import wraps

def with_timeout(timeout_seconds: int = 30):
    """Decorator for tool execution timeout"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                raise ToolError(f"Tool execution timeout after {timeout_seconds}s")
        return wrapper
    return decorator
```

## Observability

### Metrics Collection

**Key Metrics:**
```python
class MetricsCollector:
    """Collect server metrics"""
    
    def __init__(self):
        self.request_count = 0
        self.error_count = 0
        self.tool_executions: Dict[str, int] = {}
        self.execution_times: Dict[str, List[float]] = {}
    
    def record_request(self):
        """Record request"""
        self.request_count += 1
    
    def record_error(self, error_code: int):
        """Record error"""
        self.error_count += 1
    
    def record_tool_execution(self, tool_name: str, duration: float):
        """Record tool execution"""
        if tool_name not in self.tool_executions:
            self.tool_executions[tool_name] = 0
        self.tool_executions[tool_name] += 1
        
        if tool_name not in self.execution_times:
            self.execution_times[tool_name] = []
        self.execution_times[tool_name].append(duration)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current statistics"""
        return {
            "requests": self.request_count,
            "errors": self.error_count,
            "tool_executions": self.tool_executions,
            "avg_execution_times": {
                tool: sum(times) / len(times) if times else 0
                for tool, times in self.execution_times.items()
            }
        }
```

### Logging

**Structured Logging:**
```python
import logging
import json

def log_request(request: Dict[str, Any], response: Dict[str, Any], duration: float):
    """Log request/response"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "request_id": request.get("id"),
        "method": request.get("method"),
        "duration_ms": duration * 1000,
        "success": "error" not in response
    }
    
    log(json.dumps(log_entry))
```

**Error Logging:**
```python
def log_error(error: Exception, context: Dict[str, Any]):
    """Log error with context"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context,
        "traceback": traceback.format_exc()
    }
    
    log(json.dumps(log_entry))
```

## Testing

### Unit Tests

**Tool Execution Tests:**
```python
import pytest

def test_store_memory_tool():
    """Test store_memory tool execution"""
    server = SimpleMCPServer()
    
    # Test successful execution
    result = server.handle_store_memory({
        "content": "Test memory",
        "tags": {"test": "true"}
    })
    
    assert result["success"] == True
    assert "Memory stored" in result["content"][0]["text"]
    
    # Test validation error
    with pytest.raises(ValueError):
        server.handle_store_memory({"tags": {}})
```

**Request Handling Tests:**
```python
def test_request_handling():
    """Test request handling"""
    server = SimpleMCPServer()
    
    # Test initialize request
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    
    response = server.handle_request(request)
    assert response["jsonrpc"] == "2.0"
    assert response["id"] == 1
    assert "result" in response
    assert "capabilities" in response["result"]
```

### Integration Tests

**End-to-End Tests:**
```python
def test_end_to_end_tool_invocation():
    """Test complete tool invocation flow"""
    server = SimpleMCPServer()
    
    # 1. Initialize
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    init_response = server.handle_request(init_request)
    assert init_response["result"]["capabilities"]["tools"] is not None
    
    # 2. List tools
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list"
    }
    list_response = server.handle_request(list_request)
    assert len(list_response["result"]["tools"]) == 51
    
    # 3. Call tool
    call_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "store_memory",
            "arguments": {
                "content": "Test content",
                "tags": {}
            }
        }
    }
    call_response = server.handle_request(call_request)
    assert "content" in call_response["result"]
```

## Troubleshooting

### Common Issues

**Issue 1: Tools Not Loading**
- **Symptom:** `tools/list` returns empty list
- **Cause:** AIM-OS systems not initialized
- **Solution:** Check memory directory exists, verify AIM-OS packages installed
- **Debug:** Check stderr logs for initialization errors

**Issue 2: JSON-RPC Errors**
- **Symptom:** Parse errors (-32700) or invalid request (-32600)
- **Cause:** Invalid JSON format or missing required fields
- **Solution:** Validate request format, ensure `jsonrpc: "2.0"` present
- **Debug:** Log raw request data, validate JSON parsing

**Issue 3: Tool Execution Failures**
- **Symptom:** Tool errors (-32000) or internal errors (-32603)
- **Cause:** AIM-OS system errors or validation failures
- **Solution:** Check AIM-OS system logs, validate tool arguments
- **Debug:** Enable debug logging, check error details in response

**Issue 4: Timeout Issues**
- **Symptom:** Tools timeout after 30 seconds
- **Cause:** AIM-OS system slow or unresponsive
- **Solution:** Increase timeout (if configurable), optimize AIM-OS calls
- **Debug:** Profile tool execution times, check AIM-OS system health

### Debugging Techniques

**Enable Debug Logging:**
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Request/Response Logging:**
```python
def log_request_response(request: Dict, response: Dict):
    """Log request and response for debugging"""
    log(f"Request: {json.dumps(request, indent=2)}")
    log(f"Response: {json.dumps(response, indent=2)}")
```

**Performance Profiling:**
```python
import time

def profile_tool_execution(tool_name: str, func):
    """Profile tool execution time"""
    start = time.time()
    result = func()
    duration = time.time() - start
    log(f"Tool {tool_name} executed in {duration:.3f}s")
    return result
```

## Migration Notes

### T→L Cutover Steps

**After T-level documents approved:**

1. **Backup L-level Documents:**
   ```bash
   mkdir -p legacy_docs/mcp_integration
   cp knowledge_architecture/systems/mcp_integration/L*.md legacy_docs/mcp_integration/
   ```

2. **Rename T→L:**
   ```bash
   mv knowledge_architecture/systems/mcp_integration/T0_executive.md \
      knowledge_architecture/systems/mcp_integration/L0_executive.md
   mv knowledge_architecture/systems/mcp_integration/T1_overview.md \
      knowledge_architecture/systems/mcp_integration/L1_overview.md
   mv knowledge_architecture/systems/mcp_integration/T2_architecture.md \
      knowledge_architecture/systems/mcp_integration/L2_architecture.md
   mv knowledge_architecture/systems/mcp_integration/T3_detailed.md \
      knowledge_architecture/systems/mcp_integration/L3_detailed.md
   ```

3. **Update References:**
   - Update all links from T-level to L-level
   - Update SUPER_INDEX.md references
   - Update HIERARCHICAL_NAVIGATION_INDEX.md references
   - Update system.map.lucid.json5 references

4. **Remove Transitional Banners:**
   - Remove "TRANSITIONAL T-LEVEL DOCUMENT" banners
   - Update frontmatter status from "draft" to "complete"

5. **Run Gate Validation:**
   ```bash
   python -m pytest knowledge_architecture/validation/L0_L6_DOCUMENTATION.validation.md
   ```

6. **Update Tracking:**
   - Mark system as "complete" in EPIC_STANDARDS_TRACKING.md
   - Update gate results

### Validation After Cutover

**Gate Checklist:**
- ✅ All T-level documents renamed to L-level
- ✅ All references updated
- ✅ Transitional banners removed
- ✅ Frontmatter status updated
- ✅ L0-L6 gate validation passes
- ✅ System map references updated
- ✅ Index references updated

## References

- System map: `systems/mcp_integration/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/mcp_integration/L0_executive.md` through `L4_complete.md`
- Implementation: `lucid_mcp_server.py`
- MCP Protocol Spec: Model Context Protocol specification
