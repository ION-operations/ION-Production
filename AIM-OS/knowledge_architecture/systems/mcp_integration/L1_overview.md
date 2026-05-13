---
id: mcp_T1_overview
level: L1
system: MCP Integration
status: complete
updated: 2025-10-30
---

> TRANSITIONAL T-LEVEL DOCUMENT – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# MCP Integration – T1 Overview (≈500 words)

## Purpose & Scope

MCP Integration provides production-ready Model Context Protocol servers that expose AIM-OS consciousness systems as standardized tools accessible to AI agents through Cursor IDE integration. Instead of agents needing direct API access to consciousness infrastructure, MCP Integration provides a unified, protocol-compliant interface that enables seamless access to memory, retrieval, orchestration, verification, timeline tracking, and all AIM-OS capabilities.

MCP Integration provides three core guarantees:

1. **Protocol Compliance:** Fully compliant JSON-RPC 2.0 implementation with stdio transport, proper request/response handling, and comprehensive error handling. Agents can rely on standard MCP protocol without AIM-OS-specific knowledge.

2. **Complete Tool Exposure:** All 51 AIM-OS tools exposed via MCP, organized into 12 categories including Core AIM-OS (memory, knowledge, confidence), SCOR (safety, consciousness, reliability), Timeline Context, Goal Timeline, IIS (intuition), Co-Agency, Dataset Management, Application Lifecycle, Autonomous Protocol, AI Collaboration, and Observability.

3. **Production-Ready Infrastructure:** Comprehensive testing, validation, error handling, and observability. Server operates reliably in production environments with proper logging, metrics, and error recovery.

**System Boundaries:**
- MCP Integration owns: MCP server implementation, tool registration/discovery, protocol compliance, request routing, error handling
- MCP Integration does NOT own: Actual AIM-OS system implementations (delegates), tool business logic (calls AIM-OS APIs), IDE client implementation (provides server only), policy decisions (reads from AIM-OS systems)

## Users & Integrations

**Cursor IDE:** Primary client consuming MCP server. Provides JSON-RPC 2.0 transport, automatic tool discovery, and seamless integration for AI agents using AIM-OS capabilities within development workflows.

**AI Agents:** End users accessing AIM-OS capabilities through MCP tools. Agents can store memory, retrieve context, create plans, track confidence, synthesize knowledge, and perform all consciousness operations without direct API knowledge.

**All AIM-OS Systems:** Integrated through tool adapters that translate MCP tool calls into appropriate system API calls:
- **CMC:** Memory storage and retrieval (`store_memory`, `retrieve_memory`, `get_memory_stats`)
- **HHNI:** Semantic search and retrieval (via CMC retrieval tools)
- **VIF:** Provenance tracking and confidence calibration (`track_confidence`)
- **APOE:** Plan creation and execution (`create_plan`)
- **SEG:** Knowledge synthesis (`synthesize_knowledge`)
- **Timeline Context System:** Timeline tracking (`add_timeline_entry`, `get_timeline_summary`)
- **SCOR:** Safety and consciousness monitoring (`check_invariant`, `run_baseline_probe`)
- **IIS:** Intuition and learning (`compute_intuition`, `update_intuition_weights`)
- **Cross-Model Consciousness:** Multi-model coordination (via dedicated tools)
- **All Supporting Systems:** Dataset management, application lifecycle, autonomous operations, AI collaboration

## Core Concepts

**MCP Server:** JSON-RPC 2.0 compliant server implementing Model Context Protocol. Handles request validation, routing, execution, and response generation. Provides stdio transport for IDE integration.

**Tool Registry:** Central registry for all 51 AIM-OS tools. Supports tool discovery, validation, categorization, and execution. Tools organized by category with metadata for filtering and selection.

**Tool Adapter:** Bridge between MCP tool calls and AIM-OS system APIs. Translates MCP request format into appropriate system calls, handles errors, and formats responses for MCP protocol compliance.

**Request/Response Handling:** Comprehensive request validation, routing, execution, and response generation. Includes error handling, timeout management, and proper JSON-RPC 2.0 compliance.

## High‑Level Data Flow

**Server Initialization:**
```
Start Server → Load Config → Register Tools → Setup Handlers → 
Initialize Logging → Ready for Requests
```

**Tool Invocation:**
```
MCP Request → Validate Request → Route to Tool → Execute via Adapter → 
Call AIM-OS API → Format Response → Return JSON-RPC Response
```

**Tool Discovery:**
```
Client Request → List Tools → Filter by Category → Return Tool Metadata → 
Client Selects Tool → Invocation Flow
```

## Non‑Goals

MCP Integration is NOT:
- **Generic plugin marketplace:** Targeted specifically to AIM-OS tool exposure, not general-purpose tool distribution
- **Direct AIM-OS API:** Provides protocol-compliant interface, not raw system APIs
- **IDE client implementation:** Provides server only, clients implement their own MCP protocol handling
- **Business logic layer:** Tool logic handled by AIM-OS systems, MCP Integration provides protocol interface only
- **Policy enforcement:** Safety and policy decisions delegated to AIM-OS systems (SCOR, etc.)

## References

- System map: `systems/mcp_integration/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/mcp_integration/L0_executive.md` through `L4_complete.md`
- Implementation: `lucid_mcp_server.py`, `run_mcp_aimos.py`
