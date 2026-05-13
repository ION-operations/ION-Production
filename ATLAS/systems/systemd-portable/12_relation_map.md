---
atlas_package: system
system_slug: systemd-portable
schema_version: "1.0"
last_reviewed: "2026-04-12"
evidence_grade: A
---

# Relation map (narrative)

- **`integrates_with` `systemd`:** portable services are a **systemd** feature; **`portablectl`** is part of the suite (`DOCUMENTED`).  
- **`integrates_with` `systemd-unit-model`:** attached bundles expose **unit files** interpreted like normal units (`DOCUMENTED`).  
- **`integrates_with` `linux-kernel`:** loop/verity and mount behavior are Linux-backed (`DOCUMENTED` / `INFERRED`).  
- **`competes_with` `docker`:** alternative **application bundle** story on a Linux host; not the same as OCI (`INFERRED` substitution class).
