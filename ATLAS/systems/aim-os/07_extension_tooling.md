---
atlas_package: system
system_slug: aim-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Extension and tooling

## LUCID-MCP

Large **MCP** surface exposing AIM-OS capabilities to hosts (e.g. Cursor-class IDEs). **Canonical current count:** **103** tools defined in `lucid_mcp_server.py` `handle_tools_list` (**OBSERVED**, `aim-028`). `ARCHITECTURE_OVERVIEW.md` still states 93 — **stale** vs source unless updated.

## Cursor constraints

Major systems reference notes **Cursor IDE tool limit** (~80) and **RAG middleware** filtering to a subset (`DOCUMENTED`, `src-aimos-mcp-cursor-limit`).

## Goal / planning artifacts

Repository includes **goals/** trees, **MASTER_PLAN_INDEX**, YAML goal trees — operational planning, not kernel law (`DOCUMENTED` path existence `src-aimos-goals-path`).

## External protocols

AIM-OS **implements MCP** as a server; alignment with **Model Context Protocol** specification is **DOCUMENTED** at “protocol-compliant” level (`src-aimos-mcp-jsonrpc`).
