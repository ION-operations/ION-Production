---
atlas_package: system
system_slug: azure-aks
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: C
---

# Process, memory, and namespace model

- **Kubernetes pod/container** semantics apply on worker nodes (`DOCUMENTED` Kubernetes model).  
- **Windows vs Linux** node pools change isolation and image stacks — follow AKS workload docs (`DOCUMENTED`).
