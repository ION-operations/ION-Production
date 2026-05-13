---
atlas_package: system
system_slug: nomad
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Process, memory, and namespace model

- **Allocations** map work to clients per scheduler decisions (`DOCUMENTED`).  
- **Isolation** depends on task driver (cgroups/namespaces for containers; different for VMs) (`DOCUMENTED`).
