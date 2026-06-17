# G2 Durable Fan-In Map and Diagnosis (candidate)

```
schema_id: ion.production_spine.g2_fanin_map_diagnosis.v0_1_candidate
generated_at: 2026-06-17T12:00:00Z (approx)
generated_by: Composer carrier (role.auditor) — read-only G2 gap analysis
posture: candidate_only  (no production / live-execution / accepted-state / source-edit authority)
provenance: READINESS_BURNDOWN.candidate.md (G2 row); LANE14 + LANE15 harvest bodies;
            windowed reads of ION/04_packages/kernel/ion_domain_weaver.py and ion_codex_queue_runner.py;
            on-disk ls/find of codex_queue_runs; live recompute of reconciliation + fanin refs (2026-06-17)
```

## Engine fan-in map

| Component | Role | Key lines | Reads body? | Reads status/intake only? |
| --- | --- | --- | --- | --- |
| `CODEX_QUEUE_RUNS_DIR` | Volatile run-exhaust surface for `run.json` + `task_return_body.md` | `ion_domain_weaver.py:1007`; `ion_codex_queue_runner.py:59` | — | — |
| Run dir + body path allocation | Carrier worker writes under `codex_queue_runs/codex_run_*/` | `ion_codex_queue_runner.py:5711-5722`, `:5933` | writes body | — |
| `RETURN_RECORDED_PROOF_ACCEPTED` setter (work request) | Flips packet status after carrier-intake gates | `ion_chatgpt_browser_mcp_connector_contract.py:5073`, `:4979`; run mirror `ion_codex_queue_runner.py:8496` | no | yes — `accepted_for_carrier_intake`; explicitly `carrier_intake_only: True`, `product_state_accepted: False` (`:5101-5104`) |
| `_domain_weaver_dynamic_swarm_operation_plan` | Plan assembler: topology lanes + vNext productization + fanin + nemesis | `ion_domain_weaver.py:8837-8997` | no | plan metadata |
| `_domain_weaver_vnext_productization_lanes` | 8 vNext productization lane specs (lanes 6–13 class) | `ion_domain_weaver.py:8273+` | no | lane specs |
| Fanin + nemesis lane append | Last two adaptive lanes after topology+productization | `ion_domain_weaver.py:8878-8897` (`fanin_settlement`, `nemesis_overclaim_audit`) | no | lane_kind |
| `_domain_weaver_dynamic_swarm_lane_role` | Role routing incl. fanin (`settlement_lane`) and nemesis | `ion_domain_weaver.py:9086-9098` | no | lane_kind |
| `_domain_weaver_dynamic_swarm_candidate_work_request_templates` | Materializes 1 work-request JSON/lane | `ion_domain_weaver.py:9103-9179` | no | initial `QUEUED_FOR_CODEX_CARRIER` |
| `execute_domain_weaver_action` → `materialize_dynamic_swarm_candidate_work_requests` | Dispatch: queue templates, never start workers | `ion_domain_weaver.py:40720-40784` | no | plan readiness |
| `_domain_weaver_dynamic_swarm_run_records_by_request` | Scans `codex_queue_runs/*/run.json`; sets `task_return_body_present` | `ion_domain_weaver.py:9338-9373` | checks file exists | run status |
| `_domain_weaver_dynamic_swarm_fresh_context_reconciliation` | **Carrier-intake reconciliation** — lane_state from request `status` | `ion_domain_weaver.py:9376-9557` | records body path/present but **does not gate** `lane_state=accepted` on body | **yes** — `accepted_statuses` → `lane_state=accepted` at `:9428-9429`; `all_lanes_resolved_for_fanin` at `:9527-9533` ignores body presence |
| `execute_domain_weaver_action` → `reconcile_dynamic_swarm_fresh_context_return_monitor_stranded_runs` | Materializes reconciliation artifact | `ion_domain_weaver.py:40785-40822` | no | reconciliation summary |
| `_domain_weaver_dynamic_swarm_fanin_reissue_work_request_template` | Builds fanin reissue packet referencing lane body paths | `ion_domain_weaver.py:9560-9700` | collects `latest_run_task_return_body_path` | also status |
| `_domain_weaver_latest_dynamic_swarm_fanin_reissue_refs` | **Semantic fan-in gate** — parses fanin reissue body for readiness verdict | `ion_domain_weaver.py:9703-9764` | **yes** — reads `task_return_body.md` `:9737-9751` | also requires `RETURN_RECORDED_PROOF_ACCEPTED` + `accepted_for_carrier_intake` `:9710-9712` |
| `execute_domain_weaver_action` → `queue_dynamic_swarm_fanin_settlement_reissue` | Queues fanin reissue when reconciliation resolved | `ion_domain_weaver.py:40823-40885` | indirect | `all_lanes_resolved_for_fanin` |
| `_domain_weaver_dynamic_swarm_semantic_blocker_readiness_gate_work_request_template` | Downstream gate after fanin | `ion_domain_weaver.py:9767+` | references fanin body path | fanin_result |
| `_domain_weaver_dynamic_swarm_fresh_current_lifecycle_settlement` | Lifecycle SHA256 replay settlement | `ion_domain_weaver.py:10236-10359` | references lifecycle body path `:10257`; lane binding checks `accepted_for_carrier_intake` `:10306-10307`, not body content | intake flags |
| `execute_domain_weaver_action` → `materialize_dynamic_swarm_fresh_current_lifecycle_settlement` | Materializes lifecycle settlement | `ion_domain_weaver.py:41088-41125` | indirect | `fresh_current_settlement_ready` |
| Durable harvest surface (partial recovery) | Git-tracked gap returns; not wired into fanin engine | `PRODUCTION_SPINE_AUDIT/VNEXT_LANE_HARVEST/` (10 bodies); contract: 9 sections + header hash block (see LANE08 `:1-10`, sections `### CONTEXT PROOF` … `### ION OPERATIONAL POSTURE`) | yes (durable) | separate from engine fanin path |

**Live recompute (2026-06-17, verified):** `_domain_weaver_dynamic_swarm_fresh_context_reconciliation(materialize=False)` → `accepted_return_count=15`, `all_lanes_resolved_for_fanin=true`, `latest_run_task_return_body_present=False` for **all 15** lanes; `_domain_weaver_latest_dynamic_swarm_fanin_reissue_refs` → `accepted=True`, `readiness_gate_ready=False`, finding `accepted_dynamic_swarm_fanin_missing_readiness_packet_verdict`.

**On-disk durability (verified):**

```bash
# codex_queue_runs directory absent; 0 task_return_body* under chatgpt_connector
ls ION/05_context/current/chatgpt_connector/codex_queue_runs  # No such file or directory
find ION/05_context/current/chatgpt_connector -name 'task_return_body*' | wc -l  # 0
# Surviving: 673 task_returns/*.json; preview capped ~1200 chars (sample lane-14 return)
# 18 dynamic_swarm work requests persist with RETURN_RECORDED_PROOF_ACCEPTED
# 10/15 durable harvest bodies in VNEXT_LANE_HARVEST/
```

## Diagnosis

### 1. Where durability breaks

**Write path:** Carrier queue runner allocates `codex_queue_runs/codex_run_<ts>_<request_id>/task_return_body.md` alongside `run.json`, `context_receipt.json`, logs (`ion_codex_queue_runner.py:5711-5733`). Run packet records `task_return_body_path` (`:5933`).

**Prune path:** `codex_queue_runs/` is **gone on disk today** (directory missing; 0 run dirs; 0 `task_return_body*` files). Lane-14 harvest documents all 18 dynamic-swarm requests reference pruned run dirs (`LANE14`: `:46-52`). ACTIVE_CONTEXT_PACKAGE notes run-exhaust pruning, not Phase-0 cleanup.

**What survives:** (a) work-request JSON under `codex_work_requests/` with persisted `status: RETURN_RECORDED_PROOF_ACCEPTED` and `return_packet_paths`; (b) `task_returns/*.json` gate receipts with `accepted_for_carrier_intake: true` and ~1200-char `task_output_preview` + sha256 (verified sample `2026-06-02T194546Z0000_task_return.json`); (c) machine receipts; (d) partial durable re-harvest in `VNEXT_LANE_HARVEST/` (10/15 lanes). Semantic content (gap findings, recommended packets, overclaim matrix inputs) **does not survive** in the volatile layer.

### 2. Carrier-intake acceptance vs semantic completion

**Verdict: architectural decoupling that fails in practice — not a single conflating assignment line, but an absent semantic gate in the reconciliation step.**

Evidence chain:

- Intake is explicitly labeled non-product: `carrier_intake_only: True`, `product_state_accepted: False` (`ion_chatgpt_browser_mcp_connector_contract.py:5101-5104`).
- Work-request `RETURN_RECORDED_PROOF_ACCEPTED` is set on intake acceptance (`:5073`), independent of durable body retention.
- Reconciliation marks `lane_state=accepted` when `request.status ∈ accepted_statuses` only (`ion_domain_weaver.py:9428-9429`) — **does not require** `latest_run_task_return_body_present`.
- `all_lanes_resolved_for_fanin` (`:9527-9533`) checks lane counts and absence of running/stranded/unresolved — **not** body presence — so fanin reissue queueing proceeds with 15/15 accepted and 0 bodies (live recompute confirms).
- Semantic steps **do** require bodies: `_domain_weaver_latest_dynamic_swarm_fanin_reissue_refs` reads and regex-parses `task_return_body.md` for readiness verdict string (`:9737-9751`); without file, `readiness_gate_ready=False`.
- Lifecycle settlement checks `accepted_for_carrier_intake` on task-return JSON, not semantic body content (`:10306-10307`).

**Lane 14 posture (verified):** 15/15 carrier-intake accepted; 0 run bodies; semantic fan-in blocked at fanin reissue readiness gate — consistent with engine behavior, not operator error.

### 3. Gap: existing fanin/settlement lane vs TRUE semantic fan-in

| Stage | What it proves today | Blocked by |
| --- | --- | --- |
| Per-lane worker return + intake | Context/template gate receipts | Bodies pruned from `codex_queue_runs/` |
| `_domain_weaver_dynamic_swarm_fresh_context_reconciliation` | All lanes intaken (`accepted_return_count=15`) | Does not harvest or bind durable bodies |
| Fanin reissue lane (14) + `_domain_weaver_latest_dynamic_swarm_fanin_reissue_refs` | Cross-lane semantic verdict in fanin body | Missing `task_return_body.md` → cannot parse readiness packet ID / verdict |
| Lifecycle + semantic blocker gates | SHA256 replay + blocker resolution | Upstream fanin body + per-lane bodies absent |
| Nemesis overclaim (lane 15) | Cross-lane claim audit | Only 10/15 durable harvests; no engine-fed overclaim matrix from bodies |

**Core gap:** The engine implements a **two-tier** model (intake status → semantic body settlement) but durable bodies live on a **volatile surface** never consolidated into the fanin/settlement read path. Partial manual re-harvest (`VNEXT_LANE_HARVEST/`) is outside `_domain_weaver_dynamic_swarm_run_records_by_request` scan scope (`:9340` glob `codex_queue_runs` only). TRUE semantic fan-in requires durable, hash-verifiable bodies as first-class settlement inputs across all 15 lanes **plus** cross-lane nemesis matrix — not recoverable from status + preview alone.

## Design-direction stub

*(Expand in follow-up packet `PCKT-DOMAIN-WEAVER-DYNAMIC-SWARM-DURABLE-FANIN-SEMANTIC-SETTLEMENT-RE-HARVEST-20260617` — not full design here.)*

1. **Durable settlement-time harvest:** At carrier-intake accept, copy/hash-verify full return body to git-tracked surface (e.g. extend `PRODUCTION_SPINE_AUDIT/VNEXT_LANE_HARVEST/` or sibling `DURABLE_FANIN/`) and index path in work-request metadata — stop relying on `codex_queue_runs/` as semantic source of truth.
2. **Semantic fan-in from durable bodies:** Rewire `_domain_weaver_dynamic_swarm_run_records_by_request` / fanin refs to read durable harvest paths; add cross-lane overclaim matrix step (lane 15) consuming all 15 bodies before `readiness_gate_ready`.
3. **Separate `intake_accepted` from `semantically_settled`:** Reconciliation `lane_state=accepted` should require durable body present (or explicit blocker); introduce distinct `semantically_settled` flag set only after fanin/lifecycle gates pass — do not advance lifecycle on intake status alone.

## Non-claims

Candidate findings; **synthesis is not settlement.** No production authority set. Prior `RETURN_RECORDED_PROOF_ACCEPTED` statuses are gate receipts, not semantic completion or production promotion. Live recompute and disk checks performed 2026-06-17; pruning event not attributed to a specific operator action in this artifact. Design stub is directional only — no source edits, worker starts, or commits implied.
