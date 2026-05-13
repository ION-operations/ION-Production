---
atlas_package: system
system_slug: model-context-protocol
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

## Roles

- **Host:** Embeds models/UI; initiates connection (`DOCUMENTED`).  
- **Client (MCP client inside host):** Speaks MCP to servers (`DOCUMENTED`).  
- **Server:** Exposes tools/resources/prompts (`DOCUMENTED`).

## Message model

- **JSON-RPC** request/response + notifications as defined (`DOCUMENTED`, `src-mcp-schema`).

## Layering

- MCP sits **above** OS transports; uses OS IPC/network as configured (`DOCUMENTED`).
