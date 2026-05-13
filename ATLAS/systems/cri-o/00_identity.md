---
atlas_package: system
system_slug: cri-o
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# CRI-O — Identity

**Kind:** **Kubernetes-native** container runtime implementing the **CRI** for kubelet, focused on pulling images and running OCI workloads without a Docker daemon (`DOCUMENTED`, `src-cri-o-site`, `src-cri-o-repo`).

## Boundaries

- **Not** `docker` or `podman` CLI workflows — different operator surfaces (`DOCUMENTED`).  
- **Not** the only CRI — `containerd` with CRI plugin is a major alternative (`DOCUMENTED`, `src-k8s-cri`).

## Why this system matters

- Clarifies **CRI** as a distinct seam in the Kubernetes node stack (`DOCUMENTED`).  
- Common in **OpenShift-flavored** and minimal-node Linux deployments (`OBSERVED` / vendor docs — tier per claim).

## What this system teaches the atlas

- **CRI multiplicity:** kubelet ↔ (CRI-O | containerd | …) ↔ OCI runtime (`runc` class).
