# ION Custom GPT Actions and Tools Posture

## Canonical rule

The Custom GPT currently has two Action schemas, both release-managed:

```text
ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml
ION_GPT/03_ACTIONS/ion.helixion.net_mcp/SCHEMA_TO_PASTE.yaml
```

The first schema is the ION Action Gateway. The second schema is the MCP JSON-RPC wrapper.

Supabase-only, bridge-only, or domain-only OpenAPI files are fragments/templates unless the Action Release tooling explicitly promotes them.

## Normal boot rule

Normal `boot-sequence` does not require live Action calls. If the operator requests an Actions check, use read-only health/status probes first.

## Action stop rule

If a protected Action returns any of these, stop all protected Action calls immediately:

- `AUTH_INVALID`
- `gateway_token_invalid`
- unexpected `AUTH_MISSING`

Do not try other protected endpoints. Do not attempt writes. Report that GPT Builder auth is wrong/stale and request release-domain recovery.

## Canonical operation groups

Core gateway operations include health, policy, context pack, Codex queue, agent status, browser queue, validation/submission, agent relay/control/settlement, and receipts.

Supabase operations include cockpit overview, recent events, latest service health, current carrier mounts, record automation event, record service health, and record carrier mount.

MCP operations include health/status and JSON-RPC `initialize`, `tools/list`, `tools/call`, and `ping`.

## GPT Builder changes

Never instruct the operator to change GPT Builder from an improvised chat answer. GPT Builder changes require a current release bundle with schema hash, operation manifest, install sheet, rollback sheet, and auth handoff checklist.
