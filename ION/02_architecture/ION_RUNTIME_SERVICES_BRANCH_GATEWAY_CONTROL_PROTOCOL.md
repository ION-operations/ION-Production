---
type: architecture_protocol
authority: A3_CANDIDATE
created: 2026-05-15T00:00:00-04:00
status: CANDIDATE
protocol_id: ion_runtime_services_branch_gateway_control
branch_id: runtime_services
family: local_runtime_service_control
connections:
  - ION/02_architecture/ION_ACTION_MCP_BRANCH_LEADER_GATEWAY_PROTOCOL.md
  - ION/03_registry/ion_action_mcp_branch_leader_registry.yaml
  - ION/04_packages/kernel/ion_runtime_service_control.py
---

# ION Runtime Services Branch Gateway Control Protocol

## Purpose

`runtime_services` exposes local ION development service visibility and bounded
restart/retest control through the Action/MCP Branch Gateway only.

It must not create flat GPT Actions such as `restartActionGateway`, accept raw
systemd unit names, run arbitrary shell, deploy production, read credentials, or
claim accepted state.

## Allowlist

The branch accepts these stable service IDs only:

```text
action_gateway -> ion-action-gateway.service
mcp_preview -> ion-mcp-preview.service
cosmos_preview -> ion-cosmos-preview.service
cockpit_app -> ion-cockpit-app.service
chatops -> ion-chatops.service
```

Callers pass `service_id`; implementation resolves the unit from code. Raw unit
names are not accepted as input.

## Routes

```yaml
service_status:
  mutates_state: false
  meaning: read systemd and optional endpoint status for one or all allowlisted services
service_reload_plan:
  mutates_state: false
  meaning: explain what would restart, what proof is required, and where receipts land
restart_service:
  mutates_state: true
  requires:
    confirmation: ION_BOUNDED_WRITE_CONFIRMED
    idempotency_key: required
  meaning: restart one allowlisted service only after unit ownership proof
retest_service:
  mutates_state: false
  meaning: run a read-only health smoke against the allowlisted endpoint
reload_and_retest:
  mutates_state: true
  requires:
    confirmation: ION_BOUNDED_WRITE_CONFIRMED
    idempotency_key: required
  meaning: restart, retest, and record a combined receipt
```

## Proof Rules

Before a restart, the helper records a pre receipt and verifies that
`systemctl --user show` reports an `Id` equal to the allowlisted unit. It also
captures `MainPID` and a bounded `/proc/<pid>/cmdline` sample when available.

After a restart attempt, the helper records a post receipt with the restart
result and fresh unit status. `reload_and_retest` adds read-only endpoint smoke
evidence to a combined receipt.

Receipts are candidate evidence under:

```text
ION/05_context/current/runtime_services/receipts/
```

## Self-Restart Rule

When the target is `action_gateway`, the helper explicitly defers restart
instead of attempting to restart the Action Gateway process that is serving the
request. If the Action Gateway is down or stale, the recommended lawful recovery
path is MCP `8765` / `codex_queue` or a local operator terminal.

## Authority Boundaries

- No arbitrary systemd unit names.
- No arbitrary shell.
- No production deploy.
- No credential access.
- No Git push.
- No GPT Builder edit.
- No new flat GPT Actions.
- No accepted-state claim.
- Mutation routes require `ION_BOUNDED_WRITE_CONFIRMED`.
- Mutation routes require `idempotency_key`.
