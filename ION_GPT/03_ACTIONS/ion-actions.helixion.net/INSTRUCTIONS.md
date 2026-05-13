# ION Action for GPT Builder

There is one Action to install.

## 1. Schema

In GPT Builder, paste/import this file into the Schema box:

```text
SCHEMA_TO_PASTE.yaml
```

## 2. Authentication

Use the ION Action Gateway bearer token. See `WHERE_TO_FIND_AUTH_TOKEN.md`.

Do not use Supabase keys.

## 3. Privacy policy

Use the ION/Helixion privacy policy URL once verified.

## 4. After saving

Start a fresh GPT session.

If you see `AUTH_INVALID`, `gateway_token_invalid`, or unexpected `AUTH_MISSING`, stop. The Action auth is wrong or stale.


## Known public-access blocker

If GPT Builder still cannot call this Action after the schema and bearer token are correct, the likely blocker is Cloudflare. Current diagnosis showed Cloudflare can allow browser-like requests while blocking OpenAI/GPT-style requests with `403` / `1010`.

That is fixed in Cloudflare security/WAF/bot settings, not by changing the schema again.
