---
atlas_package: system
system_slug: anthropic-claude-code-agent-sdk
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Storage, network, and IPC

- **TLS** to API endpoints (`DOCUMENTED`).  
- **Local filesystem** access under user OS permissions for Claude Code (`DOCUMENTED` / `OBSERVED`).  
- **MCP** transports (stdio, SSE, etc.) per MCP spec (`DOCUMENTED` in MCP package).
