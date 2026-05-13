---
atlas_package: system
system_slug: azure-container-apps
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: C
---

# Process, memory, and namespace model

- **Container** execution with per-replica CPU/memory limits as described in scaling/profile docs (`DOCUMENTED` pattern).  
- **Pod-equivalent internals** — not operator-visible; **UNKNOWN** as a direct API.
