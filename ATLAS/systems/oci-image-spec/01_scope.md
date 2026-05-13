---
atlas_package: system
system_slug: oci-image-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Scope

## In scope

- **Image manifest** and **image index** (multi-arch) models (`DOCUMENTED`, `src-oci-image-spec-repo`).  
- **Configuration** JSON (`Config` / rootfs / `Cmd` / `Env` themes) and **layer** tarball conventions (`DOCUMENTED`).  
- Relationship to **distribution** spec (pull/push) as **adjacent** OCI work (`DOCUMENTED` cross-ref in repo).

## Out of scope

- **Runtime** bundle schema detail — **`oci-runtime-spec`**; **`runc`** **implements** it (`DOCUMENTED` split).  
- **Registry** HTTP API — **`oci-distribution-spec`** package.

## Versioning note

Spec evolves by **OCI release process**; implementations may lag **schema** features (`INFERRED`).
