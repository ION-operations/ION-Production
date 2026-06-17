# ION Exhaust & Duplication Catalog (candidate)

**Status:** candidate / read-only audit — **PROPOSAL ONLY**  
**Authority:** not-accepted-state; no production-readiness claims; no files were moved, archived, renamed, or deleted.  
**Active root:** `/home/sev/ION - Production/ION_Developement`  
**Audited:** 2026-06-17  
**Scope:** `ION/05_context` categorization, reclaimable exhaust estimate, kernel/code duplication, load-bearing exceptions, proposed archival plan.

## Executive scale (evidence)

| Surface | `du -sh` | Notes |
|---------|----------|-------|
| Repo root | 6.7G | prior session measurement |
| `ION/05_context` | 5.8G | 87% of repo |
| `ION/05_context/current` | ~5.79G | 54,282 files (`find … -type f \| wc -l`) |
| `ION/05_context` (all) | 5.8G | 55,747 files |
| `ION/04_packages` (product) | 61M | prior session measurement |
| `ION_EXPORTS_LOCAL` (repo root, outside `05_context`) | 614M | 13,466 files — duplicate transfer/export lane |

---

## 1. Category breakdown — `ION/05_context`

### 1A. Non-`current/` subtrees (~7.6M total)

| Category | Path | Size | ~Files | One-line description | Verdict |
|----------|------|------|--------|----------------------|---------|
| **signals** | `ION/05_context/signals/` | 1.5M | 329 | Kernel/domain maintenance receipts; several paths bound in `ION_LIVING_ENCYCLOPEDIA_MANIFEST_V100.json` | **load-bearing** |
| **comms** | `ION/05_context/comms/` | 2.6M | 527 | Kernel-router run ledgers, roundtable/migration comms | **process-exhaust** |
| **inbox** | `ION/05_context/inbox/` | 1.5M | 239 | Staged intake queues (bootstrap, chatgpt_browser, steward) | **mixed** |
| **history** | `ION/05_context/history/` | 424K | 70 | Front-door/runtime/conversational receipt history | **process-exhaust** |
| **runtime_state** | `ION/05_context/runtime_state/` | 688K | 160 | Local MCP bridge / runtime identity residue | **mixed** |
| **archive** | `ION/05_context/archive/` | 288K | 56 | Containment witness manifests (incl. V123 bundle referenced by `REPO_AUTHORITY.md`) | **load-bearing** (subset) |
| **graph** | `ION/05_context/graph/` | 176K | 21 | Self-mount / template-event graph state | **mixed** |
| **handoff** | `ION/05_context/handoff/` | 144K | 34 | Agent succession packets | **process-exhaust** |
| **continuation_bundles** | `ION/05_context/continuation_bundles/` | 76K | 7 | VM continuation bootstrap bundles | **process-exhaust** |
| **runtime_identity_envelopes** | `ION/05_context/runtime_identity_envelopes/` | 92K | 11 | Runtime identity envelopes | **process-exhaust** |
| **fixtures** | `ION/05_context/fixtures/` | 44K | 5 | UI/visual-regression fixtures | **mixed** |
| **runtime_reports** | `ION/05_context/runtime_reports/` | 32K | 4 | Operations runtime reports | **process-exhaust** |
| **steward_handoffs** | `ION/05_context/steward_handoffs/` | 36K | 1 | Steward handoff residue | **process-exhaust** |

### 1B. `current/` — domain weaver (~5.0G, 25,571 files)

| Category | Path | Size | ~Files | One-line description | Verdict |
|----------|------|------|--------|----------------------|---------|
| **terminal_workers** | `…/domain_weaver/terminal_workers/` | 4.7G | 11,703 | Codex-CLI terminal fleet mission/seat/attempt/gate receipts; single run `terminal_20_codex_cli_20260610T021002Z` alone is 4.7G | **process-exhaust** (see load-bearing exceptions) |
| **live_carrier_binding** | `…/domain_weaver/live_carrier_binding/` | 220M | 8,201 | Invocable binding proof rows/schemas consumed by kernel projection refresh & observatory | **mixed** |
| **full_steam_push** | `…/domain_weaver/full_steam_push/` | 18M | — | Agent-blocker team push lane returns/reports | **process-exhaust** |
| **operator_experience** | `…/domain_weaver/operator_experience/` | 6.3M | — | Operator UX/domain-expansion request drafts | **mixed** |
| **receipts** | `…/domain_weaver/receipts/` | 6.3M | — | Domain-weaver apply/validation receipts | **mixed** |
| **projection / promotion** | `DOMAIN_WEAVER_PROJECTION.json`, `PROMOTION_*.json`, `operator_actions/`, `validation/` | ~4M | — | Active projection + promotion gate artifacts referenced by Living Encyclopedia manifest | **load-bearing** |
| **other DW subtrees** | acceleration, swarm_expansion, spawn_dispatch, semantic_alias, etc. | ~60M | — | Swarm/queue/spawn operational drafts and wave receipts | **mixed** / mostly **process-exhaust** |

**Sampled `terminal_workers` evidence (confirms process receipts):**

- `LATEST_20_CODEX_CLI_TERMINAL_WORKERS.candidate.json` — pointer to active run manifest (`terminal_20_codex_cli_mount_fresh_20260610T030545Z`).
- `TERMINAL20_USAGE_LIMIT_RESET_TIMESTAMP_GATE_20260610T064948Z.candidate.json` — maintainer gate receipt referencing `ion_domain_weaver_terminal_worker_maintainer.py`, `last_tick_path`, authority ceilings.
- `terminal_20_codex_cli_20260610T021002Z/MISSION_031_FIRST_PULSE_STATUS_20260611T051446Z.candidate.md` — seat-level mission attempt inventory (`MISSION_031_ATTEMPT_*`, `not_executed`, `no_start` proofs).
- Kernel binds: `ion_domain_weaver_terminal_worker_maintainer.py` → `LATEST_20_CODEX_CLI_TERMINAL_WORKERS.candidate.json`; `ion_codex_cli_launch_variant_probe.py` → `terminal_workers/codex_cli_launch_variant_forensics/`.

### 1C. `current/` — carrier / agent / runtime lanes

| Category | Path | Size | ~Files | One-line description | Verdict |
|----------|------|------|--------|----------------------|---------|
| **codex_agent_mounts** | `…/codex_agent_mounts/` | 48M | 4,879 | 122 role mount dirs; 115 `ION_AGENT_MOUNT_MANIFEST.json`; registry write targets | **load-bearing** |
| **chatgpt_connector** | `…/chatgpt_connector/` | 69M | 4,668 | ChatGPT-browser/Codex connector runtime, queues, context packages | **load-bearing** |
| **codex_solo** | `…/codex_solo/` | 52M | 910 | Shared lead/fallback witness lane (registry + domain.ion_system_definition refs) | **load-bearing** (witness) |
| **worker_shift** | `…/worker_shift/` | 45M | 1,531 | Worker Shift lease board (`ACTIVE_WORKER_SHIFT_BOARD.json`) | **load-bearing** |
| **codex_cli** | `…/codex_cli/` | 64M | 6,531 | Generated Codex CLI mount/work artifacts | **mixed** |
| **codex_carrier** | `…/codex_carrier/` | 98M | 29 | Codex carrier sync lane (large sparse files) | **mixed** |
| **project_launcher** | `…/project_launcher/` | 172M | 2,167 | Project launch run receipts | **mixed** |
| **execution_cycles** | `…/execution_cycles/` | 33M | 2,099 | Execution-cycle run receipts | **process-exhaust** |
| **runtime_services** | `…/runtime_services/` | 1.6M | 352 | Test/run receipts referenced by MCP branch registry | **load-bearing** |
| **agent_comms** | `…/agent_comms/` | 7.5M | 380 | Communication directory + comms receipts | **load-bearing** |
| **browser_gpt_dom_profiles** | `…/browser_gpt_dom_profiles/` | 27M | 1,294 | DOM health/selector profiles for browser MCP lane | **load-bearing** |
| **action_surface_cartography** | `…/action_surface_cartography/` | 244K | — | MCP action navigation index / branch plans | **load-bearing** |
| **gemini_ion_sandboxes** | `…/gemini_ion_sandboxes/` | 4.0M | 14 | Disposable Gemini carrier sandbox copies (registry: no active repo mutation) | **process-exhaust** |
| **portable_agent_domain_packages** | `…/portable_agent_domain_packages/` | 15M | 713 | Timestamped portable agent/GPT drop-in snapshots w/ embedded `source_refs` | **mixed** / duplicate |
| **ion_system_definition** | `…/ion_system_definition/` | 224K | 17 | North Star / IONOLOGIST live lane (`.ion/`, North Star, Derived Account) | **load-bearing** |
| **ACTIVE_* root artifacts** | `…/current/ACTIVE_*.json`, large view models | ~60M | — | Live queues, cockpit view models, carrier packets, onboarding | **load-bearing** |
| **codex_capsule_chat** | `…/codex_capsule_chat/` | 28M | 416 | Capsule chat archive attachments | **mixed** |
| **repo_organization / reports / forensic** | various small dirs | ~20M | — | Audits, repo org drafts, forensic snapshots | **process-exhaust** |

---

## 2. Reclaimable estimate

### High-confidence pure process exhaust (within `ION/05_context`)

| Win | Est. GB | Evidence |
|-----|---------|----------|
| `domain_weaver/terminal_workers` mission/seat/attempt bulk | **~4.65–4.70** | 4.7G dir; 11,703 files; sampled files are gate/status/attempt receipts |
| `execution_cycles` | **~0.03** | 33M, 2,099 files |
| `comms` + `history` + stale `inbox` | **~0.005** | ~4.5M combined |
| `gemini_ion_sandboxes` | **~0.004** | 4M disposable sandboxes |
| Nested `ION/ION/` residue | **~0.0005** | 548K; `REPO_AUTHORITY.md` explicitly labels non-runnable |

**Conservative subtotal (`05_context` only): ~4.7 GB** (~81% of all `05_context`).

### Moderate-confidence (grep + manifest verification before move)

| Win | Est. GB | Notes |
|-----|---------|-------|
| `live_carrier_binding` historical proof rows (retain `ACTIVE_*` + kernel-bound paths) | **~0.15–0.20** | 220M total; kernel reads `ACTIVE_INVOKABLE_BINDING_PROOF_ROWS.candidate.json` |
| `project_launcher` completed runs | **~0.10–0.15** | 172M mixed |
| `codex_cli` stale generated mounts | **~0.04–0.06** | 64M mixed |
| `full_steam_push` + other DW wave receipts | **~0.02–0.04** | ~80M mixed |
| Large regenerated view models (e.g. `ACTIVE_COCKPIT_VIEW_MODEL.json` 22M) | **~0.02** | verify no registry bind before move |

**Moderate subtotal (additional): ~0.3–0.5 GB**  
**Combined reclaimable (with verification): ~5.0–5.2 GB of 5.8 GB `05_context`**

### Outside `05_context` but same duplication class

| Win | Est. GB | Notes |
|-----|---------|-------|
| `ION_EXPORTS_LOCAL/codex_carrier_transfer/` | **~0.61** | 606M; two near-duplicate carrier-transfer result trees |
| `projects/Cosmos/…/ION_MINIMUM_VIABLE_AGENCY_DOMAIN_SPINE_*` | **~0.03** | 29M portable spine w/ embedded partial kernel copies |
| `ION/06_intelligence/orchestration/custom_gpt/` | **~0.03** | 29M; includes `04_packages/kernel` snapshot (4.8M) |

**Repo-wide exhaust + duplication (incl. exports): up to ~5.9 GB** if all proposed moves executed after safety checks.

---

## 3. Duplication findings

### 3A. `ion_domain_weaver.py` copies

`find . -name ion_domain_weaver.py` → **4 instances**:

| # | Path | Size (`du -sh`) | Role |
|---|------|-----------------|------|
| 1 | `ION/04_packages/kernel/ion_domain_weaver.py` | (in 39M kernel dir) | **Canonical** |
| 2 | `ION_EXPORTS_LOCAL/…/234707Z/…/kernel/ion_domain_weaver.py` | 2.6M | Export overlay duplicate |
| 3 | `ION_EXPORTS_LOCAL/…/235034Z/…/kernel/ion_domain_weaver.py` | 2.6M | Export overlay duplicate |
| 4 | `ION/05_context/current/gemini_ion_sandboxes/…/kernel/ion_domain_weaver.py` | 2.5M | Sandbox partial copy |

**Duplicate count outside canonical: 3 files (~7.7M file-level du; same monolith content class).**

### 3B. `04_packages/kernel/` directory copies

`find . -type d -path '*/04_packages/kernel'` → **11 directories**:

| Location | Size | Files | vs canonical (39M / 1020 files) |
|----------|------|-------|----------------------------------|
| `ION/04_packages/kernel/` | 39M | 1020 | **Canonical** |
| `ION_EXPORTS_LOCAL/…/234707Z/…/kernel/` | 17M | 464 | Near-full overlay snapshot |
| `ION_EXPORTS_LOCAL/…/235034Z/…/kernel/` | 17M | 464 | Near-full overlay snapshot (differs slightly from sibling) |
| `ION/06_intelligence/…/ION_CUSTOM_GPT_CARRIER_PACKAGE_v2_6_…/kernel/` | 4.8M | 263 | Custom-GPT packaging snapshot |
| `ION/05_context/current/gemini_ion_sandboxes/…/kernel/` | 3.7M | 4 | Partial sandbox stub |
| `projects/Cosmos/…/portable_agent_domain_packages/…/source_refs/ION/04_packages/kernel/` (×4) | ~2.4M+324K each | 96+4 each | Embedded portable-package refs |
| `ION/05_context/current/portable_agent_domain_packages/…/source_refs/ION/04_packages/kernel/` (×2) | 176K–360K | 2–4 | Partial embedded refs |
| `projects/WaterPRO/…/Needs_Routed/ION/04_packages/kernel/` | 4K | 0 | Empty stub |

**Redundant storage outside canonical kernel (approx.):**

- Near-full duplicates: **~34M** (two export overlays) + **~4.8M** (custom GPT) + **~3.7M** (sandbox) + **~5M** (Cosmos portable refs) ≈ **~47M / ~1,300 files**
- **Export bundle duplication:** two `ION_CODEX_CARRIER_TRANSFER_*` trees under `ION_EXPORTS_LOCAL` (~606M combined lane; kernels alone 34M)
- **`diff -rq` sample:** export kernels differ on at least `ion_codex_carrier_transfer_package.py` — not bit-identical, but functionally redundant overlay class

### 3C. Nested `ION/ION/` tree

| Path | Size | Files | Nature |
|------|------|-------|--------|
| `ION/ION/` | 548K | 32 | Embedded `05_context/…/full_steam_push/…/returns/lanes/*` residue |

`REPO_AUTHORITY.md` §Nested packaged-path correction: **not a second runnable root** — archive-class residue.

### 3D. Parallel architecture lanes (outside `05_context`, product-spine relevant)

| Path | Size | Files | Notes |
|------|------|-------|-------|
| `ION/02_architecture/` | 1.9M | 339 | Canonical mount contract / architecture docs |
| `ION/02_architecture_monolith/` | 1.2M | 1 | Monolith-era parallel tree (1 file — likely aggregated) |

Not byte-duplicates of each other; **organizational duplication** to resolve during production-spine extraction, not bulk archival.

### 3E. Package / mount snapshot duplication

- **`portable_agent_domain_packages/`** (15M, 713 files): timestamped drop-ins with embedded `source_refs` copies of registry/context slices.
- **`codex_agent_mounts/`** (48M): live mounts — not duplicates of `04_packages`, but **per-role context materialization** that mirrors registry/domain surfaces.
- **`custom_gpt` packaging** under `ION/06_intelligence/` (29M): historical carrier package snapshots.

---

## 4. Load-bearing exceptions — MUST NOT blind-archive

These paths are bound by manifests, registry YAML, kernel constants, or North Star continuity. **Preserve unless a future move pass rewrites references.**

### 4A. Always preserve (explicit)

| Path | Bound by |
|------|----------|
| `ION/05_context/current/ion_system_definition/` (incl. `.ion/`, `AGENTS.md`, North Star, Derived Account, `PRODUCTION_SPINE_AUDIT/`) | `ION_CONTEXT_CAPSULE.yaml`, `domain.ion_system_definition.domain.yaml`, Living Encyclopedia manifest |
| `ION/05_context/current/codex_agent_mounts/` (active mounts + manifests) | `ion_action_mcp_branch_leader_registry.yaml`, kernel Worker Shift lease targets |
| `ION/05_context/signals/` (manifest-referenced receipts) | `ION_LIVING_ENCYCLOPEDIA_MANIFEST_V100.json`, MCP tool policy |
| `ION/05_context/archive/containment/V123_ROOT_ONBOARDING_SHIMS/…` | `REPO_AUTHORITY.md` historical disposition |
| `ION/05_context/current/ION_LIVING_ENCYCLOPEDIA_MANIFEST_V100.json` | Self-referential manifest spine |

### 4B. Domain weaver — load-bearing subset

| Path | Bound by |
|------|----------|
| `…/domain_weaver/DOMAIN_WEAVER_PROJECTION.json` | Living Encyclopedia manifest; MCP registry `large_projection_path`; kernel projection refresh |
| `…/domain_weaver/PROMOTION_REVIEW.json`, `PROMOTION_GATE.json` | Living Encyclopedia manifest |
| `…/domain_weaver/operator_actions/` (referenced settlement JSON) | Living Encyclopedia manifest |
| `…/domain_weaver/validation/` (referenced validation result) | Living Encyclopedia manifest |
| `…/domain_weaver/live_carrier_binding/ACTIVE_INVOKABLE_BINDING_PROOF_ROWS.candidate.json` | `ion_domain_weaver_projection_refresh_candidate.py`, `ion_domain_weaver_self_evolution_readiness.py`, `ion_agent_observatory.py` |
| `…/domain_weaver/live_carrier_binding/ACTIVE_*` proof rows/schemas | Kernel observatory `_recent_files` scans |
| `…/domain_weaver/.ion/ION_CONTEXT_CAPSULE.yaml` | Sampled terminal-worker receipts (`context_source`) |
| `…/domain_weaver/terminal_workers/LATEST_20_CODEX_CLI_TERMINAL_WORKERS.candidate.json` | `ion_domain_weaver_terminal_worker_maintainer.py` `LATEST_POINTER` |
| `…/domain_weaver/terminal_workers/codex_cli_launch_variant_forensics/` | `ion_codex_cli_launch_variant_probe.py` `BASE_PROBE_DIR` |
| Active terminal run dirs referenced by `LATEST_*` / maintainer `last_tick_path` | Kernel maintainer tick chain |

### 4C. Carrier / runtime — load-bearing

| Path | Bound by |
|------|----------|
| `…/current/ACTIVE_*.json` (queues, packets, onboarding, carrier state) | MCP tool policy, branch leader registry |
| `…/chatgpt_connector/` | Branch leader registry root path; MCP connector contract |
| `…/codex_solo/` (`HOT_CONTEXT.md`, `CAPSULE.md`, `ROUTE.json`, history) | Registry + `domain.ion_system_definition` witness ref |
| `…/worker_shift/` (`ACTIVE_WORKER_SHIFT_BOARD.json`) | Registry lease verification for projection/mount writes |
| `…/runtime_services/receipts/`, `test_run_receipts/` | Registry receipt_dir targets |
| `…/agent_comms/` | Registry comms surfaces |
| `…/browser_gpt_dom_profiles/` | MCP tool policy + connector handlers |
| `…/action_surface_cartography/` | MCP branch leader registry |
| `…/context_settlement/accepted/` | Registry settlement replay receipt |
| `…/workspace_roots/` | Registry spawn run target template |

### 4D. Registry-cited but lower-risk to trim (still verify first)

- `…/domain_weaver/swarm_expansion/` — registry `root_path` for one handler (do not remove root; may trim old wave artifacts after grep)
- `…/artifact_transfer/`, `…/project_workbench/` — cited as read surfaces
- `…/codex_capsule_chat/archive_attachments/` — cited attachment store

---

## 5. Proposed archival plan (PROPOSAL ONLY — nothing moved)

### 5A. Target layout (candidate)

```
/home/sev/ION_ARCHIVE/                          # external to product tree (preferred)
  2026-06-17_exhaust_candidate/
    05_context/
      domain_weaver/terminal_workers/           # bulk receipts
      domain_weaver/live_carrier_binding/       # non-ACTIVE rows only
      execution_cycles/
      comms/ history/ inbox/completed/
    exports/
      codex_carrier_transfer/                   # after operator confirms which bundle is canonical
    sandboxes/
      gemini_ion_sandboxes/
    nested_residue/
      ION_ION/                                  # from ION/ION/
    snapshots/
      portable_agent_domain_packages/           # older timestamps only
      custom_gpt_v2_6/                          # from 06_intelligence
```

In-repo fallback (if external archive unavailable): `ION/05_context/archive/2026-06-17_exhaust_candidate/` — **still outside `current/` hot lane**.

### 5B. Sequencing (future operator pass)

1. **Freeze & inventory** — snapshot this catalog; record `LATEST_*` pointers and `ACTIVE_*` paths.
2. **Reference grep pass** — for each candidate subtree, run repo-wide path grep before any move (see §5C).
3. **Phase 1 — pure exhaust (lowest risk)** — `terminal_workers` bulk **excluding** LATEST pointer, forensics dir, and last-tick chain; `execution_cycles`; `comms/history`; completed `inbox`; `gemini_ion_sandboxes`; `ION/ION/`.
4. **Phase 2 — verified mixed exhaust** — `live_carrier_binding` non-`ACTIVE_*` rows; old `project_launcher` runs; stale `codex_cli` mounts; DW wave folders (`full_steam_push` returns).
5. **Phase 3 — duplication dedup (not archival)** — collapse duplicate `ION_EXPORTS_LOCAL` transfer results to one retained bundle; dedupe portable package timestamps; **do not delete canonical kernel**.
6. **Phase 4 — product-spine separation** — resolve `02_architecture` vs `02_architecture_monolith` organizationally (separate audit: `MONOLITH_SEAM_AUDIT`).

### 5C. Pre-move safety checks (mandatory grep targets)

Before moving any path `P`, run from active root:

```bash
# 1. Repo-wide path reference scan
rg -F "P" ION/ pyproject.toml projects/ --glob '!**/archive/**'

# 2. Kernel hard-coded binds (terminal workers, live binding)
rg -F "terminal_workers" ION/04_packages/kernel/
rg -F "live_carrier_binding" ION/04_packages/kernel/

# 3. Manifest / registry binds
rg -F "P" ION/05_context/current/ION_LIVING_ENCYCLOPEDIA_MANIFEST_V100.json
rg -F "P" ION/03_registry/
rg -F "P" ION/REPO_AUTHORITY.md

# 4. Active pointer chain
cat ION/05_context/current/domain_weaver/terminal_workers/LATEST_20_CODEX_CLI_TERMINAL_WORKERS.candidate.json
```

**Post-move (future):** update any stale pointers in receipts only if operators choose rewrite; prefer leaving receipt paths immutable and adding archive redirect notes in ledger.

### 5D. Top 3 archival moves (highest GB, lowest bind risk after checks)

| Rank | Move candidate | Est. GB | Pre-check |
|------|----------------|---------|-----------|
| **1** | `domain_weaver/terminal_workers/` bulk receipts (retain LATEST + forensics + last-tick chain) | **~4.65** | Kernel `LATEST_POINTER`; maintainer `last_tick_path` |
| **2** | `ION_EXPORTS_LOCAL/codex_carrier_transfer/` duplicate bundle (keep one result tree) | **~0.30–0.61** | Operator confirms which transfer is authoritative |
| **3** | `execution_cycles/` + stale `comms/` + `history/` + completed `inbox/` | **~0.04** | Registry MCP policy lists `inbox/` — grep before move |

---

## 6. Sampling log

| File sampled | Confirmed nature |
|--------------|------------------|
| `terminal_workers/TERMINAL20_USAGE_LIMIT_RESET_TIMESTAMP_GATE_*.json` | Maintainer gate receipt w/ authority ceilings, code refs |
| `terminal_workers/…/MISSION_031_FIRST_PULSE_STATUS_*.md` | Seat/mission attempt status rollup |
| `terminal_workers/…/TERMINAL32_ADD12_BLOCKER_REPAIR_*.md` | Launch enablement process receipt |
| `live_carrier_binding/ACTIVE_INVOKABLE_BINDING_PROOF_ROWS.candidate.json` | Live binding proof table consumed by kernel |
| `gemini_ion_sandboxes/…/kernel/` (4 files) | Partial sandbox kernel stub |

---

## 7. Continuity note

This audit is a **candidate proposal** under `PRODUCTION_SPINE_AUDIT/`. It does not ratify archival actions. Next operator step: choose Phase 1 scope, run §5C greps, then execute moves outside the product hot path — **not in this read-only pass**.
