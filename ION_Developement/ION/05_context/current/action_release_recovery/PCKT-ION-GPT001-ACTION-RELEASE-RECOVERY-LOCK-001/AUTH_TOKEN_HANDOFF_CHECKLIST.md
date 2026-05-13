# Auth Token Handoff Checklist

Packet: PCKT-ION-GPT001-ACTION-RELEASE-RECOVERY-LOCK-001
Status: candidate checklist.

## Token boundary

The GPT Builder token is the ION Action Gateway token.
It is not a Supabase token.

Local token source:

```text
/home/sev/.config/ion/action-gateway.env
```

Expected variable:

```text
ION_ACTION_GATEWAY_TOKEN
```

Alternative accepted runtime variable:

```text
ION_ACTION_GATEWAY_TOKEN_SHA256
```

## Forbidden

Do not paste or store these in GPT Builder:

- `SUPABASE_SERVICE_ROLE_KEY`
- `SUPABASE_SECRET_KEY`
- `SUPABASE_DB_PASSWORD`
- database passwords
- JWT secrets
- Cloudflare tokens

## Stop rule

If a protected Action returns `AUTH_INVALID`, `gateway_token_invalid`, or
unexpected `AUTH_MISSING`, stop all protected Action calls immediately.

Do not test another protected route.
Do not attempt writes.
Do not ask the operator to try random token changes.
Return to this checklist and verify the Builder auth value against the local
Action Gateway token source.
