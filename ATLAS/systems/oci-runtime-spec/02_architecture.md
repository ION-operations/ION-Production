---
atlas_package: system
system_slug: oci-runtime-spec
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Bundle

- **`rootfs`** + **`config.json`** consumed by a **runtime** binary (`DOCUMENTED`, `src-oci-runtime-spec-repo`).

## Stack position

- **High-level** runtimes prepare bundles; **low-level** runtimes **implement** lifecycle ops per spec (`DOCUMENTED` pattern with **`runc`**).

## Host

- **Namespaces**, **cgroups**, and **capabilities** map to **Linux** (and other OS ports with different matrices) (`DOCUMENTED`).
