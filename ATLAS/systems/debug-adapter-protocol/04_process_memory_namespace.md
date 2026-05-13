---
atlas_package: system
system_slug: debug-adapter-protocol
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Process, memory, namespace

Trust boundary is **client process ↔ adapter process**; adapter may spawn or attach to **target** debugee (`DOCUMENTED` security model section of spec).
