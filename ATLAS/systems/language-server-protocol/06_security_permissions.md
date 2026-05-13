---
atlas_package: system
system_slug: language-server-protocol
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Security and permissions

- **Trust model:** language server can read project files; malicious servers are high risk (`INFERRED` security guidance in ecosystem).  
- **Spec** focuses on protocol, not OS sandboxing (`DOCUMENTED`).
