---
atlas_package: system
system_slug: debug-adapter-protocol
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| dap-001 | DAP uses JSON-RPC between client and debug adapter | DOCUMENTED | `src-dap-spec` | |
| dap-002 | DAP is specified independently of LSP | DOCUMENTED | `src-dap-spec`; `language-server-protocol` package | |
| dap-003 | DAP is not MCP (different messages and trust story) | INFERRED | Contrast `model-context-protocol` package | Host stacks may ship both. |
