---
atlas_package: system
system_slug: azure-aci
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **Container groups** as the deployable unit; multi-container groups share host, network, storage, lifecycle (`DOCUMENTED`).  
- **Hypervisor-level isolation** claim for multitenant hardening (`DOCUMENTED`).  
- **NGroups** for managing fleets of groups with rolling upgrades/load balancers (`DOCUMENTED`).

## UNKNOWN at seed depth

- Undocumented internal placement on Azure physical infrastructure — not asserted.
