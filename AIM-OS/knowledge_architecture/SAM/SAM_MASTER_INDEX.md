# SAM Master Index

**Purpose:** Central index for AIM-OS SAM (System Anatomy Mapping) sources. Lists all subsystem maps, code anchors, and cross-references.

**Date:** 2026-02-22  
**Status:** ACTIVE  
**Scope:** AIM-OS core systems, MCP integration

---

## Document Map

| System | SAM Source | Status | Description |
|--------|------------|--------|-------------|
| Project Index | [00_MASTER_AIMOS_SYSTEM_MAP.md](sources/00_MASTER_AIMOS_SYSTEM_MAP.md) | Complete | Project-level index and architecture overview |
| CMC | [MASTER_CMC_SYSTEM_MAP.md](sources/MASTER_CMC_SYSTEM_MAP.md) | Complete | Context Memory Core - Bitemporal storage |
| HHNI | [MASTER_HHNI_SYSTEM_MAP.md](sources/MASTER_HHNI_SYSTEM_MAP.md) | Complete | Hierarchical Hypergraph Neural Index |
| VIF | [MASTER_VIF_SYSTEM_MAP.md](sources/MASTER_VIF_SYSTEM_MAP.md) | Complete | Verifiable Intelligence Framework |
| SEG | [MASTER_SEG_SYSTEM_MAP.md](sources/MASTER_SEG_SYSTEM_MAP.md) | Complete | Shared Evidence Graph |
| APOE | [MASTER_APOE_SYSTEM_MAP.md](sources/MASTER_APOE_SYSTEM_MAP.md) | Complete | AI-Powered Orchestration Engine |
| SDF-CVF | [MASTER_SDFCVF_SYSTEM_MAP.md](sources/MASTER_SDFCVF_SYSTEM_MAP.md) | Complete | Atomic Evolution Framework |
| TCS | [MASTER_TCS_SYSTEM_MAP.md](sources/MASTER_TCS_SYSTEM_MAP.md) | Complete | Timeline Context System |
| CAS | [MASTER_CAS_SYSTEM_MAP.md](sources/MASTER_CAS_SYSTEM_MAP.md) | Complete | Cognitive Analysis System |
| SCOR | [MASTER_SCOR_SYSTEM_MAP.md](sources/MASTER_SCOR_SYSTEM_MAP.md) | Complete | Sanity Core |
| IIS | [MASTER_IIS_SYSTEM_MAP.md](sources/MASTER_IIS_SYSTEM_MAP.md) | Complete | Intuitive Intelligence System |
| MCP | [MASTER_MCP_INTEGRATION_SYSTEM_MAP.md](sources/MASTER_MCP_INTEGRATION_SYSTEM_MAP.md) | Complete | MCP server, RAG daemon, tool surface |

---

## Code Anchors

| System | Package/Path |
|--------|--------------|
| CMC | packages/cmc_service/ |
| HHNI | packages/hhni/ |
| VIF | packages/vif/ |
| SEG | packages/seg/ |
| APOE | packages/apoe/ |
| SDF-CVF | packages/sdfcvf/ |
| TCS | packages/timeline_context_system/ |
| MCP Server | lucid_mcp_server.py |
| RAG Daemon | daemon_rag_system/ |
| RAG Proxy | packages/mcp_rag_proxy/ |
| Cursor Addon | cursor-addon/ |

---

## Related Documentation

- **AIMOS_MAJOR_SYSTEMS:** [docs/AIMOS_MAJOR_SYSTEMS.md](../../docs/AIMOS_MAJOR_SYSTEMS.md) — Major systems reference
- **SUPER_INDEX:** [knowledge_architecture/SUPER_INDEX.md](../SUPER_INDEX.md) — Concept index
- **Living System Map:** [knowledge_architecture/AETHER_MEMORY/Living_System_Map.md](../AETHER_MEMORY/Living_System_Map.md)
- **SAM Hub:** [knowledge_architecture/SAM/README.md](README.md) — SAM protocol hub
- **SAM Growth Protocol:** [SAM_GROWTH_PROTOCOL.md](SAM_GROWTH_PROTOCOL.md) — How to add/update maps

---

## Compiler Status

The SAM compiler (`build_monolith_v2.py`) is documented but not present in the repo. Until wired: edit sources in `sources/` directly; monolith and manifest are not generated. See [SAM_PROTOCOL_COMPLETE](../PROTOCOLS/SAM_PROTOCOL_COMPLETE.md) for build architecture.
