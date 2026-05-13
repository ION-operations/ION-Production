---
atlas_package: system
system_slug: oci-image-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Descriptors** reference blobs by **digest**; **manifest** ties config + layers (`DOCUMENTED`, `src-oci-image-spec-repo`).  
- **Index** selects platform-specific manifests (`DOCUMENTED`).

## Consumers

- **Build** tools produce manifests and layer tarballs; **registries** store blobs; **CRI** stacks **unpack** toward **runtime** bundles (`DOCUMENTED` ecosystem pattern).

## Failure / ops themes

- **Digest immutability** vs **tag** mutability is an operational invariant across registries (`INFERRED` common practice).
