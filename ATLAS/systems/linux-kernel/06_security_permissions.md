---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Security and permissions

- **DAC:** UID/GID, mode bits (`DOCUMENTED`).  
- **Capabilities:** Fine-grained privilege partitioning (`DOCUMENTED`).  
- **LSM:** Pluggable security modules (SELinux, AppArmor, SMACK, etc.) (`DOCUMENTED`).  
- **Seccomp / namespaces:** Syscall filtering and isolation (`DOCUMENTED`).  
- **eBPF:** Verified programs attach to hooks (observability/security tooling) (`DOCUMENTED`).
