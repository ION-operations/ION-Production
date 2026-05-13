---
atlas_package: system
system_slug: systemd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Process, memory, and namespace model

- **Services** run as child processes in cgroups attached to units (`DOCUMENTED`).  
- **`User=` / `Group=`** drop privileges per unit (`DOCUMENTED`).  
- **Namespaces:** some isolation options exposed via unit settings where supported (`DOCUMENTED` — feature-specific).
