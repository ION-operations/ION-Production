---
atlas_package: system
system_slug: crun
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Position

- **Leaf** executor: receives **OCI bundle**, applies **Linux** namespaces/cgroups per **`oci-runtime-spec`** (`DOCUMENTED`).

## Callers

- **containerd** **shim**, **podman**, **cri-o** can **fork/exec** **crun** instead of **`runc`** (`DOCUMENTED` class).
