---
id: "cmc_T1_overview"
system: "cmc"
component: null
level: "T1"
type: "overview"
title: "CMC Overview"
description: "500-word overview of Context Memory Core"
audience: "architects, planners"
confidence_threshold: 0.75
token_cost: 500
word_count: 500
created: "2025-10-30T00:00:00Z"
updated: "2025-11-02T15:15:00Z"
author: "aether"
status: "complete"
tags: ["cmc", "core", "memory", "bitemporal", "t0-t6", "transitional"]
dependencies: ["cmc_T0_executive"]
related_docs: ["cmc_T2_architecture", "system.map.lucid.json5"]
version: "v2.2.0"
---

> **TRANSITIONAL T-LEVEL DOCUMENT** – Do not overwrite existing L-level docs. This T-level will supersede L-level after review/acceptance.

# CMC – T1 Overview (≈500 words)

## Purpose & Scope

CMC (Context Memory Core) is AIM-OS's foundational memory substrate that transforms ephemeral AI context into structured, queryable, reversible memory. Instead of forgetting between sessions, AI systems with CMC remember everything, can time-travel through memory, and always retrieve the perfect context for any task.

CMC provides three core guarantees:

1. **Bitemporal Storage:** Every memory has two timestamps—transaction time (when recorded) and valid time (when true in the world). This enables "what did we know on Oct 15?" queries and precise temporal reasoning.

2. **Provenance & Auditability:** Every atom includes a VIF witness envelope, linking content to confidence scores, sources, and verification. Full audit trail enables trust and verification.

3. **Reversible Memory:** Snapshots provide immutable, content-addressed bundles of atoms. Any state can be restored, any decision audited, any change rolled back. Git-like versioning for memory.

**System Boundaries:**
- CMC owns: Atom lifecycle, snapshot creation, storage coordination, write/read pipelines
- CMC does NOT own: Embedding generation (delegates), HHNI indexing logic (uses as library), DVNS physics (delegates), policy decisions (reads from policy engine)

## Users & Integrations

**HHNI (Hierarchical Hypergraph Neural Index):** CMC provides atoms, HHNI indexes them hierarchically (System → Subword). HHNI uses CMC for retrieval context and dependency tracking. For v1 automation, HHNI follows a polling pattern (CMC journal + MCP polling, at‑least‑once, idempotent by `atom_id`) with a modality allowlist (`tcs_timeline`, `plan_execution`, `cas_introspection_analysis`) and tag hints (`hhni_index`, `timeline_context`, `apoe`, `cas`, `seg`).

**VIF (Verifiable Intelligence Framework):** All VIF witnesses stored as atoms in CMC. CMC provides confidence envelopes and provenance chains for verification.

**SEG (Shared Evidence Graph):** Provenance graph nodes/edges stored in CMC's graph layer. CMC enables contradiction detection and evidence synthesis. A Priority‑1 helper (`store_timeline_entry_for_seg`) stores TCS timeline entries as atoms (`modality: tcs_timeline`) and returns `atom_id` for SEG ingest, enabling the gate evidence tuple `(prompt_id, atom_id, evidence_id)`.

**APOE (AI-Powered Orchestration Engine):** APOE retrieves context from CMC, stores execution traces back to CMC. CMC provides plan state and checkpoint restoration. APOE also stores `plan_execution` atoms (JSON payload of execution state) tagged with `apoe`, `plan`, and `status:*`, correlating via `execution_id`.

**SDF-CVF (Atomic Evolution Framework):** Parity gates enforce CMC schema consistency across code/docs/tests. CMC stores trace emissions for quartet parity.

## Core Concepts

**Atom:** Fundamental memory unit containing content (text, code, event, tool call), metadata (tags, embeddings, confidence), temporal bounds (valid_from, valid_to), and provenance (snapshot_id, VIF witness). Same schema works for all modality types.

**Bitemporal Model:** Every atom has transaction time (when recorded in CMC) and valid time (when true in the world). Enables as-of queries, time-travel, and precise temporal reasoning.

**Snapshots & Versioning:** Immutable, content-addressed (SHA-256) bundles of atoms at specific moments. Never modified after creation (C-2 constraint). Enables rollback, replay, audit, and distributed-system friendly deduplication.

**Provenance & Auditability:** Every atom includes VIF witness envelope (claim, confidence, sources). Full audit trail enables trust, verification, and contradiction detection.

## High‑Level Data Flow

**Write Path:**
```
Input → Parse → Create Atoms → Enrich with QS/TPV → 
Index via HHNI → Quality Gate → Add to Snapshot → 
Link to SEG → Persist
```

**Read Path:**
```
Query → HHNI Lookup → DVNS Physics Optimization → 
Deduplication → Conflict Resolution → Compression → 
Budget Fit → Optimal Context
```

## Non‑Goals

CMC is NOT:
- **Vector similarity engine:** Embeds are stored, but similarity search delegated to HHNI
- **Orchestration system:** Provides context, but planning/execution handled by APOE
- **Policy engine:** Reads policies but doesn't enforce them (gate layer)
- **UI/UX:** Provides APIs only, no user interface
- **Generic database:** Memory-native, not SQL/NoSQL database

## NL Tag Coverage

- **Total NL Tags:** 0 tags
- **Quintet Parity:** P = 0.88 (very good)
- **Semantic Search:** All functions tagged
- **Tag Catalog:** [NL_TAG_CATALOG.md](NL_TAG_CATALOG.md)

---


## References

- System map: `systems/cmc/system.map.lucid.json5`
- Validation gates: `knowledge_architecture/validation/T0_T6_DOCUMENTATION.validation.md`
- Templates: `knowledge_architecture/PERFECT_TEMPLATES_LIBRARY.md`
- L-level docs: `systems/cmc/L0_executive.md` through `L4_complete.md`
