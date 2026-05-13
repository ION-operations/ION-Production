---
atlas_package: system
system_slug: containerd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# containerd — Identity

**Kind:** **OCI-oriented container runtime** emphasizing daemon API, snapshotters, and a **CRI** implementation for Kubernetes (`DOCUMENTED`, `src-containerd-docs`, CNCF graduation status per project pages).

## Boundaries

- **Not** Docker Desktop or `docker` CLI — different control surfaces (`docker` package).  
- **Not** the only CRI implementation — CRI-O and others exist (`DOCUMENTED`, `src-k8s-cri`).

## Why this system matters

- **Default-ish CRI path** for many Kubernetes Linux nodes (`DOCUMENTED` operational pattern).  
- **Separation** between image/content store and higher-level orchestrators (`DOCUMENTED`).

## What this system teaches the atlas

- **Engine vs CRI runtime** layering (Docker → containerd → runc class diagrams — cite Engine docs + containerd docs).
