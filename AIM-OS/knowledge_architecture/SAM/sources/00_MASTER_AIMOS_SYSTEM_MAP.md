# 00 MASTER AIM-OS SYSTEM MAP

**Purpose:** Project-level SAM index for AIM-OS. Links to all subsystem maps; provides high-level architecture view.

**Date:** 2026-02-22  
**Status:** ACTIVE  
**Scope:** AIM-OS core systems, MCP integration

---

**[TAG:SAM] [TAG:MASTER] [TAG:AIMOS]**

## 1. SYSTEM OVERVIEW

**[TAG:OVERVIEW] [TAG:AIMOS]**

AIM-OS (AI-Integrated Memory and Operations System) is a research and engineering platform for building AI systems with persistent memory, verified honesty, and full auditability. This SAM index maps all major systems and their interconnections.

### Core Architecture

```
CMC (memory) <-> HHNI (retrieval) <-> VIF (provenance)
     |                |                    |
     +----------------+--------------------+
                      |
    APOE (orchestration) -> SEG (evidence) -> SDF-CVF (quality)
                      |
    TCS (timeline) <- CAS (cognitive) <- SCOR (safety)
                      |
    IIS (intuition)   MCP (tools)   Daemon/RAG (tool selection)
```

**[END:TAG:OVERVIEW]**

---

## 2. DOCUMENT MAP

| Subsystem | SAM Source | Description |
|-----------|------------|-------------|
| CMC | [MASTER_CMC_SYSTEM_MAP.md](MASTER_CMC_SYSTEM_MAP.md) | Context Memory Core - Bitemporal storage |
| HHNI | [MASTER_HHNI_SYSTEM_MAP.md](MASTER_HHNI_SYSTEM_MAP.md) | Hierarchical Hypergraph Neural Index |
| VIF | [MASTER_VIF_SYSTEM_MAP.md](MASTER_VIF_SYSTEM_MAP.md) | Verifiable Intelligence Framework |
| SEG | [MASTER_SEG_SYSTEM_MAP.md](MASTER_SEG_SYSTEM_MAP.md) | Shared Evidence Graph |
| APOE | [MASTER_APOE_SYSTEM_MAP.md](MASTER_APOE_SYSTEM_MAP.md) | AI-Powered Orchestration Engine |
| SDF-CVF | [MASTER_SDFCVF_SYSTEM_MAP.md](MASTER_SDFCVF_SYSTEM_MAP.md) | Atomic Evolution Framework |
| TCS | [MASTER_TCS_SYSTEM_MAP.md](MASTER_TCS_SYSTEM_MAP.md) | Timeline Context System |
| CAS | [MASTER_CAS_SYSTEM_MAP.md](MASTER_CAS_SYSTEM_MAP.md) | Cognitive Analysis System |
| SCOR | [MASTER_SCOR_SYSTEM_MAP.md](MASTER_SCOR_SYSTEM_MAP.md) | Sanity Core |
| IIS | [MASTER_IIS_SYSTEM_MAP.md](MASTER_IIS_SYSTEM_MAP.md) | Intuitive Intelligence System |
| MCP | [MASTER_MCP_INTEGRATION_SYSTEM_MAP.md](MASTER_MCP_INTEGRATION_SYSTEM_MAP.md) | MCP server, RAG daemon, tool surface |

---

## 3. CODE ANCHORS

| System | Package/Path |
|--------|--------------|
| CMC | packages/cmc_service/ |
| HHNI | packages/hhni/ |
| VIF | packages/vif/ |
| SEG | packages/seg/ |
| APOE | packages/apoe/ |
| SDF-CVF | packages/sdfcvf/ |
| TCS | packages/timeline_context_system/ |
| MCP | lucid_mcp_server.py |
| Daemon/RAG | daemon_rag_system/, packages/mcp_rag_proxy/ |

---

## 4. REFERENCES

- **AIMOS_MAJOR_SYSTEMS:** docs/AIMOS_MAJOR_SYSTEMS.md
- **Living System Map:** knowledge_architecture/AETHER_MEMORY/Living_System_Map.md
- **SUPER_INDEX:** knowledge_architecture/SUPER_INDEX.md
- **SAM Hub:** knowledge_architecture/SAM/README.md
