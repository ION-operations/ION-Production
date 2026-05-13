---
atlas_package: system
system_slug: vscode
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| vsc-001 | Extension Host isolates extensions in separate process | DOCUMENTED | `src-vscode-api` | |
| vsc-002 | Product ships with documented extension API | DOCUMENTED | `src-vscode-api` | |
| vsc-003 | MCP client integration documented (manage servers, mcp.json) | DOCUMENTED | `src-vscode-mcp-servers`, `src-vscode-mcp-config` | |
| vsc-004 | Uses Electron for desktop shell | DOCUMENTED | `src-vscode-repo` README / docs | |
