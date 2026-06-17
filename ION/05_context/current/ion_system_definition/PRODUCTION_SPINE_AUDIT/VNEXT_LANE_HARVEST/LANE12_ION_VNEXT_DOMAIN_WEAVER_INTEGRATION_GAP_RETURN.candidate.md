```
lane_id: ion_vnext_domain_weaver_integration (ordinal 12)
request_id: codex_req_domain_weaver_dynamic_swarm_12_domain_ion_vnext_domain_weaver_integration_20260602_attempt_001
objective_sha256: 9fd0fbeb2b99c54245d12f72ec91b84644f6cbc50c395edd4a58a11d1964a440
source_target: ION_VNEXT/06_context/domain_weave
produced_by: Composer carrier (role.mason) — durable re-drive after run-exhaust pruning
produced_at: 2026-06-17T03:54:59Z
write_posture: candidate_only
```

### CONTEXT PROOF

**Shell root proof (VERIFIED):** commands run from `/home/sev/ION - Production/ION_Developement`. Present on disk: `pyproject.toml`, `ION/REPO_AUTHORITY.md`, target `ION_VNEXT/06_context/domain_weave/` (354 files, 12 top-level groups including `dry_runs/`, `tools/`, `review_packets/`).

**Work request packet (VERIFIED):** `ION/05_context/current/chatgpt_connector/codex_work_requests/codex_req_domain_weaver_dynamic_swarm_12_domain_ion_vnext_domain_weaver_integration_20260602_attempt_001.json` — status `RETURN_RECORDED_PROOF_ACCEPTED`, `objective_sha256` matches header, `lane_ordinal` 12, `domain_id` `domain.ion_vnext_domain_weaver_integration`, all authority flags false, `agent_role` implied `role.mason` via lane routing.

**Paths read (one-line note each):**

| Path | Note |
| --- | --- |
| `ION/05_context/current/domain_weaver/DOMAIN_WEAVER_PROJECTION.json` | Live DW projection; embeds lane 12 at ordinal 12; `full_domain_weaver_ready: false`; `weave_status: candidate_coverage_ready`; many `source_registry` refs to `M103I_VNEXT_DOMAIN_REGISTRY.candidate.yaml` |
| `ION/05_context/current/domain_weaver/swarm_evolution/DYNAMIC_SWARM_OPERATION_PLAN.candidate.json` | 15 adaptive lanes; lane 12 = `domain.ion_vnext_domain_weaver_integration` → `ION_VNEXT/06_context/domain_weave`; fanin ordinals 14–15 |
| `ION/05_context/current/domain_weaver/fission_dryrun/DOMAIN_TOPOLOGY_AUDIT.candidate.json` | Adaptive topology audit; rejects fixed domain/worker counts; relationship-matrix sizing |
| `ION/05_context/current/domain_weaver/fission_dryrun/TOPOLOGY_ADAPTIVE_CONTROL_POLICY.candidate.json` | `fixed_targets_rejected`; reference ceiling 32 is observation not target |
| `ION/05_context/current/domain_weaver/fission_dryrun/FISSION_TEMPLATE_LIBRARY.candidate.json` | Fission template library for adaptive lane materialization |
| `ION/05_context/current/domain_weaver/approval_governor/LIVE_EXECUTION_APPROVAL_GOVERNOR_POLICY.candidate.json` | `max_parallel_live_workers: 3`; `live_execution_authority: false` |
| `ION/05_context/current/domain_weaver/approval_governor/APPROVAL_DECISION_LEDGER.candidate.json` | Approval decision ledger present |
| `ION/05_context/current/domain_weaver/queue_governance/TERMINAL_BACKLOG_LIFECYCLE_METADATA_BACKFILL.latest.json` | 544 classified requests; 69 terminal backlog; 4 waiting |
| `ION/05_context/current/domain_weaver/queue_governance/STALE_WAITING_REQUEST_RECONCILIATION.latest.json` | Stale waiting reconciliation snapshot present |
| `ION/05_context/current/domain_weaver/queue_governance/WAITING_ACCEPTED_SUCCESSOR_RECONCILIATION.latest.json` | Waiting/accepted successor reconciliation snapshot present |
| `ION/05_context/current/ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json` | Active queue; lane-12 request not in waiting set (terminal `RETURN_RECORDED_PROOF_ACCEPTED`) |
| `ION/05_context/current/chatgpt_connector/work_lanes/INDEX.json` | Work-lane index; 69 exact-path requests tracked |
| `ION_VNEXT/00_front_door/AI_START_HERE.md` | vNext front door; read-first routing |
| `ION_VNEXT/00_front_door/AUTHORITY_BOUNDARIES.md` | M102 authority ceiling; execution gates closed |
| `ION_VNEXT/01_canon/QUALITY_STANDARD.yaml` | Production-quality bar (candidate) |
| `ION_VNEXT/01_canon/CONTROL_SURFACE_REGISTRY.yaml` | 29 vNext control surfaces mapped to `02_kernel/ion_core` |
| `ION_VNEXT/01_canon/DOMAIN_WEAVE_READ_FIRST_BINDING.yaml` | M103C binding; `can_continue_locally: false`; routes steward contacts before cross-domain mutation |
| `Needs_Routed/ION_DOMAIN_WEAVE_FULL_ION_MASTER_PLAN_v0_1.md` | **MISSING at shell-root path** — nested copy exists under `projects/WaterPRO/aqua-react-splash/Needs_Routed/` |
| `Needs_Routed/M103_DOMAIN_WEAVE_INTEGRATED_SUBSTRATE_PLAN.md` | **MISSING at shell-root path** — same nested-only location |
| `ION/04_packages/kernel/ion_domain_weaver.py` (~L8273–8393, ~L9072–9077) | `_domain_weaver_vnext_productization_lanes`; lane routes `role.mason` / `implementation_lane` |
| `ION/04_packages/kernel/ion_agent_control_plane.py` (~L46–51, ~L831–891, ~L1105–1112) | `DOMAIN_WEAVE_ROOT` constants; reads map/registry/org-chart/DRA/M103B report at runtime |
| `ION/tests/test_kernel_ion_agent_control_plane.py` (~L5902–6039) | Asserts `domain.ion_vnext_domain_weaver_integration` → `implementation_lane`; dynamic swarm materialization tests |
| `ION_VNEXT/06_context/domain_weave/README.md` | M103B candidate MVP kernel; status not accepted state; documents MVP loop + dry-run lineage M103Y–M104Q |
| `ION_VNEXT/06_context/domain_weave/MANIFEST.json` | `status: candidate_mvp_kernel_landed`; 104-file landed subset; authority all false |

**Lane builder currentness (VERIFIED):** `_domain_weaver_vnext_productization_lanes` guard requires `target_path.exists()` and non-empty `required_context`. All three required_context files exist; lane emitted as **engine ordinal 7** among 8 vNext productization lanes (swarm plan **ordinal 12** among 15 adaptive lanes — numbering differs by topology-evolution prefix lanes 1–5).

```bash
cd "/home/sev/ION - Production/ION_Developement"
PYTHONPATH=ION/04_packages python3 -c "
from pathlib import Path
from kernel import ion_domain_weaver as dw
lanes = dw._domain_weaver_vnext_productization_lanes(Path('.'))
lane = [l for l in lanes if l['lane_kind']=='ion_vnext_domain_weaver_integration'][0]
print('engine_ordinal:', lane['ordinal'], 'path:', lane['path'])
print('required_context_reads:', lane['required_context_reads'])
"
```

```text
engine_ordinal: 7 path: ION_VNEXT/06_context/domain_weave
required_context_reads: ['ION_VNEXT/06_context/domain_weave/README.md', 'ION_VNEXT/06_context/domain_weave/MANIFEST.json', 'ION_VNEXT/01_canon/DOMAIN_WEAVE_READ_FIRST_BINDING.yaml']
```

### TEMPLATE ACTION PROOF

**M103B MVP tool loop re-run (2026-06-17, shell root):**

```bash
cd "/home/sev/ION - Production/ION_Developement"
PYTHONPATH=ION/04_packages python3 ION_VNEXT/06_context/domain_weave/tools/domain_weave_validate.py \
  ION_VNEXT/06_context/domain_weave/examples/ion_like_project --json
```

```json
{"ok": true, "blockers": [], "findings": [], "schema_id": "ion.domain_weave.validation_result.v0_1"}
```

```bash
PYTHONPATH=ION/04_packages python3 ION_VNEXT/06_context/domain_weave/tools/domain_weave_integrated_validate.py \
  ION_VNEXT/06_context/domain_weave/examples/integrated_agent_enterprise
```

```json
{"ok": true, "errors": [], "missing": [], "checks": {"agent_count": 7, "artifact_route_count": 2, "dra_count": 2, "reflex_rule_count": 2}}
```

```bash
PYTHONPATH=ION/04_packages python3 ION_VNEXT/06_context/domain_weave/tools/domain_weave_impact_check.py \
  --ownership ION_VNEXT/06_context/domain_weave/examples/integrated_agent_enterprise/ARTIFACT_OWNERSHIP_INDEX.yaml \
  --reflex ION_VNEXT/06_context/domain_weave/examples/integrated_agent_enterprise/DOMAIN_REFLEX_RULES.yaml \
  --domain ion_vnext_context --action schema_change \
  --touched ION_VNEXT/06_context/domain_weave/schemas/domain_capsule.schema.json \
  --out /tmp/lane12_impact.json
```

```json
{"can_continue_locally": false, "required_contacts": ["steward.context_package_compiler", "steward.receipt_custody"], "settlement_target": "steward.ion_vnext_context"}
```

**Live control-plane consumption probe (VERIFIED):**

```bash
PYTHONPATH=ION/04_packages python3 -c "
from pathlib import Path
from kernel.ion_agent_control_plane import build_agent_control_plane_projection, DOMAIN_WEAVE_ROOT
root = Path('.')
model = build_agent_control_plane_projection(root)
diag = model['diagnostics']
print('domain_weave_status:', diag['domain_weave_status'])
print('domain_weave_validation_status:', diag['domain_weave_validation_status'])
print('domain_weaver weave_status:', diag['domain_weaver']['weave_status'])
print('domain_weaver gap_count:', diag['domain_weaver']['gap_count'])
for p in ['README.md','reports/M103B_VALIDATION_REPORT.json','dry_runs/M103I_VNEXT_DOMAIN_REGISTRY.candidate.yaml']:
    print(p, (root/DOMAIN_WEAVE_ROOT/p).exists())
"
```

```text
domain_weave_status: present
domain_weave_validation_status: candidate_mvp_kernel_landed_and_validated
domain_weaver weave_status: needs_attention
domain_weaver gap_count: 6
README.md True
reports/M103B_VALIDATION_REPORT.json True
dry_runs/M103I_VNEXT_DOMAIN_REGISTRY.candidate.yaml True
```

**Prior run body (VERIFIED missing):** `ION/05_context/current/chatgpt_connector/codex_queue_runs/codex_run_2026-06-02T201452Z0000_codex_req_domain_weaver_dynamic_swarm_12_domain_ion_vnext_domain_weaver_integrat/` — **0 files** on disk (run-exhaust pruned). Task return `2026-06-02T202237Z0000_task_return.json` retains gate receipts (`carrier_intake_ready`) but points at missing `task_return_body.md`.

### VALIDATION

| Check | Result | Evidence |
| --- | --- | --- |
| Target path exists | **PASS** | `ION_VNEXT/06_context/domain_weave/` — 354 files |
| All three `required_context` paths | **PASS** | README, MANIFEST, DOMAIN_WEAVE_READ_FIRST_BINDING |
| `domain_weave_validate.py` (ion_like_project) | **PASS** | `"ok": true`, exit 0 |
| `domain_weave_integrated_validate.py` (integrated_agent_enterprise) | **PASS** | `"ok": true`, 7 agents / 2 DRA / 2 reflex |
| `domain_weave_impact_check.py` (schema_change) | **PASS w/ gate** | `can_continue_locally: false` — expected steward routing |
| M103B validation artifact on disk | **PASS** | `reports/M103B_VALIDATION_REPORT.json` — `status: candidate_mvp_kernel_landed_and_validated` |
| M103D steward review packets on disk | **PASS** | `review_packets/PCKT-M103D-*`, manifest + simulated returns present |
| Control plane reads domain_weave paths | **PASS** | `build_agent_control_plane_projection` resolves all bound paths |
| Kernel invokes domain_weave **tools** at runtime | **NOT OBSERVED** | Engine reads YAML/JSON only; tools are offline proof harness |
| `full_domain_weaver_ready` | **FAIL (expected)** | `DOMAIN_WEAVER_PROJECTION.json` → `false` |
| Packet `Needs_Routed/*` master-plan paths | **FAIL** | Shell-root paths absent; nested project copies only |
| Prior lane-12 return body on disk | **MISSING** | Run dir pruned; mitigated by this durable re-drive |

**M103B MVP kernel inventory (VERIFIED):** 7 Python tools under `tools/`; 8 protocols; schemas + templates; 2 example fixtures; settlement + validation reports; MANIFEST claims 104-file landed subset before reports — directory has since grown via M103I–M104Q dry-run lineage (~250 dry-run artifacts).

**Skipped / not attempted:** `pip install`, editable install, live worker start, service restart — forbidden by packet posture.

### LANE CURRENTNESS REVIEW

**Verdict: PARTIALLY CURRENT — on-disk substrate is live-bound and MVP-validated; production-grade DW integration and durable return bodies remain open.**

**Current (VERIFIED):**

- Target `ION_VNEXT/06_context/domain_weave` exists with full M103B MVP kernel + extended dry-run/review lineage (M103D–M104Q).
- Engine `_domain_weaver_vnext_productization_lanes` and `DYNAMIC_SWARM_OPERATION_PLAN.candidate.json` both list lane with matching path, domain_id, and required_context.
- Lane routes to `role.mason` / `implementation_lane` / `ion_vnext_domain_weaver_integration_gap_review` (`ion_domain_weaver.py` ~L9072–9077).
- `ion_agent_control_plane.py` declares `DOMAIN_WEAVE_ROOT` and consumes README, M103I registry/map, enterprise org-chart/DRA index, and M103B validation report in every control-plane projection build.
- M103B tool loop re-validates green on 2026-06-17.
- Work request JSON retains `RETURN_RECORDED_PROOF_ACCEPTED` with matching `objective_sha256`.

**Stale or missing (VERIFIED / INFERENCE):**

1. **Pruned 2026-06-02 run body** — automation gate receipts exist; durable markdown body lost until this re-drive.
2. **`Needs_Routed/` master-plan paths** — packet contract paths missing at shell root; breaks strict context-proof completeness for L0–L15 planning refs cited in README.
3. **README last-updated 2026-05-24** — does not mention dynamic-swarm lane 12 harvest discipline, fanin ordinals 14–15, or live `DOMAIN_WEAVE_ROOT` binding in `ion_agent_control_plane.py` (INFERENCE: discoverability gap for carriers reading README alone).
4. **`DOMAIN_WEAVE_READ_FIRST_BINDING.yaml` still declares `can_continue_locally: false`** — canon binding unchanged since M103C; cross-domain mutation guidance remains steward-gated.
5. **Dual ordinal numbering** — engine vNext productization ordinal 7 vs swarm plan ordinal 12 (VERIFIED); not a path mismatch but a carrier confusion risk.
6. **Substrate vs operational DW split** — `domain_weave` is candidate graph/witness substrate; live orchestration, queue governance, and projection mutation live under `ION/05_context/current/domain_weaver/` with `full_domain_weaver_ready: false`.

### PRODUCTION SPEC GAP REVIEW

**M103B Domain Weave MVP kernel completeness (VERIFIED):**

The landed subset proves the closed loop documented in README/MANIFEST:

```text
discover → validate → compile neighborhood/edge evidence → impact check → dry-run activation plan → settlement/non-claims
```

Landable artifacts: `protocols/` (8), `schemas/`, `templates/`, `tools/` (7), `examples/ion_like_project`, `examples/integrated_agent_enterprise`, M103B reports/settlement. **Excluded** from M103B landing per MANIFEST: `evidence/`, `packets/`, bulk L0–L15 promotion.

**What the live engine actually consumes from `domain_weave` (VERIFIED via grep + control-plane build):**

| Consumer | Paths / behavior |
| --- | --- |
| `ion_agent_control_plane.py` L46–51 | Constants: `DOMAIN_WEAVE_ROOT`, README, `dry_runs/M103I_VNEXT_DOMAIN_WEAVE_MAP.candidate.yaml`, `dry_runs/M103I_VNEXT_DOMAIN_REGISTRY.candidate.yaml`, `examples/integrated_agent_enterprise/AGENT_ORG_CHART.yaml`, `DIRECT_RESPONSIBLE_AGENT_INDEX.yaml` |
| `ion_agent_control_plane.py` L831–891 | `_domain_rows()` parses registry/map YAML into cockpit domain rows; attaches org-chart agents + DRA ownership |
| `ion_agent_control_plane.py` L1105–1112 | Reads `reports/M103B_VALIDATION_REPORT.json`; surfaces `domain_weave_status`, validation status, readme excerpt in diagnostics |
| `DOMAIN_WEAVER_PROJECTION.json` | Multiple domains cite `source_registry: .../M103I_VNEXT_DOMAIN_REGISTRY.candidate.yaml`; lane 12 entry; context-ref edges to README + REAL_USE_GATE protocol |
| `ION/03_registry/ion_action_mcp_branch_leader_registry.yaml` | Refs `MANIFEST.json`, `DOMAIN_WEAVE_REAL_USE_GATE_PROTOCOL.md` |
| `ion_domain_weaver.py` | Lane spec + work-request materialization for gap review; does **not** import domain_weave Python tools |

**NOT consumed at runtime (VERIFIED):** domain_weave CLI tools (`domain_weave_discover.py`, etc.) — offline proof only unless a carrier invokes them manually.

**Production-spec gaps (ranked):**

1. **No runtime tool integration** — MVP tools validate offline; control plane reads static YAML/JSON witness files only. Production-grade integration requires a bounded kernel hook or scheduled proof runner that re-validates substrate freshness and feeds results into DW projection/compliance blocks without claiming accepted state.

2. **Witness substrate vs operational DW registry** — Live queue, spawn dispatch, activation plane, and `DOMAIN_WEAVER_PROJECTION.json` mutation paths live under `ION/05_context/current/domain_weaver/`. `domain_weave` M103I registry is referenced as `source_registry` but `full_domain_weaver_ready: false` and control-plane `gap_count: 6` indicate unresolved binding/compliance gaps between the two trees.

3. **Real-use / steward gate still closed** — `DOMAIN_WEAVE_READ_FIRST_BINDING.yaml` and impact-check output both require `steward.context_package_compiler` + `steward.receipt_custody` before schema/template/context-package mutations. M103F `DOMAIN_WEAVE_REAL_USE_GATE_PROTOCOL.md` defines candidate gate law; no accepted-state real-use gate settlement observed on disk.

4. **L0–L15 master plan not bound at shell root** — README cites full master plan; packet `required_context_reads` paths fail at `Needs_Routed/` shell root. Integrated substrate plan similarly absent — limits production-spec traceability from vNext lane to enterprise weave roadmap.

5. **MVP scope vs production mission mismatch** — Swarm primary mission: `ion_vnext_production_spec_with_production_grade_domain_weaver_integration`. M103B MANIFEST explicitly excludes evidence/packets/bulk promotion. Current substrate is **candidate MVP**, not production-grade DW integration.

### DOMAIN WEAVER EVOLUTION REVIEW

**Engine alignment (VERIFIED):** Lane 12 is a first-class dynamic-swarm candidate lane with `candidate_only: True`, `worker_start_authority: False`, `accepted_state_authority: False`. Materialization template in `ion_domain_weaver.py` routes to `implementation_lane` with supporting `role.steward` + `role.nemesis`. Tests assert `domain.ion_vnext_domain_weaver_integration` maps to `implementation_lane` (~L6038–6039).

**Adaptive sizing (VERIFIED):** `TOPOLOGY_ADAPTIVE_CONTROL_POLICY.candidate.json` rejects fixed domain/worker counts; `dynamic_start_window: 3` in swarm plan; reference ceiling 32 is stress guardrail only — consistent with packet forbidden action `do_not_replace_adaptive_sizing_with_fixed_worker_count`.

**Evolution posture (VERIFIED / INFERENCE):**

- **Substrate evolution:** M103B → M103C read-first binding → M103D/E review packets → M103F real-use gate protocol → M103I self-map dry-run → M103Y–M104Q steward/work-release retry lineage — all under `domain_weave/dry_runs/` as candidate receipts, not accepted ION state.
- **Operational DW evolution:** Queue governance (544 requests), approval governor, need-based expansion, route gate matrix, and dynamic-swarm fanin gates (ordinals 14–15) evolve independently under `ION/05_context/current/domain_weaver/`.
- **INFERENCE:** Production-grade integration requires an explicit **reconciliation packet** wiring M103I vNext domain registry edges into DW projection compliance, plus a freshness proof that `domain_weave` witness files match what control plane reads — without conflating candidate substrate with accepted registry state.

**Projection weave status (VERIFIED):** `DOMAIN_WEAVER_PROJECTION.json` → `"weave_status": "candidate_coverage_ready"` while control-plane diagnostics report `domain_weaver.weave_status: needs_attention` and `gap_count: 6` — dual reporting surfaces; carriers must not treat either alone as production readiness.

### BLOCKERS

**Explicit blockers to production cutover / accepted-state move:**

1. **`full_domain_weaver_ready: false`** — DW projection compliance block; domain_weave substrate alone cannot close this.
2. **`DOMAIN_WEAVE_READ_FIRST_BINDING` / impact-check steward gate** — `can_continue_locally: false`; real cross-domain mutations blocked until steward settlement + M103F real-use gate proof.
3. **No runtime integration of domain_weave tools** — kernel reads witness files only; no automated freshness/revalidation loop bound to control plane or DW compliance.
4. **Pruned lane-12 return bodies** — historical markdown evidence incomplete on disk (mitigated by this re-drive, not retroactive recovery).
5. **Shell-root `Needs_Routed/` master-plan paths missing** — breaks strict packet context-proof for L0–L15 planning refs.
6. **`production_execution_authority_not_set`** — M102 / operator authority decision not settled (inherits from sibling vNext lanes).
7. **Dual-tree reconciliation unsettled** — `ION_VNEXT/06_context/domain_weave` (witness) vs `ION/05_context/current/domain_weaver` (operational) without nemesis-reviewed binding matrix.

**Not blockers for continued candidate review work:** M103B tool green paths; lane builder inclusion; required_context readability; M103D review packet presence on disk.

### RECOMMENDED NEXT PACKET

**Single most valuable next bounded packet:**

**`PCKT-VNEXT-DW-SUBSTRATE-RUNTIME-BINDING-AND-M103F-READINESS-20260617`**

**Objective:** (a) Produce a candidate binding matrix mapping every `DOMAIN_WEAVE_ROOT` path in `ion_agent_control_plane.py` to its DW projection node, freshness proof, and revalidation command; (b) define a read-only control-plane diagnostic extension that runs `domain_weave_validate` + `domain_weave_integrated_validate` on schedule/carrier-invoke without mutating source; (c) reconcile `M103I_VNEXT_DOMAIN_REGISTRY.candidate.yaml` entries with `DOMAIN_WEAVER_PROJECTION.json` domain rows (diff + nemesis review); (d) prepare M103F real-use gate proof harness checklist per `DOMAIN_WEAVE_REAL_USE_GATE_PROTOCOL.md`; (e) reroute or copy `Needs_Routed/*` master-plan paths to shell-root canonical locations or update packet path contracts.

**Role:** `role.mason` primary; `role.steward` + `role.nemesis` review.

**Authority ceiling:** candidate plan + read-only diff/validation artifacts only; **no source edits**, live worker start, git push, or accepted-state claims in first pass.

**Evidence that would gate any source edit / promotion:**

- Nemesis-reviewed binding matrix with no silent path drift between control plane reads and on-disk files.
- Revalidation harness output `"ok": true` archived under `ION/05_context/current/` with dated receipt.
- M103F gate checklist completed with explicit simulated-vs-real steward disclosure.
- Fanin lane 14 (`dynamic_swarm_fanin_settlement`) can ingest lane 12 durable return + lanes 6–13 returns without overclaim.
- Operator approval before any registry mutation, service restart, or production authority claim.

**Follow-on lane:** drive **lane 14** fanin settlement after lanes 6–13 durable returns are regained; then **lane 15** nemesis overclaim audit per swarm plan.

### ION OPERATIONAL POSTURE

This artifact is **candidate-only**. It records read-only inspection, tool re-runs, control-plane projection probes, and grep evidence. It does **not** ratify production state, close cutover gates, start live workers, or authorize source edits.

**Before any real change, separate proof packets and explicit authority would be required for:**

| Action | Required authority |
| --- | --- |
| Source edit (substrate, kernel binding, registry reconciliation) | Operator-approved bounded packet + steward integration |
| Live worker / Codex queue start | DW approval governor + `worker_start_authority` |
| Accepted-state / production cutover | M102+ operator decision record; `production_execution_authority` proof |
| Service restart / MCP mutation / Supabase write | Front-door hard stops per `AUTHORITY_BOUNDARIES.md` |
| Secret access | Explicit vault packet — never from this lane |
| Git push | Operator approval per repo authority |
| Deletion / archive of runtime artifacts | Steward + source-pool audit |

**Carrier posture:** `role.mason` bounded review worker; one write to durable harvest path only. Synthesis is not settlement. Prior `RETURN_RECORDED_PROOF_ACCEPTED` on the 2026-06-02 request remains a **gate receipt**, not a substitute for this regained body or for production promotion.

**Live-bound substrate note (VERIFIED):** `domain_weave` is **not inert drift** — `ion_agent_control_plane.py:46` binds `DOMAIN_WEAVE_ROOT = Path("ION_VNEXT/06_context/domain_weave")` and reads from it on every projection build. Treating this tree as retireable without kernel migration would break control-plane domain rows and diagnostics.
