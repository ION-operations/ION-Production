---
atlas_package: system
system_slug: docker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Security and permissions

- **Rootful vs rootless** modes documented (`DOCUMENTED`).  
- **Linux capabilities** dropped/added per container configuration (`DOCUMENTED`).  
- **seccomp / AppArmor / SELinux** profiles where supported (`DOCUMENTED` platform-dependent).  
- **Socket exposure** to daemon is a high-value trust boundary (`DOCUMENTED` hardening guides).
