# GPT Builder Install Sheet

Packet: PCKT-ION-GPT001-ACTION-RELEASE-RECOVERY-LOCK-001
Status: candidate release sheet. Do not use until operator approves release.

## Install target

Use only this combined schema artifact:

```text
ION/05_context/current/action_release_recovery/PCKT-ION-GPT001-ACTION-RELEASE-RECOVERY-LOCK-001/COMBINED_OPENAPI_SCHEMA.yaml
```

Canonical source:

```text
ION/09_integrations/custom_gpt_action_gateway/openapi.yaml
```

Do not install or recreate the former Supabase-only fragment:

```text
ION/07_templates/actions/ION_SUPABASE_ACTIONS_OPENAPI_V0_1.yaml
```

## Pre-install verification

Required facts before any Builder edit:

```text
operation_count: 25
old_operations_preserved: 18
new_supabase_operations: 7
duplicate_operation_ids: none
server: https://ion-actions.helixion.net
schema_sha256: 9ee5e43885e85607ae51a0efccd72d780ba57635074bc6b01a2f81dff8ae72ba
```

## Operation manifest

See:

```text
ION/05_context/current/action_release_recovery/PCKT-ION-GPT001-ACTION-RELEASE-RECOVERY-LOCK-001/OPERATION_ID_MANIFEST.json
```

## Auth

GPT Builder must authenticate to the ION Action Gateway only.

Expected header shape:

```text
Authorization: Bearer <ION_ACTION_GATEWAY_TOKEN>
```

Token source on local machine:

```text
/home/sev/.config/ion/action-gateway.env
```

Never place Supabase keys in GPT Builder.

## First fresh-session checks

After install and save, start a fresh GPT session.

Run only read checks first:

```text
ionGatewayHealth
ionGatewayPolicy
ionSupabaseCockpitOverview
```

If any protected call returns `AUTH_INVALID`, `gateway_token_invalid`, or
unexpected `AUTH_MISSING`, stop immediately.
