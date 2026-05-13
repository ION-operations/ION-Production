---
atlas_package: system
system_slug: kubernetes
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Process, memory, and namespace model

- **Pod** is atomic scheduling unit; containers share optional Linux namespaces per spec (`DOCUMENTED`).  
- **cgroup** and container runtime enforce compute/memory isolation (`DOCUMENTED` via Linux integration).  
- **Kubernetes Namespace** API is a cluster partitioning object — distinct from Linux namespaces (`DOCUMENTED`).
