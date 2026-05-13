---
atlas_package: system
system_slug: virtio
schema_version: "1.0"
last_reviewed: "2026-04-27"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `linux-kernel`:** **virtio** **drivers** **live** **in** **the** **kernel** **tree** (`DOCUMENTED`).  
- **`integrates_with` `linux-kvm` + `firecracker` (INFERRED/DOCUMENTED):** **guests** **consume** **virtio** **devices;** **VM** **runtime** **is** **separate** **from** **the** **virtio** **contract.**
