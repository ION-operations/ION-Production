---
atlas_package: system
system_slug: firecracker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **Userspace VMM** using **KVM** (`DOCUMENTED`, `src-firecracker-getting-started`).  
- **Minimal virtual devices** to reduce attack surface vs general-purpose QEMU VMs (`DOCUMENTED` high-level claim—cite doc section in ledger upgrades).  
- **Jailer** process model for privilege separation as documented (`DOCUMENTED`).
