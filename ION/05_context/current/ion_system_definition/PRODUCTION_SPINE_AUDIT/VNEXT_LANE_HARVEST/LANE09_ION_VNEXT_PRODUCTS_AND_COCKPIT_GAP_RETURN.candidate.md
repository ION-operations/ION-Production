```
lane_id: ion_vnext_products_and_cockpit (ordinal 9)
request_id: codex_req_domain_weaver_dynamic_swarm_09_domain_ion_vnext_products_and_cockpit_20260602_attempt_001
objective_sha256: 4a1cc23b0cbe71ed733f6a3e3eaea7965558473ce15074c2ef72f9a96dbb1b8c
source_target: ION_VNEXT/03_products
produced_by: Composer carrier (role.mason) — durable re-drive after run-exhaust pruning
produced_at: 2026-06-17T03:58:55Z
write_posture: candidate_only
```

### CONTEXT PROOF

**Shell root proof (VERIFIED):** commands run from `/home/sev/ION - Production/ION_Developement`. Present on disk: `pyproject.toml`, `ION/REPO_AUTHORITY.md`, target `ION_VNEXT/03_products/` (1 file only).

**Paths read (one-line note each):**

| Path | Note |
| --- | --- |
| `ION/05_context/current/chatgpt_connector/codex_work_requests/codex_req_domain_weaver_dynamic_swarm_09_domain_ion_vnext_products_and_cockpit_20260602_attempt_001.json` | Work request; status `RETURN_RECORDED_PROOF_ACCEPTED`; objective_sha256 matches header; points to pruned queue-run body |
| `ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json` | Domain `ion_vnext_products` at `W0_skeleton`; dynamic-swarm lane 9 entry present; maturity `candidate_covered` |
| `ION/05_context/current/domain_weaver/swarm_evolution/DYNAMIC_SWARM_OPERATION_PLAN.candidate.json` | Lane 9 ordinal/path/required_context match engine; `vnext_productization_lane_count: 8` |
| `ION/05_context/current/domain_weaver/fission_dryrun/DOMAIN_TOPOLOGY_AUDIT.candidate.json` | Candidate topology audit; adaptive controls; no live execution authority |
| `ION/05_context/current/domain_weaver/fission_dryrun/TOPOLOGY_ADAPTIVE_CONTROL_POLICY.candidate.json` | Rejects fixed domain/worker counts; reference ceiling 32 (not a target) |
| `ION/05_context/current/domain_weaver/fission_dryrun/FISSION_TEMPLATE_LIBRARY.candidate.json` | Includes `surface_bucket_split_v1` with `cockpit_surface` axis — relevant to products/cockpit split |
| `ION/05_context/current/domain_weaver/approval_governor/LIVE_EXECUTION_APPROVAL_GOVERNOR_POLICY.candidate.json` | Live execution gated; semi-auto candidate queue only |
| `ION/05_context/current/domain_weaver/approval_governor/APPROVAL_DECISION_LEDGER.candidate.json` | Decisions recorded; `worker_started_count: 0` in settlement dry-run assertions |
| `ION/05_context/current/domain_weaver/queue_governance/TERMINAL_BACKLOG_LIFECYCLE_METADATA_BACKFILL.latest.json` | 544 classified requests; 69 terminal backlog; 4 waiting |
| `ION/05_context/current/domain_weaver/queue_governance/STALE_WAITING_REQUEST_RECONCILIATION.latest.json` | Read (present); stale-waiting reconciliation artifact |
| `ION/05_context/current/domain_weaver/queue_governance/WAITING_ACCEPTED_SUCCESSOR_RECONCILIATION.latest.json` | Read (present); waiting-successor reconciliation artifact |
| `ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json` | Read (present); no active row matching lane-9 request id at review time |
| `ION/05_context/current/chatgpt_connector/work_lanes/INDEX.json` | Meta-swarm lanes listed; lane-9 not a dedicated work-lane row |
| `ION_VNEXT/00_front_door/AI_START_HERE.md` | Active mission lists products implicitly; **dAimon = deferred**; Supabase mirror/cockpit only |
| `ION_VNEXT/00_front_door/AUTHORITY_BOUNDARIES.md` | M102 authority ceiling; `ION_GPT` and `dAimon` listed as **evidence**, not vNext home |
| `ION_VNEXT/01_canon/QUALITY_STANDARD.yaml` | Production bar: receipt-backed, dogfoodable, no source migration without audit |
| `ION_VNEXT/01_canon/CONTROL_SURFACE_REGISTRY.yaml` | Bridge surfaces (MCP, Supabase mirror, action gateway) point to **monolith** `ION/04_packages/kernel/*`, not `03_products` |
| `ION_VNEXT/01_canon/DOMAIN_WEAVE_READ_FIRST_BINDING.yaml` | `can_continue_locally: false`; steward contacts required before cross-domain promotion |
| `Needs_Routed/ION_DOMAIN_WEAVE_FULL_ION_MASTER_PLAN_v0_1.md` | **MISSING at shell root** — only copy under `projects/WaterPRO/aqua-react-splash/Needs_Routed/` |
| `Needs_Routed/M103_DOMAIN_WEAVE_INTEGRATED_SUBSTRATE_PLAN.md` | **MISSING at shell root** — same nested location only |
| `ION/04_packages/kernel/ion_domain_weaver.py` (~L8313–8323, ~L9049–9055) | Lane 9 spec + `JOC_UI_CANON_STEWARD` role binding |
| `ION/tests/test_kernel_ion_agent_control_plane.py` (~L5894–5904) | Asserts `vnext_productization_lane_count > 0`; integration lane present |
| `ION_VNEXT/03_products/README.md` | **Stub only** — "candidate directory contract only"; "not populated with migrated source in M25" |
| `ION_VNEXT/01_canon/LEGACY_SOURCE_POOLS.yaml` | Maps `ION_GPT` → `03_products/custom_gpt`, `dAimon` → `03_products/daimon` (both **unpromoted**) |
| `ION_VNEXT/01_canon/FAMILY_REGISTRY.yaml` | `daimon` in `deferred_or_reference_by_default` |
| `ION_GPT/README.md` | 272 files at shell root; operator upload kit paths; product evidence pool |
| `dAimon/README.md` | 19,920 files at shell root; candidate hackathon implementation; deferred in front door |
| `ION/04_packages/kernel/ion_cockpit_view_model.py` | Live cockpit projection; references `ION_GPT/03_ACTIONS/*` paths |

**Lane builder currentness (VERIFIED):** `_domain_weaver_vnext_productization_lanes` guard passes for `ION_VNEXT/03_products` — both required_context files exist. Live builder emits lane with `lane_kind: ion_vnext_products_and_cockpit`, `target_path_exists: true`. **Ordinal note:** live builder assigns **ordinal 4** (8 vNext lanes total, renumbered); swarm plan JSON keeps **ordinal 9** in the static 15-lane table — same path/kind, different ordinal index (INFERENCE: cosmetic in plan vs runtime builder, not a path mismatch).

### TEMPLATE ACTION PROOF

**Target surface inspection (VERIFIED — stub, no importable product package):**

```bash
cd "/home/sev/ION - Production/ION_Developement/ION_VNEXT/03_products"
ls -la
find . -type f
python3 -c "import os; print(os.listdir('.'))"
```

**Key output (VERIFIED):**

```text
-rw-rw-r-- 1 sev sev 487 May 19 19:17 README.md
./README.md
['README.md']
```

**Pytest in target (VERIFIED — no tests):**

```bash
cd "/home/sev/ION - Production/ION_Developement/ION_VNEXT/03_products"
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -p no:cacheprovider .
```

```text
collected 0 items
============================ no tests ran in 0.01s =============================
```

**Live cockpit projection smoke (monolith — product/cockpit runtime today, VERIFIED):**

```bash
cd "/home/sev/ION - Production/ION_Developement"
PYTHONPATH=ION/04_packages python3 -c "
from kernel.ion_cockpit_view_model import build_worker_cockpit_view_model
m = build_worker_cockpit_view_model('.')
print('schema:', m.get('schema_id'))
print('top_keys:', sorted(m.keys())[:6])
"
```

```text
schema: ion.worker_cockpit_view_model.v1
top_keys: ['active_worker', 'event_links', 'fanout', 'filters', 'generated_at', 'latest_worker_runs']
```

**Legacy product pool sample test (ION_GPT — outside lane target, VERIFIED):**

```bash
cd ".../ION_GPT/99_WORKER_DETAILS/source_current/custom_gpt_sandbox_carrier"
PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest -p no:cacheprovider \
  tests/test_front_door_carrier_product_contract_candidate.py -q
```

```text
1 failed, 6 passed in 0.06s
FAILED ...::test_instructions_bind_product_contract
AssertionError: 'FRONT_DOOR_CARRIER_PRODUCT_LAW' not in instructions text
```

**Lane builder invocation (VERIFIED):**

```bash
PYTHONPATH=ION/04_packages python3 -c "
from pathlib import Path
from kernel.ion_domain_weaver import _domain_weaver_vnext_productization_lanes
lanes = _domain_weaver_vnext_productization_lanes(Path('.'))
print([l['lane_kind'] for l in lanes])
"
```

```text
['ion_vnext_front_door_authority', 'ion_vnext_canon_control_surface', 'ion_vnext_kernel_core',
 'ion_vnext_products_and_cockpit', 'ion_vnext_carrier_loop', 'ion_vnext_runtime_bridge',
 'ion_vnext_domain_weaver_integration', 'ion_vnext_release_cutover']
```

### VALIDATION

| Check | Result | Evidence |
| --- | --- | --- |
| Target path exists | **PASS** | `ION_VNEXT/03_products/README.md` (487 bytes) |
| Required_context (engine) | **PASS** | README + `QUALITY_STANDARD.yaml` both present |
| Importable code in `03_products` | **N/A — STUB** | No `.py`, no `pyproject.toml`, no package |
| Pytest in `03_products` | **N/A — 0 collected** | Exit code 5; no tests ran |
| `build_worker_cockpit_view_model('.')` | **PASS** | Returns `ion.worker_cockpit_view_model.v1` |
| ION_GPT product-contract test (sample) | **PARTIAL** | 6 passed, 1 failed (instructions drift) |
| dAimon test suite | **NOT RUN** | 509 `test_*.py` files; front door marks dAimon **deferred**; bounded read-only review did not execute full suite |
| Prior lane-9 run body on disk | **MISSING** | `codex_queue_runs/codex_run_2026-06-02T192726Z0000_*_products_and_cockpit_2/` — directory absent (run-exhaust pruned) |
| Packet `Needs_Routed/*` required reads at shell root | **FAIL (stale paths)** | `Needs_Routed/` missing at shell root; content only under WaterPRO nested path |
| Work request gate receipt | **PASS (receipt only)** | `2026-06-02T193423Z0000_task_return.json` — context proof accepted; body preview only (~1200 chars) |

**Product evidence inventory (VERIFIED, not in lane target):**

| Pool | Shell path | File count | vNext canonical (canon) | On disk under `03_products` |
| --- | --- | --- | --- | --- |
| Custom GPT | `ION_GPT/` | 272 | `03_products/custom_gpt` | **MISSING** |
| dAimon | `dAimon/` | 19,920 | `03_products/daimon` | **MISSING** |
| Cockpit runtime | `ION/04_packages/kernel/ion_cockpit_*.py` | many modules | (not mapped to `03_products`) | **N/A — lives in monolith** |

### LANE CURRENTNESS REVIEW

**Verdict: PARTIALLY CURRENT — lane spec and stub contract match engine/plan; product surface and cockpit home are not production-spec; legacy pools unmigrated.**

**Current (VERIFIED):**

- Target path `ION_VNEXT/03_products` exists; README explicitly declares candidate skeleton posture.
- Engine lane spec, dynamic swarm plan entry (ordinal 9), and projection domain `ion_vnext_products` agree on path and required_context.
- Work request JSON retains `RETURN_RECORDED_PROOF_ACCEPTED` with matching `objective_sha256`.
- `LEGACY_SOURCE_POOLS.yaml` documents intended promotion targets (`custom_gpt`, `daimon`) — canon is **ahead of disk** under `03_products`.
- Live cockpit view-model builds from monolith kernel; references `ION_GPT` action schema paths.

**Stale or missing (VERIFIED / INFERENCE):**

| Item | Status |
| --- | --- |
| Gap-return **body** from 2026-06-02 runs | **MISSING** — pruned queue-run dir; task_return retains preview + sha only |
| Migrated product code under `03_products/` | **MISSING** — README-only stub (by design per M25) |
| `03_products/custom_gpt`, `03_products/daimon` | **MISSING** — canon paths not materialized |
| Cockpit as vNext product lane artifact | **DIVERGENT** — runtime in `ION/04_packages/kernel/` + Supabase mirror plane (`05_runtime` lane), not `03_products` |
| Packet required_reads `Needs_Routed/*.md` at shell root | **STALE/MISSING** — paths in work request do not resolve from shell root |
| Domain maturity in projection | **W0_skeleton** — `materialized_mount_count: 0`, `portable_package_count: 0` |
| ION_GPT instruction/product-law alignment | **DRIFT** — 1/7 sample contract tests failed |
| dAimon promotion | **DEFERRED** — `FAMILY_REGISTRY` + `AI_START_HERE` + `LEGACY_SOURCE_POOLS` all defer |
| Durable harvest for lane 9 | **MISSING until this artifact** — `VNEXT_LANE_HARVEST/` had lanes 6–8, 11–14 but not lane 9 |

**INFERENCE (unverified):** Whether the 2026-06-02 accepted return documented the same stub finding — original body unavailable for diff.

### PRODUCTION SPEC GAP REVIEW

Ranked by production-cutover impact (candidate assessment):

1. **Empty product lane vs canon promotion map (CRITICAL)**  
   `03_products` is README-only while `LEGACY_SOURCE_POOLS.yaml` declares `ION_GPT` → `03_products/custom_gpt` and `dAimon` → `03_products/daimon`. No source-pool audit, promotion plan, or curated copy has landed. Production spec requires auditable product surfaces inside vNext — not evidence pools at shell root.

2. **Cockpit runtime not owned by products lane (CRITICAL)**  
   Operator cockpit (`ion_cockpit_view_model.py`, related `ion_*_cockpit*.py` modules) lives in the monolith kernel and projects worker/MCP/Supabase mirror state. The lane name implies products **and** cockpit, but cockpit integration is canon-bound to `05_runtime/supabase_mirror_cockpit` and bridge registry — not materialized under `03_products`. No reconciliation plan links cockpit UI/product release inputs to this lane.

3. **Product evidence fails partial quality bar (HIGH)**  
   Sample ION_GPT product-contract test: **6 passed, 1 failed** (instructions missing `FRONT_DOOR_CARRIER_PRODUCT_LAW`). dAimon deferred with large unmigrated tree (509 test files). Neither pool meets `QUALITY_STANDARD.yaml` "enforceable by tests/gates" inside vNext.

4. **Production authority chain open (HIGH — by design, still a gap)**  
   M102 decision draft ready; `production_execution_authority_not_set`. Product release, GPT Builder mutation, and Supabase mutation remain hard-stopped per `AUTHORITY_BOUNDARIES.md`.

5. **Domain Weaver steward gate blocks cross-domain promotion (MEDIUM)**  
   `DOMAIN_WEAVE_READ_FIRST_BINDING.yaml`: `m103b_impact_result.can_continue_locally: false`. Promoting `ION_GPT`/`dAimon` slices into vNext requires steward review packets before schema/template/context mutations.

6. **Required context path staleness in work request (MEDIUM)**  
   `Needs_Routed/ION_DOMAIN_WEAVE_FULL_ION_MASTER_PLAN_v0_1.md` and `M103_DOMAIN_WEAVE_INTEGRATED_SUBSTRATE_PLAN.md` not at shell root — carriers following the packet literally hit missing paths (content exists only under `projects/WaterPRO/aqua-react-splash/Needs_Routed/`).

7. **Harvest / return durability gap (MEDIUM — addressed by this write)**  
   Accepted swarm returns stored bodies under volatile `codex_queue_runs/`; lane-9 body pruned. Gate receipts ≠ durable gap knowledge.

8. **Projection skeleton posture (LOW as finding, HIGH as blocker for cutover)**  
   `ion_vnext_products` domain: `maturity_estimate: W0_skeleton`, zero mounts/packages — correct honesty, not production-ready.

### DOMAIN WEAVER EVOLUTION REVIEW

**Engine alignment (VERIFIED):** Lane 9 is a first-class entry in `_domain_weaver_vnext_productization_lanes` with `candidate_only: True`, `worker_start_authority: False`, `accepted_state_authority: False`. Role binding: `JOC_UI_CANON_STEWARD` on `context_lane` with supporting `FRONTEND_WORK_SURFACE_ARCHITECT`, `VISUAL_PROOF_AUDITOR`, `role.nemesis` — appropriate for product/cockpit surface gap review, not implementation.

**Divergence (VERIFIED):**

- **Product work absorbed elsewhere:** Domain Weaver terminal-worker missions (Atlas/seat_11, round-table fanout) produced maps and receipts under `ION/05_context/current/domain_weaver/`, not under `ION_VNEXT/03_products`. Projection shows candidate coverage roles (scribe/steward/atlas) pointing at `ion_vnext_products` but **zero materialized mounts**.
- **Fission template anticipates split:** `surface_bucket_split_v1` lists `cockpit_surface` as a child axis — products and cockpit may need separate vNext buckets; today both are unstaged in `03_products`.
- **Live execution path:** Approval governor + ledger allow semi-auto **queue** of candidate workers; `worker_started_count: 0` in control-plane test assertions. Lane review does not authorize live worker start.
- **Settlement posture:** 2026-06-02 proof-accepted status reflects **gate/receipt acceptance**, not product promotion or cockpit cutover.
- **Adaptive topology:** Lane sizing from queue-governor evidence is engine-side; `03_products` contains no DW topology logic — correct for a skeleton lane, but evolution depends on source-pool audit + lane 12 (domain weaver integration) and runtime bridge (lane 11).

**INFERENCE:** Until source-pool audit and cockpit/product bucket split land, Domain Weaver "production-grade integration" for products remains **plan-level** despite correct skeleton discipline.

### BLOCKERS

**Explicit blockers to production cutover / accepted-state move:**

1. **No product code in vNext lane target** — `03_products` is README-only; canon promotion paths (`custom_gpt`, `daimon`) unmigrated.
2. **Cockpit runtime not reconciled to vNext product lane** — monolith kernel owns cockpit; no vNext product/cockpit release bundle or operator surface under `03_products`.
3. **`production_execution_authority_not_set`** — M102 closes no gates; GPT Builder / deploy / Supabase mutation blocked.
4. **Pruned lane-9 return bodies** — historical evidence incomplete on disk (mitigated by this durable re-drive, not retroactive recovery).
5. **`DOMAIN_WEAVE_READ_FIRST_BINDING` steward gate** — `can_continue_locally: false` for cross-domain promotion using DW guidance.
6. **ION_GPT product-law drift** — sample contract test failure indicates instructions/upload-kit misalignment before any promotion claim.
7. **Stale `Needs_Routed/` paths in work-request required_reads** — context proof for those paths fails at shell root unless rerouted or symlinked under steward packet.

**Not blockers for continued candidate review work:** lane builder inclusion; README stub honesty; cockpit view-model local build; partial ION_GPT test green.

### RECOMMENDED NEXT PACKET

**Single most valuable next bounded packet:**

**`PCKT-VNEXT-PRODUCT-SOURCE-POOL-AUDIT-AND-COCKPIT-BUCKET-PLAN-20260617`**

**Objective:** Produce a candidate-only source-pool audit + promotion plan that (a) inventories `ION_GPT/` and deferred `dAimon/` against `LEGACY_SOURCE_POOLS.yaml` canonical targets under `03_products/`, (b) separates **product release inputs** (Custom GPT upload kit, action schemas) from **cockpit mirror surfaces** (monolith view-model, Supabase mirror — likely `05_runtime` lane), (c) runs nemesis-reviewed contract tests on ION_GPT sandbox carrier and records pass/fail matrix, (d) defines minimal curated promotion slices (no bulk copy) with path-policy + receipt requirements per `QUALITY_STANDARD.yaml`, and (e) repairs or re-homes stale `Needs_Routed/` required_read paths for future carriers.

**Role:** `JOC_UI_CANON_STEWARD` + `FRONTEND_WORK_SURFACE_ARCHITECT` + `role.nemesis` review (matches engine binding for this lane).

**Authority ceiling:** audit artifacts + promotion plan + test receipts only; **no source edits, no copy into `03_products`, no GPT Builder mutation** until operator approves promotion slices.

**Evidence that would gate any source edit / promotion:**

- Nemesis-signed source-pool audit matrix with explicit include/exclude per file class.
- ION_GPT product-contract tests green (or documented waivers with steward receipt).
- Path-policy gate approval for each proposed `03_products/custom_gpt/*` path.
- Steward review packets for context-package compiler + receipt custody (per M103B).
- Bounded promotion plan receipt landed in `ION/05_context/current/` (not chat).
- Explicit operator approval before live worker start, git push, GPT Builder change, or production authority claim.

**Follow-on lanes (after audit plan):** lane 11 (`ion_vnext_runtime_bridge`) for MCP/Supabase cockpit bridge; lane 12 (`ion_vnext_domain_weaver_integration`) for DW MVP tool binding — products lane should **feed** those, not duplicate runtime.

### ION OPERATIONAL POSTURE

This artifact is **candidate-only**. It records read-only inspection, stub verification, monolith cockpit smoke, and sample legacy-pool test evidence. It does **not** ratify production state, close cutover gates, start live workers, migrate product source pools, or authorize source edits.

**Before any real change, separate proof packets and explicit authority would be required for:**

| Action | Required authority |
| --- | --- |
| Source edit / promotion into `03_products` | Source-pool audit + path-policy gate + steward integration |
| GPT Builder / Custom GPT knowledge upload mutation | Operator-approved bounded packet; hard stop in front door |
| Cockpit runtime move or Supabase mirror mutation | M86 bridge lane + operator approval; mirror-only authority |
| Live worker / Codex queue start | DW approval governor + `worker_start_authority` |
| Accepted-state / production cutover | M102+ operator decision record; `production_execution_authority` proof |
| Service restart / MCP mutation | Front-door hard stops per `AUTHORITY_BOUNDARIES.md` |
| Secret access | Explicit vault packet — never from this lane |
| Git push | Operator approval per M97A scope |
| Deletion / bulk copy from `ION_GPT` or `dAimon` | Steward + source-pool audit — **forbidden without audit** |

**Carrier posture:** `role.mason` bounded review worker (user-directed re-drive); one write to durable harvest path only. Synthesis is not settlement. Prior `RETURN_RECORDED_PROOF_ACCEPTED` on the 2026-06-02 request remains a **gate receipt**, not a substitute for this regained body or for production promotion of product surfaces.
