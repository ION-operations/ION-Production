---
atlas_package: system
system_slug: linux-vhost
schema_version: "1.0"
last_reviewed: "2026-04-28"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `linux-kernel`:** **vhost** **is** **a** **kernel** **framework** (`DOCUMENTED`).  
- **`integrates_with` `virtio` + `linux-kvm` + `firecracker` (INFERRED/DOCUMENTED):** **virtio** **devices** **in** **guests;** **KVM**/**VMM** **hosts** **—** **distinct** **roles.**
