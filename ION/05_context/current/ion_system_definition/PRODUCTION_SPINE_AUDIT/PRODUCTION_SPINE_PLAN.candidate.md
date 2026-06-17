# ION Production Spine — Synthesis & Plan (candidate)

**Date:** 2026-06-17
**Author:** ION North Star / IONOLOGIST
**Class:** candidate / not-accepted-state. No production-readiness claim. Nothing moved, extracted, or deleted by this document — it is a plan.
**Inputs (the three audits):**
- `PRODUCTION_SPINE_AUDIT/MONOLITH_SEAM_AUDIT.candidate.md` (A)
- `PRODUCTION_SPINE_AUDIT/EXHAUST_AND_DUPLICATION_CATALOG.candidate.md` (B)
- `PRODUCTION_SPINE_AUDIT/PRODUCTION_CORE_AND_VNEXT_INVENTORY.candidate.md` (C)

---

## OPERATOR CORRECTION (2026-06-17) — supersedes the "vNext is the clean-core target" assumption below

Operator: *"ION_VNEXT was created before Domain Weaver. Domain Weaver was built and evolved
afterward and has become such an integral aspect of ION that vNext may need to be fully or majorly
rebuilt. ION must be consolidated and weighed for how it all integrated with the Domain-Weaver evolutions."*

Evidence gathered this session:
- **Recency:** DW monolith last commit `2026-06-05`; dev `ION_VNEXT` last meaningful commit `2026-05-21`. DW evolved *after* vNext froze.
- **DW is integral:** `ion_domain_weaver.py` (49,513 L) + ~31 `ion_domain_weaver_*` modules, wired into
  agent/automation/orchestrator control planes, cockpit, codex+cursor queue runners, and the agent-mount system.
- **Two competing cores + a testbed = drift:** (a) dev `ION_VNEXT` (11M, self-declared "clean rebuild target",
  stalled, with its OWN parallel `06_context/domain_weave/` tooling + `ion_vnext_production_authority_*` cutover
  modules); (b) `ION_DW_PRODUCTION_TESTBED_WORKTREE` (386M, branch `codex/domain-weaver-production-testbed-candidate`);
  (c) the real DW constellation in the live kernel.

**Consequence:** Phase 1's target is NOT "extract into `ION_VNEXT/ion_core` as-is." The clean-core target is
**TBD**, decided by the **DW Integration & vNext Reconciliation reckoning** (new precursor to Phase 1).
Phase 0 (hygiene) and the monolith seam map (A) remain valid. The first extraction slice may be re-chosen as a
DW-aligned slice after the reckoning. Reckoning reports (in progress):
`PRODUCTION_SPINE_AUDIT/CORE_RECKONING/{DW_CORE_REALITY, VNEXT_DW_RECONCILIATION}.candidate.md`.

---

## 1. Convergent conclusion

All three audits, done independently, point the same way:

1. **The product is small, identifiable, and cleanly separable.** Real runtime is ~39M kernel (461 modules) + `03_registry` + carrier queue runners + `operator_cli` + `08_ui/joc_cockpit_shell` (C). It is buried under a ~5.8G / 54k-file exhaust shell, of which ~4.7G (`terminal_workers`, 11,703 files) is pure process receipts (B).
2. **A clean skeleton already exists in embryo.** `ION_VNEXT/02_kernel/ion_core` (30 modules + control tests) is real but slim; `03_products`/`04_carriers`/`05_runtime` are README-only (C). The vNext *missions* produced maps/receipts, not product — but the *destination folder* exists. We do not start from zero.
3. **The monolith is decomposable, not a black box.** `ion_domain_weaver.py` (49,513 lines) is hand-written (366 functions, 0 classes, no codegen), with a clear 11-module seam map, a known external contract (27 public functions + ~175 imported symbols, mostly path constants), and a safe extraction order — constants first, the 107-branch dispatcher (`execute_domain_weaver_action`, ~8,939 lines) last (A).
4. **The right first slice is NOT the monolith.** It is the **carrier contract spine** — already bounded, already proven end-to-end on both Codex and Cursor, lowest coupling (C). The monolith is deferred to a parallel track.
5. **"Not ready" is tractable, not permanent.** Charter criteria are real but 0/10 fully met; roughly half are partial (demo-only), half absent; `production_readiness.py` reports false with gaps G1–G8 (C). The partials prove the safety patterns already exist in demo form — the charter's own thesis is to *generalize* them, which is exactly what staged extraction does.

**Verdict:** strangler-fig extraction to a clean core is the correct path. A from-scratch rewrite is the wrong path — it would discard the genuinely working assets (carrier contract, context/continuity system, proven Codex+Cursor carriers, the demo-proven safety patterns).

---

## 2. Why strangler, not rewrite

A rewrite throws away 2+ months of hard-won, *working* primitives to chase a clean slate, and historically lands in the same swamp. The strangler pattern instead:
- Treats the 6.7G organism as a **read-only quarry**, not a thing to certify.
- Moves capability into a clean core **one bounded, tested, ratified slice at a time**.
- Makes each slice **burn down exactly one charter gap with a proof** — so "production readiness" becomes a shrinking backlog instead of a mantra.
- Finally **exercises the promotion path** (stuck at 0) by making the first slice the first real vNext promotion.

---

## 3. Phased plan

### Phase 0 — Hygiene & separation (domain: `repo_hygiene`, role Archivist)
Archive the exhaust **out of the product tree** and de-duplicate, so the product becomes legible. This is the safest, most reversible, highest-visibility first move and it is charter gap #2 (separation) in spirit.
- Archive `terminal_workers/` bulk receipts (~4.65G) — **keep** the `LATEST_*` pointer, the `codex_cli_launch_variant_forensics/` dir, and the last-tick chain (B).
- Collapse duplication: 3 extra `ion_domain_weaver.py` copies, ~47M/~1,300 redundant kernel files across 11 locations, nested `ION/ION/` (548K, already declared non-runnable by `REPO_AUTHORITY.md`), and the duplicate `ION_EXPORTS_LOCAL/codex_carrier_transfer/` tree (~0.3–0.61G).
- **Gating (mandatory):** archive (move), do not delete; honor B's load-bearing exception list; pre-move reference-grep of manifests/registry/`REPO_AUTHORITY.md`; write a move receipt; reversible.
- **Reclaims ~4.7G conservative (up to ~5.9G aggressive) — ~80% of the repo — without touching product.**

### Phase 1 — Build the unified clean core (domain: `production_core` + `monolith_decomposition`)
> **RESOLVED (2026-06-17):** reckoning complete → **Option A** (see `CORE_RECKONING/CORE_TARGET_DECISION.candidate.md`).
> Target = repurpose the dev `ION_VNEXT` **frame** as `production_core` and populate it by **decomposing the integral
> Domain Weaver** (engine); retire the parallel drift (`domain_weave/` + `ion_vnext_production_authority_*`); the
> DW production-testbed worktree is a dead end. First slices: (0) stand up the frame, (1) land the already-decoupled
> `ion_cursor_queue_runner` as the first clean carrier, (2) projection/promotion read+review builders + DW path-constants.

Original (superseded) framing: "extract the proven carrier spine into `ION_VNEXT/ion_core` as the first vNext promotion."
- Modules: `codex_cli` + `cursor_cli` carrier profiles, `ion_context_proof_gate`, `ion_template_action_gate`, `ion_codex_queue_runner`, `ion_cursor_queue_runner`, `ion_carrier_task_return`, `ion_carrier_onboard` (C).
- Each extraction carries its tests + a proof receipt + a nemesis/adversarial check (charter #10).
- Burns down concrete slices of #5 (governed activation) and #8 (certifiable release).

### Phase 2 — Front-door + receipt visibility (`production_core`)
`front_door_runtime_entry`, a trimmed `operator_cli`, `ion_receipt_core`, `ion_status`, and the existing `ION_VNEXT/00_front_door/*` (C). Burns down #7 (operator-visible reasons/changes/refusals/pending).

### Parallel track — Monolith decomposition (domain: `monolith_decomposition`, role Surgeon)
Carve `ion_domain_weaver.py` per A's seam map: paths/constants module first, dedupe the template facades, … the dispatcher **last** (keep a facade re-exporting moved handlers to preserve the 27-function public surface). **Not on the critical path** for the first promotion.

### Cross-cutting — Readiness burn-down (domain: `readiness_burndown`, role Release Steward)
Re-baseline the charter from the 2026-04-25 / V32 pin to current state (V96 + V97–V100). Convert the 10 criteria + G1–G8 into an **owned, shrinking backlog**, where each extraction slice flips a *named* gap to green with an *exit test* and a *who-can-flip-it* owner. This is the direct cure for "not ready as canon."

---

## 4. The four domains

| Domain | Role | Mandate | First task | Charter linkage |
|---|---|---|---|---|
| `repo_hygiene` | Archivist | Separate exhaust from product; de-dup | Phase 0 archival (gated) | #2 separation |
| `production_core` | Architect | Own `ION_VNEXT/ion_core` as the real product home; receive extractions | Phase 1 carrier spine | #2, #5, #8 |
| `monolith_decomposition` | Surgeon | Carve `ion_domain_weaver.py` into bounded testable modules | Extract paths/constants module | #1, #3, #8 |
| `readiness_burndown` | Release Steward | Re-baseline charter; own the shrinking gap backlog; nemesis per slice | Re-baseline + gap-to-slice map | all 10 + G1–G8 |

Division of labor: Composer subagents do the volume (extraction mechanics, archival passes, module carving); North Star defines the spine, gates, and ratifies each slice; a nemesis subagent enforces #10 per promotion.

---

## 5. Honest caveats / non-claims
- Nothing has been moved, extracted, deleted, or promoted. This is a candidate plan.
- Reclaimable GB is an estimate (~4.7G conservative; ~5.0–5.2G with verified mixed lanes; ~5.9G aggressive incl. exports).
- The charter-criteria counts are the auditor's read (0 fully met; ~half partial/demo-only, ~half none) and should be confirmed gap-by-gap during the re-baseline.
- Phase 0 must be gated by the load-bearing exception list (B §"Load-bearing exceptions") and a reference-grep; archive (reversible), do not delete.
- This plan stays in the candidate lane; the ratified version graduates to `ION/02_architecture/`.

## 6. Recommended first action
**Phase 0 (hygiene), executed incrementally with verification + receipts under North Star gating.** It is safe, reversible, frees ~80% of the repo, and makes every later phase legible — without risking any product.
