# Production Core and vNext Inventory

**Status:** candidate / read-only audit  
**Date:** 2026-06-17  
**Authority:** reconnaissance only — no production-readiness claims, no ratification  
**Auditor lane:** PRODUCTION_SPINE_AUDIT / task C  
**Active root:** `/home/sev/ION - Production/ION_Developement`  
**Repo scale (evidence):** ~6.7G total; `ION/05_context` ~5.8G (87%); `ION/04_packages` ~61M

---

## Executive summary

The **working product surface** lives almost entirely in `ION/04_packages/kernel` (~39M, 461 `.py` modules), `ION/03_registry` (~2M YAML/JSON registries), carrier queue runners, `operator_cli.py`, and `ION/08_ui/joc_cockpit_shell` (~783M incl. `node_modules`). The rest of the top-level ION tree is predominantly **doctrine, protocols, templates, bootstrap locks, and context exhaust**.

**ION_VNEXT** exists as a **partial skeleton** at repo root (`ION_VNEXT/`, ~11M): front-door docs, a small `ion_core` package (30 src modules + control tests), candidate context/work/release artifacts — **not** a runnable production product. The Domain Weaver **seat_11 / Atlas vNext front-door mission lane** (MISSION_029–038) produced **maps, red-gate rebaselines, and receipts** under `05_context`, not a new executable product home.

Against the **2026-04-25 Product Readiness Charter** (V32 baseline): **0/10 fully implemented**, **~5 partial**, **~5 none**. The charter is **stale as a version pin** (references V32; repo now carries V96–V117 bootstrap locks and encyclopedia v4.x overlays) but its **10 criteria remain accurate** — `production_readiness.py` and `PRODUCTION_READINESS_GAP_REGISTER.md` still report the same critical gaps.

---

## 1. Product vs scaffold inventory (top-level ION tree)

| Path | du | Contents (summary) | Verdict |
|------|-----|-------------------|---------|
| `ION/00_BOOTSTRAP` | 332K | Version lock markdown (`V100`–`V117+` encyclopedia/context/integration locks) | **doctrine** — constitutional/version pins, not executable product |
| `ION/01_doctrine` | 28K | `SOVEREIGN_CONSTITUTION.md`, `CANONICAL_WORKFLOW.md`, kernel doctrine | **doctrine** |
| `ION/02_architecture` | 1.9M | ~100+ protocols (activation, daemon, release gate, ratification matrix, git containment, etc.) | **doctrine** — law/planning surface (A3) |
| `ION/03_registry` | 2.0M | Agent/domain/carrier/capability YAML+JSON; boots; schemas; `carrier_capability_registry.yaml`, `codex_cli_carrier_profile.yaml`, `cursor_cli_carrier_profile.yaml`, `chatgpt_browser_carrier_profile.yaml` | **product** — operational binding data consumed by kernel |
| `ION/04_packages` | 61M | `kernel/` (39M, 461 modules); stray `kernel.zip`/`kernel_.zip` (~23M); tiny `05_context/runtime_state/` | **mixed** — real kernel product + archive zips; exclude zips from product count |
| `ION/06_intelligence` | 34M | archaeology, orchestration notes, evidence, research, roundtable, specs | **mixed** — mostly witness/research; some load-bearing orchestration notes |
| `ION/07_templates` | 592K | Template families (carriers, context, agents, codex, automation, bindings) | **scaffolding** — governs work shape; not runtime |
| `ION/08_ui` | 783M | `joc_cockpit_shell/` React/Vite cockpit (panels incl. `VNextMissionControlPanel`, `FrontDoorProofTracePanel`, `DomainWeaverCockpitPanel`) | **product** (UI) — operator cockpit; bulk is `node_modules` |
| `ION/tests` | 19M | Kernel integration tests (`test_kernel_*`, codex hook tests) | **product support** — validates kernel behavior |
| `ION/docs` | 1.9M | Fundamentals, context system, encyclopedia v4.x subtree, setup | **mixed** — operator docs + encyclopedia witness |

**Not in scope table but dominant:** `ION/05_context` (~5.8G) = **scaffolding/exhaust** — domain_weaver terminal workers, codex mounts, mission receipts, chatgpt_connector queue state. Load-bearing for continuity; not clean production core.

---

## 2. Kernel real product modules

**Location:** `ION/04_packages/kernel/` (461 `.py` files, ~361K LOC total).  
**Install surface:** repo-root `pyproject.toml` → `where = ["ION/04_packages"]`, `include = ["kernel*"]`.  
**Exclude from “real product” for clean-core planning:**

- `kernel.zip`, `kernel_.zip` under `ION/04_packages/` (archives, not import surface)
- Duplicate snapshots under `ION/05_context/current/reports/**/ION_VNEXT/` (witness copies)
- `ION_VNEXT/02_kernel/ion_core/` (separate slim package; see §4)
- Monolith orchestration blob: `ion_domain_weaver.py` (49,513 lines) — load-bearing today but not clean-core shape

### 2.1 Functional map — where things live

| Concern | Primary paths | Notes |
|---------|---------------|-------|
| **Daemon / runtime loop** | `daemon.py`, `daemon_loop.py`, `daemon_service.py`, `daemon_actions.py`, `ion_runtime_service_control.py` | Modules explicitly disclaim full production daemon (`daemon.py` L3–6; `daemon_loop.py` L3–7). First-pass arbitration + bounded loop only. |
| **Front door / operator CLI** | `operator_cli.py` (~3K LOC), `front_door_runtime_entry.py`, `front_door_chat_orchestration.py`, `front_door_self_mount_binding.py`, `ion_carrier_onboard.py` | `operator_cli.py` = discoverable supervised entry (`python -m kernel.operator_cli`). Front-door runtime persists Persona→Relay→Steward boundary artifacts; no HTTP server. |
| **Codex carrier** | `ion_codex_queue_runner.py` (~8.6K LOC), `ion_codex_agent_mount.py`, `ion_codex_cli_carrier_audit.py`, `ion_carrier_task_return.py` | Profile: `ION/03_registry/codex_cli_carrier_profile.yaml` → `queue_runner` implied via branch registry `codex_queue` family |
| **Cursor carrier** | `ion_cursor_queue_runner.py`, `cursor_subagent_ion_role_registry.py` | Profile: `ION/03_registry/cursor_cli_carrier_profile.yaml` → `queue_runner_module: kernel.ion_cursor_queue_runner` |
| **Browser GPT / MCP carrier** | `ion_chatgpt_browser_mcp_connector_contract.py`, `ion_chatgpt_browser_mcp_http_preview.py`, `ion_custom_gpt_action_gateway.py` | Profile: `ION/03_registry/chatgpt_browser_carrier_profile.yaml`; large preview/MCP surface — demo-adjacent |
| **Registry (data)** | `ION/03_registry/*.yaml`, `ION/03_registry/boots/` | Kernel reads; does not own registry files |
| **Registry (runtime helpers)** | `authority_lineage.py`, `executor_registry.py`, `index.py`, `graph.py` | Core graph/index primitives |
| **Cockpit / UI view-model** | `ion_cockpit_view_model.py` (~7K LOC) + `ION/08_ui/joc_cockpit_shell/` | View-model binds vNext paths, front-door proof trace, queue status into UI panels |
| **Context / proof gates** | `ion_context_proof_gate.py`, `ion_template_action_gate.py`, `ion_agent_cwd_boundary.py`, `capsule_manager.py`, `context_compiler.py` | Carrier return contract enforcement |
| **Production readiness reporting** | `production_readiness.py`, `release_readiness.py` | Report/gate tooling; `production_ready: false` by design |
| **Demo workflow (not production primitive)** | `summary_refresh_demo*.py`, `summary_refresh_demo_release_candidate*.py` | Charter criterion #2 gap — still co-located with kernel |

### 2.2 Real product module categories (representative list)

**Core runtime spine (~25 modules):**  
`graph.py`, `index.py`, `store.py`, `model.py`, `execution.py`, `dispatch.py`, `scheduler.py`, `commit.py`, `governed_write.py`, `continuation.py`, `bootstrap_init.py`, `bootstrap_activation.py`, `bootstrap_bridge.py`, `horizon_state.py`, `runtime_state_views.py`, `daemon.py`, `daemon_loop.py`, `daemon_service.py`, `daemon_actions.py`, `operator_cli.py`, `ion_status.py`, `production_readiness.py`, `release_readiness.py`, `authority_lineage.py`, `executor_registry.py`

**Carrier execution (~15 modules):**  
`ion_codex_queue_runner.py`, `ion_cursor_queue_runner.py`, `ion_carrier_task_return.py`, `ion_carrier_onboard.py`, `carrier_mount.py`, `ion_codex_agent_mount.py`, `ion_codex_cli_carrier_audit.py`, `ion_context_proof_gate.py`, `ion_template_action_gate.py`, `ion_agent_cwd_boundary.py`, `ion_agent_route_enforcement.py`, `ion_ai_movement_gate.py`, `external_execution_bridge.py`, `ion_codex_work_request_target_binding.py` (also in vNext ion_core)

**Front door / operator (~8 modules):**  
`front_door_runtime_entry.py`, `front_door_chat_orchestration.py`, `front_door_self_mount_binding.py`, `front_stage_council_receipt.py`, `conversational_receipt.py`, `runtime_identity_envelope.py`, `self_surface_drift_gate.py`, `agent_succession_packet.py`

**Agent comms / spawn (partial — not production activation authority):**  
`ion_agent_comms.py`, `ion_agent_invocation_broker.py`, `ion_agent_spawn_templates.py`, `ion_agent_control_plane.py`, `ion_agent_context_systems.py`, `child_work_service.py`, `children.py`

**Cockpit / ChatOps / MCP (large, demo-adjacent):**  
`ion_cockpit_view_model.py`, `ion_chatops_bridge.py`, `ion_chatgpt_browser_mcp_connector_contract.py`, `ion_chatgpt_browser_mcp_http_preview.py`, `ion_custom_gpt_action_gateway.py`, `ion_action_mcp_branch_leaders.py`

**Monolith / domain orchestration (defer from clean core):**  
`ion_domain_weaver.py` (49,513 lines), `ion_domain_weaver_swarm_control_plane.py`, `ion_domain_weaver_route_gate_matrix.py`, plus related spawn/dispatch helpers

**Demo-only (charter #2 — must split before production core):**  
`summary_refresh_demo.py`, `summary_refresh_demo_replay.py`, `summary_refresh_demo_doctor.py`, `summary_refresh_demo_certification.py`, `summary_refresh_demo_release_candidate.py`, `summary_refresh_demo_release_candidate_verify.py`, `summary_refresh_demo_evidence_bundle.py`

---

## 3. vNext reality check

### 3.1 What vNext intended

From `ION_VNEXT/00_front_door/README.md`, mount manifest, and MISSION_038 packets:

- **Front door:** candidate entry (`00_front_door/AI_START_HERE.md`, `ROUTE_MAP.md`, `AUTHORITY_BOUNDARIES.md`) — orient humans/agents inside a clean rebuild without replacing legacy root front door
- **Red gate:** Mission 029 Atlas rebaseline — no-start repair workspawn; Worker Shift / comms / capacity gates must be GREEN before terminal32 start claims (`MISSION_029_ATTEMPT383_*`)
- **Next-wave map:** Mission 038 — route 336-domain expansion into vNext domain lanes (canon, kernel, carriers, runtime, context, work/release, references, archive)

All artifacts explicitly **candidate-only**, **no production cutover**, **no accepted state**.

### 3.2 What exists on disk

| Artifact class | Path | Real skeleton? |
|----------------|------|----------------|
| **vNext tree (May 2025 era)** | `ION_VNEXT/` (~11M, 644 files) | **Partial skeleton** |
| Front-door docs | `ION_VNEXT/00_front_door/` (52K, 5 markdown files) | Docs only — real but not executable |
| Slim kernel package | `ION_VNEXT/02_kernel/ion_core/` (988K; 30 src modules, 29 control tests) | **Real code** — gates, receipts, vNext cutover/readiness/rollback *review* modules; not full runtime |
| Products / carriers / runtime dirs | `ION_VNEXT/03_products/`, `04_carriers/`, `05_runtime/` | **README only** (except one bridge markdown in `05_runtime/`) |
| Context | `ION_VNEXT/06_context/` (2.1M) | Domain Weave candidate manifest — context, not runtime |
| Work / releases | `ION_VNEXT/07_work/` (7.3M), `08_releases/` (384K) | Mission/release **packets**, not product binaries |
| Atlas mount | `ION/05_context/current/codex_agent_mounts/role_atlas__ion_vnext_front_door/` | **Mount scaffolding** — AGENTS.md, manifest, `.ion/` capsule, 24+ mission receipts; **zero product `.py`** |
| Mission 029–038 packets | `ION/05_context/current/domain_weaver/terminal_workers/.../seat_11/MISSION_*VNEXT*` | **Maps + rebaselines + JSON receipts** — planning/audit outputs |
| Cockpit vNext panel | `ION/08_ui/joc_cockpit_shell/VNextMissionControlPanel.tsx` | UI projection over vNext paths via `ion_cockpit_view_model.py` |

### 3.3 Plain verdict

**The Domain Weaver vNext / front-door mission effort did NOT produce a new runnable product skeleton.** It produced **mission-attempt receipts, red-gate rebaselines, next-wave maps, and mount context** under `05_context`.

**A pre-existing partial skeleton** does exist at **`ION_VNEXT/02_kernel/ion_core`** (30 modules focused on proof gates, receipts, and cutover *review* tooling) plus front-door markdown — but **`03_products`, `04_carriers`, and `05_runtime` were never populated with executable product code.** The heavy runtime remains in **`ION/04_packages/kernel`**, with cockpit UI referencing `ION_VNEXT/*` paths as candidate evidence pointers.

Evidence: `DOMAIN_WEAVER_PROJECTION.json` cited in Mission 038 shows `ion_vnext_front_door` with **`agent_count=0`, `materialized_mount_count=0`** for direct mounts; coverage is via steward/relay/persona roles only.

---

## 4. Charter criteria matrix (10 production criteria)

**Sources:**  
`ION/02_architecture/PRODUCT_READINESS_CHARTER.md` (2026-04-25, V32 baseline)  
`ION/02_architecture/PRODUCTION_READINESS_GAP_REGISTER.md` (G1–G8)  
`ION/02_architecture/RELEASE_READINESS_GATE_PROTOCOL.md` (release ≠ production)  
`ION/02_architecture/PRODUCTION_RATIFICATION_MATRIX_PROTOCOL.md` (unclassified = NOT_PRODUCTION_AUTHORIZED)  
`ION/04_packages/kernel/production_readiness.py` (`production_ready: false`, CRITICAL_GAPS)

**Charter staleness:** Criteria text is still operative. Version pin ("V32 proves bounded summary-refresh release-demo") is **stale** — repo now has V96–V117 bootstrap locks, encyclopedia v4.x, Domain Weaver missions through 038+, and kernel growth to 461 modules / 49K-line weaver monolith. Gap register has **not** been closed.

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | All production authority surfaces ratified | **none** | G1; `production_readiness.py` CRITICAL_GAPS[0]; ratification rows remain A3/HOLD; `PRODUCTION_RATIFICATION_MATRIX_PROTOCOL.md` — unclassified surfaces default NOT_PRODUCTION_AUTHORIZED |
| 2 | Demo-only surfaces separated from reusable production primitives | **none** | G2; charter criterion explicitly listed in ACTIVE_CONTEXT_PACKAGE ledger as "never done"; `summary_refresh_demo*.py` still in `ION/04_packages/kernel/`; `production_readiness.py` row: `HOLD_FOR_REFACTOR` / `SPLIT_BEFORE_PRODUCTION` |
| 3 | Global graph canon defined, tested, migration-safe | **partial** | `context_graph_ontology_adapter.py`, `graph.py`, template event graph under `ION/05_context/graph/` exist; `production_readiness.py`: "NOT_GLOBAL_GRAPH_CANON"; G7 rollback/migration law missing; no ratified global canon registry |
| 4 | Source-summary rewrite authority governed, provenance-bound, reversible | **none** | G4; `production_readiness.py` row `source-summary rewrite authority` → `NOT_IMPLEMENTED` / `MISSING_PRODUCTION_AUTHORITY` |
| 5 | Agent/subagent activation governed, leased, receipted, kill-switchable | **partial** | Protocol: `ACTIVATION_AUTHORITY_PROTOCOL.md`; code: `ion_agent_invocation_broker.py`, `ion_agent_spawn_templates.py`, Domain Weaver spawn paths; **but** `production_readiness.py` row → `NOT_IMPLEMENTED`; `ion_domain_weaver.py` sets `"activation_authority": False`; no production kill-switch law ratified |
| 6 | Daemon run, pause, resume, recover idempotently | **partial** | `daemon.py`, `daemon_loop.py`, `daemon_service.py` exist with tests nearby; modules disclaim full loop; G6 "daemon runtime loop is not productionized"; no production recovery/idempotency certification |
| 7 | Front-door paths expose operator-visible reasons, changes, refusals, pending reviews | **partial** | `front_door_runtime_entry.py` (REFUSED/ACCEPTED receipts), `operator_cli.py`, `ion_cockpit_view_model.py` + `FrontDoorProofTracePanel.tsx`, `ION/05_context/current/ACTIVE_FRONT_DOOR_PROOF_TRACE.json` path binding — candidate, not ratified production front door |
| 8 | Release candidates certifiable and independently verifiable | **partial** | `summary_refresh_demo_release_candidate_verify.py`, `release_readiness.py`, `RELEASE_READINESS_GATE_PROTOCOL.md` — **demo/release-checkpoint scope only**; protocol L48: READY ≠ whole product complete |
| 9 | Multiple workflow classes pass the evented chain | **partial** | V32 demo chain referenced in charter; `contract_bound_event_runtime.py` exists; **one** certified summary-refresh demo workflow — not generalized to multiple production workflow classes |
| 10 | Nemesis/adversarial audit reports zero critical blockers | **none** | G8; no completed adversarial production audit artifact found; Domain Weaver Nemesis lanes produce candidate reviews only |

**Scorecard:** **0 implemented · 5 partial · 5 none**

---

## 5. Proposed clean production core (`ION_VNEXT` as real product home)

### 5.1 Initial minimal coherent product

A clean **`ION_VNEXT` production home** should **not** copy the 461-module monolith. It should **extract and own** a bounded spine:

```
ION_VNEXT/                          # real product root (promoted from candidate)
├── 00_front_door/                  # keep existing markdown + add thin CLI routing doc
├── 01_canon/                       # WORKSPACE_CANON, CONTROL_SURFACE_REGISTRY (existing)
├── 02_kernel/ion_core/             # expand from current 30 modules — the only Python package
├── 03_registry/                    # slim carrier + workspace registry subset (promoted from ION/03_registry)
├── 04_carriers/                    # queue runner wiring docs + carrier return templates
├── 05_runtime/                     # daemon service entry, status, receipt history paths
└── 08_ui/                          # optional: slim cockpit shell subset (or embed later)
```

**Kernel modules to seed `ion_core` (merge existing vNext + extract from main kernel):**

| Layer | Modules |
|-------|---------|
| Workspace / path law | `ion_workspace_root_registry.py`, `ion_path_authority.py`, `ion_agent_cwd_boundary.py` (already in vNext ion_core) |
| Proof gates | `ion_context_proof_gate.py`, `ion_template_action_gate.py`, `ion_ai_movement_gate.py` |
| Receipt spine | `ion_receipt_core.py` (vNext only today — promote), `ion_carrier_mount_receipt.py` |
| Carrier execution | Extract **`ion_codex_queue_runner.py`**, **`ion_cursor_queue_runner.py`**, **`ion_carrier_task_return.py`**, **`ion_carrier_onboard.py`**, **`carrier_mount.py`** — trimmed of Domain Weaver couplings |
| Front door | Extract **`front_door_runtime_entry.py`** + minimal **`operator_cli.py`** subcommands (status, carrier status, front-door trace) |
| Daemon (bounded) | Extract **`daemon_service.py`** + **`daemon.py`** act-once path only — no planner/weaver sweep |
| Readiness (report-only) | Keep vNext review modules (`ion_vnext_readiness_lock.py`, rollback/release *candidate* reviewers) — explicitly non-authorizing |

**Registry subset (promote copies, not symlinks):**

- `codex_cli_carrier_profile.yaml`
- `cursor_cli_carrier_profile.yaml`
- `carrier_capability_registry.yaml` (trimmed)
- `approved_context_index.yaml`

**Explicitly exclude from v1 core:**

- `ion_domain_weaver.py` and swarm control plane
- `summary_refresh_demo*.py` (remain legacy demo lane)
- Browser MCP preview / ChatGPT connector monolith (`ion_chatgpt_browser_mcp_*`)
- Full cockpit (783M) — defer; use CLI + JSON status first

**Daemon entry:** `python -m kernel.daemon_service` (extracted) or vNext wrapper script under `05_runtime/`  
**Front-door entry:** `python -m kernel.operator_cli` (trimmed) + `00_front_door/AI_START_HERE.md`  
**Carrier entry:** `python -m kernel.ion_codex_queue_runner --status` / `--process-once` per existing bounded contract

### 5.2 First 1–2 extraction candidates (highest value, lowest coupling)

**Candidate 1 — Carrier contract spine (extract first)**  
*Why:* Working bounded contract already enforced in production-adjacent daily use; profiles in registry; returns require CONTEXT PROOF + TEMPLATE ACTION PROOF sections; queue runners are explicitly bounded ("does not create a second work system" — `ion_codex_queue_runner.py` L3–6).

Extract bundle:

- `ION/03_registry/codex_cli_carrier_profile.yaml`
- `ION/03_registry/cursor_cli_carrier_profile.yaml`
- `ION/04_packages/kernel/ion_context_proof_gate.py`
- `ION/04_packages/kernel/ion_template_action_gate.py`
- `ION/04_packages/kernel/ion_codex_queue_runner.py` (decouple from Domain Weaver imports where possible)
- `ION/04_packages/kernel/ion_cursor_queue_runner.py`
- `ION/04_packages/kernel/ion_carrier_task_return.py`
- `ION/04_packages/kernel/ion_carrier_onboard.py`
- `ION/07_templates/carriers/CODEX_CLI_EXECUTION_PACKET.md`

**Candidate 2 — Front-door + receipt operator visibility (extract second)**  
*Why:* Charter criterion #7; low dependency on weaver/monolith; pairs with carrier returns for operator-trustworthy reasons/refusals.

Extract bundle:

- `ION/04_packages/kernel/front_door_runtime_entry.py`
- `ION/04_packages/kernel/operator_cli.py` (subset: status, front-door, carrier commands only)
- `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_receipt_core.py` (already isolated)
- `ION/04_packages/kernel/ion_status.py`
- `ION_VNEXT/00_front_door/*` (existing docs)

**Do not extract first:** `ion_domain_weaver.py` — highest coupling, 49K lines, entangled with `05_context` exhaust; aligns with parallel monolith-seam audit.

---

## 6. Cross-check notes

- **`ION/04_packages/05_context/runtime_state/`** — runtime state storage inside packages tree; not a duplicate kernel.
- **No `packages/kernel` duplicate tree found under `ION/05_context`** (only report-milestone snapshots and export overlays).
- **`pyproject.toml`** installs `kernel*` from `ION/04_packages` only; `ION_VNEXT/02_kernel/ion_core` is a **separate** nested package with its own `pyproject.toml`.
- **0 promotions** from Domain Weaver promotion review (`PROMOTION_REVIEW.md` cited in mount manifest: `accepted_state_count: 0`).

---

## 7. Audit metadata

- **Method:** read-only `du`, `find`, `ls`, file reads, targeted grep
- **Mutations:** none (this file only)
- **Next synthesis input:** combine with `MONOLITH_SEAM_AUDIT.candidate.md` and exhaust catalog for production-spine plan
