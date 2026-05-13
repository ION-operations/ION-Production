---
atlas_package: system
system_slug: model-context-protocol
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Evidence ledger

| claim_id | claim | tier | locator / protocol | notes |
|----------|-------|------|--------------------|-------|
| mcp-001 | MCP uses JSON-RPC messages | DOCUMENTED | `src-mcp-spec` | |
| mcp-002 | Host/client/server role separation | DOCUMENTED | `src-mcp-spec` | |
| mcp-003 | Tool listing and invocation are protocol primitives | DOCUMENTED | `src-mcp-spec` | |
| mcp-004 | Security model places consent/trust on host + user | DOCUMENTED | `src-mcp-spec` security section | |
| mcp-005 | Transports include stdio and Streamable HTTP (see dated spec path) | DOCUMENTED | `src-mcp-transport` | pin spec date |
| mcp-006 | JSON-RPC message shape is not gRPC/Protobuf | DOCUMENTED | `src-mcp-spec` | contrast `grpc` |
