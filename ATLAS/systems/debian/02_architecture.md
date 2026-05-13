---
atlas_package: system
system_slug: debian
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Kernel** **packages** **+** **`glibc`** **userland** **+** **`systemd`** **service** **supervision** **(default** **current** **stable)** (`DOCUMENTED`).  
- **Package** **metadata** **and** **maintainer** **scripts** **via** **`dpkg`** **/** **`apt`** (`DOCUMENTED`).

## Delivery surfaces

- **Installer** **images**, **cloud** **templates**, **container** **bases** **`debian:*`**, **and** **bare** **metal** (`DOCUMENTED` **/** `OBSERVED`).
