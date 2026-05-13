---
atlas_package: system
system_slug: aim-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Scope

## In scope

- **Governance layer:** `AETHER_CONSTITUTION`, `AETHER_KERNEL`, `AETHER_ATLAS`, `AETHER_INTERFACE` — roles, authority classes, capsule/checkpoint schemas, registry law (`DOCUMENTED`).  
- **Major implemented systems** as described in `AIMOS_MAJOR_SYSTEMS.md`: CMC, HHNI, VIF, SEG, APOE, SDF-CVF, TCS, CAS, SCOR, IIS, MCP integration, daemon/RAG, and supporting layers — at **documentation/audit** granularity (`DOCUMENTED`).  
- **Architecture overview** and **LUCID-MCP** integration claims from `ARCHITECTURE_OVERVIEW.md` (`DOCUMENTED`; tool counts may **differ** across docs — ledger notes).  
- **Lineage and ION relationship** as stated in Aether **Book I** and registry (`DOCUMENTED`).

## Out of scope

- **Line-by-line verification** of all `packages/*` Python without per-claim file pointers (treat as **UNKNOWN** or **INFERRED** until cited).  
- **Production deployment topology** on specific hosts (unless **DOCUMENTED** in cited runbooks).  
- **AIM-OS marketing** not backed by cited technical docs.

## Versioning note

Aether docs carry **version headers** (e.g. Atlas v2.1.0, KERNEL v1.0, CONSTITUTION v1.0). Pin **file + date** when making code-level claims; AIM-OS is **fast-moving** (`DOCUMENTED` as a project characteristic, `src-aimos-major-systems`).
