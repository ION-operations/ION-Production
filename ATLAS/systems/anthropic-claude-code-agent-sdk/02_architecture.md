---
atlas_package: system
system_slug: anthropic-claude-code-agent-sdk
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

## Public-surface topology

- **Clients** (SDK, CLI, editor plugins) call **HTTPS APIs** (`DOCUMENTED`).  
- **Tool execution** may occur **locally** (Claude Code on developer machine) or in **client-controlled** environments per documented flows (`DOCUMENTED` — distinguish per workflow in ledger).  
- **MCP servers** may supply tools/context to compatible hosts (`DOCUMENTED` protocol + vendor docs).

## Internal model/runtime

**UNKNOWN** in this package.

## Control vs data plane (public)

- **Control:** API keys, workspace policies in product docs (`DOCUMENTED`).  
- **Data plane:** prompts, attachments, tool I/O (`DOCUMENTED` at interface level).
