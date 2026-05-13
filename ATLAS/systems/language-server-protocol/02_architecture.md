---
atlas_package: system
system_slug: language-server-protocol
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

- **Client** sends requests/notifications; **server** responds with results/push diagnostics (`DOCUMENTED`).  
- **Workspace folders** and **text document** URIs identify resources (`DOCUMENTED`).  
- **Transport:** commonly stdio or socket-bridged JSON-RPC (`DOCUMENTED` implementation-dependent).
