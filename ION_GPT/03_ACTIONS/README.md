# 03 Actions

GPT Builder has one Schema box per Action. Install these as two separate Actions.

## Action 1: ION Action Gateway

Folder:

```text
ion-actions.helixion.net/
```

Paste/import:

```text
SCHEMA_TO_PASTE.yaml
```

Auth:

```text
Bearer token from WHERE_TO_FIND_AUTH_TOKEN.md
```

## Action 2: ION MCP Preview

Folder:

```text
ion.helixion.net_mcp/
```

Paste/import:

```text
SCHEMA_TO_PASTE.yaml
```

Auth:

Use the MCP Action auth posture currently required by GPT Builder. If auth is missing or invalid, stop and repair auth instead of trying writes.

## Boot/check rule

Normal `boot-sequence` does not require live Actions. If the operator asks for an Actions check, use read-only health/status probes first and stop immediately on `AUTH_INVALID`, `gateway_token_invalid`, unexpected `AUTH_MISSING`, or Cloudflare host/block errors.

Do not use historical schemas unless a current release bundle explicitly says so.
