---
atlas_package: system
system_slug: windows-nt
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Process, memory, and namespace model

- **Processes and threads** as schedulable units; EPROCESS/ETHREAD structures in kernel (`DOCUMENTED` internals references — cite edition).  
- **Virtual address spaces** per process with sections/views (`DOCUMENTED`).  
- **Object namespace** distinct from pure file paths (`DOCUMENTED`).
