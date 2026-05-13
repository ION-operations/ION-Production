---
atlas_package: system
system_slug: firecracker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Security and permissions

- **Seccomp** / **jailer** patterns in docs (`DOCUMENTED`).  
- **KVM access** (`/dev/kvm`) is a sensitive host permission (`DOCUMENTED`).  
- **Guest breakout** vs **host hardening** — cite security docs per claim (`DOCUMENTED`).
