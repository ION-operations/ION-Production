---
atlas_package: system
system_slug: model-context-protocol
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Security and permissions

- **Trust model:** Host is responsible for user consent and server selection (`DOCUMENTED` spec security section).  
- **Tool invocation** can execute arbitrary side effects — server must be trusted (`DOCUMENTED`).  
- **Authorization** of which tools/resources are exposed is split between server implementation and host policy (`DOCUMENTED` pattern).
