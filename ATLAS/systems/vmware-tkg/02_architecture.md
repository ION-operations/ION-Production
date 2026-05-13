---
atlas_package: system
system_slug: vmware-tkg
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **Management cluster** receives requests from **client CLI or UI** and executes them using **Cluster API** (`DOCUMENTED`, `src-broadcom-tkg-about`).  
- **Workload clusters** are created and managed via TKG workflows (vSphere-focused doc set) (`DOCUMENTED` pattern).

## UNKNOWN at seed depth

- Default CNI/ingress stack internals per release — follow TKG networking guides when needed.
