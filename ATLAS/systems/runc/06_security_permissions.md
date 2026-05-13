---
atlas_package: system
system_slug: runc
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Security and permissions

- **Capabilities**, **seccomp**, **AppArmor/SELinux** labels as OCI fields (`DOCUMENTED`).  
- **Host breakout** class is joint responsibility of kernel + config + hooks (`INFERRED` threat model).
