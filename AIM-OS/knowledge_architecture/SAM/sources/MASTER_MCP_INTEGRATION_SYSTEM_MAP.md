# MASTER MCP INTEGRATION SYSTEM MAP

**Date:** 2026-02-22  
**System:** MCP server, RAG daemon, cursor-addon, tool surface  
**Implementation:** lucid_mcp_server.py, daemon_rag_system/, packages/mcp_rag_proxy/, cursor-addon/

---

**[TAG:SAM] [TAG:MASTER] [TAG:MCP]**

## 1. SYSTEM OVERVIEW

**[TAG:OVERVIEW] [TAG:MCP]**

MCP Integration exposes AIM-OS systems as standardized Model Context Protocol tools. Enables AI agents (e.g., in Cursor IDE) to access memory, retrieval, orchestration, verification, timeline, goals without direct API knowledge. Tool surface: run `python scripts/check_mcp_tool_parity.py` for current count. Daemon/RAG: context-aware tool selection, RAG filtering, learning system. Cursor IDE limit ~80 tools; RAG middleware selects relevant subset.

**[END:TAG:OVERVIEW]**

---

## 2. STATIC STRUCTURE MAP

**[TAG:STRUCTURE] [TAG:MCP]**

### MCP Server (lucid_mcp_server.py)

- **Tool Registry:** Registers and manages all MCP tools
- **Tool Executor:** Executes tools, manages lifecycle
- **Tool Selector:** Selects tools based on context
- **Tool Monitor:** Monitors performance and health

### Daemon/RAG (daemon_rag_system)

- **toolRegistry:** Central registry; categorization, capability mapping
- **contextAnalysisEngine:** Analyzes user input, environment, task requirements
- **toolSelectionEngine:** Selects optimal subset (within Cursor limit)
- **ragSystem:** RAG-enhanced tool selection
- **serverManager:** Dynamic MCP server instances, tool loading
- **learningSystem:** Improves selection from usage patterns

### Tool Categories (from audit)

Core AIM-OS, SCOR, Snapshots, Timeline, Goal Timeline, IIS, Co-Agency, Dataset, Application, Autonomous, ARD, CAS, NL Tags, Cursor Integration, Cursor Commands, AI Collaboration, Prompt Chains, Observability, HHNI, API Integration.

**[END:TAG:STRUCTURE]**

---

## 3. DYNAMIC BEHAVIOR MAP

**[TAG:BEHAVIOR] [TAG:MCP]**

### Request Flow

User/Agent -> Context analysis -> Tool selection (RAG-enhanced) -> Execute via lucid_mcp_server -> Result -> Learning update

### Server Lifecycle

Start -> Load tools -> Register -> Serve JSON-RPC 2.0 over stdio -> Monitor -> Shutdown

**[END:TAG:BEHAVIOR]**

---

## 4. INTERFACE & INTEGRATION MAP

**[TAG:INTEGRATION] [TAG:MCP]**

### MCP Server Integrates With

All AIM-OS systems (CMC, HHNI, VIF, SEG, APOE, TCS, SDF-CVF, CAS, SCOR, IIS) via tool handlers.

### Daemon Integrates With

- **lucid_mcp_server:** Tool execution
- **packages/mcp_rag_proxy:** Embedding, learning layers
- **cursor-addon:** Command Server (port 5001), Cursor API

### Cursor-addon

Command Server, bulletproof messaging, agent automation, MCP client. See cursor-addon/MASTER_INDEX_AND_SYSTEM_MAP.md.

**[END:TAG:INTEGRATION]**

---

## 5. CONSTRAINTS & LIMITATIONS

**[TAG:PERFORMANCE] [TAG:DEPENDENCY] [TAG:MCP]**

- **Cursor IDE limit:** ~80 tools visible; RAG filters to relevant subset
- **Tool parity:** Run check_mcp_tool_parity.py for listed/callable totals
- **Known issues:** CAS (2 tools), NL tags (4 tools), get_timeline_summary — workarounds in base rules

**[END:TAG:PERFORMANCE] [END:TAG:DEPENDENCY]**

---

## 6. EVIDENCE & VALIDATION

**[TAG:SUMMARY] [TAG:MCP]**

- **lucid_mcp_server:** ~10,600 LOC
- **Audit (2026-02-19):** parity_ok: true
- **Tool count:** See scripts/check_mcp_tool_parity.py
- **Daemon:** daemon_rag_system/ (~12K LOC per Living System Map)

**[END:TAG:SUMMARY]**

---

## 7. RELATIONSHIP MATRIX

**[TAG:RELATIONSHIP] [TAG:MCP]**

| To System | Relationship |
|-----------|--------------|
| CMC | store_memory, retrieve_memory, create_snapshot, etc. |
| HHNI | Indexing, retrieval |
| VIF | track_confidence |
| APOE | create_plan, update_goal_progress |
| TCS | add_timeline_entry, get_timeline_entries |
| SEG | synthesize_knowledge |
| SDF-CVF | check_invariant |
| CAS | detect_cognitive_drift |
| SCOR | check_invariant, run_baseline_probe, detect_manipulation_signals |

**[END:TAG:RELATIONSHIP]**
