# Passive Hook Implementation Handoff Packet v0.3

Status: Historical handoff packet (constrained slice now executed by Lane A)  
Date: 2026-03-02  
Superseded for live implementation state by: `docs/LANE_A_CHECKPOINT_D_PASSIVE_HOOK_EXECUTION_REPORT_V1.md`

---

## Purpose

Provide a low-ambiguity handoff packet for implementing the first passive observational hook.  
Checkpoint D Option B has since been executed for one constrained slice; this document remains as design/provenance reference.

This packet does not authorize implementation on its own.

---

## 1) Authorized Scope Envelope (If Approved)

Implement exactly one passive slice:

- hook location: post-resolution, pre-envelope orchestration boundary
- flag: `AIMOS_SHADOW_BCI_PASSIVE_EMIT`
- mode: observational only
- failure posture: fail-open

No additional behavior changes are in-scope.

Pre-validation anchors already available (isolated):

- `context_capsule_wire_and_mapper_v1/shadow_sync/shadow_bci_v1_strict_schema.json`
- `context_capsule_wire_and_mapper_v1/shadow_sync/passive_hook_simulation_v0_3.py`
- `context_capsule_wire_and_mapper_v1/shadow_sync/tests/test_passive_hook_simulation_v0_3.py`
- `context_capsule_wire_and_mapper_v1/context_mapper_lab/src/shadow_hook.rs`
- `context_capsule_wire_and_mapper_v1/context_mapper_lab/src/main.rs`

---

## 2) Candidate File-Touch Map (Minimal)

Expected minimal touches (future implementation phase only):

1. One orchestration boundary module where extracted+resolved context is already assembled
2. One new passive hook module (adapter + guarded emission call)
3. Optional small env-flag utility helper (if needed for clean parsing)

Reference mapping already validated in lab:

- orchestration boundary call: post-resolution in `context_mapper_lab/src/main.rs`
- passive module: `context_mapper_lab/src/shadow_hook.rs`
- output behavior: adapter snapshot + emitter invocation guarded by env flag

Do not touch:

- parser internals
- resolver internals
- envelope internals
- daemon bridge internals
- kernel planes / context service seams

---

## 3) Runtime Behavior Contract

Disabled path:

- identical behavior to pre-hook baseline
- no payload mutation
- no user-visible differences

Enabled path:

- attempt adapter transform + shadow emission
- never block live response
- swallow/log all shadow failures

---

## 4) Required Validation Plan (Implementation Phase)

Mandatory proofs:

1. Flag default-off proof
2. Disabled-path equivalence proof
3. Enabled-path success proof (records emitted)
4. Enabled-path failure proof (forced failure still returns live response unchanged)
5. Latency snapshot (hook overhead bounded and documented)

Suggested command/report framing:

- baseline run (flag off)
- run with flag on and healthy shadow path
- run with flag on and injected shadow failure
- compare response payloads and status codes vs baseline

Reference execution results (lab, 2026-03-01):

- `cargo test` in `context_mapper_lab`: pass (4/4 hook tests)
- `cargo run --quiet` (flag unset): passive emission disabled
- `AIMOS_SHADOW_BCI_PASSIVE_EMIT=true cargo run --quiet`: passive emission success
- `AIMOS_SHADOW_BCI_PASSIVE_EMIT=true` + invalid python bin: fail-open confirmed, live output preserved

---

## 5) Logging Contract (Minimal)

Event names:

- `shadow_emit_attempt`
- `shadow_emit_success`
- `shadow_emit_failure`

Required fields:

- `source_path`
- `record_count` (success case)
- `elapsed_ms`
- `error_class` / `error_message` (failure case)

Keep logs light; no telemetry platform expansion in first slice.

---

## 6) Rollback Contract

Immediate rollback:

- set `AIMOS_SHADOW_BCI_PASSIVE_EMIT=false` (or unset)

Code rollback:

- remove/inert passive hook module and orchestration call site changes only

No data migration concerns expected for first passive observational slice.

---

## 7) Risk Controls

- Off-by-default flag
- Single insertion point
- Single module ownership
- No core seam rewrites
- Fail-open policy
- Explicit checkpoint adjudication before execution

---

## 8) Merge Classification

- **Safe now**
  - this handoff packet
  - lab reference implementation under `context_mapper_lab`
- **Safe later**
  - future incremental refinements that remain within constrained-slice doctrine
- **Not safe yet**
  - any gating/enforcement behavior or routing overrides

---

## 9) Drift Check

- No live seam edits in this packet.
- Mapper sovereignty preserved.
- Daemon sovereignty preserved.
- Kernel role preserved.
- Contextual Sync remains additive superstrate.
