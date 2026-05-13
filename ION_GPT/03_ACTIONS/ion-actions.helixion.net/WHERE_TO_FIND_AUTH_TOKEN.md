# Where to Find the Action Auth Token

The GPT Builder Action uses the ION Action Gateway bearer token.

It is not an OpenAI key.
It is not a Supabase key.

## Current local token source

Open this local file on the computer:

```text
/home/sev/.config/ion/action-gateway.env
```

Find:

```text
ION_ACTION_GATEWAY_TOKEN=...
```

Use the value after `=` as the GPT Builder Action bearer token.

## Backup matching local copy

A matching local copy may also exist at:

```text
/home/sev/ION - Production/ION_Developement/.env.supabase.local
```

Do not upload either file. Do not paste the token into chat or repo docs.

## GPT Builder auth field

If GPT Builder asks for Bearer/API key auth, paste only the token value.

If GPT Builder asks for a custom header, use:

```text
Authorization: Bearer <token>
```

## If auth fails

If Actions return `AUTH_INVALID`, `gateway_token_invalid`, or unexpected `AUTH_MISSING`, stop. The token in GPT Builder does not match the running Action Gateway.
