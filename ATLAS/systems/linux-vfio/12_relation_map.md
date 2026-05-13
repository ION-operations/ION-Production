---
atlas_package: system
system_slug: linux-vfio
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `linux-kernel`:** **VFIO** **is** **a** **kernel** **driver** **framework** (`DOCUMENTED`).  
- **`integrates_with` `linux-kvm` + `firecracker` (INFERRED):** **passthrough** **composition** **with** **VM** **stacks** **—** **distinct** **from** **virtio** **paravirtual** **paths** **alone.**
