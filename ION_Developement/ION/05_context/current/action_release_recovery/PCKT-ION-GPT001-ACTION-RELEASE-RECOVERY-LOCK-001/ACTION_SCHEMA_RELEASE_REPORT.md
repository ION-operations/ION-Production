# Action Schema Release Report

Packet: PCKT-ION-GPT001-ACTION-RELEASE-RECOVERY-LOCK-001
Created UTC: 2026-05-13T11:52:16Z
Status: candidate release recovery lock.

## Release posture

The Action lane is frozen until this package is reviewed.

Codex does not have authority to verbally guide the operator through GPT Builder
changes. This package exists so a separate verified release sheet can be used
instead of improvised chat instructions.

## What broke

The carrier instructed the operator to install a Supabase-only OpenAPI fragment
as if it were the full GPT Action Gateway schema.

Former incorrect install target, now removed from the live templates path:

```text
ION/07_templates/actions/ION_SUPABASE_ACTIONS_OPENAPI_V0_1.yaml
```

Correct canonical schema:

```text
ION/09_integrations/custom_gpt_action_gateway/openapi.yaml
```

## What is canonical now

Canonical schema SHA256:

```text
9ee5e43885e85607ae51a0efccd72d780ba57635074bc6b01a2f81dff8ae72ba
```

Copied release schema:

```text
ION/05_context/current/action_release_recovery/PCKT-ION-GPT001-ACTION-RELEASE-RECOVERY-LOCK-001/COMBINED_OPENAPI_SCHEMA.yaml
```

Operation count:

```text
25
```

Old operations preserved:

```text
18
```

New Supabase operations added:

```text
7
```

Duplicate operationIds:

```text
none
```

Secret-text findings in schema:

```text
none
```

## Old operations preserved

- `ionGatewayHealth`
- `ionGatewayPolicy`
- `ionGatewayContextPack`
- `ionGatewayCodexQueue`
- `ionGatewayAgentStatus`
- `ionGatewayDaimonVisibility`
- `ionGatewayReceiptsRecent`
- `ionBrowserQueueStatus`
- `ionBrowserQueueReceiptsRecent`
- `ionBrowserQueueEnqueue`
- `ionGatewayValidateAction`
- `ionGatewaySubmitAction`
- `ionGatewayAgentInvoke`
- `ionGatewayAgentRelayPending`
- `ionGatewayAgentRelayRespond`
- `ionGatewayAgentControl`
- `ionGatewayAgentReceiptsRecent`
- `ionGatewayAgentSettle`

## New operations added

- `ionSupabaseCockpitOverview`
- `ionSupabaseRecentEvents`
- `ionSupabaseLatestServiceHealth`
- `ionSupabaseCurrentCarrierMounts`
- `ionSupabaseRecordAutomationEvent`
- `ionSupabaseRecordServiceHealth`
- `ionSupabaseRecordCarrierMount`

## Stop rule

If a protected GPT Action returns `AUTH_INVALID`, `gateway_token_invalid`, or
unexpected `AUTH_MISSING`, stop all protected Action calls immediately.

Do not try other protected routes.
Do not attempt write actions.
Do not smoke test.
Report that GPT Builder Action auth is wrong or stale.

## Failure report

See:

```text
ION/05_context/current/failure_reports/2026-05-13_GPT001_ACTION_SCHEMA_CONTROL_SURFACE_FAILURE.md
```

## Non-claims

This report does not claim production deployment, accepted ION state, or repaired
GPT Builder configuration.
