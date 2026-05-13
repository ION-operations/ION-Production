---
atlas_package: system
system_slug: systemd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Security and permissions

- **Capability bounding sets** and privilege configuration per unit (`DOCUMENTED`).  
- **Sandboxing directives** (various `SystemCallFilter`, namespaces, etc.) (`DOCUMENTED` per directive).  
- **Polkit** often gates privileged D-Bus actions in desktop integrations (`DOCUMENTED` ecosystem).
