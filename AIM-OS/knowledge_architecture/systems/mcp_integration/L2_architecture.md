---
id: mcp_T2_architecture
level: L2
system: MCP Integration
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# MCP Integration – T2 Architecture (≈2000 words)

## System Overview

MCP Integration implements the Model Context Protocol (MCP) server architecture that exposes all 51 AIM-OS consciousness systems as standardized tools accessible through Cursor IDE and other MCP-compliant clients. The system provides a unified protocol interface that abstracts away AIM-OS implementation details while maintaining full protocol compliance and production-ready reliability.

MCP Integration provides three core architectural guarantees:

1. **Protocol Abstraction:** Clean separation between MCP protocol implementation and AIM-OS system implementations. Tool adapters translate MCP calls to AIM-OS APIs, enabling protocol changes without modifying AIM-OS systems.

2. **Tool Lifecycle Management:** Complete tool registration, discovery, validation, execution, and observability. Tools organized into 12 categories with metadata for filtering, selection, and execution tracking.

3. **Production Reliability:** Comprehensive error handling, timeout management, observability (metrics, logs, traces), and safety checks. Server operates reliably in production with graceful degradation and error recovery.

## Components

### 1. MCP Server Core

**Purpose:** Central JSON-RPC 2.0 server implementation handling all protocol operations

**Responsibilities:**
- Server initialization and configuration
- Request/response lifecycle management
- JSON-RPC 2.0 protocol compliance
- Transport layer management (stdio for IDE integration)
- Server state management

**Key Operations:**
- `initialize()` - Initialize server with configuration, register tools, setup handlers
- `handle_request()` - Process incoming JSON-RPC requests with validation and routing
- `shutdown()` - Graceful server shutdown with cleanup
- `get_capabilities()` - Return server capabilities and tool list

**Architecture:**
```python
class MCPServer:
    server_config: MCPServerConfig
    tool_registry: ToolRegistry
    request_handler: RequestHandler
    response_generator: ResponseGenerator
    error_handler: ErrorHandler
    logging_system: LoggingSystem
    observability: ObservabilityLayer
```

### 2. Tool Registry

**Purpose:** Central registry for all 51 AIM-OS tools with discovery, validation, and execution capabilities

**Responsibilities:**
- Tool registration and lifecycle management
- Tool discovery and metadata retrieval
- Tool categorization (12 categories)
- Tool validation and schema checking
- Tool execution coordination

**Key Operations:**
- `register_tool()` - Register new tool with validation
- `get_tool()` - Retrieve tool by name
- `list_tools()` - List all registered tools
- `list_tools_by_category()` - Filter tools by category
- `validate_tool_request()` - Validate tool invocation request

**Tool Categories:**
- Core AIM-OS (6 tools): Memory, knowledge, confidence tracking
- SCOR (3 tools): Safety, consciousness, reliability monitoring
- Timeline Context (3 tools): Timeline tracking and context preservation
- Goal Timeline (3 tools): Goal management and progress tracking
- IIS (3 tools): Intuition and learning systems
- Co-Agency (3 tools): Human-AI collaboration protocols
- Dataset Management (4 tools): Data operations and analysis
- Application Lifecycle (3 tools): Application management
- Autonomous Protocol (9 tools): Autonomous operation and safety
- Autonomous Research Dream (3 tools): Advanced research capabilities
- AI Collaboration (6 tools): Multi-AI coordination
- Observability (4 tools): System monitoring and health checks

### 3. Tool Adapter Layer

**Purpose:** Bridge between MCP tool calls and AIM-OS system APIs

**Responsibilities:**
- Translate MCP request format to AIM-OS API calls
- Handle AIM-OS system errors and translate to MCP errors
- Format AIM-OS responses as MCP-compliant responses
- Manage async operations and timeouts
- Provide authentication/authorization proxy

**Key Operations:**
- `adapt_request()` - Convert MCP request to AIM-OS API call
- `adapt_response()` - Convert AIM-OS response to MCP format
- `handle_error()` - Translate AIM-OS errors to MCP errors
- `execute_with_timeout()` - Execute AIM-OS call with timeout

**Adapter Pattern:**
Each AIM-OS system has a dedicated adapter:
- `CMCAdapter` - Memory operations (store_memory, retrieve_memory, get_memory_stats)
- `APOEAdapter` - Plan operations (create_plan)
- `VIFAdapter` - Confidence tracking (track_confidence)
- `SEGAdapter` - Knowledge synthesis (synthesize_knowledge)
- `SCORAdapter` - Safety checks (check_invariant, run_baseline_probe)
- `TimelineAdapter` - Timeline operations (add_timeline_entry, get_timeline_summary)
- And adapters for all other AIM-OS systems

### 4. Request Handler

**Purpose:** Process and route incoming JSON-RPC 2.0 requests

**Responsibilities:**
- Request validation (JSON-RPC 2.0 compliance)
- Request routing (method → tool or handler)
- Request execution coordination
- Response generation
- Error handling

**Key Operations:**
- `validate_request()` - Validate JSON-RPC 2.0 request format
- `route_request()` - Route request to appropriate handler
- `execute_request()` - Execute request and capture result
- `generate_response()` - Generate JSON-RPC 2.0 response

**Request Types:**
- `initialize` - Client initialization
- `tools/list` - List available tools
- `tools/call` - Invoke tool
- `notifications/initialized` - Client ready notification
- `notifications/cancelled` - Request cancellation

### 5. Response Generator

**Purpose:** Generate JSON-RPC 2.0 compliant responses

**Responsibilities:**
- Format successful responses
- Format error responses
- Handle request/response correlation (request_id)
- Add metadata and context
- Ensure protocol compliance

**Key Operations:**
- `generate_success_response()` - Format successful tool execution
- `generate_error_response()` - Format errors with proper codes
- `generate_notification_response()` - Handle notifications (no response)

### 6. Error Handler

**Purpose:** Comprehensive error handling and recovery

**Responsibilities:**
- Error classification (protocol errors, tool errors, system errors)
- Error translation (AIM-OS errors → MCP errors)
- Error logging and metrics
- Error recovery strategies
- User-friendly error messages

**Error Categories:**
- Protocol Errors (-32700 to -32701): Invalid JSON, parse errors
- Method Errors (-32601 to -32603): Method not found, invalid params
- Tool Errors (-32000 to -32099): Tool execution errors
- System Errors (-32100 to -32199): AIM-OS system failures

### 7. Safety Layer

**Purpose:** Security and safety checks before tool execution

**Responsibilities:**
- Authentication/authorization checks
- Rate limiting and throttling
- Input validation and sanitization
- Invariant checks (via SCOR)
- Safety policy enforcement

**Key Operations:**
- `check_auth()` - Verify client authentication
- `check_rate_limit()` - Enforce rate limits
- `validate_input()` - Validate tool input parameters
- `check_invariant()` - Call SCOR for invariant validation

### 8. Observability Layer

**Purpose:** Metrics, logging, tracing, and monitoring

**Responsibilities:**
- Request/response metrics
- Tool execution metrics
- Error tracking and alerting
- Performance monitoring
- Debug logging

**Metrics Tracked:**
- Request rate (requests/second)
- Tool execution time (p50, p95, p99)
- Error rate (errors/second)
- Tool usage by category
- System health indicators

**Logging:**
- Structured JSON logs
- Request/response logging
- Error logging with stack traces
- Debug logging (configurable)

## Data Models

### JSON-RPC 2.0 Request Schema

```python
class JSONRPCRequest(BaseModel):
    jsonrpc: Literal["2.0"]  # Protocol version
    id: Optional[Union[str, int]]  # Request ID (null for notifications)
    method: str  # Method name (e.g., "tools/call")
    params: Optional[Dict[str, Any]]  # Method parameters
```

### JSON-RPC 2.0 Response Schema

```python
class JSONRPCResponse(BaseModel):
    jsonrpc: Literal["2.0"]  # Protocol version
    id: Optional[Union[str, int]]  # Request ID (matches request)
    result: Optional[Dict[str, Any]]  # Success result (null if error)
    error: Optional[JSONRPCError]  # Error object (null if success)
```

### JSON-RPC 2.0 Error Schema

```python
class JSONRPCError(BaseModel):
    code: int  # Error code (-32700 to -32199)
    message: str  # Error message
    data: Optional[Dict[str, Any]]  # Additional error data
```

### Tool Specification Schema

```python
class MCPTool(BaseModel):
    name: str  # Tool identifier (e.g., "store_memory")
    description: str  # Human-readable description
    inputSchema: Dict[str, Any]  # JSON Schema for input validation
    category: str  # Tool category (e.g., "memory", "safety")
    metadata: Optional[Dict[str, Any]]  # Additional metadata
```

### Tool Call Request Schema

```python
class ToolCallRequest(BaseModel):
    name: str  # Tool name
    arguments: Dict[str, Any]  # Tool arguments (validated against inputSchema)
```

### Tool Call Response Schema

```python
class ToolCallResponse(BaseModel):
    content: List[ToolCallContent]  # Tool execution results
    isError: Optional[bool]  # Whether execution failed
    
class ToolCallContent(BaseModel):
    type: Literal["text", "resource"]  # Content type
    text: Optional[str]  # Text content
    resource: Optional[ResourceReference]  # Resource reference
```

### Tool Execution Context Schema

```python
class ToolExecutionContext(BaseModel):
    tool_name: str  # Tool being executed
    request_id: str  # Request identifier
    client_id: Optional[str]  # Client identifier
    timestamp: datetime  # Execution timestamp
    metadata: Dict[str, Any]  # Execution metadata
```

## System Flows

### Flow 1: Server Initialization

```
1. Server Startup
   ↓
2. Load Configuration (server_config.json)
   ↓
3. Initialize Core Components
   - Tool Registry
   - Request Handler
   - Response Generator
   - Error Handler
   - Observability Layer
   ↓
4. Register All Tools (51 tools)
   - Core AIM-OS tools (6)
   - SCOR tools (3)
   - Timeline Context tools (3)
   - Goal Timeline tools (3)
   - IIS tools (3)
   - Co-Agency tools (3)
   - Dataset Management tools (4)
   - Application Lifecycle tools (3)
   - Autonomous Protocol tools (9)
   - Autonomous Research Dream tools (3)
   - AI Collaboration tools (6)
   - Observability tools (4)
   ↓
5. Setup JSON-RPC 2.0 Handlers
   - initialize handler
   - tools/list handler
   - tools/call handler
   - notifications handlers
   ↓
6. Initialize Observability
   - Setup metrics collection
   - Setup logging
   - Setup tracing
   ↓
7. Server Ready (listening on stdio)
```

### Flow 2: Tool Discovery

```
1. Client Sends: {"jsonrpc": "2.0", "method": "tools/list", "id": 1}
   ↓
2. Request Handler Validates Request
   - Check JSON-RPC 2.0 format
   - Validate method exists
   ↓
3. Route to tools/list Handler
   ↓
4. Tool Registry Lists All Tools
   - Retrieve all 51 tools
   - Include metadata (category, description, schema)
   ↓
5. Filter Tools (if category filter provided)
   ↓
6. Response Generator Formats Response
   {
     "jsonrpc": "2.0",
     "id": 1,
     "result": {
       "tools": [
         {"name": "store_memory", "description": "...", "inputSchema": {...}},
         ...
       ]
     }
   }
   ↓
7. Send Response to Client (via stdio)
```

### Flow 3: Tool Invocation

```
1. Client Sends: {"jsonrpc": "2.0", "method": "tools/call", "params": {"name": "store_memory", "arguments": {...}}, "id": 2}
   ↓
2. Request Handler Validates Request
   - Check JSON-RPC 2.0 format
   - Validate method = "tools/call"
   - Validate params structure
   ↓
3. Route to tools/call Handler
   ↓
4. Tool Registry Validates Tool
   - Check tool exists
   - Validate arguments against inputSchema
   ↓
5. Safety Layer Checks
   - Authentication check
   - Rate limit check
   - Input sanitization
   - Invariant check (via SCOR)
   ↓
6. Tool Adapter Translates Request
   - MCP request → AIM-OS API call
   - Example: store_memory → CMC.create_atom()
   ↓
7. Execute AIM-OS API Call
   - Call CMC adapter
   - Handle async operations
   - Manage timeout
   ↓
8. Tool Adapter Translates Response
   - AIM-OS response → MCP response format
   - Handle errors
   ↓
9. Response Generator Formats Response
   {
     "jsonrpc": "2.0",
     "id": 2,
     "result": {
       "content": [...]
     }
   }
   ↓
10. Observability Records Metrics
    - Execution time
    - Success/failure
    - Error details (if any)
   ↓
11. Send Response to Client (via stdio)
```

### Flow 4: Error Handling

```
1. Error Occurs (anywhere in flow)
   ↓
2. Error Handler Classifies Error
   - Protocol error (-32700 to -32701)
   - Method error (-32601 to -32603)
   - Tool error (-32000 to -32099)
   - System error (-32100 to -32199)
   ↓
3. Error Handler Logs Error
   - Structured error log
   - Stack trace (if available)
   - Context metadata
   ↓
4. Error Handler Records Metrics
   - Error rate
   - Error type distribution
   ↓
5. Response Generator Formats Error Response
   {
     "jsonrpc": "2.0",
     "id": <request_id>,
     "error": {
       "code": <error_code>,
       "message": "<error_message>",
       "data": {...}
     }
   }
   ↓
6. Send Error Response to Client
```

## Integrations

### Integration with AIM-OS Systems

**CMC Integration:**
- Memory storage: `store_memory` → `CMC.create_atom()`
- Memory retrieval: `retrieve_memory` → `CMC.query_atoms()` via HHNI
- Memory stats: `get_memory_stats` → `CMC.get_statistics()`

**APOE Integration:**
- Plan creation: `create_plan` → `APOE.compile_plan()`
- Plan execution: Delegated to APOE runtime

**VIF Integration:**
- Confidence tracking: `track_confidence` → `VIF.create_witness()`
- Provenance queries: Via VIF API

**SEG Integration:**
- Knowledge synthesis: `synthesize_knowledge` → `SEG.synthesize()`
- Contradiction detection: Via SEG queries

**SCOR Integration:**
- Invariant checks: `check_invariant` → `SCOR.validate_action()`
- Baseline probes: `run_baseline_probe` → `SCOR.run_probe()`
- Manipulation detection: `detect_manipulation_signals` → `SCOR.detect_manipulation()`

**Timeline Context System Integration:**
- Timeline entries: `add_timeline_entry` → `TCS.record_entry()`
- Timeline queries: `get_timeline_summary` → `TCS.query_timeline()`

**IIS Integration:**
- Intuition computation: `compute_intuition` → `IIS.compute_score()`
- Weight updates: `update_intuition_weights` → `IIS.update_weights()`

**All Other AIM-OS Systems:** Similar adapter pattern for each system

### Integration with Cursor IDE

**Transport Layer:**
- stdio transport (stdin/stdout)
- JSON-RPC 2.0 protocol over stdio
- Request/response correlation via request_id

**Protocol Handshake:**
- Client sends `initialize` request
- Server responds with capabilities and tool list
- Client sends `notifications/initialized`
- Server ready for tool invocations

**Tool Discovery:**
- IDE queries `tools/list` on startup
- IDE caches tool metadata
- IDE updates tool list on `tools/listChanged` notification

**Tool Invocation:**
- IDE sends `tools/call` requests
- Server executes tools and returns results
- IDE displays results to user

## Non-Functional Requirements

### Performance Requirements

**Latency:**
- Tool invocation: < 100ms p95 (excluding AIM-OS execution time)
- Tool discovery: < 10ms p95
- Request validation: < 1ms p95

**Throughput:**
- Request rate: > 100 requests/second
- Concurrent tool executions: > 50 concurrent
- Tool registry queries: > 1000 queries/second

**Resource Usage:**
- Memory: < 100MB baseline + 10MB per concurrent request
- CPU: < 10% baseline + 5% per request/second
- Network: Minimal (stdio transport)

### Reliability Requirements

**Availability:**
- Uptime: > 99.9% (when AIM-OS systems available)
- Graceful degradation: Server continues operating if individual tools fail
- Error recovery: Automatic recovery from transient errors

**Fault Tolerance:**
- Handle AIM-OS system failures gracefully
- Timeout management: Tools timeout after 30 seconds
- Retry logic: Configurable retry for transient failures

**Error Handling:**
- All errors logged with context
- Errors never crash server
- User-friendly error messages

### Security Requirements

**Authentication:**
- Client authentication (via Cursor IDE)
- Tool execution authorization checks
- Rate limiting per client

**Input Validation:**
- All tool inputs validated against schemas
- Input sanitization to prevent injection
- Size limits on request payloads

**Safety Checks:**
- SCOR invariant checks before tool execution
- Safety policy enforcement
- Audit logging for sensitive operations

### Observability Requirements

**Metrics:**
- Request rate, latency, error rate
- Tool execution time and success rate
- System resource usage

**Logging:**
- Structured JSON logs
- Request/response logging (configurable)
- Error logging with stack traces
- Debug logging (configurable level)

**Tracing:**
- Request tracing across tool execution
- Trace IDs for correlation
- Distributed tracing support (future)

## Diagrams

### Component Diagram

```
[Cursor IDE Client]
       ↓ (stdio)
[MCP Server Core]
       ↓
[Request Handler] → [Response Generator]
       ↓
[Tool Registry] → [Tool Adapter Layer]
       ↓
[Safety Layer] → [SCOR]
       ↓
[AIM-OS Systems]
- CMC
- APOE
- VIF
- SEG
- SCOR
- TCS
- IIS
- ... (all 51 tools)
```

### Tool Invocation Sequence Diagram

```
Client          Server          Registry         Adapter          AIM-OS
  |               |                |                |                |
  |--tools/call-->|                |                |                |
  |               |--validate----->|                |                |
  |               |--route-------->|                |                |
  |               |--get_tool----->|                |                |
  |               |--check_safety->|                |                |
  |               |                |                |--adapt_request->|
  |               |                |                |--execute------>|
  |               |                |                |<--response-----|
  |               |                |                |--adapt_resp--->|
  |               |<--format_resp--|                |                |
  |<--response----|                |                |                |
```

## References

- System map: `systems/mcp_integration/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/mcp_integration/L0_executive.md` through `L4_complete.md`
- Implementation: `lucid_mcp_server.py`, `run_mcp_aimos.py`
- MCP Protocol Spec: Model Context Protocol specification
