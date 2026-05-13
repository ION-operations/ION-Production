---
atlas_package: system
system_slug: linux-kvm
schema_version: "1.0"
last_reviewed: "2026-04-26"
evidence_grade: B
---

# Relation map (narrative)

- **`integrates_with` `linux-kernel`:** **KVM** **is** **part** **of** **the** **kernel** **virtualization** **stack** (`DOCUMENTED`).  
- **`integrates_with` `firecracker`:** **Firecracker** **uses** **KVM** **on** **Linux** **per** **product** **documentation** (`DOCUMENTED` **for** **dependency** **class**).  
- **`integrates_with` `linux-namespaces` (INFERRED):** **contrasting** **isolation** **models** **—** **VM** **vs** **namespaced** **process** **containers.**
