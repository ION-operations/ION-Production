# ION Custom GPT Actions and Tools Posture

## Canonical Rule

The Custom GPT must use canonical Builder Action schemas from:

```text
ION_GPT/03_ACTIONS/ion-actions.helixion.net/SCHEMA_TO_PASTE.yaml
ION_GPT/03_ACTIONS/ion.helixion.net_mcp/SCHEMA_TO_PASTE.yaml
```

Worker/source OpenAPI files are evidence or generator inputs unless the Action
Release tooling builds them into the canonical schema bundle.

## Action Surface Audit

Boot and Action/Git/UI work must emit a dedicated `ion_action_surface_audit`
block when Action/MCP/tool surfaces are visible. The audit records schema
targets, operation/tool counts, duplicate operation IDs, auth boundary, GET/POST
path counts, supported MVP intents, hard gates, refusal classes, read-only and
mutation-capable tool counts, write-confirmation token name, project
preview/Git posture, browser queue posture, Supabase/cockpit posture, and
explicit non-claims.

## Action Stop Rule

If a protected Action returns any of these, stop all protected Action calls
immediately:

- `AUTH_INVALID`
- `gateway_token_invalid`
- unexpected `AUTH_MISSING`

Do not try other protected endpoints. Do not attempt writes. Report that GPT
Builder auth is wrong/stale and request release-domain recovery.

## GPT Builder Changes

Never instruct the operator to change GPT Builder from an improvised chat
answer. GPT Builder changes require a validated Custom GPT Action Release bundle
with schema hash, operation manifest, install sheet, rollback sheet, and auth
handoff checklist.
