# Router & Log-Sentinels API Server Integration - Research Journal

**Date:** 2025-01-27  
**Purpose:** Deep research and consolidation before planning API server integration  
**Status:** 🔬 **RESEARCH PHASE** - Consolidating understanding of all systems

---

## 🎯 Research Objective

Plan and implement API server layer connecting Router and Log-Sentinels frontend (DAC V2 IDE) to backend (Python core modules), ensuring proper integration with:
- **PLIx** (Protocol Language for Integration & Explanation)
- **AIP** (Application Integration Protocol)
- **NL Tags** (Natural Language Tags with Quintet Parity)
- **Recent AIM-OS enhancements** (ICIP, CCS, etc.)

---

## 📚 System Research Findings

### 1. PLIx (Protocol Language for Integration & Explanation)

**What It Is:**
- Typed, tag-centric protocol language for expressing deterministic intent
- Enables AI consciousness through intent contracts
- Integrates with AIM-OS via AIP (Application Integration Protocol)

**Key Features:**
- **Tag System:** Format `plix://namespace/path#rev@hash`
  - Example: `plix://room/meeting_room` (entity tag)
  - Example: `plix://tool/mcp/pg.migrate` (tool capability tag)
- **Intent Contracts:** Pre/postconditions, entity references, constraints
- **APOE Integration:** PLIx compiles to APOE ExecutionPlans
  - Uses tag-based entity references
  - Verifies intent achievement for specific entities via tags
  - Collects intent evidence with tag-based entity tracking
- **AIP Integration:** PLIx compiles to AIP graph structures
  - PLIx tags map to AIP nodes and edges
  - PLIx contracts map to AIP validation rules

**Integration Points:**
- **CMC:** Tag persistence, intent-aware memory
- **VIF:** Intent verification, witness generation
- **APOE:** Intent achievement, execution planning (Router uses APOE)
- **SEG:** Intent lineage, evidence tracking
- **HHNI:** Tag resolution, semantic search (Router uses HHNI)

**Relevance to Router/Log-Sentinels:**
- Router tool proposals could use PLIx tags for tool identification
- Router tool execution could compile to PLIx contracts → APOE plans
- Log-Sentinels tool suggestions could reference PLIx tool tags
- Both systems should support PLIx tag resolution via HHNI

---

### 2. AIP (Application Integration Protocol)

**What It Is:**
- **AIM-OS Application Integration Protocol** - comprehensive standard for app integration
- Defines three layers: Declaration (aimos.json manifest), Registration (CMC atom creation), Runtime (AIM-OS services)
- **MCP is PRIMARY integration path:** App → Command Server (HTTP :5001) → MCP Client → MCP Server → AIM-OS Systems
- PLIx contracts wrap MCP calls for intent purity

**Key Architecture:**
```
App (HTTP) → Command Server :5001 → MCP Client → MCP Server (stdio) → AIM-OS Systems
```

**Integration Points:**
- **81 MCP tools available** via Command Server HTTP wrapper (`POST /mcp/execute`)
- **PLIx Integration:** PLIx contracts compile to APOE ExecutionPlans
- **SCOR Security:** Behavioral validation (invariants, baselines, social signals)
- **CMC Storage:** All app operations create CMC atoms
- **VIF Provenance:** All decisions create VIF witnesses

**Relevance to Router/Log-Sentinels:**
- **Router/Log-Sentinels API Server should use MCP integration (PRIMARY path)**
- Use Command Server HTTP wrapper (`POST /mcp/execute`) for AIM-OS system access
- Support PLIx contracts for tool execution (compile to APOE ExecutionPlans)
- Integrate with AIP protocol for app registration and service discovery
- Use SCOR for security validation

**Status:** ✅ **RESEARCH COMPLETE**
- AIP specification found: `knowledge_architecture/systems/lucid-ide/backend-api-system/AIMOS_APP_INTEGRATION_PROTOCOL_CONSOLIDATED.md`
- MCP integration is PRIMARY path (not REST API)
- Command Server HTTP wrapper available at `http://localhost:5001/mcp/execute`

---

### 3. NL Tags (Natural Language Tags)

**What It Is:**
- Natural Language code tags ensuring accuracy through structured format
- Four tag types: NL_TAG, NL_TAG_CONNECT, NL_TAG_INTENT, NL_TAG_SPEC
- Quintet Parity: Code, Docs, Tests, Traces, NL Tags (P ≥ 0.90)

**Key Features:**
- **Structured Format:** `# NL_TAG: SYSTEM-CATEGORY-NNN | description | function_sig(...) -> ReturnType | [dep_ids]`
- **Cross-System Propagation:** Tags appear in code, docs, tests, traces, indexes
- **Dependency Tracking:** Map all connections, detect broken links
- **Change Propagation:** Update one tag, all instances update automatically

**Integration Points:**
- **CMC:** Tag storage and persistence
- **HHNI:** Tag-based semantic search
- **SDF-CVF:** Quintet parity validation
- **VIF:** Tag-based provenance tracking

**Relevance to Router/Log-Sentinels:**
- Router tool proposals should include NL tags for tools
- Log-Sentinels analysis should tag findings with NL tags
- API server endpoints should be tagged with NL tags
- All code changes require quartet/quintet parity validation

---

### 4. Router System Architecture

**Core Components:**
- **Router:** Main orchestration class (decide, update_success_rate, learn_from_outcome)
- **ScoutLLM:** Fast LLM (Cerebras) for tool proposals
- **BanditScorer:** Learned policy for tool ranking
- **RulesEngine:** Hard gates (safety, budget, preconditions)
- **ToolManifest:** Tool capability definitions
- **SnapshotBuilder:** System state aggregation
- **RouterCache:** Caching layer (context, tool proposals, embeddings)

**Integration Points:**
- **CMC:** Decision storage, tool weights, success rates
- **HHNI:** Semantic context retrieval
- **VIF:** Confidence tracking, quality gates
- **SEG:** Evidence chains, contradictions
- **TCS:** Timeline cursor, recent events
- **APOE:** Plan execution (Router proposes tools → APOE executes)

**Current State:**
- ✅ Python core modules implemented
- ✅ Integration stubs exist (CMC, HHNI, VIF, SEG, TCS, APOE)
- ❌ No HTTP API server layer
- ❌ No connection to frontend (DAC V2 IDE)

---

### 5. Log-Sentinels System Architecture

**Core Components:**
- **LogSentinelsPipeline:** Main orchestration pipeline
- **LogCollector:** Log collection from sources (browser, terminal, backend API)
- **LogNormalizer:** PII/secret redaction before cloud calls
- **LogTemplateMiner:** Drain3 algorithm for log pattern extraction
- **Windower:** Time-windowed log analysis
- **ScoutAdapter:** Fast cloud analysis (Cerebras)
- **ForensicsAdapter:** Deep local analysis (Ollama)
- **RouterPolicy:** Escalation decision logic

**Integration Points:**
- **Router:** Tool suggestions feed into Router
- **VIF:** Quality gates, confidence tracking
- **SEG:** Evidence chains, analysis provenance
- **CMC:** Decision storage, escalation logs
- **TCS:** Timeline markers, incident tracking

**Current State:**
- ✅ Python core modules implemented
- ✅ Integration stubs exist (Router, VIF, SEG, CMC, TCS)
- ❌ No HTTP API server layer
- ❌ No connection to frontend (DAC V2 IDE)

---

### 6. DAC V2 IDE Frontend

**Current State:**
- ✅ React components implemented (RouterPanel, LogSentinelsSummaries, LogSentinelsAnomalies, ToolQualityDashboard, LogAnalysisDashboard)
- ✅ React hooks implemented (useRouter, useLogSentinels)
- ✅ UI integration complete (IDELayout.tsx with toolbar buttons)
- ✅ Adjustable panel layout (drag-and-drop, resizable)
- ❌ API calls fail (404s) - endpoints don't exist

**API Endpoints Expected:**
- Router: `/api/router/tools`, `/api/router/telemetry`, `/api/router/execute`
- Log-Sentinels: `/api/log-sentinels/scouts`, `/api/log-sentinels/forensics`, `/api/log-sentinels/telemetry`, `/api/log-sentinels/stream`, `/api/log-sentinels/run-tool`

---

### 7. Recent AIM-OS Enhancements

**ICIP (Code Property Graph):**
- Technical foundation for codebase intelligence
- CPG → CMC Atoms integration
- Multi-language parsing → HHNI indexing
- Real-time processing → TCS timeline

**CCS (Consciousness Coordination System):**
- 9th APOE role: Organizer AI
- Multi-dimensional retrieval scoring (7 weight dimensions)
- Background orchestration
- Multi-AI coordination

**Relevance:**
- Router could leverage ICIP CPG for code-aware tool selection
- Log-Sentinels could analyze ICIP CPG events
- CCS could coordinate Router and Log-Sentinels operations

---

## 🔗 Integration Requirements

### Router API Server Requirements

**Endpoints:**
1. `GET /api/router/tools` - Fetch tool proposals
   - Input: Current context (goal, files, errors, agent intent)
   - Output: Tool proposals with probabilities, rationales, preconditions
   - Integration: Router.decide() → ToolCallPlan → ToolProposal[]

2. `GET /api/router/telemetry` - Fetch Router telemetry
   - Input: None (or time range)
   - Output: Latency, success rate, cost metrics, per-tool stats
   - Integration: RouterCache, CMC (decision history)

3. `POST /api/router/execute` - Execute tool
   - Input: Tool name, arguments
   - Output: Execution result
   - Integration: Router → APOE (plan execution) → Tool execution

**PLIx Integration:**
- Tool proposals should include PLIx tags (`plix://tool/mcp/...`)
- Tool execution should compile to PLIx contracts → APOE plans
- Tag resolution via HHNI for tool capabilities

**NL Tags Integration:**
- All API endpoints must be tagged with NL tags
- Tool proposals should include NL tags for tools
- Changes require quartet/quintet parity validation

---

### Log-Sentinels API Server Requirements

**Endpoints:**
1. `GET /api/log-sentinels/scouts` - Fetch Scout reports
   - Input: Time range, source filter
   - Output: ScoutReport[] (summary, confidence, severity, tags, suggested_tools)
   - Integration: LogSentinelsPipeline → ScoutAdapter → ScoutReport[]

2. `GET /api/log-sentinels/forensics` - Fetch Forensics reports
   - Input: Time range, severity filter
   - Output: ForensicsReport[] (root_cause, fix_suggestion, evidence, gate)
   - Integration: LogSentinelsPipeline → ForensicsAdapter → ForensicsReport[]

3. `GET /api/log-sentinels/telemetry` - Fetch Log-Sentinels telemetry
   - Input: Time range
   - Output: Scout calls, Forensics calls, escalations, tool suggestions, timeline
   - Integration: CMC (decision history), TCS (timeline)

4. `GET /api/log-sentinels/stream` - SSE stream for real-time updates
   - Input: None (SSE connection)
   - Output: Real-time Scout/Forensics reports
   - Integration: LogSentinelsPipeline → SSE events

5. `POST /api/log-sentinels/run-tool` - Run suggested tool
   - Input: Tool name
   - Output: Execution result
   - Integration: Router → APOE (plan execution) → Tool execution

**PLIx Integration:**
- Tool suggestions should include PLIx tags (`plix://tool/...`)
- Analysis findings should reference PLIx entity tags
- Tag resolution via HHNI for tool capabilities

**NL Tags Integration:**
- All API endpoints must be tagged with NL tags
- Analysis reports should include NL tags
- Changes require quartet/quintet parity validation

---

## 🚨 Critical Questions

### 1. AIP Protocol
- **Q:** What is AIP exactly? Is it a protocol, a format, or both?
- **A:** ⚠️ NEEDS RESEARCH - Mentioned in PLIx spec but not fully documented
- **Action:** Search for AIP documentation/specification

### 2. API Server Architecture
- **Q:** Should API server use AIP protocol or standard REST/WebSocket?
- **A:** ⚠️ NEEDS DECISION - Depends on AIP specification
- **Action:** Research AIP, then decide architecture

### 3. PLIx Integration Depth
- **Q:** How deeply should Router/Log-Sentinels integrate with PLIx?
- **A:** ⚠️ NEEDS DECISION - Tag-based tool references? Contract compilation?
- **Action:** Review PLIx integration requirements, decide integration depth

### 4. NL Tags Enforcement
- **Q:** Should API server enforce NL tags on all endpoints?
- **A:** ⚠️ NEEDS DECISION - Protocol requirement or optional?
- **Action:** Review NL Tags protocol, decide enforcement level

### 5. Real-Time Updates
- **Q:** SSE vs WebSocket for real-time updates?
- **A:** ⚠️ NEEDS DECISION - SSE simpler, WebSocket more flexible
- **Action:** Review requirements, decide protocol

---

## 📋 Next Steps

### Phase 1: Complete Research
1. ✅ Research PLIx system (COMPLETE)
2. ⚠️ Research AIP protocol (IN PROGRESS - needs more investigation)
3. ✅ Research NL Tags system (COMPLETE)
4. ✅ Research Router architecture (COMPLETE)
5. ✅ Research Log-Sentinels architecture (COMPLETE)
6. ✅ Research DAC V2 IDE frontend (COMPLETE)
7. ⚠️ Research recent AIM-OS enhancements (PARTIAL - ICIP, CCS found)

### Phase 2: Consolidation
1. Document all integration points
2. Resolve critical questions
3. Create integration architecture diagram
4. Define API contract specifications

### Phase 3: Planning
1. Create detailed implementation plan
2. Define API server architecture
3. Plan PLIx/AIP integration
4. Plan NL Tags integration
5. Plan testing strategy

### Phase 4: Implementation
1. Implement API server layer
2. Integrate with Router/Log-Sentinels core
3. Integrate with PLIx/AIP (if applicable)
4. Add NL Tags to all endpoints
5. Test integration
6. Deploy

---

## 📝 Research Notes

### PLIx Tag Format
```
plix://{namespace}/{path}#rev@{hash}
```

**Examples:**
- `plix://room/meeting_room` - Entity tag
- `plix://tool/mcp/pg.migrate` - Tool capability tag
- `plix://witness/schema_before` - Evidence witness tag

**Tag Resolution:**
- Multi-source resolution: Registry/HHNI/SEG/CMC
- Tag resolution cache in Router/Log-Sentinels
- Resolved entities/capabilities used for execution

### NL Tags Format
```
# NL_TAG: SYSTEM-CATEGORY-NNN | description | function_sig(...) -> ReturnType | [dep_ids]
# NL_TAG_CONNECT: SYSTEM-CONNECT-NNN | integration_desc | source → target | [source_tag, target_tag]
# NL_TAG_INTENT: SYSTEM-DESIGN-NNN | design_rationale | architectural_concept | [ADR_reference]
# NL_TAG_SPEC: SYSTEM-SPEC-NNN | validation_desc | validator_function | [schema_file]
```

**Router NL Tags:**
- `ROUTER-DECIDE-001` - Main decision method
- `ROUTER-SCOUT-001` - Scout LLM tool proposals
- `ROUTER-BANDIT-001` - Bandit scoring layer
- `ROUTER-APOE-001` - APOE integration

**Log-Sentinels NL Tags:**
- `LOG-SENTINELS-PIPELINE-001` - Main pipeline orchestration
- `LOG-SENTINELS-SCOUT-001` - Scout cloud analysis
- `LOG-SENTINELS-FORENSICS-001` - Forensics local analysis
- `LOG-SENTINELS-ROUTER-001` - Router integration

---

## 🎯 Research Status

**Status:** ✅ **RESEARCH COMPLETE** - Ready for planning phase

**Completed:**
- ✅ PLIx system research (COMPLETE)
- ✅ AIP protocol research (COMPLETE - MCP is PRIMARY path)
- ✅ NL Tags system research (COMPLETE)
- ✅ Router architecture research (COMPLETE)
- ✅ Log-Sentinels architecture research (COMPLETE)
- ✅ DAC V2 IDE frontend research (COMPLETE)
- ✅ Recent AIM-OS enhancements research (ICIP, CCS, AIP found)

**Key Findings:**
1. **MCP is PRIMARY integration path** - Use Command Server HTTP wrapper (`POST /mcp/execute`)
2. **PLIx integration** - Tool execution should compile to PLIx contracts → APOE ExecutionPlans
3. **AIP protocol** - Router/Log-Sentinels should register as AIM-OS apps
4. **NL Tags** - All endpoints must be tagged for quartet/quintet parity

**Critical Questions Resolved:**
1. ✅ **AIP Protocol:** MCP integration via Command Server HTTP wrapper (`POST /mcp/execute`)
2. ✅ **API Server Architecture:** Use FastAPI/Flask with MCP integration (not standalone REST)
3. ✅ **PLIx Integration Depth:** Tag-based tool references + contract compilation for execution
4. ✅ **NL Tags Enforcement:** Required for all endpoints (quartet/quintet parity protocol)
5. ✅ **Real-Time Updates:** SSE for Log-Sentinels streaming (simpler than WebSocket)

**Next Action:** ✅ **COMPLETE** - Implementation plan created and all 7 phases executed successfully.

---

## ✅ Implementation Status

**Status:** ✅ **ALL PHASES COMPLETE** - Production Ready

**Completed Phases:**
1. ✅ Phase 1: API Server Foundation
2. ✅ Phase 2: Router API Endpoints
3. ✅ Phase 3: Log-Sentinels API Endpoints
4. ✅ Phase 4: PLIx Integration
5. ✅ Phase 5: NL Tags
6. ✅ Phase 6: Testing & Validation
7. ✅ Phase 7: Documentation & Deployment

**Implementation Location:** `packages/router_api_server/`

**Key Deliverables:**
- FastAPI application with 8 API endpoints
- MCP client wrapper for AIM-OS integration
- PLIx compiler and APOE executor
- Comprehensive test suite (≥80% coverage)
- Complete documentation and Docker configuration

**Production Status:** ✅ Ready for deployment

