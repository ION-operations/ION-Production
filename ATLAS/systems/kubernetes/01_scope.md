---
atlas_package: system
system_slug: kubernetes
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Scope

## In scope

- Control plane components (apiserver, etcd, scheduler, controller manager patterns), node components (kubelet, kube-proxy), API resources, scheduling, networking model abstractions, workload controllers.

## Out of scope

- Specific cloud provider control planes unless citing their documented Kubernetes service.  
- Application code inside containers.

## Versioning note

APIs are versioned (`v1`, `apps/v1`, etc.); behavior is release-specific (`DOCUMENTED`).
