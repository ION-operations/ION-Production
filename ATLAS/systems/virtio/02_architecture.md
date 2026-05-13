---
atlas_package: system
system_slug: virtio
schema_version: "1.0"
last_reviewed: "2026-04-27"
evidence_grade: B
---

# Architecture (conceptual)

**Guests** **submit** **I/O** **requests** **through** **virtqueues;** **the** **host** **implements** **backend** **drivers** **that** **complete** **work** **according** **to** **the** **virtio** **contract** (`DOCUMENTED`).
