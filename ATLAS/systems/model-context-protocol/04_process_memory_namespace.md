---
atlas_package: system
system_slug: model-context-protocol
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Process, memory, and namespace model

- **Processes:** MCP server is typically a child process (stdio) or remote HTTP server (deployment-dependent) (`DOCUMENTED` transport docs).  
- **Memory:** No shared address space between host and server; marshaled messages (`DOCUMENTED` semantics).  
- **Namespaces:** URI schemes for resources as specified (`DOCUMENTED`).
