---
ion_id: docs/aether-os/mcp-bridge-spec
type: spec
authority: A3_OPERATIONAL
confidence: 0.80
epistemic_status: DERIVED
owner: opus
created: 2026-03-23T17:30:00-04:00
depends_on:
  - docs/aether-os/system-universe-map
  - docs/aether-os/ion-engine-spec
bonds:
  - target: docs/aether-os/aether-constitution
    type: governed_by
  - target: lucid_mcp_server.py
    type: describes
tags: [mcp, bridge, integration, track-q, transport]
---

# MCP ↔ ION Bridge Specification

> **Purpose:** Define the architecture for bridging the MCP (Model Context Protocol) infrastructure with the ION engine. The existing MCP server has 84+ tools and is the primary interface between AI agents and AIM-OS. This bridge makes ION operations available as MCP tools and routes MCP mutations through ION's governed write.
>
> **Epistemic Status:** DERIVED from observed MCP server structure and ION Track Q.01 specification.
>
> **Scale Context:** The Lucid MCP Server (`lucid_mcp_server.py`) is 570,952 bytes — the single largest file in the codebase. It exposes 84+ tools via JSON-RPC stdio protocol.

---

## §1. Current MCP Architecture

### 1.1 MCP Server Landscape

| Server | Path | Lines | Transport | Status |
|--------|------|-------|-----------|--------|
| **Lucid MCP (main)** | `lucid_mcp_server.py` | ~15,000+ | stdio (JSON-RPC) | ACTIVE — used by IDE agents |
| **HTTP Fallback** | `scripts/mcp_http_fallback_server.py` | ~1,000 | HTTP :5001 | ACTIVE — backup when stdio fails |
| **MCP Server (legacy)** | `packages/mcp_server/` | 674 | FastAPI :8000 | LEGACY |
| **AI Engine MCP** | `scripts/ai_engine/ai_engine_mcp_server.py` | 1,519 | stdio | ACTIVE — 29 tools for AI Engine |
| **MCP RAG Proxy** | `packages/mcp_rag_proxy/` | 3,562 | — | Context-aware tool selection |
| **MCP Data Integration** | `packages/mcp_data_integration/` | 7,929 | — | AETHER_MEMORY integration |

### 1.2 Current Tool Categories (84+ tools in Lucid MCP)

| Category | Example Tools | Count (est) |
|----------|--------------|-------------|
| Memory | `store_memory`, `retrieve_memory`, `search_memories` | ~8 |
| Timeline | `add_timeline_entry`, `get_timeline_summary` | ~5 |
| AI Messages | `send_ai_message`, `get_ai_messages` | ~4 |
| Context | `record_context_capsule`, `get_capsule_history` | ~5 |
| File Operations | `read_file`, `write_file`, `list_directory` | ~10 |
| System | `health_check`, `get_system_status` | ~5 |
| Agent | `list_agents`, `get_agent_status` | ~5 |
| HHNI | `hhni_query`, `hhni_index` | ~5 |
| CMC | `cmc_store`, `cmc_query` | ~5 |
| VIF | `vif_verify`, `vif_witness` | ~5 |
| Analysis | `analyze_codebase`, `search_code` | ~10 |
| Cursor | `cursor_commands` tools | ~5 |
| Misc | Various utility tools | ~12 |

### 1.3 Current MCP Memory

MCP state is stored in:
- `mcp_memory/` — key-value memory files
- `mcp_ai_messages.json` — inter-agent messages
- `mcp_timeline_entries.json` — timeline events

These are **NOT ions.** They're flat JSON/file stores with no frontmatter, no bonds, no authority classes.

---

## §2. The Bridge Architecture

### 2.1 Two-Direction Bridge

The MCP-ION bridge operates in two directions:

**Direction 1: MCP → ION (Inbound)**
External agents call MCP tools → MCP bridge translates to ION operations → ION governed write enforces rules → results returned via MCP.

**Direction 2: ION → MCP (Outbound)**
ION automation ions trigger → MCP bridge translates to MCP tool calls → external systems updated.

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  IDE Agent   │────▶│   MCP-ION        │────▶│  ION Engine     │
│  (Antigrav,  │     │   BRIDGE         │     │  (Governed      │
│   Cursor,    │◀────│                  │◀────│   Write)        │
│   Gemini)    │     │  ion_create      │     │                 │
│              │     │  ion_read        │     │  store.py       │
│              │     │  ion_query       │     │  governed_write │
│              │     │  ion_bond        │     │  graph.py       │
│              │     │  ion_navigate    │     │  navigator.py   │
└──────────────┘     └──────────────────┘     └─────────────────┘
```

### 2.2 New MCP Tools (ION-Native)

The bridge exposes ION operations as MCP tools. These REPLACE the current memory/timeline tools with ion-native equivalents:

**Ion CRUD Tools:**

| MCP Tool | ION Operation | Description |
|----------|--------------|-------------|
| `ion_create` | `governed_write.create()` | Create new ion (goes through 10-stage pipeline) |
| `ion_read` | `store.read()` | Read ion by ID |
| `ion_update` | `governed_write.update()` | Update ion (governed) |
| `ion_delete` | `governed_write.delete()` | Delete ion (governed, authority check) |
| `ion_list` | `index.query()` | List ions by type/authority/owner/tags |
| `ion_search` | `hhni.retrieve()` | Relevance search with budget |

**Ion Graph Tools:**

| MCP Tool | ION Operation | Description |
|----------|--------------|-------------|
| `ion_bond` | `graph.add_bond()` | Create bond between ions |
| `ion_unbond` | `graph.remove_bond()` | Remove bond |
| `ion_impact` | `graph.impact_analysis()` | Show blast radius of changing an ion |
| `ion_path` | `graph.find_path()` | Find shortest path between ions |
| `ion_dependencies` | `graph.get_dependencies()` | List ion dependencies |
| `ion_dependents` | `graph.get_dependents()` | List ions that depend on this one |

**Ion Cognitive Tools:**

| MCP Tool | ION Operation | Description |
|----------|--------------|-------------|
| `ion_navigate` | `navigator.navigate()` | Execute cognitive loop on a query |
| `ion_contextualize` | `navigator.contextualize()` | Load context from manifest |
| `ion_reflect` | `navigator.reflect()` | Analyze gaps and confidence |
| `ion_manifest` | `manifest.read()` | Read current manifest state |
| `ion_capsule_pre` | `capsule.write_pre()` | Write PRE session capsule |
| `ion_capsule_post` | `capsule.write_post()` | Write POST session capsule |

**Ion Governance Tools:**

| MCP Tool | ION Operation | Description |
|----------|--------------|-------------|
| `ion_health` | `health.check()` | System health metrics |
| `ion_invariants` | `invariants.check_all()` | Check all constitutional invariants |
| `ion_audit` | `audit.recent()` | Recent audit trail |
| `ion_confidence` | `confidence.report()` | Confidence distribution report |

### 2.3 Migration of Existing MCP State

Current MCP state must migrate to ION format:

| Current | Migration Target | Method |
|---------|-----------------|--------|
| `mcp_memory/` files | `.ion/memory/mcp/` ions | Convert each memory file to memory ion with frontmatter |
| `mcp_ai_messages.json` | `.ion/comms/` ions | Each message becomes a comms ion |
| `mcp_timeline_entries.json` | `.ion/timeline/` ions | Each entry becomes a timeline ion |
| `mcp_memory/context_capsules/` | `.ion/capsules/` ions | Direct conversion to capsule ions |

Migration script:
```python
def migrate_mcp_to_ion(mcp_memory_dir, ion_store):
    """Migrate existing MCP memory to ION filesystem."""
    for memory_file in Path(mcp_memory_dir).glob("*.json"):
        data = json.loads(memory_file.read_text())
        ion = create_memory_ion(
            ion_id=f"memory/mcp/{memory_file.stem}",
            title=data.get("key", memory_file.stem),
            content=data.get("value", ""),
            authority=AuthorityClass.A5_PERSONAL,
            owner="opus",
        )
        ion_store.create(ion, body=data.get("value", ""))
```

---

## §3. Protocol Compliance

### 3.1 MCP ↔ A2 Schema Mapping

Every MCP tool call that modifies state generates A2-compliant records:

| MCP Action | A2 Schema | When |
|-----------|-----------|------|
| `ion_create` | `task_intake/v1` (Schema 3) | On request |
| `ion_create` success | `revision_receipt/v1` (Schema 15) | On completion |
| `ion_update` | `mutation_request/v1` (Schema 13) | On request |
| `ion_update` fail | `escalation_notice/v1` (Schema 20) | On governed write rejection |
| `ion_capsule_pre` | `capsule/v1` (Schema 1) | On session start |
| `ion_capsule_post` | `capsule/v1` (Schema 1) | On session end |
| `ion_navigate` | `execution_class/v1` (Schema 12) | On cognitive loop start |
| Any tool failure | `audit_receipt/v1` (Schema 9) | On error |

### 3.2 Authority Enforcement via MCP

Every MCP tool call carries the agent's identity. The bridge checks authority:

```python
def ion_create(agent_id: str, ion_data: dict) -> dict:
    # 1. Identify agent's authority level
    agent_manifest = store.read(f"agents/{agent_id}/manifest")
    agent_authority = agent_manifest.authority
    
    # 2. Check if agent can write at requested authority
    requested_authority = ion_data.get("authority", "A3_OPERATIONAL")
    if not authority_enforcer.can_write(agent_id, requested_authority):
        return {"error": f"Agent {agent_id} cannot write at {requested_authority}"}
    
    # 3. Route through governed write
    result = governed_write.create(ion_data, agent=agent_id)
    return {"success": result.success, "ion_id": result.ion_id}
```

---

## §4. Backward Compatibility

### 4.1 Legacy Tool Wrapping

Existing MCP tools (`store_memory`, `retrieve_memory`, etc.) continue to work but are internally redirected to ION:

```python
# Legacy tool wrapper
def store_memory(key: str, value: str) -> dict:
    """Legacy MCP memory tool — now routes through ION."""
    return ion_create(
        agent_id="legacy_mcp",
        ion_data={
            "ion_id": f"memory/mcp/{key}",
            "type": "memory",
            "authority": "A5_PERSONAL",
            "title": key,
        },
        body=value
    )
```

### 4.2 Gradual Migration

| Phase | What Changes | What Stays Same |
|-------|-------------|----------------|
| Phase 1 | New `ion_*` tools added alongside legacy tools | Legacy tools still work |
| Phase 2 | Legacy tools emit deprecation warnings | ION tools become primary |
| Phase 3 | Legacy tools removed | Only ION tools remain |

---

## §5. Implementation Estimate

| Component | Lines (est) | Priority | Depends On |
|-----------|-------------|----------|------------|
| `mcp_ion_bridge.py` — core bridge module | ~500 | CRITICAL | ION Engine (done) |
| Ion CRUD tool handlers | ~300 | CRITICAL | Bridge core |
| Ion Graph tool handlers | ~200 | HIGH | Bridge core + graph.py |
| Ion Cognitive tool handlers | ~250 | HIGH | Bridge core + navigator.py |
| Ion Governance tool handlers | ~150 | MEDIUM | Bridge core + invariants |
| Legacy tool wrappers | ~200 | MEDIUM | Bridge core |
| Migration script | ~150 | MEDIUM | Bridge core + store.py |
| **Total** | **~1,750** | | |

---

## §6. Self-Audit Gate

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Current MCP landscape documented | ✅ | §1 — 6 servers, 84+ tools |
| Bridge architecture defined | ✅ | §2 — two-direction, tool tables |
| New ION tools specified | ✅ | §2.2 — 18 new tools in 4 categories |
| MCP state migration planned | ✅ | §2.3 — 4 data sources with migration paths |
| A2 protocol compliance mapped | ✅ | §3.1 — 8 schema mappings |
| Authority enforcement designed | ✅ | §3.2 — code example |
| Backward compatibility addressed | ✅ | §4 — legacy wrapping, 3-phase migration |
| Implementation estimate provided | ✅ | §5 — ~1,750 lines |

---

*This specification defines the bridge that makes ION accessible to every AI agent through the existing MCP protocol. Without this bridge, ION is a filesystem only accessible by direct Python code. With it, ION becomes the backend for the entire AIM-OS agent ecosystem.*

*Governed by: AETHER_CONSTITUTION.md*
*— Opus, 2026-03-23*
