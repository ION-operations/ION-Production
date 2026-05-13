---
atlas_package: system
system_slug: aim-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Relation map

## Typed edges (see `relations.json`)

- **`integrates_with` → `model-context-protocol`** — AIM-OS exposes **LUCID-MCP** as an MCP server (`DOCUMENTED`).  
- **`depends_on` → `linux-kernel`** — Typical developer/operator host for Python/MCP stacks (**INFERRED** deployment default; not a formal product requirement in cited docs).

## Narrative (cross-system)

| Related system | Relationship |
|----------------|--------------|
| **Model Context Protocol** | AIM-OS **implements** MCP server semantics (JSON-RPC) (`DOCUMENTED`). |
| **Cursor** | First-class **host** in docs (tool limits, integration) (`DOCUMENTED` as paired environment, not ownership). |
| **ION (program)** | **Lineage / design pressure** — Project ION listed as **A3** in Aether authority table; **no** `ion-*` slug in Systems ATLAS yet — relate via this narrative and ION relay packets. |
| **Docker / Kubernetes** | **UNKNOWN** as hard dependency from cited quartet alone; may appear in deployment docs not imported here. |

## Anti-confusion

| Name | Relation |
|------|----------|
| **Systems ATLAS** (this repo’s `ATLAS/`) | **Encyclopedia** *about* AIM-OS; not **AETHER_ATLAS**. |
| **00_CONSOLIDATED_ATLAS** | ION merge evidence — orthogonal. |
