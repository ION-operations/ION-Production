---
atlas_package: system
system_slug: android-aosp
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Process, memory, and namespace model

- **Per-app UID** separation and sandbox (`DOCUMENTED`).  
- **Zygote fork** for app processes (`DOCUMENTED`).  
- **Memory:** process heaps via ART; low-memory killer policy (`DOCUMENTED` at overview level).
