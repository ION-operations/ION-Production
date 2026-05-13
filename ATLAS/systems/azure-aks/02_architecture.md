---
atlas_package: system
system_slug: azure-aks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Architecture

- **Control plane** created and configured by Azure when you create an AKS cluster; Azure **manages** the control plane (`DOCUMENTED`).  
- **Worker nodes** run customer applications; Azure handles health/maintenance responsibilities as described (`DOCUMENTED` overview).  
- **Kubernetes API** is the workload interface (`DOCUMENTED` framing).

## UNKNOWN at seed depth

- Internal apiserver/etcd placement in Azure regions — not asserted.
