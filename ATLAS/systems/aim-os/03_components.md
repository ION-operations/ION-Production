---
atlas_package: system
system_slug: aim-os
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Components

Summaries below follow **`AIMOS_MAJOR_SYSTEMS.md`** unless otherwise cited. Package paths are **on-disk** under the AIM-OS repository.

## Core memory and retrieval

| Component | Ceremonial / short | Role (short) | Typical module / path (from docs) |
|-----------|-------------------|--------------|-----------------------------------|
| **CMC** | Context Memory Core | Bitemporal atoms, snapshots, provenance envelopes | `packages/cmc_service/` (`DOCUMENTED`) |
| **HHNI** | Hierarchical Hypergraph Neural Index | Multi-resolution indexing, DVNS “physics” for retrieval | `packages/hhni/` (`DOCUMENTED`) |
| **VIF** | Verifiable Intelligence Framework | Witness envelopes, κ-gating, calibration | `packages/vif/` (`DOCUMENTED`) |
| **SEG** | Shared Evidence Graph | Contradiction-aware evidence graph, export | `packages/seg/` (`DOCUMENTED`) |
| **APOE** | AI-Powered Orchestration Engine | ACL plans, roles, budgets, gates, DEPP | `packages/apoe/` (`DOCUMENTED`) |
| **SDF-CVF** | Atomic Evolution Framework | Quartet parity (code/docs/tests/traces), blast radius | `packages/sdfcvf/` (`DOCUMENTED`) |

## Context, cognition, safety

| Component | Role | Notes |
|-----------|------|-------|
| **TCS** | Timeline / session continuity | Tier D / deferred notes in registry (`DOCUMENTED`, `src-aimos-tcs-tier`) |
| **CAS** | Cognitive Analysis System | Meta-cognitive monitoring (`DOCUMENTED`) |
| **SCOR** | Sanity Core | Invariant and manipulation resistance (`DOCUMENTED`) |
| **IIS** | Intuitive Intelligence System | Partial implementation noted (`DOCUMENTED` + **INFERRED** depth) |

## Integration

| Component | Role |
|-----------|------|
| **MCP integration** | JSON-RPC MCP tool exposure (`DOCUMENTED`; tool inventory **time-sensitive**) |
| **Daemon / RAG** | Tool selection and proxy for large tool sets (`DOCUMENTED`) |
| **Co-Agency / DOS / others** | Supporting systems per same reference (`DOCUMENTED` overview) |

## Law and schema (non-code)

| Artifact | Role |
|----------|------|
| `AETHER_CONSTITUTION.md` | Supreme law |
| `AETHER_KERNEL.md` | Boot projection |
| `AETHER_ATLAS.md` | Registry + operational truth |
| `AETHER_INTERFACE.md` | Typed protocols (capsule, checkpoint, …) |
