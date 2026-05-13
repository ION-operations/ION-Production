# GPT Builder Rollback Sheet

Packet: PCKT-ION-GPT001-ACTION-RELEASE-RECOVERY-LOCK-001
Status: candidate rollback sheet.

## Rollback trigger

Rollback or freeze the Action lane if any of these happen:

- The combined schema is not accepted by GPT Builder.
- Old operationIds are missing after install.
- Supabase fragment appears as the only schema.
- Protected Action calls return `AUTH_INVALID` after token refresh.
- The GPT attempts write actions before read-only checks pass.

## Rollback target

Preferred rollback is the last known full Action Gateway schema, not the
Supabase-only fragment.

Current recovered canonical source:

```text
ION/09_integrations/custom_gpt_action_gateway/openapi.yaml
```

Recovered package copy:

```text
ION/05_context/current/action_release_recovery/PCKT-ION-GPT001-ACTION-RELEASE-RECOVERY-LOCK-001/COMBINED_OPENAPI_SCHEMA.yaml
```

## Freeze rule

If rollback cannot be completed confidently, freeze Actions instead of trying a
new schema from chat.

Operator-facing release work must resume only from a verified release package.
