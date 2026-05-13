---
atlas_package: system
system_slug: docker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Scope

## In scope

- Engine architecture at documentation level: daemon, client, build, networking models (`DOCUMENTED`).  
- OCI alignment for images/runtimes where claimed by project docs (`std-oci`).

## Out of scope

- Every third-party Compose plugin — integrate only via documented extension points unless separate package.  
- Proprietary Docker Inc. business product internals beyond public docs.

## Versioning note

Docker Engine releases are versioned; CLI flags and API evolve (`DOCUMENTED`).
