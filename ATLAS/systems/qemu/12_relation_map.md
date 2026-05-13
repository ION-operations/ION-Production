---
atlas_package: system
system_slug: qemu
schema_version: "1.0"
last_reviewed: "2026-04-04"
evidence_grade: B
---

# Relation map (narrative)

- **`depends_on` `linux-kernel`:** **host** **and** **guest** **kernel** **facilities** **(DOCUMENTED** **scope).**  
- **`integrates_with` `linux-kvm` + `virtio` + `linux-vhost` + `linux-vfio`:** **typical** **Linux** **composition** **(INFERRED** **/** **DOCUMENTED** **where** **cited).**  
- **`competes_with` `firecracker`:** **different** **VMM** **product** **scope** **(INFERRED).**
