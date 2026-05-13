---
atlas_package: system
system_slug: cri-o
schema_version: "1.0"
last_reviewed: "2026-04-02"
evidence_grade: A
---

# Scope

## In scope

- CRI-O architecture topics in official docs: storage, networking integration, runtime selection (`DOCUMENTED`).  
- Relationship to **OCI** images and low-level runtimes (`DOCUMENTED`).

## Out of scope

- OpenShift product packaging as a full second package — cross-reference only when sourced.  
- Non-Linux Kubernetes node runtimes.

## Versioning note

CRI-O versions track Kubernetes minor releases closely — cite pairing in claims (`DOCUMENTED` pattern).
