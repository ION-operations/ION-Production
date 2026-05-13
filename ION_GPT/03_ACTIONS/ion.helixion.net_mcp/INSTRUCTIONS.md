# ION MCP Action for GPT Builder

This is the second Custom GPT Action schema.

## What it is

It wraps the ION MCP preview endpoint as an OpenAPI Action so Custom GPT can call MCP JSON-RPC methods through GPT Builder Actions.

## Schema

Paste/import this file into GPT Builder as a separate Action:

```text
SCHEMA_TO_PASTE.yaml
```

## Server

```text
https://ion.helixion.net
```

The MCP endpoint path is:

```text
/mcp
```

## Operations

- `ionMcpHealth`
- `ionMcpAppStatus`
- `ionMcpJsonRpc`

## Authentication

Use whatever auth posture this MCP Action currently requires in GPT Builder. If the Builder/action reports auth missing or invalid, stop and repair the MCP Action setup rather than trying writes.

## Use only when explicit

Do not use this Action for normal file/package boot. Use it only when the user asks for live MCP/local hub status, tool listing, runtime reads, or connector-backed action.


## Known public-access blocker

If GPT Builder cannot call this MCP Action while local `127.0.0.1:8765` works, check Cloudflare. A `403` / `1010` response means Cloudflare blocked the client before it reached ION.
