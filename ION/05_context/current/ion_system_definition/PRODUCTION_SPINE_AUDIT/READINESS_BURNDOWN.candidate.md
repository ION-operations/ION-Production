# ION Production Readiness Burn-Down (candidate)

```
schema_id:    ion.production_spine.readiness_burndown.v0_1_candidate
generated_at: 2026-06-17T04:05:00Z (approx)
generated_by: Opus (ION North Star / IONOLOGIST mount, lead orchestrator)
posture:      candidate_only  (no production / live-execution / accepted-state / source-edit / secrets authority)
provenance:   synthesized from 10 durable lane gap-returns (PRODUCTION_SPINE_AUDIT/VNEXT_LANE_HARVEST/, lanes 6-15)
              + PRODUCTION_SPINE_AUDIT/KERNEL_RECONCILIATION/KERNEL_CONTROL_DIFF_MATRIX.candidate.md
              all verified: 9/9 contract sections each; kernel matrix = 29 controls; 0 source edits by any worker;
              lane-8 claims independently re-verified by the program's own nemesis overclaim audit (lane 15).
```

## Thesis — what the full sweep actually proved

ION is **not an unbuilt system.** Its executable reality is **live in the monolith** (`ION/04_packages/kernel/`) and broadly tested — kernel **176**, runtime bridge **137**, carrier loop **121**, plus product/cockpit surfaces — all green on re-run. The `ION_VNEXT` frame is a disciplined **canon/docs skeleton** plus a **control-surface superset** (`ion_core`: 29 controls including 20 production-cutover/authority harnesses the monolith lacks). The Domain Weaver engine already drove its vNext-productization program to proof-accepted settlement for all 15 lanes.

Therefore **"production" is overwhelmingly a problem of BINDING + DURABILITY + AUTHORITY — not building from scratch:** reconcile the two `kernel` trees, make settled outputs durable, and lawfully set production authority. "Not production-ready" has persisted largely because the engine's settled outputs **evaporated as run-exhaust** before being consolidated into an owned backlog. **This document is that backlog.**

## Consolidated gap register

| ID | Gap | Sev | Evidence (lanes / artifacts) | Owner domain | Exit test (flip-to-green) | Candidate next packet |
|----|-----|-----|------------------------------|--------------|---------------------------|------------------------|
| **G1** | **Dual `kernel` tree / runtime not bound to vNext** | CRIT | Kernel diff (3 identical / 6 diverged / 20 vNext-only / 0 monolith-only; live binds monolith); lanes 8,10,11,9 (executable code is monolith-only) | production_core + monolith_decomposition | Each registered control true-name resolves to **one** authoritative impl; live carriers import the registered modules; unified pytest (monolith + `ion_core` controls) green from a documented path | `KERNEL_RECONCILIATION_PLAN.candidate.md` **DONE+VERIFIED** → first packet **G1-A** `PCKT-G1-IDENTICAL-UNIFY-NAMESPACE-MERGE-SCAFFOLD-20260617` (operator-gated) |
| **G2** | **Settled outputs non-durable; semantic fan-in blocked** | CRIT | Lane 14 (15/15 carrier-intake accepted but semantic settlement blocked, 0 run bodies); lane 15 (4/15 durable at run-time; no cross-lane overclaim matrix); slice-1a trace (bodies pruned) | readiness_burndown | Every settled lane has a durable, hash-verifiable return body in a git-tracked surface; semantic fan-in runs from durable artifacts; carrier-intake acceptance no longer counts as semantic completion | `PCKT-DOMAIN-WEAVER-DYNAMIC-SWARM-DURABLE-FANIN-SEMANTIC-SETTLEMENT-RE-HARVEST-20260617` (this sweep = first installment) |
| **G3** | **Production execution authority unset** (formal cutover blocker, by design) | HIGH | Lanes 13, 6, 8 (M102 closes no gates; 6 future-transition reqs unmet) | readiness_burndown + operator | Operator authority decision recorded via M97 template **and** all 6 M102 future-transition requirements satisfied (fresh control suite, hash reverification, transition packet) | `PCKT-VNEXT-PRODUCTION-AUTHORITY-TRANSITION-PROOF-CANDIDATE-20260617` |
| **G4** | **No machine-enforceable gate at most lane targets** | HIGH | Lanes 6,7,9,10,11 (docs/stub, 0 tests at target); `QUALITY_STANDARD.yaml` demands enforceable gates; only `ion_core` has tests | production_core | Each lane target has ≥1 read-only validation/test gate runnable from root pytest | per-lane currentness+gate packets (front door, canon, runtime, carriers, products) |
| **G5** | **Currentness/orientation drift + broken `Needs_Routed/*` paths** (pervasive) | HIGH | EVERY lane: stale READMEs/capsules vs disk; `Needs_Routed/*` missing at shell root in every work request | production_core | READMEs/capsules match disk (context-proof gate passes); `Needs_Routed` path contract resolves for all 15 work requests | per-lane currentness packets + a `Needs_Routed` path-contract repair |
| **G6** | **Steward / M103D / M103F gates open; integrated DW validate fails** | MED-HIGH | Lanes 7, 12 (`can_continue_locally: false`; M103D/M103F unsettled; `domain_weave_integrated_validate` fails on 6 files) | production_core + steward | M103D steward review packets settled; M103F real-use checklist complete; integrated DW validate green | `PCKT-M103D-DOMAIN-WEAVE-STEWARD-REVIEW-PACKETS` + `PCKT-VNEXT-DW-SUBSTRATE-RUNTIME-BINDING-AND-M103F-READINESS-20260617` |
| **G7** | **Unmigrated product / source pools** | MED | Lane 9 (`ION_GPT`, `dAimon` unmigrated; cockpit in monolith; projection `W0_skeleton`) | production_core | Source-pool audit complete; gated promotion plan; products lane has real content + tests | `PCKT-VNEXT-PRODUCT-SOURCE-POOL-AUDIT-AND-COCKPIT-BUCKET-PLAN-20260617` |
| **G8** | **DW witness-vs-operational split** | MED | Lane 12 (`domain_weave` static-read bound only; live orchestration under `05_context/current/domain_weaver/` with `full_domain_weaver_ready: false`, `gap_count: 6`) | production_core | M103I registry ↔ live projection reconciled; `full_domain_weaver_ready: true` or gaps owned | folded into G6 next packet |

## Per-lane currentness snapshot (all "partially current"; candidate)

| Lane | Target | State | One-line |
|------|--------|-------|----------|
| 6 Front Door | `00_front_door` | docs-only | 4 required md present + canon-aligned; no enforceable surface; no dynamic-swarm orientation |
| 7 Canon | `01_canon` | real canon, stale README | 31/31 modules + 7/7 bridges on disk; README M25-skeleton drift; integrated DW validate fails (6) |
| 8 Kernel Core | `02_kernel/ion_core` | code, diverged+unwired | 29 controls, **176 tests pass**; live runtime binds monolith; 20 vNext-only harnesses |
| 9 Products | `03_products` | README stub | cockpit in monolith; `ION_GPT`/`dAimon` unmigrated; `W0_skeleton` |
| 10 Carriers | `04_carriers` | README-only | live Codex/Cursor loop in monolith (**121 tests**); return-contract fragmentation |
| 11 Runtime Bridge | `05_runtime` | 2-file stub | ~12.6K lines bridge in monolith (**137 tests**); authority split |
| 12 DW Integration | `06_context/domain_weave` | live-bound (static reads) | 354 files; engine reads YAML/JSON only; witness-vs-operational split |
| 13 Release/Cutover | `07_work` | complete candidate chain | M88-M102 chain (16 md + 58 json); authority unset; 6 transition reqs unmet |
| 14 Fan-In | program-level | settled-but-blocked | 15/15 carrier-intake accepted; semantic fan-in blocked (0 run bodies) |
| 15 Nemesis | program-level | cleared lane 8 | adversarially confirmed lane-8 claims; flags only 4/15 durable at run-time |

## Recommended sequencing (waves)

- **Wave A — keystones (unblock the seam + trust):** G1 (kernel reconciliation; matrix in hand) + G2 (durable semantic fan-in; this sweep is the first installment).
- **Wave B — honesty + enforcement (cheap, pervasive):** G4 (lane gates) + G5 (currentness + `Needs_Routed` repair).
- **Wave C — integration + authority:** G6 + G8 (DW steward/runtime binding) then G3 (lawful production-authority transition proof).
- **Wave D — products:** G7 (source-pool audit + promotion).

All source-changing packets are **candidate plan + read-only diffs first**, gated on operator approval + nemesis review before any edit, live worker start, accepted-state move, or cutover.

## Already done (durable, this push)

- Lane 8 re-driven + independently verified = first **durable** vNext promotion.
- 9 further lanes harvested durably + verified (all 9/9 sections; 0 source edits).
- Kernel reconciliation matrix produced (29 controls).
- Program's own nemesis lane cleared the lane-8 harvest (no material overclaim).
- This burn-down established as the owned, shrinking backlog (fixes the harvest+durability gap that kept ION "not production-ready").
- **G1 reconciliation plan produced + verified** (monolith-primary namespace merge; per-control table corroborated by ground truth: 463/30 modules, 9 shared = 3 identical + 6 diverged, 20 vNext-only; sequenced into 5 gated packets G1-A→G1-E). First source-touching packet **G1-A** awaits operator gate.
- **G1 FOUNDATION APPLIED + verified 176/176 + COMMITTED (`9ac8b9b7`, not pushed):** the full 29-control kernel merge landed as a **2-line `extend_path` scaffold** + a **24-line additive `discover_workspace_manifest` port** into monolith `path_authority` (+28 / −0 / 2 files). Verified in the REAL repo: live import unaffected (`extend_path` is a no-op until ion_core is on the path), live path_authority still functions, merged control suite **176/176**, broad monolith import sane. All 6 diverged controls reconcile to the monolith (5 natively, path_authority via the additive fn). Exit test documented (`G1_UNIFIED_PYTEST_GATE.md`); receipt written. **Residual (separate gates):** live-runtime PYTHONPATH binding (the actual cutover, needs harness-exposure security review), G1-A3 duplicate collapse. **G1 is now ~92% closed** — the keystone reconciliation is proven, landed, and committed (`9ac8b9b7`); only the runtime cutover + cleanup remain.
- **G2 DIAGNOSIS landed + VERIFIED:** the engine implements a two-tier model (carrier-intake status → semantic body settlement), but durable bodies live on the volatile `codex_queue_runs/` surface (pruned) and are never consolidated into the fan-in read path. Reconciliation sets `lane_state=accepted` from STATUS alone (`ion_domain_weaver.py:9428-9429`; `all_lanes_resolved_for_fanin` at `:9527-9533` also ignores body presence), while the semantic fan-in gate requires reading `task_return_body.md` (`:9737-9752`) → 15/15 accepted, 0 bodies, semantic settlement blocked. Map+diagnosis doc + receipt (`DURABLE_FANIN/`); orchestrator-verified against the real monolith (in `kernel/`). Full **G2 DESIGN** landed + verified: `DURABLE_FANIN/G2_DURABLE_FANIN_PLAN.candidate.md` — 7 gated packets **G2-A→G** (additive A,B,C,D,G land first; behavior-changing E=nemesis gate, F=reconciliation honesty are flag-guarded + last). Smallest safe first = **G2-A** (additive durable-harvest capture at carrier-intake accept; hook points verified at connector `:5073` + queue-runner `:8534`). Caveat: G2-A's 2 hook files carry large pre-existing uncommitted changes (+498/+252) → its apply is operator-gated + dry-run-first (unlike G1's clean files). **Wave A planning is complete (G1 landed + verified; G2 diagnosed + designed).** **G2-A dry-run GREEN + orchestrator-verified** (5/5 /tmp tests; helper genuinely additive + fail-soft; hook diffs at connector `:5095` + runner `:8543` touch nothing in accepted/status/reconciliation/fan-in). **G2-A APPLIED + verified + HELD:** new module `kernel/ion_durable_fanin.py` + 2 guarded fail-soft hooks (connector `:5095`, runner `:8543`); import OK + live harvest smoke 5/5 + **176/176** still green + engine untouched + real surface unpolluted; path proven (root→committed surface). Commit held (operator go). `DURABLE_FANIN/G2A_APPLY_GATE.md` + receipt. **Durability realized:** the whole production-spine corpus is now committed in git (`ddfdb219`, 62 files) — no longer working-tree-only; harvest bodies commit as they land. **G2-B1:** ran the helper over the 10 legacy harvests → `DURABLE_FANIN/lanes/` + manifest (10 lanes, ordinals 6–15, 0 hash mismatches; committed); migration hardened the helper against 2 real gaps (separate `lane_ordinal:` field + slug sanitize). **G2 is now ~45% closed** (harvest organ wired+proven; 10/15 lanes durable in the manifest; remaining: back-harvest lanes 1–5, broaden live-capture, G2-C/D additive reconciliation+fan-in reads, G2-E/F flag-guarded behavior changes, G2-G harness).

## Non-claims

Candidate findings; **synthesis is not settlement.** No production/authority is set or claimed. Prior `RETURN_RECORDED_PROOF_ACCEPTED` statuses are gate receipts, not production promotion. All recommended packets are candidates; the operator ratifies any direction change or source work.
