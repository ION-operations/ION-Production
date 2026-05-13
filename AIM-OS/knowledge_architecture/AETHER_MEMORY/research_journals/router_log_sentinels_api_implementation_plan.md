# Router & Log-Sentinels API Server - Comprehensive Implementation Plan

**Date:** 2025-01-27  
**Status:** 📋 **PLANNING PHASE** - Ready for implementation  
**Research Status:** ✅ **COMPLETE** - All systems researched and consolidated

---

## 🎯 Executive Summary

This plan implements the **API server layer** connecting Router and Log-Sentinels frontend (DAC V2 IDE) to backend (Python core modules), ensuring proper integration with:
- **PLIx** (Protocol Language for Integration & Explanation)
- **AIP** (Application Integration Protocol - MCP integration)
- **NL Tags** (Natural Language Tags with Quintet Parity)
- **AIM-OS Core Systems** (CMC, VIF, SEG, HHNI, TCS, APOE)

**Key Architecture Decision:**
- **MCP is PRIMARY integration path** - Use Command Server HTTP wrapper (`POST /mcp/execute`) for AIM-OS system access
- **API Server** acts as bridge between frontend and Router/Log-Sentinels Python cores
- **PLIx Integration** - Tool execution compiles to PLIx contracts → APOE ExecutionPlans
- **NL Tags** - All endpoints tagged for quartet/quintet parity validation

---

## 🏗️ Architecture Overview

### System Architecture

```
DAC V2 IDE Frontend (React)
    ↓ HTTP Requests
API Server (FastAPI/Flask)
    ↓ Python Calls
Router/Log-Sentinels Core (Python)
    ↓ MCP Integration
Command Server (HTTP :5001)
    ↓ MCP Client
MCP Server (stdio)
    ↓ Direct Access
AIM-OS Systems (CMC, VIF, SEG, HHNI, TCS, APOE)
```

### Integration Layers

**Layer 1: Frontend → API Server**
- REST API endpoints (`/api/router/*`, `/api/log-sentinels/*`)
- SSE streaming (`/api/log-sentinels/stream`)
- WebSocket support (optional, for bidirectional communication)

**Layer 2: API Server → Router/Log-Sentinels Core**
- Python module imports
- Direct function calls to Router/Log-Sentinels classes
- Async/await for non-blocking operations

**Layer 3: Router/Log-Sentinels → AIM-OS Systems**
- MCP integration via Command Server HTTP wrapper
- PLIx contract compilation for tool execution
- NL Tags for quartet/quintet parity

---

## 📋 Implementation Plan

### Phase 1: API Server Foundation (Week 1)

**Objective:** Create FastAPI server with basic structure and MCP integration

**Tasks:**
1. **Setup FastAPI Project**
   - Create `packages/router_api_server/` directory
   - Initialize FastAPI app with CORS, middleware
   - Add dependency injection for Router/Log-Sentinels instances
   - Add error handling and logging

2. **MCP Integration Layer**
   - Create `MCPClient` class wrapping Command Server HTTP calls
   - Implement `POST /mcp/execute` wrapper
   - Add retry logic and error handling
   - Add connection pooling for performance

3. **Router Core Integration**
   - Import Router Python modules
   - Create Router service class wrapping Router.decide()
   - Integrate with MCPClient for AIM-OS system access
   - Add caching layer (RouterCache)

4. **Log-Sentinels Core Integration**
   - Import Log-Sentinels Python modules
   - Create LogSentinelsPipeline service class
   - Integrate with MCPClient for AIM-OS system access
   - Add pipeline orchestration

**Deliverables:**
- `packages/router_api_server/main.py` - FastAPI app
- `packages/router_api_server/mcp_client.py` - MCP integration
- `packages/router_api_server/services/router_service.py` - Router service
- `packages/router_api_server/services/log_sentinels_service.py` - Log-Sentinels service

**NL Tags Required:**
- `ROUTER-API-SERVER-001` - Main FastAPI app
- `ROUTER-API-MCP-001` - MCP client wrapper
- `ROUTER-API-SERVICE-001` - Router service class
- `LOG-SENTINELS-API-SERVICE-001` - Log-Sentinels service class

---

### Phase 2: Router API Endpoints (Week 1-2)

**Objective:** Implement Router API endpoints with PLIx integration

**Endpoints:**

1. **GET /api/router/tools**
   - **Input:** Query params (goal, files, errors, agent_intent)
   - **Output:** `{ tools: ToolProposal[], suggestions: ToolProposal[] }`
   - **Integration:** Router.decide() → ToolCallPlan → ToolProposal[]
   - **PLIx:** Tool proposals include PLIx tags (`plix://tool/mcp/...`)
   - **NL Tags:** `ROUTER-API-ENDPOINT-001`

2. **GET /api/router/telemetry**
   - **Input:** Query params (time_range)
   - **Output:** `RouterTelemetry` (latency, success_rate, cost, per-tool stats)
   - **Integration:** RouterCache, CMC (decision history)
   - **NL Tags:** `ROUTER-API-ENDPOINT-002`

3. **POST /api/router/execute**
   - **Input:** `{ tool: string, args: Record<string, any> }`
   - **Output:** `{ success: boolean, result: any, plan_id?: string }`
   - **Integration:** Router → PLIx contract → APOE ExecutionPlan → Tool execution
   - **PLIx:** Compile tool execution to PLIx contract → APOE plan
   - **NL Tags:** `ROUTER-API-ENDPOINT-003`

**PLIx Integration:**
- Tool proposals include PLIx tags for tool identification
- Tool execution compiles to PLIx contracts → APOE ExecutionPlans
- Tag resolution via HHNI for tool capabilities

**Deliverables:**
- `packages/router_api_server/routes/router.py` - Router endpoints
- `packages/router_api_server/schemas/router.py` - Pydantic schemas
- `packages/router_api_server/integrations/plix.py` - PLIx integration

---

### Phase 3: Log-Sentinels API Endpoints (Week 2)

**Objective:** Implement Log-Sentinels API endpoints with SSE streaming

**Endpoints:**

1. **GET /api/log-sentinels/scouts**
   - **Input:** Query params (time_range, source_filter)
   - **Output:** `{ reports: ScoutReport[] }`
   - **Integration:** LogSentinelsPipeline → ScoutAdapter → ScoutReport[]
   - **NL Tags:** `LOG-SENTINELS-API-ENDPOINT-001`

2. **GET /api/log-sentinels/forensics**
   - **Input:** Query params (time_range, severity_filter)
   - **Output:** `{ reports: ForensicsReport[] }`
   - **Integration:** LogSentinelsPipeline → ForensicsAdapter → ForensicsReport[]
   - **NL Tags:** `LOG-SENTINELS-API-ENDPOINT-002`

3. **GET /api/log-sentinels/telemetry**
   - **Input:** Query params (time_range)
   - **Output:** `LogSentinelsTelemetry` (scout_calls, forensics_calls, escalations, timeline)
   - **Integration:** CMC (decision history), TCS (timeline)
   - **NL Tags:** `LOG-SENTINELS-API-ENDPOINT-003`

4. **GET /api/log-sentinels/stream** (SSE)
   - **Input:** None (SSE connection)
   - **Output:** Real-time Scout/Forensics reports via SSE
   - **Integration:** LogSentinelsPipeline → SSE events
   - **NL Tags:** `LOG-SENTINELS-API-ENDPOINT-004`

5. **POST /api/log-sentinels/run-tool**
   - **Input:** `{ tool: string }`
   - **Output:** `{ success: boolean, result: any }`
   - **Integration:** Router → PLIx contract → APOE ExecutionPlan → Tool execution
   - **PLIx:** Compile tool execution to PLIx contract → APOE plan
   - **NL Tags:** `LOG-SENTINELS-API-ENDPOINT-005`

**Deliverables:**
- `packages/router_api_server/routes/log_sentinels.py` - Log-Sentinels endpoints
- `packages/router_api_server/schemas/log_sentinels.py` - Pydantic schemas
- `packages/router_api_server/sse/stream.py` - SSE streaming implementation

---

### Phase 4: PLIx Integration (Week 2-3)

**Objective:** Integrate PLIx contract compilation for tool execution

**Tasks:**
1. **PLIx Contract Compilation**
   - Create `PLIxCompiler` class for tool execution → PLIx contract → APOE plan
   - Integrate with Router tool execution endpoint
   - Integrate with Log-Sentinels tool execution endpoint
   - Add tag resolution via HHNI

2. **Tag Resolution**
   - Integrate HHNI for tool capability tag resolution
   - Cache resolved tags for performance
   - Handle tag resolution failures gracefully

3. **APOE Integration**
   - Convert PLIx contracts to APOE ExecutionPlans
   - Execute plans via APOE MCP tool
   - Track execution results and update Router success rates

**Deliverables:**
- `packages/router_api_server/integrations/plix_compiler.py` - PLIx compiler
- `packages/router_api_server/integrations/tag_resolver.py` - Tag resolution
- `packages/router_api_server/integrations/apoe_executor.py` - APOE executor

**NL Tags Required:**
- `ROUTER-API-PLIX-001` - PLIx compiler integration
- `ROUTER-API-TAG-RESOLVE-001` - Tag resolution via HHNI
- `ROUTER-API-APOE-001` - APOE execution integration

---

### Phase 5: NL Tags Integration (Week 3)

**Objective:** Add NL Tags to all endpoints for quartet/quintet parity

**Tasks:**
1. **Endpoint Tagging**
   - Add NL_TAG comments to all endpoint handlers
   - Add NL_TAG_CONNECT for cross-system calls
   - Add NL_TAG_INTENT for design decisions
   - Add NL_TAG_SPEC for validation schemas

2. **Quartet Parity Validation**
   - Create validation script for quartet/quintet parity
   - Run validation in CI/CD pipeline
   - Ensure P ≥ 0.90 for all changes

3. **Tag Registry Integration**
   - Register all API endpoint tags in NL Tags registry
   - Link tags to code, docs, tests, traces
   - Maintain tag dependency graph

**Deliverables:**
- NL Tags added to all endpoint handlers
- `packages/router_api_server/tags/` - Tag definitions
- `packages/router_api_server/validation/parity.py` - Parity validation

---

### Phase 6: Testing & Validation (Week 3-4)

**Objective:** Comprehensive testing and validation

**Tasks:**
1. **Unit Tests**
   - Test all API endpoints
   - Test MCP integration
   - Test PLIx compilation
   - Test tag resolution

2. **Integration Tests**
   - Test Router → APOE → Tool execution flow
   - Test Log-Sentinels → Router → Tool execution flow
   - Test SSE streaming
   - Test error handling

3. **End-to-End Tests**
   - Test frontend → API server → Router/Log-Sentinels → AIM-OS flow
   - Test real-time updates (SSE)
   - Test tool execution with PLIx contracts

**Deliverables:**
- `packages/router_api_server/tests/unit/` - Unit tests
- `packages/router_api_server/tests/integration/` - Integration tests
- `packages/router_api_server/tests/e2e/` - End-to-end tests

---

### Phase 7: Documentation & Deployment (Week 4)

**Objective:** Complete documentation and deployment

**Tasks:**
1. **API Documentation**
   - OpenAPI/Swagger documentation
   - Endpoint descriptions with examples
   - PLIx integration guide
   - NL Tags reference

2. **Deployment**
   - Docker containerization
   - Environment configuration
   - Health checks
   - Monitoring setup

**Deliverables:**
- `packages/router_api_server/docs/` - API documentation
- `packages/router_api_server/Dockerfile` - Docker container
- `packages/router_api_server/docker-compose.yml` - Deployment config

---

## 🔗 Integration Points

### Router Integration Points

**AIM-OS Systems:**
- **CMC:** Decision storage, tool weights, success rates
- **HHNI:** Semantic context retrieval, tag resolution
- **VIF:** Confidence tracking, quality gates
- **SEG:** Evidence chains, contradictions
- **TCS:** Timeline cursor, recent events
- **APOE:** Plan execution (via PLIx contracts)

**PLIx Integration:**
- Tool proposals include PLIx tags (`plix://tool/mcp/...`)
- Tool execution compiles to PLIx contracts → APOE ExecutionPlans
- Tag resolution via HHNI for tool capabilities

**NL Tags:**
- All endpoints tagged with NL_TAG, NL_TAG_CONNECT, NL_TAG_INTENT, NL_TAG_SPEC
- Quartet/quintet parity validation (P ≥ 0.90)

---

### Log-Sentinels Integration Points

**AIM-OS Systems:**
- **Router:** Tool suggestions feed into Router
- **VIF:** Quality gates, confidence tracking
- **SEG:** Evidence chains, analysis provenance
- **CMC:** Decision storage, escalation logs
- **TCS:** Timeline markers, incident tracking

**PLIx Integration:**
- Tool suggestions include PLIx tags (`plix://tool/...`)
- Analysis findings reference PLIx entity tags
- Tag resolution via HHNI for tool capabilities

**NL Tags:**
- All endpoints tagged with NL_TAG, NL_TAG_CONNECT, NL_TAG_INTENT, NL_TAG_SPEC
- Quartet/quintet parity validation (P ≥ 0.90)

---

## 📊 Success Criteria

**Phase 1-2 (API Server Foundation + Router Endpoints):**
- ✅ FastAPI server running
- ✅ MCP integration working
- ✅ Router endpoints functional
- ✅ Tool proposals include PLIx tags

**Phase 3 (Log-Sentinels Endpoints):**
- ✅ Log-Sentinels endpoints functional
- ✅ SSE streaming working
- ✅ Real-time updates delivered

**Phase 4 (PLIx Integration):**
- ✅ PLIx contract compilation working
- ✅ Tag resolution via HHNI functional
- ✅ APOE execution via PLIx contracts working

**Phase 5 (NL Tags Integration):**
- ✅ All endpoints tagged
- ✅ Quartet/quintet parity validation passing (P ≥ 0.90)

**Phase 6 (Testing):**
- ✅ Unit tests passing (≥80% coverage)
- ✅ Integration tests passing
- ✅ End-to-end tests passing

**Phase 7 (Documentation & Deployment):**
- ✅ API documentation complete
- ✅ Docker containerization complete
- ✅ Deployment successful

---

## 🚨 Risk Mitigation

**Risk 1: MCP Integration Complexity**
- **Mitigation:** Use Command Server HTTP wrapper (simpler than direct MCP)
- **Fallback:** Direct Python imports if MCP unavailable

**Risk 2: PLIx Compilation Errors**
- **Mitigation:** Comprehensive error handling, fallback to direct APOE plans
- **Validation:** PLIx contract validation before compilation

**Risk 3: Performance Issues**
- **Mitigation:** Caching layer (RouterCache), async/await for non-blocking
- **Monitoring:** Performance metrics, latency tracking

**Risk 4: NL Tags Parity Failures**
- **Mitigation:** Automated validation in CI/CD, pre-commit hooks
- **Process:** Tag review before merge

---

## 📝 Next Steps

1. **Review Plan** - Get approval for implementation approach
2. **Start Phase 1** - Create API server foundation
3. **Iterate** - Build incrementally, test continuously
4. **Integrate** - Connect with frontend, validate end-to-end
5. **Deploy** - Production deployment with monitoring

---

**Status:** ✅ **PLAN COMPLETE** - Ready for implementation  
**Research:** ✅ **COMPLETE** - All systems researched and consolidated  
**Next Action:** Begin Phase 1 implementation

