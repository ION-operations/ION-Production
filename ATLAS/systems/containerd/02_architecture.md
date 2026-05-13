---
atlas_package: system
system_slug: containerd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Architecture

- **Daemon** with gRPC API (`DOCUMENTED`).  
- **Content store** + **snapshotters** for layer/rootfs management (`DOCUMENTED`).  
- **CRI plugin** bridges kubelet to OCI runtime (`DOCUMENTED`, `src-k8s-cri`).  
- **Namespaces** inside containerd isolate tenants of metadata/images (`DOCUMENTED`).
