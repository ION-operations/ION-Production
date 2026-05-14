# ION Custom GPT Actions and Tools Posture

## Canonical rule

The Custom GPT must use one canonical full Action Gateway schema, not fragments.

Canonical schema path:

```text
ION_GPT/custom_gpt_action_gateway/openapi.yaml
```

Supabase-only, bridge-only, or domain-only OpenAPI files are fragments/templates unless the Action Release tooling builds them into the canonical schema.

## Action stop rule

If a protected Action returns any of these, stop all protected Action calls immediately:

- `AUTH_INVALID`
- `gateway_token_invalid`
- unexpected `AUTH_MISSING`

Do not try other protected endpoints. Do not attempt writes. Report that GPT Builder auth is wrong/stale and request release-domain recovery.

## Canonical operation groups

Core gateway operations include health, policy, context pack, Codex queue, agent status, browser queue, validation/submission, agent relay/control/settlement, and receipts.

Supabase operations include cockpit overview, recent events, latest service health, current carrier mounts, record automation event, record service health, and record carrier mount.

## GPT Builder changes

Never instruct the operator to change GPT Builder from an improvised chat answer. GPT Builder changes require a Custom GPT Action Release bundle with schema hash, operation manifest, install sheet, rollback sheet, and auth handoff checklist.
