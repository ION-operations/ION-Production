# Lane B: Contextual Sync × AIM-OS Prime Convergence Blueprint (v1)

Status: Drafted for merge-safe parallel branch planning  
Date: 2026-03-01  
Owner lane: Lane B (Contextual Sync convergence)  
Canon tier: **Tier B (staging/prototype canonical)** per `docs/CONTEXT_SYSTEM_CANON_REGISTRY_2026-03-05.md`  
Runtime note: This blueprint is not Tier A live runtime canon.

---

## Mission Frame

This document defines a first convergence path where Contextual Sync is a **superstrate** over AIM-OS Prime, not a rewrite.

Frozen doctrine preserved:

- Rust Context Mapper remains deterministic parser and envelope truth plane.
- Python daemon remains tool/memory/orchestration plane.
- Kernel remains supervision/routing/access plane.
- Contextual Sync is indexing/synchronization/governance substrate.
- No mapper pipeline replacement.
- No mapper/daemon responsibility collapse.
- No mandatory blocking sync gate yet.

---

## A) Convergence Blueprint

### A.1 Direct correspondences

| AIM-OS Prime component (current) | Contextual Sync concept | Correspondence type | Notes |
|---|---|---|---|
| `context_capsule_wire_and_mapper_v1/context_mapper_lab/src/extractor.rs` + `types.rs` | **BCI fact producer** | Direct | Extracted imports/contracts/parse confidence are source facts. |
| `context_capsule_wire_and_mapper_v1/context_mapper_lab/src/envelope.rs` | **Boundary view anchor (highest-fidelity view)** | Direct | Active Context Envelope source and metadata map to top view layer. |
| `context_capsule_wire_and_mapper_v1/context_mapper_lab/src/resolver.rs` | **Dependency relationship graph edges** | Direct | Local import resolution can emit dependency edges with confidence. |
| `context_capsule_wire_and_mapper_v1/daemon/lucid_mcp_server.py` | **Evidence/provenance plane** | Direct | Tool outputs (memory/timeline/goal state) provide operational evidence. |
| Kernel/Tauri role from `docs/SOVEREIGN_CONTEXT_MAPPER_AIMOS_PRIME_BUILD_PLAN.md` | **Retrieval/coordination surface** | Direct (architectural) | Kernel remains router and supervisor; Contextual Sync only advises. |

### A.2 Partial correspondences

| AIM-OS Prime state | Contextual Sync need | Gap type | Impact |
|---|---|---|---|
| `symbol_usage.rs` is placeholder | Symbol-level usage truth | Missing implementation | Limits precision of “used surface only” sync. |
| `resolve_reexports()` placeholder | Re-export provenance chains | Missing implementation | Limits transitive dependency certainty. |
| Envelope currently shape-only in mapper lab | L0-L5 boundary-view stack | Missing layering | Needs derived summary views above envelope. |

### A.3 Non-correspondences (explicitly not present yet)

- No hard synchronization gate in runtime routing.
- No dedicated Shadow BCI storage schema in live architecture.
- No contradiction/drift engine wired into kernel decisions.

---

## B) Shadow BCI v1

Design goal: minimal, additive, replayable shadow index.

### B.1 Core entities

1. `bci_atom` (fact record)
- What it stores: extracted contracts/imports/envelope metadata/tool evidence.

2. `bci_edge` (relationship record)
- What it stores: dependency, emits, supports, contradicts, supersedes relations.

3. `bci_boundary_view` (view materialization)
- What it stores: L0-L5 summary-to-envelope projections.

4. `bci_sync_advisory` (non-blocking sync state)
- What it stores: stale/drift/contradiction warnings and severity.

### B.2 Required fields

`bci_atom`:

- `atom_id` (uuid)
- `fact_type` (contract/import/envelope_meta/tool_evidence)
- `source_plane` (mapper/daemon/kernel/contextual_sync)
- `source_ref` (file path + symbol or tool name)
- `payload` (json object)
- `payload_hash` (sha256)
- `created_at` (ISO-8601 UTC)

`bci_edge`:

- `edge_id` (uuid)
- `from_atom_id`
- `to_atom_id`
- `relation_type` (depends_on/emits/derived_from/supports/contradicts)
- `created_at`

`bci_boundary_view`:

- `view_id` (uuid)
- `target_ref` (file/symbol)
- `view_level` (L0..L5)
- `render_payload` (json)
- `derived_from_atom_ids` (array)
- `created_at`

`bci_sync_advisory`:

- `advisory_id` (uuid)
- `target_ref`
- `sync_state` (`fresh` | `stale` | `drift` | `contradiction` | `unknown`)
- `severity` (`info` | `warn` | `high`)
- `message`
- `evidence_atom_ids` (array)
- `detected_at`
- `resolved_at` (nullable)

### B.3 Temporal fields (explicit)

- `observed_at` (when source fact was observed)
- `valid_from` (fact validity start)
- `valid_to` (nullable, open-ended allowed)
- `recorded_at` (when written into shadow store)
- `last_checked_at` (advisory refresh point)

### B.4 Sync state model (advisory-first)

- `fresh`: source and shadow consistent.
- `stale`: source changed, shadow not refreshed.
- `drift`: semantic mismatch likely.
- `contradiction`: incompatible facts present.
- `unknown`: insufficient evidence.

No blocking behavior in v1.

### B.5 Provenance/evidence fields

Per record include:

- `producer` (component/function or tool name)
- `producer_version`
- `parse_confidence` (High/Degraded/Fallback when mapper-derived)
- `tool_call_id` (if daemon-derived)
- `snapshot_id` (optional link to CMC snapshot)
- `correlation_id` (cross-plane request chain)

### B.6 Minimum viable storage shape

SQLite (recommended for merge-safe additive v1):

- `shadow_bci_atoms`
- `shadow_bci_edges`
- `shadow_bci_views`
- `shadow_bci_sync_advisories`

Optional append-only `jsonl` mirror for audit replay.

---

## C) First Emission Plan

### C.1 Emission points (current system)

1. **EP-1 (Mapper extract complete)**  
Insertion point: after `TreeSitterExtractor.extract()` result exists.  
Classification: Observational only.

2. **EP-2 (Resolver complete)**  
Insertion point: after `resolve_imports()` returns file paths.  
Classification: Observational only.

3. **EP-3 (Envelope materialized)**  
Insertion point: after `Envelope::from_extracted()` and `meta()`.  
Classification: Observational only.

4. **EP-4 (Daemon tool evidence)**  
Insertion point: after successful `tools/call` result in bridge or daemon wrapper.  
Classification: Advisory only.

### C.2 What can populate BCI immediately

- Target file path.
- Imports list.
- Public contract set (kind/name/signature).
- Parse confidence.
- Resolved local dependency file list.
- Envelope metadata (`contract_count`, confidence).
- Daemon evidence (tool name + response hash).

### C.3 What is missing today

- Real symbol usage graph (`symbol_usage.rs` currently placeholder).
- Re-export chain certainty (`resolve_reexports()` placeholder).
- Inbound caller context.
- Full transitive type exposure guarantees.

### C.4 Minimal-disruption emission payload

Emit immutable snapshots of mapper/daemon outputs into Shadow BCI store, without changing routing, mutation logic, or envelope construction behavior.

---

## D) Merge-Safe Implementation Slice

### D.1 First merge candidate

- **Module/file location:** `context_capsule_wire_and_mapper_v1/shadow_sync/shadow_bci_v1_schema.json`
- **Why safe:** additive file only, no runtime wiring to kernel/context_service/context_mapper core/daemon bridge internals.
- **What it does:** defines shared schema contract for Shadow BCI records and advisory sync states.
- **What it intentionally does not do:** no blocking gate, no command routing changes, no mapper/daemon ownership changes.

### D.2 Merge impact classification

- **Safe now**
  - Add schema and design docs.
  - Add standalone validator or fixture examples in `shadow_sync`.
- **Safe later**
  - Add passive emitter hooks behind explicit feature flag.
  - Add kernel read-only endpoint for advisory state lookup.
- **Not safe yet**
  - Hard gate on sync contradictions.
  - Any automatic mutation-blocking behavior.
  - Any rewrite of mapper extraction or daemon request dispatch.

---

## E) Drift Check (Doctrine Preservation)

Confirmed preserved:

- Mapper sovereignty preserved (remains deterministic source analysis authority).
- Daemon sovereignty preserved (tool/memory/orchestration remains Python daemon).
- Kernel role preserved (supervision/routing/access remains kernel responsibility).
- Contextual Sync remains superstrate (indexing/governance/advisory layer only).

No doctrine bend required for this v1 convergence path.

---

## Lane B Report Shape (Current Iteration)

### A. What changed

- Added this convergence blueprint document.
- Added Shadow BCI v1 schema file (see merge candidate path).
- No edits to `kernel_planes`, `context_service`, mapper core extraction flow, or daemon bridge internals.

### B. Assumptions made

- Lane A remains source of truth for live kernel behavior.
- Current mapper and wire proof artifacts in `context_capsule_wire_and_mapper_v1` represent the active convergence baseline.
- Contextual Sync enters first as read-only/advisory shadow substrate.

### C. Merge impact

- Isolated and additive.
- No dependency on modifying active live seams.
- Prepares future convergence without behavior changes.

### D. Drift check

- Frozen doctrine remains intact.
- No parallel rewrite pattern introduced.

### E. Recommended next move

Create a tiny standalone shadow emitter prototype that ingests one `ExtractedFile` JSON sample into `shadow_bci_atoms` and produces one L0 + one L5 boundary view record, without touching mapper runtime flow.
