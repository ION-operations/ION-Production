---
atlas_package: system
system_slug: oci-runtime-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **Bundle** filesystem layout, **`config.json`** schema themes (process, root, mounts, linux resources, …) (`DOCUMENTED`, `src-oci-runtime-spec-repo`).  
- **Lifecycle** operation model at the spec layer (`DOCUMENTED`).

## Out of scope

- **Image** manifest and layer tarballs — **`oci-image-spec`**.  
- **Registry** protocols — **`oci-distribution-spec`**.  
- **Kernel** implementation bugs — **`linux-kernel`** (host law), though the spec **references** Linux primitives (`DOCUMENTED` split).

## Versioning note

Spec and **kernel** features (e.g. cgroup versions) evolve on different clocks (`INFERRED`).
