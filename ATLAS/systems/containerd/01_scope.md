---
atlas_package: system
system_slug: containerd
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Scope

## In scope

- `containerd` daemon, namespaces, snapshots, image transfer, CRI plugin (`DOCUMENTED`).  
- Relationship to **runc** (or compatible low-level runtime) as documented (`DOCUMENTED`).

## Out of scope

- Every Kubernetes distribution’s default socket paths — environment-specific (`OBSERVED`).  
- Windows/macOS variants unless explicitly curated.

## Versioning note

Major releases (1.x vs 2.x) change config schema — cite version (`DOCUMENTED`).
