---
atlas_package: system
system_slug: rocky-linux
schema_version: "1.0"
last_reviewed: "2026-04-03"
evidence_grade: A
---

# Architecture (conceptual)

## Layers

- **Kernel** **packages** **+** **`glibc`** **+** **`systemd`** **(default)** (`DOCUMENTED`).  
- **RPM** **metadata** **via** **`dnf`** (`DOCUMENTED`).

## Delivery surfaces

- **Server** **/** **cloud** **images**, **`rockylinux:*`** **containers**, **bare** **metal** (`DOCUMENTED` **/** `OBSERVED`).
