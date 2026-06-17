# Domain Weaver Core Reality (candidate)

**Status:** candidate / read-only analysis — **PROPOSAL ONLY**  
**Authority:** not-accepted-state; no production-readiness claims; nothing moved, renamed, archived, or deleted.  
**Active root:** `/home/sev/ION - Production/ION_Developement`  
**Audited:** 2026-06-17  
**Scope:** What Domain Weaver (DW) **is today**, what state it owns, how kernel runtime modules integrate around it, evolution vs `ION_VNEXT`, and subsumption overlap.

---

## Executive scale (active-truth)

| Surface | Measure | Notes |
|---------|---------|-------|
| DW monolith | **49,513** lines | `ION/04_packages/kernel/ion_domain_weaver.py` (`wc -l`) |
| DW satellite modules | **38** files, **38,371** lines | `ion_domain_weaver_*.py` excluding monolith |
| DW constellation total | **87,884** lines | monolith + satellites |
| Kernel files mentioning `domain_weaver` | **56** `.py` files | `rg -l domain_weaver ION/04_packages/kernel/` |
| Kernel files importing `ion_domain_weaver*` | **31** files | includes 22 DW modules + 9 non-DW consumers |
| `05_context/current/domain_weaver/` | **329M**, **14,404** files | `du -sh`; `find … -type f \| wc -l` |
| Sibling `worker_shift/` (consumed, not owned) | **45M**, **1,531** files | read by DW orchestrator reducer |

---

## 1. DW constellation inventory

### 1A. Kernel modules — monolith + satellites

| Module | Lines | One-line role |
|--------|-------|---------------|
| `ion_domain_weaver.py` | 49,513 | Operational domain/agent projection joiner; 107 operator actions; materializes projection, promotion gates, dogfood capsule; `execute_domain_weaver_action` dispatcher (~L40574–49513) |
| `ion_domain_weaver_swarm_control_plane.py` | 11,330 | Swarm control-plane synthesis (round-table, fanout/fanin, standing operations) |
| `ion_domain_weaver_projection_refresh_candidate.py` | 2,026 | Candidate-only accepted projection refresh evidence and apply paths |
| `ion_domain_weaver_spawn_request_dispatcher.py` | 1,905 | Lead-side dispatcher for worker-local spawn requests under `spawn_dispatch/` |
| `ion_domain_weaver_context_active_resolver.py` | 1,896 | No-write active context resolver — mount/lane binding gate for worker starts |
| `ion_domain_weaver_terminal_worker_maintainer.py` | 1,737 | Maintains standalone Codex CLI terminal worker fleet; binds `LATEST_20_CODEX_CLI_TERMINAL_WORKERS` pointer |
| `ion_domain_weaver_need_based_expansion.py` | 1,588 | Need-based domain/agent expansion planning and context materialization |
| `ion_domain_weaver_semantic_alias_canonicalization.py` | 1,548 | Candidate semantic-alias canonicalization and supervised projection/mount rewrites |
| `ion_domain_weaver_self_repair_supervisor.py` | 1,311 | Read-only self-repair supervisor; worker-shift/capacity/queue hygiene preflights |
| `ion_domain_weaver_worker_start_readiness.py` | 1,231 | Read-only worker-start readiness projection and backlog hygiene |
| `ion_domain_weaver_self_evolution_readiness.py` | 1,046 | Self-evolution readiness projection over route/topology gates |
| `ion_domain_weaver_route_gate_matrix.py` | 903 | Candidate route-gate matrix for self-evolution readiness |
| `ion_domain_weaver_monolith_index.py` | 840 | AST-backed navigation index for the 49K-line monolith (does not execute it) |
| `ion_domain_weaver_proposal_wave.py` | 801 | Proposal-write swarm planning |
| `ion_domain_weaver_true_names.py` | 732 | Candidate true-name and role-tier identity helpers for workers/domains |
| `ion_domain_weaver_pressure_wave.py` | 687 | Pressure-wave planning over scarce native Codex slots |
| `ion_domain_weaver_orchestrator_blocker_router.py` | 639 | Read-only blocker routing for orchestration (worker-shift, round-table fanin) |
| `ion_domain_weaver_packet_templates.py` | 574 | Pure packet/template construction (work requests, next-packet, source-seam) |
| `ion_domain_weaver_worker_context_lanes.py` | 556 | Per-worker context lane definitions |
| `ion_domain_weaver_exact_start_gate.py` | 527 | Exact-path gate for spawn-dispatch main test |
| `ion_domain_weaver_orchestrator_state_reducer.py` | 512 | Read-only orchestrator state reducer — folds projection + worker_shift + round-table fanin |
| `ion_domain_weaver_round_table_request_emission.py` | 508 | Fresh exact-only round-table request emission |
| `ion_domain_weaver_orchestrator_domain_agent_router.py` | 441 | Read-only domain/agent route bindings for orchestration |
| `ion_domain_weaver_orchestrator_return_fanin_index.py` | 434 | Read-only return and fan-in index |
| `ion_domain_weaver_round_table_return_lint.py` | 417 | Semantic lint for standing round-table returns |
| `ion_domain_weaver_queue_governance.py` | 416 | Pure queue-governance helper seam (duplicate classification, ledger rows) |
| `ion_domain_weaver_dynamic_expansion_promotion.py` | 408 | Candidate dynamic domain expansion promotion drafts |
| `ion_domain_weaver_larger_fanout_control.py` | 403 | Read-only larger-fanout control-plane readiness |
| `ion_domain_weaver_context_catalog.py` | 403 | Read-only context catalog for Codex workbench / browser MCP chat binding |
| `ion_domain_weaver_continuous_ops.py` | 382 | Candidate dry-run supervisor for queue operations |
| `ion_domain_weaver_exact_start_readiness_dry_run.py` | 378 | Read-only exact request start-readiness dry run |
| `ion_domain_weaver_materialization_pointers.py` | 353 | Pure no-write materialization pointer helpers |
| `ion_domain_weaver_projection_records.py` | 300 | Deterministic projection-record helpers |
| `ion_domain_weaver_orchestrator_signal_ledger.py` | 280 | Read-only approval/question/stale-notice ledger for orchestrator |
| `ion_domain_weaver_run_return_backfill_apply.py` | 264 | Gated run-return alias backfill for accepted Codex queue runs |
| `ion_domain_weaver_io.py` | 258 | Leaf IO/hash/path helpers |
| `ion_domain_weaver_second_limited_wave.py` | 208 | Read-only second limited exact-path wave preview |
| `ion_domain_weaver_semantic_ids.py` | 112 | Read-time semantic ID normalization |
| `ion_domain_weaver_catalog.py` | 17 | Leaf static schema/catalog constants |

**Monolith path registry (active-truth):** root constants at `ion_domain_weaver.py` L339–514 define `DOMAIN_WEAVER_ROOT`, `DOMAIN_WEAVER_PROJECTION_PATH`, promotion artifacts, queue-governance dirs, live-carrier-binding dirs, activation plane, swarm-evolution ledgers, etc.

### 1B. DATA/STATE surfaces under `ION/05_context/current/domain_weaver/`

| Surface | Size / count | Role | DW write? |
|---------|--------------|------|-----------|
| **projection** | `DOMAIN_WEAVER_PROJECTION.json` **1.3M** (mtime 2026-06-04); dir `projection_refresh/` **5.5M** | Machine-readable domain/agent weave map consumed by control plane, mounts, cockpit | **yes** — `materialize_domain_weaver_projection` (`ion_domain_weaver.py` L38981+) |
| **promotion gates** | `PROMOTION_GATE.json` **22K**, `PROMOTION_REVIEW.json/md`, `promotion_drafts/` **44K** | Steward/operator promotion review and gate artifacts (`accepted_state_count: 0` per sibling audit — witness) | **yes** — `materialize_domain_weaver_promotion_*` (L40337+) |
| **terminal_workers** | **4.0M**, **536** files | Codex CLI terminal fleet manifests, seat/mission attempt receipts, maintainer gate pointers | **yes** — maintainer + spawn/dispatch lanes write receipts; bulk is process exhaust |
| **live_carrier_binding** | **220M**, **8,201** files | Invocable binding proof rows, fanin settlement monitors, hydration proofs | **yes** — monolith paths L489–514; kernel reads `ACTIVE_INVOKABLE_BINDING_PROOF_ROWS` |
| **worker_shift** | *(sibling)* `../worker_shift/` **45M**, **1,531** files | Lease board — **not owned by DW** but required input to orchestrator reducer | **read-only** for DW — `ACTIVE_WORKER_SHIFT_BOARD.json` consumed at `ion_domain_weaver_orchestrator_state_reducer.py` L29, L332 |
| **operator_actions** | **3.5M**, **623** files | Bounded operator action receipts from cockpit/MCP dispatch | **yes** — written by `execute_domain_weaver_action` branches |
| **validation** | **40K**, **3** files | Validation gate artifacts | **yes** — promotion/refresh validation lanes |
| **receipts** | **6.3M**, **828** files | Apply/validation/maintenance receipts | **yes** |
| **orchestrator_experience** | **18M** under `operator_experience/` | Orchestrator gate settlements, recovery indexes, UX drafts | **yes** — `ion_orchestrator_actions.py` writes under `operator_experience/orchestrator_*` |
| **spawn_dispatch** | **2.2M** | Spawn request materialization and start plans | **yes** — `ion_domain_weaver_spawn_request_dispatcher.py` |
| **queue_governance** | **2.4M** | Duplicate-group ledgers, lifecycle backfill | **yes** |
| **context capsule** | `.ion/ION_CONTEXT_CAPSULE.yaml`, `AGENTS.md`, `dogfood_context_capsule/` | Folder-local working capsule for DW seat | **yes** — materialization actions |
| **monolith_index** | **1.4M** | Generated navigation index (`DOMAIN_WEAVER_MONOLITH_INDEX.latest.json`) | **witness** — index of monolith, not runtime authority |

**Other DW subtrees (mixed / mostly process-exhaust):** `full_steam_push/` 26M, `semantic_alias_canonicalization/` 5.5M, `swarm_expansion/` 2.7M, `founding_domain_swarm/` 1.7M, `continuous_operations/` 2.0M, plus ~60 smaller mission lanes (see exhaust catalog §1B).

### 1C. Signals DW emits (active-truth)

DW does **not** write to `ION/05_context/signals/` (`rg '05_context/signals' ion_domain_weaver*.py` → no matches). Signals are **artifact-local**:

| Signal class | Emitter | Sink path pattern |
|--------------|---------|-------------------|
| Operator action results | `execute_domain_weaver_action` | `domain_weaver/operator_actions/`, action-specific subdirs |
| Orchestrator receipts | `ion_orchestrator_actions.py` | `domain_weaver/operator_experience/orchestrator_*` |
| Live binding monitors | monolith live-carrier paths | `live_carrier_binding/*RETURN_MONITOR*`, `*FANIN_SETTLEMENT*` |
| Terminal worker ticks | `ion_domain_weaver_terminal_worker_maintainer.py` | `terminal_workers/LATEST_20_*`, run-scoped seat receipts |
| Projection refresh | `ion_domain_weaver_projection_refresh_candidate.py` | `projection_refresh/`, `projection_refresh_candidates/` |
| Orchestrator signal ledger | `ion_domain_weaver_orchestrator_signal_ledger.py` | in-memory/read from operator_experience artifacts |
| Cockpit/MCP JSON responses | `ion_local_cockpit_app.py`, `ion_chatgpt_browser_mcp_http_preview.py` | HTTP response bodies (not persisted unless action writes) |

---

## 2. Integration / centrality map

**Dependency direction convention:** `consumer → DW` means the listed module imports or calls DW; DW does not import those consumers for the same concern.

### 2A. Assigned runtime modules

| Module | DW dependency | Direction | Evidence (file:line) |
|--------|---------------|-----------|----------------------|
| `ion_agent_control_plane` | `build_domain_weaver_projection`; `ion_domain_weaver_true_names` identity helpers; hard-coded resolver/readiness module refs | **→ DW** | imports L32–40; projection call L1096–1098; module refs L127–128, L805–806 |
| `ion_automation_control_plane` | Path constants + five `materialize_domain_weaver_*` writers (projection, promotion review/gate, dogfood capsule, steward ready review) | **→ DW** | imports L22–32; materialize calls L390–421; path refs L217–272 |
| `ion_orchestrator_actions` | `build_domain_weaver_orchestrator_state`; `resolve_domain_active_context`; lazy `build_domain_weaver_worker_start_readiness`; writes under `domain_weaver/operator_experience/` | **→ DW** | imports L12–13; resolver L1113, L1143; state L1596; worker readiness L992–994 |
| `ion_local_cockpit_app` | `execute_domain_weaver_action` HTTP handler | **→ DW** | import L82; routes `/cockpit/domain-weaver/action`, `/cockpit/weave/action` L1654–1659 |
| `ion_codex_queue_runner` | `resolve_domain_active_context` at worker-start context gate | **→ DW** | import L49; gate call L6298–6303 |
| `ion_cursor_queue_runner` | **none** | — | `rg domain_weaver\|worker_shift\|context_active ion_cursor_queue_runner.py` → no matches |
| `ion_codex_agent_mount` | Reads `DOMAIN_WEAVER_PROJECTION_PATH`, promotion review paths; embeds pointers in mount manifests and AGENTS.md prose | **→ DW (read-only paths)** | imports L29–33; manifest refs L204–206, L736–737; AGENTS guidance L331–332, L413–414 |
| `ion_chatgpt_browser_mcp_http_preview` | `execute_domain_weaver_action`; `build_domain_weaver_context_catalog` | **→ DW** | imports L82–83; catalog L5508; action dispatch L6233 |
| `ion_agent_invocation_broker` | `resolve_domain_active_context` with lane fallback | **→ DW** | import L32; resolution L372–377; fallback L383–388 |

### 2B. Adjacent hubs (not in assignment list but load-bearing)

| Module | Role |
|--------|------|
| `ion_runtime_service_control.py` | **29** lazy imports of DW satellite builders (spawn, pressure wave, need-based expansion, projection refresh, semantic alias apply, round-table, self-repair) — L4010–5220 |
| `ion_cockpit_view_model.py` | Reads `DOMAIN_WEAVER_PROJECTION.json` directly (L83, L127–165) — no Python import of monolith, but UI spine depends on DW artifact |
| `ion_build_workspace_model.py`, `ion_agent_observatory.py`, `ion_steward_dispatcher.py` | String/path references to `domain_weaver/` artifacts |

### 2C. Centrality verdict

**Yes — DW is the de-facto runtime spine for domain/agent orchestration, context-active gating, and operator weave actions** (confidence **high**, caveats §5).

Evidence chain:

1. **Single projection truth:** `build_domain_weaver_projection` (`ion_domain_weaver.py` L37788+) feeds agent control plane (L1096) and is the artifact mounts and cockpit read (`DOMAIN_WEAVER_PROJECTION.json`).
2. **Worker-start gate:** Codex queue runner blocks starts without `resolve_domain_active_context` (L6298); invocation broker uses same resolver (L372).
3. **Operator dispatch surface:** 107 monolith actions via `execute_domain_weaver_action` (L40574); exposed on cockpit (L1654) and browser MCP (L6233).
4. **Orchestrator lane:** `ion_orchestrator_actions.py` schema IDs are all `ion.domain_weaver.main_orchestrator_*` (L19–34); state reducer reads DW projection + worker_shift + round-table fanin.
5. **Automation maintenance:** bounded writes for projection/promotion/dogfood flow through DW materializers exclusively (`ion_automation_control_plane.py` L390–421).

**Exception:** `ion_cursor_queue_runner.py` has **no DW coupling** — Cursor carrier path is parallel, not DW-gated today.

---

## 3. Evolution timeline

### 3A. Git history (this repo snapshot)

| Target | Git result | Classification |
|--------|------------|----------------|
| `ion_domain_weaver.py` + sample satellites | **One** commit: `2026-06-05 work: add active ION source packet` | **active-truth** (git) — history compressed/squashed in this checkout |
| `ION_VNEXT/` | Last commit **`2026-05-21`** `R0033: Promote ION_VNEXT promotion plan core layer`; prior `R0024`–`R0032` May 19–20 promotion layers | **active-truth** (git) |
| File mtimes | Monolith **2026-06-04**; `DOMAIN_WEAVER_PROJECTION.json` **2026-06-04** | **active-truth** (filesystem) |

**Caveat:** Per-file `git log --follow` cannot reconstruct DW's organic growth in this repo — the active ION source packet import collapsed history. Timeline below blends git (vNext), mtimes, and receipt witnesses.

### 3B. Witness timeline (receipts / mission artifacts)

| Era | Representative subjects / artifacts | Source |
|-----|--------------------------------------|--------|
| **2026-05-19–21** | `R0024: Land ION_VNEXT M31 dependency-closed control promotion`; `R0026: Bind ION_VNEXT front door to canon`; `R0030–R0033` receipt/context/promotion-plan core layers | git / **witness** |
| **2026-06-01–04** | `PROMOTION_GATE.json` mtime Jun 1; projection + monolith mtime Jun 4 | filesystem **active-truth** |
| **2026-06-05** | Bulk kernel/context land: `work: add active ION source packet` | git **active-truth** |
| **2026-06-07–09** | Round-table second wave, exact-start readiness, orchestration blocker index (`DOMAIN_WEAVER_SECOND_WAVE_*`, `ORCHESTRATION_SYSTEM_CURRENT_BLOCKER_INDEX_*`) | receipt paths cited in `ion_domain_weaver_orchestrator_blocker_router.py` L36–156 — **witness** |
| **2026-06-10–11** | Terminal-20 Codex CLI fleet (`terminal_20_codex_cli_*`); seat_11 Atlas vNext front-door missions (`MISSION_029–038`, `vnext_contract_delta`, `vnext_next_wave`) | exhaust catalog §1B; mount receipts — **witness** |
| **2026-06-12–17** | Live carrier binding repair fanin settlements (`EXACT_ACTIVE_SPECIALIST_BINDING_KERNEL_REPAIR_*` snapshots) | `live_carrier_binding/snapshots/` — **active-truth** (filesystem listing) |

### 3C. When DW became integral

**Working conclusion (witness + integration, medium-high confidence):**

- **ION_VNEXT stopped evolving in git on 2026-05-21** while **`ION/04_packages/kernel` DW code and `05_context/current/domain_weaver/` continued through June 2026**.
- **Inflection ~2026-06-07–11:** round-table orchestration, terminal worker fleet, spawn dispatch, and Atlas vNext missions **execute inside DW context** (`domain_weaver/terminal_workers/`, `domain_weaver/.ion/receipts/seat_11_mission*`) rather than extending `ION_VNEXT/03_products` or `04_carriers`.
- Operator-established ordering (**ION_VNEXT before Domain Weaver conceptually; DW built afterward**) aligns with: vNext skeleton first (May), DW operational mass and kernel coupling second (June).

---

## 4. Subsumption — DW vs ION_VNEXT parallel machinery

| Concern | DW module(s) / artifact(s) today | ION_VNEXT / parallel artifact | Relationship |
|---------|----------------------------------|-------------------------------|--------------|
| **Domain weaving / expansion** | `build_domain_weaver_projection` (L37788); `ion_domain_weaver_need_based_expansion.py`; `ion_domain_weaver_dynamic_expansion_promotion.py`; `DOMAIN_WEAVER_PROJECTION.json` | `ION_VNEXT/06_context/domain_weave/` (README + dry-run YAML); `ion_agent_control_plane.py` still points `DOMAIN_WEAVE_*` at vNext paths L46–51 | **DW subsumes operationally** — vNext weave map is witness; live projection is DW |
| **Promotion / projection governance** | `materialize_domain_weaver_promotion_*`; `PROMOTION_GATE.json`; `PROMOTION_REVIEW.json`; `ion_domain_weaver_projection_refresh_candidate.py` | `ION_VNEXT/02_kernel/ion_core/.../ion_promotion_plan_core.py` (in-memory plan records only, L1–7: "does not … write files") | **Parallel** — vNext is spec/review primitive; DW performs actual materialization |
| **Context mounts / active context** | `ion_domain_weaver_context_active_resolver.py`; `ion_domain_weaver_context_catalog.py`; mount binding via `ion_codex_agent_mount.py` + resolver gate | `ion_context_package_core.py` (in-memory package describe/validate, L1–7); `ION_VNEXT/04_carriers/` README-only | **DW subsumes runtime** — vNext context package core never reads live mounts |
| **Carrier dispatch / worker spawn** | `ion_domain_weaver_spawn_request_dispatcher.py`; `ion_domain_weaver_terminal_worker_maintainer.py`; `live_carrier_binding/`; pressure/need-based waves | `ION_VNEXT/04_carriers/` (no executable); `ion_carrier_mount_receipt.py` in vNext ion_core (receipt primitive only) | **DW subsumes** — only legacy kernel queue runners execute; vNext has no queue runner |
| **Governance / proof gates** | `ion_domain_weaver_route_gate_matrix.py`; `ion_domain_weaver_exact_start_gate.py`; `ion_domain_weaver_queue_governance.py`; orchestrator gate settlements | `ion_context_proof_gate.py`, `ion_template_action_gate.py`, `ion_ai_movement_gate.py` (copied/shared in vNext ion_core) | **Shared primitives, DW orchestrates** — gates exist in both; DW weaves them into worker-start and operator-action policy |
| **Receipt spine** | `domain_weaver/receipts/`, operator_actions, orchestrator receipts | `ion_receipt_core.py` (vNext, in-memory) | **Parallel** — vNext receipt core is bounded primitive; DW emits the operational receipt volume |
| **Front door / vNext mission lane** | seat_11 missions absorbed into `domain_weaver/` receipts; `role_atlas__ion_vnext_front_door` mount reads DW projection | `ION_VNEXT/00_front_door/` markdown; Mission 029–038 **maps/rebaselines** under terminal_workers | **DW absorbed mission outputs** — vNext front door remains doc skeleton |

---

## 5. Honest assessment

### 5.1 Must DW be carried to production (via decomposition)?

**Answer: Yes, functionally — not as a 49K monolith, but as the capability spine.** (Confidence: **high** for operational reality; **medium** for clean-core extraction feasibility.)

| For | Against / caveats |
|-----|-------------------|
| 8/9 assigned runtime modules import or call DW; queue runner worker-start is DW-gated | `ion_cursor_queue_runner` is uncoupled — production Cursor path needs explicit decision |
| `05_context/current/domain_weaver/` is where live projection, binding proofs, and orchestrator settlements live | **329M / 14K files** — majority is reclaimable process exhaust (terminal attempt bulk, snapshots) per exhaust catalog |
| ION_VNEXT frozen **2026-05-21**; no executable carriers/products populated | vNext **ion_core** gates/receipt primitives are still valuable **extract targets**, not replacements for DW |
| vNext Atlas missions produced **receipts inside DW**, not a second runtime | Git history for DW pre-2026-06-05 is **not visible** in this repo — evolution claims rely on receipts/mtimes |
| Monolith already partially strangler-figged (**38** satellites, monolith index) | Decomposition risk: `execute_domain_weaver_action` ~8.9K lines / 107 branches (MONOLITH_SEAM_AUDIT) |

### 5.2 Is vNext machinery largely parallel/redundant?

**Answer: Largely yes for runtime orchestration; partially no for clean primitives.**

- **Redundant / witness-only for runtime:** `ION_VNEXT/03_products`, `04_carriers`, `05_runtime` (README shells); domain weave dry-run YAML; Mission 029–038 **planning outputs** now referenced from DW mounts.
- **Still worth carrying forward (decomposed):** vNext `ion_core` proof gates, receipt core, path authority, promotion-plan **review** primitives — these are small, tested, and map to charter gaps — but they **do not** replace DW projection/orchestration.
- **ION_VNEXT as "clean rebuild target"** remains valid as a **destination layout**, not as the **current operational engine**. The engine is `ION/04_packages/kernel/ion_domain_weaver*` + `05_context/current/domain_weaver/`.

---

## 6. Non-claims

- This document **does not** assert production readiness, ratified authority, or accepted state for any DW artifact.
- **Does not** recommend deleting `ION_VNEXT`, terminal worker exhaust, or the monolith without separate gated archival plans.
- **Does not** claim complete DW git archaeology — pre-2026-06-05 commit history is **not available** in this checkout beyond the single source-packet import.
- **Does not** classify all `domain_weaver/` files as load-bearing — terminal worker attempt bulk is **process exhaust** unless bound by kernel pointers (see EXHAUST_AND_DUPLICATION_CATALOG).
- **Does not** grant live execution, deploy, push, or secrets authority.
- Synthesis here is **candidate evidence** for PRODUCTION_SPINE_AUDIT / CORE_RECKONING — not North Star ratification.

---

## Audit metadata

- **Method:** read-only `wc`, `du`, `find`, `rg`, `git log`, targeted file reads, module docstring scan
- **Mutations:** this file only (`ION/05_context/current/ion_system_definition/PRODUCTION_SPINE_AUDIT/CORE_RECKONING/DW_CORE_REALITY.candidate.md`)
- **Sibling inputs:** `EXHAUST_AND_DUPLICATION_CATALOG.candidate.md`, `MONOLITH_SEAM_AUDIT.candidate.md`, `PRODUCTION_CORE_AND_VNEXT_INVENTORY.candidate.md`
