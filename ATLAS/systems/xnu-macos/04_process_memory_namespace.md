---
atlas_package: system
system_slug: xnu-macos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Process, memory, and namespace model

- **Tasks/threads** (Mach) mapped to BSD processes (`DOCUMENTED`).  
- **Mach ports** for capabilities-style IPC (`DOCUMENTED`).  
- **Memory maps** via Mach VM + BSD mmap (`DOCUMENTED`).
