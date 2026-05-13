---
atlas_package: system
system_slug: firecracker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Process, memory, and namespace model

- **Host processes** run VMM; **guest** is separate VM with own kernel (`DOCUMENTED`).  
- **Memory** assigned to microVM; overhead claims are doc/benchmark dependent (`DOCUMENTED` / `OBSERVED`).
