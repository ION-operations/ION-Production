---
atlas_package: system
system_slug: firecracker
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: B
---

# Scope

## In scope

- VMM responsibilities, guest boot requirements (kernel + rootfs), rate limiting, snapshot APIs as documented (`DOCUMENTED`).  
- Security model at the level described in official docs (`DOCUMENTED`).

## Out of scope

- Guest OS internals.  
- Proprietary cloud orchestration unless sourced.

## Versioning note

Firecracker releases are versioned; device support and APIs evolve (`DOCUMENTED`).
