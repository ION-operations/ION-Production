# vNext ↔ Domain Weaver Reconciliation (candidate)

**Status:** candidate / read-only analysis — **PROPOSAL ONLY**  
**Authority:** not-accepted-state; no production-readiness claims; no files were moved, archived, renamed, or deleted.  
**Active root:** `/home/sev/ION - Production/ION_Developement`  
**Sibling worktree:** `/home/sev/ION - Production/ION_DW_PRODUCTION_TESTBED_WORKTREE` (branch `codex/domain-weaver-production-testbed-candidate`)  
**Audited:** 2026-06-17  
**Scope:** characterize dev `ION_VNEXT`, testbed worktree, and live DW kernel; reconcile parallels; classify vNext assets; propose unified clean-core targets.  
**Companion:** `PRODUCTION_SPINE_AUDIT/CORE_RECKONING/DW_CORE_REALITY.candidate.md` (DW-internal map — cross-check only; not required for this pass).

---

## Executive summary

Three frames compete for “clean core” authority:

| Frame | Scale | Last meaningful motion | Governs reality? |
|-------|-------|------------------------|------------------|
| **Dev `ION_VNEXT`** | 11M / 644 files | git `2026-05-21` (R0033 promotion-plan layer) | **No** — candidate skeleton + cutover review theater |
| **Testbed worktree** | 386M total; `ION_VNEXT` inside it **572K** | git `2026-05-21`; untracked June-5 testbed receipts | **No** — frozen pre-DW snapshot + donor lanes; abandoned reconciliation |
| **Live DW kernel** | `ion_domain_weaver.py` 49,513 L + 38 sibling modules | git `2026-06-05` on monolith | **Yes (active-truth for orchestration)** — projection, promotion, mounts, control planes |

**Reconciliation verdict:** vNext’s **lane layout and control-surface discipline** are worth keeping as the skeleton. vNext’s **`06_context/domain_weave/` tooling** and **`ion_vnext_production_authority_*` cutover stack** are **parallel drift** — abandoned or witness-only relative to live DW. The testbed worktree is **not** a more-current reconciliation; it is a **May-21 fork** missing the entire DW constellation, with ~375M of bulk in **AIM-OS / Needs_Routed / ION_GPT**, not in vNext.

**Recommended target (Option A):** keep vNext’s **FRAME**, populate it by **decomposing integral DW in place** into bounded modules aligned to vNext lanes; **retire** domain_weave + cutover drift; **witness-archive** the testbed worktree.

---

## 1. Three-frame characterization

### 1A. Dev `ION_VNEXT` (`ION_Developement/ION_VNEXT`, 11M)

**Top-level structure (measured):**

| Lane | Files | Size | Contents |
|------|-------|------|----------|
| `00_front_door` | 5 | 52K | Entry docs: `AI_START_HERE.md`, `HUMAN_START_HERE.md`, `AUTHORITY_BOUNDARIES.md`, `ROUTE_MAP.md`, `README.md` |
| `01_canon` | 19 | 180K | `WORKSPACE_CANON.yaml`, `FAMILY_REGISTRY.yaml`, gate/source-pool maps — **candidate policy, not accepted canon** |
| `02_kernel/ion_core` | 75 | 988K | **30 src modules + 29 control tests** — real code |
| `03_products` | 1 | 8K | **README only** — “candidate directory contract only” (`03_products/README.md` L5–7) |
| `04_carriers` | 1 | 8K | **README only** |
| `05_runtime` | 2 | 16K | **README + bridge markdown** (`M86_ACTIONS_MCP_SUPABASE_BRIDGE.md`) — no executable runtime |
| `06_context` | 355 | 2.1M | **`domain_weave/`** MVP kernel + dry-run exhaust |
| `07_work` | 129 | 7.3M | Mission packets M49–M104*, settlement JSON |
| `08_releases` | 53 | 384K | M90–M102 cutover/rehearsal/authority review artifacts |
| `09_references` | 1 | 8K | README |
| `90_archive` | 1 | 8K | README |
| `99_private` | 1 | 8K | README |

**`02_kernel/ion_core/src/kernel/*` — control surfaces (active code):**

| Module cluster | Modules | Posture |
|----------------|---------|---------|
| **Path / movement authority** | `ion_path_authority.py`, `ion_workspace_root_registry.py`, `ion_ai_movement_gate.py`, `ion_agent_cwd_boundary.py`, `ion_codex_work_request_target_binding.py` | In-memory gate builders; **8/10 already duplicated in live kernel** (`ION/04_packages/kernel/ion_path_authority.py` et al.) |
| **Proof / template gates** | `ion_context_proof_gate.py`, `ion_template_action_gate.py` | Same — **promoted to kernel** |
| **Receipt / context / promotion primitives** | `ion_receipt_core.py`, `ion_context_package_core.py`, `ion_source_pool_audit_core.py`, `ion_promotion_plan_core.py` | **vNext-only** — in-memory; explicitly “does not copy, move, delete… or write files” (`ion_promotion_plan_core.py` L3–6) |
| **Operator hygiene / carrier** | `ion_operator_artifact_hygiene_check.py`, `ion_carrier_mount_receipt.py` | Promoted to kernel |
| **Cutover / production authority review** | 14× `ion_vnext_*` modules (M90–M102): `ion_vnext_production_authority_transition_precheck.py`, `ion_vnext_production_authority_decision_packet_draft.py`, `ion_vnext_cutover_execution_rehearsal_dryrun.py`, … | Self-referential review builders over `ION_VNEXT/08_releases/*` paths; **no kernel import surface** |

**`06_context/domain_weave/` tooling:**

| Artifact | Evidence |
|----------|----------|
| **Tools (955 LOC total)** | 7 scripts under `tools/`: `domain_weave_discover.py` (269 L), `domain_weave_validate.py`, `domain_weave_compile_context.py`, `domain_weave_impact_check.py`, `domain_weave_activation_plan.py`, `domain_weave_integrated_validate.py`, `domain_weave_yaml.py` |
| **Loop proven** | `README.md` L47–55: discover → validate → compile → impact → activation plan → settlement |
| **Schema** | `ion.domain_weave.map.v0_1` (`domain_weave_discover.py` L19) — **not** `ion.domain_weaver.*` |
| **Examples** | `examples/ion_like_project/`, `examples/integrated_agent_enterprise/` |
| **Exhaust** | `dry_runs/` 1.4M — M103–M104 mission receipts |
| **Status** | M103B candidate MVP landed 2026-05-23 per `README.md` L3–4; **after** vNext kernel freeze (2026-05-21) |

**Git recency (dev root):** last 5 commits touching `ION_VNEXT/` all **2026-05-20..21** (R0029–R0033 promotion layers). No commits after DW’s 2026-06-05 evolution.

---

### 1B. Testbed worktree (`ION_DW_PRODUCTION_TESTBED_WORKTREE`, 386M)

**Where the ~375M “extra” bulk lives (NOT in `ION_VNEXT`):**

| Path | Size | Nature |
|------|------|--------|
| `AIM-OS/` | 174M | Separate knowledge/IDE orchestration tree (`knowledge_architecture` 53M, `packages` 33M, …) — **donor/reference lane** |
| `ION_Developement/ION/` | 82M | Frozen kernel snapshot — **301** `.py` modules vs **461** in dev; **`ion_domain_weaver.py` absent** |
| `ION_GPT/` | 54M | Custom GPT packaging |
| `Needs_Routed/` | 54M | Routed workpackets/diffs (`workpackets` 27M, `diffs` 26M) — intake exhaust |
| `ION_VNEXT/` | **572K** | Stale vNext copy — **missing 14 cutover modules** present in dev; `ion_path_authority.py` differs |

**Branch activity (`git log -15 --date=short`):** all commits **≤ 2026-05-21**; tip `eb8f2838` “R0033: Promote ION_VNEXT promotion plan core layer”. Dev HEAD `a2f3a0e3` is **ahead** (includes post-vNext DW work).

**June-5 testbed artifacts:** `ION_Developement/ION/05_context/current/domain_weaver/production_testbed_planning/` exists with `BRANCH_START_RECEIPT_20260605T0055Z.candidate.json` (branch start, skeleton paths under `ION/examples/domain_weaver_production_testbed/`) — but **`git status` shows `??` untracked**. Reconciliation attempt **started locally, never committed, abandoned**.

**Verdict:** worktree is **not** a more-current DW+vNext merge. It is a **May-21 time capsule** plus sibling donor trees and uncommitted June-5 planning receipts. **Inactive / abandoned** as a reconciliation lane.

---

### 1C. Live DW in dev kernel (`ION/04_packages/kernel`)

**Scale (cross-check with companion audit / MONOLITH_SEAM):**

| Surface | Measure |
|---------|---------|
| Monolith | `ion_domain_weaver.py` — **49,513** lines (`wc -l`) |
| Sibling modules | **38** files matching `ion_domain_weaver*.py` |
| Last monolith commit | **2026-06-05** “work: add active ION source packet” |
| Projection artifact | `ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json` — load-bearing, referenced by mounts/runtime |
| Promotion artifacts | `PROMOTION_REVIEW.json`, `PROMOTION_GATE.json`, `promotion_drafts/` under `domain_weaver/` |
| Dispatcher | `execute_domain_weaver_action` — ~8,939 lines, 107 operator actions (MONOLITH_SEAM §2) |

**Wiring (active-truth samples):**

- `ion_codex_agent_mount.py` L30–32, L204–206: binds `DOMAIN_WEAVER_PROJECTION_PATH`, `DOMAIN_WEAVER_PROMOTION_REVIEW_PATH` into mount manifests
- `ion_runtime_service_control.py` L49–50, L3738+: reads projection for service control surfaces
- `ion_agent_control_plane.py` L40, L46–50: imports `build_domain_weaver_projection` **and** reads vNext `DOMAIN_WEAVE_ROOT` as **witness**
- `ion_cockpit_view_model.py`: Domain Weaver + vNext path bindings for UI panels

**Scope note:** companion `DW_CORE_REALITY.candidate.md` maps DW-internal regions; this audit treats DW as **governing orchestration truth** without re-deriving seam map.

---

## 2. Parallel reconciliation

### 2A. vNext `domain_weave/` vs live `ion_domain_weaver*` constellation

| Dimension | vNext Domain **Weave** | Live Domain **Weaver** |
|-----------|------------------------|------------------------|
| **Name / schema** | `ion.domain_weave.*` | `ion.domain_weaver.*` |
| **Size** | ~955 LOC tools + YAML/schemas | 49,513 L monolith + ~11K swarm CP + 38 modules |
| **Purpose** | Read-only planning: discover files, infer domains, impact check, dry-run activation | Operational: projection refresh, promotion review/gate, queue governance, terminal workers, spawn, cockpit |
| **Mutates state?** | No — “Read-only by default” (`domain_weave_discover.py` L3–4) | Yes — materialization pointers, promotion drafts, operator actions |
| **Kernel integration** | Peripheral: `ion_agent_control_plane.py` L46–50 reads M103B validation + map YAML as **witness**; MCP routes to `dAimon/gemini_cli/.../domain_weave_controller_mvp*.py` (`ion_action_mcp_branch_leaders.py` L1482+) — **third parallel** | Central: imports across queue runners, mounts, orchestrator, automation CP |
| **Recency** | Landed M103B 2026-05-23; frozen with vNext | Evolved through **2026-06-05** |

**Classification of relationship:** **not** a clean reimplementation. **Not** a subset — disjoint schema family and capability set. **Diverged / abandoned** as operational core; vNext weave is a **pre-DW planning experiment** packaged from `Needs_Routed/` zips (`domain_weave/README.md` L18–28).

**Which is truer to what ION needs?** **Live DW (witness: active-truth).** vNext weave lacks projection, promotion gate, queue ledger, worker-start readiness, terminal-worker maintainer, and mount binding — the machinery ION actually runs. vNext weave’s **fact-posture taxonomy** (`observed_fact` … `accepted_ion_state`, `README.md` L82–95) is salvageable as **documentation discipline**, not as a runtime substitute.

---

### 2B. vNext `ion_vnext_production_authority_*` vs DW promotion/projection machinery

| Surface | Location | Governs reality? | Overlap |
|---------|----------|------------------|---------|
| **vNext cutover stack** | `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_vnext_*.py` + `08_releases/m90–m102_*` | **No** — “does not set authority, execute cutover… or claim accepted state” (`ion_vnext_production_authority_transition_precheck.py` L3–7) | Thematic only (release gates, hash manifests, rehearsal dry-runs) |
| **vNext promotion plan core** | `ion_promotion_plan_core.py` — **vNext-only**, in-memory | **No** | Conceptual overlap with promotion *planning*; zero bind to `PROMOTION_*.json` |
| **DW promotion/projection** | `build_domain_weaver_promotion_review` (`ion_domain_weaver.py` L2359+), `DOMAIN_WEAVER_PROJECTION.json`, `PROMOTION_GATE.json`, `ion_domain_weaver_projection_refresh_candidate.py`, `ion_domain_weaver_dynamic_expansion_promotion.py` | **Yes (active-truth for domain registry drafts + projection)** | Operational promotion review consumed by mounts and runtime service control |
| **Kernel path authority (promoted from vNext)** | `ION/04_packages/kernel/ion_path_authority.py` (287 L) | **Yes** — imported by worker shift, agent cwd, movement gate | Partial vNext control surface **already won** |

**Which governs reality?** **DW projection + promotion JSON + monolith builders** for domain orchestration. vNext cutover modules govern **nothing outside their own artifact tree** — they are **witness packets** for a vNext-root cutover that never happened and **predates DW’s June evolution**.

---

## 3. vNext asset classification

| Asset | Class | Rationale (evidence) |
|-------|-------|----------------------|
| `00_front_door/*` | **KEEP-AS-FRAME** | Disciplined entry, authority boundaries, route map (`README.md` L7–9) |
| `01_canon/*` | **KEEP-AS-FRAME** (candidate) | Lifecycle separation principles (`WORKSPACE_CANON.yaml` L9–17); must be re-aligned to DW domain IDs |
| Lane layout `03_products` … `99_private` | **KEEP-AS-FRAME** | Empty contracts define lifecycle slots (`03_products/README.md` L7–12) |
| `02_kernel` gates: path, movement, cwd, proof, template | **SALVAGE** | Good patterns; **8/10 already in kernel** — dedupe vNext copies, single import surface |
| `02_kernel`: receipt, context package, source-pool audit, promotion plan core | **SALVAGE** | Useful in-memory primitives; promote or fold into DW receipt/materialization lanes |
| `02_kernel`: 14× `ion_vnext_*` cutover modules | **DRIFT-RETIRE** | Self-referential M90–M102 theater; no kernel binds; predates DW |
| `06_context/domain_weave/tools/*` | **DRIFT-RETIRE** | Parallel `ion.domain_weave.*` stack; 955 LOC vs 49K L DW; witness-only kernel touch |
| `06_context/domain_weave/dry_runs/*`, schemas, examples | **STALE-PRE-DW** | M103–M104 mission exhaust; planning inputs superseded by live `DOMAIN_WEAVER_PROJECTION.json` |
| `07_work/*` | **STALE-PRE-DW** (witness) | Historical mission packets; retain as archive evidence, not operating law |
| `08_releases/*` | **DRIFT-RETIRE** | Cutover rehearsal artifacts for vNext-root promotion never executed |
| `03_products`, `04_carriers`, `05_runtime` READMEs | **KEEP-AS-FRAME** | Correct empty-lane discipline |
| `05_runtime/M86_*` bridge doc | **SALVAGE** | Intent doc for MCP bridge; re-bind to kernel `ion_chatgpt_browser_mcp_*` |
| Testbed `ION/examples/domain_weaver_production_testbed/` | **STALE-PRE-DW** | Untracked skeleton; vNext-shaped but on pre-DW branch |
| Testbed `AIM-OS/`, `Needs_Routed/`, `ION_GPT/` | **STALE-PRE-DW** (donor) | Source pools per vNext README L33–36; not clean core |
| Live `ION/04_packages/kernel/ion_domain_weaver*` | **KEEP-AS-FRAME** (engine) | Active-truth orchestration — **decompose**, do not retire |
| Live `DOMAIN_WEAVER_PROJECTION.json`, `PROMOTION_*.json` | **KEEP-AS-FRAME** | Load-bearing state artifacts |

---

## 4. Unified clean-core target options

### Option A — **vNext frame + DW decompose-in-place** (recommended)

| Dimension | Choice |
|-----------|--------|
| **Thesis** | Keep vNext’s numbered lanes and front-door discipline; make DW the **engine** by strangler extraction into lane-aligned modules. |
| **DW** | **Decompose in place** — constants → projection_records → promotion_review → queue_governance → dispatcher last (MONOLITH_SEAM order); extracted modules land under `ION_VNEXT/02_kernel/` (or `ION/04_packages/kernel/` with vNext mirror imports). |
| **vNext** | **Absorb frame**; retire `domain_weave/` + `ion_vnext_*` cutover; salvage gate/receipt primitives not yet in kernel. |
| **Testbed** | **Witness-archive** — no merge; optionally mine `production_testbed_planning/` receipts as audit evidence only. |
| **First slice** | **Projection + promotion review builders** (`ion_domain_weaver_projection_records.py`, `build_domain_weaver_promotion_review`) — already partially extracted; binds directly to `DOMAIN_WEAVER_PROJECTION.json` / `PROMOTION_REVIEW.json`. |
| **Risks** | Lane mapping arguments; duplicate path_authority during transition; operator confusion if both weave and weaver names persist. |
| **Effort** | **Medium–high** (8–14 weeks staged): frame stable immediately; DW decomposition parallel to Phase 0 hygiene. |

### Option B — **DW-centric kernel shell, vNext demoted to docs**

| Dimension | Choice |
|-----------|--------|
| **Thesis** | DW monolith + siblings **are** the core; vNext becomes README-only front door pointing at kernel paths. |
| **DW** | Decompose under `ION/04_packages/kernel/` only — no vNext code home. |
| **vNext** | **Retire** as code host; keep `00_front_door` + `01_canon` as markdown/YAML only. |
| **Testbed** | Delete path from operator workflow; archive worktree. |
| **First slice** | Carrier contract spine (per PRODUCTION_SPINE_PLAN Phase 1 — codex/cursor queue runners + gates). |
| **Risks** | Loses vNext’s promotion/receipt primitive lab; harder to prove “clean rebuild” narrative; kernel stays visually monolithic longer. |
| **Effort** | **Medium** (6–10 weeks) — less relocation, more social/consistency debt. |

### Option C — **Revive testbed reconciliation branch**

| Dimension | Choice |
|-----------|--------|
| **Thesis** | Finish `codex/domain-weaver-production-testbed-candidate` as integration branch, merge to dev. |
| **DW** | Port June DW forward into testbed, then merge. |
| **vNext** | Reconcile testbed’s slimmer `ION_VNEXT/02_kernel` with dev’s cutover modules. |
| **Testbed** | **Active integration lane** |
| **First slice** | Commit untracked `production_testbed_planning/` + forward-port `ion_domain_weaver.py`. |
| **Risks** | **High** — 26-day DW drift to replay; 386M donor noise; duplicate AIM-OS/Needs_Routed; branch already stale vs dev HEAD. |
| **Effort** | **High** (12–20 weeks) with low confidence — replays merge conflict surface already abandoned once. |

---

## 5. Hypothesis test

> *“Keep vNext’s disciplined FRAME as skeleton; populate by decomposing integral DW into bounded modules; retire vNext’s parallel domain_weave + cutover drift.”*

| Claim | Verdict | Evidence |
|-------|---------|----------|
| vNext frame is disciplined | **Confirm** | Numbered lanes, empty-lane README contracts, front-door read order, canon principles |
| vNext frame is current | **Partial refute** | Frozen 2026-05-21; canon still references Domain Weave as substrate (`WORKSPACE_CANON.yaml` L22–24) — needs rewrite |
| DW should populate frame | **Confirm** | DW last commit 2026-06-05; wired to mounts/runtime/cockpit; vNext has no runnable products/carriers/runtime |
| domain_weave should retire | **Confirm** | Disjoint schema; 955 LOC; kernel uses DW projection; weave referenced as witness only |
| cutover drift should retire | **Confirm** | 14 modules + 08_releases produce artifacts about vNext cutover that never executes; DW monolith references `ion_vnext_production_spec_*` missions (L8922+) as **integration intent**, not vNext cutover modules |
| Testbed is the better skeleton | **Refute** | No `ion_domain_weaver.py`; 572K vNext; untracked June receipts; git tip May-21 |

**Net: hypothesis CONFIRMED** as Option A, with explicit caveat that **canon YAML must be rewritten** to name Domain **Weaver** (operational) vs retired Domain **Weave** (planning).

---

## 6. Recommendation

**Choose Option A.** Evidence weight:

1. **Recency:** DW evolved after vNext froze (2026-06-05 vs 2026-05-21).
2. **Integration:** 60+ kernel files reference `domain_weaver`; vNext weave touched only via witness reads.
3. **Frame value:** vNext’s lane layout is the only articulated clean-room structure; DW has no equivalent folder discipline.
4. **Duplication cost:** Partial promotion already happened (path/proof gates); finishing dedupe cheaper than testbed revival.
5. **Testbed:** Abandoned untracked state — not a trustworthy integration branch.

**Immediate next steps (proposal only):**

1. Freeze new work on `06_context/domain_weave/tools/` and `ion_vnext_*` cutover modules — witness-only.
2. First extraction slice: **`ion_domain_weaver_projection_records` + promotion review builders** → vNext-aligned module under `02_kernel`, re-export from monolith.
3. Rewrite `01_canon/WORKSPACE_CANON.yaml` Domain Weave paragraph to point at DW projection paths.
4. Archive testbed worktree decision — do not forward-port.

---

## 7. Summary (8–12 lines)

- **Three frames:** dev vNext (11M, May-21), testbed worktree (386M bulk in AIM-OS/Needs_Routed, not vNext; pre-DW kernel), live DW (49K L + 38 modules, June-5) — **only DW governs orchestration**.
- **domain_weave vs domain_weaver:** disjoint; weave is abandoned planning MVP; weaver is active-truth.
- **Cutover vs promotion:** vNext M90–M102 is review theater; DW `PROMOTION_*.json` + projection builders govern domain registry reality.
- **Testbed:** frozen May-21 fork, missing entire DW; June-5 planning **uncommitted** — abandoned.
- **Classify:** keep vNext front-door/canon/lanes; salvage gate/receipt primitives; retire domain_weave + cutover; decompose DW in place.
- **Recommend Option A:** vNext frame + DW decomposition; first slice = projection/promotion review extraction.
- **Refute** testbed-as-reconciliation and vNext-as-engine hypotheses with file-size, git, and import-path evidence.

---

## Non-claims

- No production readiness, accepted state, or cutover authority.
- No recommendation to delete or move files — classification is planning input only.
- No claim that DW decomposition order is fully specified (defer to MONOLITH_SEAM + DW_CORE_REALITY).
- No claim that vNext canon YAML is ratified law — all `candidate` / `v1_candidate` posture.
- No verification that all 461 kernel modules were read — sampling + grep + git + `du` evidence only.
- Synthesis is **not** ratification; operator + North Star hold final target decision.
