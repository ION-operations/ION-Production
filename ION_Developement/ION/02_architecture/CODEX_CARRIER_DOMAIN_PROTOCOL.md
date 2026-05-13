# Codex Carrier Domain Protocol

Status: active candidate protocol  
Authority: Codex carrier-domain control plane only  
Production authority: false  
Live execution authority: false

## Purpose

This protocol makes Codex CLI/App a first-class ION carrier domain without letting Codex memory, sessions, or app state become accepted ION state by themselves.

Codex is valuable because it can keep local sessions, run bounded filesystem work, use hooks, load project instructions, and expose MCP/tooling surfaces. ION must bind those capabilities to branch capsules, packets, proof gates, receipts, and settlement.

## Core law

```text
Codex memory/session = working continuity.
Raw Codex context = bounded diagnostic continuity.
ION branch capsule = durable governed continuity.
ION receipt/settlement = accepted inheritance.
```

Codex may remember, resume, build, test, report, and preserve local-private diagnostic context. It may not accept state directly.

## Domain objects

### Codex Carrier Domain Registry

Path:

```text
ION/05_context/current/codex_carrier/CODEX_CARRIER_DOMAIN_REGISTRY.json
```

This registry projects the Codex carrier-domain objects, required surfaces, agent profiles, memory policy, session schema, MCP read-only tools, cockpit panels, and non-authority boundaries.

### Codex Session Registry

Path:

```text
ION/05_context/current/codex_carrier/CODEX_SESSION_REGISTRY.json
ION/05_context/current/codex_carrier/sessions/<session_id>.json
```

Each real local Codex session may be registered with:

```json
{
  "schema_id": "ion.codex_carrier_session.v1",
  "session_id": "codex_session_...",
  "agent_tag": "codex_local_ion_mason",
  "branch_id": "branch_...",
  "ion_branch_capsule": "ION/05_context/current/agent_context_branches/.../",
  "current_packet": "PCKT-...",
  "write_scope": [],
  "settlement_required": true,
  "accepted_state_authority": false
}
```

A session record is carrier state, not settled ION state.

### Codex Branch Capsule

Each significant Codex lane must bind to a branch capsule under:

```text
ION/05_context/current/agent_context_branches/
```

The branch capsule is the durable governed continuity surface. It may hold local task context, assumptions, candidate receipts, proof paths, and settlement requests. It must not claim accepted shared state.

### Codex Memory Policy

Path:

```text
ION/05_context/current/codex_carrier/CODEX_MEMORY_POLICY.md
```

Rules:

```text
Memory may orient.
Branch capsule governs.
Receipts inherit.
Settlement accepts.
```

Raw `~/.codex` memories, transcripts, session stores, credentials, or private operator data must not be exported into repo state without explicit review and redaction.

### Raw Codex Context Sync Lane

Path:

```text
ION/02_architecture/CODEX_RAW_CONTEXT_SYNC_LANE_PROTOCOL.md
ION/05_context/current/codex_carrier/CODEX_RAW_CONTEXT_SYNC_LANE_POLICY.md
ION/05_context/current/codex_carrier/raw_context_manifests/
```

The raw context lane preserves diagnostic continuity as local-private snapshots plus public-safe manifests. Raw snapshot content stays under `.ion_private/codex_raw_context/` by default and must not be committed or mirrored externally by default.

Promotion path:

```text
native Codex session / memory
-> local-private raw snapshot
-> public-safe manifest
-> redacted diagnostic excerpt or summary
-> proof gate
-> receipt / settlement
-> inheritable ION state
```

### Runtime Event Ledger

Path:

```text
ION/02_architecture/CODEX_CARRIER_EVENT_BUS_PROTOCOL.md
ION/05_context/current/codex_carrier/CODEX_CARRIER_EVENT_LEDGER.json
ION/05_context/current/codex_carrier/events/
```

Events are public-safe telemetry for cockpit/proof/drift displays. Events are not receipts and do not settle state.

### Codex Carrier OS Source Map

Path:

```text
ION/02_architecture/CODEX_CARRIER_OS_RUNTIME_PROTOCOL.md
ION/05_context/current/codex_carrier/CODEX_CARRIER_OS_SOURCE_MAP.json
```

The OS source map composes domain registry, sessions, agents, raw context lane, event bus, cockpit projection, slash commands, and context mirror policy into one inspectable runtime substrate. It is projection state, not accepted state.

### Codex Cockpit Snapshot

Path:

```text
ION/05_context/current/codex_carrier/CODEX_CARRIER_COCKPIT_SNAPSHOT.json
```

The cockpit snapshot exposes agent/session graph, git state, drift signals, service port map, context truth boundaries, and proof visibility requirements.

## MCP exposure

The local MCP bridge may expose read-only Codex carrier domain tools:

```text
ion.codex.carrier.status
ion.codex.carrier.cockpit
ion.codex.carrier.events
ion.codex.carrier.os
ion.codex.raw_context.status
```

These tools may project status, cockpit state, event ledger state, OS source-map state, and raw-context lane readiness. They must not register sessions, mutate files, start workers, call providers, read raw Codex context, read secrets, or accept state.

## Hooks and commands

Codex hooks should eventually enforce:

```text
SessionStart -> mount proof + domain registry + branch identity
pre-material-work -> write-scope / protected-path check
post-material-work -> touched-path and proof candidate capture
before-exit -> rolling context sync + handoff candidate
```

Slash commands should be deterministic wrappers where possible:

```text
/ion-mount
/ion-identity
/ion-packet
/ion-branch
/ion-sync
/ion-proof
/ion-git-plan
/ion-receipt
/ion-settlement
/ion-handoff
```

## Drift classes

The Codex carrier cockpit should expose at least:

```text
missing_domain_surface
missing_session_registry
stale_session_registry
git_worktree_dirty
branch_capsule_missing
shared_context_write_attempted
memory_claim_without_receipt
proof_claim_without_command
service_port_mismatch
mcp_tool_boundary_violation
raw_context_manifest_missing
raw_context_content_committed
event_without_receipt_claim
context_mirror_stale_or_noisy
```

## Settlement boundary

Codex outputs settle through normal ION gates:

```text
packet
-> compiled context
-> Codex carrier execution
-> proof-bearing return
-> gate
-> Steward/human decision
-> receipt
-> next state
```

The following are always proposals until settlement:

```text
Codex memory claims
Codex session summaries
Codex generated diffs
Codex task returns
Codex cockpit observations
Codex raw-context manifests
Codex runtime events
Codex Carrier OS source-map projections
MCP read-only projections
```

## Forbidden claims

Codex carrier domain work must not claim:

```text
ION identity
STEWARD authority
RELAY authority
PERSONA authority
accepted-state authority
production authority
live execution authority
secrets authority
direct shared Capsule/Mini/HOT_CONTEXT mutation
```

## Local PC Codex OS audit

The first local-PC bringup step is a read-only Codex OS audit. It inventories Codex CLI/App capability, project `.codex` surfaces, and user-local `~/.codex` shape without exporting raw memories, transcripts, sessions, or config values.

```bash
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_local_os_audit \
  --ion-root . \
  --write \
  --json
```

Optional local service probe:

```bash
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_local_os_audit \
  --ion-root . \
  --probe-ports \
  --write \
  --json
```

The audit output is candidate evidence at:

```text
ION/05_context/current/codex_carrier/CODEX_LOCAL_OS_AUDIT.json
```

It does not start Codex workers, app servers, remote-control services, queue runners, or MCP mutation lanes.

## Initialization command

From the shell root:

```bash
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_carrier_domain init \
  --ion-root . \
  --confirmation ION_CODEX_CARRIER_DOMAIN_WRITE_CONFIRMED \
  --json
```

Read-only status:

```bash
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_carrier_domain status --ion-root . --json
PYTHONPATH=ION/04_packages python3 -m kernel.ion_codex_carrier_domain cockpit --ion-root . --json
```

## Non-claims

This protocol does not:

```text
read hidden Codex memories
commit or mirror raw Codex context by default
prove a live local Codex app/server exists
start a Codex worker
start queue runners
mutate production systems
push Git changes
accept candidate work as state
settle branch outputs
```
