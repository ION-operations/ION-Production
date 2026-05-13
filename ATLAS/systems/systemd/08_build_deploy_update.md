---
atlas_package: system
system_slug: systemd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Build, deploy, and update

- **Build:** meson/ninja from upstream source (`DOCUMENTED`, `src-systemd-source`).  
- **Deploy:** distribution packages swap PID 1 (`OBSERVED` practice).  
- **Update:** transactional unit reloads; daemon-reexec mechanisms (`DOCUMENTED`).
