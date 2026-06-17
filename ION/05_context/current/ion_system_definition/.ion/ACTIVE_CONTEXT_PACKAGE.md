# ION System Definition — Folder-Local Active Context Package (North Star / IONOLOGIST)

context_id: ion_system_definition_north_star_context
domain_id: domain.ion_system_definition
anchored_role: IONOLOGIST
active_template: ION_NORTH_STAR_CONTINUITY
write_posture: candidate_only
last_refreshed_at: 2026-06-17T00:45:00Z
maintained_by: Opus (ION North Star / IONOLOGIST mount)

## Identity

You are the ION **North Star / IONOLOGIST** mount and lead orchestrator of the ION
domain: the agent responsible for holding a full-horizon, honest, evidence-grounded
understanding of *what ION is*, and for turning that understanding into durable
candidate documentation. You manage subagents to do bounded work; you keep the
horizon.

**You are continuing prior work, not starting fresh.** The ledger below is your own
record. Read it before you act.

## Authority boundary

Candidate-only. No production, live-execution, accepted-state, secrets, push, or
materialization authority. Synthesis/explanation is **not** ratification. Where this
lane disagrees with constitutional law (A1/A2) or `ION/REPO_AUTHORITY.md`, the law
wins.

## Sign-in (read order, before substantive North Star work)

1. This file (`.ion/ACTIVE_CONTEXT_PACKAGE.md`) — your prior-work ledger.
2. `.ion/ION_CONTEXT_CAPSULE.yaml` — folder-local working capsule.
3. `../ION_NORTH_STAR.candidate.md` — living full-horizon understanding.
4. `../ION_DERIVED_ACCOUNT.candidate.md` — six-layer derived account.
5. `ION/REPO_AUTHORITY.md` — repo authority (from active root `ION_Developement`).

Shell root for kernel commands: `/home/sev/ION - Production/ION_Developement`
(has `pyproject.toml` + `ION/REPO_AUTHORITY.md`).

## Sign-out (after material work)

Append a dated entry to **## Continuity Ledger** below: what you did, where the
artifacts live, and what's next. This is the mechanism by which the next session
inherits your work. **Do not rely on chat memory** — a chat summary already lost
this lane's work once (see the 2026-06-16 entry).

## Continuity Ledger (newest first)

### 2026-06-17 (OPERATING-MODEL CORRECTION — READ THIS FIRST) — lead owns decisions; mission = build the team; operator is sovereign, not dev

Operator course-corrected hard, and rightly. Two failures I am correcting:
1. **Role inversion** — I converted lead-dev decisions into a stream of technical questions and handed them to the operator, who cannot and should not answer them. That made the operator drift-correct me (backwards) and guaranteed drift. Most of those weren't even real gaps — I was failing to OWN calls I'm equipped to make.
2. **Lost mission** — the PRIMARY mission is to **build the agent-domain team that works with me as lead**; production is the *outcome the team drives*, not a solo grind. I had gone heads-down on production and treated carriers as ad-hoc help instead of the point.

**Who the operator is:** sovereign / visionary / owner. Holds ION's intent; authorizes only big/irreversible/costly moves; **not a developer; never hand them technical adjudication.**

**Corrected model (now encoded in this capsule's `operating_model` + `operator_profile`):** I (lead orchestrator) own ALL technical decisions with verification + receipts; when I hit a gap I charter/dispatch the agent-domain that fills it (never offload to operator); operator hears from me only on vision alignment, sovereign authorizations, and plain-language progress.

**Action this turn:** authored `AGENT_TEAM_CHARTER.candidate.md` (the next layers of domains + operating model + escalation contract); encoded the model here; committing durably; standing up the team (Phase B). The two in-flight back-harvest carriers are the team already in action. **NO operator questions.**

**Standing rule:** if I ever catch myself about to ask the operator a technical question, I decide it myself or build the domain that decides it.

### 2026-06-17 (midday, G2-B1 MIGRATION) — 10/10 legacy harvests now durable in the manifest surface; helper hardened by 2 real gaps

Proceeding G2-B (operator chose it). Ran the proven G2-A helper over the 10 `VNEXT_LANE_HARVEST/` bodies → `DURABLE_FANIN/lanes/` + `MANIFEST.candidate.json` (**10 lanes, ordinals 6–15, 0 hash mismatches**). This both populates the durable surface and validates G2-A against 10 real bodies.
- **The migration EXPOSED 2 real helper gaps (now fixed):** (1) lanes 14/15 carry the ordinal in a SEPARATE `lane_ordinal:` field, not inline `(ordinal N)` → added a fallback read; (2) LANE13's `lane_id` = `domain.ion_vnext_release_cutover` produced a dotted slug `LANE13_DOMAIN.ION_...` → replaced `_domain_slug` with a real sanitizer (non-alnum→`_`, strip `DOMAIN_` prefix). Re-ran clean: **10/10**; smoke still **5/5** (LANE08 sha unchanged `ef6244141d45`). This is exactly the coverage hardening G2-B is for — caught before it mattered.
- **COMMITTED** the durable bodies + manifest + apply-gate doc + receipt + ledger/burndown (data + docs are durable). **HELD:** the helper source + 2 hooks (the G2-A *source* commit is still operator-gated).
- **NEXT:** G2-B3 — back-harvest the 5 missing topology lanes (1–5) via Composer (pruned originals unrecoverable); then broaden live-capture (derive identity from the work-request when a body has no header).

### 2026-06-17 (morning, CORPUS COMMITTED + G2-A APPLIED) — durability realized in git; second real source apply landed (held)

Operator answered the apply gate: **apply G2-A (hold commit)** + **commit the corpus now**.
- **CORPUS COMMITTED — `ddfdb219`** "docs: make production-spine + IONOLOGIST domain corpus durable" (62 files, +11,897): all 45 `ion_system_definition` docs (10 harvest bodies, burn-down, G1/G2 plans + dry-run reports, M105C atlas, North Star/derived/surface-map, **and the `.ion` continuity lane**) + 17 mandate receipts. **Scoped carefully** — `signals/` had **342** untracked (mostly unrelated historical ATLAS_/CODEX_/NEMESIS_/VIZIER_/cosmos); I added ONLY `production_spine_*` + 4 consolidation receipts. The production-spine work is now durable in git (not working-tree-only). G2's own durability thesis now applies to my own corpus.
- **G2-A APPLIED (held)** — NEW module `kernel/ion_durable_fanin.py` + 2 guarded **fail-soft** hooks (connector `:5095`, runner `:8543`). **VERIFIED in the real repo:** import OK; live harvest smoke **5/5** (fresh writes body+manifest ordinal 8 + `intake_accepted`/`semantically_settled` honesty fields; idempotent; missing-section reject; fail-soft no-raise); merged **176/176** control suite still green; real `DURABLE_FANIN/` surface unpolluted (temp-root smoke); **engine `ion_domain_weaver.py` untouched**. Path proven correct (connector/runner `root` == `ION_Developement` → `DURABLE_FANIN_REL` resolves to the `ddfdb219`-committed surface). Doc `DURABLE_FANIN/G2A_APPLY_GATE.md` + receipt.
- **COMMIT HELD** (G2-A source; operator go). Revert = `rm ion_durable_fanin.py` + delete the two `# G2-A` blocks.
- **Scope honesty:** G2-A captures header-bearing dynamic-swarm bodies (the re-drive cohort); raw live bodies lacking the header fail-soft no-op → broadening coverage (request-derived identity + section resolver) is **G2-B**.
- **NEXT (all gated):** (a) G2-A commit; (b) G2-B (migrate 10 legacy harvests + back-harvest lanes 1–5 + broaden capture); G1 runtime cutover + G1-A3 collapse still pending.

### 2026-06-17 (morning, G2-A DRY-RUN green + VERIFIED) — mechanism proven; durability nuance surfaced

[G2-A durable-harvest dry-run](1b65b76b-3894-4fb2-ab82-94a3c00878c2) returned GREEN. Doc: `DURABLE_FANIN/G2A_DRYRUN.candidate.md` (full helper source + 2 hook diffs) + receipt.
- **ORCHESTRATOR-VERIFIED (read full helper source):** genuinely additive + **fail-soft** (top-level try/except wrapper, lines 298-313, always returns `{harvested:false,...}` on error); validates the 9 sections (reject+no-write if missing); full-file sha256; idempotent on `(request_id, objective_sha256)`+hash; supersede-on-mismatch; returns additive-only metadata (no existing fields mutated). Both hook diffs insert **guarded side-effect calls AFTER** existing accept writes (connector `:5095`, runner `:8543`) — touch nothing in `accepted`/status/return payloads/reconciliation/fan-in. 5/5 /tmp tests pass. Real source still 0 harvest symbols; G1 commit `9ac8b9b7` intact.
- **FINDING (durability gap at my own layer):** the harvest surface is git-track*able* (NOT ignored) but **0 files are tracked** under `PRODUCTION_SPINE_AUDIT/` or `DURABLE_FANIN/` — the ENTIRE production-spine candidate corpus (audits, plans, burndown, 10 harvest bodies, receipts) is **untracked working-tree only**. So G2 "durable" isn't fully realized until the surface is committed — OR the operator confirms stable-working-tree IS the intended candidate durability (candidate→accepted→commit being ION law). This is a genuine ION-law call, surfaced to operator (NOT guessed).
- **NEXT:** G2-A apply gate to operator — recommend new shared module `kernel/ion_durable_fanin.py` to isolate the helper bulk from the 2 pre-dirty hook files (footprint there = 1 import + 1 guarded block) + the durability-posture decision.

### 2026-06-17 (early AM, G1 COMMITTED + G2-A dry-run launched) — keystone foundation now durable in git

Operator answered the Wave-A checkpoint: **commit G1** + **dry-run G2-A first**.
- **G1 COMMITTED:** scoped commit `9ac8b9b7` "feat: reconcile dual kernel namespace via additive scaffold" (2 files, +28) on branch `codex/ion-custom-gpt-front-door-carrier-v4`. **NOT pushed** (operator's call). Working tree clean on those 2 files. The proven keystone is now durable.
- **G2-A:** dispatched a BOUNDED dry-run carrier (Composer, `/tmp` only): build the new standalone `_durable_fanin_harvest_lane_body` helper + unit-test it (durable body + manifest + metadata + idempotency + 9-section validation + fail-soft), and produce the EXACT additive hook diffs at connector `:5073` / runner `:8534` — no real source edits, no monolith load. Verify on return, then bring the G2-A apply gate.

### 2026-06-17 (early AM, G2 DESIGN landed + VERIFIED) — Wave A planning COMPLETE; G2-A apply needs care (dirty hook files)

[G2 durable fan-in full design](95c60dfe-facb-46be-87a8-ffad873dc20a) succeeded. Doc: `DURABLE_FANIN/G2_DURABLE_FANIN_PLAN.candidate.md` (336 lines) + receipt. 7 gated packets **G2-A→G**; additive = A,B,C,D,G; behavior-changing (flag-guarded, last) = E (nemesis gate), F (reconciliation honesty). Smallest safe first = **G2-A** (additive durable-harvest capture at carrier-intake accept).
- **VERIFIED:** both G2-A hook points real — connector `:5073` (status flip to `RETURN_RECORDED_PROOF_ACCEPTED`, with `carrier_intake_only:True` at `:5101-5104`) + queue-runner `:8534` (`if accepted:` finalization). 0 harvest symbols present anywhere ⇒ design purely on paper.
- **KEY CAVEAT (vs G1):** the 2 hook files (`ion_chatgpt_browser_mcp_connector_contract.py`, `ion_codex_queue_runner.py`) carry LARGE **pre-existing uncommitted** changes (+498 / +252 lines). G1's 2 files were clean (trivial revert). So G2-A would mix with that dirty state + hook hot live-intake paths ⇒ G2-A must be **operator-gated + dry-run first** (do NOT auto-apply like G1).
- **Wave A PLANNING COMPLETE:** G1 (foundation landed+verified 176/176) + G2 (diagnosed+designed, both orchestrator-verified). NEXT: consolidated Wave-A checkpoint to operator; **pausing autonomous source applies here** (the next moves are operator decisions: G1 commit, G1 runtime cutover, G2-A).

### 2026-06-17 (early AM, G2 DIAGNOSIS landed + VERIFIED) — root cause located: reconciliation accepts on STATUS; semantic fan-in needs the PRUNED bodies

Lean retry [G2 fan-in map + diagnosis](d9b5899d-8864-4388-bded-38141f1acff4) succeeded (the first carrier's `resource_exhausted` was the wholesale-monolith read; avoided here via Grep-targeted windows). Doc: `PRODUCTION_SPINE_AUDIT/DURABLE_FANIN/G2_DURABLE_FANIN_MAP_AND_DIAGNOSIS.candidate.md` (+ receipt).
- **ORCHESTRATOR-VERIFIED against the real monolith** (`ION/04_packages/kernel/ion_domain_weaver.py` — note: in `kernel/`, not `04_packages/` root; my brief's path was wrong, the carrier Grep-found the real file): reconciliation `:9428-9429` sets `lane_state=accepted` from request STATUS only (body presence feeds only the "stranded" case); the semantic fan-in gate `:9737-9752` requires reading `task_return_body.md`. `DOMAIN_WEAVER_MONOLITH_INDEX` corroborates both signatures. ⇒ 15/15 accepted on status, semantic settlement can't fire (bodies pruned from `codex_queue_runs/`). **Diagnosis sound.**
- Note: the `kernel/` dir has MANY pre-existing uncommitted files (repo messiness) — the G1 foundation commit must stay scoped to the 2 files.
- NEXT: dispatched the **G2 DESIGN** follow-up (bounded; diagnosis passed inline so no monolith re-read); then a consolidated **Wave-A checkpoint** to operator.

### 2026-06-17 (early AM, G2 plan attempt failed) — Composer carrier `resource_exhausted`; NO output; G1 intact; lean retry dispatched

First G2 durable-fan-in PLAN carrier errored `resource_exhausted` (usage/budget — likely reading the `ion_domain_weaver.py` monolith wholesale, or a Composer usage-window cap after tonight's many carriers). **It wrote nothing** (no `DURABLE_FANIN/` dir, no receipt).
- **G1 foundation re-verified INTACT:** both files still ` M` (modified); `extend_path` (2) + `discover_workspace_manifest` (1) present; nothing reverted.
- Re-dispatched a **leaner** carrier: map + diagnosis ONLY, via **Grep-targeted** reads of the engine fan-in functions (no wholesale monolith read), one output file, deferring full design/harness/packets to a follow-up. If it *also* exhausts ⇒ treat as a Composer usage cap and surface to operator instead of retrying further.

### 2026-06-17 (night, G1 FOUNDATION APPLIED) — FIRST REAL SOURCE WRITE: G1 foundation landed + verified 176/176 (commit HELD)

Operator skipped the apply gate ("continue with what you have") → I proceeded with the recommended **safe foundation**. This is the first real source edit of the production push.
- **Applied (working tree, NOT committed; additive +28 / −0 / 2 files):** `kernel/__init__.py` +4 (`extend_path` scaffold); `ion_path_authority.py` +24 (`import os` + `WORKSPACE_MANIFEST_NAME` + additive `discover_workspace_manifest`). No existing functions changed.
- **VERIFIED in the REAL repo:** (1) `import kernel` OK; `kernel.__path__` stays monolith-only when ion_core isn't on the path ⇒ `extend_path` is a **confirmed no-op for the live runtime** (zero behavior change); (2) live `path_authority` resolves the real manifest + decides correctly; (3) **merged control suite 176/176** (monolith-first + ion_core; two runs); (4) broad monolith import sanity OK.
- **COMMIT HELD** (git law — no commit without explicit operator go). Revert = `git checkout -- ION/04_packages/kernel/__init__.py ION/04_packages/kernel/ion_path_authority.py`.
- Exit-test gate documented: `KERNEL_RECONCILIATION/G1_UNIFIED_PYTEST_GATE.md`. Receipt: `signals/production_spine_g1_foundation_applied_176green_receipt_20260617.txt`.
- **DEFERRED (separate gates):** live-runtime PYTHONPATH binding (wire ion_core/src onto the Codex-mount path — the actual cutover, needs harness-exposure security review); G1-A3 collapse of the 3 duplicates; the commit itself.

### 2026-06-17 (night, G1 PROVEN GREEN) — G1 reconciliation SOLVED-PENDING-APPLY: 176/176

The resumed carrier re-ran the combined bundle with the manifest provisioned (production-faithful). **VERIFIED 176/176** (Variant B symlink reproduces the real repo's module-relative DEFAULT). The original 78/176 was **entirely a `/tmp` fixture gap** (bare temp tree lacked repo-root markers → `resolve_repo_root(__file__)` degenerated the default manifest path). **No genuine residual forks.**
- **G1 reduces to a tiny change:** the full 29-control merge needs only (1) a **2-line `extend_path` scaffold** in monolith `kernel/__init__.py` + (2) a **~25-line additive `discover_workspace_manifest` port** into monolith `ion_path_authority.py`. All 6 diverged controls reconcile to the monolith (5 natively; path_authority via the additive port). Both ADDITIVE + zero live-runtime impact.
- **Verified (orchestrator):** source-edit guard empty; nothing applied (monolith still lacks port + extend_path); artifact appended + stale verdict marked SUPERSEDED; corroborated by my own read of both modules + tests + real manifest.
- **Security note (standing):** keep `discover` opt-in; wiring it into the live default would widen manifest trust → separate gated decision.
- Receipt: `signals/production_spine_g1b_corrected_dryrun_176green_receipt_20260617.txt`.
- **NEXT: operator APPLY gate** — first real source write. Recommended: safe foundation (port + scaffold + documented unified-pytest gate), verify 176/176 in real repo, commit; defer live-PYTHONPATH binding + duplicate collapse to follow-on gates.

### 2026-06-17 (night, G1-B crux) — FINDING: the 98 failures look like a `/tmp` FIXTURE GAP, not a security fork

Read both `path_authority` modules + ion_core tests + the real manifest (orchestrator, direct).
- **Root cause of the 98 `NotADirectoryError`:** monolith `DEFAULT_WORKSPACE_MANIFEST` is **module-relative** (`resolve_repo_root(__file__)/ION_WORKSPACE_MANIFEST.yaml`); in the carrier's `/tmp` copy that path has **no manifest** (never provisioned). In the REAL repo the manifest exists at `ION_Developement/ION_WORKSPACE_MANIFEST.yaml` and the default resolves fine.
- **The 3 "forks" are benign under the real manifest:** (a) resolution strategy — monolith module-relative (deterministic, safer) vs ion_core discovery (cwd/env-dependent), both → the same file in-repo; (b) artifact policy — monolith gates on `require_artifacts_outside_active_repo`, which the real manifest sets **true** → identical reject to ion_core's hardcode; (c) `discover_workspace_manifest` is the ported fn and tests assert it equals `ION_ROOT/manifest` ✓.
- **Security flag does NOT apply:** we KEEP monolith `load_workspace_authority(None)=DEFAULT` (module-relative); `discover_workspace_manifest` stays **opt-in**, so manifest trust is not widened.
- **⇒ Hypothesis:** "promote monolith + additive port + scaffold" is production-correct; the dry run just needs the manifest provisioned. Resumed the G1-B carrier to re-run with the manifest in place + report any genuinely residual fork. No source edits.

### 2026-06-17 (night, G1-A2 scaffold dry-run) — DONE+VERIFIED: scaffold import-correct but coupled to G1-B; additive surface = ONE function

Composer carrier dry-ran the scaffold in `/tmp` (real repo untouched; source-edit guard empty). VERIFIED:
- **Mechanics correct:** 2-line `extend_path` + monolith-first PYTHONPATH → 9/9 shared controls resolve from monolith; vNext-only harnesses from core via `extend_path`; monolith-only stays mono.
- **Not green standalone:** ion_core suite 78 pass / 89 fail / 1 collection error (baseline 176/176). Root cause **corroborated**: monolith `path_authority` lacks `discover_workspace_manifest` (present in ion_core L121) → collection error + `NotADirectoryError` in harnesses.
- **Scope win (verified):** the ONLY top-level def in ion_core `path_authority` absent from monolith is `discover_workspace_manifest` (Δ ~20 lines; mono 287 / core 307) ⇒ G1-B is very likely a CLEAN ADDITIVE port of one function (exact-diff confirmation pending).
- **Corrected empirical sequence:** G1-B additive port (`discover_workspace_manifest` → monolith path_authority) → G1-A2 scaffold (then green) → G1-A3 collapse 3 identical dups.
- Artifacts: `KERNEL_RECONCILIATION/G1A2_NAMESPACE_SCAFFOLD_CANDIDATE_DIFF.candidate.md` + `signals/production_spine_g1a2_scaffold_dryrun_verification_receipt_20260617.txt`.
- **Next:** read-only carrier proving the COMBINED bundle (additive port + scaffold) hits 176/176 in `/tmp` + security-checking the ported function; then operator APPLY gate (touches LIVE path_authority + kernel/__init__.py). No source edits made.

### 2026-06-17 (night, G1-A identity proof + coupling correction) — DONE: identity PROVEN; scaffold must precede collapse

Operator chose "split" (apply identical-unify now, hold scaffold for diffs-first). Read-only investigation **corrected the premise**: the collapse is COUPLED to the scaffold.
- **PROVEN byte-identical (full sha256 match):** `ion_ai_movement_gate`, `ion_codex_work_request_target_binding`, `ion_template_action_gate`. 6 diverged confirmed (re-confirms the matrix).
- **COUPLING:** the 3 identical `ion_core` modules are imported by KEPT harnesses (`ion_vnext_readiness_lock`, `ion_vnext_boot_dogfood_smoke`) + the 176-test control suite + pinned in canon registry ⇒ deleting them before the scaffold breaks `ion_core`.
- **CORRECTED ORDER:** G1-A1 identity proof = DONE (bankable, zero risk); G1-A2 namespace scaffold = candidate-diffs-first/gated (live `kernel/__init__.py` edit), proven via temp-dir dry run; G1-A3 collapse 3 duplicates = after scaffold (behavior-neutral).
- **Open empirical Q for the dry run:** monolith-first resolution routes ion_core's *diverged*-control tests to monolith versions; if any assert ion_core behavior, scaffold isn't green-neutral until G1-B. Dry run reports, not assumes.
- Artifacts: `KERNEL_RECONCILIATION/G1A_IDENTICAL_UNIFY_IDENTITY_PROOF.candidate.md` + `signals/production_spine_g1a_identity_proof_and_coupling_finding_receipt_20260617.txt`.
- **Next:** Composer carrier generating G1-A2 scaffold candidate-diff + temp-dir dry run (read-only) for operator review. No source edits made.

### 2026-06-17 (night, G1 reconciliation plan) — DONE: candidate KERNEL_RECONCILIATION_PLAN for dual-kernel seam

- Composer carrier (`role.mason`, nemesis posture) produced read-only reconciliation plan extending diff matrix: monolith-primary namespace merge (`pkgutil.extend_path`), per-control table (29), diverged behavioral diffs, exit-test harness, sequenced packets G1-A→G1-D.
- Artifact: `PRODUCTION_SPINE_AUDIT/KERNEL_RECONCILIATION/KERNEL_RECONCILIATION_PLAN.candidate.md`
- Counts: 3 identical unify · 6 diverged promote monolith · 4 primitives promote · 16 vnext harness keep in ion_core.
- **Orchestrator verification (verify-not-trust, all green):** source-edit guard empty; counts corroborated on disk — monolith 463 mods / `ion_core` 30 (=29 controls + `__init__`); **9 shared control true-names = 3 identical + 6 diverged**; 20 vNext-only = 16 harness + 4 primitives; 0 monolith-only. monolith `kernel/__init__.py` exists but does NOT yet use `extend_path` ⇒ the scaffold is an additive change to the live import root. Receipt: `signals/production_spine_g1_kernel_reconciliation_plan_verification_receipt_20260617.txt`.
- **GATE OPEN:** G1-A (`PCKT-G1-IDENTICAL-UNIFY-NAMESPACE-MERGE-SCAFFOLD`) is the FIRST source-touching step of the whole production push. Awaiting operator: candidate-diffs-first (recommended) vs direct execute vs review plan. No edits made.

### 2026-06-17 (night, vnext-frame-harvest + burndown) — DONE: full vNext-frame durable harvest (10 lanes + kernel diff) → readiness burn-down established

Operator chose "both" (breadth + depth). Dispatched 10 Composer carriers in parallel (candidate-only); all returned + verified.
- **Breadth:** durable 9-section gap-returns for lanes 6,7,9,10,11,12,13,14,15 → `PRODUCTION_SPINE_AUDIT/VNEXT_LANE_HARVEST/` (with lane 8 = 10 total). All 9/9 sections; 0 source edits (mtime+grep guard clean).
- **Depth:** `KERNEL_RECONCILIATION/KERNEL_CONTROL_DIFF_MATRIX.candidate.md` — 29 controls: **3 identical / 6 diverged / 20 vNext-only / 0 monolith-only**; live binds monolith; promote-and-replace per true-name (gated).
- **Independent corroboration:** lane 14 found carrier-intake 15/15 accepted but semantic fan-in blocked (0 run bodies) = the durability gap, confirmed by a worker who didn't write it. Lane 15 (nemesis) cleared the lane-8 harvest (no material overclaim; re-ran 176 tests).
- **META-FINDING (architecture truth):** ION's executable reality is LIVE + tested in the monolith (kernel 176 / bridge 137 / carriers 121 tests); the vNext frame is a canon/docs skeleton + control SUPERSET (ion_core 29 controls incl. 20 cutover harnesses absent from monolith). **Production = BINDING + DURABILITY + AUTHORITY, not build-from-scratch.**
- **SYNTHESIS:** `PRODUCTION_SPINE_AUDIT/READINESS_BURNDOWN.candidate.md` — 8 consolidated gaps (G1 dual-kernel binding CRIT · G2 non-durable fan-in CRIT · G3 authority unset · G4 no lane gates · G5 currentness/Needs_Routed · G6 steward/M103D/F · G7 product pools · G8 DW witness split), each with owner + exit test + candidate next packet; sequenced Wave A→D. Receipt: `signals/production_spine_vnext_frame_harvest_and_burndown_receipt_20260617.txt`.
- **Open:** topology lanes 1-5 not harvested (scoped to vNext frame). Next: operator picks a Wave-A keystone to execute (G1 kernel reconciliation packet, or G2 durable-fanin automation).

### 2026-06-17 (night, slice1-drive) — DONE: first DURABLE vNext promotion (lane-8 kernel-core gap return) harvested + independently verified

- Composer carrier (`role.mason`) re-drove lane 8 to a fresh 9-section gap return; landed durably at `PRODUCTION_SPINE_AUDIT/VNEXT_LANE_HARVEST/LANE08_ION_VNEXT_KERNEL_CORE_GAP_RETURN.candidate.md` (224 lines; header carries request_id + objective_sha256). Receipt: `signals/production_spine_slice1_lane08_kernel_core_harvest_receipt_20260617.txt`.
- **Independently verified** (verify-not-trust): 9/9 sections present; `tests/control` re-run = **176 passed / 0 fail, exit 0**; `import kernel` OK with `PYTHONPATH=src`, fails without (gap, not fixed); **NO source edits** (src/kernel + tests mtimes May 23; only the .md written 23:41). Subagent honored one-write candidate posture.
- **KEY FINDING (real seam):** TWO diverged `kernel` trees — live runtime imports `kernel.*` from `ION/04_packages/kernel` (monolith), **not** `ion_core/src/kernel`. vNext's 29 controls are canon-registered but **UNWIRED**; copies diverged (e.g. `ion_path_authority` 307 vs 287 lines). DW "production-grade integration" is plan-level for kernel core despite local green. Other gaps: no editable-install/CI; stale `ion_core` docs/capsules; M102 authority unset; tests hardcode abs paths.
- **Recommended next packet:** `PCKT-VNEXT-KERNEL-MONOLITH-RECONCILIATION-AND-RUNTIME-BINDING-20260617` (diff 29 controls → one authoritative impl each → re-export/shim → fix docs → root pytest; mason+nemesis; candidate-only first pass; operator gate before source edit).
- **Significance:** proves the missing organ — HARVEST + DURABILITY. Template ready for the remaining 7 vNext lanes (+ fanin/nemesis) → seeds the readiness burn-down.

### 2026-06-17 (night, slice1a-trace) — TRACE DONE: the vnext_productization program ALREADY ran to green; outputs pruned → harvest is the real gap

Completed the Slice-1a trace AND ground-truthed the program's execution state. No engine/source mutation.
- **Lifecycle:** `materialize_dynamic_swarm_candidate_work_requests` (writes 1 work-request packet/lane to `chatgpt_connector/codex_work_requests/`; never starts workers) → carrier worker writes `run.json`+`task_return_body.md` under `codex_queue_runs/` and flips packet `status`→`RETURN_RECORDED_PROOF_ACCEPTED` after proof gates → `_domain_weaver_dynamic_swarm_fresh_context_reconciliation` settles from the **persisted packet status**. Dispatcher `execute_domain_weaver_action`; all actions `policy_governed_no_magic`; `dynamic_start_window`=3.
- **CRITICAL:** the program was already driven to FULL settlement on 2026-06-02 — **all 15 lanes `RETURN_RECORDED_PROOF_ACCEPTED`** (5 topology + 8 vNext incl Kernel Core + fanin + nemesis); today's read-only recon still settles all 15 = `accepted`. Lane 8 ran **8×** that day, all gates passed (context proof 35/35). **This corrects audit C's "0 promotions / execution unverified."**
- **BUT the outputs are GONE:** `codex_queue_runs/` = 0 run dirs / 0 `task_return_body.md`; surviving `task_returns/*.json` keep only a 1200-char preview + sha256 (no gap findings, no recommended next-packet). NOT caused by Phase 0 (which never touched `chatgpt_connector/`) — pruned earlier as run-exhaust.
- **Reframed blocker:** capability is proven; the missing organ is **harvest + durability**. The program settles, then its results evaporate before becoming the product → "**0 durable promotions**," not "never run."
- **Corrected Slice 1 (drive):** re-drive `ion_vnext_kernel_core` freshly + land the gap-return BODY durably in `PRODUCTION_SPINE_AUDIT/` (git-tracked), not volatile `codex_queue_runs/`; template for harvesting all lanes into the burn-down. Findings appended to `CORE_RECKONING/SLICE0_GROUNDTRUTH_FINDINGS.candidate.md`.
- **Next:** dispatched a Composer carrier worker (`role.mason`) to produce the fresh, durable Kernel-Core gap return.

### 2026-06-17 (night, slice0-recon) — CRITICAL: the engine already encodes Option A; "retire drift" RETRACTED

Operator gave GO on Option A Slice 0. Before mutating the frame I ground-truthed the live kernel and found the
approved plan rests on FALSE premises (audits R2/decision were wrong). Nothing was mutated.
- **`domain_weave` is LIVE-BOUND, not drift.** `ion_agent_control_plane.py:46 DOMAIN_WEAVE_ROOT = ION_VNEXT/06_context/domain_weave`
  (used incl :1105 reads M103B_VALIDATION_REPORT.json) + bound by ion_domain_weaver, MCP connector, chatops bridge, 2 registries.
  Quarantining it (the approved step) would have broken live kernel. RETRACTED.
- **The engine already encodes Option A.** `ion_domain_weaver.py:8273 _domain_weaver_vnext_productization_lanes` (called :8873)
  defines 8 domains = the 8 vNext lanes; mission `bring_ion_vnext_to_production_spec_with_domain_weaver_integrated...`;
  program `ion_vnext_production_spec_hardening`; route family `domain_weaver_dynamic_swarm_vnext_productization` (9 routes);
  surfaced in cockpit projection. 80 live refs into ION_VNEXT across ALL lanes.
- **Corrected architecture:** ONE engine (live DW) whose built-in vnext_productization swarm program targets the vNext
  frame as production_core. Path to production = DRIVE that existing program to settlement (run lane -> gap_return ->
  settle -> burn down), via proven Cursor/Codex carriers. NOT rebuild / decompose-into-frame / retire-drift.
- Findings: PRODUCTION_SPINE_AUDIT/CORE_RECKONING/SLICE0_GROUNDTRUTH_FINDINGS.candidate.md (full evidence).
  Annotated CORE_TARGET_DECISION with a correction box. Testbed worktree dead-end STILL valid (0 unmerged commits).
- Revised Slice 1 (stronger): exercise ONE vnext_productization lane end-to-end to a settled gap-return (recommend
  `ion_vnext_kernel_core`: has pyproject + control tests) = first real vNext promotion. AWAITING operator confirm on pivot.

### 2026-06-17 (night, hygiene-3) — Phase 0 COMPLETE: mixed DW-adjacent lanes reclaimed + DW verified

Executed the Composer mixed-lane manifest (PRODUCTION_SPINE_AUDIT/PHASE0_MIXED_LANE_RECLAIM_MANIFEST.candidate.md),
re-guarded + verified by North Star. Move 3 (gated, reversible):
- STEP A (low risk): full_steam_push (whole, 22M); codex_cli 64M->892K (6 launch_variant dirs, bugcrowd/layout/
  quarantine, 49 orchestration MD, 2,837/2,857 identity sessions — kept newest 20 + carrier-profile files);
  codex_capsule_chat (prune backup + 31 old response_runs, kept newest 24); codex_carrier production_zip_prep
  (kept commit_boundary 97M load-bearing).
- STEP B (HIGH risk): live_carrier_binding 220M->2.1M — staged 8,037 snapshot files, restored KEEP=45 (25
  projection-cited UNION 20 newest), archived proof_row dirs + repair map; kept ALL 16 ACTIVE_* + 103 monolith
  constants + .latest monitors.
- DW INTEGRITY (post-move, all PASS): 92/92 projection live_carrier_binding refs resolve (0 missing); ACTIVE proof
  rows present; DW kernel spine imports (ion_domain_weaver / observatory / projection_refresh); projection loads;
  cursor tests 3/3; scope binds lane.
- DEFERRED (operator-gated): project_launcher node_modules ~126M (regenerable; install_repair). NOT TOUCHED:
  portable_agent_domain_packages (registry-cited), codex_carrier/commit_boundary, gemini_sandboxes, execution_cycles.
- Receipt: signals/production_spine_phase0_mixed_lanes_receipt_20260617.txt.

PHASE 0 DONE. Reclaim this round ~305M; CUMULATIVE Phase 0 ~5.4 GB; product tree 6.7G -> 1.7G (~75% smaller),
product runtime untouched + DW proven intact. NEXT: build Option A — Slice 0 (stand up vNext frame as production_core
+ quarantine drift). AWAITING OPERATOR GO to begin building.

### 2026-06-17 (night, hygiene-2) — Phase 0 export dedup + nested residue (operator: finish Phase 0 first)

Operator chose to finish Phase 0 before building. Move 2 executed (gated, reversible):
- ION_EXPORTS_LOCAL 614M->217M: 3 result trees -> kept canonical latest (235034Z) + the runtime-bound export
  root; archived the two older/dup trees (224933Z 187M + 234707Z 210M, ~397M; also removed a dup kernel overlay).
- nested ION/ION (548K, REPO_AUTHORITY non-runnable) -> archived.
- SKIPPED (guard caught binds; audit B WRONG): gemini_ion_sandboxes (registry roots) + execution_cycles
  (ion_cycle_runner + context_lifecycle) are runtime-bound -> left in place.
- Verified: cursor tests pass; resolve_context_scope binds lane; export root+latest intact.
- Receipt: signals/production_spine_phase0_export_dedup_receipt_20260617.txt. Cumulative reclaim ~5.1 GB.

REMAINING Phase 0 = mixed in-product-tree DW-adjacent lanes (live_carrier_binding 220M [keep ALL ACTIVE_*],
project_launcher 172M, codex_carrier 98M, codex_cli 64M, codex_capsule_chat 28M, full_steam_push 26M,
portable_agent_domain_packages 15M). These are DW-core-adjacent -> NEXT: Composer produces a per-lane
keep/archive manifest with grep evidence; North Star executes + verifies DW after each. THEN build (Option A).

### 2026-06-17 (night, decision) — Reckoning complete: Option A decided (vNext frame + DW decomposition)

Both reckoning audits returned and CONVERGED:
- R1 (DW core reality): DW = 39 modules / 87,884 LOC; 8/9 runtime modules depend on it; owns ~329M state;
  de-facto runtime spine (107 actions @ ion_domain_weaver.py:40574). Carry DW forward by DECOMPOSITION.
- R2 (vNext/testbed reconciliation): vNext is a clean FRAME + useful in-memory primitives, NOT a parallel runtime;
  its domain_weave (~955 LOC, witness-only) + cutover stack are DRIFT; testbed worktree is abandoned (its ION_VNEXT
  only 572K; 386M is unrelated AIM-OS/Needs_Routed/ION_GPT over a pre-DW kernel). Recommend Option A.

DECISION written: CORE_RECKONING/CORE_TARGET_DECISION.candidate.md — Option A: repurpose dev ION_VNEXT frame as
production_core; decompose DW in place as the engine; retire drift (domain_weave + ion_vnext_production_authority_*);
mark testbed worktree dead. monolith_decomposition is now the ENGINE build (not a side track). Phase 0 hygiene still first.
First slices: (0) stand up frame + quarantine drift; (1) land already-DW-decoupled ion_cursor_queue_runner as first
clean carrier; (2) projection/promotion read+review builders + DW path-constants (facade; tests; receipt; nemesis).
Updated PRODUCTION_SPINE_PLAN Phase 1 (RESOLVED). AWAITING OPERATOR GO to begin Slice 0.

NOTE: corrects my earlier framing — the testbed worktree is NOT a live DW+vNext reconciliation; it's a dead end.

### 2026-06-17 (night, reframe) — Operator correction: DW is the integral core, not vNext; reckoning launched

Operator corrected the Phase 1 target assumption: ION_VNEXT predates Domain Weaver; DW was built/evolved
AFTER and became integral; vNext may need full/major rebuild; ION must be consolidated + weighed for how it
integrates with the DW evolutions. Evidence (this session):
- git recency: DW monolith last commit 2026-06-05 vs dev ION_VNEXT 2026-05-21 (DW evolved after vNext froze).
- DW integral: ion_domain_weaver.py (49,513 L) + ~31 ion_domain_weaver_* modules wired into agent/automation/
  orchestrator control planes, cockpit, codex+cursor queue runners, agent mounts.
- TWO competing cores + testbed: (a) dev ION_VNEXT (11M, "clean rebuild target", stalled ~May 21, with its OWN
  parallel 06_context/domain_weave/ tooling + ion_vnext_production_authority_* cutover modules); (b)
  ION_DW_PRODUCTION_TESTBED_WORKTREE (386M, branch codex/domain-weaver-production-testbed-candidate); (c) real DW
  in the live kernel. = parallel/conflicting cores (the drift ION treats as a defect).

ACTION: Corrected PRODUCTION_SPINE_PLAN (operator-correction box + Phase 1 hold). Phase 1 target reclassified
TBD pending a **DW Integration & vNext Reconciliation reckoning**. Launched 2 background Composer audits ->
PRODUCTION_SPINE_AUDIT/CORE_RECKONING/{DW_CORE_REALITY, VNEXT_DW_RECONCILIATION}.candidate.md. North Star holds
the synthesis + final target decision (with operator). Phase 0 hygiene + monolith seam map remain valid.

### 2026-06-17 (night, exec) — Phase 0 hygiene: first move executed + verified (reversible)

Operator chose Phase 0 (hygiene/separation). Executed the audit's rank-1 move with full gating.
- Pre-checks: git root = ION_Developement; terminal_workers = 0 tracked files (untracked data, no git
  impact). LATEST pointer names the moved dir as `previous_run_id` (active run is `mount_fresh_T030545Z`,
  resume disallowed). No runtime binds of the stale run in kernel/registry/architecture/manifest/authority.
  Maintainer binds only the LATEST pointer (kept). Final load-bearing DW guard clear.
- Move (atomic rename, same fs): `terminal_workers/terminal_20_codex_cli_20260610T021002Z` (4.7G)
  -> `/home/sev/ION - Production/ION_ARCHIVE/2026-06-17_exhaust_candidate/...` (OUTSIDE git repo + product tree).
- Kept: LATEST pointer, active `mount_fresh_T030545Z` run + LAUNCH_MANIFEST, forensics dir, small receipts.
- RESULT: terminal_workers 4.7G->4.0M; **ION product tree 6.7G -> 2.0G** in one reversible move.
- Post-verify: resolve_context_scope binds the lane; all load-bearing paths present; cursor runner tests 3/3.
- Receipt: `ION/05_context/signals/production_spine_phase0_terminal_workers_archive_receipt_20260617.txt`
  (incl. one-line reversal command).

Remaining Phase 0 (proposed, not done): export-bundle dedup (needs operator choice of canonical tree),
execution_cycles (33M), comms/history, nested ION/ION (548K, REPO_AUTHORITY non-runnable),
gemini sandboxes (4M), mixed DW lanes (live_carrier_binding non-ACTIVE rows, project_launcher, codex_cli).
NEXT FORK: finish remaining Phase 0 sweep vs begin Phase 1 (carrier-spine pilot into ION_VNEXT/ion_core).

### 2026-06-17 (night) — Audits complete; production-spine plan synthesized

All 3 background audits returned and wrote candidate reports under `PRODUCTION_SPINE_AUDIT/`.
Convergent finding: product is small/separable (~39M kernel + registry + carriers + cockpit) under a
~5.8G exhaust shell; a partial clean skeleton already exists (`ION_VNEXT/ion_core`, 30 modules);
the monolith is hand-written + decomposable (A: 11-module seam map, dispatcher last); first slice =
the proven carrier contract spine, NOT the monolith; charter 0/10 fully met (~half partial demo-only).
=> Strangler-fig extraction, not rewrite.

Synthesis written: `PRODUCTION_SPINE_PLAN.candidate.md` — phased plan (Phase 0 hygiene/de-dup ~4.7G
reclaimable -> Phase 1 carrier-spine pilot = first real vNext promotion -> Phase 2 front-door;
monolith decomposition parallel track; readiness burn-down cross-cutting) + the 4 domains
(repo_hygiene / production_core / monolith_decomposition / readiness_burndown).

Recommended first action: Phase 0 hygiene (archive exhaust out of product tree, gated by B's
load-bearing list + reference-grep; archive not delete; receipts). Reversible, frees ~80% of repo,
touches no product.

AWAITING OPERATOR GO on which entry point (asked). Nothing moved/extracted/deleted yet.

### 2026-06-17 (eve) — Production-spine audit launched (decide-with-map)

Operator reframed the mission: "NOT_PRODUCTION_READY" has functioned as canon/ritual, not a
burn-down. Evidence (this session): repo 6.7G; `05_context` 5.8G (87%); `domain_weaver/terminal_workers`
4.7G (70%) = mission/seat/attempt readiness/gate receipts; product `04_packages` only 61M;
`ion_domain_weaver.py` = 49,513 lines (single file); 0 promotions. Charter
(`02_architecture/PRODUCT_READINESS_CHARTER.md`, 2026-04-25 / pinned V32) has 10 real criteria incl.
#2 "separate demo from production primitives" — never done.

Recommended strategy = strangler-fig extraction to a clean production core (ION_VNEXT as a real
product home), NOT a scratch rewrite (would discard the working carrier contract + context system).
Operator chose: AUDIT FIRST, then decide.

Launched 3 background Composer audits -> `PRODUCTION_SPINE_AUDIT/`:
- A `MONOLITH_SEAM_AUDIT` — decomposition seams of `ion_domain_weaver.py` (+ 4 other big kernels);
  external public surface; extraction order.
- B `EXHAUST_AND_DUPLICATION_CATALOG` — categorize `05_context` exhaust + duplicate kernels;
  archival plan; flag load-bearing context (this lane, active mounts, manifest-referenced signals).
- C `PRODUCTION_CORE_AND_VNEXT_INVENTORY` — product-vs-scaffold; vNext reality check;
  charter 10-criteria implementation matrix; first extraction candidates.

Next: synthesize A/B/C into the production-spine plan + the 4 proposed domains
(`production_core` / `monolith_decomposition` / `repo_hygiene` / `readiness_burndown`).
Still candidate; no rewrite/move/delete started.

### 2026-06-17 — Gated consolidation EXECUTED + verified (candidate space)

Operator authorized all four gated steps (see prior entry). All four are done with receipts, then verified.

1. **Registry amendment** OK — `domain.ion_system_definition.domain.yaml` `owned_or_stewarded_surfaces`
   + `IONOLOGIST.context_system.md` route-deeper. Receipt:
   `signals/ion_system_definition_consolidation_registry_receipt_20260616.txt`.
2. **Mount refresh** OK — `role_ionologist__domain_ion_system_definition` re-materialized
   (`generated_at` 2026-06-17), `context_refs` 19->25; the mount's `.ion/ACTIVE_CONTEXT_PACKAGE.md` is
   now a COMPILED view pointing at THIS ledger (single canonical ledger; dual-working-capsule defect
   resolved). Receipt: `signals/ion_system_definition_consolidation_mount_refresh_receipt_20260616.txt`.
3. **M105C atlas** OK (Composer subagent) — extracted to candidate `ION_SYSTEM_AUDIT_ATLAS/`
   (+ `README_CANDIDATE.md`). Candidate, NOT applied to accepted state. Receipt:
   `signals/v105c_atlas_extract_receipt_20260616.txt`.
4. **Encyclopedia v4.1** OK (Composer draft, orchestrator-finalized) —
   `docs/encyclopedia/ION_Production_Encyclopedia_v4_1_LIVE_V100_CONTEXT_SYSTEMS_CONSOLIDATION_AND_CARRIER_PROOF.md`
   (8 protocol sections; sha256 `832a9344`, 22510 B). `ION_LIVING_ENCYCLOPEDIA_MANIFEST_V100.json`:
   `updated`->2026-06-16; `latest_current_state_supplement`->v4.1; prior 2026-06-04 supplement preserved
   under `prior_current_state_supplements`; `v4_1_source_artifacts` + `overlay_files` appended. Receipt:
   `signals/v100_living_encyclopedia_v4_1_consolidation_update_receipt_20260616.txt` (sha256 `4aa8f7d5`).
   `FILES_ADDED_V4_1.txt` finalized.

**Verification (gate_verify) — all green:**
- Manifest re-parses as valid JSON; latest + prior supplement + all new `overlay_files` hashes match disk.
- `v4_1_source_artifacts` match disk except North Star (->v0.8), surface map, and the manifest itself,
  which drift AS DOCUMENTED (post-compile currentness edits / self-mutation; recorded as as-compiled provenance).
- `resolve_context_scope`: LANE cwd -> `folder_local_context_capsule` binding `.ion/ACTIVE_CONTEXT_PACKAGE.md`
  (this ledger); MOUNT cwd -> `codex_agent_mount` binding the mount manifest + compiled package. Single
  canonical ledger confirmed from both entry points.
- `pytest ION/tests/test_kernel_ion_cursor_queue_runner.py`: 3 passed.

Post-compile currentness fixes: North Star §9 `[gated]`->`[enacted]` (v0.8); `DOMAIN_SURFACE_MAP.md`
consolidation status -> steps 1-4 enacted; v4.1 M105C rows -> candidate-on-disk-extract (not applied).

Pre-existing manifest wart FIXED while here: the `overlay_files` entry for
`FILES_ADDED_V100_LIVING_ENCYCLOPEDIA_AND_CONTEXT_SYSTEM_INTEGRATION.txt` was a bare filename ->
repointed to `ION/05_context/archive/root_witness_manifests/...` (recorded hash `16619dcb`/586B already
matched the archived file, confirming identity). Remaining known wart (NOT fixed; self-referential): the
manifest self-hash in `overlay_files` is a stale creation snapshot — a file cannot hold its own post-write hash.

Next: (a) OPERATOR decision — first vNext domain promotion (crosses the accepted-state membrane);
(b) resume substantive North Star mandate (next domain layers to production + carrier-chassis validation);
(c) optional: add `role.ionologist` to the encyclopedia maintenance-protocol §5 route-deeper list, and fix
the manifest self-hash wart. Still gated/operator: vNext promotion, M105B v4.1 pointer apply, M105C accepted-state application.

### 2026-06-16 — Consolidation enacted (candidate) + gated proposals staged

Operator directive: consolidate the IONOLOGIST / ion_system_definition domain into
ONE harmonized surface (no parallel/conflicting docs+agents). ION = a web of related
domains/contexts/specialties harmonizing as one system (now recorded as North Star
essence, v0.7).

Framing correction: there are NOT two domains. `domain.ion_system_definition` (role
IONOLOGIST) is the one domain the North Star is anchored to, and it already owns the
encyclopedia + maintenance protocol + registry identity. I had added parallel
SURFACES (the North Star lane) alongside existing ones (encyclopedia, generated
mount). Inventory (Composer) found SEVEN parallel surfaces; primary defect = TWO
working `.ion/` ledgers for one role+domain (in-folder lane 2026-06-16 vs generated
mount 2026-06-04).

Enacted now (candidate, in-authority):
- Created `ion_system_definition/DOMAIN_SURFACE_MAP.md` — the single domain index:
  one role per artifact, canonical/candidate/witness/stale classification, the
  dual-ledger resolution, and the M105 applied/not-applied table.
- Affirmed encyclopedia v4.0 (live; receipt 2026-06-04 / C-752) as the canonical
  "what is ION" reader spine; North Star = candidate operating overlay; Derived
  Account = staged input for a v4.1 encyclopedia maintenance update (the Living
  Encyclopedia Law forbids orphan chat-only corpora).

Verified not-applied (IONOLOGIST Usage Rule): M105B v4.1 pointer
(`patch_applied: false`; no v4.1/V105 file on disk) and M105C atlas
(`settled_candidate`; zips only inside the 2026-05-26 portable embed; active-root
`Needs_Routed/` absent). Historical witness until an apply receipt exists.

Staged as operator/Steward-gated (NOT done unilaterally — crosses the membrane):
registry owned-surfaces amendment; mount refresh/regeneration to bind the single
ledger + corpus; v4.1 encyclopedia maintenance packet from the Derived Account;
M105C atlas extraction with receipt. All listed in the surface map.

### 2026-06-16 — Context-systems certainty pass + IONOLOGIST prior-work discovery (operator-gated)

**Context systems — mapped + verified first-hand.** Live working set is narrow:
- ENACTED runtime: `resolve_context_scope` (ion_codex_carrier_sync) binds EITHER a
  **folder-local `.ion/` capsule** (`ion.folder_local_context_capsule.v0_1`) for an
  orchestration/self-context lane, OR a generated
  **`codex_agent_mounts/role_*__domain_*/`** (`ion.portable_agent_domain_context_capsule.v0_1`)
  for a queue worker — the latter selected by `ion_domain_weaver_context_active_resolver`
  (no-write; 48h freshness gate; read first-hand).
- WITNESS only (not a working capsule): `codex_solo` (C-750), `~/.codex/memories` (recall).
- CANDIDATE / doctrine-only (NOT the runtime loader): branch-context node mesh
  (`ion.branch_context_node.v0_1`); context-graph substrate + node/package protocol
  (`PROPOSED_RESTORATION_NOT_YET_RATIFIED`, read first-hand); `active_context_refresh`
  gated-apply (preflight only).

**Correct working Domain Weaver context = two tiers** — folder-local `domain_weaver/.ion/`
for orchestration + generated `codex_agent_mounts` (via resolver) for workers; codex_solo
witness only. CAVEAT: `domain_weaver/.ion/` *binding* is live but *content* is a stale
2026-06-07 snapshot (`focus: usage_limit_blocked`); current DW truth = terminal receipts /
`live_carrier_binding` / `operator_experience/orchestrator_actions/` (Jun 11-16).

**This lane re-validated:** `ion.folder_local_context_capsule.v0_1` + continuity ledger is
the correct, current, enacted pattern for a self-context lane (post-C-751). Right mechanism.

**MAJOR discovery (corrects an earlier subagent claim).** The IONOLOGIST role already has
an established "what is ION" documentation SYSTEM that North Star / Derived Account ran
parallel to and must RECONCILE with — I was not aware of it:
- Mount `codex_agent_mounts/role_ionologist__domain_ion_system_definition/` (manifest
  2026-05-27) is NOT abandoned — `.ion/receipts/` show active `seat_06` work through
  2026-06-11 (Mission 038, attempt 378). A queue start for `role.ionologist` binds THIS
  mount, not the new lane.
- LIVE on disk: `ION/docs/encyclopedia/ION_Production_Encyclopedia_v4_0_LIVE_V96_V100_...md`
  (v4.0) + `ION_LIVING_ENCYCLOPEDIA_MANIFEST_V100.json`, governed by
  `ION/02_architecture/ION_LIVING_ENCYCLOPEDIA_MAINTENANCE_PROTOCOL.md` (receipt 2026-06-04).
- CANDIDATE, staged NOT applied: v4.1 pointer (M105B) + M105C "Full System Audit Atlas" =
  18-system taxonomy + relationship map + stale/quarantine index (`Needs_Routed/*.zip`,
  `ION_VNEXT/07_work/`). Governing rule:
  `ionologist/M105B_M105C_READ_FIRST_WITNESS_INDEX.md` (classify every claim
  active-truth/candidate/historical/superseded/unknown; zips are witness until a receipt
  proves application).

**NEXT (reconciliation — before treating my docs as the definition):** read live v4.0
encyclopedia + candidate M105C atlas; classify per the Usage Rule; position North Star
(= living operating dashboard) + Derived Account relative to the encyclopedia (advance via
the maintenance protocol, not a rogue parallel doc). Then refresh the IONOLOGIST mount so
worker starts bind North Star truth.

### 2026-06-16 — Continuity lane established (this work)
- Diagnosed the root cause of repeated continuity loss: the North Star and Derived
  Account were *orphan candidate files* — registered in no surface any session reads
  at sign-in (not the capsule mesh, not `codex_solo`, not Codex native memory;
  confirmed by grep of `~/.codex/memories`). No carrier would have surfaced them.
- Built this folder-local continuity lane mirroring the live `domain_weaver/.ion/`
  precedent: `AGENTS.md`, `.ion/ION_CONTEXT_CAPSULE.yaml`
  (`ion.folder_local_context_capsule.v0_1`), and this ledger. The runtime
  (`ion_codex_carrier_sync.resolve_context_scope`) binds this as the working capsule
  for sessions routed into this lane.
- Authored a current Cursor sign-in loader at the **real** workspace root:
  `/home/sev/ION - Production/.cursor/rules/ion-north-star-continuity.mdc`. The older
  `ION_Developement/.cursor/` stack is stale/deprecated and is superseded by this.
- Verified engine binding (`resolve_context_scope` → `folder_local_context_capsule`,
  binding this ledger as the working capsule) and registered the lane upstream in the
  root `ION_CONTEXT_CAPSULE.yaml` (`child_domains` + `child_index`) so root-launched
  sessions can discover it without `cd`-ing into the lane.

### 2026-06-16 — North Star + Derived Account (with a continuity-loss witness)
- `ION_NORTH_STAR.candidate.md` (v0.4) — living full-horizon understanding of ION.
- `ION_DERIVED_ACCOUNT.candidate.md` — six-layer, fully-cited account of what ION is.
- These were authored, then partially lost when a network interruption + a lossy chat
  summary erased model memory of them; they were re-derived independently and
  cross-verified to match. This event *is* ION's thesis in miniature: continuity
  survives in externalized on-disk state, not in model memory. This lane exists so it
  does not recur.

### 2026-06-16 — Cursor CLI carrier proven (candidate)
- `ION/04_packages/kernel/ion_cursor_queue_runner.py` rewired to the headless
  `cursor-agent` binary; `ION/03_registry/cursor_cli_carrier_profile.yaml` and
  `ion_carrier_onboard.py` aliases updated. End-to-end round-trip proven (candidate).

### 2026-06-16 — Opus Master Index system
- `ION_Developement/indexes/scripts/`: `generate_opus_master_map.py` (with Phase-3
  indexes), `build_master_index_query_surface.py`, `query_master_index.py`,
  `review_index_staleness.py`. Unified query surface + staleness/supersession review.

### 2026-06-16 — Stale human gate cleared (candidate/receipted)
- Lawfully rejected the stale `orchestrator_lease_worker_start_approval` gate via the
  orchestrator path, clearing a globally-blocking flag.

## Current state

Continuity lane established and self-describing. Sign-in / sign-out protocol defined.
The substantive North Star mandate (below) is resumable from here.

## Next / open threads

- **Register this lane upstream** so a root-launched session surfaces it without
  cd'ing here: add it to the root `ION_CONTEXT_CAPSULE.yaml` child index and/or a
  pointer from `codex_solo/MINI.md`.
- **Optional automation parity:** build `ion_cursor_carrier_sync` + Cursor
  Stop/UserPromptSubmit hooks mirroring Codex, so sign-in/out becomes automatic
  rather than rule-driven.
- **Deprecate cleanly:** decide whether to neutralize the stale
  `ION_Developement/.cursor/` stack (it may still fire a sessionStart hook).
- **Resume mandate:** (1) define the next domain layers needed to take ION to
  production; (2) validate the carrier chassis (Cursor / Codex / Gemini CLIs);
  (3) keep `ION_NORTH_STAR` + `ION_DERIVED_ACCOUNT` current.

## Scope

Use this lane for: holding/curating the definition of ION, North Star / Derived
Account maintenance, production-path and domain-layer design, carrier-chassis
validation, and orchestrating subagents in service of those. Candidate-only.
