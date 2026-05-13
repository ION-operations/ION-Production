---
atlas_package: system
system_slug: musl
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layering

- **Single** **repository** **libc** + **dynamic** **linker** **(ld-musl)** on **supported** **Linux** **ABIs** (`DOCUMENTED`, `src-musl-wiki`).

## Containers

- **Small** **rootfs** images often **static**-**link** or **use** **musl** **shared** **objects** (`INFERRED`).
