---
atlas_package: system
system_slug: language-server-protocol
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| lsp-001 | LSP uses JSON-RPC messages | DOCUMENTED | `src-lsp-spec-3-17` | |
| lsp-002 | Client/server capability negotiation exists | DOCUMENTED | `src-lsp-spec-3-17` | |
| lsp-003 | LSP is not MCP (different capability surface) | DOCUMENTED | `src-lsp-spec-3-17`; contrast `model-context-protocol` package | |
