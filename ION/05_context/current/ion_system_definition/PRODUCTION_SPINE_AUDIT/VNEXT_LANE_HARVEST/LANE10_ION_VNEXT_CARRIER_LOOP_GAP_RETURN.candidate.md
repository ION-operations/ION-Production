```
lane_id: ion_vnext_carrier_loop (ordinal 10)
request_id: codex_req_domain_weaver_dynamic_swarm_10_domain_ion_vnext_carrier_loop_20260602_attempt_001
objective_sha256: bae58a6f4b9c13385c67d3b3cbffc1f79849799cdbb8bfd99e2098cfc533e130
source_target: ION_VNEXT/04_carriers
produced_by: Composer carrier (role.mason) — durable re-drive after run-exhaust pruning
produced_at: 2026-06-17T03:59:14Z
write_posture: candidate_only
```

### CONTEXT PROOF

**Shell root proof (VERIFIED):** commands run from `/home/sev/ION - Production/ION_Developement`. Present on disk: `pyproject.toml` (shell root, `ion-kernel` → `ION/04_packages`), `ION/REPO_AUTHORITY.md`, and target `ION_VNEXT/04_carriers/README.md` (sole file under lane path).

**On-disk lane target (VERIFIED):**

```bash
find ION_VNEXT/04_carriers -type f | sort
# ION_VNEXT/04_carriers/README.md
```

**Paths read (one-line note each):**

| Path | Note |
| --- | --- |
| `ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json` | Large projection graph; lane 10 `domain.ion_vnext_carrier_loop` → `ION_VNEXT/04_carriers` with work-request backrefs |
| `ION/05_context/current/domain_weaver/swarm_evolution/DYNAMIC_SWARM_OPERATION_PLAN.candidate.json` | Lane ordinal **10**, path `ION_VNEXT/04_carriers`, `required_output: production_spec_carrier_loop_gap_return` |
| `ION/05_context/current/domain_weaver/fission_dryrun/DOMAIN_TOPOLOGY_AUDIT.candidate.json` | Adaptive topology audit; authority gates closed; `worker_start_authority: false` |
| `ION/05_context/current/domain_weaver/fission_dryrun/TOPOLOGY_ADAPTIVE_CONTROL_POLICY.candidate.json` | Rejects fixed worker/domain counts; reference ceiling 32 is guardrail only |
| `ION/05_context/current/domain_weaver/fission_dryrun/FISSION_TEMPLATE_LIBRARY.candidate.json` | Fission templates for topology evolution; no carrier-loop-specific template |
| `ION/05_context/current/domain_weaver/approval_governor/LIVE_EXECUTION_APPROVAL_GOVERNOR_POLICY.candidate.json` | Live execution approval-governed; `max_parallel_live_workers: 3`; candidate policy only |
| `ION/05_context/current/domain_weaver/approval_governor/APPROVAL_DECISION_LEDGER.candidate.json` | Semi-auto queue approvals; `worker_started_count: 0` |
| `ION/05_context/current/domain_weaver/queue_governance/TERMINAL_BACKLOG_LIFECYCLE_METADATA_BACKFILL.latest.json` | 544 classified requests; 69 terminal backlog; `work_lane_projection_ready: false` |
| `ION/05_context/current/domain_weaver/queue_governance/STALE_WAITING_REQUEST_RECONCILIATION.latest.json` | `stale_waiting_request_count: 0`; queue governor dogfood ready |
| `ION/05_context/current/domain_weaver/queue_governance/WAITING_ACCEPTED_SUCCESSOR_RECONCILIATION.latest.json` | 4 waiting requests; 1 work-lane waiting; projection not ready |
| `ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json` | Active queue surface; no live match for lane-10 dedupe key in quick scan |
| `ION/05_context/current/chatgpt_connector/work_lanes/INDEX.json` | Work-lane index; 69 exact-request-path entries; round-table / spawn dispatch heavy |
| `ION_VNEXT/00_front_door/AI_START_HERE.md` | M103C front door; lists Codex worker loop as active mission; Cursor extension reference-only |
| `ION_VNEXT/00_front_door/AUTHORITY_BOUNDARIES.md` | M102 authority ceiling; all execution gates closed |
| `ION_VNEXT/01_canon/QUALITY_STANDARD.yaml` | Production bar; Codex CLI primary dogfood carrier; receipt-backed transitions |
| `ION_VNEXT/01_canon/CONTROL_SURFACE_REGISTRY.yaml` | 29 controls; `primary_dogfood_carrier: codex_cli`; only `carrier_mount_receipt` control in vNext tree |
| `ION_VNEXT/01_canon/DOMAIN_WEAVE_READ_FIRST_BINDING.yaml` | M103B binding; `can_continue_locally: false` for cross-domain promotion |
| `Needs_Routed/ION_DOMAIN_WEAVE_FULL_ION_MASTER_PLAN_v0_1.md` | **MISSING at shell root** (work-request required path); witness copy under `projects/WaterPRO/aqua-react-splash/Needs_Routed/` |
| `Needs_Routed/M103_DOMAIN_WEAVE_INTEGRATED_SUBSTRATE_PLAN.md` | **MISSING at shell root**; witness copy under `projects/WaterPRO/aqua-react-splash/Needs_Routed/` |
| `ION/04_packages/kernel/ion_domain_weaver.py` (~L8324–8393) | `_domain_weaver_vnext_productization_lanes`; lane spec for `ion_vnext_carrier_loop` |
| `ION/tests/test_kernel_ion_agent_control_plane.py` (~L5894–5924) | Asserts dynamic swarm / vNext productization lane counts and topology posture |
| `ION_VNEXT/04_carriers/README.md` | Candidate lane README; states implementations remain in active source locations until promoted |
| `ION/05_context/current/chatgpt_connector/codex_work_requests/codex_req_domain_weaver_dynamic_swarm_10_domain_ion_vnext_carrier_loop_20260602_attempt_001.json` | Work request; status `RETURN_RECORDED_PROOF_ACCEPTED`; run body path points to pruned dir |

**Lane builder currentness (VERIFIED):**

```bash
cd "/home/sev/ION - Production/ION_Developement"
PYTHONPATH=ION/04_packages python3 -c "
from kernel.ion_domain_weaver import _domain_weaver_vnext_productization_lanes
from pathlib import Path
lanes = _domain_weaver_vnext_productization_lanes(Path('.'))
l = next(x for x in lanes if x['lane_kind']=='ion_vnext_carrier_loop')
print('engine ordinal:', l['ordinal'], 'path:', l['path'])
print('required_context:', l['required_context'])
"
```

```text
engine ordinal: 5 path: ION_VNEXT/04_carriers
required_context: ['ION_VNEXT/04_carriers/README.md', 'ION_VNEXT/00_front_door/AI_START_HERE.md']
```

**Ordinal note (VERIFIED):** Dynamic swarm plan assigns **ordinal 10** to this lane; engine renumbers emitted lanes by pass order (carrier loop is **5 of 8** emitted vNext productization lanes). Both agree on `path`, `domain_id`, and `required_output`.

### TEMPLATE ACTION PROOF

**vNext lane has no executable template (VERIFIED):** `ION_VNEXT/04_carriers/` contains only `README.md`. No importable carrier loop package, queue runner, or test harness exists under the lane target.

**Monolith carrier import attempt (live runtime binding — VERIFIED):**

```bash
cd "/home/sev/ION - Production/ION_Developement"
PYTHONPATH=ION/04_packages python3 -c "
from kernel import ion_codex_queue_runner, ion_cursor_queue_runner
from kernel import ion_carrier_task_return, ion_carrier_tick, ion_carrier_onboard
print('imports OK')
print('codex_runner:', ion_codex_queue_runner.__file__)
print('cursor_runner:', ion_cursor_queue_runner.__file__)
print('carrier_task_return:', ion_carrier_task_return.__file__)
"
```

```text
imports OK
codex_runner: .../ION/04_packages/kernel/ion_codex_queue_runner.py
cursor_runner: .../ION/04_packages/kernel/ion_cursor_queue_runner.py
carrier_task_return: .../ION/04_packages/kernel/ion_carrier_task_return.py
```

**Return-contract template mismatch (VERIFIED):** `ION_VNEXT/04_carriers/README.md` documents a **3-section** Codex CLI return (`### CONTEXT PROOF`, `### TEMPLATE ACTION PROOF`, `### RESULT`). This work request requires **9 sections** (`return_contract_sections` in packet). Kernel `ion_carrier_task_return.py` enforces context/template proof gates against monolith paths, not vNext lane artifacts.

**Partial vNext carrier primitive (VERIFIED):** `ION_VNEXT/02_kernel/ion_core/src/kernel/ion_carrier_mount_receipt.py` exists (518 lines) and is registered in `CONTROL_SURFACE_REGISTRY.yaml`. `diff -q` against monolith copy reports **files differ** (same line count, diverged content).

**Prior run body (VERIFIED missing):**

```bash
ls "ION/05_context/current/chatgpt_connector/codex_queue_runs/codex_run_2026-06-02T193546Z0000_codex_req_domain_weaver_dynamic_swarm_10_domain_ion_vnext_carrier_loop_20260602_/"
# No such file or directory
```

Task return `2026-06-02T194244Z0000_task_return.json` retains gate receipts (`carrier_intake_ready`) but `raw_latest_return_md_expected_from_run_packet: true` with pruned run dir — body not recoverable from disk.

### VALIDATION

| Check | Result | Evidence |
| --- | --- | --- |
| Lane path exists | **PASS** | `ION_VNEXT/04_carriers/README.md` present |
| Lane `required_context` (engine) | **PASS** | Both paths exist |
| Work-request `required_context_reads` (22 paths) | **PARTIAL** | 20 exist at declared paths; **2 `Needs_Routed/*` paths MISSING** at shell root |
| vNext lane executable / import | **FAIL** | No Python modules under `04_carriers` |
| Monolith carrier module imports | **PASS** | `ion_codex_queue_runner`, `ion_cursor_queue_runner`, `ion_carrier_*` import via `PYTHONPATH=ION/04_packages` |
| Carrier subset pytest (read-only) | **PASS** | **121 passed** in 45.67s — `test_kernel_ion_codex_queue_runner`, `test_kernel_ion_cursor_queue_runner`, `test_kernel_ion_carrier_{task_return,onboard,tick,continue}` |
| vNext `carrier_mount_receipt` control test | **PASS** | **12 passed** — `ION_VNEXT/02_kernel/ion_core/tests/control/test_kernel_ion_carrier_mount_receipt.py` |
| Dynamic-swarm vNext lane emission tests | **PASS (subset)** | 8 passed / 1 failed when running `-k "vnext_productization or dynamic_swarm"` — failure is unrelated worker-start window test, not lane-10 path guard |
| Prior lane-10 run markdown body | **MISSING** | Run dir pruned; only JSON gate metadata survives |
| Live MCP / Action Gateway smoke for carriers | **NOT RUN** | README explicitly separates repo-observed source proof from live listener state |

**Monolith carrier surface inventory (VERIFIED):**

| Module | Lines (approx) | Role |
| --- | --- | --- |
| `ion_codex_queue_runner.py` | 8651 | Bounded Codex CLI queue adapter over ChatGPT connector work queue |
| `ion_cursor_queue_runner.py` | 399 | Bounded Cursor Agent CLI spawn-row runner |
| `ion_carrier_onboard.py` | 450 | Shell-root mount / onboarding |
| `ion_carrier_continue.py` | 786 | Turn-packet continuation |
| `ion_carrier_task_return.py` | 395 | Cursor Task return intake + proof gates |
| `ion_carrier_tick.py` | 474 | Carrier tick loop |
| `ion_carrier_mount_receipt.py` | 518 | Mount receipt (also copied to vNext ion_core) |
| `ion_carrier_onboarding_packet.py` | 352 | Onboarding packet builder |
| `ion_carrier_onboarding_authority_audit.py` | 285 | Onboarding authority audit |
| `ion_carrier_workflow_audit.py` | 266 | Workflow audit |
| + 7 `ion_codex_*carrier*` modules | ~5300+ | Codex carrier sync/domain/OS/audit surfaces |

**vNext lane inventory (VERIFIED):** 1 markdown file (3434 bytes). Zero tests. Zero queue runners. One related control primitive (`ion_carrier_mount_receipt`) lives in **lane 3** (`02_kernel/ion_core`), not in `04_carriers`.

### LANE CURRENTNESS REVIEW

**Verdict: PARTIALLY CURRENT — lane frame and engine spec align; production-spec carrier loop is not landed in the vNext target; live loop runs from monolith kernel.**

**Current (VERIFIED):**

- Target path `ION_VNEXT/04_carriers` exists; README accurately states carrier implementations remain in active source locations until audit/tests/receipt promotion.
- Engine lane spec (`ion_domain_weaver.py` L8324–8333) and `DYNAMIC_SWARM_OPERATION_PLAN.candidate.json` ordinal-10 entry match path, `domain_id`, and `required_output`.
- Both engine `required_context` files exist and are readable.
- Work request JSON retains `RETURN_RECORDED_PROOF_ACCEPTED`, matching `objective_sha256`, and automation diagnosis `carrier_intake_ready` (gate receipt only).
- Monolith carrier loop modules import cleanly and **121** focused tests pass.
- README M86 bridge bullets align with repo-observed MCP connector contract surfaces (`ion_request_codex_work_packet`, `ion_submit_task_return`, `ion_action_branch_invoke`).

**Stale or missing (VERIFIED / INFERENCE):**

| Item | Status |
| --- | --- |
| Executable carrier loop under `ION_VNEXT/04_carriers` | **MISSING** — README-only frame |
| Gap-return body from 2026-06-02 runs | **MISSING** — `codex_queue_runs/` dir pruned |
| Work-request paths `Needs_Routed/ION_DOMAIN_WEAVE_FULL_ION_MASTER_PLAN_v0_1.md` and `Needs_Routed/M103_DOMAIN_WEAVE_INTEGRATED_SUBSTRATE_PLAN.md` | **MISSING at shell root** — stale required_context_reads |
| Return contract in README (`RESULT` section) vs dynamic-swarm gap-return (9 sections) | **DIVERGENT** |
| vNext promotion of queue runners / full `ion_carrier_*` loop | **NOT STARTED** — only mount-receipt primitive in ion_core |
| `ion_carrier_mount_receipt.py` monolith vs vNext copies | **DIVERGENT** — same size, `diff` reports difference |
| Domain Weaver live carrier binding | **INFERENCE from projection** — spawn/queue execution remains monolith-side; vNext lane is review target only |

**INFERENCE (unverified):** Whether the 2026-06-02 accepted return's carrier test counts matched today's 121/121 — original markdown body unavailable for diff.

### PRODUCTION SPEC GAP REVIEW

Ranked by production-cutover impact (candidate assessment):

1. **Empty vNext carrier lane vs live monolith loop (CRITICAL)**  
   `ION_VNEXT/04_carriers` is a single README. The operative carrier loop — Codex queue runner (8651 lines), Cursor queue runner (399 lines), onboard/continue/tick/task-return chain, and Codex carrier sync/domain modules — lives entirely in `ION/04_packages/kernel/`. vNext canon declares Codex CLI as primary dogfood carrier but does not host runnable loop code in the lane that claims to represent it. Production spec requires either phased promotion into `04_carriers` or an explicit source-pool map that names monolith modules as authoritative until promotion — today the README says the latter posture but provides no module index, test matrix, or promotion gates.

2. **Return-contract fragmentation across carriers (HIGH)**  
   Three competing contracts coexist: (a) README 3-section Codex return, (b) dynamic-swarm 9-section gap return, (c) kernel `ion_carrier_task_return.py` proof gates tied to monolith ledger paths. No vNext-unified carrier return schema ties Cursor spawn returns, Codex task returns, and Domain Weaver fanin settlement. `QUALITY_STANDARD.yaml` requires receipt-backed state transitions; the lane does not define how vNext carrier returns inherit receipts across Codex/Cursor/ChatOps surfaces.

3. **No vNext carrier test harness or CI binding (HIGH)**  
   Monolith has extensive carrier tests (121 in focused subset alone). vNext has **zero** tests under `04_carriers`. Only `ion_carrier_mount_receipt` control tests (12) exist in `ion_core`. Shell-root `pyproject.toml` `testpaths = ["ION/tests"]` does not cover vNext carrier promotion. Production spec cannot cut over carrier behavior without a vNext-local or cross-root pytest job proving queue-runner parity.

4. **Dual `ion_carrier_mount_receipt` implementations (MEDIUM–HIGH)**  
   Monolith and vNext each hold 518-line modules that differ. `CONTROL_SURFACE_REGISTRY.yaml` points to vNext copy; live carrier onboarding paths in monolith import monolith copy. Same class of divergence as lane-8 kernel-core finding.

5. **Cursor carrier deferred in front door but implemented in monolith (MEDIUM)**  
   `AI_START_HERE.md` marks Cursor extension/SDK as reference-only, yet `ion_cursor_queue_runner.py` and `ion_carrier_task_return.py` implement a bounded Cursor Agent CLI loop in monolith. vNext lane README lists Cursor among deferred/reference carriers without reconciling live monolith implementation status.

6. **Domain Weaver orchestration subsumes carrier dispatch (MEDIUM)**  
   `ion_domain_weaver_spawn_request_dispatcher.py`, terminal worker maintainer, and live carrier binding plans execute from monolith context — not from `ION_VNEXT/04_carriers`. Lane 10 documents roles; DW runtime owns spawn/queue/fanin. Production-grade integration requires explicit seam between DW binding and vNext carrier canon.

7. **Harvest durability / pruned run bodies (MEDIUM — addressed by this write)**  
   Accepted 2026-06-02 returns stored bodies under volatile `codex_queue_runs/`; pruning evaporated lane knowledge. This durable artifact restores inspectable evidence; discipline must extend to fanin/nemesis for remaining lanes.

8. **Live MCP / Action Gateway carrier smoke deferred (LOW–MEDIUM, tracked)**  
   README and M93 canon correctly defer live listener proof. Repo-observed connector contract exists; production cutover still needs optional smoke per `vnext_optional_live_mcp_supabase_smoke_proof`.

### DOMAIN WEAVER EVOLUTION REVIEW

**Engine alignment (VERIFIED):** Lane 10 is a first-class entry in `_domain_weaver_vnext_productization_lanes` with `candidate_only: True`, `worker_start_authority: False`, `accepted_state_authority: False`. Dynamic swarm plan primary mission: `ion_vnext_production_spec_with_production_grade_domain_weaver_integration`. `DOMAIN_WEAVER_PROJECTION.json` edges `domain_context_ref:ion_vnext_carriers` → `ION_VNEXT/04_carriers/README.md`.

**Adaptive topology posture (VERIFIED):** `TOPOLOGY_ADAPTIVE_CONTROL_POLICY.candidate.json` rejects fixed worker/domain counts; operator parallelism ceiling 32 is reference-only. Lane sizing for swarm wave 10 comes from engine materialization, not from executable content in `04_carriers`.

**Divergence (VERIFIED):**

- **Live execution path:** Domain Weaver monolith orchestrates spawn dispatch, terminal workers, and queue governance from `ION/04_packages/kernel/`. Lane 10 path is a **documentation frame** referenced by projection and work requests, not imported runtime.
- **Queue governor evidence:** `WAITING_ACCEPTED_SUCCESSOR_RECONCILIATION.latest.json` reports `work_lane_projection_ready: false` and waiting requests — carrier-loop gap review does not by itself clear queue settlement.
- **Approval governor:** `worker_started_count: 0` in approval ledger; semi-auto approvals exist for queue-when-bound, but no live carrier binding promotes vNext lane code.
- **Settlement posture:** 2026-06-02 `RETURN_RECORDED_PROOF_ACCEPTED` reflects **gate/receipt acceptance** on submitted return metadata, not production promotion of carrier loop into vNext.

**INFERENCE:** Until a source-pool map + promotion plan lands, Domain Weaver "production-grade integration" for the carrier loop remains **plan-level** despite monolith test green — the vNext lane does not yet host the loop it names.

### BLOCKERS

**Explicit blockers to production cutover / accepted-state move:**

1. **No executable carrier loop in vNext lane target** — `ION_VNEXT/04_carriers` is README-only; live loop bound to monolith kernel.
2. **No unified vNext carrier return contract** — README 3-section vs swarm 9-section vs monolith proof gates; blocks steward fanin without reconciliation packet.
3. **Dual `ion_carrier_mount_receipt` authority** — registry points vNext; runtime uses monolith; implementations differ.
4. **`production_execution_authority_not_set`** — M102 closes no gates; operator authority decision not recorded (`AUTHORITY_BOUNDARIES.md`).
5. **Pruned lane-10 return bodies** — historical markdown evidence incomplete on disk (mitigated by this durable re-drive, not retroactive recovery).
6. **Stale work-request context paths** — two `Needs_Routed/*` required reads missing at shell root; context-proof gate would flag on strict re-run unless paths repaired or aliased.
7. **`DOMAIN_WEAVE_READ_FIRST_BINDING` steward gate** — `can_continue_locally: false` for cross-domain promotion using DW guidance without steward review.

**Not blockers for continued candidate review work:** monolith carrier imports; 121/121 focused carrier tests; lane builder inclusion; README readability; this durable harvest write.

### RECOMMENDED NEXT PACKET

**Single most valuable next bounded packet:**

**`PCKT-VNEXT-CARRIER-LOOP-SOURCE-POOL-MAP-AND-PROMOTION-PLAN-20260617`**

**Objective:** Produce a candidate source-pool map + phased promotion plan that (a) inventories every monolith carrier module (`ion_codex_queue_runner`, `ion_cursor_queue_runner`, full `ion_carrier_*` + `ion_codex_*carrier*` chain) with test coverage and MCP/ChatOps touchpoints, (b) defines which modules land under `ION_VNEXT/04_carriers/` vs remain monolith-referenced during transition, (c) reconciles return contracts (README 3-section, swarm 9-section, `ion_carrier_task_return` gates) into one vNext carrier return schema candidate, (d) resolves `ion_carrier_mount_receipt` monolith↔vNext divergence with nemesis-reviewed diff, (e) repairs or re-aliases missing `Needs_Routed/*` context paths in work-request templates, and (f) specifies pytest/CI proof before any code move.

**Role:** `role.mason` + `role.nemesis` review + `role.steward` receipt custody.

**Authority ceiling:** candidate map + plan + read-only diff artifacts in first pass; **no source edits, no queue runner starts, no promotion** until operator approves promotion strategy.

**Evidence that would gate any source edit / live worker start / promotion:**

- Nemesis-signed module map with explicit authority owner per true name (monolith vs vNext vs shared shim).
- Unified return-contract YAML accepted by context-proof and template-action gates in monolith harness.
- pytest green: existing monolith carrier suite + new vNext carrier tests (or approved cross-root job) from documented install path.
- Queue-governor clearance: `work_lane_projection_ready: true` for carrier-loop work class after reconciliation.
- Steward receipt landing promotion decision in `ION/05_context/current/` (not chat).
- DW approval governor live-binding record if any queue runner start is requested.

**Follow-on lane (after map/plan):** drive **lane 11** (`ion_vnext_runtime_bridge`, `ION_VNEXT/05_runtime`) — Actions/MCP/ChatOps bridge is the natural integration seam for carrier queue surfaces documented in README M86 bullets.

### ION OPERATIONAL POSTURE

This artifact is **candidate-only**. It records read-only inspection, import attempts, and pytest evidence. It does **not** ratify production state, close cutover gates, start live workers, or authorize source edits.

**Before any real change, separate proof packets and explicit authority would be required for:**

| Action | Required authority |
| --- | --- |
| Source edit (promotion, shims, README contract fix) | Operator-approved bounded packet + steward integration |
| Live worker / Codex or Cursor queue start | DW approval governor + `worker_start_authority` + live carrier binding |
| Accepted-state / production cutover | M102+ operator decision record; `production_execution_authority` proof |
| Service restart / MCP mutation / Supabase write | Front-door hard stops per `AUTHORITY_BOUNDARIES.md` |
| Secret access | Explicit vault packet — never from this lane |
| Git push | Operator approval per M97A scope |
| Deletion / archive of runtime artifacts | Steward + source-pool audit |

**Carrier posture:** `role.mason` bounded review worker; one write to durable harvest path only. Synthesis is not settlement. Prior `RETURN_RECORDED_PROOF_ACCEPTED` on the 2026-06-02 request remains a **gate receipt**, not a substitute for this regained body or for production promotion of carrier loop code into `ION_VNEXT/04_carriers`.
