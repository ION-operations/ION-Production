---
atlas_package: system
system_slug: linux-kernel
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Operator / user surface

- **Syscalls** for programs; **pseudo-filesystems** (`/proc`, `/sys`) for introspection and tuning (`DOCUMENTED`).  
- **`sysctl`** and **netlink** for runtime configuration (`DOCUMENTED`).  
- **dmesg** / kernel log for early boot and driver messages (`DOCUMENTED`).
