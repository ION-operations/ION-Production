---
atlas_package: system
system_slug: cri-o
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

- **CRI server** for kubelet gRPC (`DOCUMENTED`).  
- **Image service** + **runtime service** responsibilities per CRI (`DOCUMENTED`, `src-k8s-cri`).  
- Delegates OCI bundle execution to configured low-level runtime (often `runc`) (`DOCUMENTED`).
