---
ion_id: intents/composer_deep_consolidation
ion_type: intent
title: "Mission — Composer deep consolidation (ion-native knowledge graph)"
owner: opus
authority: A2
state: active
confidence: 0.85
gate_class: 2
priority: high
depends_on:
  - memory/composer/protocol_native_ion_outputs
  - memory/composer/canon_crosswalk_seed
affects:
  - memory/composer/audit_log
  - memory/knowledge_architecture/index
  - memory/packages/index
  - memory/composer/ion_tracks/index
  - memory/composer/consolidation_master_hub
metadata:
  epistemic_status: ASSIGNED
  mission_phase_1_ka_subtrees: complete
  mission_phase_2_core_packages: complete
  mission_phase_3_ion_tracks: complete
  mission_phase_4_alignment_mcp_hub: complete
  mission_version: "1.0"
  handoff_for: composer
  mirror_path_operation_victus: data/.ion/intents/composer_deep_consolidation.md
  external_targets:
    - kind: aether_doc
      repo: AIM-OS-GIT
      path: docs/Aether-OS/MASTER_INDEX.md
    - kind: aether_doc
      repo: AIM-OS-GIT
      path: docs/Aether-OS/SYSTEM_UNIVERSE_MAP.md
    - kind: aether_doc
      repo: AIM-OS-GIT
      path: docs/Aether-OS/ION_ENGINE_SPEC.md
    - kind: aether_doc
      repo: AIM-OS-GIT
      path: docs/Aether-OS/AETHER_INTEGRATION_SPEC.md
provenance:
  created_by: opus
  created_at: 1774306021.31
  version: 1
  lineage: []
tags:
  - mission
  - composer
  - ion-native
  - consolidation
  - knowledge-graph
---

# Mission — Composer deep consolidation

## Intent

Populate the ION filesystem with **first-class ions** (not parallel markdown summaries). Composer’s analyses are knowledge graph nodes: YAML frontmatter, valid `ion_type`, native bond lists (`requires`, `produces`, `affects`, `depends_on`, `escalate_to`, `supersedes`), and bodies that humans and ingest pipelines can read.

**Meta-circular rule:** Use the system’s format to document the system so that when ION boots and indexes `operation-victus/data/.ion/`, the graph already contains structured, bonded content.

## Current system state (bond targets, not copies)

| Canon | Absolute path |
|-------|----------------|
| Master index | `/home/sev/AIM-OS-GIT/docs/Aether-OS/MASTER_INDEX.md` |
| Universe map | `/home/sev/AIM-OS-GIT/docs/Aether-OS/SYSTEM_UNIVERSE_MAP.md` |
| ION engine spec | `/home/sev/AIM-OS-GIT/docs/Aether-OS/ION_ENGINE_SPEC.md` |
| Integration spec | `/home/sev/AIM-OS-GIT/docs/Aether-OS/AETHER_INTEGRATION_SPEC.md` |

Repository paths that are not yet ions MUST appear under `metadata.external_targets` (or equivalent) until ingested; edges between real ions use native bond fields only.

## Output format (required)

- **Location (runtime):** `operation-victus/data/.ion/` under the correct type directory (`memory/`, `intents/`, `evidence/`, etc.) per `IonType.default_directory` in `victus/ion/model.py`.
- **Knowledge-architecture sweep:** place subtree summary ions under `memory/knowledge_architecture/<subdir_slug>/summary.md` (one ion per AIM-OS-FRESH `knowledge_architecture/` subdirectory, ~30 ions), each with `metadata.external_targets` pointing at the scanned directory and `depends_on` / `affects` linking related summary ions.
- **Core packages (9):** one **memory** ion each for CMC, HHNI, VIF, APOE, SEG, SDF-CVF, TCS, CAS, IIS — `depends_on` edges to sibling summaries where the integration spec defines coupling (e.g. CMC ↔ HHNI retrieval).
- **ION tracks:** one **memory** ion per track cluster (A–Q) summarizing implemented vs stub modules and inter-module edges; `depends_on` the canonical spec ion `memory/composer/canon_crosswalk_seed` or successor.
- **Authority:** Composer factual writeups = `A4` (`AuthorityClass.A4_RUNTIME`). Do not mint A0–A1 constitutional ions.
- **Bonds:** Use **native lists** only. Do not use a fictional `bonds:` YAML array; `BondType` is enforced in code (`affects`, `depends_on`, …). Optional nuance (strength, “describes”) lives in `metadata` on the ion or in the markdown body.

## Agent protocol (Composer)

1. Load `.agent/genomes/composer.genome.md` at session start.
2. Obey `.agent/COMMS_DOCTRINE.md` for human-facing messages (e.g. `[COMPOSER] | …`).
3. Post state to `.agent/comms/status/composer.status.md` when work phases complete.
4. Prefer **ions on disk** as the durable artifact; chat is not the source of truth.

## Success criteria

- Every deliverable in this mission is a **single `.md` ion file** parseable by `victus.ion.parser.read_ion_file` without errors.
- Each ion has a stable `ion_id` matching its path under `data/.ion/` (e.g. `memory/knowledge_architecture/sam/summary`).
- Cross-ion relationships are expressed with at least one native bond field where another ion exists; otherwise `metadata.external_targets` documents the repo path.
- Opus (or index jobs) can run `IonStore` / indexer over `data/.ion` and see new nodes without ad-hoc importers.

## Priority order

1. **AIM-OS-FRESH `knowledge_architecture/`** — one summary ion per immediate subdirectory (~30); highest leverage for unread surface area.
2. **Nine core packages** — deep-read memory ions (production vs prototype, real entrypoints/APIs).
3. **ION track clusters** — A–Q rollup ions tied to `operation-victus/victus/ion/`.

## Phase status (runtime)

- **Phase 1 (KA subtrees):** complete — hub ion `memory/knowledge_architecture/index`, 30 summaries under `memory/knowledge_architecture/*/summary` in `operation-victus/data/.ion/`.
- **Phase 2 (nine core packages):** complete — hub `memory/packages/index`, nine `memory/packages/<pkg>/summary` ions.
- **Phase 3 (ION track rollups):** complete — `memory/composer/ion_tracks/index` + `rollup_track_a`…`q` + `rollup_track_u`.
- **Phase 4 (hub + alignment + MCP):** complete — `memory/composer/consolidation_master_hub` and companion ions; see audit log for runtime enum/governance/viz edits.

## Completion signal

When a phase finishes, append a dated entry to `memory/composer/audit_log` (ion) and update `composer.status.md` with counts (ions written, bonds added, blockers).
