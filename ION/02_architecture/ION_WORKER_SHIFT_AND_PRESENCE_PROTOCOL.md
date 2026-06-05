# ION Worker Shift and Presence Protocol v0.1

Status: candidate local protocol
Packet: PCKT-ION-WORKER-SHIFT-PRESENCE-V0_1
Production authority: false
Live execution authority: false
Accepted state claim: false

## Core Law

```text
WORKERS MUST ENTER AND EXIT THE FIELD WITH RECEIPTS
```

A worker is not active merely because a chat, terminal, tab, process, or queued
request exists. For this protocol, a worker becomes active when it signs on or
claims work, and it exits through sign-off, return, release, failure,
suspension, or stale classification.

## Purpose

Worker Shift and Presence is a lightweight durable coordination layer for
Browser GPT carriers, Codex CLI terminal copartners, queued Codex workers,
capsule agents, future branch agents, and eventual swarms.

It answers the live coordination questions:

- who is active;
- what packet or objective each worker is holding;
- what paths, branches, or work scopes are under lease;
- which conflicts are advisory and which are hard blockers;
- who is stale;
- what the next worker should know.

## Non-Replacement Rules

This protocol does not replace carrier mount receipts. Shift receipts may cite a
mount receipt, but the mount receipt remains the authority witness for carrier
identity, context, source posture, write scope, and authority.

This protocol does not replace executor lifecycle. Shift statuses map to
executor lifecycle states:

| Shift status | Executor lifecycle state |
| --- | --- |
| `SIGNED_ON`, `ACTIVE`, `HEARTBEAT` | `ACTIVE` |
| `STALE`, `EXPIRED`, `SUSPENDED` | `SUSPENDED` |
| `RETURNED` | `RETURNED` |
| `RELEASED`, `FAILED` | `RELEASED` |

This protocol does not replace carrier-to-carrier messaging. It provides
presence and lease evidence; carrier messages remain the communication layer.

This protocol does not replace scheduler or allocator law. It provides live
presence and lease input that schedulers and allocators may consult.

Future Action/MCP exposure should route through the Branch Leader Gateway branch
`worker_shift` rather than expanding a flat GPT Action surface.

## Runtime Files

The active candidate board lives at:

```text
ION/05_context/current/worker_shift/ACTIVE_WORKER_SHIFT_BOARD.json
```

Runtime receipt folders:

```text
ION/05_context/current/worker_shift/signons/
ION/05_context/current/worker_shift/signoffs/
ION/05_context/current/worker_shift/heartbeats/
ION/05_context/current/worker_shift/leases/
ION/05_context/current/worker_shift/messages/
ION/05_context/current/worker_shift/stale/
```

The helper implementation is:

```text
ION/04_packages/kernel/ion_worker_shift_presence.py
```

## Objects

### WorkerIdentity

Runtime identity for one active worker instance. It is not equivalent to a
human, model, role, or process.

Required fields:

```yaml
worker_id: <carrier_type>:<workspace>:<yyyymmdd>:<ordinal>
display_callsign: <carrier-family>-<ordinal> / <role> / <domain>
carrier_type:
carrier_instance_id:
model:
role_hint:
domain_hint:
active_root:
authority:
  accepted_state_authority: false
  production_authority: false
  live_execution_authority: false
  secrets_authority: false
```

### WorkerShift

Current active working session:

```yaml
shift_id:
worker_id:
status:
executor_lifecycle_state:
started_at:
last_heartbeat_at:
packet_id:
current_objective:
current_branch:
return_target:
likely_touched_paths: []
signon_receipt_path:
```

### WorkLease

Path, branch, or objective claim used to avoid worker collisions:

```yaml
lease_id:
worker_id:
mode: read | write | exclusive_write
paths: []
objective:
packet_id:
branch_id:
status:
claimed_at:
```

Conflict law:

- `exclusive_write` conflicts with any active lease touching the same path or a
  parent/child path;
- `write` conflicts with an active overlapping `exclusive_write`;
- `read` may coexist with `read`;
- overlapping non-exclusive writes are advisory coordination warnings in this
  candidate helper, not hard blockers.

### WorkerShiftBoard

Compact roster containing active workers, active leases, stale workers, recent
signoffs, and recent receipt refs.

## Flows

### Sign-On

1. Resolve the active root.
2. Read the current shift board.
3. Generate or receive a worker identity.
4. Record packet, objective, branch, return target, and likely touched paths.
5. Write a sign-on receipt under `signons/`.
6. Add or update the active shift board.

### Heartbeat

Heartbeat receipts are quiet and small. They refresh `last_heartbeat_at`.

Suggested policy:

```text
optional for short tasks
every 15-30 minutes for long tasks
stale after 45 minutes without heartbeat
expired after 2 hours unless long_running
```

### Lease Claim and Release

`read_interest`, `write_intent`, `review_only`, and `blocked` leases are
coordination signals. `exclusive_write` is the only v0 lease type that can hard
block another worker on path collision.

Claims and releases write receipts under `leases/` and update
`ACTIVE_WORKER_SHIFT_BOARD.json`.

### Sign-Off

Sign-off records work done, touched paths, validation, receipt refs, next baton,
and released leases. It removes the shift from the active board and appends a
recent signoff entry.

### Stale Classification

Stale classification reads the board, compares `last_heartbeat_at` to policy,
and may write a stale classification receipt. Stale workers remain evidence;
they are not silently deleted.

## Candidate Helper API

```text
sign_on(worker_id, carrier, mission, allowed_paths)
heartbeat(worker_id)
claim_work_lease(worker_id, lease_id, paths, mode)
release_work_lease(worker_id, lease_id)
sign_off(worker_id, summary)
generate_worker_id
load_shift_board
write_shift_board
write_signon_receipt
write_signoff_receipt
write_heartbeat
claim_work_lease
release_work_lease
detect_lease_conflicts
classify_stale_workers
summarize_shift_board
```

## Authority Boundary

This protocol is candidate/local only. It grants no production authority, live
execution authority, accepted-state authority, secrets authority, git push
authority, or deployment authority.
