---
atlas_package: system
system_slug: oci-distribution-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Client / server

- **Registry** exposes HTTP endpoints; **clients** resolve names/tags to **manifests**, then fetch **blobs** by **digest** (`DOCUMENTED`, `src-oci-distribution-spec-repo`).

## Composition

- Transferred artifacts are typically **OCI Image** manifests/indexes/config/layers per **`oci-image-spec`** (`DOCUMENTED`).

## Ops themes

- **Mirroring**, **air-gap** pulls, and **garbage collection** are **deployment** concerns layered on the API (`INFERRED`).
