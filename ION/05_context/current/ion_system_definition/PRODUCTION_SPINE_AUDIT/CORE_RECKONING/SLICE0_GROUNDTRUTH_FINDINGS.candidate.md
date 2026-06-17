# Slice 0 Ground-Truth Findings — the engine already encodes Option A (candidate)

**Date:** 2026-06-17
**Author:** ION North Star / IONOLOGIST
**Class:** candidate / not-accepted-state. No production-readiness claim. Nothing moved, retired, or mutated by this document — it records ground-truth recon that **supersedes** specific prior audit/decision claims.
**Trigger:** Operator gave GO on Option A Slice 0 ("stand up vNext frame as production_core + quarantine drift"). Before mutating, I ground-truthed the actual on-disk + in-kernel reality. The approved plan rests on two false premises. This file corrects them.

---

## TL;DR

ION_VNEXT is **not** a dormant parallel rebuild to "adopt and clean." The **live Domain Weaver engine already contains, defines, and wires a complete program to take ION_VNEXT to production** — `domain_weaver_dynamic_swarm_vnext_productization`. The path to production is to **drive that existing program to settlement**, not to rebuild a frame or retire "drift." The proposed "retire the drift (domain_weave)" step is **unsafe and retracted** — that path is a live kernel constant.

---

## Finding 1 — the live runtime binds ION_VNEXT across every lane (not dormant)

`rg "ION_VNEXT" ION/04_packages ION/03_registry` = **80 references in 8 live files.** Rollup of referenced vNext lanes (from `ion_domain_weaver.py`, 50 of the 80):

| vNext lane | live refs | bound by |
|---|---|---|
| `01_canon` | 18 | ion_domain_weaver, registry, project_cockpit, mcp_connector |
| `00_front_door` | 14 | ion_domain_weaver, mcp_connector |
| `02_kernel` | 5 | ion_domain_weaver |
| `06_context` (domain_weave) | ~9 | ion_domain_weaver, **ion_agent_control_plane**, chatops_bridge, mcp_connector, 2 registries |
| `05_runtime` | 5 | ion_domain_weaver, ion_cockpit_view_model |
| `07_work` | 8 | ion_domain_weaver, project_cockpit, chatops_bridge, mcp_tool_policy |
| `04_carriers`, `03_products`, `09_references` | 2 each | ion_domain_weaver, mcp connector/policy |

The live runtime **reaches into ION_VNEXT**. It is structurally entangled, not frozen-and-separate.

## Finding 2 — the SMOKING GUN: the engine already encodes Option A

`ion_domain_weaver.py:8273` `def _domain_weaver_vnext_productization_lanes(root)` — **called** at `:8873`. It defines **8 first-class domains, one per vNext lane**, each with `required_context` + a `production_spec_*_gap_return` output:

| lane_kind | path | required_output |
|---|---|---|
| `ion_vnext_front_door_authority` | `ION_VNEXT/00_front_door` | front-door authority + currentness gap |
| `ion_vnext_canon_control_surface` | `ION_VNEXT/01_canon` | canon/control gap |
| `ion_vnext_kernel_core` | `ION_VNEXT/02_kernel/ion_core` | kernel test+import gap |
| `ion_vnext_products_and_cockpit` | `ION_VNEXT/03_products` | product surface gap |
| `ion_vnext_carrier_loop` | `ION_VNEXT/04_carriers` | carrier loop gap |
| `ion_vnext_runtime_bridge` | `ION_VNEXT/05_runtime` | runtime bridge gap |
| `ion_vnext_domain_weaver_integration` | `ION_VNEXT/06_context/domain_weave` | DW-integration gap |
| `ion_vnext_release_cutover` | `ION_VNEXT/07_work` | cutover remaining-gate gap |

- **mission** (`:8387`): `bring_ion_vnext_to_production_spec_with_domain_weaver_integrated_as_candidate_until_gated`
- **primary_mission** (`:8922`,`:8959`): `ion_vnext_production_spec_with_production_grade_domain_weaver_integration`
- **program_id** (`:8935`): `ion_vnext_production_spec_hardening`
- **route_family** (`:9180`–`:11484`, 9 routes): `domain_weaver_dynamic_swarm_vnext_productization`
- surfaced in the cockpit **projection** summary (`:38450`,`:39515`): `dynamic_swarm_vnext_productization_lane_count`

The lane builder is **guarded** (`if not target_path.exists() or not required_context: continue`, `:8379`) — so it degrades gracefully, but removing vNext paths silently drops domains from the program.

**Interpretation:** Option A (vNext = production target, Domain Weaver = the integrated engine) is not a new decision — **the integral engine already defines and wires it as its own swarm program.** Per audit C, 0 vNext domains have been promoted: the program appears **defined + wired but never driven to settlement**.

## Finding 3 — `domain_weave` is a LIVE kernel constant, not inert drift

`ion_agent_control_plane.py:46` `DOMAIN_WEAVE_ROOT = Path("ION_VNEXT/06_context/domain_weave")`, then used for `README`, `dry_runs/M103I_*` map+registry, `examples/integrated_agent_enterprise/*` org-chart+DRA index, and (`:1105`) reads `reports/M103B_VALIDATION_REPORT.json` at runtime. Also referenced by `ion_domain_weaver.py` (the `ion_vnext_domain_weaver_integration` domain), the MCP connector contract, the chatops bridge, and 2 registries. **MANIFEST.json present on disk; bindings resolve.**

`domain_weave` is the engine's **declared Domain-Weaver integration domain**, not "witness-only drift."

---

## Corrections to prior docs (explicit supersession)

| Prior claim | Source | Corrected |
|---|---|---|
| "domain_weave is witness-only drift → DRIFT-RETIRE" | `VNEXT_DW_RECONCILIATION` (R2) | **FALSE.** Live-bound (kernel constant + 6 files + 2 registries). KEEP. |
| "retire the drift (domain_weave + cutover)" | `CORE_TARGET_DECISION` | **RETRACTED.** Would break live kernel/registry/MCP. |
| "two competing cores + a testbed = drift" | R2 / decision | **Refined.** There is ONE engine (live DW) that already targets vNext productization. Not two competing cores. |
| "vNext froze 2026-05-21, stalled, separate" | reckoning | **Refined.** vNext content froze, but the live engine actively references it as its productization target. |
| "testbed worktree is a dead end" | R2 / decision | **STILL TRUE** (independent; tip is ancestor of HEAD = 0 unmerged commits; 148K untracked). |
| vNext frame is the disciplined production_core skeleton | decision | **CONFIRMED** (`01_canon/WORKSPACE_CANON.yaml` = clean 12-lane contract). |
| Domain Weaver is the integral engine | R1 | **CONFIRMED + strengthened** (it owns the vNext-productization program). |

---

## Corrected architecture (one paragraph)

There is **one** engine — the live Domain Weaver — and it already contains a wired program (`domain_weaver_dynamic_swarm_vnext_productization`, program `ion_vnext_production_spec_hardening`) whose 8 domains map exactly onto the vNext frame's lanes, with the mission of bringing vNext to production spec with Domain Weaver integrated. The vNext frame is the disciplined target skeleton; `domain_weave` is the engine's integration substrate. **The path to production is to drive this existing program to settlement** (run each lane → produce its `*_gap_return` → settle → burn down the gap), using the proven Cursor/Codex carriers — **not** to rebuild a frame, decompose DW into it, or retire "drift."

## Revised Slice 0 / Slice 1

- **Slice 0 (safe, recalibrated):** (a) write a `production_core` identity doc that *recognizes* the engine's existing program (no new third root); (b) retire the dead testbed worktree (archive 148K untracked → `git worktree remove`, keep branch); (c) **NO** domain_weave / canon mutation.
- **Slice 1 (recalibrated, much stronger):** exercise **one** `vnext_productization` lane end-to-end to a settled gap-return — recommend `ion_vnext_kernel_core` (most concrete + testable: it has `pyproject.toml` + a control test suite) — as the **first real vNext promotion**, via a Cursor/Codex carrier. This finally exercises the promotion path (stuck at 0) using the engine's own machinery.
- **Hygiene nuance (later):** only the *verified-unbound* `domain_weave` exhaust (e.g., `receipts/`, `settlement/`, `review_packets/`, non-`M103I` `dry_runs/`) is a reclaim candidate; the live-bound core (`MANIFEST.json`, `README.md`, `protocols/`, `dry_runs/M103I_*`, `examples/integrated_agent_enterprise/*`, `reports/M103B_VALIDATION_REPORT.json`) is KEEP.

---

## Non-claims
- No production-readiness claim. Candidate findings; operator ratifies any direction change.
- "The engine encodes the program" ≠ "the program has been run to green" (audit C: 0 vNext promotions). Execution status to be verified by actually invoking a lane.
- Nothing was moved/retired/mutated by this recon. The only proposed mutation (testbed worktree) is reversible (branch persists).
- This corrects, but does not delete, the prior audit/decision docs; they remain as the record, with these supersessions noted.

---

## SLICE 1a TRACE RESULT — the program already ran to green, then the outputs were pruned (2026-06-17)

**Trace complete.** Lifecycle of the `vnext_productization` program:
1. `materialize_dynamic_swarm_candidate_work_requests` — writes one work-request packet per lane to `chatgpt_connector/codex_work_requests/`; **never** starts workers (`start_workers_requested=False, max_worker_starts=0`).
2. a carrier worker runs a packet (`role.mason` + `role.steward`/`role.nemesis`), writes `run.json` + `task_return_body.md` under `codex_queue_runs/`, and flips the packet `status` to `RETURN_RECORDED_PROOF_ACCEPTED` once the proof gates pass (context proof, template-action proof, operational posture, workload diff).
3. `_domain_weaver_dynamic_swarm_fresh_context_reconciliation` reads the **persisted packet `status`** (not the recomputed plan) to settle each lane.
`execute_domain_weaver_action(root, {"action": ...})` is the dispatcher; **all** allowed actions are `policy_governed_no_magic` (no operator magic-string; governed by internal gates + `dynamic_start_window`, currently 3).

**Discovery that overturns the Slice-1 premise (and corrects audit C's "0 vNext promotions / execution unverified"):**
- The program was **already driven to full settlement on 2026-06-02.** All **15** dynamic-swarm lanes — 5 topology + 8 vNext productization (Front Door, Canon, **Kernel Core**, Products/Cockpit, Carrier Loop, Runtime Bridge, DW Integration, Release/Cutover) + Fan-In Settlement + Nemesis Overclaim Audit — are persisted at `RETURN_RECORDED_PROOF_ACCEPTED`; today's read-only reconciliation still classifies all 15 as `accepted`.
- Lane 8 (Kernel Core) alone was run **8 times** that day; returns passed every gate (context proof 35/35 paths present, 0 missing). The worker really read+analyzed `ION_VNEXT/02_kernel/ion_core/{pyproject.toml,src/kernel,tests/control}`.
- **But the substantive output is gone.** `codex_queue_runs/` now holds **zero** run dirs and **0** `task_return_body.md` files. Surviving `task_returns/*.json` packets retain only a **1200-char `task_output_preview`** (the CONTEXT-PROOF header) + a sha256 — **no gap findings, no recommended next packet.** This pruning was **not** the 2026-06-17 Phase 0 hygiene (which never touched `chatgpt_connector/`); the run-exhaust was cleaned earlier.

**Reframed production blocker (the real "why not production-ready"):** ION's own machinery already *runs the production-spec gap program to proof-accepted settlement* — repeatedly — and then treats the results as disposable run-exhaust that is pruned before being **harvested** into a durable product plan. The promotion path is not "stuck at 0 because it was never run"; it is "**0 durable promotions because the settled outputs evaporate.**" The missing organ is **harvest + durability**, not capability.

**Corrected Slice 1 (drive):** re-drive `ion_vnext_kernel_core` **freshly and durably** — produce a new 9-section gap return and land its **body** in a git-tracked harvest surface (`PRODUCTION_SPINE_AUDIT/`), not in volatile `codex_queue_runs/`. This satisfies "drive one lane to a settled gap-return" with real content **and** establishes the harvesting discipline whose absence is the actual blocker; it becomes the template for harvesting all lanes into the readiness burn-down.
