---
atlas_package: system
system_slug: aim-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Storage, network, and IPC

## Storage (CMC)

**SQLite** backend is stated for **CMC** service implementation, with compression options (gzip, lz4, brotli, zlib) per major systems reference (`DOCUMENTED`, `src-aimos-cmc`).

## MCP / JSON-RPC

**MCP integration** is described as **JSON-RPC 2.0** over **stdio**, protocol-compliant (`DOCUMENTED`, `src-aimos-mcp-section`).

## Network exposure

**DEFAULT:** Deployment-specific. Public docs describe **IDE-integrated** MCP usage; **wide-area** service topology for a full AIM-OS deployment is **UNKNOWN** in this package without cited deployment doc.

## Inter-process / host boundaries

**Daemon/RAG** and **MCP proxy** components mediate tool exposure; exact process model is **DOCUMENTED** only at overview level (`src-aimos-daemon-rag`).
