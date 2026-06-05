# Codex Carrier Event Bus Protocol

Status: active candidate protocol
Authority: runtime telemetry and cockpit projection only
Accepted-state authority: false
Production authority: false
Live execution authority: false

## Purpose

The Codex carrier event bus records public-safe runtime telemetry so the cockpit can show what happened across Codex sessions, branch capsules, patches, tests, receipts, settlement, MCP, Action Gateway, dAimon, and Git workflows.

Events are not receipts. They are operational evidence.

```text
event -> projection/evidence
receipt -> accepted inheritable state evidence after gate/decision
```

## Ledger

Events are written under:

```text
ION/05_context/current/codex_carrier/events/<event_id>.json
```

The summary ledger is:

```text
ION/05_context/current/codex_carrier/CODEX_CARRIER_EVENT_LEDGER.json
```

## Event envelope

Each event uses:

```json
{
  "schema_id": "ion.codex_carrier_runtime_event.v1",
  "event_id": "evt_...",
  "created_at": "...",
  "event_type": "codex.session.started",
  "actor": {},
  "packet_id": "PCKT-...",
  "branch_id": "branch_...",
  "session_id": "codex_session_...",
  "refs": [],
  "evidence": [],
  "detail": "...",
  "authority": {
    "accepted_state_authority": false,
    "production_authority": false,
    "live_execution_authority": false,
    "secrets_authority": false
  },
  "visibility": {
    "cockpit": true,
    "public_safe": true,
    "redacted": true,
    "raw_context_exported": false
  }
}
```

## Event classes

Recommended classes:

```text
ion.mount.requested
ion.mount.completed
ion.context.compiled
ion.context.drift_detected
ion.packet.opened
ion.packet.updated
ion.packet.closed
codex.session.started
codex.session.resumed
codex.session.registered
codex.session.rolling_context_synced
codex.subagent.spawned
codex.subagent.returned
codex.raw_context_manifest.written
codex.memory.summary_proposed
tool.call.started
tool.call.completed
tool.call.blocked
patch.previewed
patch.applied
patch.reverted
test.started
test.completed
git.status.captured
git.stage_manifest.proposed
git.commit.proposed
git.commit.created
git.push.requested
git.push.approved
git.push.completed
receipt.proposed
receipt.written
settlement.requested
settlement.accepted
settlement.deferred
settlement.conflict_recorded
settlement.abandoned
service.port.probed
service.routing.changed
mcp.tool_surface.changed
action_gateway.health_changed
daimon.bridge.health_changed
ui.visual_proof.captured
ui.visual_proof.failed
ui.canon_violation_detected
```

## Boundary

The event bus must not:

```text
start workers
mutate Git
accept state
write secrets
export raw Codex context
replace receipts
replace settlement
```
