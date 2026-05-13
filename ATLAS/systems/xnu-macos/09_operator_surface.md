---
atlas_package: system
system_slug: xnu-macos
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: C
---

# Operator / user surface

- **End users** rarely touch kernel; **developers** use Xcode + logs + `sysctl` (`DOCUMENTED` / `OBSERVED`).  
- **systemextensionsctl** etc. for extension management (`DOCUMENTED`).
