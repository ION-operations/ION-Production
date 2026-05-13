---
atlas_package: system
system_slug: language-server-protocol
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Storage, network, and IPC

- **JSON-RPC** framing over stdio/TCP as chosen by host (`DOCUMENTED` implementation).  
- **File system access** is server-side responsibility subject to host policy (`DOCUMENTED` pattern).
