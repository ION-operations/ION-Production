---
atlas_package: system
system_slug: oci-distribution-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# OCI Distribution Specification

**Kind:** **Open Container Initiative** specification for **registry** HTTP APIs — **push**, **pull**, **content discovery**, and **blob** / **manifest** upload and download for OCI artifacts (`DOCUMENTED`, `src-oci-distribution-spec-repo`).

## Boundaries

- **Not** **`oci-image-spec`** — that package defines **manifest / index / config / layer** *data*; distribution defines **how registries move** those blobs (`DOCUMENTED`).  
- **Not** a **container runtime** — **`docker`**, **`containerd`**, **`podman`**, **`cri-o`** are **clients** or stacks that **speak** registry protocols (`DOCUMENTED`).  
- **Not** **object-storage** backends (S3, GCS) — storage layout is **implementation**; the spec is the **registry-facing** API class (`INFERRED`).

## Why this system matters

- **Interoperable** pull/push between **builders**, **CI**, **Kubernetes** nodes, and **hosted registries** (`DOCUMENTED`).  
- Separates **transport and discovery** from **image layout** when auditing supply chain and air-gap mirroring.

## What this system teaches the atlas

- Pair **`oci-distribution-spec`** with **`oci-image-spec`** for any “registry vs image format” question.
