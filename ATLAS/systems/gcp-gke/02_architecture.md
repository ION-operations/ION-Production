---
atlas_package: system
system_slug: gcp-gke
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **Nodes** are **Compute Engine VMs** grouped into a **cluster** (`DOCUMENTED`).  
- **Control plane** runs management components (e.g. API server); **Google Cloud manages** the control plane and system components (`DOCUMENTED`).  
- **Autopilot:** Google Cloud also manages **worker nodes**; **Standard:** customer manages node pools (`DOCUMENTED`).

## UNKNOWN at seed depth

- Regional control plane replication internals — follow “cluster architecture” doc for allowed claims.
