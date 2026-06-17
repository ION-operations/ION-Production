# ION Clean-Core Target — DECISION (candidate)

**Date:** 2026-06-17
**Author:** ION North Star / IONOLOGIST
**Class:** candidate / not-accepted-state. No production-readiness claim. Decision of *architectural target*;
operator ratifies *execution*. Nothing moved/retired by this document.
**Inputs:** `CORE_RECKONING/DW_CORE_REALITY.candidate.md` (R1), `CORE_RECKONING/VNEXT_DW_RECONCILIATION.candidate.md` (R2),
audits A/B/C in `PRODUCTION_SPINE_AUDIT/`.

---

> ## ⚠ SLICE 0 GROUND-TRUTH CORRECTION (2026-06-17) — read `SLICE0_GROUNDTRUTH_FINDINGS.candidate.md` first
>
> On operator GO, Slice-0 recon ground-truthed this decision against the live kernel and found two false premises:
> 1. **"retire the drift (domain_weave + cutover)" is RETRACTED — UNSAFE.** `ION_VNEXT/06_context/domain_weave` is a
>    **live kernel constant** (`ion_agent_control_plane.py:46 DOMAIN_WEAVE_ROOT`, used incl. `:1105`) + bound by
>    `ion_domain_weaver.py`, the MCP connector, the chatops bridge, and 2 registries. It is the engine's declared
>    `ion_vnext_domain_weaver_integration` domain, **not** witness-only drift.
> 2. **The engine already encodes Option A.** `ion_domain_weaver.py:8273 _domain_weaver_vnext_productization_lanes`
>    (called `:8873`) defines **8 domains = the 8 vNext lanes**, mission
>    `bring_ion_vnext_to_production_spec_with_domain_weaver_integrated_as_candidate_until_gated`, program
>    `ion_vnext_production_spec_hardening`, route family `domain_weaver_dynamic_swarm_vnext_productization` (9 routes),
>    surfaced in the cockpit projection. The live runtime carries **80 refs into ION_VNEXT across all lanes**.
>
> **Net:** Option A's *spirit* is CONFIRMED and already wired in the engine (vNext = target, DW = integrated engine).
> Its *mechanics* below — "decompose DW into a clean frame" + "retire drift" — are **superseded**. The corrected path
> is to **drive the engine's existing `vnext_productization` swarm program to settlement** (run each lane → gap-return →
> settle → burn down), not to rebuild/retire. See findings doc for the corrected Slice 0/1.

---

## Decision (one line)

**Adopt Option A:** the unified ION clean core = **vNext's disciplined FRAME (skeleton)** populated by
**DECOMPOSING the integral Domain Weaver (engine)**; **retire the parallel drift**; the DW production-testbed
worktree is a **dead end**.

> **CORRECTED (see box above):** keep "vNext FRAME = target" + "Domain Weaver = integrated engine"; **drop**
> "decompose DW into the frame" and "retire drift" — the engine already wires the vNext-productization program and
> `domain_weave` is live-bound. Testbed worktree dead-end stands.

This resolves the `[TBD]` Phase-1 target from `PRODUCTION_SPINE_PLAN.candidate.md`.

---

## Why — the two reckonings converged independently

- **DW is the integral, de-facto runtime spine.** 39 modules / 87,884 LOC (49,513 monolith + 38 satellites);
  56 kernel files mention it; **8 of 9** runtime modules depend on it; owns ~329M of orchestration state;
  107 operator actions via `execute_domain_weaver_action` (`ion_domain_weaver.py:40574`). It kept evolving
  through June; vNext froze 2026-05-21. (R1)
- **vNext is NOT a parallel runtime — it is a clean FRAME + a few useful primitives.** Its `06_context/domain_weave/`
  (~955 LOC) is a *diverged pre-DW planning MVP* (kernel treats it as witness only); its `ion_vnext_production_authority_*`
  cutover stack is *review-theater* over `08_releases/`; 8/10 of its gate modules are *already duplicated* in the
  kernel. What's genuinely valuable: the front-door/canon/lane layout and the in-memory gate/receipt/promotion-plan
  primitives. (R2)
- **The testbed worktree is abandoned.** `ION_DW_PRODUCTION_TESTBED_WORKTREE` is 386M, but its `ION_VNEXT` is only
  572K; the bulk is unrelated (AIM-OS 174M, Needs_Routed 54M, ION_GPT 54M) over a **pre-DW kernel with no
  `ion_domain_weaver.py`**; June planning receipts are untracked. Frozen at May-21. (R2)
- Both audits independently conclude: **carry DW forward by decomposition; keep the vNext frame; retire the drift.**
  The hypothesis posed to R2 was confirmed.

---

## Asset disposition

| Asset | Source | Disposition |
|---|---|---|
| vNext `00_front_door` + `01_canon` + lane layout (`00..09`, `90_archive`, `99_private`) | dev `ION_VNEXT` | **KEEP-AS-FRAME** — skeleton of `production_core` (rename canon "Domain Weave" → "Domain Weaver") |
| vNext `ion_core` primitives: proof gates, `ion_receipt_core`, `ion_promotion_plan_core`, `ion_context_package_core` | dev `ION_VNEXT/02_kernel/ion_core` | **SALVAGE** — adopt as clean primitives; reconcile against the kernel duplicates (8/10 already exist) |
| vNext `06_context/domain_weave/*` (~955 LOC, `ion.domain_weave.*`) | dev `ION_VNEXT` | **DRIFT-RETIRE** — diverged pre-DW MVP, superseded by live DW |
| vNext `ion_vnext_production_authority_*` cutover modules | dev `ION_VNEXT/02_kernel/ion_core` | **DRIFT-RETIRE** — review-theater; DW promotion/projection machinery governs reality |
| DW constellation (monolith + 38 satellites) | `ION/04_packages/kernel` | **DECOMPOSE-IN-PLACE** into bounded modules → these become the **engine** landed into the frame |
| DW `domain_weaver/` state (~329M / 14,404 files) | `ION/05_context/current/domain_weaver` | **MOSTLY RECLAIMABLE EXHAUST** (Phase 0 `repo_hygiene`) once kernel binds verified; keep `ACTIVE_*`/projection/promotion |
| `ION_DW_PRODUCTION_TESTBED_WORKTREE` | repo worktree | **DEAD-END** — `git worktree remove` after confirming nothing unmerged is needed |

---

## Reconciliation with the production-spine plan

- **Phase 1 target RESOLVED.** `production_core` home = the **adopted vNext frame** (repurpose dev `ION_VNEXT`,
  don't create a third root). The earlier "carrier-spine-first" framing is refined below.
- **`monolith_decomposition` is no longer a side track — it is the engine build.** `production_core` (frame) and
  `monolith_decomposition` (engine) run as one coordinated *"build the unified core"* effort.
- **Phase 0 hygiene still goes first** (legibility) and now also covers retiring the two drift sets + the dead worktree.
- **Naming sub-decision (non-blocking):** whether to rename `ION_VNEXT` → `ION_CORE`/`ION_PRODUCTION` now that it
  becomes the real core. Keep structure regardless.

---

## First slices (lowest-risk first; evidence-backed)

- **Slice 0 — stand up the core home (scaffolding, no engine logic).** Repurpose dev `ION_VNEXT` as the unified
  `production_core`: rewrite canon naming (Domain Weave → Domain Weaver), quarantine the drift (`domain_weave/` +
  `ion_vnext_production_authority_*`) with receipts + reference-grep, and mark the testbed worktree dead. Reversible.
- **Slice 1 — first clean carrier (near-zero coupling).** `ion_cursor_queue_runner` is the **only** runtime module
  with **zero DW coupling** (R1) — land it as the reference carrier in the frame's `04_carriers`, proving the carrier
  contract + the first real promotion path.
- **Slice 2 — first DW-engine seam.** Extract a DW **path-constants** module (A's safe first cut) + the
  **projection/promotion read+review builders** (`ion_domain_weaver_projection_records` + `build_domain_weaver_promotion_review`,
  binding the live projection/promotion JSON — R2's recommended slice) behind a facade, with tests + proof receipt + nemesis.
- **Last:** the 107-branch dispatcher `execute_domain_weaver_action` (A: extract last; keep a re-export facade to
  preserve the public surface).

---

## Caveats / non-claims

- No production-readiness claim; candidate decision; operator ratifies execution.
- "Retire" = archive/quarantine **with receipts + reference-grep** (reversible), never blind delete.
- Canon YAML rename (Domain Weave → Domain Weaver) is required so the frame doesn't perpetuate the drift name.
- Worktree removal requires a prior check for unmerged/untracked-but-wanted content.
- Decomposition must preserve DW's external public surface (27 public fns + path constants per A) via facades.
