# ION Multi-Lane Worker Queue Protocol v0.1 Candidate

Status: candidate
Accepted state claim: false
Production authority: false
Live execution authority: false
Created for: removing the single-queue bottleneck across heterogeneous ION workers

## Problem

ION currently exposes a single operational Codex work queue as the dominant scheduling surface for different classes of work and different worker identities. A single append-only intake ledger is acceptable. A single execution queue for all workers is not acceptable.

The defect is structural:

- unrelated workers contend for one queue head;
- stale or blocked legacy packets can delay fresh high-priority packets;
- architecture, implementation, browser, comms, settlement, and audit work are serialized even when independent;
- one worker lifecycle projection becomes overloaded as system truth;
- dogfooding Domain Weave becomes unsafe because the weave cannot route its own work without joining the same bottleneck it is trying to repair.

## Law

Separate these concepts:

1. intake ledger — immutable receipt of requested work;
2. router — classifies work by domain, authority, risk, carrier, and dependencies;
3. lane queue — per worker-class or per domain execution backlog;
4. worker lease — one bounded claim on one lane item;
5. result intake — strict proof-gated return contract;
6. settlement — accepted/rejected/deferred state decision.

Output is not state until accepted with proof.

## Minimum lane taxonomy

The first implementation should not invent a large scheduler. It should split the current single execution queue into the smallest useful set:

- `architecture_lane` — Vizier, Steward proposal, Domain Weave architecture, context-shape decisions.
- `implementation_lane` — Mason/code patch work with explicit file targets and tests.
- `audit_lane` — Nemesis, Vice, validation-only review, release blockers.
- `comms_lane` — Comms Cartographer, agent workspace/read-model/cockpit communication work.
- `browser_lane` — Browser DOM Cartographer, extension/browser carrier probes, no Send authority unless separately approved.
- `context_lane` — Context Cartographer, IONOLOGIST, manifest/path/capsule/context package work.
- `maintenance_lane` — queue repair, stale legacy cleanup, compaction, duplicate/supersede operations.

The legacy single queue may remain as `global_intake_ledger`, but workers should not select directly from it except through a compatibility router.

## Work packet routing fields

Every new work request should carry:

```yaml
schema_id: ion.work_request.v0_2
request_id: string
created_at: iso8601
objective: string
work_class: architecture | implementation | audit | comms | browser | context | maintenance | settlement
lane_id: string
agent_role: string | null
domain_id: string | null
carrier_id: string | null
priority: integer
risk_level: low | medium | high | red_alert
authority:
  production_authority: false
  live_execution_authority: false
  accepted_state_authority: false
requires_operator_approval: boolean
context_refs: [string]
dependencies:
  after_request_ids: [string]
  after_receipt_paths: [string]
return_contract:
  required_sections:
    - CONTEXT PROOF
    - TEMPLATE ACTION PROOF
    - VALIDATION
    - WORKLOAD DIFF
    - BLOCKERS
    - RESULT
    - RECOMMENDED NEXT PACKET
```

## Router behavior

The router must be deterministic and conservative:

1. preserve the request in the global intake ledger;
2. derive or verify `lane_id` from `work_class`, `agent_role`, and `domain_id`;
3. reject ambiguous requests into `needs_triage`, not the execution head;
4. write a route receipt with chosen lane and reasons;
5. never silently escalate authority;
6. never allow production/live execution authority through ChatGPT-originated queue routing.

## Worker claim behavior

A worker may claim only from its allowed lanes.

Examples:

- `role.vizier` may claim `architecture_lane` and some `settlement_lane` planning packets, not browser automation packets.
- `role.mason` may claim `implementation_lane`, not audit acceptance decisions.
- `role.nemesis` may claim `audit_lane`, not implementation patches.
- `role.comms_cartographer` may claim `comms_lane`, not Domain Weave canon promotion.

A claim writes:

```yaml
schema_id: ion.worker_lease.v0_1
lease_id: string
lane_id: string
request_id: string
worker_role: string
claimed_at: iso8601
expires_at: iso8601
authority_snapshot:
  production_authority: false
  live_execution_authority: false
  accepted_state_authority: false
```

## Compatibility migration

Do not delete the existing queue. Add a compatibility layer:

1. `ACTIVE_CHATGPT_CONNECTOR_CODEX_WORK_QUEUE.json` remains the global intake/read model during migration.
2. New router projection writes lane files under an allowlisted current context path, for example:

```text
ION/05_context/current/chatgpt_connector/work_lanes/architecture_lane.json
ION/05_context/current/chatgpt_connector/work_lanes/implementation_lane.json
ION/05_context/current/chatgpt_connector/work_lanes/audit_lane.json
ION/05_context/current/chatgpt_connector/work_lanes/comms_lane.json
ION/05_context/current/chatgpt_connector/work_lanes/browser_lane.json
ION/05_context/current/chatgpt_connector/work_lanes/context_lane.json
ION/05_context/current/chatgpt_connector/work_lanes/maintenance_lane.json
ION/05_context/current/chatgpt_connector/work_lanes/needs_triage.json
```

3. `process_once` gains optional `lane_id` and `request_path` selectors.
4. Default behavior changes from `oldest global queued request` to `next eligible request for selected lane`.
5. Global status reports lane counts, active leases, blocked head items, and stale legacy packets separately.

## Domain Weave dogfood requirement

Domain Weave must use this routing model on itself:

- Domain Weave architecture proposals route to `architecture_lane`.
- Domain Weave validators/tooling patches route to `implementation_lane`.
- Domain Weave fact-posture/authority review routes to `audit_lane`.
- Domain Weave context package/materialization work routes to `context_lane`.
- Domain Weave comms/cockpit projection routes to `comms_lane`.

This prevents Domain Weave from becoming another monolithic supervisor queue.

## Minimum implementation packet

Recommended next packet:

```text
PCKT-ION-MULTI-LANE-WORKER-QUEUE-MVP-20260530
```

Objective:

Implement the smallest compatibility-safe multi-lane scheduler MVP:

1. add lane classification helper near the existing Codex queue runner/connector owner code;
2. add compact lane projection files under `ION/05_context/current/chatgpt_connector/work_lanes/`;
3. add `lane_id` support to request creation and `process_once` selection;
4. preserve the old global queue as intake ledger;
5. add tests proving architecture and implementation packets do not block each other when both are queued;
6. add tests proving blocked legacy head item does not prevent selecting an explicitly requested lane item;
7. return strict proof-gated task return.

Required validation:

```bash
python3 -m pytest -q ION/tests/test_kernel_ion_chatgpt_browser_mcp_connector_contract.py -k "lane or queue or process_once"
python3 -m pytest -q ION/tests/test_kernel_ion_agent_invocation_broker.py -k "lane or queue or agent"
```

Use narrower real test names if these selectors do not exist.

## Non-goals

- No deletion of old queue files.
- No broad scheduler rewrite.
- No production deploy.
- No accepted-state claim.
- No hidden auto-run daemon.
- No bypass of return-template proof gates.

## Acceptance gates

This protocol may be promoted only after:

1. lane projection exists and is deterministic;
2. request routing writes receipts;
3. process-once can target lane or request path;
4. blocked legacy queue head no longer blocks unrelated lane work;
5. tests pass;
6. Nemesis or equivalent audit finds no authority escalation;
7. operator/steward accepts the result with proof.
